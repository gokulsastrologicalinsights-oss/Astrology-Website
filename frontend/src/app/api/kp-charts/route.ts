import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { listSavedKpCharts, saveKpChart } from "@/lib/api";
import { validateAndNormalizePhone } from "@/lib/phone-utils";
import { getOrCreateCustomerRecord } from "@/lib/customer-service";

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
 * Persists a KP chart calculation snapshot with mandatory customer contact validation.
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
    const chartType = payload.chart_type || "natal";

    // Customer identification & optional contact details during client horoscope creation
    if (chartType === "natal") {
      const customerName = (payload.customer_full_name || payload.title || "").trim();
      if (!customerName) {
        return NextResponse.json(
          { error: "Customer Full Name is required." },
          { status: 400 }
        );
      }
      if (!payload.birth_date) {
        return NextResponse.json(
          { error: "Date of Birth is required for client horoscope." },
          { status: 400 }
        );
      }

      const countryCode = (payload.country_code || "+91").trim();
      const rawPhone = (payload.customer_phone || "").trim();

      if (rawPhone) {
        const phoneVal = validateAndNormalizePhone(rawPhone, countryCode);
        if (!phoneVal.isValid) {
          return NextResponse.json(
            { error: phoneVal.error || "Invalid WhatsApp phone number." },
            { status: 400 }
          );
        }
      }

      // Authoritative Customer Deduplication & Provisioning
      const { customer } = await getOrCreateCustomerRecord(session.user.id, {
        customerId: payload.customer_id,
        fullName: customerName,
        birthDate: payload.birth_date,
        countryCode,
        phoneNumber: rawPhone || undefined,
      });

      payload.customer_id = customer.id;
      payload.customer_phone = customer.phone_number || null;
      payload.country_code = customer.country_code;
      payload.normalized_phone = customer.normalized_phone || null;
      payload.whatsapp_number = customer.whatsapp_number || null;
      payload.customer_full_name = customer.full_name;
    }

    const data = await saveKpChart(session.access_token, payload);
    return NextResponse.json(data, { status: 201 });
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || "Failed to save KP chart." },
      { status: 400 }
    );
  }
}
