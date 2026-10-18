/**
 * Gokul's Astrological Insights - TypeScript Data Models
 * Exactly matches FastAPI backend schemas from app/schemas/
 */

export interface BirthInput {
  birth_date: string; // YYYY-MM-DD
  birth_time: string; // HH:MM:SS
  timezone: string;   // IANA identifier (e.g. "Asia/Kolkata") or offset "+05:30"
  latitude: number;   // -90 to +90
  longitude: number;  // -180 to +180
}

export interface CalculationMetadata {
  engine: string;
  birth_utc_iso: string;
  julian_day_ut1: number;
  local_timezone?: string;
  utc_offset_hours?: number;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  ayanamsa_id: number;
  ayanamsa_name: string;
  ayanamsa_deg: number;
  house_system_id: number;
  house_system_name: string;
  calculation_frame: string;
  notes: string[];
}

export interface NakshatraDetail {
  name: string;
  index: number;
  pada: number;
  lord: string;
  deity: string;
}

export interface PlanetInfo {
  name: string;
  body_id: number;
  longitude: number;
  latitude: number;
  distance_au: number;
  speed_deg_per_day: number;
  is_retrograde: boolean;
  sign_index: number;       // 1-12
  sign_name: string;
  sign_name_tamil: string;
  degree_in_sign: number;   // 0.0 to 30.0
  nakshatra: NakshatraDetail;
}

export interface HouseInfo {
  house_number: number;     // 1-12
  cusp_degree: number;      // 0.0 to 360.0
  sign_index: number;       // 1-12
  sign_name: string;
  sign_name_tamil: string;
  degree_in_sign: number;
  nakshatra: string;
  pada: number;
  star_lord: string;
}

export interface AscendantInfo {
  degree: number;
  sign_index: number;
  sign_name: string;
  sign_name_tamil: string;
  degree_in_sign: number;
  nakshatra: NakshatraDetail;
}

export interface TithiInfo {
  number: number;
  name: string;
  paksha: string;
}

export interface YogaInfo {
  number: number;
  name: string;
}

export interface PanchangInfo {
  tithi: TithiInfo;
  nakshatra: string;
  yoga: YogaInfo;
  karana: string;
  vara: string;
}

export interface NabhashaYogaDetail {
  name: string;
  category: string; // "Ashraya" | "Dala" | "Aakriti" | "Sankhya"
  formation_rule: string;
  qualifying_houses: number[];
  qualifying_signs: number[];
  planets_involved: string[];
  description: string;
  is_primary: boolean;
}

export interface NabhashaDistribution {
  distinct_signs_count: number;
  distinct_houses_count: number;
  planets_by_house: Record<string, string[]>;
  planets_by_sign: Record<string, string[]>;
  kendra_planets: string[];
  panaphara_planets: string[];
  apoklima_planets: string[];
  trikona_planets: string[];
}

export interface NabhashaResponse {
  metadata?: CalculationMetadata;
  distribution: NabhashaDistribution;
  primary_yoga?: NabhashaYogaDetail;
  all_qualifying_yogas: NabhashaYogaDetail[];
  classical_reference: string;
}

export interface PlanetBavDetail {
  planet: string;
  sign_bindus: Record<string, number>;
  house_bindus: Record<string, number>;
  total_bindus: number;
  expected_total: number;
  trikona_reduced?: Record<string, number> | null;
  ekadhipatya_reduced?: Record<string, number> | null;
  rashi_pinda?: number | null;
  graha_pinda?: number | null;
  shodhya_pinda?: number | null;
}

export interface SavDetail {
  sign_bindus: Record<string, number>;
  house_bindus: Record<string, number>;
  total_bindus: number; // 337 invariant
  average_per_sign: number; // 28.08
  auspicious_signs: number[];
  inauspicious_signs: number[];
}

export interface AshtakavargaResponse {
  metadata?: CalculationMetadata;
  bhinnashtakavarga: Record<string, PlanetBavDetail>;
  sarvashtakavarga: SavDetail;
  lagna_sign_index: number;
  validation_status: string;
  classical_reference: string;
}

export interface YogaConditionItem {
  condition: string;
  passed: boolean;
  detail: string;
}

export interface YogaDetail {
  id: string;
  name: string;
  name_tamil: string;
  category: string;
  status: "Qualifying" | "Partially Qualifying" | "Cancelled" | "Not Qualifying";
  is_qualifying: boolean;
  planets_involved: string[];
  relevant_houses: number[];
  conditions: YogaConditionItem[];
  short_interpretation: string;
  classical_definition: string;
  classical_reference: string;
  verification_status: string;
  cancellation_reason?: string | null;
}

export interface YogaSummary {
  total_evaluated: number;
  total_qualifying: number;
  raja_yogas_count: number;
  dhana_yogas_count: number;
  mahapurusha_yogas_count: number;
  vipareeta_yogas_count: number;
  other_classical_count: number;
  cancelled_count: number;
}

export interface VedicYogaResponse {
  metadata?: CalculationMetadata;
  summary: YogaSummary;
  yogas: YogaDetail[];
}

export interface HoroscopeRequest extends BirthInput {
  ayanamsa: number;
  house_system: number;
  include_panchang: boolean;
  include_outer_planets: boolean;
  include_nabhasha?: boolean;
  include_ashtakavarga?: boolean;
  include_vedic_yogas?: boolean;
  include_varga?: boolean;
  gender?: string;
}

export interface HoroscopeResponse {
  metadata: CalculationMetadata;
  ascendant: AscendantInfo;
  midheaven: AscendantInfo;
  planets: PlanetInfo[];
  houses: HouseInfo[];
  panchang?: PanchangInfo;
  nabhasha_yogas?: NabhashaResponse;
  ashtakavarga?: AshtakavargaResponse;
  vedic_yogas?: VedicYogaResponse;
  varga_d1_d9?: VargaD1D9Response;
}

export interface DasaPeriodAgeDict {
  years: number;
  months: number;
  days: number;
}

export interface DasaPeriodNode {
  lord: string;
  level: string; // "Mahadasha", "Antardasha", "Pratyantardasha", "Sookshmadasha", "Pranadasha"
  start_jd: number;
  end_jd: number;
  duration_days: number;
  duration_years: number;
  start_date_iso?: string;
  end_date_iso?: string;
  start_age?: string;
  end_age?: string;
  start_age_dict?: DasaPeriodAgeDict;
  end_age_dict?: DasaPeriodAgeDict;
  star_lord?: string;
  benefit_bhavas?: string;
  period_lord_occupied?: number | null;
  star_lord_occupied?: number | null;
  period_lord_owned?: number[];
  star_lord_owned?: number[];
  sub_periods?: DasaPeriodNode[];
}

export interface ActivePeriodPath {
  mahadasha: string;
  antardasha?: string;
  pratyantardasha?: string;
  sookshmadasha?: string;
  pranadasha?: string;
  target_jd: number;
  target_date_iso: string;
  target_age?: string;
  target_age_dict?: DasaPeriodAgeDict;
}

export interface DasaRequest extends BirthInput {
  depth: number;
  ayanamsa: number;
  house_system?: number;
  target_date?: string;
}

export interface DasaResponse {
  metadata: CalculationMetadata;
  moon_sidereal_deg: number;
  nakshatra: NakshatraDetail;
  birth_dasa_lord: string;
  birth_balance_years: number;
  birth_balance_formatted: string;
  dasa_tree: DasaPeriodNode[];
  active_period?: ActivePeriodPath;
}

export interface PlanetaryKpPosition {
  planet: string;
  body_id: number;
  longitude: number;
  sign_index: number;
  sign_name: string;
  sign_lord: string;
  star_lord: string;
  sub_lord: string;
  sub_sub_lord: string;
  kp_number: number; // 1-249
}

export interface KpCuspDetail {
  house: number;
  cusp_degree: number;
  sign_index: number;
  sign_name: string;
  sign_lord: string;
  star_lord: string;
  sub_lord: string;
  promise: string; // "Positive", "Negative", "Mixed"
  sub_sub_lord?: string;
}

export interface SignificatorStrengthEntry {
  house: number;
  type: string; // "StarLord", "Occupant", "Owner", "Aspecting"
}

export interface PlanetSignificator {
  planet: string;
  signified_houses: number[];
  strength_order: SignificatorStrengthEntry[];
}

export interface HouseSignificatorEntry {
  house: number;
  sign_name: string;
  sign_lord: string;
  star_lord: string;
  sub_lord: string;
  sub_sub_lord: string;
  level_a: string[]; // Planets in star of occupants (strongest)
  level_b: string[]; // House occupants
  level_c: string[]; // Planets in star of house lord
  level_d: string[]; // House sign lord
  all_significators: string[];
}

export interface RulingPlanetEntry {
  role: string;
  planet: string;
}

export interface RulingPlanetsDetail {
  day_lord: string;
  ascendant_sign_lord: string;
  ascendant_star_lord: string;
  ascendant_sub_lord: string;
  moon_sign_lord: string;
  moon_star_lord: string;
  moon_sub_lord: string;
  ruling_planets_list: string[];
  details: RulingPlanetEntry[];
}

export interface KpDasaPeriod {
  level: number;
  level_name: string;
  vedic_name: string;
  lord: string;
  start_date: string;
  end_date: string;
  duration_days: number;
}

export interface KpDasaBalance {
  birth_epoch: string;
  mahadasha_lord: string;
  mahadasha_balance_years: number;
  mahadasha_balance_days: number;
  antardasha_lord: string;
  antardasha_balance_days: number;
  pratyantardasha_lord: string;
  pratyantardasha_balance_days: number;
  sookshmadasha_lord: string;
  sookshmadasha_balance_days: number;
  pranadasha_lord: string;
  pranadasha_balance_days: number;
  current_periods: KpDasaPeriod[];
  mahadashas: KpDasaPeriod[];
}

export interface KpRequest extends BirthInput {
  ayanamsa: number;
  house_system: number;
}

export interface KpResponse {
  metadata: CalculationMetadata;
  planetary_positions: PlanetaryKpPosition[];
  cuspal_analysis: KpCuspDetail[];
  significators: PlanetSignificator[];
  house_significators?: HouseSignificatorEntry[];
  ruling_planets?: RulingPlanetsDetail;
  dasa_hierarchy?: KpDasaBalance;
}

export interface HoraryKpRequest {
  horary_number: number;
  question_text?: string;
  question_date: string;
  question_time: string;
  timezone: string;
  latitude: number;
  longitude: number;
  location_name?: string;
  ayanamsa?: number;
  house_system?: number;
}

export interface HoraryDivisionDetail {
  number: number;
  start_degree: number;
  end_degree: number;
  mid_degree: number;
  sign: string;
  sign_lord: string;
  star: string;
  star_lord: string;
  sub_lord: string;
  sub_sub_lord: string;
  pada: number;
}

export interface HoraryKpResponse {
  metadata: CalculationMetadata;
  horary_number: number;
  horary_division: HoraryDivisionDetail;
  question_text?: string;
  question_datetime: string;
  location_name?: string;
  ascendant_degree: number;
  planetary_positions: PlanetaryKpPosition[];
  cuspal_analysis: KpCuspDetail[];
  significators: PlanetSignificator[];
  house_significators: HouseSignificatorEntry[];
  ruling_planets: RulingPlanetsDetail;
  dasa_hierarchy?: KpDasaBalance;
}

export interface SavedKpChartRecord {
  id: string;
  user_id: string;
  display_number: number;
  chart_type: "natal" | "horary";
  title: string;
  birth_date?: string;
  birth_time?: string;
  horary_number?: number;
  question_text?: string;
  question_date?: string;
  question_time?: string;
  location_name: string;
  latitude: number;
  longitude: number;
  timezone: string;
  ayanamsa_id: number;
  house_system_id: number;
  engine_version: string;
  calculation_result: KpResponse | HoraryKpResponse | any;
  saved_horoscope_id?: string;
  created_at: string;
  updated_at: string;
}

export interface SaveKpChartPayload {
  chart_type: "natal" | "horary";
  title: string;
  customer_full_name?: string;
  customer_phone?: string;
  country_code?: string;
  customer_id?: string;
  normalized_phone?: string;
  whatsapp_number?: string;
  birth_date?: string;
  birth_time?: string;
  horary_number?: number;
  question_text?: string;
  question_date?: string;
  question_time?: string;
  location_name: string;
  latitude: number;
  longitude: number;
  timezone: string;
  ayanamsa_id?: number;
  house_system_id?: number;
  calculation_result: Record<string, any>;
  saved_horoscope_id?: string;
}

export interface AyanamsaOption {
  id: number;
  name: string;
  description: string;
  is_default: boolean;
}

export interface HouseSystemOption {
  id: number;
  name: string;
  description: string;
  is_default: boolean;
}

export interface LanguageOption {
  code: string;
  name: string;
  native_name: string;
}

export interface ChartCapability {
  id: string;
  name: string;
  description: string;
}

export interface MetadataResponse {
  engine: string;
  version: string;
  verified_phases: string[];
  dasa_year_convention: string;
  kp_sub_divisions: number;
  supported_ayanamsas: AyanamsaOption[];
  supported_house_systems: HouseSystemOption[];
  supported_languages: LanguageOption[];
  chart_capabilities: ChartCapability[];
  limitations: string[];
}

export interface HealthEngine {
  name: string;
  version: string;
  rust_core_available: boolean;
  error?: string | null;
}

export interface HealthResponse {
  status: "healthy" | "degraded";
  service: string;
  timestamp_utc: string;
  engine: HealthEngine;
}

export interface ApiValidationError {
  field: string;
  message: string;
  type: string;
}

export interface ApiErrorResponse {
  error: string;
  detail?: string;
  validation_errors?: ApiValidationError[];
}

export interface FullHoroscopeResult {
  horoscope: HoroscopeResponse;
  dasa?: DasaResponse;
  kp?: KpResponse;
  nabhasha?: NabhashaResponse;
  ashtakavarga?: AshtakavargaResponse;
  vedic_yogas?: VedicYogaResponse;
  calculatedAt: string;
  savedId?: string;
  displayNumber?: number;
  isSaved?: boolean;
  saveError?: string;
  saveStatus?: "idle" | "saving" | "saved" | "error";
  idempotencyKey?: string;
  editedAfterCalculation?: boolean;
  clientInputs: {
    fullName?: string;
    birthDate: string;
    birthTime: string;
    isTimeConfirmed: boolean;
    locationName: string;
    latitude: number;
    longitude: number;
    timezone: string;
    ayanamsaId: number;
    houseSystemId: number;
  };
}

export interface CustomerSummary {
  id: string;
  full_name: string;
  birth_date: string;
  country_code: string;
  phone_number: string;
  normalized_phone: string;
  whatsapp_number: string;
}

export interface SavedHoroscopeItem {
  id: string;
  user_id: string;
  display_number: number;
  person_name: string;
  birth_date: string;
  birth_time: string;
  timezone: string;
  birthplace: string;
  latitude: number;
  longitude: number;
  ayanamsa_id: number;
  house_system_id: number;
  customer_id?: string | null;
  customer?: CustomerSummary | null;
  customer_phone?: string | null;
  customer_country_code?: string | null;
  country_code?: string | null;
  normalized_phone?: string | null;
  whatsapp_number?: string | null;
  has_missing_contact?: boolean;
  calculation_result?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface SavedHoroscopesListResponse {
  success: boolean;
  horoscopes: SavedHoroscopeItem[];
  totalCount: number;
  page: number;
  pageSize: number;
  totalPages: number;
  error?: string;
}


// -----------------------------------------------------------------------------
// Numerology Module Types
// -----------------------------------------------------------------------------

export interface TraditionalNumberDetail {
  number_name: string;
  number_value: number;
  calculation_method: string;
  is_master: boolean;
  short_interpretation: string;
  detailed_interpretation: string;
  key_attributes: string[];
}

export interface TraditionalNumerologyRequest {
  full_name: string;
  birth_date: string;
  system_convention: "pythagorean" | "chaldean";
  language: "en" | "ta";
}

export interface TraditionalNumerologyResponse {
  person_name: string;
  birth_date: string;
  system_convention: string;
  engine_version: string;
  life_path: TraditionalNumberDetail;
  expression_destiny: TraditionalNumberDetail;
  soul_urge: TraditionalNumberDetail;
  personality: TraditionalNumberDetail;
  birthday_number: TraditionalNumberDetail;
  attitude_number: TraditionalNumberDetail;
  maturity_number: TraditionalNumberDetail;
  personal_year: TraditionalNumberDetail;
  karmic_lessons: number[];
  hidden_passion: number[];
  strengths: string[];
  challenges: string[];
  career_tendencies: string[];
  financial_tendencies: string[];
  love_themes: string[];
  overall_synthesis: string;
}

export interface DestinyMatrixRequest {
  birth_date: string;
  person_name?: string;
  partner_birth_date?: string;
  partner_name?: string;
  language: "en" | "ta";
}

export interface MatrixNodeDetail {
  node_id: string;
  label: string;
  arcana_number: number;
  arcana_name: string;
  meaning: string;
  positive_traits: string;
  negative_traps: string;
  recommendations: string;
}

export interface PurposeBreakdown {
  personal_purpose: number;
  social_purpose: number;
  spiritual_purpose: number;
  planetary_purpose: number;
}

export interface AgeTimelinePoint {
  age: number;
  arcana_number: number;
  theme: string;
  description: string;
}

export interface CompatibilityResult {
  person1_name: string;
  person2_name: string;
  relationship_purpose: number;
  couple_karmic_task: number;
  shared_finance: number;
  love_harmony: number;
  compatibility_synthesis: string;
}

export interface DestinyMatrixResponse {
  birth_date: string;
  person_name?: string;
  engine_version: string;
  day_arcana: MatrixNodeDetail;
  month_arcana: MatrixNodeDetail;
  year_arcana: MatrixNodeDetail;
  karmic_tail_base: MatrixNodeDetail;
  karmic_tail_triad: number[];
  comfort_zone: MatrixNodeDetail;
  father_spirit: MatrixNodeDetail;
  mother_spirit: MatrixNodeDetail;
  father_matter: MatrixNodeDetail;
  mother_matter: MatrixNodeDetail;
  love_line: MatrixNodeDetail;
  money_line: MatrixNodeDetail;
  purpose: PurposeBreakdown;
  age_timeline: AgeTimelinePoint[];
  compatibility?: CompatibilityResult | null;
  strengths: string[];
  challenges: string[];
  career_tendencies: string[];
  financial_tendencies: string[];
  love_themes: string[];
  overall_synthesis: string;
}

export interface AdvancedAnalysisRequest {
  full_name: string;
  birth_date: string;
  language: "en" | "ta";
}

export interface LoShuGridResult {
  grid_counts: Record<string, number>;
  planes: Record<string, {
    name: string;
    present_count: number;
    description: string;
  }>;
  arrows_of_strength: Array<{
    numbers: string;
    name: string;
    description: string;
  }>;
  arrows_of_weakness: Array<{
    numbers: string;
    name: string;
    description: string;
  }>;
}

export interface PinnacleChallengeResult {
  pinnacles: Array<{
    pinnacle_number: number;
    value: number;
    age_span: string;
    theme: string;
  }>;
  challenges: Array<{
    challenge_number: number;
    value: number;
    age_span: string;
    theme: string;
  }>;
}

export interface AdvancedAnalysisResponse {
  full_name: string;
  birth_date: string;
  engine_version: string;
  unicode_derived_name_number: number;
  lo_shu: LoShuGridResult;
  pinnacles_challenges: PinnacleChallengeResult;
  karmic_debts: Array<{
    number: number;
    origin: string;
    title: string;
    description: string;
  }>;
  karmic_lessons: number[];
  dominant_vibrations: number[];
  strengths: string[];
  challenges: string[];
  career_tendencies: string[];
  financial_tendencies: string[];
  love_themes: string[];
  overall_synthesis: string;
}

export interface SaveNumerologyReportRequest {
  person_name: string;
  birth_date: string;
  method: "traditional" | "destiny_matrix" | "advanced";
  system_convention: string;
  calculation_data: Record<string, any>;
  interpretation_data: Record<string, any>;
}

export interface SavedNumerologyReportResponse {
  id: string;
  user_id: string;
  display_number: number;
  person_name: string;
  birth_date: string;
  method: "traditional" | "destiny_matrix" | "advanced";
  system_convention: string;
  calculation_data: Record<string, any>;
  interpretation_data: Record<string, any>;
  engine_version: string;
  created_at: string;
  updated_at: string;
}

export interface NumerologyMetadataResponse {
  service: string;
  engine_version: string;
  methods: Array<{ id: string; name: string; description: string }>;
  conventions: Array<{ id: string; name: string; default: boolean }>;
  supported_languages: string[];
  disclaimer: string;
}

// ============================================================================
// Muhurta & Panchang Module Data Models
// ============================================================================

export interface OccasionItem {
  id?: string;
  code: string;
  name_en: string;
  name_ta: string;
  category:
    | "marriage_relationships"
    | "family_ceremonies"
    | "home_property"
    | "business_professional"
    | "travel_vehicles"
    | "education_spiritual"
    | "custom";
  description_en?: string;
  description_ta?: string;
  icon: string;
  is_enabled?: boolean;
  is_system?: boolean;
  rules?: Record<string, any>;
}

export interface CandidateSlot {
  id: string;
  event_date: string;
  weekday: string;
  weekday_ta: string;
  start_time_local: string;
  end_time_local: string;
  start_time_utc: string;
  end_time_utc: string;
  duration_minutes: number;
  status:
    | "meets_configured_rules"
    | "meets_rules_with_advisories"
    | "fails_mandatory_rules"
    | "incomplete";
  score: number;
  explanation: string;
  passed_rules: Array<{ rule: string; message: string }>;
  failed_rules: Array<{ rule: string; severity?: string; message: string }>;
  advisories: Array<{ rule: string; message: string }>;
  incomplete_checks: Array<{ check: string; message: string }>;
  tithi: {
    number: number;
    name: string;
    name_ta?: string;
    paksha: string;
    start_time_local?: string;
    end_time_local?: string;
  };
  nakshatra: {
    number: number;
    name: string;
    name_ta?: string;
    lord: string;
    pada: number;
    start_time_local?: string;
    end_time_local?: string;
  };
  yoga: {
    number: number;
    name: string;
  };
  karana: {
    number: number;
    name: string;
  };
  ascendant: {
    sign_index: number;
    sign_name: string;
    sign_name_ta: string;
    degree_in_sign: number;
    nakshatra?: string;
    pada?: number;
  };
  planets: Record<string, any>;
  inauspicious_periods: {
    rahu_kalam: { start_local: string; end_local: string };
    yamagandam: { start_local: string; end_local: string };
    varjyam: { start_local: string; end_local: string };
  };
  auspicious_periods: {
    abhijit: { start_local: string; end_local: string };
    amrita_kalam: { start_local: string; end_local: string };
  };
}

export interface FindMuhurtaResponse {
  occasion: {
    code: string;
    name_en: string;
    name_ta: string;
    category: string;
  };
  search_params: {
    start_date: string;
    end_date: string;
    latitude: number;
    longitude: number;
    timezone: string;
    preferred_time_range: string;
    ayanamsa_id: number;
  };
  total_candidates: number;
  candidates: CandidateSlot[];
  calendar_summary: Record<
    string,
    {
      badge: "auspicious" | "moderate" | "restricted" | "incomplete";
      total_slots: number;
      best_score: number;
      weekday: string;
      tithi: string;
      nakshatra: string;
    }
  >;
}

export interface SavedMuhurtaItem {
  id: string;
  user_id: string;
  display_number: number;
  title: string;
  occasion_code: string;
  occasion_name: string;
  event_date: string;
  start_time: string;
  end_time: string;
  local_start_time: string;
  local_end_time: string;
  duration_minutes: number;
  location_name: string;
  latitude: number;
  longitude: number;
  timezone: string;
  ayanamsa_id: number;
  tradition: string;
  score: number;
  status:
    | "meets_configured_rules"
    | "meets_rules_with_advisories"
    | "fails_mandatory_rules"
    | "incomplete";
  panchang_summary: Record<string, any>;
  lagna_summary: Record<string, any>;
  rule_evaluations: Record<string, any>;
  birth_details?: Record<string, any> | null;
  notes?: string | null;
  client_name?: string | null;
  created_at: string;
  updated_at: string;
}

export interface SaveMuhurtaRequest {
  title?: string;
  occasion_code: string;
  occasion_name: string;
  event_date: string;
  start_time: string;
  end_time: string;
  local_start_time: string;
  local_end_time: string;
  duration_minutes: number;
  location_name: string;
  latitude: number;
  longitude: number;
  timezone: string;
  ayanamsa_id: number;
  tradition: string;
  score: number;
  status: string;
  panchang_summary: Record<string, any>;
  lagna_summary: Record<string, any>;
  rule_evaluations: Record<string, any>;
  birth_details?: Record<string, any> | null;
  notes?: string | null;
  client_name?: string | null;
}

// ==========================================
// KP Event Prediction Engine Interfaces
// ==========================================

export interface HouseSignificationDetail {
  house: number;
  level: string; // L1, L2, L3, L4
  weight: number;
}

export interface EventGradingDetail {
  event: string;
  color: "green" | "orange" | "red";
  grade: "STRONG" | "MODERATE" | "WEAK";
  support_score: number;
  denial_score: number;
  coverage: number;
  supporting: HouseSignificationDetail[];
  denying: HouseSignificationDetail[];
  denied: boolean;
  retrograde_note?: string | null;
  csl_adjustment?: string | null;
  hint: string;
  scoring_metadata?: Record<string, any>;
  supporting_houses_covered?: HouseSignificationDetail[];
  missing_supporting_houses?: number[];
  denying_houses_present?: HouseSignificationDetail[];
  retrograde_delay?: boolean;
  csl_adjustment_reason?: string | null;
}

export interface PeriodSummaryCounts {
  green_count: number;
  orange_count: number;
  red_count: number;
}

export interface PeriodAnalysisResult {
  period: string;
  mahadasha_lord: string;
  bhukti_lord: string;
  antara_lord?: string | null;
  start: string;
  end: string;
  running: boolean;
  is_running?: boolean;
  status: string;
  missing_fields?: string[];
  events: EventGradingDetail[];
  all_events?: EventGradingDetail[];
  summary: PeriodSummaryCounts;
}

export interface OverallAnalysisSummary {
  rule_set_version: string;
  total_periods: number;
  running_period?: string | null;
  green_count: number;
  orange_count: number;
  red_count: number;
  persistence_status?: string;
  persistence_warning?: string;
}

export interface KpEventAnalysisResponse {
  rule_set_version: string;
  lagna?: string | null;
  current_date: string;
  timezone: string;
  overall_summary: OverallAnalysisSummary;
  periods: PeriodAnalysisResult[];
  human_readable_report: string;
  persistence_status?: string;
  persistence_warning?: string;
}

export interface KpEventPeriodInput {
  mahadasha_lord: string;
  bhukti_lord: string;
  antara_lord?: string;
  start_date: string;
  end_date: string;
}

export interface KpEventAnalysisRequest {
  lagna?: string;
  periods: KpEventPeriodInput[];
  significations: Record<string, any>;
  csl_significations?: Record<string, string>;
  retrograde_status?: Record<string, boolean>;
  current_date?: string;
  timezone?: string;
  filter_category?: string;
  filter_grade?: string;
  filter_event?: string;
  running_only?: boolean;
  save_horoscope_id?: string;
}

export interface UserKpAnalysisSummary {
  id: string;
  user_id: string;
  horoscope_id?: string | null;
  rule_set_version: string;
  calculation_timestamp: string;
  created_at: string;
  updated_at: string;
  running_period?: string | null;
  total_periods: number;
  green_count: number;
  orange_count: number;
  red_count: number;
  persistence_status: string;
  person_name?: string | null;
  birth_date?: string | null;
  display_number?: number | null;
  lagna?: string | null;
}

export interface UserKpAnalysisListResponse {
  total_count: number;
  limit: number;
  offset: number;
  items: UserKpAnalysisSummary[];
}

// ------------------------------------------------------------------------------
// Vastu Shastra Models
// ------------------------------------------------------------------------------

export interface DirectionMetadata {
  code: string;
  sanskrit_name: string;
  english_name: string;
  chinese_name: string;
  center_degree: number;
  start_degree: number;
  end_degree: number;
  deity: string;
  element: string;
  planet: string;
  traditional_significance: string;
  recommended_colors: string[];
  color_hex: string[];
  traditional_remedies: string[];
  suitable_uses: string[];
  prohibited_uses: string[];
}

export interface PadaDeityMetadata {
  pada_index: number;
  direction_side: string;
  sanskrit_name: string;
  chinese_name: string;
  nature: "auspicious" | "neutral" | "inauspicious";
  governing_direction: string;
  traditional_result: string;
  start_degree?: number;
  end_degree?: number;
}

export interface VastuDirectionsResponse {
  directions_8: DirectionMetadata[];
  directions_16: DirectionMetadata[];
  padas_32: PadaDeityMetadata[];
  engine_version: string;
}

export interface RoomPlacementsInput {
  main_entrance_direction?: string;
  main_entrance_pada?: string;
  kitchen_direction?: string;
  master_bedroom_direction?: string;
  pooja_room_direction?: string;
  toilet_directions?: string[];
  septic_tank_direction?: string;
  underground_water_tank_direction?: string;
  overhead_water_tank_direction?: string;
  living_room_direction?: string;
  dining_room_direction?: string;
  staircase_direction?: string;
  study_room_direction?: string;
  brahmasthan_status?: "clear" | "partially_obstructed" | "heavily_obstructed" | "unassessed";
  plot_shape?: "square" | "rectangular" | "gaumukhi" | "shermukhi" | "triangular" | "irregular" | "unassessed";
  slope_direction?: string;

  // Commercial
  owner_cabin_direction?: string;
  accounts_cash_direction?: string;
  conference_room_direction?: string;
  reception_direction?: string;

  // Industrial
  heavy_machinery_direction?: string;
  raw_material_storage_direction?: string;
  finished_goods_direction?: string;
  boiler_furnace_direction?: string;
  effluent_treatment_direction?: string;
}

export interface VastuEvaluationRequest {
  property_name: string;
  property_type: "residential" | "commercial" | "plot" | "industrial";
  facing_direction?: string;
  facing_degrees?: number;
  placements?: RoomPlacementsInput;
  saved_horoscope_id?: string;
  person_name?: string;
  birth_date?: string;
  birth_time?: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
}

export interface FactorEvaluation {
  factor_key: string;
  factor_name: string;
  assessed: boolean;
  input_value?: string | null;
  score?: number | null;
  max_weight: number;
  severity: "ideal" | "acceptable" | "moderate_defect" | "severe_defect" | "unassessed";
  traditional_rule: string;
  rule_source: string;
  explanation: string;
  remedy?: string | null;
}

export interface VastuDosha {
  dosha_code: string;
  dosha_name: string;
  severity: "critical" | "major" | "moderate" | "minor";
  zone: string;
  traditional_impact: string;
  traditional_source: string;
  remedies: string[];
}

export interface AstroOverlayResult {
  lagna_sign: string;
  lagna_ruler: string;
  moon_sign?: string;
  nakshatra?: string;
  favorable_directions: string[];
  unfavorable_directions: string[];
  elemental_synergy: string;
  planetary_zone_notes: string[];
  calculation_source: string;
}

export interface VastuEvaluationResponse {
  property_name: string;
  property_type: string;
  facing_direction: string;
  facing_degrees?: number | null;
  engine_version: string;
  rubric_version: string;
  compliance_score?: number | null;
  score_grade?: string | null;
  factors_assessed: number;
  factors_total: number;
  factor_results: FactorEvaluation[];
  doshas: VastuDosha[];
  general_remedies: string[];
  missing_data_warnings: string[];
  conflicting_input_warnings: string[];
  astro_overlay?: AstroOverlayResult | null;
  disclaimer: string;
}

export interface SaveVastuReportRequest {
  property_name: string;
  property_type: "residential" | "commercial" | "plot" | "industrial";
  facing_direction: string;
  facing_degrees?: number | null;
  horoscope_id?: string | null;
  person_name?: string | null;
  birth_date?: string | null;
  evaluation_data: Record<string, any>;
}

export interface SavedVastuReportResponse {
  id: string;
  user_id: string;
  display_number: number;
  property_name: string;
  property_type: string;
  facing_direction: string;
  facing_degrees?: number | null;
  horoscope_id?: string | null;
  person_name?: string | null;
  birth_date?: string | null;
  calculation_data: Record<string, any>;
  dosha_evaluations: Record<string, any>[];
  remedy_recommendations: string[];
  compliance_score: number;
  engine_version: string;
  created_at: string;
  updated_at: string;
}

export interface SavedVastuReportsListResponse {
  reports: SavedVastuReportResponse[];
  total_count: number;
  limit: number;
  offset: number;
}

// ===========================================================================
// KP Transit Timeline Interfaces (Phase 3)
// ===========================================================================

export interface TransitTimelineRequest {
  start_date: string; // YYYY-MM-DD
  start_time?: string; // HH:MM:SS (optional, defaults to 00:00:00)
  end_date?: string; // YYYY-MM-DD (optional)
  end_time?: string; // HH:MM:SS (optional)
  forecast_days?: number; // 7 to 30 days
  timezone: string; // IANA identifier (e.g. "Asia/Kolkata", "UTC") or offset ("+05:30")
  planets?: string[]; // ["Moon", "Sun", "Jupiter", "Saturn", "Rahu", "Ketu", "Mars", "Mercury", "Venus"]
  ayanamsa?: number; // 0 = Lahiri, 1 = KP
  max_events?: number; // 1 to 1000
}

export interface TransitIngressEvent {
  planet: string;
  planet_id: number;
  utc_datetime: string;
  local_datetime: string;
  jd: number;
  boundary_type: "rashi" | "nakshatra" | "sub_lord";
  boundary_longitude: number;
  is_retrograde: boolean;
  speed_deg_per_day: number;

  // Sign transition
  from_sign: string;
  to_sign: string;
  from_sign_lord: string;
  to_sign_lord: string;
  is_rashi_boundary: boolean;

  // Star transition
  from_nakshatra: string;
  to_nakshatra: string;
  from_star_lord: string;
  to_star_lord: string;
  is_nakshatra_boundary: boolean;

  // KP Sub-Lord transition
  from_sub_lord: string;
  to_sub_lord: string;
  from_kp_number: number;
  to_kp_number: number;
  is_sub_lord_boundary: boolean;

  calculation_precision_seconds: number;
}

export interface TransitTimelineBenchmarkStats {
  duration_ms: number;
  total_evaluations: number;
  step_evaluations: number;
  bisection_evaluations: number;
}

export interface TransitTimelineResponse {
  start_time_utc: string;
  start_time_local: string;
  end_time_utc: string;
  end_time_local: string;
  timezone: string;
  utc_offset_hours: number;
  ayanamsa_id: number;
  ayanamsa_name: string;
  forecast_days: number;
  planets_analyzed: string[];
  total_events: number;
  truncated: boolean;
  events: TransitIngressEvent[];
  benchmark_stats?: TransitTimelineBenchmarkStats;
}


// ─── Remedies & Pariharam Module Types ───────────────────────────────────────

export interface SourceReferenceResponse {
  id?: string;
  code: string;
  title_en: string;
  title_sa?: string;
  author?: string;
  tradition: string;
  canonical_status: string;
  description?: string;
  is_published: boolean;
}

export interface ProblemTaxonomyItem {
  id?: string;
  slug: string;
  category: string;
  name_en: string;
  name_ta: string;
  description_en?: string;
  description_ta?: string;
  primary_karakas: string[];
  governing_houses: number[];
  display_order: number;
  is_published: boolean;
  verification_status: string;
}

export interface ProblemTaxonomyListResponse {
  total_count: number;
  categories: string[];
  items: ProblemTaxonomyItem[];
}

export interface RemedyItem {
  id?: string;
  code: string;
  graha: string;
  remedy_type: string;
  name_en: string;
  name_ta: string;
  description_en: string;
  description_ta: string;
  deity_en: string;
  deity_ta: string;
  sanskrit_text?: string;
  transliteration_iast?: string;
  transliteration_ta?: string;
  meaning_en?: string;
  meaning_ta?: string;
  procedure_en: string;
  procedure_ta: string;
  japa_count?: number;
  timing_recommendation_en?: string;
  timing_recommendation_ta?: string;
  source_reference_id?: string;
  source_code?: string;
  source_verse_or_page?: string;
  is_pacification_only: boolean;
  problem_slugs: string[];
  is_published: boolean;
  verification_status: string;
}

export interface RemedyListResponse {
  total_count: number;
  items: RemedyItem[];
}

export interface NavagrahaTempleItem {
  id?: string;
  code: string;
  graha: string;
  name_en: string;
  name_ta: string;
  presiding_deity_en: string;
  presiding_deity_ta: string;
  graha_deity_en: string;
  graha_deity_ta: string;
  place_name_en: string;
  place_name_ta: string;
  district_en: string;
  district_ta: string;
  state: string;
  latitude: number;
  longitude: number;
  visiting_day_en: string;
  visiting_day_ta: string;
  significance_en: string;
  significance_ta: string;
  remedy_offerings_en: string;
  remedy_offerings_ta: string;
  source_tradition: string;
  is_published: boolean;
  verification_status: string;
}

export interface NavagrahaTempleListResponse {
  total_count: number;
  items: NavagrahaTempleItem[];
}

export interface ContentValidationCheck {
  check_name: string;
  is_valid: boolean;
  details: string;
}

export interface ContentValidationReport {
  total_remedies_audited: number;
  total_problems_audited: number;
  total_temples_audited: number;
  checks: ContentValidationCheck[];
  all_passed: boolean;
}

export interface RemedyEligibilityRequest {
  ascendant_sign: string;
  graha: string;
  remedy_type: string;
}

export interface RemedyEligibilityResponse {
  graha: string;
  ascendant_sign: string;
  remedy_type: string;
  is_eligible: boolean;
  is_yogakaraka: boolean;
  is_functional_benefic: boolean;
  is_functional_malefic: boolean;
  restriction_reason?: string;
  safe_alternative_recommendation?: string;
}


// ─── D1 Rasi & D9 Navamsa Varga Module Types ──────────────────────────────────

export interface VargaPlanetPosition {
  name: string;
  body_id: number;
  d1_longitude: number;
  d1_sign_index: number;
  d1_sign_name: string;
  d1_sign_name_tamil: string;
  d1_degree_in_sign: number;
  d1_house: number;
  d1_sign_lord: string;
  d9_sign_index: number;
  d9_sign_name: string;
  d9_sign_name_tamil: string;
  d9_degree_in_sign: number;
  d9_house: number;
  d9_sign_lord: string;
  is_vargottama: boolean;
  is_pushkara_navamsa: boolean;
  is_retrograde: boolean;
  speed_deg_per_day: number;
  nakshatra_name: string;
  nakshatra_index: number;
  pada: number;
  star_lord: string;
}

export interface VargaAscendantPosition {
  d1_degree: number;
  d1_sign_index: number;
  d1_sign_name: string;
  d1_sign_name_tamil: string;
  d1_degree_in_sign: number;
  d1_sign_lord: string;
  d9_sign_index: number;
  d9_sign_name: string;
  d9_sign_name_tamil: string;
  d9_degree_in_sign: number;
  d9_sign_lord: string;
  is_vargottama: boolean;
  nakshatra_name: string;
  nakshatra_index: number;
  pada: number;
  star_lord: string;
}

export interface VargaChartSummary {
  vargottama_planets: string[];
  pushkara_navamsa_planets: string[];
  total_vargottama_count: number;
  d9_lagna_sign: string;
  d9_lagna_sign_tamil: string;
}

export interface VargaD1D9Response {
  metadata: CalculationMetadata;
  ascendant: VargaAscendantPosition;
  planets: VargaPlanetPosition[];
  summary: VargaChartSummary;
  d1_chart: any;
  d9_chart: any;
}

export interface VargaD1D9Request {
  saved_horoscope_id?: string;
  birth_date?: string;
  birth_time?: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
  ayanamsa?: number;
  house_system?: number;
}




