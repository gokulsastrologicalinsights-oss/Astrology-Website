import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { PLAN_PRESETS } from "@/lib/permissions";

const SINGLE_SERVICE_PRICES: Record<
  string,
  { nameEn: string; nameTa: string; priceInr: number }
> = {
  single_tamil_booklet: {
    nameEn: "Traditional Tamil 6-Page Booklet PDF",
    nameTa: "பாரம்பரிய தமிழ் 6-பக்க ஜாதக புத்தகம்",
    priceInr: 199,
  },
  single_marriage_matching: {
    nameEn: "Marriage Compatibility Report",
    nameTa: "திருமணப் பொருத்த விரிவான அறிக்கை",
    priceInr: 149,
  },
  single_kp_report: {
    nameEn: "Advanced KP Sub-Lord Analysis",
    nameTa: "உயர்நிலை கே.பி. உப-அதிபதி அறிக்கை",
    priceInr: 249,
  },
  single_vedic_kundli: {
    nameEn: "Full Vedic Kundli & Predictions",
    nameTa: "முழுமையான வேத ஜாதக அறிக்கை",
    priceInr: 299,
  },
  single_tool_unlock: {
    nameEn: "Instant Single Tool Report Unlock",
    nameTa: "உடனடி ஒற்றை அறிக்கை கட்டணம்",
    priceInr: 199,
  },
};

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json(
        { error: "Authentication required. Please sign in to complete payment." },
        { status: 401 }
      );
    }

    const body = await request.json();
    const { planId = "pro", billingCycle = "monthly", singleItemKey } = body;

    let amountInr = 1999;
    let planNameEn = "Tamil Horoscope Specialist";
    let planNameTa = "தமிழ் ஜாதகப் பிரதியாளர் திட்டம்";
    let isSingleService = false;

    if (singleItemKey && SINGLE_SERVICE_PRICES[singleItemKey]) {
      const item = SINGLE_SERVICE_PRICES[singleItemKey];
      amountInr = item.priceInr;
      planNameEn = item.nameEn;
      planNameTa = item.nameTa;
      isSingleService = true;
    } else if (PLAN_PRESETS[planId]) {
      const preset = PLAN_PRESETS[planId];
      const isYearly = billingCycle === "yearly";
      amountInr = isYearly ? preset.yearlyPriceInr : preset.monthlyPriceInr;
      planNameEn = preset.nameEn;
      planNameTa = preset.nameTa;
    } else {
      return NextResponse.json(
        { error: `Invalid subscription plan or service item '${planId}'.` },
        { status: 400 }
      );
    }

    const amountInPaise = amountInr * 100;
    const keyId =
      process.env.RAZORPAY_KEY_ID || process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID;
    const keySecret = process.env.RAZORPAY_KEY_SECRET;

    if (!keyId || !keySecret) {
      return NextResponse.json(
        {
          error:
            "Razorpay payment gateway credentials are not configured on the server. Please check your environment variables.",
        },
        { status: 500 }
      );
    }

    // Generate unique receipt reference (max 40 chars for Razorpay)
    const receipt = `gai_${user.id.replace(/[^a-zA-Z0-9]/g, "").slice(0, 8)}_${Date.now()}`.slice(0, 40);

    const authHeader = `Basic ${Buffer.from(`${keyId}:${keySecret}`).toString("base64")}`;

    const orderPayload = {
      amount: amountInPaise,
      currency: "INR",
      receipt,
      notes: {
        userId: user.id,
        userEmail: user.email || "",
        planId: isSingleService ? singleItemKey : planId,
        billingCycle: isSingleService ? "one-time" : billingCycle,
        type: isSingleService ? "single_service" : "subscription",
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
      planId: isSingleService ? singleItemKey : planId,
      planNameEn,
      planNameTa,
      billingCycle: isSingleService ? "one-time" : billingCycle,
      isSingleService,
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
