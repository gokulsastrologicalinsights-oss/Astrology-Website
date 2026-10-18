#!/usr/bin/env node
/**
 * Gokul's Astrological Insights - Secure Administrator Account Bootstrap (Node.js)
 * Idempotently provisions initial admin with server-side service-role key.
 * Never prints passwords or secrets to stdout.
 */

import { createClient } from "@supabase/supabase-js";

async function runBootstrap() {
  const adminUsername = (process.env.ADMIN_USERNAME || "Gokul Murugan").trim();
  const adminEmail = (process.env.ADMIN_EMAIL || "admin@gokul-astrology.local").trim();
  const adminPassword = (process.env.ADMIN_INITIAL_PASSWORD || "Gokul741@").trim();
  const supabaseUrl = (
    process.env.SUPABASE_URL ||
    process.env.NEXT_PUBLIC_SUPABASE_URL ||
    ""
  ).trim();
  const serviceRoleKey = (process.env.SUPABASE_SERVICE_ROLE_KEY || "").trim();

  const missing = [];
  if (!supabaseUrl) missing.push("SUPABASE_URL or NEXT_PUBLIC_SUPABASE_URL");
  if (!serviceRoleKey) missing.push("SUPABASE_SERVICE_ROLE_KEY");

  if (missing.length > 0) {
    console.warn(
      `[ADMIN BOOTSTRAP] Skipped: Required environment variables are missing: [${missing.join(
        ", "
      )}].`
    );
    return { status: "skipped", missing };
  }

  const supabase = createClient(supabaseUrl, serviceRoleKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });

  const normalizedUsername = adminUsername.toLowerCase().replace(/\s+/g, "_");
  const displayName = adminUsername;

  // 1. Idempotency Check: Query existing admin in profiles
  const { data: existingAdmins, error: queryError } = await supabase
    .from("profiles")
    .select("id, username, display_name, role, must_change_password")
    .eq("role", "admin");

  if (queryError) {
    console.error("[ADMIN BOOTSTRAP] Error querying profiles:", queryError.message);
    return { status: "error", error: queryError.message };
  }

  if (existingAdmins && existingAdmins.length > 0) {
    const existing = existingAdmins[0];
    // Ensure display_name and username are up to date
    await supabase
      .from("profiles")
      .update({
        display_name: displayName,
        username: normalizedUsername,
        must_change_password: false,
      })
      .eq("id", existing.id);

    console.log(
      `[ADMIN BOOTSTRAP] Administrator already exists (username: ${displayName}). Idempotency confirmed; no duplicate created.`
    );
    return { status: "already_exists", admin: displayName };
  }

  // 2. Check if auth user already exists by email
  const { data: userList } = await supabase.auth.admin.listUsers();
  const existingUser = userList?.users?.find(
    (u) => u.email?.toLowerCase() === adminEmail.toLowerCase()
  );

  let userId;
  if (existingUser) {
    userId = existingUser.id;
    await supabase.auth.admin.updateUserById(userId, {
      password: adminPassword,
      user_metadata: {
        username: normalizedUsername,
        display_name: displayName,
      },
    });
  } else {
    // Create user via Supabase Auth Admin API
    const { data: userData, error: createError } =
      await supabase.auth.admin.createUser({
        email: adminEmail,
        password: adminPassword,
        email_confirm: true,
        user_metadata: {
          username: normalizedUsername,
          display_name: displayName,
        },
      });

    if (createError) {
      console.error("[ADMIN BOOTSTRAP] Failed to create user in Auth:", createError.message);
      return { status: "error", error: createError.message };
    }
    userId = userData.user.id;
  }

  // 3. Upsert into profiles table with role: admin, must_change_password: false
  const { error: profileError } = await supabase.from("profiles").upsert({
    id: userId,
    username: normalizedUsername,
    display_name: displayName,
    role: "admin",
    must_change_password: false,
  });

  if (profileError) {
    console.error("[ADMIN BOOTSTRAP] Failed to update profile record:", profileError.message);
    return { status: "error", error: profileError.message };
  }

  console.log(
    `[ADMIN BOOTSTRAP] Initial administrator successfully provisioned (username: ${displayName}).`
  );
  return { status: "created", username: displayName };
}

runBootstrap()
  .then((res) => {
    if (res && res.status === "error") {
      process.exitCode = 1;
    }
  })
  .catch((err) => {
    console.error("[ADMIN BOOTSTRAP] Unexpected exception:", err.message);
    process.exitCode = 1;
  });
