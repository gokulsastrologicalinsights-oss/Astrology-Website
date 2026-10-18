import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET() {
  try {
    const supabase = await createClient();
    const {
      data: { user },
      error: userError,
    } = await supabase.auth.getUser();

    if (userError || !user) {
      return NextResponse.json({ authenticated: false, user: null }, { status: 200 });
    }

    const { data: profile } = await supabase
      .from("profiles")
      .select("username, display_name, role, must_change_password, created_at")
      .eq("id", user.id)
      .single();

    return NextResponse.json({
      authenticated: true,
      user: {
        id: user.id,
        email: user.email,
        username:
          profile?.display_name ||
          profile?.username ||
          user.user_metadata?.display_name ||
          user.user_metadata?.username ||
          "user",
        displayName:
          profile?.display_name ||
          profile?.username ||
          user.user_metadata?.display_name ||
          "User",
        role: profile?.role || "user",
        mustChangePassword: profile?.must_change_password || false,
        createdAt: profile?.created_at || user.created_at,
      },
    });
  } catch (error: any) {
    console.error("Error in /api/auth/me:", error?.message || error);
    return NextResponse.json(
      { authenticated: false, user: null, error: "Internal error" },
      { status: 500 }
    );
  }
}
