-- Gokul's Astrological Insights - Database Schema & Security Migration
-- Migration: 20261017000001_init_auth_profiles_saved_horoscopes.sql
-- Description: Sets up profiles, saved_horoscopes, transactional display numbering, RLS policies, and admin bootstrap support.

-- 1. Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create public.profiles table
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT NOT NULL,
    display_name TEXT,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    must_change_password BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT username_min_length CHECK (char_length(username) >= 3),
    CONSTRAINT username_max_length CHECK (char_length(username) <= 30),
    CONSTRAINT username_format CHECK (username ~ '^[a-zA-Z0-9_-]{3,30}$')
);

-- Case-insensitive unique index on normalized username
CREATE UNIQUE INDEX IF NOT EXISTS idx_profiles_username_lower ON public.profiles (LOWER(username));
CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles (role);

-- 3. Create public.saved_horoscopes table (prepared for Task 3 automatic saves)
CREATE TABLE IF NOT EXISTS public.saved_horoscopes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    display_number INTEGER NOT NULL,
    person_name TEXT NOT NULL CHECK (char_length(trim(person_name)) > 0),
    birth_date DATE NOT NULL,
    birth_time TEXT NOT NULL CHECK (char_length(trim(birth_time)) > 0),
    timezone TEXT NOT NULL CHECK (char_length(trim(timezone)) > 0),
    birthplace TEXT NOT NULL CHECK (char_length(trim(birthplace)) > 0),
    latitude DOUBLE PRECISION NOT NULL CHECK (latitude >= -90.0 AND latitude <= 90.0),
    longitude DOUBLE PRECISION NOT NULL CHECK (longitude >= -180.0 AND longitude <= 180.0),
    ayanamsa_id INTEGER NOT NULL,
    house_system_id INTEGER NOT NULL,
    calculation_result JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_saved_horoscopes_user_display UNIQUE (user_id, display_number)
);

CREATE INDEX IF NOT EXISTS idx_saved_horoscopes_user_id ON public.saved_horoscopes (user_id);
CREATE INDEX IF NOT EXISTS idx_saved_horoscopes_created_at ON public.saved_horoscopes (created_at DESC);

-- 4. Transactional Sequential Numbering Mechanism for saved_horoscopes
-- Uses a transaction-level advisory lock scoped to the user_id to prevent numbering collisions
-- under concurrent requests, guaranteeing 1, 2, 3... per user without SELECT COUNT(*) + 1 races.
CREATE OR REPLACE FUNCTION public.set_saved_horoscope_display_number()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
BEGIN
    IF NEW.display_number IS NULL OR NEW.display_number <= 0 THEN
        -- Acquire transactional advisory lock hashed to this user's UUID
        PERFORM pg_advisory_xact_lock(hashtext('saved_horoscopes_' || NEW.user_id::text));
        
        -- Get the highest display_number for this user and increment
        SELECT COALESCE(MAX(display_number), 0) + 1
        INTO next_num
        FROM public.saved_horoscopes
        WHERE user_id = NEW.user_id;
        
        NEW.display_number := next_num;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_saved_horoscope_display_number ON public.saved_horoscopes;
CREATE TRIGGER trg_set_saved_horoscope_display_number
BEFORE INSERT ON public.saved_horoscopes
FOR EACH ROW
EXECUTE FUNCTION public.set_saved_horoscope_display_number();

-- 5. Helper Function: Check if current authenticated user is an administrator
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM public.profiles
        WHERE id = auth.uid() AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

-- 6. Trigger: Prevent unauthorized privilege escalation or ID mutation
CREATE OR REPLACE FUNCTION public.prevent_profile_role_tampering()
RETURNS TRIGGER AS $$
BEGIN
    -- Prevent altering profile user ID
    IF NEW.id <> OLD.id THEN
        RAISE EXCEPTION 'Profile user ID cannot be modified.';
    END IF;

    -- Prevent regular users from altering their own or others' roles
    IF NEW.role <> OLD.role THEN
        IF auth.role() = 'authenticated' AND NOT public.is_admin() THEN
            RAISE EXCEPTION 'Unauthorized: Users cannot modify their own account role.';
        END IF;
        IF auth.role() = 'anon' THEN
            RAISE EXCEPTION 'Unauthorized: Anonymous users cannot modify account roles.';
        END IF;
    END IF;

    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS trg_prevent_profile_role_tampering ON public.profiles;
CREATE TRIGGER trg_prevent_profile_role_tampering
BEFORE UPDATE ON public.profiles
FOR EACH ROW
EXECUTE FUNCTION public.prevent_profile_role_tampering();

-- 7. Trigger: Automatically provision public.profiles entry upon auth.users signup
CREATE OR REPLACE FUNCTION public.handle_new_auth_user()
RETURNS TRIGGER AS $$
DECLARE
    raw_uname TEXT;
    cleaned_uname TEXT;
BEGIN
    raw_uname := LOWER(TRIM(COALESCE(NEW.raw_user_meta_data->>'username', '')));
    IF raw_uname = '' OR raw_uname !~ '^[a-zA-Z0-9_-]{3,30}$' THEN
        cleaned_uname := 'user_' || SUBSTRING(REPLACE(NEW.id::text, '-', '') FROM 1 FOR 8);
    ELSE
        cleaned_uname := raw_uname;
    END IF;

    -- Always assign 'user' role regardless of what metadata was supplied
    INSERT INTO public.profiles (
        id,
        username,
        display_name,
        role,
        must_change_password,
        created_at,
        updated_at
    ) VALUES (
        NEW.id,
        cleaned_uname,
        COALESCE(NEW.raw_user_meta_data->>'display_name', cleaned_uname),
        'user',
        FALSE,
        NOW(),
        NOW()
    )
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS trg_on_auth_user_created ON auth.users;
CREATE TRIGGER trg_on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.handle_new_auth_user();

-- 8. Helper RPC Function: Securely resolve username to email on server
-- Revoked from anon and authenticated clients; accessible strictly by service_role
CREATE OR REPLACE FUNCTION public.resolve_username_to_email(p_username TEXT)
RETURNS TEXT AS $$
DECLARE
    resolved_email TEXT;
BEGIN
    SELECT u.email INTO resolved_email
    FROM public.profiles p
    JOIN auth.users u ON u.id = p.id
    WHERE LOWER(p.username) = LOWER(TRIM(p_username))
    LIMIT 1;

    RETURN resolved_email;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

REVOKE ALL ON FUNCTION public.resolve_username_to_email(TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.resolve_username_to_email(TEXT) FROM anon;
REVOKE ALL ON FUNCTION public.resolve_username_to_email(TEXT) FROM authenticated;
GRANT EXECUTE ON FUNCTION public.resolve_username_to_email(TEXT) TO service_role;

-- 9. Row-Level Security (RLS) Configuration

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_horoscopes ENABLE ROW LEVEL SECURITY;

-- Clean existing policies for idempotency
DROP POLICY IF EXISTS "profiles_select_policy" ON public.profiles;
DROP POLICY IF EXISTS "profiles_insert_policy" ON public.profiles;
DROP POLICY IF EXISTS "profiles_update_policy" ON public.profiles;
DROP POLICY IF EXISTS "profiles_delete_policy" ON public.profiles;

DROP POLICY IF EXISTS "saved_horoscopes_select_policy" ON public.saved_horoscopes;
DROP POLICY IF EXISTS "saved_horoscopes_insert_policy" ON public.saved_horoscopes;
DROP POLICY IF EXISTS "saved_horoscopes_update_policy" ON public.saved_horoscopes;
DROP POLICY IF EXISTS "saved_horoscopes_delete_policy" ON public.saved_horoscopes;

-- PROFILES POLICIES
-- Normal users can view only their own profile; admins can view all profiles
CREATE POLICY "profiles_select_policy"
ON public.profiles
FOR SELECT
USING (
    auth.uid() = id OR public.is_admin()
);

-- Users can insert only their own profile as a normal 'user'
CREATE POLICY "profiles_insert_policy"
ON public.profiles
FOR INSERT
WITH CHECK (
    auth.uid() = id AND role = 'user'
);

-- Users can update only their own profile (trigger prevents role elevation)
CREATE POLICY "profiles_update_policy"
ON public.profiles
FOR UPDATE
USING (
    auth.uid() = id OR public.is_admin()
)
WITH CHECK (
    auth.uid() = id OR public.is_admin()
);

-- Profiles can only be deleted by admins or via auth.users CASCADE
CREATE POLICY "profiles_delete_policy"
ON public.profiles
FOR DELETE
USING (
    public.is_admin()
);

-- SAVED HOROSCOPES POLICIES
-- Normal users can read only their own saved horoscopes; admins can inspect
CREATE POLICY "saved_horoscopes_select_policy"
ON public.saved_horoscopes
FOR SELECT
USING (
    auth.uid() = user_id OR public.is_admin()
);

-- Normal users can create records only for their own account
CREATE POLICY "saved_horoscopes_insert_policy"
ON public.saved_horoscopes
FOR INSERT
WITH CHECK (
    auth.uid() = user_id
);

-- Normal users can update only their own records
CREATE POLICY "saved_horoscopes_update_policy"
ON public.saved_horoscopes
FOR UPDATE
USING (
    auth.uid() = user_id
)
WITH CHECK (
    auth.uid() = user_id
);

-- Normal users can delete only their own records
CREATE POLICY "saved_horoscopes_delete_policy"
ON public.saved_horoscopes
FOR DELETE
USING (
    auth.uid() = user_id
);

-- 10. Table & Sequence Grants for Supabase Roles
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.profiles TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.saved_horoscopes TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.is_admin() TO anon, authenticated, service_role;

