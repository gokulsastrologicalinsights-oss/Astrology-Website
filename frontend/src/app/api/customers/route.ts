import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import {
  listCustomersForUser,
  getOrCreateCustomerRecord,
} from "@/lib/customer-service";

/**
 * GET /api/customers
 * Retrieves unique customer profiles for autocomplete and deduplication.
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
    const search = searchParams.get("search") || "";

    const { data: profile } = await supabase
      .from("profiles")
      .select("role")
      .eq("id", user.id)
      .single();

    const isAdmin = profile?.role === "admin";
    const customers = await listCustomersForUser(user.id, isAdmin, search);

    return NextResponse.json({
      success: true,
      customers,
      totalCount: customers.length,
    });
  } catch (err: any) {
    console.error("GET /api/customers error:", err);
    return NextResponse.json(
      { error: err?.message || "Internal server error fetching customers." },
      { status: 500 }
    );
  }
}

/**
 * POST /api/customers
 * Creates or deduplicates a customer profile with validated phone number.
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
    const { full_name, birth_date, country_code, phone_number, customer_id } = body;

    if (!full_name || typeof full_name !== "string" || !full_name.trim()) {
      return NextResponse.json(
        { error: "Customer full name is required." },
        { status: 400 }
      );
    }

    if (!birth_date || typeof birth_date !== "string") {
      return NextResponse.json(
        { error: "Customer birth date is required (YYYY-MM-DD)." },
        { status: 400 }
      );
    }

    const rawPhone = (phone_number || "").toString().trim();

    const { customer, isNew } = await getOrCreateCustomerRecord(user.id, {
      customerId: customer_id,
      fullName: full_name,
      birthDate: birth_date,
      countryCode: country_code || "+91",
      phoneNumber: rawPhone || undefined,
    });

    return NextResponse.json(
      {
        success: true,
        customer,
        isNew,
      },
      { status: isNew ? 201 : 200 }
    );
  } catch (err: any) {
    console.error("POST /api/customers error:", err);
    return NextResponse.json(
      { error: err?.message || "Failed to create or update customer." },
      { status: 400 }
    );
  }
}
