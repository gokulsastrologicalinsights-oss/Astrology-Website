import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { updateCustomerContactDetails } from "@/lib/customer-service";

/**
 * PUT /api/customers/[id]
 * Updates customer contact information (phone number, name, DOB)
 * Authoritative record updates across all linked horoscopes.
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

    const body = await request.json();
    const { full_name, birth_date, country_code, phone_number } = body;

    if (!phone_number || typeof phone_number !== "string" || !phone_number.trim()) {
      return NextResponse.json(
        { error: "Valid customer WhatsApp number is required." },
        { status: 400 }
      );
    }

    const updated = await updateCustomerContactDetails(id, {
      fullName: full_name,
      birthDate: birth_date,
      countryCode: country_code || "+91",
      phoneNumber: phone_number,
    });

    return NextResponse.json({
      success: true,
      customer: updated,
    });
  } catch (err: any) {
    console.error("PUT /api/customers/[id] error:", err);
    return NextResponse.json(
      { error: err?.message || "Failed to update customer contact details." },
      { status: 400 }
    );
  }
}
