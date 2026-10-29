import { type NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";
import {
  BASIC_PLAN_PERMISSIONS,
  PRO_PLAN_PERMISSIONS,
  UserPermissions,
  UserSubscription,
} from "@/lib/permissions";

/**
 * Helper to ensure the calling user has administrative privileges.
 */
async function verifyAdminCaller() {
  const supabase = await createClient();
  const {
    data: { user },
    error: userError,
  } = await supabase.auth.getUser();

  if (userError || !user) {
    return { error: "Unauthorized access: Sign-in required.", status: 401, adminUser: null };
  }

  const { data: requesterProfile } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", user.id)
    .single();

  if (requesterProfile?.role !== "admin") {
    return {
      error: "Forbidden: Administrative privileges required.",
      status: 403,
      adminUser: null,
    };
  }

  return { error: null, status: 200, adminUser: user };
}

// 1. GET: List all tenant/astrologer accounts with subscriptions & permissions
export async function GET(_request: NextRequest) {
  try {
    const authCheck = await verifyAdminCaller();
    if (authCheck.error) {
      return NextResponse.json({ error: authCheck.error }, { status: authCheck.status });
    }

    const adminClient = createAdminClient();

    // Query profiles and auth users concurrently
    const [profilesRes, authUsersRes] = await Promise.all([
      adminClient
        .from("profiles")
        .select("id, username, display_name, role, must_change_password, created_at, updated_at")
        .order("created_at", { ascending: false }),
      adminClient.auth.admin.listUsers({ perPage: 1000 }),
    ]);

    if (profilesRes.error) {
      return NextResponse.json(
        { error: profilesRes.error.message || "Failed to load profiles." },
        { status: 500 }
      );
    }

    const authMap = new Map<string, any>();
    if (authUsersRes.data?.users) {
      for (const u of authUsersRes.data.users) {
        authMap.set(u.id, u);
      }
    }

    const mergedUsers = (profilesRes.data || []).map((p) => {
      const authUser = authMap.get(p.id);
      const meta = authUser?.user_metadata || {};
      const isAdmin = p.role === "admin";

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
        const rawSub = meta.subscription || {};
        const validUntil = rawSub.validUntil || null;
        let status = rawSub.status || "active";

        if (validUntil) {
          const expiry = new Date(validUntil).getTime();
          if (!isNaN(expiry) && expiry < Date.now()) {
            status = "expired";
          }
        }

        subscription = {
          tier: rawSub.tier || "basic",
          status,
          validUntil,
          maxPdfMonthly: rawSub.maxPdfMonthly || 30,
        };

        const rawPerms = meta.permissions;
        permissions =
          rawPerms && typeof rawPerms === "object"
            ? { ...BASIC_PLAN_PERMISSIONS, ...rawPerms }
            : subscription.tier === "pro"
            ? PRO_PLAN_PERMISSIONS
            : BASIC_PLAN_PERMISSIONS;
      }

      return {
        id: p.id,
        username: p.username,
        display_name: p.display_name,
        email: authUser?.email || null,
        role: p.role,
        must_change_password: p.must_change_password,
        created_at: p.created_at,
        updated_at: p.updated_at,
        last_sign_in_at: authUser?.last_sign_in_at || null,
        subscription,
        permissions,
      };
    });

    return NextResponse.json({
      success: true,
      users: mergedUsers,
    });
  } catch (error: any) {
    console.error("Admin users GET error:", error?.message || error);
    return NextResponse.json(
      { error: "Internal error retrieving admin user list." },
      { status: 500 }
    );
  }
}

// 2. POST: Create a new tenant/astrologer account with specified permissions
export async function POST(request: NextRequest) {
  try {
    const authCheck = await verifyAdminCaller();
    if (authCheck.error) {
      return NextResponse.json({ error: authCheck.error }, { status: authCheck.status });
    }

    const body = await request.json();
    const {
      username,
      email,
      password,
      displayName,
      role = "user",
      tier = "basic",
      validUntil = null,
      status = "active",
      permissions = null,
      maxPdfMonthly = 30,
    } = body;

    if (!username || !email || !password) {
      return NextResponse.json(
        { error: "Username, email, and password are required fields." },
        { status: 400 }
      );
    }

    const trimmedUsername = username.trim().toLowerCase();
    const trimmedEmail = email.trim().toLowerCase();

    // Validate username format
    if (!/^[a-zA-Z0-9_-]{3,30}$/.test(trimmedUsername)) {
      return NextResponse.json(
        {
          error:
            "Username must be 3-30 characters and alphanumeric with optional underscores/hyphens.",
        },
        { status: 400 }
      );
    }

    if (password.length < 8) {
      return NextResponse.json(
        { error: "Password must be at least 8 characters in length." },
        { status: 400 }
      );
    }

    const adminClient = createAdminClient();

    // Check if username already exists in profiles
    const { data: existingProfile } = await adminClient
      .from("profiles")
      .select("id")
      .ilike("username", trimmedUsername)
      .maybeSingle();

    if (existingProfile) {
      return NextResponse.json(
        { error: `The username '${trimmedUsername}' is already taken.` },
        { status: 409 }
      );
    }

    // Determine permissions
    let finalPermissions: UserPermissions;
    if (role === "admin") {
      finalPermissions = PRO_PLAN_PERMISSIONS;
    } else if (permissions && typeof permissions === "object") {
      finalPermissions = { ...BASIC_PLAN_PERMISSIONS, ...permissions };
    } else {
      finalPermissions = tier === "pro" ? PRO_PLAN_PERMISSIONS : BASIC_PLAN_PERMISSIONS;
    }

    const subscriptionPayload: UserSubscription = {
      tier,
      status: role === "admin" ? "active" : status,
      validUntil: role === "admin" ? null : validUntil,
      maxPdfMonthly: role === "admin" ? 999999 : Number(maxPdfMonthly) || 30,
    };

    // Create user in Supabase Auth
    const { data: createdAuth, error: authError } =
      await adminClient.auth.admin.createUser({
        email: trimmedEmail,
        password,
        email_confirm: true,
        user_metadata: {
          username: trimmedUsername,
          display_name: displayName?.trim() || trimmedUsername,
          role,
          subscription: subscriptionPayload,
          permissions: finalPermissions,
        },
      });

    if (authError || !createdAuth?.user) {
      return NextResponse.json(
        { error: authError?.message || "Failed to create user in authentication directory." },
        { status: 400 }
      );
    }

    const newUserId = createdAuth.user.id;

    // Upsert into public.profiles to ensure consistency
    const { error: profileUpsertError } = await adminClient.from("profiles").upsert({
      id: newUserId,
      username: trimmedUsername,
      display_name: displayName?.trim() || trimmedUsername,
      role,
      must_change_password: false,
      updated_at: new Date().toISOString(),
    });

    if (profileUpsertError) {
      console.warn("Profile table upsert warning:", profileUpsertError.message);
    }

    return NextResponse.json({
      success: true,
      message: `Profile created successfully for ${trimmedUsername}.`,
      user: {
        id: newUserId,
        username: trimmedUsername,
        display_name: displayName?.trim() || trimmedUsername,
        email: trimmedEmail,
        role,
        subscription: subscriptionPayload,
        permissions: finalPermissions,
      },
    });
  } catch (error: any) {
    console.error("Admin user creation error:", error?.message || error);
    return NextResponse.json(
      { error: "Internal server error creating astrologer account." },
      { status: 500 }
    );
  }
}

// 3. PATCH: Update existing user permissions, subscription, status, or password
export async function PATCH(request: NextRequest) {
  try {
    const authCheck = await verifyAdminCaller();
    if (authCheck.error) {
      return NextResponse.json({ error: authCheck.error }, { status: authCheck.status });
    }

    const body = await request.json();
    const {
      userId,
      displayName,
      role,
      tier,
      status,
      validUntil,
      permissions,
      maxPdfMonthly,
      newPassword,
    } = body;

    if (!userId) {
      return NextResponse.json({ error: "userId is required for updates." }, { status: 400 });
    }

    const adminClient = createAdminClient();

    // Fetch existing user
    const { data: existingUser, error: fetchError } =
      await adminClient.auth.admin.getUserById(userId);

    if (fetchError || !existingUser?.user) {
      return NextResponse.json({ error: "User not found in directory." }, { status: 404 });
    }

    const currentMeta = existingUser.user.user_metadata || {};
    const existingSub = currentMeta.subscription || {};

    const updatedSub: UserSubscription = {
      tier: tier !== undefined ? tier : existingSub.tier || "basic",
      status: status !== undefined ? status : existingSub.status || "active",
      validUntil: validUntil !== undefined ? validUntil : existingSub.validUntil || null,
      maxPdfMonthly:
        maxPdfMonthly !== undefined
          ? Number(maxPdfMonthly)
          : existingSub.maxPdfMonthly || 30,
    };

    const updatedPermissions: UserPermissions =
      permissions !== undefined
        ? { ...BASIC_PLAN_PERMISSIONS, ...permissions }
        : currentMeta.permissions || BASIC_PLAN_PERMISSIONS;

    const updatePayload: any = {
      user_metadata: {
        ...currentMeta,
        display_name: displayName !== undefined ? displayName.trim() : currentMeta.display_name,
        role: role !== undefined ? role : currentMeta.role || "user",
        subscription: updatedSub,
        permissions: updatedPermissions,
      },
    };

    if (newPassword && newPassword.trim().length >= 8) {
      updatePayload.password = newPassword.trim();
    }

    const { data: updatedAuth, error: updateError } =
      await adminClient.auth.admin.updateUserById(userId, updatePayload);

    if (updateError) {
      return NextResponse.json(
        { error: updateError.message || "Failed to update authentication record." },
        { status: 500 }
      );
    }

    // Sync profiles table
    const profileUpdates: any = { updated_at: new Date().toISOString() };
    if (displayName !== undefined) profileUpdates.display_name = displayName.trim();
    if (role !== undefined) profileUpdates.role = role;

    await adminClient.from("profiles").update(profileUpdates).eq("id", userId);

    return NextResponse.json({
      success: true,
      message: "Astrologer account and permissions updated successfully.",
      user: {
        id: userId,
        email: updatedAuth.user?.email,
        display_name: updatePayload.user_metadata.display_name,
        role: updatePayload.user_metadata.role,
        subscription: updatedSub,
        permissions: updatedPermissions,
      },
    });
  } catch (error: any) {
    console.error("Admin user PATCH error:", error?.message || error);
    return NextResponse.json(
      { error: "Internal server error updating account permissions." },
      { status: 500 }
    );
  }
}

// 4. DELETE: Remove user account safely
export async function DELETE(request: NextRequest) {
  try {
    const authCheck = await verifyAdminCaller();
    if (authCheck.error) {
      return NextResponse.json({ error: authCheck.error }, { status: authCheck.status });
    }

    const body = await request.json();
    const { userId } = body;

    if (!userId) {
      return NextResponse.json({ error: "userId is required for deletion." }, { status: 400 });
    }

    if (userId === authCheck.adminUser?.id) {
      return NextResponse.json(
        { error: "Security Restriction: You cannot delete your own administrator account." },
        { status: 400 }
      );
    }

    const adminClient = createAdminClient();

    // Delete from auth.users (cascades to profiles and linked records)
    const { error: deleteError } = await adminClient.auth.admin.deleteUser(userId);

    if (deleteError) {
      return NextResponse.json(
        { error: deleteError.message || "Failed to delete user account." },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      message: "Account and associated access removed successfully.",
    });
  } catch (error: any) {
    console.error("Admin user DELETE error:", error?.message || error);
    return NextResponse.json(
      { error: "Internal error deleting account." },
      { status: 500 }
    );
  }
}
