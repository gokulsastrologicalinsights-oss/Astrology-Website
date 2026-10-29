import { type NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import {
  PRO_PLAN_PERMISSIONS,
  BASIC_PLAN_PERMISSIONS,
  UserSubscription,
  UserPermissions,
} from "@/lib/permissions";

export async function GET(_request: NextRequest) {
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

    const role = profile?.role || "user";
    const isAdmin = role === "admin";

    // Determine subscription
    let subscription: UserSubscription;
    let permissions: UserPermissions;

    if (isAdmin) {
      subscription = {
        tier: "enterprise",
        status: "active",
        validUntil: null,
        maxPdfMonthly: 999999,
      };
      permissions = PRO_PLAN_PERMISSIONS;
    } else {
      const metaSub = user.user_metadata?.subscription || {};
      const validUntil = metaSub.validUntil || null;
      let status = metaSub.status || "active";

      // Auto-expire if past validity date
      if (validUntil) {
        const expiryTime = new Date(validUntil).getTime();
        if (!isNaN(expiryTime) && expiryTime < Date.now()) {
          status = "expired";
        }
      }

      subscription = {
        tier: metaSub.tier || "basic",
        status,
        validUntil,
        maxPdfMonthly: metaSub.maxPdfMonthly || 30,
      };

      const metaPerms = user.user_metadata?.permissions;
      if (metaPerms && typeof metaPerms === "object") {
        permissions = {
          ...BASIC_PLAN_PERMISSIONS,
          ...metaPerms,
        };
      } else {
        permissions = subscription.tier === "pro" ? PRO_PLAN_PERMISSIONS : BASIC_PLAN_PERMISSIONS;
      }
    }

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
        role,
        mustChangePassword: profile?.must_change_password || false,
        createdAt: profile?.created_at || user.created_at,
        subscription,
        permissions,
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
