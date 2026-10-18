import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createClient } from "@/lib/supabase/server";

export async function POST() {
  try {
    const supabase = await createClient();
    await supabase.auth.signOut();

    // Explicitly delete any residual Supabase auth cookies
    const cookieStore = await cookies();
    const allCookies = cookieStore.getAll();
    for (const cookie of allCookies) {
      if (cookie.name.startsWith("sb-") || cookie.name.includes("auth")) {
        cookieStore.delete(cookie.name);
      }
    }

    const response = NextResponse.json({
      success: true,
      message: "Logged out successfully.",
    });
    response.headers.set(
      "Cache-Control",
      "no-store, no-cache, must-revalidate, proxy-revalidate"
    );
    return response;
  } catch (error: any) {
    console.error("Logout error:", error?.message || error);
    return NextResponse.json(
      { error: "Error during logout operation." },
      { status: 500 }
    );
  }
}
