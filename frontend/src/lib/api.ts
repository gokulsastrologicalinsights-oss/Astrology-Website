/**
 * Gokul's Astrological Insights - Backend API Client
 * Connects to FastAPI backend endpoints with strict typed contracts.
 */

import {
  HealthResponse,
  MetadataResponse,
  HoroscopeRequest,
  HoroscopeResponse,
  DasaRequest,
  DasaResponse,
  KpRequest,
  KpResponse,
  FullHoroscopeResult,
  NabhashaResponse,
  AshtakavargaResponse,
  BirthInput,
  ApiErrorResponse,
  TraditionalNumerologyRequest,
  TraditionalNumerologyResponse,
  DestinyMatrixRequest,
  DestinyMatrixResponse,
  AdvancedAnalysisRequest,
  AdvancedAnalysisResponse,
  SaveNumerologyReportRequest,
  SavedNumerologyReportResponse,
  NumerologyMetadataResponse,
  NameAnalysisRequest,
  NameAnalysisResponse,
  NameCorrectionRequest,
  NameCorrectionResponse,
  BusinessNumerologyRequest,
  BusinessNumerologyResponse,
  PhoneNumerologyRequest,
  PhoneNumerologyResponse,
  VehicleNumerologyRequest,
  VehicleNumerologyResponse,
  PropertyNumerologyRequest,
  PropertyNumerologyResponse,
  MarriageNumerologyRequest,
  MarriageNumerologyResponse,
  FamilyNumerologyRequest,
  FamilyNumerologyResponse,
  HoraryKpRequest,
  HoraryKpResponse,
  SaveKpChartPayload,
  SavedKpChartRecord,
  VedicYogaResponse,
  UnifiedDoshaResponse,
  PredictionCategoryGroup,
  EvaluatePredictionRulesRequest,
  EvaluatePredictionRulesResponse,
  EvaluatedPredictionRule,
  MedicalAstrologyResponse,
  KpEventAnalysisRequest,
  KpEventAnalysisResponse,
  UserKpAnalysisListResponse,
  VastuDirectionsResponse,
  VastuEvaluationRequest,
  VastuEvaluationResponse,
  SaveVastuReportRequest,
  SavedVastuReportResponse,
  SavedVastuReportsListResponse,
  TransitTimelineRequest,
  TransitTimelineResponse,
  ShadbalaResponse,
  VargaD1D9Request,
  VargaD1D9Response,
  ShodashvargaRequest,
  ShodashvargaResponse,
  SourceReferenceResponse,
  ProblemTaxonomyItem,
  ProblemTaxonomyListResponse,
  RemedyItem,
  RemedyListResponse,
  NavagrahaTempleItem,
  NavagrahaTempleListResponse,
  ContentValidationReport,
  RemedyEligibilityRequest,
  RemedyEligibilityResponse,
  SupportedKpEventItem,
  KpPredictionScanRequest,
  KpPredictionResponse,
  RemedyAnalysisResponse,
  LiveRemedyAnalysisRequest,
  SaveRemedyReportRequest,
  SavedRemedyReportResponse,
  SavedRemedyReportsListResponse,
  PilgrimageCircuitResponse,
  PersonalizedPilgrimageRequest,
  GemstoneAdvisoryResponse,
  GemstoneAdvisoryRequest,
  UnifiedMarriageRequest,
  UnifiedMarriageResponse,
  MarriageCompatibilityRequest,
  MarriageCompatibilityResponse,
  RuleRegisterResponse,
  SaveMarriageCompatibilityReportRequest,
  UpdateMarriageReportMetadataRequest,
  SavedMarriageReportSummary,
  SavedMarriageReportDetail,
  SavedMarriageReportsListResponse,
  LiveTransitsResponse,
  HoroscopeWritingRequest,
  HoroscopeWritingResponse,
  HoroscopeWritingSaveResponse,
  SavedHoroscopeWritingItem,
  SavedHoroscopeWritingListResponse,
} from "./types";


function getApiBaseUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");
  if (envUrl) return envUrl;
  if (typeof window !== "undefined" && process.env.NODE_ENV === "production") {
    // In production client environments without an explicit NEXT_PUBLIC_API_BASE_URL,
    // fall back to same-origin relative path for reverse-proxy routing
    return "";
  }
  return "http://127.0.0.1:8000";
}

const API_BASE_URL = getApiBaseUrl();

export class ApiError extends Error {
  statusCode: number;
  data?: ApiErrorResponse;

  constructor(message: string, statusCode: number, data?: ApiErrorResponse) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.data = data;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${path}`;

  try {
    let response: Response;
    try {
      response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
          ...(options.headers || {}),
        },
      });
    } catch (primaryFetchErr) {
      // In the browser, if direct fetch to API_BASE_URL failed (e.g. cross-origin, host mismatch, or PNA policy),
      // fallback to same-origin path via Next.js rewrites proxy
      if (typeof window !== "undefined" && url.startsWith("http")) {
        try {
          response = await fetch(path, {
            ...options,
            headers: {
              "Content-Type": "application/json",
              "Accept": "application/json",
              ...(options.headers || {}),
            },
          });
        } catch {
          throw primaryFetchErr;
        }
      } else {
        throw primaryFetchErr;
      }
    }

    if (!response.ok) {
      let errorData: ApiErrorResponse | undefined;
      try {
        errorData = await response.json();
      } catch {
        // Response was not JSON
      }

      const message =
        errorData?.detail ||
        errorData?.error ||
        `Backend request failed with HTTP ${response.status} (${response.statusText})`;

      throw new ApiError(message, response.status, errorData);
    }

    return (await response.json()) as T;
  } catch (err: unknown) {
    if (err instanceof ApiError) {
      throw err;
    }
    const rawMsg = err instanceof Error ? err.message : "";
    const isConnRefused =
      !rawMsg ||
      rawMsg.toLowerCase().includes("failed to fetch") ||
      rawMsg.toLowerCase().includes("networkerror") ||
      rawMsg.toLowerCase().includes("connection refused");

    const errorMsg = isConnRefused
      ? "Unable to connect to astrology calculation backend at http://127.0.0.1:8000. Please ensure the FastAPI backend is running."
      : rawMsg || "Failed to connect to calculation engine.";
    throw new ApiError(errorMsg, 0);
  }
}

/**
 * 1. Health check endpoint (GET /health)
 */
export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

/**
 * 2. Calculation engine metadata (GET /api/v1/metadata)
 */
export async function getMetadata(): Promise<MetadataResponse> {
  return request<MetadataResponse>("/api/v1/metadata");
}

/**
 * 3. Vedic Horoscope calculation (POST /api/v1/horoscope/calculate)
 */
export async function calculateHoroscope(req: HoroscopeRequest): Promise<HoroscopeResponse> {
  return request<HoroscopeResponse>("/api/v1/horoscope/calculate", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/**
 * 3b. Real-time Live Planetary Transits (GET/POST /api/v1/horoscope/live-transits)
 */
export async function getLiveTransits(params?: {
  timezone?: string;
  latitude?: number;
  longitude?: number;
  ayanamsa?: number;
  target_datetime?: string;
}): Promise<LiveTransitsResponse> {
  const query = new URLSearchParams();
  if (params?.timezone) query.set("timezone", params.timezone);
  if (params?.latitude !== undefined) query.set("latitude", String(params.latitude));
  if (params?.longitude !== undefined) query.set("longitude", String(params.longitude));
  if (params?.ayanamsa !== undefined) query.set("ayanamsa", String(params.ayanamsa));
  if (params?.target_datetime) query.set("target_datetime", params.target_datetime);
  const qStr = query.toString();
  const getPath = `/api/v1/horoscope/live-transits${qStr ? `?${qStr}` : ""}`;

  try {
    return await request<LiveTransitsResponse>(getPath);
  } catch (getErr) {
    // Resilient fallback to POST endpoint with structured payload
    try {
      return await request<LiveTransitsResponse>("/api/v1/horoscope/live-transits", {
        method: "POST",
        body: JSON.stringify({
          timezone: params?.timezone || "Asia/Kolkata",
          latitude: params?.latitude ?? 13.0827,
          longitude: params?.longitude ?? 80.2707,
          ayanamsa: params?.ayanamsa ?? 0,
          target_datetime: params?.target_datetime,
        }),
      });
    } catch {
      // Re-throw original or final error
      throw getErr;
    }
  }
}



/**
 * 4. Vimshottari Dasa calculation (POST /api/v1/horoscope/dasa)
 */
export async function calculateDasa(req: DasaRequest): Promise<DasaResponse> {
  return request<DasaResponse>("/api/v1/horoscope/dasa", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/**
 * 5. KP Krishnamurti Paddhati calculation (POST /api/v1/horoscope/kp)
 */
export async function calculateKp(req: KpRequest): Promise<KpResponse> {
  return request<KpResponse>("/api/v1/horoscope/kp", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/**
 * 5b. Authentic KP Horary Prashna calculation (POST /api/v1/horoscope/kp/horary)
 */
export async function calculateHoraryKp(req: HoraryKpRequest): Promise<HoraryKpResponse> {
  return request<HoraryKpResponse>("/api/v1/horoscope/kp/horary", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/**
 * 5c. Export Dedicated Server-Side KP Astrology PDF Report (POST /api/v1/reports/kp/pdf)
 */
export async function exportKpPdf(
  payload: {
    chart_type?: "natal" | "horary";
    birth_input?: Record<string, any>;
    horary_input?: Record<string, any>;
    saved_chart_id?: string;
    native_name?: string;
    gender?: string;
    language?: "en" | "ta";
    ayanamsa?: number;
    house_system?: number;
  },
  token?: string
): Promise<Blob> {
  const authHeaders = await resolveAuthHeaders(token);
  const url = `${API_BASE_URL}/api/v1/reports/kp/pdf`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to export KP PDF: ${response.status} ${errorText}`);
  }

  return response.blob();
}

/**
 * 5d. Download Saved KP Chart PDF Report (GET /api/v1/reports/kp/pdf/{id})
 */
export async function downloadSavedKpPdf(
  chartId: string,
  language: string = "en",
  token?: string
): Promise<Blob> {
  const authHeaders = await resolveAuthHeaders(token);
  const url = `${API_BASE_URL}/api/v1/reports/kp/pdf/${encodeURIComponent(chartId)}?language=${encodeURIComponent(language)}`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      ...authHeaders,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to download saved KP PDF: ${response.status} ${errorText}`);
  }

  return response.blob();
}

/**
 * 6. Classical Nabhasha Yogas calculation (POST /api/v1/vedic/nabhasha)
 */
export async function calculateNabhasha(
  req: BirthInput & { ayanamsa?: number }
): Promise<NabhashaResponse> {
  return request<NabhashaResponse>("/api/v1/vedic/nabhasha", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/**
 * 7. Classical Ashtakavarga calculation (POST /api/v1/vedic/ashtakavarga)
 */
export async function calculateAshtakavarga(
  req: BirthInput & { ayanamsa?: number }
): Promise<AshtakavargaResponse> {
  return request<AshtakavargaResponse>("/api/v1/vedic/ashtakavarga", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/**
 * 8. Classical Vedic Yogas calculation (POST /api/v1/vedic/yogas)
 */
export async function calculateVedicYogas(
  req: BirthInput & { ayanamsa?: number; house_system?: number; gender?: string }
): Promise<VedicYogaResponse> {
  return request<VedicYogaResponse>("/api/v1/vedic/yogas", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/**
 * 8b. Classical Vedic Doshas calculation (POST /api/v1/vedic/doshas)
 */
export async function calculateDoshas(
  req: BirthInput & {
    ayanamsa?: number;
    house_system?: number;
    include_2nd_house_in_kuja?: boolean;
    transit_date?: string;
    transit_time?: string;
  }
): Promise<UnifiedDoshaResponse> {
  return request<UnifiedDoshaResponse>("/api/v1/vedic/doshas", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/**
 * 8c. Classical Shadbala calculation (POST /api/v1/vedic/shadbala)
 */
export async function calculateShadbala(
  req: BirthInput & {
    ayanamsa?: number;
    house_system?: number;
    gender?: string;
  }
): Promise<ShadbalaResponse> {
  return request<ShadbalaResponse>("/api/v1/vedic/shadbala", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/**
 * 8d. Classical Vedic & KP Medical Astrology calculation (POST /api/v1/vedic/medical-astrology)
 */
export async function calculateMedicalAstrology(
  req: BirthInput & {
    ayanamsa?: number;
    house_system?: number;
    gender?: string;
  }
): Promise<MedicalAstrologyResponse> {
  return request<MedicalAstrologyResponse>("/api/v1/vedic/medical-astrology", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export interface ClientHoroscopeFormData {
  fullName?: string;
  birthDate: string; // YYYY-MM-DD
  birthTime: string; // HH:MM:SS
  isTimeConfirmed: boolean;
  locationName: string;
  latitude: number;
  longitude: number;
  timezone: string;
  ayanamsaId: number;
  houseSystemId: number;
  includePanchang: boolean;
  includeOuterPlanets: boolean;
}

/**
 * Full calculation suite orchestrator
 * Calls Horoscope, Dasa, and KP endpoints.
 */
export async function calculateFullHoroscopeSuite(
  form: ClientHoroscopeFormData
): Promise<FullHoroscopeResult> {
  const baseBirth = {
    birth_date: form.birthDate,
    birth_time: form.birthTime,
    timezone: form.timezone,
    latitude: form.latitude,
    longitude: form.longitude,
  };

  // 1. Calculate Core Vedic Horoscope (with Nabhasha, Ashtakavarga, and Vedic Yogas enabled)
  const horoscopePromise = calculateHoroscope({
    ...baseBirth,
    ayanamsa: form.ayanamsaId,
    house_system: form.houseSystemId,
    include_panchang: form.includePanchang,
    include_outer_planets: form.includeOuterPlanets,
    include_nabhasha: true,
    include_ashtakavarga: true,
    include_vedic_yogas: true,
    include_doshas: true,
  });

  // 2. Calculate Vimshottari Dasa (complete 5 levels: Maha -> Antar -> Pratyantar -> Sookshma -> Prana)
  const todayIso = new Date().toISOString().split("T")[0];
  const dasaPromise = calculateDasa({
    ...baseBirth,
    depth: 5,
    ayanamsa: form.ayanamsaId,
    house_system: form.houseSystemId,
    target_date: todayIso,
  }).catch((err) => {
    console.warn("Dasa calculation failed:", err);
    return undefined;
  });

  // 3. Calculate KP system (uses KP ayanamsa=1 if available, or selected ayanamsa)
  const kpPromise = calculateKp({
    ...baseBirth,
    ayanamsa: form.ayanamsaId === 0 ? 1 : form.ayanamsaId, // default KP ayanamsa is 1
    house_system: 2, // Placidus standard for KP
  }).catch((err) => {
    console.warn("KP calculation failed:", err);
    return undefined;
  });

  const [horoscope, dasa, kp] = await Promise.all([
    horoscopePromise,
    dasaPromise,
    kpPromise,
  ]);

  return {
    horoscope,
    dasa,
    kp,
    nabhasha: horoscope.nabhasha_yogas,
    ashtakavarga: horoscope.ashtakavarga,
    vedic_yogas: horoscope.vedic_yogas,
    doshas: horoscope.doshas,
    calculatedAt: new Date().toISOString(),
    clientInputs: {
      fullName: form.fullName,
      birthDate: form.birthDate,
      birthTime: form.birthTime,
      isTimeConfirmed: form.isTimeConfirmed,
      locationName: form.locationName,
      latitude: form.latitude,
      longitude: form.longitude,
      timezone: form.timezone,
      ayanamsaId: form.ayanamsaId,
      houseSystemId: form.houseSystemId,
    },
  };
}

// -----------------------------------------------------------------------------
// Numerology API Endpoints
// -----------------------------------------------------------------------------

export async function calculateTraditionalNumerology(
  req: TraditionalNumerologyRequest,
  token?: string
): Promise<TraditionalNumerologyResponse> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return request<TraditionalNumerologyResponse>("/api/v1/numerology/traditional", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

export async function calculateDestinyMatrix(
  req: DestinyMatrixRequest,
  token?: string
): Promise<DestinyMatrixResponse> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return request<DestinyMatrixResponse>("/api/v1/numerology/destiny-matrix", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

export async function calculateAdvancedAnalysis(
  req: AdvancedAnalysisRequest,
  token?: string
): Promise<AdvancedAnalysisResponse> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return request<AdvancedAnalysisResponse>("/api/v1/numerology/advanced", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

export async function analyzeNameNumerology(
  req: NameAnalysisRequest,
  token?: string
): Promise<NameAnalysisResponse> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return request<NameAnalysisResponse>("/api/v1/numerology/name/analyze", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

export async function suggestNameCorrections(
  req: NameCorrectionRequest,
  token?: string
): Promise<NameCorrectionResponse> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return request<NameCorrectionResponse>("/api/v1/numerology/name/suggest-corrections", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

export async function analyzeBusinessNumerology(
  req: BusinessNumerologyRequest,
  token?: string
): Promise<BusinessNumerologyResponse> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return request<BusinessNumerologyResponse>("/api/v1/numerology/business/analyze", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

export async function analyzePhoneNumerology(
  req: PhoneNumerologyRequest,
  token?: string
): Promise<PhoneNumerologyResponse> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return request<PhoneNumerologyResponse>("/api/v1/numerology/phone/analyze", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

export async function analyzeVehicleNumerology(
  req: VehicleNumerologyRequest,
  token?: string
): Promise<VehicleNumerologyResponse> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return request<VehicleNumerologyResponse>("/api/v1/numerology/vehicle/analyze", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

export async function analyzePropertyNumerology(
  req: PropertyNumerologyRequest,
  token?: string
): Promise<PropertyNumerologyResponse> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return request<PropertyNumerologyResponse>("/api/v1/numerology/property/analyze", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

export async function analyzeMarriageNumerology(
  req: MarriageNumerologyRequest,
  token?: string
): Promise<MarriageNumerologyResponse> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return request<MarriageNumerologyResponse>("/api/v1/numerology/marriage/analyze", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

export async function analyzeFamilyNumerology(
  req: FamilyNumerologyRequest,
  token?: string
): Promise<FamilyNumerologyResponse> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return request<FamilyNumerologyResponse>("/api/v1/numerology/family/analyze", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}



export async function getNumerologyMetadata(): Promise<NumerologyMetadataResponse> {
  return request<NumerologyMetadataResponse>("/api/v1/numerology/metadata", {
    method: "GET",
  });
}

export async function saveNumerologyReport(
  payload: SaveNumerologyReportRequest,
  token: string
): Promise<SavedNumerologyReportResponse> {
  return request<SavedNumerologyReportResponse>("/api/v1/numerology/reports", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
}

export async function listNumerologyReports(
  token: string,
  limit: number = 50,
  offset: number = 0
): Promise<{ reports: SavedNumerologyReportResponse[]; count: number }> {
  return request<{ reports: SavedNumerologyReportResponse[]; count: number }>(
    `/api/v1/numerology/reports?limit=${limit}&offset=${offset}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
}

export async function getNumerologyReport(
  id: string,
  token: string
): Promise<SavedNumerologyReportResponse> {
  return request<SavedNumerologyReportResponse>(`/api/v1/numerology/reports/${id}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export async function deleteNumerologyReport(
  id: string,
  token: string
): Promise<{ success: boolean; message: string }> {
  return request<{ success: boolean; message: string }>(`/api/v1/numerology/reports/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * Download Saved Numerology Report PDF (GET /api/v1/numerology/reports/{id}/pdf)
 */
export async function downloadNumerologyReportPdf(
  reportId: string,
  lang: string = "en",
  token?: string
): Promise<Blob> {
  const authHeaders = await resolveAuthHeaders(token);
  const url = `${API_BASE_URL}/api/v1/numerology/reports/${encodeURIComponent(reportId)}/pdf?lang=${encodeURIComponent(lang)}`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      ...authHeaders,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to download numerology PDF: ${response.status} ${errorText}`);
  }

  return response.blob();
}

/**
 * Export Ad-Hoc Numerology PDF directly from live studio calculation (POST /api/v1/numerology/export-pdf)
 */
export async function exportNumerologyPdf(
  payload: {
    person_name: string;
    birth_date?: string | null;
    method: string;
    system_convention?: string;
    language?: string;
    calculation_data: Record<string, any>;
    interpretation_data?: Record<string, any> | null;
    display_number?: number | null;
    report_id?: string | null;
  },
  token?: string
): Promise<Blob> {
  const authHeaders = await resolveAuthHeaders(token);
  const url = `${API_BASE_URL}/api/v1/numerology/export-pdf`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to export numerology PDF: ${response.status} ${errorText}`);
  }

  return response.blob();
}

// ============================================================================
// Muhurta & Panchang Module API Endpoints
// ============================================================================

import type {
  OccasionItem,
  FindMuhurtaResponse,
  SavedMuhurtaItem,
  SaveMuhurtaRequest,
} from "./types";

export async function getOccasions(includeDisabled: boolean = false): Promise<{ occasions: OccasionItem[] }> {
  return request<{ occasions: OccasionItem[] }>(`/api/v1/muhurta/occasions?include_disabled=${includeDisabled}`);
}

export async function addCustomOccasion(
  token: string,
  payload: {
    code: string;
    name_en: string;
    name_ta?: string;
    category?: string;
    description_en?: string;
    description_ta?: string;
    icon?: string;
    rules?: Record<string, any>;
  }
): Promise<{ status: string; occasion: OccasionItem }> {
  return request<{ status: string; occasion: OccasionItem }>("/api/v1/muhurta/occasions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
}

export async function updateOccasion(
  token: string,
  code: string,
  updates: Record<string, any>
): Promise<{ status: string; occasion: OccasionItem }> {
  return request<{ status: string; occasion: OccasionItem }>(`/api/v1/muhurta/occasions/${code}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(updates),
  });
}

export async function getDailyPanchang(params: {
  date: string;
  latitude: number;
  longitude: number;
  timezone?: string;
  ayanamsa_id?: number;
}): Promise<Record<string, any>> {
  return request<Record<string, any>>("/api/v1/muhurta/panchang", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function findMuhurtas(params: {
  occasion_code: string;
  start_date: string;
  end_date: string;
  latitude: number;
  longitude: number;
  location_name?: string;
  timezone?: string;
  preferred_time_range?: string;
  ayanamsa_id?: number;
  tradition?: string;
  custom_rules?: Record<string, any>;
  birth_details?: Record<string, any>;
  limit?: number;
}): Promise<FindMuhurtaResponse> {
  return request<FindMuhurtaResponse>("/api/v1/muhurta/find", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function saveMuhurtaSelection(
  token: string,
  payload: SaveMuhurtaRequest
): Promise<{ status: string; record: SavedMuhurtaItem }> {
  return request<{ status: string; record: SavedMuhurtaItem }>("/api/v1/muhurta/saved", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
}

export async function listSavedMuhurtas(
  token: string,
  limit: number = 50,
  offset: number = 0,
  search?: string,
  allUsers: boolean = false
): Promise<{ count: number; items: SavedMuhurtaItem[] }> {
  const query = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
    all_users: String(allUsers),
  });
  if (search) query.append("search", search);

  return request<{ count: number; items: SavedMuhurtaItem[] }>(`/api/v1/muhurta/saved?${query.toString()}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export async function getSavedMuhurta(token: string, id: string): Promise<SavedMuhurtaItem> {
  return request<SavedMuhurtaItem>(`/api/v1/muhurta/saved/${id}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export async function updateSavedMuhurta(
  token: string,
  id: string,
  updates: { title?: string; client_name?: string; notes?: string }
): Promise<{ status: string; record: SavedMuhurtaItem }> {
  return request<{ status: string; record: SavedMuhurtaItem }>(`/api/v1/muhurta/saved/${id}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(updates),
  });
}

export async function deleteSavedMuhurta(token: string, id: string): Promise<{ status: string; message: string }> {
  return request<{ status: string; message: string }>(`/api/v1/muhurta/saved/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * Advanced KP Charts Persistence (public.saved_kp_charts)
 */
export async function saveKpChart(token: string, payload: SaveKpChartPayload): Promise<SavedKpChartRecord> {
  return request<SavedKpChartRecord>("/api/v1/horoscope/kp/charts", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
}

export async function listSavedKpCharts(
  token: string,
  chartType?: string,
  limit: number = 50,
  offset: number = 0,
  allUsers: boolean = false
): Promise<{ charts: SavedKpChartRecord[]; total_count: number }> {
  const query = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });
  if (chartType) query.append("chart_type", chartType);
  if (allUsers) query.append("all_users", "true");

  return request<{ charts: SavedKpChartRecord[]; total_count: number }>(
    `/api/v1/horoscope/kp/charts?${query.toString()}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
}

export async function getSavedKpChart(token: string, id: string): Promise<SavedKpChartRecord> {
  return request<SavedKpChartRecord>(`/api/v1/horoscope/kp/charts/${id}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export async function deleteSavedKpChart(token: string, id: string): Promise<{ status: string; message: string }> {
  return request<{ status: string; message: string }>(`/api/v1/horoscope/kp/charts/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * 15. KP Event Prediction Engine API
 */
export async function analyzeKpEvents(
  req: KpEventAnalysisRequest,
  token?: string
): Promise<KpEventAnalysisResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return request<KpEventAnalysisResponse>("/api/v1/horoscope/kp-events/analyze", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

export async function analyzeSavedHoroscopeKpEvents(
  token: string,
  savedHoroscopeId: string,
  params?: {
    filter_category?: string;
    filter_grade?: string;
    filter_event?: string;
    running_only?: boolean;
    regenerate?: boolean;
  }
): Promise<KpEventAnalysisResponse> {
  return request<KpEventAnalysisResponse>(
    `/api/v1/horoscope/kp-events/from-saved/${savedHoroscopeId}`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params || {}),
    }
  );
}

export async function getSavedKpEventAnalysis(
  token: string,
  savedHoroscopeId: string
): Promise<KpEventAnalysisResponse> {
  return request<KpEventAnalysisResponse>(
    `/api/v1/horoscope/kp-events/analyses/${savedHoroscopeId}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
}

export async function getKpEventRegistry(): Promise<{
  rule_set_version: string;
  total_events: number;
  events: Array<{
    name: string;
    category: string;
    supporting_houses: number[];
    denying_houses: number[];
    primary_cusp: number;
    is_gain_type: boolean;
    description: string;
  }>;
}> {
  return request("/api/v1/horoscope/kp-events/registry", {
    method: "GET",
  });
}

export async function listUserKpEventAnalyses(
  token: string,
  limit: number = 10,
  offset: number = 0
): Promise<UserKpAnalysisListResponse> {
  return request<UserKpAnalysisListResponse>(
    `/api/v1/horoscope/kp-events/user-analyses?limit=${limit}&offset=${offset}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
}

// ------------------------------------------------------------------------------
// Vastu Shastra API Functions
// ------------------------------------------------------------------------------

export async function getVastuDirections(): Promise<VastuDirectionsResponse> {
  return request<VastuDirectionsResponse>("/api/v1/vastu/directions", {
    method: "GET",
  });
}

export async function evaluateVastuLayout(
  req: VastuEvaluationRequest
): Promise<VastuEvaluationResponse> {
  return request<VastuEvaluationResponse>("/api/v1/vastu/evaluate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });
}

export async function saveVastuReport(
  token: string,
  req: SaveVastuReportRequest
): Promise<SavedVastuReportResponse> {
  return request<SavedVastuReportResponse>("/api/v1/vastu/reports", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });
}

export async function listVastuReports(
  token: string,
  limit: number = 50,
  offset: number = 0
): Promise<SavedVastuReportsListResponse> {
  return request<SavedVastuReportsListResponse>(
    `/api/v1/vastu/reports?limit=${limit}&offset=${offset}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
}

export async function getVastuReport(
  token: string,
  reportId: string
): Promise<SavedVastuReportResponse> {
  return request<SavedVastuReportResponse>(`/api/v1/vastu/reports/${reportId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export async function updateVastuReport(
  token: string,
  reportId: string,
  req: SaveVastuReportRequest
): Promise<SavedVastuReportResponse> {
  return request<SavedVastuReportResponse>(`/api/v1/vastu/reports/${reportId}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });
}

export async function deleteVastuReport(
  token: string,
  reportId: string
): Promise<void> {
  await request<void>(`/api/v1/vastu/reports/${reportId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * 20. KP Transit Ingress and Sub-Lord Timeline (POST /api/v1/horoscope/kp/transit-timeline)
 */
export async function getTransitTimeline(
  req: TransitTimelineRequest,
  token?: string
): Promise<TransitTimelineResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return request<TransitTimelineResponse>("/api/v1/horoscope/kp/transit-timeline", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

/**
 * 21. D1 Rasi & D9 Navamsa Charts (POST /api/v1/horoscope/varga/d1-d9)
 */
export async function calculateVargaD1D9(
  req: VargaD1D9Request,
  token?: string
): Promise<VargaD1D9Response> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return request<VargaD1D9Response>("/api/v1/horoscope/varga/d1-d9", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

/**
 * 22. Get Saved Horoscope D1/D9 (GET /api/v1/horoscope/varga/d1-d9/{id})
 */
export async function getSavedHoroscopeVargaD1D9(
  horoscopeId: string,
  token: string
): Promise<VargaD1D9Response> {
  return request<VargaD1D9Response>(`/api/v1/horoscope/varga/d1-d9/${horoscopeId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * 22b. Calculate Complete 16 Shodashvarga Charts (POST /api/v1/horoscope/varga/shodashvarga)
 */
export async function calculateShodashvarga(
  req: ShodashvargaRequest,
  token?: string
): Promise<ShodashvargaResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return request<ShodashvargaResponse>("/api/v1/horoscope/varga/shodashvarga", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

/**
 * 22c. Get Saved Horoscope 16 Shodashvarga Charts (GET /api/v1/horoscope/varga/shodashvarga/{id})
 */
export async function getSavedHoroscopeShodashvarga(
  horoscopeId: string,
  token: string
): Promise<ShodashvargaResponse> {
  return request<ShodashvargaResponse>(`/api/v1/horoscope/varga/shodashvarga/${horoscopeId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * 23. Remedies & Pariharam Module API Methods
 */

export async function getProblemTaxonomy(
  category?: string
): Promise<ProblemTaxonomyListResponse> {
  const query = category ? `?category=${encodeURIComponent(category)}` : "";
  return request<ProblemTaxonomyListResponse>(`/api/v1/remedies/taxonomy${query}`);
}

export async function getRemedyCatalog(params?: {
  graha?: string;
  remedy_type?: string;
  problem_slug?: string;
}): Promise<RemedyListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.graha) searchParams.append("graha", params.graha);
  if (params?.remedy_type) searchParams.append("remedy_type", params.remedy_type);
  if (params?.problem_slug) searchParams.append("problem_slug", params.problem_slug);
  const qs = searchParams.toString();
  return request<RemedyListResponse>(`/api/v1/remedies/catalog${qs ? `?${qs}` : ""}`);
}

export async function getRemedyDetail(code: string): Promise<RemedyItem> {
  return request<RemedyItem>(`/api/v1/remedies/catalog/${encodeURIComponent(code)}`);
}

export async function getNavagrahaTemples(
  graha?: string
): Promise<NavagrahaTempleListResponse> {
  const query = graha ? `?graha=${encodeURIComponent(graha)}` : "";
  return request<NavagrahaTempleListResponse>(`/api/v1/remedies/temples${query}`);
}

export async function getTempleDetail(code: string): Promise<NavagrahaTempleItem> {
  return request<NavagrahaTempleItem>(`/api/v1/remedies/temples/${encodeURIComponent(code)}`);
}

export async function getClassicalSources(): Promise<SourceReferenceResponse[]> {
  return request<SourceReferenceResponse[]>("/api/v1/remedies/sources");
}

export async function validateRemedyContent(): Promise<ContentValidationReport> {
  return request<ContentValidationReport>("/api/v1/remedies/validate-content", {
    method: "POST",
  });
}

export async function checkRemedyEligibility(
  req: RemedyEligibilityRequest
): Promise<RemedyEligibilityResponse> {
  return request<RemedyEligibilityResponse>("/api/v1/remedies/eligibility-check", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

async function resolveAuthHeaders(token?: string): Promise<Record<string, string>> {
  const headers: Record<string, string> = {};
  let activeToken = token;
  if (!activeToken && typeof window !== "undefined") {
    try {
      const { createClient } = await import("./supabase/client");
      const supabase = createClient();
      const { data } = await supabase.auth.getSession();
      activeToken = data?.session?.access_token;
    } catch {
      // Fallback if supabase client is not accessible in context
    }
  }
  if (activeToken) {
    headers["Authorization"] = `Bearer ${activeToken}`;
  }
  return headers;
}

export async function getSavedHoroscopeRemedyAnalysis(
  horoscopeId: string,
  token?: string
): Promise<RemedyAnalysisResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<RemedyAnalysisResponse>(
    `/api/v1/remedies/analysis/saved/${encodeURIComponent(horoscopeId)}`,
    {
      method: "GET",
      headers: {
        ...authHeaders,
      },
    }
  );
}

export async function getLiveRemedyAnalysis(
  req: LiveRemedyAnalysisRequest,
  token?: string
): Promise<RemedyAnalysisResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<RemedyAnalysisResponse>("/api/v1/remedies/analysis/live", {
    method: "POST",
    headers: {
      ...authHeaders,
    },
    body: JSON.stringify(req),
  });
}

export async function saveRemedyReport(
  payload: SaveRemedyReportRequest,
  token?: string
): Promise<SavedRemedyReportResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<SavedRemedyReportResponse>("/api/v1/remedies/reports", {
    method: "POST",
    headers: {
      ...authHeaders,
    },
    body: JSON.stringify(payload),
  });
}

export async function getRemedyReport(
  reportId: string,
  token?: string
): Promise<SavedRemedyReportResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<SavedRemedyReportResponse>(
    `/api/v1/remedies/reports/${encodeURIComponent(reportId)}`,
    {
      method: "GET",
      headers: {
        ...authHeaders,
      },
    }
  );
}

export async function listRemedyReportsForHoroscope(
  horoscopeId: string,
  token?: string
): Promise<SavedRemedyReportsListResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<SavedRemedyReportsListResponse>(
    `/api/v1/remedies/reports/by-horoscope/${encodeURIComponent(horoscopeId)}`,
    {
      method: "GET",
      headers: {
        ...authHeaders,
      },
    }
  );
}

export async function getPilgrimageCircuits(): Promise<PilgrimageCircuitResponse[]> {
  return request<PilgrimageCircuitResponse[]>("/api/v1/remedies/pilgrimage/circuits");
}

export async function getPersonalizedPilgrimageCircuit(
  req: PersonalizedPilgrimageRequest,
  token?: string
): Promise<PilgrimageCircuitResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<PilgrimageCircuitResponse>("/api/v1/remedies/pilgrimage/personalized", {
    method: "POST",
    headers: {
      ...authHeaders,
    },
    body: JSON.stringify(req),
  });
}

export async function getGemstoneAdvisory(
  req: GemstoneAdvisoryRequest,
  token?: string
): Promise<GemstoneAdvisoryResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<GemstoneAdvisoryResponse>("/api/v1/remedies/gemstones/advisory", {
    method: "POST",
    headers: {
      ...authHeaders,
    },
    body: JSON.stringify(req),
  });
}


// ------------------------------------------------------------------------------
// KP Events & Prediction API Functions
// ------------------------------------------------------------------------------

export async function getSupportedKpEvents(): Promise<{ status: string; total_events: number; events: SupportedKpEventItem[] }> {
  return request<{ status: string; total_events: number; events: SupportedKpEventItem[] }>(
    "/api/v1/kp-prediction/events",
    {
      method: "GET",
    }
  );
}

export async function scanKpPrediction(
  req: KpPredictionScanRequest,
  token?: string
): Promise<KpPredictionResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return request<KpPredictionResponse>("/api/v1/kp-prediction/scan", {
    method: "POST",
    headers,
    body: JSON.stringify(req),
  });
}

/**
 * 23. Unified KP + Vedic Marriage Prediction Engine (POST /api/v1/predictions/marriage)
 */
export async function predictMarriageEvent(
  req: UnifiedMarriageRequest,
  token?: string
): Promise<UnifiedMarriageResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<UnifiedMarriageResponse>("/api/v1/predictions/marriage", {
    method: "POST",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });
}

/**
 * 24. Dual-Horoscope Marriage Compatibility Analysis (POST /api/marriage-compatibility/analyze)
 */
export async function analyzeMarriageCompatibility(
  req: MarriageCompatibilityRequest,
  token?: string
): Promise<MarriageCompatibilityResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<MarriageCompatibilityResponse>("/api/marriage-compatibility/analyze", {
    method: "POST",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });
}

/**
 * 25. Marriage Compatibility Rules Register (GET /api/marriage-compatibility/rules)
 */
export async function getMarriageCompatibilityRules(): Promise<RuleRegisterResponse> {
  return request<RuleRegisterResponse>("/api/marriage-compatibility/rules", {
    method: "GET",
  });
}

/**
 * 26. Save Marriage Compatibility Report (POST /api/marriage-compatibility/saved)
 */
export async function saveMarriageCompatibilityReport(
  req: SaveMarriageCompatibilityReportRequest,
  token?: string
): Promise<SavedMarriageReportDetail> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<SavedMarriageReportDetail>("/api/marriage-compatibility/saved", {
    method: "POST",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });
}

/**
 * 27. List Saved Marriage Compatibility Reports (GET /api/marriage-compatibility/saved)
 */
export async function listSavedMarriageCompatibilityReports(
  options: { limit?: number; offset?: number; all_users?: boolean } = {},
  token?: string
): Promise<SavedMarriageReportsListResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  const params = new URLSearchParams();
  if (options.limit !== undefined) params.set("limit", options.limit.toString());
  if (options.offset !== undefined) params.set("offset", options.offset.toString());
  if (options.all_users) params.set("all_users", "true");
  const queryStr = params.toString() ? `?${params.toString()}` : "";

  return request<SavedMarriageReportsListResponse>(`/api/marriage-compatibility/saved${queryStr}`, {
    method: "GET",
    headers: {
      ...authHeaders,
    },
  });
}

/**
 * 28. Get Saved Marriage Compatibility Report by ID (GET /api/marriage-compatibility/saved/{id})
 */
export async function getSavedMarriageCompatibilityReport(
  reportId: string,
  token?: string
): Promise<SavedMarriageReportDetail> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<SavedMarriageReportDetail>(`/api/marriage-compatibility/saved/${encodeURIComponent(reportId)}`, {
    method: "GET",
    headers: {
      ...authHeaders,
    },
  });
}

/**
 * 29. Update Saved Marriage Compatibility Report Metadata (PATCH /api/marriage-compatibility/saved/{id})
 */
export async function updateSavedMarriageCompatibilityReportMetadata(
  reportId: string,
  req: UpdateMarriageReportMetadataRequest,
  token?: string
): Promise<SavedMarriageReportDetail> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<SavedMarriageReportDetail>(`/api/marriage-compatibility/saved/${encodeURIComponent(reportId)}`, {
    method: "PATCH",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });
}

/**
 * 30. Delete Saved Marriage Compatibility Report (DELETE /api/marriage-compatibility/saved/{id})
 */
export async function deleteSavedMarriageCompatibilityReport(
  reportId: string,
  token?: string
): Promise<{ success: boolean; message: string }> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<{ success: boolean; message: string }>(`/api/marriage-compatibility/saved/${encodeURIComponent(reportId)}`, {
    method: "DELETE",
    headers: {
      ...authHeaders,
    },
  });
}










/**
 * 31. Calculate Traditional Tamil Horoscope Writing (POST /api/v1/tools/horoscope-writing/calculate)
 */
export async function calculateHoroscopeWriting(
  req: import("./types").HoroscopeWritingRequest,
  token?: string
): Promise<import("./types").HoroscopeWritingResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<import("./types").HoroscopeWritingResponse>("/api/v1/tools/horoscope-writing/calculate", {
    method: "POST",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });
}

/**
 * 32. Download Six-Page Traditional Tamil Horoscope Booklet PDF (POST /api/v1/tools/horoscope-writing/pdf)
 */
export async function downloadHoroscopeWritingPdf(
  req: import("./types").HoroscopeWritingRequest & { precalculated_data?: any },
  token?: string
): Promise<Blob> {
  const authHeaders = await resolveAuthHeaders(token);
  const url = `${API_BASE_URL}/api/v1/tools/horoscope-writing/pdf`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to generate horoscope writing PDF: ${response.status} ${errorText}`);
  }

  return response.blob();
}

/**
 * 33. Save Horoscope Writing Document (POST /api/v1/tools/horoscope-writing/save)
 */
export async function saveHoroscopeWriting(
  payload: {
    horoscope_id?: string | null;
    person_name: string;
    birth_date: string;
    birth_time: string;
    birth_place?: string | null;
    latitude: number;
    longitude: number;
    timezone?: string;
    panchanga_system?: string;
    calculated_data: any;
    overrides?: any;
  },
  token?: string
): Promise<HoroscopeWritingSaveResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<HoroscopeWritingSaveResponse>("/api/v1/tools/horoscope-writing/save", {
    method: "POST",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

/**
 * 34. List Saved Horoscope Writing Documents (GET /api/v1/tools/horoscope-writing/saved)
 */
export async function listSavedHoroscopeWritings(
  token?: string,
  limit: number = 50,
  offset: number = 0
): Promise<SavedHoroscopeWritingListResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  const query = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  }).toString();
  return request<SavedHoroscopeWritingListResponse>(`/api/v1/tools/horoscope-writing/saved?${query}`, {
    method: "GET",
    headers: {
      ...authHeaders,
    },
  });
}

/**
 * 35. Get Saved Horoscope Writing Document by ID (GET /api/v1/tools/horoscope-writing/saved/{id})
 */
export async function getSavedHoroscopeWriting(
  id: string,
  token?: string
): Promise<SavedHoroscopeWritingItem> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<SavedHoroscopeWritingItem>(`/api/v1/tools/horoscope-writing/saved/${encodeURIComponent(id)}`, {
    method: "GET",
    headers: {
      ...authHeaders,
    },
  });
}

/**
 * 36. Delete Saved Horoscope Writing Document by ID (DELETE /api/v1/tools/horoscope-writing/saved/{id})
 */
export async function deleteSavedHoroscopeWriting(
  id: string,
  token?: string
): Promise<{ success: boolean; message: string }> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<{ success: boolean; message: string }>(`/api/v1/tools/horoscope-writing/saved/${encodeURIComponent(id)}`, {
    method: "DELETE",
    headers: {
      ...authHeaders,
    },
  });
}

/**
 * 37. Update Saved Horoscope Writing Document by ID (PUT /api/v1/tools/horoscope-writing/saved/{id})
 */
export async function updateSavedHoroscopeWriting(
  id: string,
  payload: import("./types").HoroscopeWritingUpdateRequest,
  token?: string
): Promise<SavedHoroscopeWritingItem> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<SavedHoroscopeWritingItem>(`/api/v1/tools/horoscope-writing/saved/${encodeURIComponent(id)}`, {
    method: "PUT",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

/**
 * 38. Get Prediction Categories Registry (GET /api/v1/rules/categories)
 */
export async function getPredictionCategories(): Promise<PredictionCategoryGroup[]> {
  return request<PredictionCategoryGroup[]>("/api/v1/rules/categories", {
    method: "GET",
  });
}

/**
 * 39. Evaluate Astrological Rules (POST /api/v1/rules/evaluate)
 */
export async function evaluatePredictionRules(
  req: EvaluatePredictionRulesRequest,
  token?: string
): Promise<EvaluatePredictionRulesResponse> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<EvaluatePredictionRulesResponse>("/api/v1/rules/evaluate", {
    method: "POST",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });
}

/**
 * 40. Validate Rule AST Definition (POST /api/v1/rules/validate)
 */
export async function validateRuleDefinition(
  rule: Record<string, any>
): Promise<{ is_valid: boolean; errors: string[] }> {
  return request<{ is_valid: boolean; errors: string[] }>("/api/v1/rules/validate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ rule }),
  });
}

/**
 * 41. Test Rule Definition against Horoscope (POST /api/v1/rules/test)
 */
export async function testRuleDefinition(
  req: {
    rule: Record<string, any>;
    horoscope?: HoroscopeResponse;
    saved_horoscope_id?: string;
    dasa?: Record<string, any>;
    kp?: Record<string, any>;
    language?: string;
  },
  token?: string
): Promise<EvaluatedPredictionRule> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<EvaluatedPredictionRule>("/api/v1/rules/test", {
    method: "POST",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });
}

/**
 * 42. List Admin Rule Definitions (GET /api/v1/rules/definitions)
 */
export async function listRuleDefinitions(
  params?: {
    category_slug?: string;
    subcategory?: string;
    enabled_only?: boolean;
  },
  token?: string
): Promise<any[]> {
  const authHeaders = await resolveAuthHeaders(token);
  const q = new URLSearchParams();
  if (params?.category_slug) q.set("category_slug", params.category_slug);
  if (params?.subcategory) q.set("subcategory", params.subcategory);
  if (params?.enabled_only) q.set("enabled_only", "true");
  const qs = q.toString() ? `?${q.toString()}` : "";
  return request<any[]>(`/api/v1/rules/definitions${qs}`, {
    method: "GET",
    headers: {
      ...authHeaders,
    },
  });
}

/**
 * 43. Create or Update Rule Definition (POST /api/v1/rules/definitions)
 */
export async function saveRuleDefinition(
  rule: Record<string, any>,
  token?: string
): Promise<{ status: string; action: string; rule: any }> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<{ status: string; action: string; rule: any }>("/api/v1/rules/definitions", {
    method: "POST",
    headers: {
      ...authHeaders,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(rule),
  });
}

/**
 * 44. Toggle Rule Status (PATCH /api/v1/rules/definitions/{id}/status)
 */
export async function toggleRuleStatus(
  ruleId: string,
  enabled: boolean,
  token?: string
): Promise<{ status: string; rule_id: string; is_enabled: boolean }> {
  const authHeaders = await resolveAuthHeaders(token);
  return request<{ status: string; rule_id: string; is_enabled: boolean }>(
    `/api/v1/rules/definitions/${encodeURIComponent(ruleId)}/status?enabled=${enabled}`,
    {
      method: "PATCH",
      headers: {
        ...authHeaders,
      },
    }
  );
}
