import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";

/**
 * GET /api/horoscopes/[id]
 * Retrieves a single saved horoscope including its stored calculation_result snapshot.
 * Enforces ownership and admin permissions.
 */
export async function GET(
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

    // Query single record
    const { data: record, error } = await supabase
      .from("saved_horoscopes")
      .select("*")
      .eq("id", id)
      .single();

    if (error || !record) {
      return NextResponse.json(
        { error: "Horoscope not found or access denied." },
        { status: 404 }
      );
    }

    // Verify ownership (or admin privileges)
    if (record.user_id !== user.id) {
      const { data: profile } = await supabase
        .from("profiles")
        .select("role")
        .eq("id", user.id)
        .single();

      if (profile?.role !== "admin") {
        return NextResponse.json(
          { error: "Forbidden: You are not authorized to view this horoscope." },
          { status: 403 }
        );
      }
    }

    return NextResponse.json({
      success: true,
      horoscope: record,
    });
  } catch (err: any) {
    console.error("GET /api/horoscopes/[id] error:", err?.message || err);
    return NextResponse.json(
      { error: "Internal error retrieving saved horoscope." },
      { status: 500 }
    );
  }
}

/**
 * PUT /api/horoscopes/[id]
 * Updates the subject's birth details metadata.
 * CRITICAL RULES:
 * 1. Preserves the permanent sequential display_number (NEVER mutated)
 * 2. Updates the existing record without creating a duplicate record
 * 3. Does NOT alter the original calculation snapshot
 * 4. Strict ownership enforcement: only record owner or authorized admin can update
 */
export async function PUT(
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

    // Verify existing record and ownership
    const { data: existing, error: findError } = await supabase
      .from("saved_horoscopes")
      .select("id, user_id, display_number")
      .eq("id", id)
      .single();

    if (findError || !existing) {
      return NextResponse.json(
        { error: "Horoscope not found or access denied." },
        { status: 404 }
      );
    }

    // Check admin role if not owner
    let isAdmin = false;
    if (existing.user_id !== user.id) {
      const { data: profile } = await supabase
        .from("profiles")
        .select("role")
        .eq("id", user.id)
        .single();

      if (profile?.role !== "admin") {
        return NextResponse.json(
          { error: "Forbidden: You are not authorized to edit this horoscope." },
          { status: 403 }
        );
      }
      isAdmin = true;
    }

    const body = await request.json();
    const {
      person_name,
      birth_date,
      birth_time,
      timezone,
      birthplace,
      latitude,
      longitude,
      ayanamsa_id,
      house_system_id,
    } = body;

    // Strict validation
    if (!person_name || typeof person_name !== "string" || !person_name.trim()) {
      return NextResponse.json(
        { error: "Person's name is required." },
        { status: 400 }
      );
    }
    if (!birth_date || typeof birth_date !== "string") {
      return NextResponse.json(
        { error: "birth_date is required (YYYY-MM-DD)." },
        { status: 400 }
      );
    }
    if (!birth_time || typeof birth_time !== "string") {
      return NextResponse.json(
        { error: "birth_time is required." },
        { status: 400 }
      );
    }
    if (
      latitude === undefined ||
      typeof latitude !== "number" ||
      latitude < -90 ||
      latitude > 90
    ) {
      return NextResponse.json(
        { error: "Valid latitude between -90 and 90 is required." },
        { status: 400 }
      );
    }
    if (
      longitude === undefined ||
      typeof longitude !== "number" ||
      longitude < -180 ||
      longitude > 180
    ) {
      return NextResponse.json(
        { error: "Valid longitude between -180 and 180 is required." },
        { status: 400 }
      );
    }

    // Perform update
    const clientToUse = isAdmin ? createAdminClient() : supabase;
    const { data: updatedRecord, error: updateError } = await clientToUse
      .from("saved_horoscopes")
      .update({
        person_name: person_name.trim(),
        birth_date,
        birth_time,
        timezone: (timezone || "UTC").trim(),
        birthplace: (birthplace || "Unknown Location").trim(),
        latitude,
        longitude,
        ayanamsa_id: typeof ayanamsa_id === "number" ? ayanamsa_id : 0,
        house_system_id: typeof house_system_id === "number" ? house_system_id : 2,
        updated_at: new Date().toISOString(),
      })
      .eq("id", id)
      .select(
        "id, display_number, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, created_at, updated_at"
      )
      .single();

    if (updateError) {
      console.error("Update saved_horoscope error:", updateError);
      return NextResponse.json(
        { error: updateError.message || "Failed to update horoscope record." },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      horoscope: updatedRecord,
    });
  } catch (err: any) {
    console.error("PUT /api/horoscopes/[id] error:", err?.message || err);
    return NextResponse.json(
      { error: "Internal error updating saved horoscope." },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/horoscopes/[id]
 * Deletes a saved horoscope.
 * - Enforces ownership (or authorized admin role).
 * - Sequential numbering of remaining records is preserved.
 * - The deleted sequential number remains unused and is not reused.
 */
export async function DELETE(
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

    // Check existing record
    const { data: existing, error: findError } = await supabase
      .from("saved_horoscopes")
      .select("id, user_id, display_number")
      .eq("id", id)
      .single();

    if (findError || !existing) {
      return NextResponse.json(
        { error: "Horoscope not found or access denied." },
        { status: 404 }
      );
    }

    let isAdmin = false;
    if (existing.user_id !== user.id) {
      const { data: profile } = await supabase
        .from("profiles")
        .select("role")
        .eq("id", user.id)
        .single();

      if (profile?.role !== "admin") {
        return NextResponse.json(
          { error: "Forbidden: You are not authorized to delete this horoscope." },
          { status: 403 }
        );
      }
      isAdmin = true;
    }

    // Delete record using appropriate client
    const clientToUse = isAdmin ? createAdminClient() : supabase;
    const { error: deleteError } = await clientToUse
      .from("saved_horoscopes")
      .delete()
      .eq("id", id);

    if (deleteError) {
      return NextResponse.json(
        { error: deleteError.message || "Failed to delete horoscope." },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      message: "Horoscope deleted successfully.",
      deleted_number: existing.display_number,
    });
  } catch (err: any) {
    console.error("DELETE /api/horoscopes/[id] error:", err?.message || err);
    return NextResponse.json(
      { error: "Internal error deleting saved horoscope." },
      { status: 500 }
    );
  }
}
