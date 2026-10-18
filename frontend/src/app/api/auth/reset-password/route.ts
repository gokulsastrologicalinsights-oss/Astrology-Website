import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email } = body;

    if (!email || typeof email !== "string") {
      return NextResponse.json(
        { error: "A valid email address is required." },
        { status: 400 }
      );
    }

    const trimmedEmail = email.trim().toLowerCase();

    // Trigger password reset email via Supabase Auth
    try {
      const supabase = await createClient();
      const origin = request.headers.get("origin") || request.nextUrl.origin;
      await supabase.auth.resetPasswordForEmail(trimmedEmail, {
        redirectTo: `${origin}/update-password`,
      });
    } catch (authErr: any) {
      console.warn("Supabase resetPasswordForEmail notice:", authErr?.message);
    }

    // Always return a generic success message to prevent user enumeration
    return NextResponse.json({
      success: true,
      message:
        "If an account is associated with that email address, you will receive password reset instructions shortly.",
    });
  } catch (error: any) {
    console.error("Password reset error:", error?.message || error);
    return NextResponse.json(
      { error: "An unexpected error occurred. Please try again later." },
      { status: 500 }
    );
  }
}
