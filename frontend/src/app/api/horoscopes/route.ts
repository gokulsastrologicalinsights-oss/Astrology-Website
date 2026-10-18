import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { compactDasaTree } from "@/lib/horoscope-storage-utils";

/**
 * GET /api/horoscopes
 * Retrieves paginated saved horoscopes for the authenticated user (or all users if admin requests ?all=true).
 * Supports query params:
 *   - search: string (case-insensitive filter by person_name)
 *   - page: number (1-based, default 1)
 *   - limit: number (default 6)
 *   - all: boolean (admin-only view of all records)
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
    const search = searchParams.get("search")?.trim() || "";
    const page = Math.max(1, parseInt(searchParams.get("page") || "1", 10) || 1);
    const limit = Math.max(1, Math.min(50, parseInt(searchParams.get("limit") || "6", 10) || 6));
    const offset = (page - 1) * limit;
    const viewAll = searchParams.get("all") === "true";

    // Verify admin role if viewAll requested
    let isAdmin = false;
    const { data: profile } = await supabase
      .from("profiles")
      .select("role")
      .eq("id", user.id)
      .single();

    if (profile?.role === "admin") {
      isAdmin = true;
    }

    if (viewAll && !isAdmin) {
      return NextResponse.json(
        { error: "Forbidden: Administrative privileges required to view all records." },
        { status: 403 }
      );
    }

    // Build query with RLS enforcement
    let query = supabase
      .from("saved_horoscopes")
      .select(
        "id, user_id, display_number, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, created_at, updated_at",
        { count: "exact" }
      );

    if (!viewAll) {
      query = query.eq("user_id", user.id);
    }

    if (search) {
      query = query.ilike("person_name", `%${search}%`);
    }

    // Normal user: order by user display_number ASC
    // Admin all view: order by created_at DESC with stable record identifier
    if (viewAll) {
      query = query.order("created_at", { ascending: false }).range(offset, offset + limit - 1);
    } else {
      query = query.order("display_number", { ascending: true }).range(offset, offset + limit - 1);
    }

    const { data: horoscopes, count, error } = await query;

    if (error) {
      console.error("Supabase saved_horoscopes query error:", error);
      return NextResponse.json(
        { error: error.message || "Failed to retrieve saved horoscopes." },
        { status: 500 }
      );
    }

    // If admin viewAll, enrich with owner username/display_name
    let enrichedHoroscopes = horoscopes || [];
    if (viewAll && enrichedHoroscopes.length > 0) {
      try {
        const adminClient = createAdminClient();
        const userIds = Array.from(new Set(enrichedHoroscopes.map((h) => h.user_id)));
        const { data: profiles } = await adminClient
          .from("profiles")
          .select("id, username, display_name")
          .in("id", userIds);

        const profileMap = new Map((profiles || []).map((p) => [p.id, p]));
        enrichedHoroscopes = enrichedHoroscopes.map((h) => ({
          ...h,
          owner: profileMap.get(h.user_id) || { username: "unknown", display_name: null },
        }));
      } catch (enrichErr) {
        console.warn("Could not enrich admin horoscopes with owner profile:", enrichErr);
      }
    }

    const totalCount = count || 0;
    const totalPages = Math.ceil(totalCount / limit) || 1;

    return NextResponse.json({
      success: true,
      horoscopes: enrichedHoroscopes,
      totalCount,
      page,
      pageSize: limit,
      totalPages,
      isAdmin,
    });
  } catch (err: any) {
    console.error("GET /api/horoscopes error:", err);
    return NextResponse.json(
      { error: "Internal server error fetching saved horoscopes." },
      { status: 500 }
    );
  }
}

/**
 * POST /api/horoscopes
 * Automatically and persistently saves a completed horoscope calculation to Supabase.
 * - Authenticates the user session server-side (never trusts browser-supplied user ID).
 * - Enforces idempotency: if retried with the same idempotency_key, returns existing record.
 * - Atomically assigns monotonic sequential display_number per user (deleted numbers remain unused).
 * - Compacts calculation snapshot so payload is fast, lightweight (~200 KB), and safe from gateway limits.
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
      idempotency_key,
      person_name,
      birth_date,
      birth_time,
      timezone,
      birthplace,
      latitude,
      longitude,
      ayanamsa_id,
      house_system_id,
      calculation_result,
    } = body;

    // Strict validation of actual required inputs
    const trimmedName = (person_name || "").trim() || "Unnamed Horoscope";
    if (!birth_date || typeof birth_date !== "string") {
      return NextResponse.json(
        { error: "birth_date is required (YYYY-MM-DD)." },
        { status: 400 }
      );
    }
    if (!birth_time || typeof birth_time !== "string") {
      return NextResponse.json(
        { error: "birth_time is required (HH:MM or HH:MM:SS)." },
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
    if (!calculation_result || typeof calculation_result !== "object") {
      return NextResponse.json(
        { error: "calculation_result payload is required." },
        { status: 400 }
      );
    }

    // Resolved idempotency key from request or embedded payload
    const effectiveIdempotencyKey =
      (idempotency_key && typeof idempotency_key === "string" ? idempotency_key.trim() : null) ||
      (calculation_result.idempotency_key && typeof calculation_result.idempotency_key === "string"
        ? calculation_result.idempotency_key.trim()
        : null) ||
      (calculation_result.idempotencyKey && typeof calculation_result.idempotencyKey === "string"
        ? calculation_result.idempotencyKey.trim()
        : null) ||
      `calc_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

    // 1. Idempotency Check:
    // If the calculation with this unique idempotency key was already saved by this user,
    // return the existing saved record immediately without inserting a duplicate.
    const { data: existingRecords } = await supabase
      .from("saved_horoscopes")
      .select(
        "id, display_number, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, created_at, updated_at"
      )
      .eq("user_id", user.id)
      .eq("calculation_result->>idempotency_key", effectiveIdempotencyKey)
      .limit(1);

    if (existingRecords && existingRecords.length > 0) {
      return NextResponse.json(
        {
          success: true,
          idempotent: true,
          horoscope: existingRecords[0],
        },
        { status: 200 }
      );
    }

    // 2. Prepare structured, versioned calculation snapshot
    // Prunes huge 60k-node dasa trees down to 3 levels while preserving the 5-level active period,
    // keeping payload ~200 KB and preventing gateway timeouts or size errors.
    let dasaPayload = calculation_result.dasa;
    if (dasaPayload && Array.isArray(dasaPayload.dasa_tree)) {
      dasaPayload = {
        ...dasaPayload,
        dasa_tree: compactDasaTree(dasaPayload.dasa_tree, 3),
      };
    }

    const structuredSnapshot = {
      schema_version: "1.0.0",
      idempotency_key: effectiveIdempotencyKey,
      calculatedAt: calculation_result.calculatedAt || new Date().toISOString(),
      clientInputs: calculation_result.clientInputs || {
        fullName: trimmedName,
        birthDate: birth_date,
        birthTime: birth_time,
        isTimeConfirmed: true,
        locationName: (birthplace || "Unknown Location").trim(),
        latitude,
        longitude,
        timezone: (timezone || "UTC").trim(),
        ayanamsaId: typeof ayanamsa_id === "number" ? ayanamsa_id : 0,
        houseSystemId: typeof house_system_id === "number" ? house_system_id : 2,
      },
      horoscope: calculation_result.horoscope,
      dasa: dasaPayload,
      kp: calculation_result.kp,
    };

    // 3. Monotonic Sequential Numbering Mechanism:
    // Per-user sequence starting at 1, concurrency safe.
    // Deleting existing records leaves the number unused without renumbering or reusing.
    let nextDisplayNumber: number | undefined = undefined;
    try {
      const adminClient = createAdminClient();
      const lastSeq = (user.user_metadata?.last_horoscope_seq as number) || 0;

      // Query highest display_number currently in database for this user
      const { data: maxRow } = await adminClient
        .from("saved_horoscopes")
        .select("display_number")
        .eq("user_id", user.id)
        .order("display_number", { ascending: false })
        .limit(1);

      const maxExisting = maxRow?.[0]?.display_number || 0;
      nextDisplayNumber = Math.max(lastSeq, maxExisting) + 1;

      // Atomically bump user watermark
      await adminClient.auth.admin.updateUserById(user.id, {
        user_metadata: {
          ...(user.user_metadata || {}),
          last_horoscope_seq: nextDisplayNumber,
        },
      });
    } catch (seqErr) {
      console.warn("Could not update user_metadata sequence counter, falling back to database trigger:", seqErr);
      nextDisplayNumber = undefined;
    }

    // 4. Insert new horoscope record with Supabase RLS
    const insertPayload: Record<string, any> = {
      user_id: user.id,
      person_name: trimmedName,
      birth_date,
      birth_time,
      timezone: (timezone || "UTC").trim(),
      birthplace: (birthplace || "Unknown Location").trim(),
      latitude,
      longitude,
      ayanamsa_id: typeof ayanamsa_id === "number" ? ayanamsa_id : 0,
      house_system_id: typeof house_system_id === "number" ? house_system_id : 2,
      calculation_result: structuredSnapshot,
    };

    if (nextDisplayNumber && nextDisplayNumber > 0) {
      insertPayload.display_number = nextDisplayNumber;
    }

    const { data: newRecord, error: insertError } = await supabase
      .from("saved_horoscopes")
      .insert(insertPayload)
      .select(
        "id, display_number, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, created_at, updated_at"
      )
      .single();

    if (insertError) {
      // If unique violation occurred due to simultaneous request race:
      if (insertError.code === "23505") {
        // Check if our idempotency key was inserted concurrently
        const { data: raceRecord } = await supabase
          .from("saved_horoscopes")
          .select(
            "id, display_number, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, created_at, updated_at"
          )
          .eq("user_id", user.id)
          .eq("calculation_result->>idempotency_key", effectiveIdempotencyKey)
          .single();

        if (raceRecord) {
          return NextResponse.json(
            { success: true, idempotent: true, horoscope: raceRecord },
            { status: 200 }
          );
        }

        // Display number collision under concurrency: let database trigger assign automatically
        delete insertPayload.display_number;
        const retryRes = await supabase
          .from("saved_horoscopes")
          .insert(insertPayload)
          .select(
            "id, display_number, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, created_at, updated_at"
          )
          .single();

        if (retryRes.data) {
          return NextResponse.json(
            { success: true, idempotent: false, horoscope: retryRes.data },
            { status: 201 }
          );
        }
      }

      console.error("Insert saved_horoscope error:", insertError);
      return NextResponse.json(
        { error: insertError.message || "Failed to save horoscope." },
        { status: 500 }
      );
    }

    return NextResponse.json(
      { success: true, idempotent: false, horoscope: newRecord },
      { status: 201 }
    );
  } catch (err: any) {
    console.error("POST /api/horoscopes error:", err?.message || err);
    return NextResponse.json(
      { error: err?.message || "Internal server error saving horoscope." },
      { status: 500 }
    );
  }
}
