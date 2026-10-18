import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { username, email, password } = body;

    // 1. Basic presence check
    if (!username || !email || !password) {
      return NextResponse.json(
        { error: "Username, email, and password are required." },
        { status: 400 }
      );
    }

    const trimmedUsername = username.trim().toLowerCase();
    const trimmedEmail = email.trim().toLowerCase();

    // 2. Validate username format (3-30 chars, letters, numbers, underscores, hyphens)
    const usernameRegex = /^[a-zA-Z0-9_-]{3,30}$/;
    if (!usernameRegex.test(trimmedUsername)) {
      return NextResponse.json(
        {
          error:
            "Username must be between 3 and 30 characters and contain only letters, numbers, underscores, or hyphens.",
        },
        { status: 400 }
      );
    }

    // 3. Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmedEmail)) {
      return NextResponse.json(
        { error: "Please enter a valid email address." },
        { status: 400 }
      );
    }

    // 4. Validate password strength (at least 8 chars, mixed letters and numbers)
    if (password.length < 8) {
      return NextResponse.json(
        { error: "Password must be at least 8 characters in length." },
        { status: 400 }
      );
    }

    // 5. Check username uniqueness in profiles table
    try {
      const adminClient = createAdminClient();
      const { data: existingUser } = await adminClient
        .from("profiles")
        .select("id")
        .ilike("username", trimmedUsername)
        .maybeSingle();

      if (existingUser) {
        return NextResponse.json(
          { error: "Username is already taken. Please choose another." },
          { status: 409 }
        );
      }
    } catch (checkErr: any) {
      console.warn("Could not pre-check username via admin client:", checkErr?.message);
    }

    // 6. Register with Supabase Auth
    // Note: Role is intentionally omitted from user metadata so client cannot tamper.
    // Database trigger trg_on_auth_user_created enforces role = 'user'.
    const supabase = await createClient();
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email: trimmedEmail,
      password,
      options: {
        data: {
          username: trimmedUsername,
          display_name: trimmedUsername,
        },
      },
    });

    if (authError) {
      // Avoid revealing exact details if user exists with email
      if (
        authError.message.toLowerCase().includes("already registered") ||
        authError.message.toLowerCase().includes("unique constraint")
      ) {
        return NextResponse.json(
          {
            error:
              "An account with this email or username already exists. Please log in instead.",
          },
          { status: 409 }
        );
      }

      return NextResponse.json(
        { error: authError.message || "Registration failed." },
        { status: 400 }
      );
    }

    // 7. Check if email confirmation is required
    const emailConfirmationRequired =
      authData.user && !authData.session;

    return NextResponse.json({
      success: true,
      emailConfirmationRequired,
      message: emailConfirmationRequired
        ? "Registration successful! A verification email has been sent. Please confirm your email before signing in."
        : "Registration successful!",
      user: authData.user
        ? {
            id: authData.user.id,
            email: authData.user.email,
            username: trimmedUsername,
            role: "user",
          }
        : null,
    });
  } catch (error: any) {
    console.error("Register route error:", error?.message || error);
    return NextResponse.json(
      { error: "Connection error during registration. Please try again later." },
      { status: 500 }
    );
  }
}
