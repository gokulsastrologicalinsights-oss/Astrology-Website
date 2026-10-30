import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { updateCustomerContactDetails } from "@/lib/customer-service";

async function handleUpdateCustomer(
  request: NextRequest,
  paramsPromise: Promise<{ id: string }>
) {
  try {
    const { id } = await paramsPromise;
    let resolvedId = id;
    try {
      resolvedId = decodeURIComponent(id);
    } catch {
      resolvedId = id;
    }

    if (!resolvedId) {
      return NextResponse.json(
        { error: "Customer ID is required." },
        { status: 400 }
      );
    }

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

    let body: any = {};
    try {
      body = await request.json();
    } catch {
      return NextResponse.json(
        { error: "Invalid JSON request payload." },
        { status: 400 }
      );
    }

    const phone_number = body.phone_number ?? body.phoneNumber;
    const country_code = body.country_code ?? body.countryCode ?? "+91";
    const full_name = body.full_name ?? body.fullName;
    const birth_date = body.birth_date ?? body.birthDate;
    const horoscope_id = body.horoscope_id ?? body.horoscopeId;

    if (!phone_number || typeof phone_number !== "string" || !phone_number.trim()) {
      return NextResponse.json(
        { error: "Valid customer WhatsApp number is required." },
        { status: 400 }
      );
    }

    const updated = await updateCustomerContactDetails(resolvedId, {
      fullName: full_name,
      birthDate: birth_date,
      countryCode: country_code || "+91",
      phoneNumber: phone_number.trim(),
      horoscopeId: horoscope_id,
    });

    return NextResponse.json({
      success: true,
      customer: updated,
    });
  } catch (err: any) {
    console.error("Update /api/customers/[id] error:", err);
    return NextResponse.json(
      { error: err?.message || "Failed to update customer contact details." },
      { status: 400 }
    );
  }
}

/**
 * PUT /api/customers/[id]
 * Updates customer contact information (phone number, name, DOB)
 * Authoritative record updates across linked horoscopes.
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  return handleUpdateCustomer(request, params);
}

/**
 * PATCH /api/customers/[id]
 * Partially updates customer contact information (phone number, country code)
 */
export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  return handleUpdateCustomer(request, params);
}
