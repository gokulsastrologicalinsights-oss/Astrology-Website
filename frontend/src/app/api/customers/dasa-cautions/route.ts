import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import {
  getTodayDasaCautionAlerts,
  markDasaCautionAlertSent,
} from "@/lib/dasa-caution-service";

/**
 * GET /api/customers/dasa-cautions
 * Scans saved charts for the authenticated user (or all if admin) and identifies
 * clients who are currently in or entering an adverse Dasa-Bhukti period.
 */
export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json(
        { error: "Unauthorized access: Sign-in required." },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(request.url);
    const lang = (searchParams.get("lang") === "ta" ? "ta" : "en") as "en" | "ta";

    const { data: profile } = await supabase
      .from("profiles")
      .select("role")
      .eq("id", user.id)
      .single();

    const isAdmin = profile?.role === "admin";

    const data = await getTodayDasaCautionAlerts(user.id, isAdmin, lang);

    return NextResponse.json({
      success: true,
      ...data,
      isAdmin,
    });
  } catch (err: any) {
    console.error("GET /api/customers/dasa-cautions error:", err);
    return NextResponse.json(
      { error: err?.message || "Internal server error fetching Dasa caution reminders." },
      { status: 500 }
    );
  }
}

/**
 * POST /api/customers/dasa-cautions
 * Manually marks an adverse Dasa-Bhukti reminder as sent by the astrologer.
 */
export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json(
        { error: "Unauthorized access: Sign-in required." },
        { status: 401 }
      );
    }

    const body = await request.json();
    const {
      horoscope_id,
      customer_id,
      dasa_lord,
      bhukti_lord,
      period_start,
      period_end,
      severity,
    } = body;

    if (!horoscope_id || !dasa_lord || !bhukti_lord || !period_start) {
      return NextResponse.json(
        { error: "Missing required caution alert identification fields." },
        { status: 400 }
      );
    }

    const result = await markDasaCautionAlertSent({
      horoscopeId: horoscope_id,
      customerId: customer_id,
      dasaLord: dasa_lord,
      bhuktiLord: bhukti_lord,
      periodStart: period_start,
      periodEnd: period_end,
      severity,
      sentBy: user.id,
    });

    return NextResponse.json(result);
  } catch (err: any) {
    console.error("POST /api/customers/dasa-cautions error:", err);
    return NextResponse.json(
      { error: err?.message || "Failed to mark caution alert as sent." },
      { status: 500 }
    );
  }
}
