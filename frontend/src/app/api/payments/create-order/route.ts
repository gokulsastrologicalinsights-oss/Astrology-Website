import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { PLAN_PRESETS } from "@/lib/permissions";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json(
        { error: "Authentication required. Please sign in to purchase a software subscription." },
        { status: 401 }
      );
    }

    const body = await request.json();
    const { planId = "pro", billingCycle = "monthly" } = body;

    const preset = PLAN_PRESETS[planId];
    if (!preset) {
      return NextResponse.json(
        { error: `Invalid subscription plan '${planId}' specified.` },
        { status: 400 }
      );
    }

    const isYearly = billingCycle === "yearly";
    const amountInr = isYearly ? preset.yearlyPriceInr : preset.monthlyPriceInr;
    const amountInPaise = amountInr * 100;

    const keyId =
      process.env.RAZORPAY_KEY_ID || process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID;
    const keySecret = process.env.RAZORPAY_KEY_SECRET;

    if (!keyId || !keySecret) {
      return NextResponse.json(
        {
          error:
            "Razorpay payment gateway credentials are not configured on the server. Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in environment variables.",
        },
        { status: 500 }
      );
    }

    // Generate unique receipt reference (max 40 chars for Razorpay)
    const receipt = `gai_${user.id.replace(/[^a-zA-Z0-9]/g, "").slice(0, 10)}_${Date.now()}`.slice(0, 40);

    const authHeader = `Basic ${Buffer.from(`${keyId}:${keySecret}`).toString("base64")}`;

    const orderPayload = {
      amount: amountInPaise,
      currency: "INR",
      receipt,
      notes: {
        userId: user.id,
        userEmail: user.email || "",
        planId,
        billingCycle,
        service: "Gokul Astrological Insights Software Tools",
      },
    };

    const rzpResponse = await fetch("https://api.razorpay.com/v1/orders", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: authHeader,
      },
      body: JSON.stringify(orderPayload),
    });

    const orderData = await rzpResponse.json();

    if (!rzpResponse.ok) {
      console.error("Razorpay order creation failed:", orderData);
      return NextResponse.json(
        {
          error:
            orderData?.error?.description ||
            "Unable to generate payment order with Razorpay. Please try again or contact support.",
        },
        { status: rzpResponse.status }
      );
    }

    return NextResponse.json({
      success: true,
      orderId: orderData.id,
      amount: orderData.amount,
      currency: orderData.currency || "INR",
      keyId,
      planId,
      planNameEn: preset.nameEn,
      planNameTa: preset.nameTa,
      billingCycle,
      user: {
        id: user.id,
        email: user.email,
        name:
          user.user_metadata?.display_name ||
          user.user_metadata?.username ||
          user.email?.split("@")[0] ||
          "Customer",
      },
    });
  } catch (error: any) {
    console.error("Error in /api/payments/create-order:", error?.message || error);
    return NextResponse.json(
      { error: "Internal server error initiating payment checkout." },
      { status: 500 }
    );
  }
}
