import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { Database } from "@/lib/supabase/types";

// Public page routes that do not require authentication
const PUBLIC_PAGES = ["/login", "/register", "/forgot-password"];

// Public auth API prefixes
const PUBLIC_API_PREFIXES = [
  "/api/auth/login",
  "/api/auth/register",
  "/api/auth/reset-password",
  "/api/auth/logout",
  "/api/auth/me",
];

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  });

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!supabaseUrl || !supabaseAnonKey) {
    return response;
  }

  const supabase = createServerClient<Database>(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value }) =>
          request.cookies.set(name, value)
        );
        response = NextResponse.next({
          request,
        });
        cookiesToSet.forEach(({ name, value, options }) =>
          response.cookies.set(name, value, {
            ...options,
            httpOnly: options?.httpOnly ?? true,
            secure: process.env.NODE_ENV === "production",
            sameSite: (options?.sameSite as any) ?? "lax",
            path: "/",
          })
        );
      },
    },
  });

  const {
    data: { user },
  } = await supabase.auth.getUser();

  const pathname = request.nextUrl.pathname;

  // 1. Root URL Enforcement:
  // Root URL ('/') must always redirect unauthenticated visitors to /login,
  // and authenticated users to /dashboard.
  if (pathname === "/") {
    const redirectUrl = request.nextUrl.clone();
    if (user) {
      redirectUrl.pathname = "/dashboard";
    } else {
      redirectUrl.pathname = "/login";
    }
    return NextResponse.redirect(redirectUrl);
  }

  // 2. Protected Backend API Endpoints:
  // Pass through /api/v1/* to FastAPI backend (FastAPI handles its own token auth & public endpoints)
  if (pathname.startsWith("/api/v1/")) {
    return response;
  }

  // Unauthenticated requests to non-public Next.js /api routes are rejected immediately with 401.
  if (pathname.startsWith("/api/")) {
    const isPublicApi = PUBLIC_API_PREFIXES.some((prefix) =>
      pathname.startsWith(prefix)
    );

    if (!isPublicApi && !user) {
      return NextResponse.json(
        { error: "Unauthorized access: Sign-in required." },
        { status: 401 }
      );
    }

    return response;
  }

  // 3. Public Pages Handling:
  // If user is already authenticated and visits /login, /register, or /forgot-password,
  // redirect them directly to /dashboard (or /update-password if required).
  const isPublicPage = PUBLIC_PAGES.some(
    (p) => pathname === p || pathname.startsWith(p + "/")
  );

  if (isPublicPage) {
    if (user) {
      const { data: profile } = await supabase
        .from("profiles")
        .select("must_change_password")
        .eq("id", user.id)
        .single();

      const redirectUrl = request.nextUrl.clone();
      if (profile?.must_change_password) {
        redirectUrl.pathname = "/update-password";
      } else {
        redirectUrl.pathname = "/dashboard";
      }
      return NextResponse.redirect(redirectUrl);
    }
    // Unauthenticated user viewing public page: allow
    return response;
  }

  // 4. All Other Internal Application Pages:
  // (e.g. /dashboard, /horoscope, /numerology, /admin, /update-password, etc.)
  // Unauthenticated visitors MUST be redirected to /login.
  if (!user) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = "/login";
    redirectUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(redirectUrl);
  }

  // 5. Authenticated User Role & Privilege Enforcement:
  const { data: profile } = await supabase
    .from("profiles")
    .select("role, must_change_password")
    .eq("id", user.id)
    .single();

  const role = profile?.role || "user";
  const mustChangePassword = profile?.must_change_password || false;

  // A. First-login password change enforcement
  if (mustChangePassword && pathname !== "/update-password") {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = "/update-password";
    return NextResponse.redirect(redirectUrl);
  }

  // B. Admin-only route protection
  if (pathname.startsWith("/admin")) {
    if (role !== "admin") {
      const redirectUrl = request.nextUrl.clone();
      redirectUrl.pathname = "/dashboard";
      redirectUrl.searchParams.set("error", "unauthorized");
      return NextResponse.redirect(redirectUrl);
    }
  }

  // 6. Prevent browser back-forward cache leaks of protected pages after logout:
  response.headers.set(
    "Cache-Control",
    "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0"
  );
  response.headers.set("Pragma", "no-cache");
  response.headers.set("Expires", "0");

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (images, etc)
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
