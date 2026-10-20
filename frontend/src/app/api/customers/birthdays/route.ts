import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import {
  getTodayBirthdayCelebrants,
  markBirthdayWishSent,
} from "@/lib/customer-service";

/**
 * GET /api/customers/birthdays
 * Identifies customers whose birthday is today in the Asia/Kolkata timezone.
 * Generates personalized WhatsApp links with recipient numbers and messages prefilled.
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

    const data = await getTodayBirthdayCelebrants(user.id, isAdmin, lang);

    return NextResponse.json({
      success: true,
      ...data,
      isAdmin,
    });
  } catch (err: any) {
    console.error("GET /api/customers/birthdays error:", err);
    return NextResponse.json(
      { error: err?.message || "Internal server error fetching birthday reminders." },
      { status: 500 }
    );
  }
}

/**
 * POST /api/customers/birthdays
 * Manually updates the status after the administrator has actually sent the wish.
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
    const { customer_id } = body;

    if (!customer_id || typeof customer_id !== "string") {
      return NextResponse.json(
        { error: "customer_id is required." },
        { status: 400 }
      );
    }

    const result = await markBirthdayWishSent(customer_id, user.id);

    return NextResponse.json({
      ...result,
    });
  } catch (err: any) {
    console.error("POST /api/customers/birthdays error:", err);
    return NextResponse.json(
      { error: err?.message || "Failed to update wish status." },
      { status: 500 }
    );
  }
}
