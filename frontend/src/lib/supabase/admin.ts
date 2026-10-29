import { createClient as createSupabaseClient } from "@supabase/supabase-js";
import { Database } from "./types.ts";

/**
 * Server-only Supabase Admin client with service_role privileges.
 * NEVER import or invoke this file in client-side code.
 */
export function createAdminClient() {
  if (typeof window !== "undefined") {
    throw new Error(
      "CRITICAL SECURITY VIOLATION: createAdminClient() cannot be invoked from the browser. The Supabase service-role key must remain strictly server-side."
    );
  }

  const supabaseUrl =
    process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL || "";
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY || "";

  if (!supabaseUrl || !serviceRoleKey) {
    throw new Error(
      "Missing Supabase server credentials. Please ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are configured in your server environment."
    );
  }

  return createSupabaseClient<Database>(supabaseUrl, serviceRoleKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });
}
