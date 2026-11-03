import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import {
  setPinnedStatus,
  isHoroscopePinned,
} from "@/lib/pinned-horoscopes-service";

/**
 * POST /api/horoscopes/[id]/pin
 * Pins or unpins a horoscope for the authenticated user.
 * Pinned horoscopes are displayed as the first chart(s) at the top of the dashboard
 * and the open saved charts directories.
 *
 * Body (optional JSON):
 *   - is_pinned: boolean (if omitted, toggles current status)
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
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

    // Verify record existence
    const { data: record, error: findError } = await supabase
      .from("saved_horoscopes")
      .select("id, user_id")
      .eq("id", id)
      .single();

    if (findError || !record) {
      return NextResponse.json(
        { error: "Horoscope not found or access denied." },
        { status: 404 }
      );
    }

    // Ownership or admin check
    if (record.user_id !== user.id) {
      const { data: profile } = await supabase
        .from("profiles")
        .select("role")
        .eq("id", user.id)
        .single();

      if (profile?.role !== "admin") {
        return NextResponse.json(
          { error: "Forbidden: You are not authorized to pin this horoscope." },
          { status: 403 }
        );
      }
    }

    // Determine target pinned state
    let targetPinned: boolean;
    try {
      const body = await request.json();
      if (typeof body.is_pinned === "boolean") {
        targetPinned = body.is_pinned;
      } else {
        const current = await isHoroscopePinned(user.id, id);
        targetPinned = !current;
      }
    } catch {
      // Body not supplied; toggle current status
      const current = await isHoroscopePinned(user.id, id);
      targetPinned = !current;
    }

    const result = await setPinnedStatus(user.id, id, targetPinned);

    return NextResponse.json({
      success: true,
      horoscope_id: id,
      is_pinned: result.is_pinned,
    });
  } catch (err: any) {
    console.error("POST /api/horoscopes/[id]/pin error:", err?.message || err);
    return NextResponse.json(
      { error: "Internal error updating pinned status." },
      { status: 500 }
    );
  }
}
