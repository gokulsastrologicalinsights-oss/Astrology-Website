import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { compactDasaTree } from "@/lib/horoscope-storage-utils";
import { validateAndNormalizePhone } from "@/lib/phone-utils";
import {
  getOrCreateCustomerRecord,
  listCustomersForUser,
} from "@/lib/customer-service";

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
        "id, user_id, display_number, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, calculation_result, created_at, updated_at",
        { count: "exact" }
      );

    if (!viewAll) {
      query = query.eq("user_id", user.id);
    }

    if (search) {
      query = query.ilike("person_name", `%${search}%`);
    }

    // Display saved horoscopes in descending order of generation/creation time (newest first)
    // with stable secondary sort on display_number DESC and primary key id DESC
    query = query
      .order("created_at", { ascending: false })
      .order("display_number", { ascending: false })
      .order("id", { ascending: false })
      .range(offset, offset + limit - 1);

    const { data: horoscopes, count, error } = await query;

    if (error) {
      console.error("Supabase saved_horoscopes query error:", error);
      return NextResponse.json(
        { error: error.message || "Failed to retrieve saved horoscopes." },
        { status: 500 }
      );
    }

    // Load authoritative customer profiles to enrich horoscopes & detect legacy missing contacts
    const allCustomers = await listCustomersForUser(user.id, isAdmin);
    const customerById = new Map(allCustomers.map((c) => [c.id, c]));
    const customerByNameDob = new Map(
      allCustomers.map((c) => [`${c.full_name.trim().toLowerCase()}_${c.birth_date}`, c])
    );

    let enrichedHoroscopes = (horoscopes || []).map((h) => {
      const calc = h.calculation_result || {};
      const savedCust = calc.customer;
      let matchedCust = savedCust?.id ? customerById.get(savedCust.id) : undefined;
      if (!matchedCust) {
        matchedCust = customerByNameDob.get(`${h.person_name.trim().toLowerCase()}_${h.birth_date}`);
      }

      const hasPhone = !!matchedCust?.normalized_phone && !matchedCust?.is_legacy_without_phone;

      // Clean calculation_result from lightweight listing to preserve bandwidth
      const { calculation_result: _, ...cleanHoro } = h;

      const resolvedBirthTime =
        (h.birth_time && typeof h.birth_time === "string" && h.birth_time.trim()) ||
        (calc.clientInputs?.birthTime && typeof calc.clientInputs.birthTime === "string" && calc.clientInputs.birthTime.trim()) ||
        (calc.clientInputs?.birth_time && typeof calc.clientInputs.birth_time === "string" && calc.clientInputs.birth_time.trim()) ||
        (calc.horoscope?.birth_time && typeof calc.horoscope.birth_time === "string" && calc.horoscope.birth_time.trim()) ||
        null;

      return {
        ...cleanHoro,
        birth_time: resolvedBirthTime,
        customer_id: matchedCust?.id || savedCust?.id || null,
        customer: hasPhone ? matchedCust : null,
        customer_phone: matchedCust?.normalized_phone || savedCust?.normalized_phone || null,
        customer_country_code: matchedCust?.country_code || savedCust?.country_code || null,
        whatsapp_number: matchedCust?.whatsapp_number || savedCust?.whatsapp_number || null,
        has_missing_contact: !hasPhone,
      };
    });

    // If admin viewAll, enrich with owner username/display_name
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
      customer_full_name,
      birth_date,
      birth_time,
      timezone,
      birthplace,
      latitude,
      longitude,
      ayanamsa_id,
      house_system_id,
      calculation_result,
      customer_phone,
      country_code,
      customer_id,
    } = body;

    // 1. Mandatory Customer Full Name & Date of Birth
    const finalCustomerName = (customer_full_name || person_name || "").trim();
    if (!finalCustomerName) {
      return NextResponse.json(
        { error: "Customer Full Name is required." },
        { status: 400 }
      );
    }

    if (!birth_date || typeof birth_date !== "string") {
      return NextResponse.json(
        { error: "Date of Birth is required (YYYY-MM-DD)." },
        { status: 400 }
      );
    }

    // 2. Optional Customer WhatsApp Number & Country Code
    const effectiveCountryCode = (country_code || "+91").trim();
    const rawCustomerPhone = (
      customer_phone ||
      calculation_result?.customer?.phone_number ||
      calculation_result?.customer_phone ||
      ""
    ).toString().trim();

    if (rawCustomerPhone) {
      const phoneValidation = validateAndNormalizePhone(rawCustomerPhone, effectiveCountryCode);
      if (!phoneValidation.isValid) {
        return NextResponse.json(
          { error: phoneValidation.error || "Invalid WhatsApp phone number." },
          { status: 400 }
        );
      }
    }

    // 3. Authoritative Customer Deduplication & Provisioning
    const { customer: authoritativeCustomer } = await getOrCreateCustomerRecord(user.id, {
      customerId: customer_id,
      fullName: finalCustomerName,
      birthDate: birth_date,
      countryCode: effectiveCountryCode,
      phoneNumber: rawCustomerPhone || undefined,
    });

    const trimmedName = authoritativeCustomer.full_name;
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
    // Compacts Dasa hierarchy to 3 levels (~200 KB) while preserving full accuracy and Benefit Bhavas
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
      customer: {
        id: authoritativeCustomer.id,
        full_name: authoritativeCustomer.full_name,
        birth_date: authoritativeCustomer.birth_date,
        country_code: authoritativeCustomer.country_code,
        phone_number: authoritativeCustomer.phone_number,
        normalized_phone: authoritativeCustomer.normalized_phone,
        whatsapp_number: authoritativeCustomer.whatsapp_number,
      },
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

    // 4. Insert new horoscope record with verified user_id
    const isUuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
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

    if (authoritativeCustomer.id && isUuid.test(authoritativeCustomer.id)) {
      insertPayload.customer_id = authoritativeCustomer.id;
    }

    if (nextDisplayNumber && nextDisplayNumber > 0) {
      insertPayload.display_number = nextDisplayNumber;
    }

    // Use adminClient for insertion to guarantee reliable persistence for the authenticated user session
    const dbClient = createAdminClient();
    let { data: newRecord, error: insertError } = await dbClient
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
        const { data: raceRecord } = await dbClient
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
        const retryRes = await dbClient
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
        if (retryRes.error) {
          insertError = retryRes.error;
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
