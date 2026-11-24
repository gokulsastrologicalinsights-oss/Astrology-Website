# GOKUL'S ASTROLOGICAL INSIGHTS
## AUTHENTICATION COMPATIBILITY & MOBILE IDENTITY SPECIFICATION

> **Document Version:** 1.0.0  
> **Source Verification:** `backend/app/services/auth_service.py` & `frontend/src/app/api/auth/*`  
> **Identity Provider:** Supabase Auth (GoTrue Engine)  
> **Key Constraint:** Do not modify existing authentication settings or database schema.

---

### 1. IDENTITY PROVIDER AUDIT

#### 1.1 Primary Identity Provider
**Supabase Auth (GoTrue)** is the sole and authoritative identity provider for Gokul's Astrological Insights. There is no secondary auth server or custom OAuth broker.

#### 1.2 Session vs Custom JWT Tokens
- The system uses **standard Supabase JWTs** issued directly by GoTrue.
- Each JWT contains:
  - `sub`: User UUID matching `auth.users(id)`.
  - `email`: Authenticated user's email address.
  - `role`: PostgreSQL role (`authenticated`).
  - `exp`: Expiration Unix epoch (default 3600 seconds / 1 hour).
- Tokens are cryptographically signed by Supabase using the project's JWT Secret.

---

### 2. FASTAPI SERVER-SIDE TOKEN VALIDATION

In `backend/app/services/auth_service.py`, FastAPI enforces stateless token validation without relying on session cookies:

```python
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Dict[str, Any]:
    # 1. Extract Bearer token from 'Authorization: Bearer <token>'
    token = credentials.credentials
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    
    # 2. Check in-memory fast cache (60s TTL)
    if token_hash in _AUTH_CACHE:
        ...
        return cached_user
        
    # 3. Cryptographically verify with Supabase Auth
    supabase = get_supabase_client()
    user_response = supabase.auth.get_user(token)
    user_id = user_response.user.id
    
    # 4. Query user profile to determine role and permissions
    profile_res = (
        supabase.table("profiles")
        .select("id, username, display_name, role, must_change_password")
        .eq("id", user_id)
        .single()
        .execute()
    )
    ...
```

#### Key Characteristics:
1. **Zero Cookie Dependency:** FastAPI requires strictly `Authorization: Bearer <JWT>`, which is the native, standard pattern for mobile HTTP requests.
2. **In-Memory Cache:** Avoids roundtripping to Supabase on every rapid API call (60s TTL per token hash).
3. **Role Determination:** Roles (`admin` vs `user`) are queried from `public.profiles.role`. Privileged endpoints use `get_admin_user` which verifies `current_user.get("role") == "admin"`.

---

### 3. EXPO SECURESTORE INTEGRATION ARCHITECTURE

React Native + Expo applications cannot store session tokens in web `localStorage` or browser cookies. Instead, Android hardware keystore / encrypted SharedPreferences must be used via `expo-secure-store`.

#### 3.1 Custom SecureStore Adapter for Supabase Client
The standard `@supabase/supabase-js` client accepts a custom storage provider. Below is the verified Expo implementation:

```typescript
import * as SecureStore from "expo-secure-store";
import { createClient } from "@supabase/supabase-js";

// Hardware-backed secure storage adapter
const ExpoSecureStoreAdapter = {
  getItem: (key: string) => {
    return SecureStore.getItemAsync(key);
  },
  setItem: (key: string, value: string) => {
    return SecureStore.setItemAsync(key, value);
  },
  removeItem: (key: string) => {
    return SecureStore.deleteItemAsync(key);
  },
};

export const supabase = createClient(
  process.env.EXPO_PUBLIC_SUPABASE_URL!,
  process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY!,
  {
    auth: {
      storage: ExpoSecureStoreAdapter,
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: false,
    },
  }
);
```

#### 3.2 Token Lifecycle & Auto-Refresh
1. When the user logs in via `supabase.auth.signInWithPassword({ email, password })`, the session and refresh token are encrypted and stored in `ExpoSecureStore`.
2. `@supabase/supabase-js` automatically refreshes the JWT in the background before the 1-hour expiration.
3. Every outgoing request to the FastAPI backend attaches the active token:
   ```typescript
   const { data: { session } } = await supabase.auth.getSession();
   const response = await fetch(`${API_BASE_URL}/api/v1/horoscope/calculate`, {
     headers: {
       "Authorization": `Bearer ${session?.access_token}`,
       "Content-Type": "application/json",
     },
     body: JSON.stringify(payload),
   });
   ```

---

### 4. USERNAME VS EMAIL LOGIN AUDIT & RESOLUTION

#### 4.1 The Current Web Behavior
- On the web app (`frontend/src/app/api/auth/login/route.ts`), users can log in using either **Email** or **Username**.
- If a username is supplied, Next.js calls `createAdminClient()` (using `SUPABASE_SERVICE_ROLE_KEY`) to query `profiles` by `username.ilike.${username}`, retrieves the user's email from `auth.users`, and then performs `supabase.auth.signInWithPassword({ email, password })`.

#### 4.2 Mobile Security Constraint
- **The Android app must NEVER bundle the `SUPABASE_SERVICE_ROLE_KEY`.**
- Direct anonymous queries to `public.profiles` cannot reveal other users' emails.

#### 4.3 Mobile Resolution Options
1. **Option A (Standard Email Login - Recommended for MVP):**
   - The Android login screen provides an Email + Password input.
   - 100% compliant with standard Supabase Auth out of the box with zero backend changes.
2. **Option B (FastAPI Username Resolver):**
   - Provide a lightweight endpoint `POST /api/v1/auth/resolve-username` on FastAPI that takes `{ username }` and resolves it using FastAPI's existing `get_supabase_client()` (which already possesses the service role key).
3. **Option C (Call Existing Next.js Login Route):**
   - Mobile calls `POST https://gai-astrology.com/api/auth/login` to authenticate and receives the initial session.

---

### 5. VERDICT: AUTHENTICATION READINESS

| Checkpoint | Status | Assessment |
| :--- | :--- | :--- |
| Primary Identity Provider | **Supabase Auth** | Fully supported on both Web and Expo Android. |
| Token Format | **Standard Bearer JWT** | FastAPI directly accepts and verifies Supabase JWTs. |
| Hardware Encryption | **Expo SecureStore** | Supported via standard `@supabase/supabase-js` storage adapter. |
| Production Config Changes | **None Required** | Existing auth settings remain 100% untouched. |
