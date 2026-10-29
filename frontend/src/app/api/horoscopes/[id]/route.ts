import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { compactDasaTree } from "@/lib/horoscope-storage-utils";
import { validateAndNormalizePhone } from "@/lib/phone-utils";
import {
  listCustomersForUser,
  getOrCreateCustomerRecord,
} from "@/lib/customer-service";

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

    // Enrich horoscope with authoritative customer contact information
    const adminClient = createAdminClient();
    let customerInfo = record.calculation_result?.customer || null;
    try {
      const customers = await listCustomersForUser(user.id, true);
      const matched =
        customers.find((c) => c.id === customerInfo?.id) ||
        customers.find(
          (c) =>
            c.full_name.trim().toLowerCase() === record.person_name.trim().toLowerCase() &&
            c.birth_date === record.birth_date
        );
      if (matched && matched.normalized_phone && !matched.is_legacy_without_phone) {
        customerInfo = matched;
      }
    } catch {
      // Ignore
    }

    const hasPhone = !!customerInfo?.normalized_phone;

    const resolvedGender = record.calculation_result?.clientInputs?.gender || (record as any).gender || "male";
    return NextResponse.json({
      success: true,
      horoscope: {
        gender: resolvedGender,
        ...record,
        customer_id: customerInfo?.id || null,
        customer: hasPhone ? customerInfo : null,
        customer_phone: customerInfo?.normalized_phone || null,
        customer_country_code: customerInfo?.country_code || null,
        whatsapp_number: customerInfo?.whatsapp_number || null,
        has_missing_contact: !hasPhone,
      },
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
 * Updates the subject's birth details metadata and customer contact info,
 * and replaces the calculation snapshot in-place without duplicating the record.
 * CRITICAL RULES:
 * 1. Preserves the permanent sequential display_number and ID (NEVER duplicated or mutated)
 * 2. Replaces or updates the calculation snapshot in-place
 * 3. Strict ownership enforcement: only record owner or authorized admin can update
 * 4. Synchronizes customer contact details to authoritative customer record
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
      .select("id, user_id, display_number, calculation_result")
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
      customer_phone,
      country_code,
      customer_id,
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

    // Update or link customer contact info if customer_phone is provided
    let updatedCustomer = null;

    if (customer_phone && typeof customer_phone === "string" && customer_phone.trim()) {
      const effectiveCountryCode = (country_code || "+91").trim();
      const phoneVal = validateAndNormalizePhone(customer_phone, effectiveCountryCode);
      if (!phoneVal.isValid) {
        return NextResponse.json(
          { error: phoneVal.error || "Invalid WhatsApp phone number." },
          { status: 400 }
        );
      }

      const existingCustId = customer_id || existing.calculation_result?.customer?.id;
      const { customer } = await getOrCreateCustomerRecord(existing.user_id, {
        customerId: existingCustId,
        fullName: person_name.trim(),
        birthDate: birth_date,
        countryCode: effectiveCountryCode,
        phoneNumber: customer_phone,
      });

      updatedCustomer = customer;
    }

    const effectiveGender = (body.gender || body.calculation_result?.clientInputs?.gender || existing.calculation_result?.clientInputs?.gender || "male").toLowerCase();
    // Reconstruct calculation snapshot with fresh calculations or synchronized clientInputs
    let updatedCalculationResult = existing.calculation_result || {};

    if (body.calculation_result && typeof body.calculation_result === "object") {
      let dasaPayload = body.calculation_result.dasa;
      if (dasaPayload && Array.isArray(dasaPayload.dasa_tree)) {
        dasaPayload = {
          ...dasaPayload,
          dasa_tree: compactDasaTree(dasaPayload.dasa_tree, 3),
        };
      }

      const activeCust =
        updatedCustomer ||
        body.calculation_result.customer ||
        existing.calculation_result?.customer;

      updatedCalculationResult = {
        schema_version: "1.0.0",
        idempotency_key:
          body.calculation_result.idempotency_key ||
          existing.calculation_result?.idempotency_key ||
          `calc_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
        calculatedAt: body.calculation_result.calculatedAt || new Date().toISOString(),
        clientInputs: body.calculation_result.clientInputs || {
          fullName: person_name.trim(),
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
        horoscope: body.calculation_result.horoscope,
        dasa: dasaPayload !== undefined ? dasaPayload : body.calculation_result.dasa,
        kp: body.calculation_result.kp,
        customer: activeCust
          ? {
              id: activeCust.id,
              full_name: activeCust.full_name,
              birth_date: activeCust.birth_date,
              country_code: activeCust.country_code,
              phone_number: activeCust.phone_number,
              normalized_phone: activeCust.normalized_phone,
              whatsapp_number: activeCust.whatsapp_number,
            }
          : undefined,
      };
    } else {
      // If calculation_result was not passed, update clientInputs inside snapshot to match new metadata
      const activeCust = updatedCustomer || existing.calculation_result?.customer;
      updatedCalculationResult = {
        ...existing.calculation_result,
        clientInputs: {
          gender: effectiveGender,
          ...(existing.calculation_result?.clientInputs || {}),
          fullName: person_name.trim(),
          birthDate: birth_date,
          birthTime: birth_time,
          locationName: (birthplace || "Unknown Location").trim(),
          latitude,
          longitude,
          timezone: (timezone || "UTC").trim(),
          ayanamsaId: typeof ayanamsa_id === "number" ? ayanamsa_id : 0,
          houseSystemId: typeof house_system_id === "number" ? house_system_id : 2,
        },
        customer: activeCust
          ? {
              id: activeCust.id,
              full_name: activeCust.full_name,
              birth_date: activeCust.birth_date,
              country_code: activeCust.country_code,
              phone_number: activeCust.phone_number,
              normalized_phone: activeCust.normalized_phone,
              whatsapp_number: activeCust.whatsapp_number,
            }
          : undefined,
      };
    }

    // Perform update
    const clientToUse = isAdmin ? createAdminClient() : supabase;
    const isUuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    const updatePayload: Record<string, any> = {
      person_name: person_name.trim(),
      birth_date,
      birth_time,
      timezone: (timezone || "UTC").trim(),
      birthplace: (birthplace || "Unknown Location").trim(),
      latitude,
      longitude,
      ayanamsa_id: typeof ayanamsa_id === "number" ? ayanamsa_id : 0,
      house_system_id: typeof house_system_id === "number" ? house_system_id : 2,
      calculation_result: updatedCalculationResult,
      updated_at: new Date().toISOString(),
    };

    const effectiveCustId = updatedCustomer?.id || customer_id;
    if (effectiveCustId && isUuid.test(effectiveCustId)) {
      updatePayload.customer_id = effectiveCustId;
    }

    const { data: updatedRecord, error: updateError } = await clientToUse
      .from("saved_horoscopes")
      .update(updatePayload as any)
      .eq("id", id)
      .select(
        "id, display_number, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, calculation_result, created_at, updated_at"
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
      horoscope: {
        ...updatedRecord,
        customer: updatedCustomer || updatedCalculationResult.customer || null,
        has_missing_contact: !updatedCustomer && !updatedCalculationResult.customer?.normalized_phone,
      },
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
 * PATCH /api/horoscopes/[id]
 * Atomically updates the calculation snapshot of an existing horoscope record
 * (e.g. persisting newly calculated Doshas, Yogas, or Varga extensions).
 * - Enforces authentication and record ownership (or admin role).
 * - Deeply merges calculation_result with existing data to prevent erasing Dasa, KP, charts, or customer contact.
 * - Mutates only the existing record without creating duplicate rows or altering the permanent display_number.
 */
export async function PATCH(
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
      .select("id, user_id, display_number, calculation_result")
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
          { error: "Forbidden: You are not authorized to update this horoscope." },
          { status: 403 }
        );
      }
      isAdmin = true;
    }

    const body = await request.json();
    const incomingCalc = body.calculation_result;

    if (!incomingCalc || typeof incomingCalc !== "object") {
      return NextResponse.json(
        { error: "A valid calculation_result object is required for PATCH." },
        { status: 400 }
      );
    }

    const existingCalc = existing.calculation_result || {};
    const mergedHoroscope = {
      ...(existingCalc.horoscope || {}),
      ...(incomingCalc.horoscope || {}),
    };
    if (incomingCalc.doshas && !mergedHoroscope.doshas) {
      mergedHoroscope.doshas = incomingCalc.doshas;
    }

    const mergedCalculationResult = {
      ...existingCalc,
      ...incomingCalc,
      horoscope: mergedHoroscope,
      dasa: incomingCalc.dasa || existingCalc.dasa,
      kp: incomingCalc.kp || existingCalc.kp,
      customer: existingCalc.customer || incomingCalc.customer,
      updatedAt: new Date().toISOString(),
    };

    const clientToUse = isAdmin ? createAdminClient() : supabase;
    const { data: updatedRecord, error: updateError } = await clientToUse
      .from("saved_horoscopes")
      .update({
        calculation_result: mergedCalculationResult,
        updated_at: new Date().toISOString(),
      })
      .eq("id", id)
      .select(
        "id, display_number, person_name, birth_date, birth_time, timezone, birthplace, latitude, longitude, ayanamsa_id, house_system_id, calculation_result, created_at, updated_at"
      )
      .single();

    if (updateError) {
      console.error("PATCH saved_horoscopes error:", updateError);
      return NextResponse.json(
        { error: updateError.message || "Failed to update horoscope calculation." },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      horoscope: updatedRecord,
    });
  } catch (err: any) {
    console.error("PATCH /api/horoscopes/[id] error:", err?.message || err);
    return NextResponse.json(
      { error: "Internal error updating saved horoscope calculation." },
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
