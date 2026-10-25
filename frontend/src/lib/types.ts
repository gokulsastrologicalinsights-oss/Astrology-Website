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
  house?: number;
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
  include_doshas?: boolean;
  gender?: string;
}

export interface DoshaEvaluationItem {
  dosha_id: string;
  name_en: string;
  name_ta: string;
  category: string;
  status: "present" | "mitigated" | "absent" | "indeterminate";
  reference_basis: string;
  formation_conditions: string[];
  involved_planets: string[];
  signs_and_houses: string[];
  degrees: Record<string, number>;
  cancellation_conditions_checked: string[];
  cancellation_evidence: string[];
  interpretation: string;
  interpretation_ta: string;
  rule_set_version: string;
  source_references: string;
  evaluated_at?: string;
  remedies?: string[];
  missing_prerequisites?: string;
}

export interface DoshaSummary {
  total_rules_evaluated: number;
  total_present: number;
  total_mitigated: number;
  total_absent: number;
  total_indeterminate: number;
}

export interface KujaDoshaReferenceDetail {
  reference_point: string;
  reference_sign_index: number;
  reference_sign_name: string;
  mars_house_from_reference: number;
  has_dosha: boolean;
  is_cancelled: boolean;
  cancellation_reasons: string[];
  effective_intensity_percent: number;
}

export interface KujaDoshaResult {
  is_present: boolean;
  is_cancelled: boolean;
  severity: string;
  house_convention: string;
  details_by_reference: Record<string, KujaDoshaReferenceDetail>;
  cancellation_summary?: string;
  interpretation: string;
  interpretation_tamil: string;
}

export interface KaalSarpResult {
  is_present: boolean;
  dosha_type: string;
  subtype_name?: string;
  subtype_name_tamil?: string;
  rahu_house: number;
  ketu_house: number;
  direction?: string;
  planets_inside: string[];
  planets_outside: string[];
  is_cancelled: boolean;
  cancellation_reasons: string[];
  interpretation: string;
  interpretation_tamil: string;
}

export interface SadesatiPhaseInfo {
  is_active: boolean;
  phase: string;
  phase_name_tamil: string;
  natal_moon_sign_index: number;
  natal_moon_sign_name: string;
  transit_saturn_sign_index: number;
  transit_saturn_sign_name: string;
  transit_saturn_degree_in_sign: number;
  saturn_is_retrograde: boolean;
  house_from_moon: number;
  saturn_ashtakavarga_bindus?: number;
  nature_of_transit: string;
  interpretation: string;
  interpretation_tamil: string;
}

export interface UnifiedDoshaResponse {
  metadata?: CalculationMetadata;
  kuja_dosha: KujaDoshaResult;
  kaal_sarp_dosha: KaalSarpResult;
  sadesati: SadesatiPhaseInfo;
  additional_doshas: any[];
  summary_counts: {
    total_doshas_evaluated: number;
    total_active_doshas: number;
    total_cancelled_doshas: number;
  };
  all_doshas: DoshaEvaluationItem[];
  summary?: DoshaSummary;
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
  doshas?: UnifiedDoshaResponse;
  medical_astrology?: MedicalAstrologyResponse;
}

export interface LiveTransitsResponse {
  calculated_at: string;
  timezone: string;
  ayanamsa_id: number;
  ayanamsa_name: string;
  julian_day_ut1: number;
  planets: PlanetInfo[];
}


export interface DasaPeriodAgeDict {
  years: number;
  months: number;
  days: number;
}

export interface DasaBalanceDuration {
  years: number;
  months: number;
  days: number;
  total_days: number;
  total_years: number;
  formatted: string;
}

export interface BenefitBhavasDetail {
  star_lord: string;
  period_lord: string;
  star_lord_houses?: number | null;
  star_lord_owned_houses?: number[];
  planet_placement_house?: number | null;
  planet_owned_houses?: number[];
  formatted: string;
}

export interface BirthDasaBalance {
  birth_date: string;
  birth_time: string;
  moon_sidereal_deg: number;
  nakshatra_name: string;
  nakshatra_pada: number;
  nakshatra_lord: string;
  starting_mahadasha_lord: string;
  mahadasha_full_duration: DasaBalanceDuration;
  elapsed_duration: DasaBalanceDuration;
  remaining_balance: DasaBalanceDuration;
  starting_bhukti_lord?: string;
  starting_bhukti_remaining?: DasaBalanceDuration;
  starting_antharam_lord?: string;
  starting_antharam_remaining?: DasaBalanceDuration;
  starting_sookshamam_lord?: string;
  starting_pranam_lord?: string;
  next_dasa_transition_date: string;
  next_dasa_transition_jd: number;
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
  benefit_bhavas_detail?: BenefitBhavasDetail;
  theoretical_start_jd?: number;
  theoretical_end_jd?: number;
  theoretical_duration_days?: number;
  theoretical_duration_years?: number;
  theoretical_start_date_iso?: string;
  theoretical_end_date_iso?: string;
  is_active?: boolean;
  is_active_at_birth?: boolean;
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
  birth_dasa_balance?: BirthDasaBalance;
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
  level_a?: number[];
  level_b?: number[];
  level_c?: number[];
  level_d?: number[];
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
  doshas?: UnifiedDoshaResponse;
  shadbala?: ShadbalaResponse;
  medical_astrology?: MedicalAstrologyResponse;
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
  location_name?: string;
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
  raw_value?: number;
  reduction_steps?: string[];
}

export interface LetterMapping {
  char: string;
  value: number;
  is_vowel: boolean;
  word: string;
}

export interface WordBreakdown {
  word: string;
  letter_sum: number;
  vowel_sum: number;
  consonant_sum: number;
  reduced_expression: number;
}

export interface KarmicDebtItem {
  number: number;
  source: string;
  title: string;
  description: string;
  remedy_focus: string;
}

export interface CalculationBreakdown {
  system_convention: string;
  source_birth_date: string;
  birth_date_digits: number[];
  life_path_period_reduction: Record<string, any>;
  life_path_full_sum: Record<string, any>;
  birth_number_reduction: Record<string, any>;
  letter_mappings: LetterMapping[];
  word_breakdowns: WordBreakdown[];
  expression_reduction: string[];
  soul_urge_reduction: string[];
  personality_reduction: string[];
  maturity_reduction: string[];
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
  birth_psychic_number?: TraditionalNumberDetail;
  life_path: TraditionalNumberDetail;
  expression_destiny: TraditionalNumberDetail;
  soul_urge: TraditionalNumberDetail;
  personality: TraditionalNumberDetail;
  birthday_number: TraditionalNumberDetail;
  attitude_number: TraditionalNumberDetail;
  maturity_number: TraditionalNumberDetail;
  personal_year: TraditionalNumberDetail;
  karmic_debts?: KarmicDebtItem[];
  calculation_breakdown?: CalculationBreakdown;
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
  method: "traditional" | "destiny_matrix" | "advanced" | "name_correction" | "business" | "phone" | "vehicle" | "property" | "marriage" | "family";
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
  method: "traditional" | "destiny_matrix" | "advanced" | "name_correction" | "business" | "phone" | "vehicle" | "property" | "marriage" | "family";
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

// -----------------------------------------------------------------------------
// Name Suggestion & Correction Studio Types
// -----------------------------------------------------------------------------

export interface NameComponentDetail {
  component_type: string;
  text: string;
  expression: number;
  compound_expression: number;
  soul_urge: number;
  personality: number;
  reduction_steps: string[];
  letter_mappings: LetterMapping[];
}

export interface NameAnalysisRequest {
  full_name: string;
  system_convention: "pythagorean" | "chaldean";
  language: "en" | "ta";
}

export interface NameAnalysisResponse {
  full_name: string;
  convention: string;
  engine_version: string;
  expression: number;
  compound_expression: number;
  soul_urge: number;
  personality: number;
  is_master: boolean;
  reduction_steps: string[];
  letter_mappings: LetterMapping[];
  word_breakdowns: WordBreakdown[];
  components: NameComponentDetail[];
}

export interface NameCorrectionRequest {
  original_name: string;
  system_convention: "pythagorean" | "chaldean";
  target_number?: number;
  birth_date?: string;
  custom_variations?: string[];
  language?: "en" | "ta";
  max_candidates?: number;
  allow_vowel_changes?: boolean;
  allow_consonant_doubling?: boolean;
  allow_phonetic_replacements?: boolean;
}

export interface NameCandidateResult {
  name: string;
  variation_type: string;
  expression_number: number;
  compound_expression: number;
  soul_urge_number: number;
  personality_number: number;
  is_master: boolean;
  matches_target: boolean;
  harmony_score: number;
  pronunciation_score: number;
  simplicity_score: number;
  composite_score: number;
  letter_mappings: LetterMapping[];
  word_breakdowns: WordBreakdown[];
  reduction_steps: string[];
  vibrational_synthesis: string;
}

export interface NameCorrectionResponse {
  original_name: string;
  system_convention: string;
  engine_version: string;
  target_number: number;
  target_source: string;
  original_analysis: NameAnalysisResponse;
  candidates: NameCandidateResult[];
  scoring_explanation: {
    formula: string;
    weights: {
      numerological_harmony: number;
      pronunciation_preservation: number;
      spelling_simplicity: number;
    };
    target_number: number;
    target_source: string;
    psychic_number?: number;
    life_path_number?: number;
    selected_convention: string;
    disclaimer: string;
  };
}

// -----------------------------------------------------------------------------
// Business & Brand Numerology Studio Types
// -----------------------------------------------------------------------------

export interface FounderInput {
  name: string;
  birth_date?: string;
  role?: string;
  share_percentage?: number;
}

export interface FounderEvaluationResult {
  name: string;
  birth_date?: string;
  role?: string;
  share_percentage?: number;
  psychic_number?: number;
  life_path_number?: number;
  name_expression: number;
  psychic_harmony_score?: number;
  life_path_harmony_score?: number;
  alignment_score: number;
  alignment_level: string;
  notes: string;
}

export interface TaglineAnalysisResult {
  tagline: string;
  expression_number: number;
  compound_expression: number;
  synergy_score: number;
  synergy_interpretation: string;
}

export interface DomainHandleAnalysisResult {
  raw_handle: string;
  clean_handle: string;
  expression_number: number;
  compound_expression: number;
  matches_brand: boolean;
}

export interface BusinessCandidateResult {
  name: string;
  candidate_type: string;
  expression_number: number;
  compound_expression: number;
  soul_urge_number: number;
  personality_number: number;
  is_master: boolean;
  industry_harmony_score: number;
  founder_harmony_score: number;
  pronunciation_score: number;
  simplicity_score: number;
  composite_score: number;
  is_favorable: boolean;
  vibrational_synthesis: string;
  letter_mappings: LetterMapping[];
  reduction_steps: string[];
  founder_alignments: FounderEvaluationResult[];
}

export interface BusinessNumerologyRequest {
  legal_name: string;
  brand_name?: string;
  tagline?: string;
  domain_or_handle?: string;
  system_convention: "pythagorean" | "chaldean";
  industry_category:
    | "technology"
    | "retail"
    | "education"
    | "healthcare"
    | "finance"
    | "manufacturing"
    | "astrology"
    | "creative"
    | "other";
  founders?: FounderInput[];
  custom_candidates?: string[];
  max_candidates?: number;
  language?: "en" | "ta";
}

export interface BusinessNumerologyResponse {
  legal_name: string;
  normalized_brand_name: string;
  acronym: string;
  detected_suffixes: string[];
  system_convention: string;
  industry_category: string;
  industry_vibrations: {
    name: string;
    primary_numbers: number[];
    secondary_numbers: number[];
    planetary_ruler: string;
    traditional_rationale: string;
  };
  engine_version: string;
  legal_analysis: BusinessCandidateResult;
  brand_analysis: BusinessCandidateResult;
  tagline_analysis?: TaglineAnalysisResult;
  domain_analysis?: DomainHandleAnalysisResult;
  partnership_matrix: {
    overall_partnership_score: number;
    has_friction: boolean;
    friction_founders: string[];
    founder_results: FounderEvaluationResult[];
    synthesis: string;
  };
  candidates: BusinessCandidateResult[];
  scoring_explanation: {
    formula: string;
    weights: {
      founder_harmony: number;
      industry_alignment: number;
      pronunciation_preservation: number;
      spelling_simplicity: number;
    };
    industry_profile: {
      key: string;
      name: string;
      primary_numbers: number[];
      planetary_ruler: string;
      rationale: string;
    };
    selected_convention: string;
    disclaimer: string;
  };
}

// -----------------------------------------------------------------------------
// Phone & Mobile Number Numerology Studio Types
// -----------------------------------------------------------------------------

export interface PhoneAnalysisDetail {
  digits: string;
  digit_count: number;
  compound_sum: number;
  root_number: number;
  single_root: number;
  is_master: boolean;
  reduction_steps: string[];
  frequencies: Record<string, number>;
  dominant_digits: number[];
  missing_digits: number[];
  zero_count: number;
  ruling_planet: string;
  keyword: string;
  vibrational_meaning: string;
  patterns: {
    repeats: Array<{
      digit: number;
      count: number;
      pattern: string;
      label: string;
    }>;
    sequences: Array<{
      sequence: string;
      type: string;
      length: number;
    }>;
    mirrors: string[];
    vanity_score: number;
    is_vip_vanity: boolean;
  };
}

export interface PhoneCandidateResult {
  raw_input: string;
  masked_phone: string;
  national_number: string;
  formatted_national: string;
  display_international: string;
  country_name?: string | null;
  country_code?: string | null;
  compound_sum: number;
  root_number: number;
  single_root: number;
  is_master: boolean;
  reduction_steps: string[];
  frequencies: Record<string, number>;
  dominant_digits: number[];
  missing_digits: number[];
  zero_count: number;
  ruling_planet: string;
  keyword: string;
  vibrational_meaning: string;
  patterns: {
    repeats: Array<{
      digit: number;
      count: number;
      pattern: string;
      label: string;
    }>;
    sequences: Array<{
      sequence: string;
      type: string;
      length: number;
    }>;
    mirrors: string[];
    vanity_score: number;
    is_vip_vanity: boolean;
  };
  personal_compatibility?: {
    birth_date: string;
    psychic_number: number;
    life_path_number: number;
    psychic_harmony_score: number;
    life_path_harmony_score: number;
    personal_score: number;
    level: string;
    synthesis: string;
  } | null;
  industry_compatibility?: {
    industry_category: string;
    industry_name: string;
    planetary_ruler: string;
    primary_numbers: number[];
    secondary_numbers: number[];
    score: number;
    level: string;
    description: string;
  } | null;
  personal_score?: number | null;
  industry_score?: number | null;
  vanity_score: number;
  composite_score: number;
  is_favorable: boolean;
}

export interface PhoneNumerologyRequest {
  phone_number: string;
  system_convention?: "pythagorean" | "chaldean";
  include_country_code?: boolean;
  birth_date?: string;
  industry_category?:
    | "technology"
    | "retail"
    | "education"
    | "healthcare"
    | "finance"
    | "manufacturing"
    | "astrology"
    | "creative"
    | "other";
  candidate_numbers?: string[];
  max_candidates?: number;
  language?: "en" | "ta";
}

export interface PhoneNumerologyResponse {
  raw_input: string;
  masked_phone: string;
  national_number: string;
  formatted_national: string;
  all_digits: string;
  display_international: string;
  detected_country_code?: string | null;
  detected_country_name?: string | null;
  is_indian_mobile: boolean;
  system_convention: string;
  include_country_code: boolean;
  engine_version: string;
  primary_analysis: PhoneAnalysisDetail;
  national_analysis: PhoneAnalysisDetail;
  international_analysis: PhoneAnalysisDetail;
  missing_digits_analysis: Array<{
    digit: number;
    lesson: string;
  }>;
  zero_significance: string;
  personal_compatibility?: {
    birth_date: string;
    psychic_number: number;
    life_path_number: number;
    psychic_harmony_score: number;
    life_path_harmony_score: number;
    personal_score: number;
    level: string;
    synthesis: string;
  } | null;
  industry_compatibility?: {
    industry_category: string;
    industry_name: string;
    planetary_ruler: string;
    primary_numbers: number[];
    secondary_numbers: number[];
    score: number;
    level: string;
    description: string;
  } | null;
  candidates: PhoneCandidateResult[];
  scoring_explanation: {
    selected_basis: string;
    formula: string;
    weights: {
      personal_harmony: number;
      industry_match: number;
      vanity_rhythm: number;
    };
    privacy_notice: string;
    disclaimer: string;
  };
}

// ============================================================================
// Vehicle & Asset Registration Number Numerology Models
// ============================================================================

export interface VehicleOwnerInput {
  name: string;
  birth_date: string;
  role?: string;
  is_primary?: boolean;
}

export interface VehicleOwnerEvaluation {
  name: string;
  birth_date: string;
  role: string;
  is_primary: boolean;
  psychic_number: number;
  life_path_number: number;
  psychic_harmony_score: number;
  life_path_harmony_score: number;
  personal_score: number;
  level: string;
  synthesis: string;
}

export interface VehicleAnalysisDetail {
  calculation_mode: string;
  mode_label: string;
  source_string: string;
  character_mappings: Array<{
    char: string;
    value: number;
    type: "digit" | "letter" | "unknown";
  }>;
  compound_sum: number;
  root_number: number;
  single_root: number;
  is_master: boolean;
  reduction_steps: string[];
  ruling_planet: string;
  keyword: string;
  vibrational_meaning: string;
}

export interface VehicleCandidateResult {
  raw_input: string;
  normalized_registration: string;
  plate_classification: string;
  state_code?: string | null;
  state_name?: string | null;
  rto_code?: string | null;
  series_letters?: string | null;
  numeric_digits: string;
  calculation_mode: string;
  compound_sum: number;
  root_number: number;
  single_root: number;
  is_master: boolean;
  reduction_steps: string[];
  patterns: {
    vanity_score: number;
    pattern_tags: string[];
    pattern_classification: string;
    is_vip_number: boolean;
    repeats: string[];
    is_ascending: boolean;
    is_descending: boolean;
    is_mirror: boolean;
    details: string;
  };
  vanity_score: number;
  usage_score?: number | null;
  owner_score?: number | null;
  composite_score: number;
  is_favorable: boolean;
}

export interface VehicleNumerologyRequest {
  registration_number: string;
  system_convention?: "pythagorean" | "chaldean";
  calculation_mode?: "digits_only" | "numeric_all" | "full_alphanumeric";
  vehicle_usage?: "personal" | "family" | "commercial" | "fleet";
  primary_birth_date?: string;
  primary_owner_name?: string;
  co_owners?: VehicleOwnerInput[];
  candidate_numbers?: string[];
  max_candidates?: number;
  language?: "en" | "ta";
}

export interface VehicleNumerologyResponse {
  raw_input: string;
  normalized_registration: string;
  formatted_registration: string;
  state_code?: string | null;
  state_name?: string | null;
  rto_code?: string | null;
  series_letters?: string | null;
  numeric_digits: string;
  is_valid_indian_format: boolean;
  plate_classification: string;
  system_convention: string;
  calculation_mode: string;
  vehicle_usage: string;
  engine_version: string;
  primary_analysis: VehicleAnalysisDetail;
  digits_only_analysis: VehicleAnalysisDetail;
  numeric_all_analysis: VehicleAnalysisDetail;
  full_alphanumeric_analysis: VehicleAnalysisDetail;
  patterns: {
    vanity_score: number;
    pattern_tags: string[];
    pattern_classification: string;
    is_vip_number: boolean;
    repeats: string[];
    is_ascending: boolean;
    is_descending: boolean;
    is_mirror: boolean;
    details: string;
  };
  vanity_score: number;
  usage_alignment: {
    vehicle_usage: string;
    usage_name: string;
    planetary_rulers: string;
    primary_numbers: number[];
    secondary_numbers: number[];
    score: number;
    level: string;
    description: string;
  };
  owner_alignments: VehicleOwnerEvaluation[];
  overall_owner_score?: number | null;
  candidates: VehicleCandidateResult[];
  scoring_explanation: {
    active_mode: string;
    system_convention: string;
    calculation_rules: Record<string, string>;
    vanity_scoring: string;
    usage_weighting: string;
  };
  disclaimer: string;
}

// ============================================================================
// House, Flat & Property Numerology Models
// ============================================================================

export interface PropertyResidentInput {
  name: string;
  birth_date: string;
  role?: string;
  is_primary?: boolean;
}

export interface PropertyResidentEvaluation {
  name: string;
  birth_date: string;
  role: string;
  is_primary: boolean;
  psychic_number: number;
  life_path_number: number;
  psychic_harmony_score: number;
  life_path_harmony_score: number;
  personal_score: number;
  level: string;
  synthesis: string;
}

export interface PropertyComponentDetail {
  component_name: string;
  component_label: string;
  calculation_mode?: string | null;
  source_string: string;
  included_characters: string[];
  character_mappings: Array<{
    char: string;
    value: number;
    type: "digit" | "letter" | "unknown";
  }>;
  compound_sum: number;
  root_number: number;
  single_root: number;
  is_master: boolean;
  reduction_steps: string[];
  ruling_planet: string;
  keyword: string;
  vibrational_meaning: string;
  formula_explanation?: string | null;
}

export interface PropertyCandidateInput {
  door_flat_number?: string;
  building_number?: string;
  floor_number?: string;
  plot_number?: string;
  building_name?: string;
  label?: string;
}

export interface PropertyCandidateResult {
  label: string;
  door_flat_number?: string | null;
  building_number?: string | null;
  floor_number?: string | null;
  plot_number?: string | null;
  building_name?: string | null;
  calculation_mode: string;
  compound_sum: number;
  root_number: number;
  single_root: number;
  is_master: boolean;
  reduction_steps: string[];
  ruling_planet: string;
  keyword: string;
  usage_score: number;
  owner_score?: number | null;
  composite_score: number;
  is_favorable: boolean;
}

export interface PropertyNumerologyRequest {
  property_category?:
    | "independent_house"
    | "apartment_flat"
    | "commercial_office"
    | "commercial_shop"
    | "plot_land"
    | "multi_unit";
  tenure_type?: "purchased" | "rental";
  door_flat_number?: string;
  building_number?: string;
  block_or_wing?: string;
  floor_number?: string;
  plot_number?: string;
  building_name?: string;
  facing_direction?: string;
  property_usage?:
    | "residential_living"
    | "commercial_business"
    | "rental_investment"
    | "creative_studio"
    | "spiritual_wellness";
  system_convention?: "pythagorean" | "chaldean";
  calculation_mode?:
    | "door_number"
    | "building_number"
    | "floor_number"
    | "plot_number"
    | "combined_property"
    | "full_alphanumeric";
  primary_birth_date?: string;
  primary_owner_name?: string;
  co_residents?: PropertyResidentInput[];
  candidate_properties?: PropertyCandidateInput[];
  max_candidates?: number;
  language?: "en" | "ta";
}

export interface PropertyNumerologyResponse {
  property_category: string;
  tenure_type: string;
  door_flat_number: string;
  building_number: string;
  block_or_wing: string;
  floor_number: string;
  plot_number: string;
  building_name: string;
  facing_direction?: string | null;
  full_identifier: string;
  system_convention: string;
  calculation_mode: string;
  property_usage: string;
  primary_analysis: PropertyComponentDetail;
  door_analysis: PropertyComponentDetail;
  building_analysis: PropertyComponentDetail;
  floor_analysis: PropertyComponentDetail;
  plot_analysis: PropertyComponentDetail;
  combined_analysis: PropertyComponentDetail;
  full_alphanumeric_analysis: PropertyComponentDetail;
  usage_alignment: {
    property_usage: string;
    usage_name: string;
    planetary_rulers: string;
    primary_numbers: number[];
    secondary_numbers: number[];
    score: number;
    level: string;
    description: string;
  };
  vastu_alignment?: {
    facing_direction: string;
    sanskrit_name: string;
    presiding_deity: string;
    element: string;
    ruling_planet: string;
    energy_type: string;
    alignment_score: number;
    alignment_level: string;
    notes: string;
  } | null;
  resident_alignments: PropertyResidentEvaluation[];
  overall_household_score?: number | null;
  candidates: PropertyCandidateResult[];
  scoring_explanation: {
    active_mode: string;
    system_convention: string;
    calculation_rules: Record<string, string>;
    vastu_integration: string;
    resident_harmony: string;
  };
  disclaimer: string;
}

// ============================================================================
// Marriage Compatibility by Numerology Studio Types
// ============================================================================

export interface MarriagePersonInput {
  full_name?: string | null;
  birth_date: string;
  preferred_name?: string | null;
  surname_initials?: string | null;
  relationship_status?: string | null;
  language?: "en" | "ta";
}

export interface MarriagePersonProfile {
  person_label: string;
  full_name?: string | null;
  preferred_name?: string | null;
  surname_initials?: string | null;
  birth_date: string;
  birth_psychic_number: number;
  birth_psychic_compound: number;
  birth_psychic_planet: string;
  birth_psychic_archetype: string;
  birth_psychic_reduction_steps: string[];
  life_path_number: number;
  life_path_compound: number;
  life_path_planet: string;
  life_path_archetype: string;
  life_path_reduction_steps: string[];
  is_life_path_master: boolean;
  expression_number?: number | null;
  expression_compound?: number | null;
  expression_planet?: string | null;
  expression_reduction_steps?: string[] | null;
  is_expression_master?: boolean;
  soul_urge_number?: number | null;
  soul_urge_compound?: number | null;
  personality_number?: number | null;
  personality_compound?: number | null;
  master_numbers: number[];
  karmic_debts: Array<{
    number: number;
    source: string;
    title: string;
    description: string;
    remedy_focus: string;
  }>;
  key_attributes: string[];
}

export interface MarriageComponentComparison {
  component_name: string;
  person_a_number: number;
  person_b_number: number;
  person_a_label: string;
  person_b_label: string;
  score: number;
  weight: number;
  harmony_level: string;
  planetary_dynamic: string;
  interpretation: string;
}

export interface MarriageNumerologyRequest {
  person_a: MarriagePersonInput;
  person_b: MarriagePersonInput;
  system_convention: "pythagorean" | "chaldean";
  language: "en" | "ta";
}

export interface MarriageNumerologyResponse {
  system_convention: string;
  engine_version: string;
  relationship_status?: string | null;
  person_a_profile: MarriagePersonProfile;
  person_b_profile: MarriagePersonProfile;
  psychic_compatibility: MarriageComponentComparison;
  life_path_compatibility: MarriageComponentComparison;
  expression_compatibility?: MarriageComponentComparison | null;
  soul_urge_compatibility?: MarriageComponentComparison | null;
  personality_compatibility?: MarriageComponentComparison | null;
  emotional_themes: string[];
  communication_themes: string[];
  shared_strengths: string[];
  potential_challenges: string[];
  conversation_prompts: string[];
  growth_recommendations: string[];
  overall_score: number;
  overall_harmony_level: string;
  overall_synthesis: string;
  scoring_formula_explanation: {
    formula: string;
    weights: Record<string, number>;
    has_name_derived_comparison: boolean;
    methodology: string;
  };
  disclaimer: string;
}

// ----------------------------------------------------------------------------
// Family & Baby Numerology Studio Types
// ----------------------------------------------------------------------------

export interface FamilyMemberInput {
  id: string;
  name?: string;
  birth_date?: string;
  role?: string;
  relationship?: string;
  gender?: string;
  preferred_name?: string;
  surname?: string;
}

export interface FamilyMemberEvaluation {
  id: string;
  name: string;
  role: string;
  birth_date?: string | null;
  birth_psychic_number?: number | null;
  birth_psychic_planet?: string | null;
  life_path_number?: number | null;
  life_path_planet?: string | null;
  is_life_path_master: boolean;
  expression_number?: number | null;
  compound_expression?: number | null;
  soul_urge_number?: number | null;
  personality_number?: number | null;
  karmic_debts: number[];
  archetype: string;
  element: string;
  reduction_steps: string[];
  short_summary: string;
  ruling_planet?: string | null;
}

export interface BabyNameCandidateResult {
  name: string;
  is_generated: boolean;
  variation_type: string;
  pythagorean_expression: number;
  pythagorean_compound: number;
  chaldean_expression: number;
  chaldean_compound: number;
  active_expression: number;
  active_compound: number;
  soul_urge: number;
  personality: number;
  ruling_planet: string;
  archetype: string;
  dob_harmony_score: number;
  parent_harmony_score: number;
  pronunciation_score: number;
  simplicity_score: number;
  composite_score: number;
  is_master: boolean;
  reduction_steps: string[];
  letter_mappings: Array<{
    char: string;
    value: number;
    is_vowel: boolean;
    word?: string;
  }>;
  vibrational_synthesis: string;
}

export interface FamilyPairwiseComparison {
  person_a_id: string;
  person_a_name: string;
  person_a_role: string;
  person_b_id: string;
  person_b_name: string;
  person_b_role: string;
  relationship_type: string;
  psychic_harmony_score: number;
  life_path_harmony_score: number;
  expression_harmony_score?: number | null;
  composite_harmony_score: number;
  harmony_level: string;
  planetary_dynamic: string;
  shared_strengths: string[];
  growth_edges: string[];
  nurturing_prompt: string;
  parenting_dialogue_prompt?: string | null;
}

export interface FamilyDistributionItem {
  number: number;
  count: number;
  percentage: number;
  ruling_planet: string;
  element: string;
  members_with_number: string[];
}

export interface FamilyNumerologyRequest {
  family_name?: string;
  members: FamilyMemberInput[];
  candidate_names?: string[];
  baby_candidates?: string[];
  baby_dob?: string;
  surname?: string;
  target_root?: number;
  system_convention: "pythagorean" | "chaldean";
  generate_suggestions: boolean;
  language: "en" | "ta";
}

export interface FamilyNumerologyResponse {
  family_name: string;
  system_convention: string;
  language: string;
  members_evaluated: FamilyMemberEvaluation[];
  pairwise_comparisons: FamilyPairwiseComparison[];
  number_distribution: FamilyDistributionItem[];
  dominant_vibrations: number[];
  missing_vibrations: number[];
  elemental_balance: Record<string, any>;
  baby_name_candidates: BabyNameCandidateResult[];
  overall_family_harmony_score: number;
  overall_family_harmony_level: string;
  scoring_formula_explanation: Record<string, any>;
  family_strengths: string[];
  family_challenges: string[];
  reflection_questions: string[];
  overall_synthesis: string;
  engine_version: string;
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
  requires_manual_astrologer_review?: boolean;
  is_review_gated?: boolean;
}

export interface NeechaBhangaAssessment {
  graha: string;
  d1_sign: string;
  d1_house?: number | null;
  is_d1_debilitated: boolean;
  d9_data_status: "verified" | "unavailable" | "insufficient_data" | string;
  d9_sign?: string | null;
  d9_house?: number | null;
  is_d9_exalted: boolean;
  is_d9_own_sign: boolean;
  is_vargottama: boolean;
  cancellation_status: "none" | "cancellation_indicator_present" | "complete_nbry_qualifying" | "nbry_neutralized_by_combustion" | "insufficient_data" | string;
  has_cancellation_indicator: boolean;
  is_complete_nbry: boolean;
  is_combust: boolean;
  qualifying_criteria: string[];
  rule_identifiers: string[];
  severity: "mild" | "moderate" | "high" | string;
  reason_en: string;
  reason_ta: string;
  supporting_placements: Record<string, any>;
  confidence_status: "high" | "medium" | "conditional" | "unresolved" | string;
  unresolved_interpretation?: string | null;
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

// ==========================================
// KP Events & Prediction Types
// ==========================================

export interface SupportedKpEventItem {
  name: string;
  category: string;
  primary_cusp: number;
  supporting_houses: number[];
  denying_houses: number[];
  is_gain_type: boolean;
  description: string;
}

export interface KpPredictionScanRequest {
  horoscope_id?: string;
  birth_date?: string;
  birth_time?: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
  place_name?: string;
  customer_name?: string;
  event_name: string;
  start_date?: string;
  end_date?: string;
  scan_resolution_minutes?: number;
  max_candidates?: number;
  include_ruling_planets?: boolean;
  judgement_datetime?: string;
  judgement_latitude?: number;
  judgement_longitude?: number;
  judgement_timezone?: string;
  scan_mode?: "standard" | "deep";
  deep_refinement_target?: "sub_lord" | "sub_sub_lord";
  deep_max_intervals_to_refine?: number;
}

export interface KpEventPromiseResult {
  event_name: string;
  category: string;
  primary_cusp: number;
  cusp_degree: number;
  cusp_sign: string;
  cusp_star_lord: string;
  cusp_sub_lord: string;
  csl_significations: number[];
  supporting_houses: number[];
  denying_houses: number[];
  promise_status: string; // "Promised" | "Delayed / Mixed" | "Denied / Weak"
  is_csl_retrograde: boolean;
  is_star_lord_retrograde: boolean;
  supporting_hits: number[];
  denying_hits: number[];
  rule_explanation: string;
}

export interface KpDashaPeriodResult {
  level: number;
  mahadasha_lord: string;
  bhukti_lord?: string;
  antara_lord?: string;
  start_date: string;
  end_date: string;
  is_running: boolean;
  signified_houses: number[];
  support_status: string;
  scoring_explanation: string;
}

export interface RulingPlanetsInfo {
  judgement_time: string;
  judgement_place: string;
  ascendant_sign_lord: string;
  ascendant_star_lord: string;
  moon_sign_lord: string;
  moon_star_lord: string;
  day_lord: string;
  active_ruling_planets: string[];
  rejected_ruling_planets: Array<{ planet: string; role: string; reason: string }>;
}

export interface KpCandidateTimeWindow {
  id: string;
  date: string;
  start_time: string;
  end_time: string;
  timezone: string;
  evidence_grade: "A" | "B" | "C";
  composite_score: number;
  dasha_chain: string;
  dasha_favorable: boolean;
  moon_transit: {
    sign: string;
    sign_lord: string;
    star: string;
    star_lord: string;
    sub_lord: string;
    sub_sub_lord: string;
  };
  lagna_transit: {
    sign: string;
    sign_lord: string;
    star: string;
    star_lord: string;
    sub_lord: string;
    sub_sub_lord: string;
  };
  ruling_planets_matched: string[];
  supporting_houses_activated: number[];
  explanation: string;
  scan_mode?: "standard" | "deep";
  refinement_resolution?: string;
  precision_seconds?: number;
  transit_transitions?: {
    refinement_level?: string;
    astronomical_precision_seconds?: number;
    lagna_ingress_time?: string;
    lagna_egress_time?: string;
    lagna_ingress_degree?: number;
    lagna_egress_degree?: number;
    lagna_sub_lord?: string;
    lagna_sub_sub_lord?: string;
    moon_sub_lord_ingress_in_window?: boolean;
    moon_crossing_time?: string | null;
    moon_from_sub_lord?: string | null;
    moon_to_sub_lord?: string | null;
    dasha_transition_in_window?: boolean;
    dasha_chain_at_midpoint?: string;
    disclaimer?: string;
  };
}

export interface KpPredictionResponse {
  horoscope_id?: string;
  customer_name?: string;
  birth_details: {
    birth_date: string;
    birth_time: string;
    timezone: string;
    latitude: number;
    longitude: number;
    birth_place: string;
  };
  calculation_convention: string;
  birth_time_accuracy_warning: string;
  event_promise: KpEventPromiseResult;
  ruling_planets?: RulingPlanetsInfo;
  candidate_dasha_periods: KpDashaPeriodResult[];
  candidate_windows: KpCandidateTimeWindow[];
  total_windows_found: number;
  scan_parameters: {
    start_date: string;
    end_date: string;
    scan_resolution_minutes: number;
    max_candidates: number;
    scan_mode?: string;
    deep_refinement_target?: string;
    deep_max_intervals_to_refine?: number;
    benchmark_metrics?: Record<string, any>;
  };
  limitations_disclaimer: string;
  report_markdown: string;
}


export interface ChartFactorExplanation {
  factor_type: string;
  graha: string;
  house?: number | null;
  title_en: string;
  title_ta: string;
  description_en: string;
  description_ta: string;
  rule_reference: string;
  is_confirmed: boolean;
  severity: string;
  neecha_bhanga?: NeechaBhangaAssessment | null;
}

export interface RecommendedRemedy {
  remedy: RemedyItem;
  relevance_score: number;
  priority_tier: "essential" | "recommended" | "optional" | string;
  reason_en: string;
  reason_ta: string;
  matching_factors: string[];
  yogakaraka_warning?: string | null;
  temple?: NavagrahaTempleItem | null;
}

export interface ChartContextSummary {
  lagna_sign: string;
  lagna_lord?: string | null;
  running_mahadasha?: string | null;
  running_bhukti?: string | null;
  running_pratyantardasha?: string | null;
  yogakaraka_graha?: string | null;
  yogakaraka_planets?: string[];
  functional_benefics: string[];
  functional_malefics: string[];
  afflicted_grahas?: string[];
  afflicted_bhavas?: number[];
  debilitated_planets?: string[];
  combust_planets?: string[];
  exalted_planets?: string[];
  kuja_dosha_status?: string;
  kuja_dosha_present?: boolean;
  kuja_dosha_cancelled?: boolean;
  kuja_dosha_cancellation_reason?: string | null;
  d9_data_status?: string;
  d9_planetary_signs?: Record<string, string>;
  vargottama_planets?: string[];
  neecha_bhanga_assessments?: NeechaBhangaAssessment[];
}

export interface RemedyAnalysisResponse {
  horoscope_id?: string | null;
  person_name?: string | null;
  birth_date?: string | null;
  birth_time?: string | null;
  chart_context: ChartContextSummary;
  diagnosed_factors: ChartFactorExplanation[];
  recommendations: RecommendedRemedy[];
  total_recommendations: number;
  input_fingerprint: string;
  classical_disclaimer_en: string;
  classical_disclaimer_ta: string;
  status: string;
}

export interface LiveRemedyAnalysisRequest {
  birth_date?: string | null;
  birth_time?: string | null;
  timezone?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  ayanamsa?: number | null;
  chart_snapshot?: Record<string, any> | null;
}

export interface SaveRemedyReportRequest {
  horoscope_id: string;
  input_data_fingerprint: string;
  person_name?: string | null;
  review_status: "draft" | "reviewed" | "approved";
  astrologer_notes?: string | null;
  selected_remedy_codes: string[];
  language: "en" | "ta";
  analysis_snapshot: RemedyAnalysisResponse;
}

export interface SavedRemedyReportResponse {
  id: string;
  horoscope_id: string;
  user_id: string;
  person_name?: string | null;
  input_data_fingerprint: string;
  review_status: "draft" | "reviewed" | "approved";
  astrologer_notes?: string | null;
  selected_remedy_codes: string[];
  language: "en" | "ta";
  analysis_snapshot: RemedyAnalysisResponse;
  created_at: string;
  updated_at: string;
}

export interface SavedRemedyReportsListResponse {
  total_count: number;
  reports: SavedRemedyReportResponse[];
}


// ─── Kaveri Delta Navagraha Pilgrimage Circuit Types ──────────────────────────

export interface PilgrimageTempleStop {
  order_in_day: number;
  code: string;
  graha: string;
  graha_name_en: string;
  graha_name_ta: string;
  name_en: string;
  name_ta: string;
  presiding_deity_en: string;
  presiding_deity_ta: string;
  place_name_en: string;
  place_name_ta: string;
  district_en: string;
  district_ta: string;
  latitude: number;
  longitude: number;
  visiting_time_window_en: string;
  visiting_time_window_ta: string;
  darshan_timings_en: string;
  darshan_timings_ta: string;
  special_ritual_en: string;
  special_ritual_ta: string;
  remedy_offerings_en: string;
  remedy_offerings_ta: string;
  distance_from_previous_km: number;
  driving_minutes_from_previous: number;
  is_chart_priority: boolean;
  priority_level?: "high" | "essential" | "moderate" | null;
  chart_priority_reason_en?: string | null;
  chart_priority_reason_ta?: string | null;
}

export interface PilgrimageDayPlan {
  day_number: number;
  title_en: string;
  title_ta: string;
  base_camp_en: string;
  base_camp_ta: string;
  recommended_start_time: string;
  total_distance_km: number;
  estimated_travel_time_hours: number;
  temple_stops: PilgrimageTempleStop[];
  practical_tips_en: string[];
  practical_tips_ta: string[];
}

export interface PilgrimageCircuitResponse {
  circuit_id: string;
  title_en: string;
  title_ta: string;
  summary_en: string;
  summary_ta: string;
  base_hub_en: string;
  base_hub_ta: string;
  total_temples: number;
  total_distance_km: number;
  day_plans: PilgrimageDayPlan[];
  chart_priorities_present: boolean;
  rahu_kalam_guidelines_en: string;
  rahu_kalam_guidelines_ta: string;
  dress_code_and_customs_en: string;
  dress_code_and_customs_ta: string;
}

export interface PersonalizedPilgrimageRequest {
  horoscope_id?: string;
  birth_date?: string;
  birth_time?: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
  ayanamsa?: number;
  chart_snapshot?: Record<string, any>;
  circuit_type?: "1_day_express" | "2_day" | string;
}


// ─── Astrological Gemstone (Ratna) Advisory Types ────────────────────────────

export interface GemstoneRecommendation {
  category_code: "life_stone" | "lucky_stone" | "fortune_stone" | string;
  category_name_en: string;
  category_name_ta: string;
  governing_purpose_en: string;
  governing_purpose_ta: string;
  graha: string;
  graha_name_en: string;
  graha_name_ta: string;
  house_lordships: number[];
  primary_gem_en: string;
  primary_gem_ta: string;
  primary_gem_sanskrit: string;
  upratna_substitutes_en: string[];
  upratna_substitutes_ta: string[];
  prescribed_metal_en: string;
  prescribed_metal_ta: string;
  ideal_finger_en: string;
  ideal_finger_ta: string;
  minimum_carats: number;
  energization_day_en: string;
  energization_day_ta: string;
  consecration_mantra_sanskrit: string;
  consecration_mantra_ta: string;
  cleansing_vidhi_en: string;
  cleansing_vidhi_ta: string;
  safety_status: "auspicious" | "caution_required" | "prohibited" | string;
  is_eligible: boolean;
  astrological_justification_en: string;
  astrological_justification_ta: string;
  incompatible_gems_warning_en?: string | null;
  incompatible_gems_warning_ta?: string | null;
}

export interface ProhibitedGemstoneItem {
  graha: string;
  graha_name_en: string;
  graha_name_ta: string;
  primary_gem_en: string;
  primary_gem_ta: string;
  reason_en: string;
  reason_ta: string;
  dusthana_houses_ruled: number[];
  is_functional_malefic: boolean;
  safe_alternative_en: string;
  safe_alternative_ta: string;
}

export interface GemstoneAdvisoryResponse {
  lagna_sign: string;
  moon_sign?: string | null;
  running_mahadasha?: string | null;
  running_bhukti?: string | null;
  life_stone: GemstoneRecommendation;
  lucky_stone: GemstoneRecommendation;
  fortune_stone: GemstoneRecommendation;
  prohibited_gemstones: ProhibitedGemstoneItem[];
  conflicting_combinations_warning_en: string[];
  conflicting_combinations_warning_ta: string[];
  general_wearing_rules_en: string[];
  general_wearing_rules_ta: string[];
  mandatory_review_notice_en: string;
  mandatory_review_notice_ta: string;
}

export interface GemstoneAdvisoryRequest {
  ascendant_sign?: string;
  horoscope_id?: string;
  birth_date?: string;
  birth_time?: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
  ayanamsa?: number;
  chart_snapshot?: Record<string, any>;
}

export interface SthanaBalaSub {
  uchcha_bala: number;
  saptavargaja_bala: number;
  ojhayugma_bala: number;
  kendradi_bala: number;
  drekkana_bala: number;
  total: number;
}

export interface KalaBalaSub {
  nathonnatha_bala: number;
  paksha_bala: number;
  tribhaga_bala: number;
  abda_bala: number;
  masa_bala: number;
  vara_bala: number;
  hora_bala: number;
  ayana_bala: number;
  total: number;
}

export interface PlanetShadbalaDetail {
  planet: string;
  sthana_bala: SthanaBalaSub;
  dig_bala: number;
  kala_bala: KalaBalaSub;
  cheshta_bala: number;
  naisargika_bala: number;
  drik_bala: number;
  total_virupas: number;
  total_rupas: number;
  required_virupas: number;
  ratio: number;
  is_strong: boolean;
  rank: number;
}

export interface ShadbalaResponse {
  metadata?: CalculationMetadata;
  planets: PlanetShadbalaDetail[];
  strongest_planet: string;
  weakest_planet: string;
  calculation_notes?: string[];
}

// ==============================================================================
// Unified KP + Vedic Marriage Prediction Engine Types
// ==============================================================================

export type EventVerdict = "EVENT_INDICATED" | "EVENT_NOT_INDICATED" | "INDETERMINATE";

export type TimingStatus =
  | "WINDOW_FOUND"
  | "NO_WINDOW_IN_RANGE"
  | "TIMING_NOT_DETERMINABLE"
  | "NOT_EVALUATED";

export type PromiseVerdict = "PROMISED" | "DENIED" | "INDETERMINATE";

export type KPInternalModifier =
  | "PROMISED_SMOOTH"
  | "PROMISED_WITH_OBSTACLES"
  | "PROMISED_DELAYED"
  | "DENIED_AT_ROOT"
  | "DENIED_AT_FRUITION"
  | "INDETERMINATE_DATA";

export type VedicInternalModifier =
  | "PROMISED_FAVORABLE"
  | "PROMISED_WITH_OBSTACLES"
  | "DENIED_COMPOUND"
  | "INDETERMINATE_DATA";

export type RuleProvenanceTag =
  | "SOURCE_VERIFIED"
  | "SOURCE_UNVERIFIED"
  | "PROJECT_ENGINEERING_POLICY";

export type ScanStatus =
  | "STABLE"
  | "BOUNDARY_CROSSING_DETECTED"
  | "SCAN_FAILED_OR_INCOMPLETE";

export interface CuspCrossingDetail {
  crossing_time_iso: string;
  delta_seconds: number;
  boundary_longitude_deg: number;
  from_sub_lord: string;
  to_sub_lord: string;
  verdict_impact: string; // 'VERDICT_PRESERVED' | 'VERDICT_FLIPPED'
}

export interface SensitivityToleranceGuarantee {
  mesh_step_seconds: number;
  max_recursion_depth: number;
  time_tolerance_seconds: number;
  longitude_tolerance_deg: number;
  disclaimer: string;
}

export interface BirthTimeSensitivityReport {
  is_sensitive: boolean;
  uncertainty_seconds: number;
  scan_status: ScanStatus;
  nominal_sub_lord: string;
  nominal_cusp_degree: number;
  crossings: CuspCrossingDetail[];
  tolerance_guarantee: SensitivityToleranceGuarantee;
  error_detail?: string | null;
}

export interface KPPromiseDetail {
  verdict: PromiseVerdict;
  internal_modifier: KPInternalModifier;
  cuspal_sub_lord_7: string;
  star_lord_of_csl: string;
  star_lord_significations: number[];
  sub_lord_significations: number[];
  is_csl_retrograde: boolean;
  is_star_lord_retrograde: boolean;
  rule_id: string;
  rule_provenance: RuleProvenanceTag;
  explanation: string;
}

export interface VedicPromiseDetail {
  verdict: PromiseVerdict;
  internal_modifier: VedicInternalModifier;
  seventh_lord_d1: string;
  seventh_house_sign_d1: string;
  seventh_lord_house_d1: number;
  venus_combustion: boolean;
  venus_debilitation: boolean;
  venus_dusthana: boolean;
  kuja_dosha_present: boolean;
  kuja_dosha_cancelled: boolean;
  d9_seventh_sign: string;
  d9_seventh_lord: string;
  d9_venus_sign: string;
  d9_afflicted: boolean;
  compound_denial_gates_met: number;
  rule_id: string;
  rule_provenance: RuleProvenanceTag;
  explanation: string;
}

export interface TimingWindow {
  start_date: string;
  end_date: string;
  mahadasha: string;
  antardasha: string;
  pratyantardasha?: string | null;
  double_transit_active: boolean;
  kp_significator_confluence: boolean;
  confidence_score: number;
}

export interface UnifiedTimingReport {
  best_window?: TimingWindow | null;
  evaluated_windows_count: number;
  search_start_date: string;
  search_end_date: string;
  rule_provenance: RuleProvenanceTag;
}

export interface UnifiedMarriageRequest {
  birth: BirthInput;
  birth_time_uncertainty_seconds?: number;
  start_year?: number | null;
  end_year?: number | null;
}

export interface UnifiedMarriageResponse {
  final_verdict: EventVerdict;
  timing_status: TimingStatus;
  kp_promise: KPPromiseDetail;
  vedic_promise: VedicPromiseDetail;
  birth_time_sensitivity: BirthTimeSensitivityReport;
  timing?: UnifiedTimingReport | null;
  reconciliation_rule_id: string;
  reconciliation_provenance: RuleProvenanceTag;
  metadata: CalculationMetadata;
}

// ---------------------------------------------------------------------------
// Comprehensive Dual-Horoscope Marriage Compatibility Engine (Phases 1-9)
// ---------------------------------------------------------------------------

export interface MarriagePartnerInput {
  name?: string;
  gender?: "male" | "female";
  birth_date?: string;
  birth_time?: string;
  is_birth_time_approximate?: boolean;
  timezone?: string;
  latitude?: number;
  longitude?: number;
  birth_input?: BirthInput;
  saved_horoscope_id?: string;
}

export interface MarriageCompatibilityRequest {
  groom: MarriagePartnerInput;
  bride: MarriagePartnerInput;
  rule_system?: string; // "all", "tamil_porutham", "ashtakoota", "vedic_kp"
  ayanamsa_id?: number; // 0=Lahiri, 1=KP
  house_system_id?: number; // 0=Whole Sign, 2=Placidus
  include_timing?: boolean;
  include_kp?: boolean;
}

export interface PersonProfileSummary {
  name: string;
  gender: string;
  birth_date: string;
  birth_time: string;
  timezone: string;
  latitude: number;
  longitude: number;
  ascendant_sign: string;
  ascendant_sign_tamil: string;
  ascendant_degree: number;
  ascendant_nakshatra: string;
  ascendant_pada: number;
  ascendant_navamsa_sign: string;
  moon_sign: string;
  moon_sign_tamil: string;
  moon_degree: number;
  moon_nakshatra: string;
  moon_nakshatra_tamil: string;
  moon_pada: number;
  moon_navamsa_sign: string;
  venus_sign: string;
  mars_sign: string;
  jupiter_sign: string;
}

export interface PoruthamDetailItem {
  rule_id: string;
  name_en: string;
  name_ta: string;
  status: string;
  grade: string;
  score: number;
  max_score: number;
  is_favorable: boolean;
  groom_input?: Record<string, any>;
  bride_input?: Record<string, any>;
  intermediate_calculation?: Record<string, any>;
  counting_direction?: string;
  applied_acceptance_criteria?: string;
  source_and_version?: string;
  description: string;
  description_tamil: string;
  classical_reference: string;
  warnings: string[];
}

export interface TamilPoruthamSummary {
  poruthams: Record<string, PoruthamDetailItem>;
  total_score: number;
  max_score: number;
  aggregate_verdict: string;
  rajju_status: string;
  vedha_status: string;
  summary_notes: string[];
}

export interface KootaDetailItem {
  koota_id: string;
  name_en: string;
  status: string;
  max_points: number;
  earned_points: number;
  raw_calculation: string;
  groom_input?: Record<string, any>;
  bride_input?: Record<string, any>;
  intermediate_calculation?: Record<string, any>;
  is_dosha_present: boolean;
  is_cancelled: boolean;
  cancellation_reason?: string | null;
  description: string;
  classical_reference: string;
  warnings: string[];
}

export interface AshtakootaSummary {
  kootas: Record<string, KootaDetailItem>;
  total_points: number;
  max_points: number;
  minimum_threshold: number;
  is_threshold_met: boolean;
  nadi_dosha_present: boolean;
  nadi_dosha_cancelled: boolean;
  bhakoot_dosha_present: boolean;
  bhakoot_dosha_cancelled: boolean;
  summary_notes: string[];
}

export interface CategoryVerdictModel {
  category_id: string;
  category_name_en: string;
  category_name_ta: string;
  status: "FAVORABLE" | "MIXED" | "UNFAVORABLE" | "INDETERMINATE";
  tradition: string;
  score_summary: string;
  key_factors: string[];
  vetoes_applied: string[];
}

export interface ConflictFindingModel {
  conflict_type: string;
  title_en: string;
  title_ta: string;
  finding_a: string;
  finding_b: string;
  resolution_principle: string;
  explanation_en: string;
  explanation_ta: string;
  rule_sources: string[];
}

export interface CompositeAssessmentSummary {
  overall_outcome: "FAVOURABLE_UNDER_SELECTED_RULES" | "MIXED_OR_CONDITIONAL" | "UNFAVOURABLE_UNDER_SELECTED_RULES" | "INDETERMINATE";
  overall_outcome_label_en: string;
  overall_outcome_label_ta: string;
  category_verdicts: Record<string, CategoryVerdictModel>;
  major_supportive_indicators: string[];
  major_challenging_indicators: string[];
  conflicting_findings: ConflictFindingModel[];
  missing_or_uncertain_evidence: string[];
  recommended_astrologer_review: string[];
  decision_path: string[];
  disclaimers: string[];
  rule_sources: string[];
  warnings: string[];
  explanation_en: string;
  explanation_ta: string;
}

export interface FinalAssessmentSummary {
  verdict: string;
  verdict_label_en: string;
  verdict_label_ta: string;
  primary_strengths: string[];
  primary_concerns: string[];
  decision_path: string[];
  scientific_disclaimer: string;
  reproducibility_fingerprint: string;
}

export interface MarriageCompatibilityResponse {
  metadata: CalculationMetadata;
  groom_profile: PersonProfileSummary;
  bride_profile: PersonProfileSummary;
  composite_assessment: CompositeAssessmentSummary;
  tamil_porutham?: TamilPoruthamSummary;
  ashtakoota?: AshtakootaSummary;
  dosha_analysis?: Record<string, any>;
  synastry?: Record<string, any>;
  kp_marriage?: Record<string, any>;
  groom_vedic?: Record<string, any>;
  bride_vedic?: Record<string, any>;
  final_assessment: FinalAssessmentSummary;
}

export interface RuleRegisterItem {
  rule_id: string;
  name: string;
  tradition: string;
  classical_source: string;
  approval_status: string;
  description: string;
}

export interface RuleRegisterResponse {
  engine_name: string;
  ruleset_version: string;
  rules: RuleRegisterItem[];
}

// ---------------------------------------------------------------------------
// Medical Astrology Interfaces
// ---------------------------------------------------------------------------

export interface MedicalConditionItem {
  condition: string;
  passed: boolean;
  detail: string;
}

export interface MedicalRule {
  id: string;
  name: string;
  name_tamil: string;
  source: string;
  chapter_verse: string;
  category: string;
  system: "vedic" | "kp";
  required_placements: string;
  mandatory_conditions: string[];
  traditional_interpretation: string;
  interpretation_tamil: string;
  anatomical_system: string;
  modifiers?: string | null;
  conflicting_indications?: string | null;
  is_active: boolean;
  status: "Qualifying" | "Mitigated" | "Not Qualifying";
  triggered_positions: string[];
  planets_involved: string[];
  relevant_houses: number[];
  conditions: MedicalConditionItem[];
}

export interface HouseHealthAnalysis {
  house_number: number;
  sign_index: number;
  sign_name_en: string;
  sign_name_ta: string;
  lord: string;
  lord_house?: number | null;
  lord_sign?: string | null;
  lord_dignity: string;
  occupants: string[];
  aspecting_planets: string[];
  anatomical_system_en: string;
  anatomical_system_ta: string;
  traditional_summary_en: string;
  traditional_summary_ta: string;
  afflictions: string[];
  mitigations: string[];
}

export interface AnatomicalSystemMapping {
  system_name_en: string;
  system_name_ta: string;
  organs_en: string;
  organs_ta: string;
  sign_governance: string;
  planetary_governance: string;
  status: "Balanced" | "Afflicted" | "Mitigated" | "Neutral";
  observations_en: string;
  observations_ta: string;
}

export interface BirthChartPerspective {
  lagna_analysis: HouseHealthAnalysis;
  sixth_house_analysis: HouseHealthAnalysis;
  eighth_house_analysis: HouseHealthAnalysis;
  twelfth_house_analysis: HouseHealthAnalysis;
  triggered_rules: MedicalRule[];
  conflicting_indications: string[];
  anatomical_mappings: AnatomicalSystemMapping[];
}

export interface TransitInfluence {
  planet: string;
  sign_index: number;
  sign_name_en: string;
  sign_name_ta: string;
  degree: number;
  house_from_lagna: number;
  is_retrograde: boolean;
  traditional_symbolism_en: string;
  traditional_symbolism_ta: string;
}

export interface CurrentPeriodPerspective {
  mahadasha: string;
  bhukti?: string | null;
  antara?: string | null;
  start_date_iso?: string | null;
  end_date_iso?: string | null;
  matching_rules: MedicalRule[];
  transits: TransitInfluence[];
  traditional_synthesis_en: string;
  traditional_synthesis_ta: string;
}

export interface HistoricalPeriodItem {
  period_name: string;
  lord: string;
  sub_lord?: string | null;
  start_date_iso: string;
  end_date_iso: string;
  age_range: string;
  traditional_rules: MedicalRule[];
  traditional_notes_en: string;
  traditional_notes_ta: string;
}

export interface HistoricalPeriodPerspective {
  periods: HistoricalPeriodItem[];
}

export interface VedicMedicalAnalysis {
  birth_chart: BirthChartPerspective;
  current_period: CurrentPeriodPerspective;
  historical_periods: HistoricalPeriodPerspective;
}

export interface SignificatorSourceDetail {
  house: number;
  source_type: string;
  planet_channel?: string;
  level_name_en: string;
  level_name_ta: string;
  description_en: string;
  description_ta: string;
}

export interface KpCslAnalysis {
  cusp_number: number;
  cusp_degree?: number;
  sign_name?: string;
  sign_lord?: string;
  cusp_star_lord?: string;
  csl_planet: string;
  csl_star_lord?: string;
  star_lord: string;
  sub_lord?: string;
  signified_houses: number[];
  signification_details?: SignificatorSourceDetail[];
  primary_signification_en: string;
  primary_signification_ta: string;
  anatomical_rulership_en: string;
  anatomical_rulership_ta: string;
  
  recovery_status?: "present" | "not_found" | "data_unavailable";
  disease_status?: "present" | "not_found" | "data_unavailable";
  chronic_status?: "present" | "not_found" | "data_unavailable";
  hospitalization_status?: "present" | "not_found" | "data_unavailable";

  recovery_signified: boolean;
  disease_signified: boolean;
  chronic_signified: boolean;
  hospitalization_signified: boolean;

  recovery_houses?: number[];
  disease_houses?: number[];
  chronic_houses?: number[];
  hospitalization_houses?: number[];

  is_data_available?: boolean;
  missing_data_reason?: string | null;
  calculation_provenance?: string;
}

export interface KpDasaSignification {
  period_level: string;
  lord: string;
  signified_houses: number[];
  indication_en: string;
  indication_ta: string;
}

export interface KpMedicalAnalysis {
  sixth_csl: KpCslAnalysis;
  lagna_csl?: KpCslAnalysis | null;
  eighth_csl?: KpCslAnalysis | null;
  twelfth_csl?: KpCslAnalysis | null;
  current_dasa_significations: KpDasaSignification[];
  kp_rules: MedicalRule[];
  recovery_indicators: string[];
  susceptibility_indicators: string[];
}

export interface MedicalAstrologyResponse {
  metadata?: CalculationMetadata;
  rule_set_version: string;
  disclaimer_en: string;
  disclaimer_ta: string;
  vedic_analysis: VedicMedicalAnalysis;
  kp_analysis?: KpMedicalAnalysis | null;
}

// ---------------------------------------------------------------------------
// Saved Marriage Compatibility Reports (Phase 11C/11D)
// ---------------------------------------------------------------------------

export interface SaveMarriageCompatibilityReportRequest {
  title: string;
  groom_name: string;
  bride_name: string;
  groom_birth_date: string;
  bride_birth_date: string;
  groom_is_approximate?: boolean;
  bride_is_approximate?: boolean;
  groom_saved_horoscope_id?: string | null;
  bride_saved_horoscope_id?: string | null;
  rule_system?: string;
  ayanamsa_id?: number;
  house_system_id?: number;
  include_kp?: boolean;
  include_timing?: boolean;
  overall_outcome: "FAVOURABLE_UNDER_SELECTED_RULES" | "MIXED_OR_CONDITIONAL" | "UNFAVOURABLE_UNDER_SELECTED_RULES" | "INDETERMINATE";
  porutham_score?: number | null;
  ashtakoota_points?: number | null;
  samadosham_status?: string | null;
  papasamya_verdict?: string | null;
  ruling_planets_agreement?: string | null;
  report_data: Record<string, any>;
  engine_version?: string;
  report_schema_version?: string;
}

export interface UpdateMarriageReportMetadataRequest {
  title?: string;
  groom_name?: string;
  bride_name?: string;
  groom_saved_horoscope_id?: string | null;
  bride_saved_horoscope_id?: string | null;
}

export interface SavedMarriageReportSummary {
  id: string;
  user_id: string;
  display_number: number;
  title: string;
  groom_name: string;
  bride_name: string;
  groom_birth_date: string;
  bride_birth_date: string;
  groom_is_approximate: boolean;
  bride_is_approximate: boolean;
  groom_saved_horoscope_id?: string | null;
  bride_saved_horoscope_id?: string | null;
  rule_system: string;
  ayanamsa_id: number;
  house_system_id: number;
  include_kp: boolean;
  include_timing: boolean;
  overall_outcome: "FAVOURABLE_UNDER_SELECTED_RULES" | "MIXED_OR_CONDITIONAL" | "UNFAVOURABLE_UNDER_SELECTED_RULES" | "INDETERMINATE";
  porutham_score?: number | null;
  ashtakoota_points?: number | null;
  samadosham_status?: string | null;
  papasamya_verdict?: string | null;
  ruling_planets_agreement?: string | null;
  engine_version: string;
  report_schema_version: string;
  created_at: string;
  updated_at: string;
}

export interface SavedMarriageReportDetail extends SavedMarriageReportSummary {
  report_data: MarriageCompatibilityResponse | Record<string, any>;
}

export interface SavedMarriageReportsListResponse {
  reports: SavedMarriageReportSummary[];
  total_count: number;
  limit: number;
  offset: number;
}




// ==========================================
// Traditional Tamil Horoscope Writing Module
// ==========================================

export interface HoroscopeWritingRequest {
  birth_input?: BirthInput;
  saved_horoscope_id?: string | null;
  person_name?: string;
  gender?: string;
  panchanga_system?: string;
  ayanamsa_id?: number;
  house_system_id?: number;
  entrance_direction_basis?: "rasi" | "lagna" | "manual";
  overrides?: Record<string, any>;
}

export interface HoroscopeWritingResponse {
  metadata: Record<string, any>;
  person_details: {
    name: string;
    gender: string;
    birth_date: string;
    birth_time: string;
    birth_place: string;
    latitude: number;
    longitude: number;
    timezone: string;
  };
  page1_birth_details: {
    tamil_year: string;
    tamil_month: string;
    tamil_date: number;
    tamil_year_month_date: string;
    weekday: string;
    ayanam: string;
    ritu: string;
    paksha: string;
    tithi: string;
    prev_nakshatra: string;
    birth_nakshatra: string;
    next_nakshatra: string;
    nama_yoga: string;
    karana: string;
    tyajyam: string;
    ahas: string;
    birth_time: string;
    udayadhi_nazhigai: string;
    udayadhi_hours: string;
    sunrise: string;
    sunset: string;
    udaya_lagna: string;
    vara_yoga: string;
  };
  page2_dinasuthi: {
    saka_year: string;
    kali_year: string;
    hijri_year: string;
    kollam_year: string;
    english_year: number;
    english_date: string;
    tamil_month_date: string;
    panchangam: string;
    calculation_method: string;
  };
  page3_udumaka_dasa: {
    param_nazhigai: string;
    pada_duration: string;
    birth_pada: number;
    pada_sentrathu: string;
    pada_nindrathu: string;
    dasa_lord: string;
    dasa_full_years: string;
    dasa_sentrathu: string;
    dasa_iruppu: string;
    dasa_sequence: Array<{
      order: number;
      lord_en: string;
      lord_ta: string;
      total_years: number;
      balance_str: string;
      start_date: string;
      end_date: string;
      duration_years: number;
    }>;
  };
  page4_kurippu: {
    udayadhi_mani: string;
    lagna_iruppu: string;
    ahas: string;
    kalam_ontrukku: string;
    kalam: string;
    lagna: string;
    rasi: string;
    nakshatra: string;
    pada: number;
    mrigam: string;
    pakshi: string;
    maram: string;
    gana: string;
    rajju: string;
    nadi: string;
  };
  page5_padupakshi: {
    birth_nakshatra: string;
    uyir_pakshi: string;
    paksha: string;
    valarpirai_guidance: string;
    theypirai_guidance: string;
    dominant_state: string;
    detailed_guidance: string;
    five_birds_list: string[];
  };
  page6_archana_slip: {
    rasi: string;
    nakshatra: string;
    lagna: string;
    birth_date: string;
    tamil_date: string;
    entrance_direction: string;
    lucky_day: string;
    lucky_color: string;
    lucky_gem: string;
    worship_deity: string;
    calculated_entrance_direction: string;
    calculated_lucky_day: string;
    calculated_lucky_color: string;
    calculated_lucky_gem: string;
    calculated_worship_deity: string;
    entrance_direction_basis: string;
  };
  overrides?: Record<string, any>;
}

export interface HoroscopeWritingSaveResponse {
  success: boolean;
  id: string;
  persistence_target: string;
  message: string;
  created_at: string;
}

export interface SavedHoroscopeWritingItem {
  id: string;
  user_id: string;
  horoscope_id?: string | null;
  person_name: string;
  birth_date: string;
  birth_time: string;
  birth_place?: string | null;
  latitude: number;
  longitude: number;
  timezone: string;
  panchanga_system: string;
  calculated_data: HoroscopeWritingResponse;
  overrides?: Record<string, any>;
  created_at: string;
  updated_at: string;
  persistence_target?: string;
}

export interface SavedHoroscopeWritingListResponse {
  success: boolean;
  count: number;
  items: SavedHoroscopeWritingItem[];
}

export interface HoroscopeWritingUpdateRequest {
  person_name?: string;
  birth_place?: string;
  panchanga_system?: string;
  calculated_data?: HoroscopeWritingResponse;
  overrides?: Record<string, any>;
}

// ============================================================================
// Prediction Rules Engine Types
// ============================================================================

export interface PredictionSubcategory {
  slug: string;
  name_en: string;
  name_ta: string;
  description_en: string;
  description_ta: string;
}

export interface PredictionCategoryGroup {
  group_code: string;
  group_name_en: string;
  group_name_ta: string;
  display_order: number;
  subcategories: PredictionSubcategory[];
}

export interface EvaluatedPredictionRule {
  rule_id: string;
  version: number;
  name: string;
  name_en: string;
  name_ta?: string;
  category_slug: string;
  subcategory?: string;
  astrology_system: string;
  chart_scope: string;
  calculation_mode: string;
  severity: "info" | "favorable" | "unfavorable" | "neutral" | "mixed";
  status: "matched" | "not_matched" | "unevaluable";
  matched: boolean;
  unevaluable?: boolean;
  unevaluable_reason?: string;
  interpretation: string;
  interpretation_en: string;
  interpretation_ta?: string;
  astrological_principle: string;
  astrological_principle_en: string;
  astrological_principle_ta?: string;
  chart_evidence: string[];
  match_reasons: string[];
  source_reference?: string;
  limitations?: string;
  limitations_en?: string;
  limitations_ta?: string;
}

export interface EvaluatePredictionRulesRequest {
  horoscope?: HoroscopeResponse;
  saved_horoscope_id?: string;
  category_slug?: string;
  subcategory?: string;
  chart_scope?: string;
  astrology_system?: string;
  language?: string;
  dasa?: Record<string, any>;
  kp?: Record<string, any>;
}

export interface EvaluatePredictionRulesResponse {
  total_rules_evaluated: number;
  total_matched: number;
  total_unevaluable: number;
  category_slug?: string;
  subcategory?: string;
  language: string;
  results: EvaluatedPredictionRule[];
}

