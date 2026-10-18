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
  HoraryKpRequest,
  HoraryKpResponse,
  SaveKpChartPayload,
  SavedKpChartRecord,
  VedicYogaResponse,
  KpEventAnalysisRequest,
  KpEventAnalysisResponse,
  UserKpAnalysisSummary,
  UserKpAnalysisListResponse,
  VastuDirectionsResponse,
  VastuEvaluationRequest,
  VastuEvaluationResponse,
  SaveVastuReportRequest,
  SavedVastuReportResponse,
  SavedVastuReportsListResponse,
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
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
        ...(options.headers || {}),
      },
    });

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
    const errorMsg =
      err instanceof Error
        ? err.message
        : "Failed to connect to calculation engine. Please ensure the backend is running.";
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




