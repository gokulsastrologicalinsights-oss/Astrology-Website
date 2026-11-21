import { NextRequest, NextResponse } from "next/server";
import crypto from "crypto";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { PLAN_PRESETS, UserPermissions, UserSubscription } from "@/lib/permissions";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json(
        { error: "Authentication required to complete payment verification." },
        { status: 401 }
      );
    }

    const body = await request.json();
    const {
      razorpay_order_id,
      razorpay_payment_id,
      razorpay_signature,
      planId = "pro",
      billingCycle = "monthly",
      isSingleService = false,
    } = body;

    if (!razorpay_order_id || !razorpay_payment_id || !razorpay_signature) {
      return NextResponse.json(
        { error: "Missing required payment transaction parameters." },
        { status: 400 }
      );
    }

    const keySecret = process.env.RAZORPAY_KEY_SECRET;
    if (!keySecret) {
      return NextResponse.json(
        { error: "Server payment verification secret is not configured." },
        { status: 500 }
      );
    }

    // 1. Verify HMAC SHA-256 signature
    const generatedSignature = crypto
      .createHmac("sha256", keySecret)
      .update(`${razorpay_order_id}|${razorpay_payment_id}`)
      .digest("hex");

    if (generatedSignature !== razorpay_signature) {
      console.error("Signature mismatch:", { generatedSignature, razorpay_signature });
      return NextResponse.json(
        { error: "Tampered or invalid payment signature received from gateway." },
        { status: 400 }
      );
    }

    const adminClient = createAdminClient();
    const { data: existingUser, error: fetchErr } =
      await adminClient.auth.admin.getUserById(user.id);

    if (fetchErr || !existingUser?.user) {
      return NextResponse.json(
        { error: "Failed to locate user account for provisioning." },
        { status: 404 }
      );
    }

    const currentMeta = existingUser.user.user_metadata || {};

    // If it's a single service purchase (pay-per-report)
    if (isSingleService) {
      const singlePurchases = currentMeta.singlePurchases || [];
      const newPurchase = {
        itemKey: planId,
        paymentId: razorpay_payment_id,
        orderId: razorpay_order_id,
        purchasedAt: new Date().toISOString(),
        status: "active",
      };

      const updatedMeta = {
        ...currentMeta,
        singlePurchases: [...singlePurchases, newPurchase],
        reportCredits: (currentMeta.reportCredits || 0) + 1,
      };

      await adminClient.auth.admin.updateUserById(user.id, {
        user_metadata: updatedMeta,
      });

      return NextResponse.json({
        success: true,
        message: "Payment verified successfully! Your report access is now unlocked.",
        paymentId: razorpay_payment_id,
        isSingleService: true,
      });
    }

    // Otherwise, handle Astrologer SaaS subscription plan
    const preset = PLAN_PRESETS[planId] || PLAN_PRESETS.pro;
    const isYearly = billingCycle === "yearly";
    const durationDays = isYearly ? 365 : 30;
    const validUntilDate = new Date(Date.now() + durationDays * 24 * 60 * 60 * 1000);
    const validUntil = validUntilDate.toISOString();

    const finalTier = preset.tier;
    const finalPermissions: UserPermissions = { ...preset.permissions };
    const maxPdfMonthly =
      planId === "basic" ? 30 : planId === "tamil_specialist" ? 100 : 999999;

    const subscriptionPayload: UserSubscription = {
      tier: finalTier,
      status: "active",
      validUntil,
      maxPdfMonthly,
    };

    const updatedMeta = {
      ...currentMeta,
      subscription: {
        ...subscriptionPayload,
        lastPayment: {
          orderId: razorpay_order_id,
          paymentId: razorpay_payment_id,
          planId,
          billingCycle,
          paidAt: new Date().toISOString(),
          validUntil,
        },
      },
      permissions: finalPermissions,
    };

    const { error: updateErr } = await adminClient.auth.admin.updateUserById(
      user.id,
      { user_metadata: updatedMeta }
    );

    if (updateErr) {
      console.error("Error activating subscription in Supabase:", updateErr);
      return NextResponse.json(
        {
          error:
            "Payment verified, but account activation encountered a database issue. Please contact support with payment ID: " +
            razorpay_payment_id,
        },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      message: `Your ${preset.nameEn} subscription is now active! Valid until ${validUntilDate.toLocaleDateString()}.`,
      subscription: subscriptionPayload,
      permissions: finalPermissions,
      paymentId: razorpay_payment_id,
    });
  } catch (error: any) {
    console.error("Error in /api/payments/verify:", error?.message || error);
    return NextResponse.json(
      { error: "Internal server error verifying payment." },
      { status: 500 }
    );
  }
}
