import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { password } = body;

    if (!password || typeof password !== "string") {
      return NextResponse.json(
        { error: "Password is required." },
        { status: 400 }
      );
    }

    if (password.length < 8) {
      return NextResponse.json(
        { error: "Password must be at least 8 characters in length." },
        { status: 400 }
      );
    }

    const supabase = await createClient();
    const {
      data: { user },
      error: userError,
    } = await supabase.auth.getUser();

    if (userError || !user) {
      return NextResponse.json(
        { error: "Authentication required to update password." },
        { status: 401 }
      );
    }

    // 1. Update password in Supabase Auth
    const { error: updateError } = await supabase.auth.updateUser({
      password,
    });

    if (updateError) {
      return NextResponse.json(
        { error: updateError.message || "Failed to update password." },
        { status: 400 }
      );
    }

    // 2. Mark must_change_password = false in profiles
    const { error: profileError } = await supabase
      .from("profiles")
      .update({
        must_change_password: false,
        updated_at: new Date().toISOString(),
      })
      .eq("id", user.id);

    if (profileError) {
      console.warn("Could not reset must_change_password flag:", profileError.message);
    }

    // Fetch refreshed role to determine proper redirect
    const { data: profile } = await supabase
      .from("profiles")
      .select("role")
      .eq("id", user.id)
      .single();

    const redirectPath = profile?.role === "admin" ? "/admin" : "/dashboard";

    return NextResponse.json({
      success: true,
      message: "Password updated successfully.",
      redirect: redirectPath,
    });
  } catch (error: any) {
    console.error("Update password error:", error?.message || error);
    return NextResponse.json(
      { error: "An unexpected error occurred while updating password." },
      { status: 500 }
    );
  }
}
