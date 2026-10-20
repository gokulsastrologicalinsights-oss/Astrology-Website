import { type NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";

export async function GET(_request: NextRequest) {
  try {
    const supabase = await createClient();
    const {
      data: { user },
      error: userError,
    } = await supabase.auth.getUser();

    if (userError || !user) {
      return NextResponse.json(
        { error: "Unauthorized access: Sign-in required." },
        { status: 401 }
      );
    }

    // Check if the requester is an admin
    const { data: requesterProfile } = await supabase
      .from("profiles")
      .select("role")
      .eq("id", user.id)
      .single();

    if (requesterProfile?.role !== "admin") {
      return NextResponse.json(
        { error: "Forbidden: Administrative privileges required." },
        { status: 403 }
      );
    }

    // Use admin client to query all profiles
    const adminClient = createAdminClient();
    const { data: profiles, error: profilesError } = await adminClient
      .from("profiles")
      .select("id, username, display_name, role, must_change_password, created_at, updated_at")
      .order("created_at", { ascending: false });

    if (profilesError) {
      return NextResponse.json(
        { error: profilesError.message || "Failed to load profiles." },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      users: profiles || [],
    });
  } catch (error: any) {
    console.error("Admin users API error:", error?.message || error);
    return NextResponse.json(
      { error: "Internal error retrieving admin user list." },
      { status: 500 }
    );
  }
}
