import { NextResponse, type NextRequest } from "next/server";
import { listSavedMuhurtas, saveMuhurtaSelection } from "@/lib/api";
import { createClient } from "@/lib/supabase/server";

export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session?.access_token) {
      return NextResponse.json({ error: "Unauthorized access: Sign-in required." }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get("limit") || "50", 10);
    const offset = parseInt(searchParams.get("offset") || "0", 10);
    const search = searchParams.get("search") || undefined;
    const allUsers = searchParams.get("all_users") === "true";

    const data = await listSavedMuhurtas(session.access_token, limit, offset, search, allUsers);
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || "Failed to retrieve saved Muhurtas." },
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
      return NextResponse.json({ error: "Unauthorized access: Sign-in required." }, { status: 401 });
    }

    const payload = await request.json();
    const data = await saveMuhurtaSelection(session.access_token, payload);
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || "Failed to save Muhurta selection." },
      { status: 500 }
    );
  }
}
