import { NextResponse, type NextRequest } from "next/server";
import { getOccasions, addCustomOccasion } from "@/lib/api";
import { createClient } from "@/lib/supabase/server";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const includeDisabled = searchParams.get("include_disabled") === "true";
    const data = await getOccasions(includeDisabled);
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || "Failed to load occasions." },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session?.access_token) {
      return NextResponse.json({ error: "Unauthorized access." }, { status: 401 });
    }

    const payload = await request.json();
    const data = await addCustomOccasion(session.access_token, payload);
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || "Failed to create custom occasion." },
      { status: 500 }
    );
  }
}
