import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { identifier, password } = body;

    if (!identifier || !password) {
      return NextResponse.json(
        { error: "Identifier and password are required." },
        { status: 400 }
      );
    }

    const trimmedIdentifier = identifier.trim();
    let email = trimmedIdentifier;

    // Check if identifier is an email (contains '@')
    if (!trimmedIdentifier.includes("@")) {
      // Identifier is a username - resolve to email securely on the server
      try {
        const adminClient = createAdminClient();
        
        const lower = trimmedIdentifier.toLowerCase();
        const slugUnderscore = lower.replace(/\s+/g, "_");
        const compact = lower.replace(/\s+/g, "");
        const slugHyphen = lower.replace(/\s+/g, "-");

        // Find profile by username (exact or normalized slug) or display_name
        const { data: profiles, error: profileError } = await adminClient
          .from("profiles")
          .select("id, username, display_name")
          .or(
            `username.ilike.${lower},username.ilike.${slugUnderscore},username.ilike.${compact},username.ilike.${slugHyphen},display_name.ilike.${lower},display_name.ilike.${trimmedIdentifier}`
          )
          .limit(1);

        if (profileError || !profiles || profiles.length === 0) {
          // Do not reveal whether user exists
          return NextResponse.json(
            { error: "Invalid username or password." },
            { status: 401 }
          );
        }

        const profile = profiles[0];

        // Get user's email from auth.users via admin client
        const { data: userData, error: userError } =
          await adminClient.auth.admin.getUserById(profile.id);

        if (userError || !userData?.user?.email) {
          return NextResponse.json(
            { error: "Invalid username or password." },
            { status: 401 }
          );
        }

        email = userData.user.email;
      } catch (err: any) {
        console.error("Error resolving username to email:", err?.message || err);
        return NextResponse.json(
          { error: "Authentication service unavailable. Please check system configuration." },
          { status: 503 }
        );
      }
    }

    // Now sign in with Supabase Auth using the email & password
    const supabase = await createClient();
    const { data: authData, error: authError } =
      await supabase.auth.signInWithPassword({
        email,
        password,
      });

    if (authError || !authData.user) {
      return NextResponse.json(
        { error: "Invalid username or password." },
        { status: 401 }
      );
    }

    // Fetch user profile to verify role and must_change_password
    const { data: profile } = await supabase
      .from("profiles")
      .select("username, display_name, role, must_change_password")
      .eq("id", authData.user.id)
      .single();

    const role = profile?.role || "user";
    const mustChangePassword = profile?.must_change_password || false;

    let redirectPath = "/dashboard";
    if (mustChangePassword) {
      redirectPath = "/update-password";
    }

    return NextResponse.json({
      success: true,
      user: {
        id: authData.user.id,
        email: authData.user.email,
        username: profile?.display_name || profile?.username || trimmedIdentifier,
        displayName: profile?.display_name || profile?.username || trimmedIdentifier,
        role,
        mustChangePassword,
      },
      redirect: redirectPath,
    });
  } catch (error: any) {
    console.error("Login route error:", error?.message || error);
    return NextResponse.json(
      { error: "Connection error while contacting authentication server." },
      { status: 500 }
    );
  }
}
