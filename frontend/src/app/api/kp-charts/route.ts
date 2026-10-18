import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { listSavedKpCharts, saveKpChart } from "@/lib/api";

/**
 * GET /api/kp-charts
 * Lists saved KP charts for the authenticated user (or all if admin).
 */
export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session?.access_token) {
      return NextResponse.json(
        { error: "Unauthorized access: Sign-in required." },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get("limit") || "50", 10);
    const offset = parseInt(searchParams.get("offset") || "0", 10);
    const chartType = searchParams.get("chart_type") || undefined;
    const allUsers = searchParams.get("all_users") === "true";

    const data = await listSavedKpCharts(
      session.access_token,
      chartType,
      limit,
      offset,
      allUsers
    );
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || "Failed to retrieve saved KP charts." },
      { status: 500 }
    );
  }
}

/**
 * POST /api/kp-charts
 * Persists a KP chart calculation snapshot.
 */
export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session?.access_token) {
      return NextResponse.json(
        { error: "Unauthorized access: Sign-in required." },
        { status: 401 }
      );
    }

    const payload = await request.json();
    const data = await saveKpChart(session.access_token, payload);
    return NextResponse.json(data, { status: 201 });
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || "Failed to save KP chart." },
      { status: 500 }
    );
  }
}
