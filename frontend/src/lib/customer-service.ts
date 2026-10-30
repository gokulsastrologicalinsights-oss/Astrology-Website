/**
 * Gokul's Astrological Insights - Authoritative Customer Management Service
 * Handles customer deduplication, phone normalization, horoscope linking,
 * birthday reminders in Asia/Kolkata timezone, and manual wish status tracking.
 */

import fs from "fs";
import path from "path";
import { createAdminClient } from "./supabase/admin";
import {
  validateAndNormalizePhone,
  isBirthdayTodayInKolkata,
  generateWhatsAppBirthdayLink,
  getTodayKolkataDateString,
} from "./phone-utils";

export interface CustomerRecord {
  id: string;
  user_id: string;
  full_name: string;
  birth_date: string; // YYYY-MM-DD
  country_code: string; // e.g. "+91"
  phone_number?: string | null; // raw / formatted
  normalized_phone?: string | null; // e.g. "+919876543210"
  whatsapp_number?: string | null; // digits only e.g. "919876543210"
  created_at: string;
  updated_at: string;
  is_legacy_without_phone?: boolean;
}

export interface CustomerBirthdayItem {
  id?: string;
  customer_id: string;
  customerId?: string;
  full_name: string;
  fullName?: string;
  birth_date: string;
  birthDate?: string;
  country_code: string;
  countryCode?: string;
  phone_number: string;
  phoneNumber?: string;
  normalized_phone: string;
  normalizedPhone?: string;
  whatsapp_number: string;
  whatsappNumber?: string;
  has_valid_phone: boolean;
  hasValidPhone?: boolean;
  whatsapp_link?: string;
  whatsappLink?: string;
  warning?: string;
  warningMessage?: string;
  wish_sent: boolean;
  wishSent?: boolean;
  wish_sent_at?: string;
  wishSentAt?: string;
  horoscope_ids: string[];
}

export interface WishStatusRecord {
  customer_id: string;
  wish_date: string; // YYYY-MM-DD in Asia/Kolkata
  sent_by: string;
  sent_at: string;
}

// Persistent JSON storage fallback path
const DATA_DIR = path.join(process.cwd(), "data");
const CUSTOMERS_FILE = path.join(DATA_DIR, "customers.json");
const WISHES_FILE = path.join(DATA_DIR, "birthday_wishes.json");

function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) {
    try {
      fs.mkdirSync(DATA_DIR, { recursive: true });
    } catch {
      // Ignore directory creation error in read-only setups
    }
  }
}

function loadLocalCustomers(): CustomerRecord[] {
  ensureDataDir();
  if (fs.existsSync(CUSTOMERS_FILE)) {
    try {
      const content = fs.readFileSync(CUSTOMERS_FILE, "utf-8");
      return JSON.parse(content);
    } catch {
      return [];
    }
  }
  return [];
}

function saveLocalCustomers(customers: CustomerRecord[]) {
  ensureDataDir();
  try {
    fs.writeFileSync(CUSTOMERS_FILE, JSON.stringify(customers, null, 2), "utf-8");
  } catch (err) {
    console.warn("Could not save local customers:", err);
  }
}

function loadLocalWishes(): WishStatusRecord[] {
  ensureDataDir();
  if (fs.existsSync(WISHES_FILE)) {
    try {
      const content = fs.readFileSync(WISHES_FILE, "utf-8");
      return JSON.parse(content);
    } catch {
      return [];
    }
  }
  return [];
}

function saveLocalWishes(wishes: WishStatusRecord[]) {
  ensureDataDir();
  try {
    fs.writeFileSync(WISHES_FILE, JSON.stringify(wishes, null, 2), "utf-8");
  } catch (err) {
    console.warn("Could not save local wishes:", err);
  }
}

/**
 * Normalizes customer full name for stable matching (trimmed, case-insensitive).
 */
export function normalizeCustomerName(name: string): string {
  return (name || "").trim().toLowerCase();
}

/**
 * Finds or provisions an authoritative customer record.
 * Deduplication rules:
 * 1. Match by normalized_phone (authoritative identifier per user)
 * 2. If no phone match, match by normalized full_name AND birth_date
 * 3. Otherwise, create a new authoritative customer record
 */
export async function getOrCreateCustomerRecord(
  userId: string,
  params: {
    customerId?: string;
    fullName: string;
    birthDate: string;
    countryCode?: string;
    phoneNumber?: string | null;
    isLegacyWithoutPhone?: boolean;
  }
): Promise<{ customer: CustomerRecord; isNew: boolean }> {
  const adminClient = createAdminClient();
  const trimmedName = params.fullName.trim();
  const birthDate = params.birthDate.trim();
  const countryCode = (params.countryCode || "+91").trim();
  const rawPhone = (params.phoneNumber || "").trim();
  const nowIso = new Date().toISOString();

  // Validate phone ONLY if provided
  let val: ReturnType<typeof validateAndNormalizePhone> | null = null;
  if (rawPhone && !params.isLegacyWithoutPhone) {
    val = validateAndNormalizePhone(rawPhone, countryCode);
    if (!val.isValid) {
      throw new Error(val.error || "Invalid phone number.");
    }
  }

  // 1. Try Supabase public.customers if provisioned
  try {
    // If specific customerId provided, check it first
    if (params.customerId) {
      const { data: byId } = await adminClient
        .from("customers")
        .select("*")
        .eq("id", params.customerId)
        .single();
      if (byId) {
        if (val && byId.normalized_phone !== val.normalizedPhone) {
          const { data: updated } = await adminClient
            .from("customers")
            .update({
              country_code: countryCode,
              phone_number: val.nationalNumber,
              normalized_phone: val.normalizedPhone,
              whatsapp_number: val.whatsappNumber,
              updated_at: nowIso,
            })
            .eq("id", byId.id)
            .select()
            .single();
          return { customer: updated || byId, isNew: false };
        }
        return { customer: byId, isNew: false };
      }
    }

    // Lookup by normalized_phone ONLY when valid phone is provided (never on empty/null)
    if (val && val.normalizedPhone) {
      const { data: byPhone } = await adminClient
        .from("customers")
        .select("*")
        .eq("user_id", userId)
        .eq("normalized_phone", val.normalizedPhone)
        .limit(1);

      if (byPhone && byPhone.length > 0) {
        return { customer: byPhone[0], isNew: false };
      }
    }

    // Lookup by full_name and birth_date under this user
    const { data: byNameDob } = await adminClient
      .from("customers")
      .select("*")
      .eq("user_id", userId)
      .ilike("full_name", trimmedName)
      .eq("birth_date", birthDate)
      .limit(1);

    if (byNameDob && byNameDob.length > 0) {
      const existing = byNameDob[0];
      if (val && existing.normalized_phone !== val.normalizedPhone) {
        const { data: updated } = await adminClient
          .from("customers")
          .update({
            country_code: countryCode,
            phone_number: val.nationalNumber,
            normalized_phone: val.normalizedPhone,
            whatsapp_number: val.whatsappNumber,
            updated_at: nowIso,
          })
          .eq("id", existing.id)
          .select()
          .single();
        return { customer: updated || existing, isNew: false };
      }
      return { customer: existing, isNew: false };
    }

    // Insert new customer in Supabase
    const newCustomer = {
      user_id: userId,
      full_name: trimmedName,
      birth_date: birthDate,
      country_code: countryCode,
      phone_number: val ? val.nationalNumber : null,
      normalized_phone: val ? val.normalizedPhone : null,
      whatsapp_number: val ? val.whatsappNumber : null,
      created_at: nowIso,
      updated_at: nowIso,
    };

    const { data: inserted, error } = await adminClient
      .from("customers")
      .insert(newCustomer as any)
      .select()
      .single();

    if (!error && inserted) {
      return { customer: inserted, isNew: true };
    }
  } catch (dbErr) {
    // Fall back to resilient local authoritative storage
  }

  // 2. Resilient Local / Synced Authoritative Customer Store
  const localList = loadLocalCustomers();

  // If customerId provided
  if (params.customerId) {
    const foundIdx = localList.findIndex((c) => c.id === params.customerId);
    if (foundIdx >= 0) {
      if (val && localList[foundIdx].normalized_phone !== val.normalizedPhone) {
        localList[foundIdx].country_code = countryCode;
        localList[foundIdx].phone_number = val.nationalNumber;
        localList[foundIdx].normalized_phone = val.normalizedPhone;
        localList[foundIdx].whatsapp_number = val.whatsappNumber;
        localList[foundIdx].is_legacy_without_phone = false;
        localList[foundIdx].updated_at = nowIso;
        saveLocalCustomers(localList);
      }
      return { customer: localList[foundIdx], isNew: false };
    }
  }

  // Check normalized phone ONLY if phone is provided
  if (val && val.normalizedPhone) {
    const matchPhoneIdx = localList.findIndex(
      (c) => c.user_id === userId && c.normalized_phone === val!.normalizedPhone
    );
    if (matchPhoneIdx >= 0) {
      return { customer: localList[matchPhoneIdx], isNew: false };
    }
  }

  // Check name + DOB
  const matchNameDobIdx = localList.findIndex(
    (c) =>
      c.user_id === userId &&
      normalizeCustomerName(c.full_name) === normalizeCustomerName(trimmedName) &&
      c.birth_date === birthDate
  );
  if (matchNameDobIdx >= 0) {
    if (val && localList[matchNameDobIdx].normalized_phone !== val.normalizedPhone) {
      localList[matchNameDobIdx].country_code = countryCode;
      localList[matchNameDobIdx].phone_number = val.nationalNumber;
      localList[matchNameDobIdx].normalized_phone = val.normalizedPhone;
      localList[matchNameDobIdx].whatsapp_number = val.whatsappNumber;
      localList[matchNameDobIdx].is_legacy_without_phone = false;
      localList[matchNameDobIdx].updated_at = nowIso;
      saveLocalCustomers(localList);
    }
    return { customer: localList[matchNameDobIdx], isNew: false };
  }

  // Create new local customer
  const isLegacy = params.isLegacyWithoutPhone || !val;
  const newId = params.isLegacyWithoutPhone
    ? `legacy_${normalizeCustomerName(trimmedName)}_${birthDate}`
    : `cust_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

  const created: CustomerRecord = {
    id: newId,
    user_id: userId,
    full_name: trimmedName,
    birth_date: birthDate,
    country_code: countryCode,
    phone_number: val ? val.nationalNumber : "",
    normalized_phone: val ? val.normalizedPhone : "",
    whatsapp_number: val ? val.whatsappNumber : "",
    created_at: nowIso,
    updated_at: nowIso,
    is_legacy_without_phone: isLegacy,
  };

  localList.push(created);
  saveLocalCustomers(localList);
  return { customer: created, isNew: true };
}

/**
 * Retrieves all unique customers for the given user (or all if admin).
 * Synchronizes with saved_horoscopes records to surface legacy profiles.
 */
export async function listCustomersForUser(
  userId: string,
  isAdmin: boolean = false,
  searchTerm: string = ""
): Promise<CustomerRecord[]> {
  const adminClient = createAdminClient();
  const customerMap = new Map<string, CustomerRecord>();

  // 1. Fetch from Supabase public.customers if available
  try {
    let query = adminClient.from("customers").select("*");
    if (!isAdmin) {
      query = query.eq("user_id", userId);
    }
    const { data: dbCustomers } = await query;
    if (dbCustomers) {
      for (const c of dbCustomers) {
        customerMap.set(c.id, c);
      }
    }
  } catch {
    // public.customers not present yet
  }

  // 2. Merge local customers
  const localCustomers = loadLocalCustomers();
  for (const c of localCustomers) {
    if (isAdmin || c.user_id === userId) {
      if (!customerMap.has(c.id)) {
        customerMap.set(c.id, c);
      }
    }
  }

  // 3. Inspect saved_horoscopes in Supabase only if customerMap is empty
  if (customerMap.size === 0) {
    try {
      let horoQuery = adminClient
        .from("saved_horoscopes")
        .select("id, user_id, person_name, birth_date, calculation_result, created_at, updated_at");
    if (!isAdmin) {
      horoQuery = horoQuery.eq("user_id", userId);
    }
    const { data: horoscopes } = await horoQuery;

    if (horoscopes) {
      for (const h of horoscopes) {
        const calc = h.calculation_result || {};
        const custMeta = calc.customer;

        if (custMeta && custMeta.id) {
          if (!customerMap.has(custMeta.id)) {
            customerMap.set(custMeta.id, {
              id: custMeta.id,
              user_id: h.user_id,
              full_name: custMeta.full_name || h.person_name,
              birth_date: custMeta.birth_date || h.birth_date,
              country_code: custMeta.country_code || "+91",
              phone_number: custMeta.phone_number || "",
              normalized_phone: custMeta.normalized_phone || "",
              whatsapp_number: custMeta.whatsapp_number || "",
              created_at: h.created_at || new Date().toISOString(),
              updated_at: h.updated_at || new Date().toISOString(),
              is_legacy_without_phone: !custMeta.normalized_phone,
            });
          }
        } else {
          // Unlinked legacy record without customer contact details
          // Key by legacy_<h.id> so unrelated people with same name/DOB are not falsely merged
          const legacyKey = `legacy_${h.id}`;
          if (!customerMap.has(legacyKey)) {
            customerMap.set(legacyKey, {
              id: legacyKey,
              user_id: h.user_id,
              full_name: h.person_name,
              birth_date: h.birth_date,
              country_code: "+91",
              phone_number: "",
              normalized_phone: "",
              whatsapp_number: "",
              created_at: h.created_at || new Date().toISOString(),
              updated_at: h.updated_at || new Date().toISOString(),
              is_legacy_without_phone: true,
            });
          }
        }
      }
    }
    } catch (err) {
      console.warn("Could not inspect saved_horoscopes for customers:", err);
    }
  }

  let results = Array.from(customerMap.values());

  if (searchTerm.trim()) {
    const term = searchTerm.toLowerCase();
    results = results.filter(
      (c) =>
        c.full_name.toLowerCase().includes(term) ||
        (c.normalized_phone && c.normalized_phone.includes(term)) ||
        c.birth_date.includes(term)
    );
  }

  // Sort by full_name
  return results.sort((a, b) => a.full_name.localeCompare(b.full_name));
}

/**
 * Updates an authoritative customer's contact details across the system.
 */
export async function updateCustomerContactDetails(
  customerId: string,
  params: {
    fullName?: string;
    birthDate?: string;
    countryCode: string;
    phoneNumber: string;
  }
): Promise<CustomerRecord> {
  const val = validateAndNormalizePhone(params.phoneNumber, params.countryCode);
  if (!val.isValid) {
    throw new Error(val.error || "Invalid phone number.");
  }

  const nowIso = new Date().toISOString();
  const adminClient = createAdminClient();

  let updatedCustomer: CustomerRecord | null = null;

  // 1. Update in Supabase public.customers if present
  try {
    const updateData: Record<string, any> = {
      country_code: params.countryCode,
      phone_number: val.nationalNumber,
      normalized_phone: val.normalizedPhone,
      whatsapp_number: val.whatsappNumber,
      updated_at: nowIso,
    };
    if (params.fullName) updateData.full_name = params.fullName.trim();
    if (params.birthDate) updateData.birth_date = params.birthDate.trim();

    const { data: updated } = await adminClient
      .from("customers")
      .update(updateData as any)
      .eq("id", customerId)
      .select()
      .single();

    if (updated) {
      updatedCustomer = updated;
    }
  } catch {
    // Ignore
  }

  // 2. Update in local store
  const localList = loadLocalCustomers();
  const foundIdx = localList.findIndex((c) => c.id === customerId);
  if (foundIdx >= 0) {
    if (params.fullName) localList[foundIdx].full_name = params.fullName.trim();
    if (params.birthDate) localList[foundIdx].birth_date = params.birthDate.trim();
    localList[foundIdx].country_code = params.countryCode;
    localList[foundIdx].phone_number = val.nationalNumber;
    localList[foundIdx].normalized_phone = val.normalizedPhone;
    localList[foundIdx].whatsapp_number = val.whatsappNumber;
    localList[foundIdx].is_legacy_without_phone = false;
    localList[foundIdx].updated_at = nowIso;
    saveLocalCustomers(localList);
    updatedCustomer = localList[foundIdx];
  } else if (!updatedCustomer) {
    // If it was a legacy ID or newly created from update
    const newRecord: CustomerRecord = {
      id: customerId.startsWith("legacy_")
        ? `cust_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
        : customerId,
      user_id: "system",
      full_name: params.fullName?.trim() || "Customer",
      birth_date: params.birthDate?.trim() || "2000-01-01",
      country_code: params.countryCode,
      phone_number: val.nationalNumber,
      normalized_phone: val.normalizedPhone,
      whatsapp_number: val.whatsappNumber,
      created_at: nowIso,
      updated_at: nowIso,
      is_legacy_without_phone: false,
    };
    localList.push(newRecord);
    saveLocalCustomers(localList);
    updatedCustomer = newRecord;
  }

  // 3. Propagate updated authoritative contact details to all linked saved_horoscopes
  try {
    const rawHoroId = customerId.startsWith("legacy_")
      ? customerId.replace(/^legacy_/, "")
      : null;

    // Fast targeted query: only fetch horoscopes matching this customer or person name
    let matchedHoroscopes: Array<{ id: string; calculation_result: any }> = [];

    if (rawHoroId) {
      const { data } = await adminClient
        .from("saved_horoscopes")
        .select("id, calculation_result")
        .eq("id", rawHoroId);
      if (data) matchedHoroscopes = data;
    } else if (params.fullName && params.fullName.trim()) {
      const { data } = await adminClient
        .from("saved_horoscopes")
        .select("id, calculation_result")
        .ilike("person_name", params.fullName.trim());
      if (data) matchedHoroscopes = data;
    }

    if (matchedHoroscopes.length > 0) {
      for (const h of matchedHoroscopes) {
        const calc = h.calculation_result || {};
        const custMeta = calc.customer;
        const updatedCalc = {
          ...calc,
          customer: {
            ...(custMeta || {}),
            id: updatedCustomer!.id,
            full_name: updatedCustomer!.full_name,
            birth_date: updatedCustomer!.birth_date,
            country_code: updatedCustomer!.country_code,
            phone_number: updatedCustomer!.phone_number,
            normalized_phone: updatedCustomer!.normalized_phone,
            whatsapp_number: updatedCustomer!.whatsapp_number,
          },
        };

        await adminClient
          .from("saved_horoscopes")
          .update({
            calculation_result: updatedCalc,
            updated_at: nowIso,
          } as any)
          .eq("id", h.id);
      }
    }
  
  } catch (propagateErr) {
    console.warn("Could not propagate customer contact details to horoscopes:", propagateErr);
  }

  return updatedCustomer!;
}

/**
 * Identifies all customers whose birthday falls on current date in the Asia/Kolkata timezone.
 * Rules:
 * - Detects birthdays using month and day from every saved horoscope's valid date of birth, including legacy records.
 * - Birthday detection does NOT depend on whether customer has a phone number.
 * - Deduplicates by customer identity when known. Where identity cannot be established, avoids silently merging unrelated people.
 * - Generates WhatsApp click-to-chat links only when a valid phone number exists.
 * - Never generates a WhatsApp URL for an empty or invalid number.
 * - Shows clear "WhatsApp number not added." when phone is missing.
 * - Opening WhatsApp does NOT mark wish as sent.
 */
export async function getTodayBirthdayCelebrants(
  userId: string,
  isAdmin: boolean = false,
  lang: "en" | "ta" = "en"
): Promise<{
  celebrants: CustomerBirthdayItem[];
  todayKolkata: string;
  totalCelebrants: number;
  wishedCount: number;
  pendingCount: number;
}> {
  const todayKolkata = getTodayKolkataDateString();
  const allCustomers = await listCustomersForUser(userId, isAdmin);
  const localWishes = loadLocalWishes();

  // Deduplicated map keyed by authoritative identity (customer ID or unlinked legacy horoscope ID)
  const celebrantsMap = new Map<string, CustomerBirthdayItem>();

  // 1. Check all authoritative customer records whose birthday is today in Asia/Kolkata
  for (const c of allCustomers) {
    if (isBirthdayTodayInKolkata(c.birth_date)) {
      const hasValidPhone =
        !!c.normalized_phone &&
        c.normalized_phone.trim().length > 0 &&
        !c.is_legacy_without_phone;

      const waLink = hasValidPhone
        ? generateWhatsAppBirthdayLink(c.whatsapp_number, c.full_name, lang)
        : "";

      const warning = hasValidPhone
        ? ""
        : lang === "ta"
        ? "வாட்ஸ்அப் எண் சேர்க்கப்படவில்லை."
        : "WhatsApp number not added.";

      const wishRec = localWishes.find(
        (w) => (w.customer_id === c.id || w.customer_id === c.normalized_phone) && w.wish_date === todayKolkata
      );

      celebrantsMap.set(c.id, {
        id: c.id,
        customer_id: c.id,
        customerId: c.id,
        full_name: c.full_name,
        fullName: c.full_name,
        birth_date: c.birth_date,
        birthDate: c.birth_date,
        country_code: c.country_code || "+91",
        countryCode: c.country_code || "+91",
        phone_number: c.phone_number || "",
        phoneNumber: c.phone_number || "",
        normalized_phone: c.normalized_phone || "",
        normalizedPhone: c.normalized_phone || "",
        whatsapp_number: c.whatsapp_number || "",
        whatsappNumber: c.whatsapp_number || "",
        has_valid_phone: hasValidPhone,
        hasValidPhone: hasValidPhone,
        whatsapp_link: waLink,
        whatsappLink: waLink,
        warning,
        warningMessage: warning,
        wish_sent: !!wishRec,
        wishSent: !!wishRec,
        wish_sent_at: wishRec?.sent_at,
        wishSentAt: wishRec?.sent_at,
        horoscope_ids: [],
      });
    }
  }

  // 2. Inspect saved_horoscopes to ensure EVERY saved horoscope with today's birthday is included
  try {
    const adminClient = createAdminClient();
    let horoQuery = adminClient
      .from("saved_horoscopes")
      .select("id, user_id, person_name, birth_date, calculation_result");
    if (!isAdmin) {
      horoQuery = horoQuery.eq("user_id", userId);
    }
    const { data: savedHoroscopes } = await horoQuery;

    if (savedHoroscopes) {
      for (const h of savedHoroscopes) {
        if (!h.birth_date || !isBirthdayTodayInKolkata(h.birth_date)) {
          continue;
        }

        const calc = h.calculation_result || {};
        const custMeta = calc.customer;
        const linkedCustId = custMeta?.id || (h as any).customer_id;

        // If this horoscope is linked to an existing celebrant in our map
        if (linkedCustId && celebrantsMap.has(linkedCustId)) {
          const entry = celebrantsMap.get(linkedCustId)!;
          if (!entry.horoscope_ids.includes(h.id)) {
            entry.horoscope_ids.push(h.id);
          }
          continue;
        }

        // If linked to an authoritative customer that wasn't yet added
        if (linkedCustId) {
          const authCust = allCustomers.find((c) => c.id === linkedCustId);
          if (authCust) {
            const hasValidPhone =
              !!authCust.normalized_phone &&
              authCust.normalized_phone.trim().length > 0 &&
              !authCust.is_legacy_without_phone;

            const waLink = hasValidPhone
              ? generateWhatsAppBirthdayLink(authCust.whatsapp_number, authCust.full_name, lang)
              : "";

            const warning = hasValidPhone
              ? ""
              : lang === "ta"
              ? "வாட்ஸ்அப் எண் சேர்க்கப்படவில்லை."
              : "WhatsApp number not added.";

            const wishRec = localWishes.find(
              (w) => (w.customer_id === authCust.id || w.customer_id === authCust.normalized_phone) && w.wish_date === todayKolkata
            );

            celebrantsMap.set(authCust.id, {
              id: authCust.id,
              customer_id: authCust.id,
              customerId: authCust.id,
              full_name: authCust.full_name,
              fullName: authCust.full_name,
              birth_date: authCust.birth_date,
              birthDate: authCust.birth_date,
              country_code: authCust.country_code || "+91",
              countryCode: authCust.country_code || "+91",
              phone_number: authCust.phone_number || "",
              phoneNumber: authCust.phone_number || "",
              normalized_phone: authCust.normalized_phone || "",
              normalizedPhone: authCust.normalized_phone || "",
              whatsapp_number: authCust.whatsapp_number || "",
              whatsappNumber: authCust.whatsapp_number || "",
              has_valid_phone: hasValidPhone,
              hasValidPhone: hasValidPhone,
              whatsapp_link: waLink,
              whatsappLink: waLink,
              warning,
              warningMessage: warning,
              wish_sent: !!wishRec,
              wishSent: !!wishRec,
              wish_sent_at: wishRec?.sent_at,
              wishSentAt: wishRec?.sent_at,
              horoscope_ids: [h.id],
            });
            continue;
          }
        }

        // Unlinked legacy horoscope
        // Use legacy_<h.id> so distinct unlinked charts avoid false merging
        const legacyKey = `legacy_${h.id}`;
        if (!celebrantsMap.has(legacyKey)) {
          const hasValidPhone =
            !!custMeta?.normalized_phone &&
            custMeta.normalized_phone.trim().length > 0;

          const waLink = hasValidPhone
            ? generateWhatsAppBirthdayLink(custMeta.whatsapp_number, h.person_name, lang)
            : "";

          const warning = hasValidPhone
            ? ""
            : lang === "ta"
            ? "வாட்ஸ்அப் எண் சேர்க்கப்படவில்லை."
            : "WhatsApp number not added.";

          const wishRec = localWishes.find(
            (w) =>
              (w.customer_id === legacyKey || w.customer_id === h.id) &&
              w.wish_date === todayKolkata
          );

          celebrantsMap.set(legacyKey, {
            id: legacyKey,
            customer_id: legacyKey,
            customerId: legacyKey,
            full_name: h.person_name,
            fullName: h.person_name,
            birth_date: h.birth_date,
            birthDate: h.birth_date,
            country_code: custMeta?.country_code || "+91",
            countryCode: custMeta?.country_code || "+91",
            phone_number: custMeta?.phone_number || "",
            phoneNumber: custMeta?.phone_number || "",
            normalized_phone: custMeta?.normalized_phone || "",
            normalizedPhone: custMeta?.normalized_phone || "",
            whatsapp_number: custMeta?.whatsapp_number || "",
            whatsappNumber: custMeta?.whatsapp_number || "",
            has_valid_phone: hasValidPhone,
            hasValidPhone: hasValidPhone,
            whatsapp_link: waLink,
            whatsappLink: waLink,
            warning,
            warningMessage: warning,
            wish_sent: !!wishRec,
            wishSent: !!wishRec,
            wish_sent_at: wishRec?.sent_at,
            wishSentAt: wishRec?.sent_at,
            horoscope_ids: [h.id],
          });
        }
      }
    }
  } catch (horoErr) {
    console.warn("Could not query saved_horoscopes for birthdays:", horoErr);
  }

  const items = Array.from(celebrantsMap.values());
  const wishedCount = items.filter((i) => i.wish_sent).length;
  const pendingCount = items.length - wishedCount;

  return {
    celebrants: items,
    todayKolkata,
    totalCelebrants: items.length,
    wishedCount,
    pendingCount,
  };
}

/**
 * Manually marks a birthday wish as sent for today.
 */
export async function markBirthdayWishSent(
  customerId: string,
  sentBy: string
): Promise<{ success: boolean; alreadySent?: boolean; wish_date: string; sent_at: string }> {
  const todayKolkata = getTodayKolkataDateString();
  const nowIso = new Date().toISOString();

  // Try Supabase table if provisioned
  try {
    const adminClient = createAdminClient();
    await adminClient.from("customer_birthday_wishes").insert({
      customer_id: customerId,
      wish_date: todayKolkata,
      sent_by: sentBy,
      sent_at: nowIso,
    });
  } catch {
    // Ignore
  }

  // Save to local wish tracker
  const localWishes = loadLocalWishes();
  const existingIdx = localWishes.findIndex(
    (w) => w.customer_id === customerId && w.wish_date === todayKolkata
  );

  const alreadySent = existingIdx >= 0;

  if (existingIdx >= 0) {
    localWishes[existingIdx].sent_at = nowIso;
    localWishes[existingIdx].sent_by = sentBy;
  } else {
    localWishes.push({
      customer_id: customerId,
      wish_date: todayKolkata,
      sent_by: sentBy,
      sent_at: nowIso,
    });
  }

  saveLocalWishes(localWishes);

  return {
    success: true,
    alreadySent,
    wish_date: todayKolkata,
    sent_at: nowIso,
  };
}
