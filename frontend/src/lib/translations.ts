/**
 * Gokul's Astrological Insights - Centralized Localization Dictionary
 * English and Tamil strings for Vedic & KP Astrology terms, UI elements, errors, and metadata.
 */

export type LanguageCode = "en" | "ta";

export interface TranslationDictionary {
  // Navigation & Brand
  brandName: string;
  brandTagline: string;
  navHome: string;
  navHoroscope: string;
  navMuhurta?: string;
  navMethodology: string;
  navLanguage: string;
  statusOnline: string;
  statusDegraded: string;
  statusOffline: string;

  // Common UI
  loading: string;
  calculate: string;
  calculating: string;
  reset: string;
  back: string;
  viewResults: string;
  error: string;
  retry: string;
  optional: string;
  required: string;
  notAvailableYet: string;
  details: string;

  // Home Page
  heroTitle: string;
  heroSubtitle: string;
  heroCta: string;
  heroSecondaryCta: string;
  featureTitle: string;
  featureSubtitle: string;
  featEphemerisTitle: string;
  featEphemerisDesc: string;
  featVedicTitle: string;
  featVedicDesc: string;
  featKpTitle: string;
  featKpDesc: string;
  featDasaTitle: string;
  featDasaDesc: string;
  limitationNoticeTitle: string;
  limitationNoticeText: string;

  // Form
  formTitle: string;
  formSubtitle: string;
  sectionPersonal: string;
  fieldName: string;
  fieldNamePlaceholder: string;
  fieldDate: string;
  fieldTime: string;
  fieldTimeConfirmed: string;
  fieldTimeUnknownNotice: string;
  sectionLocation: string;
  fieldPlace: string;
  fieldPlacePlaceholder: string;
  fieldLatitude: string;
  fieldLongitude: string;
  fieldTimezone: string;
  fieldTimezonePlaceholder: string;
  sectionCalculations: string;
  fieldAyanamsa: string;
  fieldHouseSystem: string;
  fieldIncludePanchang: string;
  fieldIncludeOuterPlanets: string;
  submitButton: string;

  // Validation Errors
  valDateRequired: string;
  valTimeRequired: string;
  valPlaceRequired: string;
  valLatInvalid: string;
  valLonInvalid: string;
  valTzRequired: string;

  // Results Interface
  resultsTitle: string;
  resultsSubtitle: string;
  tabChart: string;
  tabPlanets: string;
  tabHouses: string;
  tabDasa: string;
  tabKp: string;
  tabPanchang: string;
  tabNabhasha: string;
  tabAshtakavarga: string;
  tabVedicYogas: string;
  tabMedicalAstrology: string;
  tabDoshas: string;
  tabDestinyCard: string;
  destinyCardTitle: string;
  destinyCardSubtitle: string;
  destinyCardDownload: string;
  destinyCardGenerating: string;
  destinyCardLagna: string;
  destinyCardRasi: string;
  destinyCardNakshatra: string;
  destinyCardPada: string;
  destinyCardDasa: string;
  destinyCardBirthDasa: string;
  destinyCardSunSign: string;
  destinyCardLord: string;
  destinyCardAyanamsa: string;
  destinyCardVerification: string;
  destinyCardPrivacyNotice: string;
  destinyCardShowDate: string;
  destinyCardMissingData: string;
  destinyCardSwitchLang: string;
  vedicYogasTitle: string;
  vedicYogasSubtitle: string;
  vedicYogasTotalQualifying: string;
  vedicYogasRajaYogas: string;
  vedicYogasDhanaYogas: string;
  vedicYogasMahapurusha: string;
  vedicYogasVipareeta: string;
  vedicYogasOtherClassical: string;
  vedicYogasFilterAll: string;
  vedicYogasFilterQualifying: string;
  vedicYogasFilterNonQualifying: string;
  vedicYogasSearchPlaceholder: string;
  vedicYogasColSNo: string;
  vedicYogasColName: string;
  vedicYogasColCategory: string;
  vedicYogasColStatus: string;
  vedicYogasColPlanets: string;
  vedicYogasColHouses: string;
  vedicYogasColConditions: string;
  vedicYogasColAction: string;
  vedicYogasModalTitle: string;
  vedicYogasModalDefinition: string;
  vedicYogasModalConditionsEval: string;
  vedicYogasModalInterpretation: string;
  vedicYogasModalReference: string;
  vedicYogasModalVerification: string;
  vedicYogasModalCancellation: string;
  doshasTitle: string;
  doshasSubtitle: string;
  doshasTotalEvaluated: string;
  doshasPresent: string;
  doshasMitigated: string;
  doshasAbsent: string;
  doshasIndeterminate: string;
  doshasFilterAll: string;
  doshasFilterPresent: string;
  doshasFilterMitigated: string;
  doshasFilterAbsent: string;
  doshasFilterIndeterminate: string;
  doshasSearchPlaceholder: string;
  doshasColSNo: string;
  doshasColName: string;
  doshasColCategory: string;
  doshasColStatus: string;
  doshasColPlanets: string;
  doshasColReference: string;
  doshasColConditions: string;
  doshasColAction: string;
  doshasModalTitle: string;
  doshasModalFormation: string;
  doshasModalCancellation: string;
  doshasModalInterpretation: string;
  doshasModalRemedies: string;
  doshasModalReference: string;
  doshasModalMissingPrereq: string;
  doshasMissingNotice: string;
  doshasCalculateButton: string;
  doshasCalculating: string;
  nabhashaTitle: string;
  nabhashaSubtitle: string;
  nabhashaPrimaryYoga: string;
  nabhashaCategory: string;
  nabhashaFormationRule: string;
  nabhashaDescription: string;
  nabhashaPlanetsInvolved: string;
  nabhashaQualifyingHouses: string;
  nabhashaQualifyingSigns: string;
  nabhashaDistribution: string;
  nabhashaDistinctSigns: string;
  nabhashaDistinctHouses: string;
  nabhashaKendraPlanets: string;
  nabhashaPanapharaPlanets: string;
  nabhashaApoklimaPlanets: string;
  nabhashaTrikonaPlanets: string;
  nabhashaAllQualifying: string;
  nabhashaPrecedenceNotice: string;
  ashtakavargaTitle: string;
  ashtakavargaSubtitle: string;
  ashtakavargaSavTab: string;
  ashtakavargaBavTab: string;
  ashtakavargaMatrixTab: string;
  ashtakavargaRawBindus: string;
  ashtakavargaTrikona: string;
  ashtakavargaEkadhipatya: string;
  ashtakavargaShodhyaPinda: string;
  ashtakavargaRashiPinda: string;
  ashtakavargaGrahaPinda: string;
  ashtakavargaTotalBindus: string;
  ashtakavargaAuspiciousSigns: string;
  ashtakavargaInauspiciousSigns: string;
  ashtakavargaInvariantValidated: string;
  chartSouthIndian: string;
  chartNorthIndian: string;
  chartSwitchMode: string;
  birthSummaryTitle: string;
  calculatedWith: string;
  recalculateCta: string;

  // Astrological Data Labels
  planet: string;
  longitude: string;
  sign: string;
  degreeInSign: string;
  nakshatra: string;
  pada: string;
  lord: string;
  speed: string;
  retrograde: string;
  direct: string;
  ascendant: string;
  midheaven: string;
  house: string;
  cuspDegree: string;
  starLord: string;
  subLord: string;
  subSubLord: string;
  kpNumber: string;
  promise: string;
  significators: string;

  // Dasa
  dasaBalanceAtBirth: string;
  dasaActiveNow: string;
  dasaMahadasha: string;
  dasaAntardasha: string;
  dasaPratyantar: string;
  dasaPratyantardasha: string;
  dasaSookshmadasha: string;
  dasaPranadasha: string;
  dasaStartDate: string;
  dasaEndDate: string;
  dasaAgeAtStart: string;
  dasaAgeAtEnd: string;
  dasaDuration: string;
  dasaActivePeriod: string;
  dasaSelectedDate: string;
  dasaExpand: string;
  dasaCollapse: string;
  dasaExpandAll: string;
  dasaCollapseAll: string;
  dasaExpandActivePath: string;
  dasaLoading: string;
  dasaNoPeriodsAvailable: string;
  dasaAgeUnavailable: string;
  dasaPeriodOutsideRange: string;
  dasaBenefitBhavas: string;
  dasaStarLord: string;

  // Panchang
  panchangTithi: string;
  panchangPaksha: string;
  panchangNakshatra: string;
  panchangYoga: string;
  panchangKarana: string;
  panchangVara: string;

  // Disclaimer / Footer
  footerDisclaimer: string;
  footerEngineInfo: string;
  footerCopyright: string;

  // Authentication & Account
  navLogin: string;
  navRegister: string;
  navDashboard: string;
  navAdmin: string;
  navLogout: string;

  loginTitle: string;
  loginSubtitle: string;
  fieldUsernameOrEmail: string;
  fieldUsernameOrEmailPlaceholder: string;
  fieldPassword: string;
  fieldPasswordPlaceholder: string;
  showPassword: string;
  hidePassword: string;
  signInButton: string;
  signingIn: string;
  invalidCredentials: string;
  connectionError: string;
  forgotPasswordLink: string;
  dontHaveAccount: string;
  registerLink: string;
  alreadyHaveAccount: string;

  registerTitle: string;
  registerSubtitle: string;
  fieldUsername: string;
  fieldUsernamePlaceholder: string;
  fieldEmail: string;
  fieldEmailPlaceholder: string;
  fieldConfirmPassword: string;
  fieldConfirmPasswordPlaceholder: string;
  signUpButton: string;
  signingUp: string;
  registrationSuccess: string;
  passwordMismatch: string;
  usernameRequirements: string;
  passwordRequirements: string;

  forgotPasswordTitle: string;
  forgotPasswordSubtitle: string;
  sendResetLink: string;
  sendingResetLink: string;
  resetLinkSent: string;
  backToLogin: string;

  updatePasswordTitle: string;
  updatePasswordSubtitle: string;
  firstLoginNotice: string;
  fieldNewPassword: string;
  updatePasswordButton: string;
  updatingPassword: string;
  passwordUpdatedSuccess: string;

  userDashboardTitle: string;
  userDashboardSubtitle: string;
  adminDashboardTitle: string;
  adminDashboardSubtitle: string;
  roleBadgeUser: string;
  roleBadgeAdmin: string;
  savedHoroscopesTitle: string;
  savedHoroscopesPlaceholder: string;
  memberSince: string;

  // Saved Horoscopes UI (Task 3)
  myHoroscopes: string;
  createNewHoroscope: string;
  serialNumberLabel: string;
  birthDateLabel: string;
  birthTimeLabel: string;
  birthPlaceLabel: string;
  actionEdit: string;
  actionOpenHoroscope: string;
  searchHoroscopesPlaceholder: string;
  noSavedHoroscopes: string;
  noSavedHoroscopesDesc: string;
  noSearchResults: string;
  clearSearch: string;
  editHoroscopeTitle: string;
  editHoroscopeSubtitle: string;
  saveChangesButton: string;
  savingChanges: string;
  recalculateAsNewButton: string;
  recalculatingAsNew: string;
  editedWithoutRecalcBadge: string;
  editedWithoutRecalcNotice: string;
  openHoroscopeStoredNotice: string;
  backToSavedHoroscopes: string;
  unnamedHoroscope: string;
  locationUnavailable: string;
  autoSaveSuccess: string;
  autoSaveFailed: string;
  retrySave: string;
  savingToDatabase: string;
  pageIndicator: string;
  prevPage: string;
  nextPage: string;
  totalHoroscopes: string;
  deleteHoroscope: string;
  confirmDeleteHoroscope: string;

  // Numerology Module Keys
  navNumerology: string;
  numerologyTitle: string;
  numerologySubtitle: string;
  cardTraditionalTitle: string;
  cardTraditionalDesc: string;
  cardTraditionalCta: string;
  cardDestinyTitle: string;
  cardDestinyDesc: string;
  cardDestinyCta: string;
  cardAdvancedTitle: string;
  cardAdvancedDesc: string;
  cardAdvancedCta: string;
  savedNumerologyTitle: string;
  savedNumerologySubtitle: string;
  savedNumerologyEmpty: string;
  saveReportSuccess: string;
  reopenReport: string;
  printReport: string;
  exportPdf: string;
  conventionPythagorean: string;
  conventionChaldean: string;

  // Astrology Tools & Navigation Redesign
  navTools: string;
  toolsTitle: string;
  toolsSubtitle: string;
  sectionHoroscopeTitle: string;
  sectionHoroscopeTitleTa: string;
  sectionHoroscopeDesc: string;
  sectionHoroscopeCta: string;
  sectionNumerologyTitle: string;
  sectionNumerologyTitleTa: string;
  sectionNumerologyDesc: string;
  sectionNumerologyCta: string;
  helpGuide: string;
  searchPlaceholder: string;
  welcomeBack: string;
  homeQuickAccess: string;
  homeRecentCharts: string;
  exploreCategories: string;
}

export const translations: Record<LanguageCode, TranslationDictionary> = {
  en: {
    brandName: "Gokul's Astrological Insights",
    brandTagline: "Deterministic Vedic & KP Astronomical System",
    navHome: "Home",
    navHoroscope: "Generate Horoscope",
    navMuhurta: "Muhurta",
    navMethodology: "Methodology",
    navLanguage: "Language",
    statusOnline: "Engine Online",
    statusDegraded: "Engine Degraded",
    statusOffline: "Engine Offline",

    loading: "Computing calculations...",
    calculate: "Generate Vedic Horoscope",
    calculating: "Processing Astronomical Ephemeris...",
    reset: "Clear Form",
    back: "Back",
    viewResults: "View Calculations",
    error: "Calculation Error",
    retry: "Try Again",
    optional: "Optional",
    required: "Required",
    notAvailableYet: "Data not available yet from calculation engine",
    details: "Details",

    heroTitle: "Precision Vedic & KP Astrology Powered by Astronomical Ephemeris",
    heroSubtitle:
      "Deterministic, mathematically rigorous calculations powered by the XALEN astronomical engine. Pure algorithmic astrology rooted in classical Vedic and Krishnamurti Paddhati principles, completely free of AI-generated claims.",
    heroCta: "Generate Vedic Horoscope",
    heroSecondaryCta: "Explore System Engine",
    featureTitle: "Classical Astrological Calculations",
    featureSubtitle:
      "All positions computed in sidereal coordinates using JPL-standard planetary models with millisecond angular accuracy.",
    featEphemerisTitle: "XALEN Astronomical Engine",
    featEphemerisDesc:
      "Pure Rust core ephemeris calculating accurate geocentric sidereal planetary coordinates, ayanamsa corrections, and true lunar nodes.",
    featVedicTitle: "Classical Parashari System",
    featVedicDesc:
      "Rasi, Navamsa, 12 Bhavas, 27 Nakshatras with pada divisions, Graha speeds, and retrograde tracking across traditional houses.",
    featKpTitle: "KP Krishnamurti Paddhati",
    featKpDesc:
      "Exact 249 sub-division table, planetary sign-star-sub-sub lords, Placidus cuspal divisions, and 4-tier house significators.",
    featDasaTitle: "Vimshottari Dasa Hierarchy",
    featDasaDesc:
      "Precise balance of birth Dasa and recursive Mahadasha through Pranadasha using the classical 365.25-day Julian year canon.",
    limitationNoticeTitle: "Deterministic Astrological Methodology Notice",
    limitationNoticeText:
      "All outputs generated by Gokul's Astrological Insights are rule-based astronomical and traditional astrological calculations. They are deterministic mathematical interpretations intended for study and personal reflection, not empirical scientific forecasts or guarantees.",

    formTitle: "Enter Birth Details",
    formSubtitle:
      "Provide precise birth time and location coordinates for accurate Ascendant, house cusps, and KP sub-lord calculations.",
    sectionPersonal: "1. Identity & Birth Time",
    fieldName: "Full Name",
    fieldNamePlaceholder: "e.g., Sundar Raman",
    fieldDate: "Birth Date",
    fieldTime: "Birth Time (24-Hour)",
    fieldTimeConfirmed: "Birth time is confirmed & accurate",
    fieldTimeUnknownNotice:
      "Note: When birth time is approximate or unknown, 12:00 PM is used to calculate planetary signs and Moon nakshatra. Ascendant (Lagna), house cusps, and KP sub-lords require confirmed birth time.",
    sectionLocation: "2. Birth Place & Coordinates",
    fieldPlace: "City or Birthplace",
    fieldPlacePlaceholder: "Search city (e.g. Chennai, Madurai, London, New York...)",
    fieldLatitude: "Latitude (Decimal)",
    fieldLongitude: "Longitude (Decimal)",
    fieldTimezone: "Time Zone (IANA)",
    fieldTimezonePlaceholder: "Select or search IANA time zone",
    sectionCalculations: "3. Astronomical Configuration",
    fieldAyanamsa: "Ayanamsa System",
    fieldHouseSystem: "House System (Bhava Madhya)",
    fieldIncludePanchang: "Calculate Birth Panchang (5 Limbs)",
    fieldIncludeOuterPlanets: "Include Outer Planets (Uranus, Neptune, Pluto)",
    submitButton: "Calculate Complete Horoscope",

    valDateRequired: "Please enter a valid birth date (YYYY-MM-DD).",
    valTimeRequired: "Please enter a valid birth time (HH:MM or HH:MM:SS).",
    valPlaceRequired: "Please enter or select a birth location.",
    valLatInvalid: "Latitude must be between -90.0 and +90.0 degrees.",
    valLonInvalid: "Longitude must be between -180.0 and +180.0 degrees.",
    valTzRequired: "Please select a valid time zone.",

    resultsTitle: "Horoscope & Astrological Analysis",
    resultsSubtitle:
      "Calculated sidereal planetary coordinates, bhava cusps, Vimshottari dasa, and KP sub-lord placements.",
    tabChart: "Birth Chart",
    tabPlanets: "Planetary Positions",
    tabHouses: "Bhavas (Houses)",
    tabDasa: "Vimshottari Dasa",
    tabKp: "KP System",
    tabPanchang: "Panchang",
    tabNabhasha: "Nabhasha Yogas",
    tabAshtakavarga: "Ashtakavarga",
    tabVedicYogas: "Vedic Yogas",
    tabMedicalAstrology: "Medical Astrology",
    tabDoshas: "Doshas",
    tabDestinyCard: "Destiny Card",
    destinyCardTitle: "Vedic Destiny Card",
    destinyCardSubtitle:
      "Authoritative birth identity summary card backed by XALEN ephemeris calculation.",
    destinyCardDownload: "Download High-Res PNG",
    destinyCardGenerating: "Generating Image...",
    destinyCardLagna: "Ascendant (Lagna)",
    destinyCardRasi: "Moon Sign (Rasi)",
    destinyCardNakshatra: "Birth Star (Nakshatra)",
    destinyCardPada: "Pada / Quarter",
    destinyCardDasa: "Current Mahadasha",
    destinyCardBirthDasa: "Birth Mahadasha",
    destinyCardSunSign: "Sun Sign (Surya)",
    destinyCardLord: "Star Lord",
    destinyCardAyanamsa: "Ayanamsa",
    destinyCardVerification: "Verified XALEN Calculation",
    destinyCardPrivacyNotice:
      "Exact coordinates and sensitive details are excluded to protect your privacy.",
    destinyCardShowDate: "Include Birth Date",
    destinyCardMissingData:
      "Authoritative calculation data is required to generate the Destiny Card.",
    destinyCardSwitchLang: "Card Language",
    vedicYogasTitle: "Vedic Yoga Calculator",
    vedicYogasSubtitle: "Classical Vedic astrological combinations evaluated on authoritative planetary longitudes, dignities, and house lordships.",
    vedicYogasTotalQualifying: "Qualifying Yogas",
    vedicYogasRajaYogas: "Raja Yogas",
    vedicYogasDhanaYogas: "Dhana Yogas",
    vedicYogasMahapurusha: "Mahapurusha Yogas",
    vedicYogasVipareeta: "Vipareeta Raja",
    vedicYogasOtherClassical: "Other Classical",
    vedicYogasFilterAll: "All Yogas",
    vedicYogasFilterQualifying: "Qualifying Only",
    vedicYogasFilterNonQualifying: "Non-Qualifying & Cancelled",
    vedicYogasSearchPlaceholder: "Search yoga by name or category...",
    vedicYogasColSNo: "#",
    vedicYogasColName: "Yoga Name",
    vedicYogasColCategory: "Category",
    vedicYogasColStatus: "Status",
    vedicYogasColPlanets: "Planets Involved",
    vedicYogasColHouses: "Houses",
    vedicYogasColConditions: "Formation Summary",
    vedicYogasColAction: "Details",
    vedicYogasModalTitle: "Yoga Analytical Inspector",
    vedicYogasModalDefinition: "Classical Definition",
    vedicYogasModalConditionsEval: "Conditions Evaluated",
    vedicYogasModalInterpretation: "Traditional Interpretation",
    vedicYogasModalReference: "Textual Authority",
    vedicYogasModalVerification: "Rule Verification Status",
    vedicYogasModalCancellation: "Cancellation Analysis (Bhanga)",
    doshasTitle: "Vedic Dosha Analysis",
    doshasSubtitle: "Rule-based evaluation of classical afflictions, conjunction doshas, and mitigations based on authoritative planetary positions.",
    doshasTotalEvaluated: "Total Rules Evaluated",
    doshasPresent: "Active Doshas",
    doshasMitigated: "Mitigated / Cancelled",
    doshasAbsent: "Absent / Non-Afflicted",
    doshasIndeterminate: "Indeterminate / Requires Data",
    doshasFilterAll: "All Doshas",
    doshasFilterPresent: "Active Only",
    doshasFilterMitigated: "Mitigated Only",
    doshasFilterAbsent: "Absent Only",
    doshasFilterIndeterminate: "Indeterminate Only",
    doshasSearchPlaceholder: "Search dosha by name, planet, or category...",
    doshasColSNo: "#",
    doshasColName: "Dosha Name",
    doshasColCategory: "Category",
    doshasColStatus: "Status",
    doshasColPlanets: "Planets & Degrees",
    doshasColReference: "Reference Basis",
    doshasColConditions: "Formation Summary",
    doshasColAction: "Details",
    doshasModalTitle: "Vedic Dosha Analytical Inspector",
    doshasModalFormation: "Formation Conditions Evaluated",
    doshasModalCancellation: "Cancellation & Mitigation Analysis",
    doshasModalInterpretation: "Traditional Interpretation",
    doshasModalRemedies: "Verified Classical Remedies",
    doshasModalReference: "Textual Authority & Rule-set",
    doshasModalMissingPrereq: "Missing Prerequisite Notice",
    doshasMissingNotice: "Dosha analysis has not yet been computed for this chart.",
    doshasCalculateButton: "Calculate Vedic Doshas",
    doshasCalculating: "Evaluating 30 Classical Dosha Rules...",
    nabhashaTitle: "Classical Nabhasha Yogas",
    nabhashaSubtitle: "Celestial pattern yogas formed by the spatial distribution of the 7 classical planets (BPHS Ch. 35).",
    nabhashaPrimaryYoga: "Primary Operative Yoga",
    nabhashaCategory: "Classification",
    nabhashaFormationRule: "Classical Formation Rule",
    nabhashaDescription: "Traditional Interpretation",
    nabhashaPlanetsInvolved: "Participating Grahas",
    nabhashaQualifyingHouses: "Qualifying Houses",
    nabhashaQualifyingSigns: "Qualifying Signs",
    nabhashaDistribution: "Planetary Distribution Across Bhavas",
    nabhashaDistinctSigns: "Occupied Signs",
    nabhashaDistinctHouses: "Occupied Houses",
    nabhashaKendraPlanets: "Kendra Grahas (1, 4, 7, 10)",
    nabhashaPanapharaPlanets: "Panaphara Grahas (2, 5, 8, 11)",
    nabhashaApoklimaPlanets: "Apoklima Grahas (3, 6, 9, 12)",
    nabhashaTrikonaPlanets: "Trikona Grahas (1, 5, 9)",
    nabhashaAllQualifying: "All Qualifying Formations",
    nabhashaPrecedenceNotice: "Evaluated under classical Parashari precedence: Ashraya -> Dala -> Aakriti -> Sankhya.",
    ashtakavargaTitle: "Classical Ashtakavarga System",
    ashtakavargaSubtitle: "Comprehensive 8-fold benefic point matrix, Shodhana reductions, and Shodhya Pinda calculations (BPHS Ch. 66–73).",
    ashtakavargaSavTab: "Sarvashtakavarga (SAV)",
    ashtakavargaBavTab: "Bhinnashtakavarga (BAV)",
    ashtakavargaMatrixTab: "7-Planet BAV Grid",
    ashtakavargaRawBindus: "Raw Bindus",
    ashtakavargaTrikona: "Trikona Shodhana",
    ashtakavargaEkadhipatya: "Ekadhipatya Shodhana",
    ashtakavargaShodhyaPinda: "Shodhya Pinda",
    ashtakavargaRashiPinda: "Rashi Pinda",
    ashtakavargaGrahaPinda: "Graha Pinda",
    ashtakavargaTotalBindus: "Total Bindus",
    ashtakavargaAuspiciousSigns: "Auspicious Signs (≥ 28 Bindus)",
    ashtakavargaInauspiciousSigns: "Deficient Signs (< 28 Bindus)",
    ashtakavargaInvariantValidated: "Canonical 337 SAV Invariant Validated",
    chartSouthIndian: "South Indian (Square)",
    chartNorthIndian: "North Indian (Diamond)",
    chartSwitchMode: "Chart Tradition",
    birthSummaryTitle: "Subject & Ephemeris Summary",
    calculatedWith: "Computed with",
    recalculateCta: "Calculate Another Chart",

    planet: "Graha (Planet)",
    longitude: "Longitude",
    sign: "Rasi (Zodiac)",
    degreeInSign: "Degree",
    nakshatra: "Nakshatra",
    pada: "Pada",
    lord: "Lord",
    speed: "Motion (°/day)",
    retrograde: "Retrograde",
    direct: "Direct",
    ascendant: "Ascendant (Lagna)",
    midheaven: "Midheaven (MC)",
    house: "House (Bhava)",
    cuspDegree: "Cusp Degree",
    starLord: "Star Lord",
    subLord: "Sub Lord",
    subSubLord: "Sub-Sub Lord",
    kpNumber: "KP #",
    promise: "Promise",
    significators: "Significator Strengths",

    dasaBalanceAtBirth: "Dasa Balance at Birth",
    dasaActiveNow: "Active Dasa-Bhukti Currently",
    dasaMahadasha: "Mahadasha",
    dasaAntardasha: "Antardasha (Bhukti)",
    dasaPratyantar: "Pratyantar Dasa",
    dasaPratyantardasha: "Pratyantardasha (Antaram)",
    dasaSookshmadasha: "Sookshmadasha (Sookshma)",
    dasaPranadasha: "Pranadasha (Prana)",
    dasaStartDate: "Start Date",
    dasaEndDate: "End Date",
    dasaAgeAtStart: "Age at Start",
    dasaAgeAtEnd: "Age at End",
    dasaDuration: "Duration",
    dasaActivePeriod: "Active Period",
    dasaSelectedDate: "Selected Date",
    dasaExpand: "Expand",
    dasaCollapse: "Collapse",
    dasaExpandAll: "Expand All",
    dasaCollapseAll: "Collapse All",
    dasaExpandActivePath: "Expand Active Path",
    dasaLoading: "Loading Dasa hierarchy...",
    dasaNoPeriodsAvailable: "No periods available",
    dasaAgeUnavailable: "Age unavailable",
    dasaPeriodOutsideRange: "Target date is outside the available Dasa range",
    dasaBenefitBhavas: "Benefit Bhavas",
    dasaStarLord: "Star Lord",

    panchangTithi: "Tithi (Lunar Day)",
    panchangPaksha: "Paksha",
    panchangNakshatra: "Birth Nakshatra",
    panchangYoga: "Yoga",
    panchangKarana: "Karana",
    panchangVara: "Vara (Solar Day)",

    footerDisclaimer:
      "Gokul's Astrological Insights provides strictly rule-based astronomical ephemeris and classical Vedic calculations. Calculations are deterministic and provided for personal and educational insight without supernatural or predictive guarantees.",
    footerEngineInfo: "Powered by XALEN 0.6.0 Ephemeris Engine • Geocentric Sidereal Frame",
    footerCopyright: "© 2026 Gokul's Astrological Insights. All rights reserved.",

    // Authentication & Account
    navLogin: "Sign In",
    navRegister: "Register",
    navDashboard: "My Dashboard",
    navAdmin: "Admin Portal",
    navLogout: "Sign Out",

    loginTitle: "Sign In to Your Account",
    loginSubtitle:
      "Access your saved horoscopes, ephemeris calculations, and personalized astrological analysis.",
    fieldUsernameOrEmail: "Username or Email Address",
    fieldUsernameOrEmailPlaceholder: "Enter your username or email",
    fieldPassword: "Password",
    fieldPasswordPlaceholder: "Enter your password",
    showPassword: "Show password",
    hidePassword: "Hide password",
    signInButton: "Sign In",
    signingIn: "Verifying credentials...",
    invalidCredentials: "Invalid username/email or password.",
    connectionError:
      "Unable to connect to authentication server. Please check your network or try again later.",
    forgotPasswordLink: "Forgot your password?",
    dontHaveAccount: "Don't have an account?",
    registerLink: "Register here",
    alreadyHaveAccount: "Already have an account?",

    registerTitle: "Create Your Account",
    registerSubtitle:
      "Register to save and manage your Vedic & KP astrological charts with persistent database storage.",
    fieldUsername: "Username",
    fieldUsernamePlaceholder: "Choose a unique username",
    fieldEmail: "Email Address",
    fieldEmailPlaceholder: "Enter your active email",
    fieldConfirmPassword: "Confirm Password",
    fieldConfirmPasswordPlaceholder: "Re-enter your password",
    signUpButton: "Create Account",
    signingUp: "Registering account...",
    registrationSuccess: "Account registered successfully!",
    passwordMismatch: "Passwords do not match.",
    usernameRequirements:
      "3-30 characters, letters, numbers, underscores, and hyphens.",
    passwordRequirements: "At least 8 characters with letters and numbers.",

    forgotPasswordTitle: "Reset Your Password",
    forgotPasswordSubtitle:
      "Enter your registered email address to receive password reset instructions.",
    sendResetLink: "Send Reset Link",
    sendingResetLink: "Sending instructions...",
    resetLinkSent:
      "If an account is associated with that email, reset instructions have been dispatched.",
    backToLogin: "Back to Sign In",

    updatePasswordTitle: "Set New Password",
    updatePasswordSubtitle:
      "Please enter your new password to secure your account.",
    firstLoginNotice:
      "First-Time Administrator Login: You are required to update your initial password before accessing the system.",
    fieldNewPassword: "New Password",
    updatePasswordButton: "Update Password",
    updatingPassword: "Updating password...",
    passwordUpdatedSuccess: "Your password has been successfully updated.",

    userDashboardTitle: "User Dashboard",
    userDashboardSubtitle:
      "Manage your astrological charts and profile details.",
    adminDashboardTitle: "Administrative Control Center",
    adminDashboardSubtitle:
      "System administration, user oversight, and deterministic engine telemetry.",
    roleBadgeUser: "User",
    roleBadgeAdmin: "Administrator",
    savedHoroscopesTitle: "Saved Astrological Horoscopes",
    savedHoroscopesPlaceholder:
      "Horoscope auto-save database pipeline is configured for Task 3. You can generate charts from the Horoscope page.",
    memberSince: "Member Since",

    // Saved Horoscopes UI (Task 3)
    myHoroscopes: "My Horoscopes",
    createNewHoroscope: "+ Create New Horoscope",
    serialNumberLabel: "Serial #",
    birthDateLabel: "Birth Date",
    birthTimeLabel: "Birth Time",
    birthPlaceLabel: "Birth Place",
    actionEdit: "Edit",
    actionOpenHoroscope: "Open Horoscope",
    searchHoroscopesPlaceholder: "Search by birth name...",
    noSavedHoroscopes: "No saved horoscopes yet.",
    noSavedHoroscopesDesc:
      "Generate and compute your first Vedic & KP horoscope to view and manage it here.",
    noSearchResults: "No horoscopes matched your search criteria.",
    clearSearch: "Clear search",
    editHoroscopeTitle: "Edit Saved Birth Details",
    editHoroscopeSubtitle:
      "Update saved birth metadata or generate updated calculation results.",
    saveChangesButton: "Save Changes",
    savingChanges: "Saving changes...",
    recalculateAsNewButton: "Calculate as New Horoscope",
    recalculatingAsNew: "Calculating new chart...",
    editedWithoutRecalcBadge: "Details Edited",
    editedWithoutRecalcNotice:
      "Birth details have been updated since the stored calculation snapshot was created.",
    openHoroscopeStoredNotice:
      "Displaying stored calculation snapshot. No recalculation performed.",
    backToSavedHoroscopes: "Saved Horoscopes",
    unnamedHoroscope: "Unnamed Horoscope",
    locationUnavailable: "Location unavailable",
    autoSaveSuccess: "Horoscope saved to your account",
    autoSaveFailed: "Automatic save could not be completed",
    retrySave: "Retry Save",
    savingToDatabase: "Saving horoscope...",
    pageIndicator: "Page {current} of {total}",
    prevPage: "Previous",
    nextPage: "Next",
    totalHoroscopes: "Total: {count} horoscopes",
    deleteHoroscope: "Delete",
    confirmDeleteHoroscope:
      "Are you sure you want to delete this saved horoscope? This action cannot be undone.",


    // Numerology
    navNumerology: "Numerology",
    numerologyTitle: "Numerological Analysis & Destiny Blueprints",
    numerologySubtitle:
      "Deterministic, rule-based core numbers, 22-Arcana Destiny Matrix, and structured Yuan multi-dimensional frameworks.",
    cardTraditionalTitle: "Traditional Numerology",
    cardTraditionalDesc:
      "Calculate core numerology numbers using the person's name and date of birth.",
    cardTraditionalCta: "Open Traditional Numerology",
    cardDestinyTitle: "Destiny Matrix",
    cardDestinyDesc:
      "Generate a birth-date-based Destiny Matrix chart with its supported interpretations.",
    cardDestinyCta: "Open Destiny Matrix",
    cardAdvancedTitle: "Advanced Analysis",
    cardAdvancedDesc:
      "Access additional validated analysis methods and structured report features derived from compatible Yuan components.",
    cardAdvancedCta: "Open Advanced Analysis",
    savedNumerologyTitle: "Saved Numerology Reports",
    savedNumerologySubtitle: "Your auto-saved numerology calculations and structured readings.",
    savedNumerologyEmpty: "No numerology reports saved yet. Generate a reading above to automatically save it here.",
    saveReportSuccess: "Numerology report saved successfully to your dashboard.",
    reopenReport: "Reopen Report",
    printReport: "Print Report",
    exportPdf: "Export PDF",
    conventionPythagorean: "Pythagorean (Western Standard 1-9)",
    conventionChaldean: "Chaldean (Ancient Esoteric 1-8)",

    // Astrology Tools & Navigation Redesign
    navTools: "Astrology Tools",
    toolsTitle: "Astrology Tools | ஜோதிடக் கருவிகள்",
    toolsSubtitle: "Access your horoscope calculations, KP astrology analysis, and numerology tools from one place.",
    sectionHoroscopeTitle: "Horoscope / KP System",
    sectionHoroscopeTitleTa: "ஜாதகம் மற்றும் கே.பி. ஜோதிடம்",
    sectionHoroscopeDesc: "Create and manage horoscopes, examine planetary positions, explore KP astrology calculations, and access Dasa-Bhukti timelines.",
    sectionHoroscopeCta: "Open Horoscope Tools",
    sectionNumerologyTitle: "Numerology",
    sectionNumerologyTitleTa: "எண் கணிதம்",
    sectionNumerologyDesc: "Calculate numerology values, analyze names and birth dates, compare alternative spellings, and access supported numerology reports.",
    sectionNumerologyCta: "Open Numerology Tools",
    helpGuide: "Help & Guide",
    searchPlaceholder: "Search features, tools, or saved horoscopes...",
    welcomeBack: "Welcome back",
    homeQuickAccess: "Quick Tools Access",
    homeRecentCharts: "Recent Horoscopes",
    exploreCategories: "Astrology Tools Directory",
  },

  ta: {
    brandName: "கோகுலின் ஜோதிட நுண்ணறிவுகள்",
    brandTagline: "துல்லியமான வேத மற்றும் கே.பி வானியல் கணித முறை",
    navHome: "முகப்பு",
    navHoroscope: "ஜாதகம் கணிக்க",
    navMuhurta: "முகூர்த்தம்",
    navMethodology: "கணித முறைமை",
    navLanguage: "மொழி",
    statusOnline: "இயந்திரம் தயார்",
    statusDegraded: "குறைந்த நிலை",
    statusOffline: "இணைப்பு இல்லை",

    loading: "கணக்கீடுகள் செய்யப்படுகின்றன...",
    calculate: "வேத ஜாதகம் கணிக்க",
    calculating: "வானியல் எஃபிமெரிஸ் கணிக்கப்படுகிறது...",
    reset: "படிவத்தை அழிக்க",
    back: "பின்செல்",
    viewResults: "முடிவுகளைக் காண்க",
    error: "கணக்கீட்டுப் பிழை",
    retry: "மீண்டும் முயற்சிக்கவும்",
    optional: "விருப்பத்தேர்வு",
    required: "கட்டாயம்",
    notAvailableYet: "கணிப்பு இயந்திரத்திலிருந்து தரவு இன்னும் பெறப்படவில்லை",
    details: "விவரங்கள்",

    heroTitle: "வானியல் துல்லியத்துடன் கூடிய வேத மற்றும் கே.பி ஜோதிடம்",
    heroSubtitle:
      "XALEN வானியல் எஃபிமெரிஸ் இயந்திரத்தால் இயக்கப்படும் துல்லியமான, விதி சார்ந்த ஜோதிடக் கணக்கீடுகள். AI இல்லாத பாரம்பரிய வேத மற்றும் கிருஷ்ணமூர்த்தி பத்தாதி நியதிகளின் கணிதம்.",
    heroCta: "வேத ஜாதகம் கணிக்க",
    heroSecondaryCta: "கணித முறையை அறிக",
    featureTitle: "பாரம்பரிய ஜோதிடக் கணக்கீடுகள்",
    featureSubtitle:
      "ஜேபிஎல் (JPL) வானியல் தரவுகளின் அடிப்படையில் மில்லிசெகண்ட் கோணத் துல்லியத்துடன் நிராயன முறையில் கணக்கிடப்படுகிறது.",
    featEphemerisTitle: "XALEN வானியல் எஃபிமெரிஸ்",
    featEphemerisDesc:
      "துல்லியமான பூமி மைய சயன/நிராயன கிரக நிலைகள், அயனாம்சம் மற்றும் சந்திரனின் உண்மை முடிச்சுகளைக் கணக்கிடும் ரஸ்ட் (Rust) இயந்திரம்.",
    featVedicTitle: "பாரம்பரிய பராசர முறை",
    featVedicDesc:
      "ராசி, நவாம்சம், 12 பாவங்கள், 27 நட்சத்திரங்கள், பாதப் பிரிவுகள், கிரக வேகம் மற்றும் வக்ர நிலைகளின் தெளிவான பகுப்பாய்வு.",
    featKpTitle: "கே.பி கிருஷ்ணமூர்த்தி பத்தாதி",
    featKpDesc:
      "துல்லியமான 249 உப-பிரிவுகள் அட்டவணை, ராசி-நட்சத்திர-உப அதிபதிகள், பிளாசிடஸ் பாவக முனைகள் மற்றும் 4-நிலை காரகத்துவங்கள்.",
    featDasaTitle: "விம்சோத்தரி தசா அமைப்பு",
    featDasaDesc:
      "365.25 நாள் ஜூலியன் ஆண்டு நியதியின்படி பிறப்பு இருப்பு தசை முதல் பிராண தசை வரையிலான அடுக்கு விம்சோத்தரி தசா கணிப்பு.",
    limitationNoticeTitle: "கணித முறைமை மற்றும் ஜோதிட அறிவிப்பு",
    limitationNoticeText:
      "கோகுலின் ஜோதிட நுண்ணறிவுகளின் அனைத்து கணிப்புகளும் வானியல் மற்றும் பாரம்பரிய விதிகளின் அடிப்படையிலான நிர்ணயிக்கப்பட்ட கணித முடிவுகளே ஆகும். இவை கல்வி மற்றும் தனிப்பட்ட பயன்பாட்டிற்கானவை, எதிர்கால உத்தரவாதங்கள் அல்ல.",

    formTitle: "பிறப்பு விவரங்களை உள்ளிடவும்",
    formSubtitle:
      "துல்லியமான லக்னம், பாவக முனைகள் மற்றும் கே.பி உப-அதிபதிகளைக் கணக்கிட சரியான பிறந்த நேரம் மற்றும் இடத்தை வழங்கவும்.",
    sectionPersonal: "1. சுயவிவரம் மற்றும் பிறந்த நேரம்",
    fieldName: "முழு பெயர்",
    fieldNamePlaceholder: "எ.கா: சுந்தர் ராமன்",
    fieldDate: "பிறந்த தேதி",
    fieldTime: "பிறந்த நேரம் (24 மணி நேரம்)",
    fieldTimeConfirmed: "பிறந்த நேரம் உறுதி செய்யப்பட்டது",
    fieldTimeUnknownNotice:
      "குறிப்பு: பிறந்த நேரம் தோராயமாகவோ தெரியாமலோ இருந்தால், மதியம் 12:00 மணி நிலவரப்படி கிரக நிலைகளும் சந்திர நட்சத்திரமும் கணக்கிடப்படும். லக்னம், பாவங்கள் மற்றும் கே.பி உப-அதிபதிகளுக்கு சரியான பிறந்த நேரம் அவசியம்.",
    sectionLocation: "2. பிறந்த இடம் மற்றும் அட்சரேகை/தீர்க்கரேகை",
    fieldPlace: "பிறந்த ஊர் / நகரம்",
    fieldPlacePlaceholder: "நகரத்தைத் தேடுங்கள் (எ.கா: சென்னை, மதுரை, கோயம்புத்தூர், லண்டன்...)",
    fieldLatitude: "அட்சரேகை (Latitude)",
    fieldLongitude: "தீர்க்கரேகை (Longitude)",
    fieldTimezone: "நேர மண்டலம் (IANA Time Zone)",
    fieldTimezonePlaceholder: "நேர மண்டலத்தைத் தேர்ந்தெடுக்கவும்",
    sectionCalculations: "3. வானியல் அமைப்புகள்",
    fieldAyanamsa: "அயனாம்ச முறை",
    fieldHouseSystem: "பாவக முறை (House System)",
    fieldIncludePanchang: "பிறப்பு பஞ்சாங்கம் கணிக்கவும் (5 அங்கங்கள்)",
    fieldIncludeOuterPlanets: "வெளிப்புற கிரகங்களைச் சேர்க்கவும் (யுரேனஸ், நெப்டியூன், புளூட்டோ)",
    submitButton: "முழு ஜாதகத்தைக் கணிக்க",

    valDateRequired: "சரியான பிறந்த தேதியை உள்ளிடவும் (YYYY-MM-DD).",
    valTimeRequired: "சரியான பிறந்த நேரத்தை உள்ளிடவும் (HH:MM அல்லது HH:MM:SS).",
    valPlaceRequired: "பிறந்த ஊர் அல்லது நகரத்தைத் தேர்ந்தெடுக்கவும்.",
    valLatInvalid: "அட்சரேகை -90.0 முதல் +90.0 பாகைக்குள் இருக்க வேண்டும்.",
    valLonInvalid: "தீர்க்கரேகை -180.0 முதல் +180.0 பாகைக்குள் இருக்க வேண்டும்.",
    valTzRequired: "சரியான நேர மண்டலத்தைத் தேர்ந்தெடுக்கவும்.",

    resultsTitle: "ஜாதகம் மற்றும் ஜோதிட பகுப்பாய்வு",
    resultsSubtitle:
      "கணக்கிடப்பட்ட நிராயன கிரக நிலைகள், பாவக முனைகள், விம்சோத்தரி தசா இருப்பு மற்றும் கே.பி உப-அதிபதி நிலைகள்.",
    tabChart: "ராசி கட்டம்",
    tabPlanets: "கிரக நிலைகள்",
    tabHouses: "பாவகங்கள்",
    tabDasa: "விம்சோத்தரி தசை",
    tabKp: "கே.பி முறை",
    tabPanchang: "பஞ்சாங்கம்",
    tabNabhasha: "நபச யோகங்கள்",
    tabAshtakavarga: "அஷ்டகவர்க்கம்",
    tabVedicYogas: "வேத யோகங்கள்",
    tabMedicalAstrology: "மருத்துவ ஜோதிடம்",
    tabDoshas: "தோஷங்கள்",
    tabDestinyCard: "விதி அட்டை",
    destinyCardTitle: "வேத விதி அட்டை",
    destinyCardSubtitle:
      "XALEN வானியல் கணிப்பின் மூலம் பெறப்பட்ட அதிகாரப்பூர்வ ஜாதக அடையாள அட்டை.",
    destinyCardDownload: "உயர் தெளிவுத்திறன் PNG பதிவிறக்கு",
    destinyCardGenerating: "படம் உருவாக்கப்படுகிறது...",
    destinyCardLagna: "லக்னம்",
    destinyCardRasi: "சந்திர ராசி",
    destinyCardNakshatra: "ஜன்ம நட்சத்திரம்",
    destinyCardPada: "பாதம்",
    destinyCardDasa: "தற்போதைய மகா தசா",
    destinyCardBirthDasa: "ஜன்ம மகா தசா",
    destinyCardSunSign: "சூரிய ராசி",
    destinyCardLord: "நட்சத்திர அதிபதி",
    destinyCardAyanamsa: "அயனாம்சம்",
    destinyCardVerification: "சரிபார்க்கப்பட்ட XALEN கணிப்பு",
    destinyCardPrivacyNotice:
      "உங்கள் தனியுரிமையைப் பாதுகாக்க துல்லியமான இருப்பிட விவரங்கள் தவிர்க்கப்பட்டுள்ளன.",
    destinyCardShowDate: "பிறந்த தேதியை இணைக்க",
    destinyCardMissingData:
      "விதி அட்டையை உருவாக்க அதிகாரப்பூர்வ கணிப்புத் தரவு தேவைப்படுகிறது.",
    destinyCardSwitchLang: "அட்டை மொழி",
    vedicYogasTitle: "வேத யோக கால்குலேட்டர்",
    vedicYogasSubtitle: "துல்லியமான கிரக நிலைகள் மற்றும் பாவாதிபதிகள் அடிப்படையில் கணக்கிடப்பட்ட பாரம்பரிய வேத யோகங்கள்.",
    vedicYogasTotalQualifying: "பொருந்தும் யோகங்கள்",
    vedicYogasRajaYogas: "ராஜ யோகங்கள்",
    vedicYogasDhanaYogas: "தன யோகங்கள்",
    vedicYogasMahapurusha: "மகாபுருஷ யோகங்கள்",
    vedicYogasVipareeta: "விபரீத ராஜ யோகம்",
    vedicYogasOtherClassical: "இதர யோகங்கள்",
    vedicYogasFilterAll: "அனைத்து யோகங்கள்",
    vedicYogasFilterQualifying: "பொருந்தியவை மட்டும்",
    vedicYogasFilterNonQualifying: "பொருந்தாதவை & ரத்தானவை",
    vedicYogasSearchPlaceholder: "யோகப் பெயரைத் தேடுக...",
    vedicYogasColSNo: "எண்",
    vedicYogasColName: "யோகப் பெயர்",
    vedicYogasColCategory: "பிரிவு",
    vedicYogasColStatus: "நிலை",
    vedicYogasColPlanets: "பங்கேற்கும் கிரகங்கள்",
    vedicYogasColHouses: "பாவங்கள்",
    vedicYogasColConditions: "அமைப்பு விவரம்",
    vedicYogasColAction: "விவரம்",
    vedicYogasModalTitle: "யோக ஆய்வுக் கண்ணோட்டம்",
    vedicYogasModalDefinition: "பாரம்பரிய வரையறை",
    vedicYogasModalConditionsEval: "ஆய்வு செய்யப்பட்ட நிபந்தனைகள்",
    vedicYogasModalInterpretation: "பாரம்பரிய பலன்",
    vedicYogasModalReference: "சாஸ்திர ஆதாரம்",
    vedicYogasModalVerification: "விதி சரிபார்ப்பு நிலை",
    vedicYogasModalCancellation: "பங்க பகுப்பாய்வு (ரத்து விவரம்)",
    doshasTitle: "வேத தோஷ பகுப்பாய்வு",
    doshasSubtitle: "துல்லியமான கிரக நிலைகள், திருக்கணித விதிகள் மற்றும் பரிகார/பங்க அமைப்புகளின் அடிப்படையில் கணக்கிடப்பட்ட பாரம்பரிய தோஷங்கள்.",
    doshasTotalEvaluated: "ஆய்வு செய்யப்பட்ட விதிகள்",
    doshasPresent: "உள்ள தோஷங்கள்",
    doshasMitigated: "பங்கமடைந்தவை / நிவர்த்தி",
    doshasAbsent: "தோஷமில்லை",
    doshasIndeterminate: "கூடுதல் தரவு தேவை",
    doshasFilterAll: "அனைத்து தோஷங்கள்",
    doshasFilterPresent: "உள்ளவை மட்டும்",
    doshasFilterMitigated: "நிவர்த்தியானவை மட்டும்",
    doshasFilterAbsent: "இல்லாதவை மட்டும்",
    doshasFilterIndeterminate: "தரவு தேவைப்படுபவை",
    doshasSearchPlaceholder: "தோஷப் பெயர், கிரகம் அல்லது வகையைத் தேடுக...",
    doshasColSNo: "எண்",
    doshasColName: "தோஷப் பெயர்",
    doshasColCategory: "பிரிவு",
    doshasColStatus: "நிலை",
    doshasColPlanets: "கிரகங்கள் & பாகைகள்",
    doshasColReference: "ஆதார மையம்",
    doshasColConditions: "அமைப்பு விவரம்",
    doshasColAction: "விவரம்",
    doshasModalTitle: "தோஷ ஆய்வுக் கண்ணோட்டம்",
    doshasModalFormation: "ஆய்வு செய்யப்பட்ட தோஷ விதிகள்",
    doshasModalCancellation: "பங்க மற்றும் நிவர்த்தி ஆய்வு",
    doshasModalInterpretation: "பாரம்பரிய பலன் விளக்கம்",
    doshasModalRemedies: "சாஸ்திர பரிகார முறைகள்",
    doshasModalReference: "சாஸ்திர ஆதாரம் & விதித்தொகுப்பு",
    doshasModalMissingPrereq: "முன்நிபந்தனை தகவல்",
    doshasMissingNotice: "இந்த ஜாதகத்திற்கு வேத தோஷ பகுப்பாய்வு இன்னும் கணக்கிடப்படவில்லை.",
    doshasCalculateButton: "வேத தோஷங்களை கணக்கிடுக",
    doshasCalculating: "30 பாரம்பரிய தோஷ விதிகள் கணக்கிடப்படுகின்றன...",
    nabhashaTitle: "பாரம்பரிய நபச யோகங்கள்",
    nabhashaSubtitle: "7 பாரம்பரிய கிரகங்களின் ராசி/பாவக அமைப்பால் உருவாகும் விண்வெளி வடிவ யோகங்கள் (பராசரர் ஹோரா சாஸ்திரம் அத்தியாயம் 35).",
    nabhashaPrimaryYoga: "முதன்மைச் செயல் யோகம்",
    nabhashaCategory: "வகைப்பாடு",
    nabhashaFormationRule: "பாரம்பரிய உருவாக்கம் விதி",
    nabhashaDescription: "பாரம்பரிய பலன் விளக்கம்",
    nabhashaPlanetsInvolved: "பங்குபெறும் கிரகங்கள்",
    nabhashaQualifyingHouses: "அமைந்த பாவகங்கள்",
    nabhashaQualifyingSigns: "அமைந்த ராசிகள்",
    nabhashaDistribution: "கிரகங்களின் பாவகப் பரவல்",
    nabhashaDistinctSigns: "கிரகங்கள் உள்ள ராசிகள்",
    nabhashaDistinctHouses: "கிரகங்கள் உள்ள பாவகங்கள்",
    nabhashaKendraPlanets: "கேந்திர கிரகங்கள் (1, 4, 7, 10)",
    nabhashaPanapharaPlanets: "பணபர கிரகங்கள் (2, 5, 8, 11)",
    nabhashaApoklimaPlanets: "அபோக்லிம கிரகங்கள் (3, 6, 9, 12)",
    nabhashaTrikonaPlanets: "திரிகோண கிரகங்கள் (1, 5, 9)",
    nabhashaAllQualifying: "தகுதிபெறும் அனைத்து யோகங்கள்",
    nabhashaPrecedenceNotice: "பராசரர் முன்னுரிமை விதிப்படி கணக்கிடப்பட்டது: ஆச்ரய -> தல -> ஆக்ருதி -> சங்க்யா.",
    ashtakavargaTitle: "பாரம்பரிய அஷ்டகவர்க்க முறை",
    ashtakavargaSubtitle: "சுப பிந்து பரவல், திரிகோண/ஏகாதிபத்ய சோதனைகள் மற்றும் சோத்திய பிண்டம் (பராசரர் ஹோரா சாஸ்திரம் அத்தியாயங்கள் 66–73).",
    ashtakavargaSavTab: "சர்வ அஷ்டகவர்க்கம் (SAV)",
    ashtakavargaBavTab: "பின்ன அஷ்டகவர்க்கம் (BAV)",
    ashtakavargaMatrixTab: "7-கிரக BAV கட்டம்",
    ashtakavargaRawBindus: "அசல் பிந்துக்கள்",
    ashtakavargaTrikona: "திரிகோண சோதனை",
    ashtakavargaEkadhipatya: "ஏகாதிபத்திய சோதனை",
    ashtakavargaShodhyaPinda: "சோத்திய பிண்டம்",
    ashtakavargaRashiPinda: "ராசி பிண்டம்",
    ashtakavargaGrahaPinda: "கிரக பிண்டம்",
    ashtakavargaTotalBindus: "மொத்த பிந்துக்கள்",
    ashtakavargaAuspiciousSigns: "சுப ராசிகள் (≥ 28 பிந்துக்கள்)",
    ashtakavargaInauspiciousSigns: "குறைவு ராசிகள் (< 28 பிந்துக்கள்)",
    ashtakavargaInvariantValidated: "337 மொத்த பிந்து விதி சரிபார்க்கப்பட்டது",
    chartSouthIndian: "தென்னிந்திய முறை (சதுர கட்டம்)",
    chartNorthIndian: "வடஇந்திய முறை (வைர கட்டம்)",
    chartSwitchMode: "ஜாதக வடிவம்",
    birthSummaryTitle: "ஜாதகர் மற்றும் வானியல் குறிப்பு",
    calculatedWith: "கணக்கிடப்பட்ட இயந்திரம்",
    recalculateCta: "மற்றொரு ஜாதகம் கணிக்க",

    planet: "கிரகம்",
    longitude: "ஸ்புடம் (பாகை)",
    sign: "ராசி",
    degreeInSign: "ராசி பாகை",
    nakshatra: "நட்சத்திரம்",
    pada: "பாதம்",
    lord: "அதிபதி",
    speed: "வேகம் (°/நாள்)",
    retrograde: "வக்ரம்",
    direct: "நேர்கதி",
    ascendant: "லக்னம் (ASC)",
    midheaven: "பத்தாம் பாவம் (MC)",
    house: "பாவம்",
    cuspDegree: "பாவக முனை பாகை",
    starLord: "நட்சத்திர அதிபதி",
    subLord: "உப அதிபதி",
    subSubLord: "உப-உப அதிபதி",
    kpNumber: "கே.பி எண்",
    promise: "பலன் வாக்குறுதி",
    significators: "காரகத்துவ பலம்",

    dasaBalanceAtBirth: "பிறப்பில் தசா இருப்பு",
    dasaActiveNow: "தற்போது நடைபெறும் தசா-புக்தி",
    dasaMahadasha: "மகா தசை",
    dasaAntardasha: "அந்தர்தசை (புக்தி)",
    dasaPratyantar: "பிரத்யந்தர தசை",
    dasaPratyantardasha: "பிரத்யந்தர தசை (அந்தரம்)",
    dasaSookshmadasha: "சூட்சும தசை (சூட்சுமம்)",
    dasaPranadasha: "பிராண தசை (பிராணன்)",
    dasaStartDate: "தொடக்க தேதி",
    dasaEndDate: "முடிவு தேதி",
    dasaAgeAtStart: "தொடக்கத்தில் வயது",
    dasaAgeAtEnd: "முடிவில் வயது",
    dasaDuration: "கால அளவு",
    dasaActivePeriod: "நடப்பு தசா காலம்",
    dasaSelectedDate: "தேர்ந்தெடுக்கப்பட்ட தேதி",
    dasaExpand: "விரிவாக்கு",
    dasaCollapse: "சுருக்கு",
    dasaExpandAll: "அனைத்தையும் விரிவாக்கு",
    dasaCollapseAll: "அனைத்தையும் சுருக்கு",
    dasaExpandActivePath: "நடப்பு தசா பாதையை விரிவாக்கு",
    dasaLoading: "தசா விவரங்கள் ஏற்றப்படுகின்றன...",
    dasaNoPeriodsAvailable: "தசா காலங்கள் எதுவும் இல்லை",
    dasaAgeUnavailable: "வயது கிடைக்கவில்லை",
    dasaPeriodOutsideRange: "தேர்ந்தெடுக்கப்பட்ட தேதி தசா கால வரம்பிற்கு வெளியே உள்ளது",
    dasaBenefitBhavas: "பலன் தரும் பாவகங்கள்",
    dasaStarLord: "சார நாதர்",

    panchangTithi: "திதி",
    panchangPaksha: "பட்சம்",
    panchangNakshatra: "பிறந்த நட்சத்திரம்",
    panchangYoga: "யோகம்",
    panchangKarana: "கரணம்",
    panchangVara: "வாரம் (கிழமை)",

    footerDisclaimer:
      "கோகுலின் ஜோதிட நுண்ணறிவுகள் பாரம்பரிய வேத ஜோதிட நியதிகள் மற்றும் வானியல் கணிதத்தின்படி துல்லியமாக இயங்குகிறது. இக்கணிப்புகள் கல்வி மற்றும் தனிப்பட்ட ஆய்வு நோக்கம் கொண்டவை; எதிர்கால உறுதிமொழிகள் அல்ல.",
    footerEngineInfo: "XALEN 0.6.0 எஃபிமெரிஸ் கணித இயந்திரம் • பூமி மைய நிராயன முறை",
    footerCopyright: "© 2026 கோகுலின் ஜோதிட நுண்ணறிவுகள். அனைத்து உரிமைகளும் பாதுகாக்கப்பட்டவை.",

    // Authentication & Account
    navLogin: "உள்நுழைக",
    navRegister: "பதிவு செய்க",
    navDashboard: "என் கணக்கு பலகை",
    navAdmin: "நிர்வாக தளம்",
    navLogout: "வெளியேறுக",

    loginTitle: "உங்கள் கணக்கில் உள்நுழையவும்",
    loginSubtitle:
      "சேமிக்கப்பட்ட ஜாதகங்கள், எஃபிமெரிஸ் கணக்கீடுகள் மற்றும் தனிப்பயனாக்கப்பட்ட ஜோதிட பகுப்பாய்வுகளை அணுகவும்.",
    fieldUsernameOrEmail: "பயனர் பெயர் அல்லது மின்னஞ்சல் முகவரி",
    fieldUsernameOrEmailPlaceholder: "பயனர் பெயர் அல்லது மின்னஞ்சலை உள்ளிடவும்",
    fieldPassword: "கடவுச்சொல்",
    fieldPasswordPlaceholder: "உங்கள் கடவுச்சொல்லை உள்ளிடவும்",
    showPassword: "கடவுச்சொல்லைக் காட்டு",
    hidePassword: "கடவுச்சொல்லை மறை",
    signInButton: "உள்நுழைக",
    signingIn: "சரிபார்க்கப்படுகிறது...",
    invalidCredentials: "தவறான பயனர் பெயர்/மின்னஞ்சல் அல்லது கடவுச்சொல்.",
    connectionError:
      "அங்கீகார சேவையகத்துடன் இணைக்க முடியவில்லை. இணைய இணைப்பைச் சரிபார்க்கவும் அல்லது சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்.",
    forgotPasswordLink: "கடவுச்சொல் மறந்துவிட்டதா?",
    dontHaveAccount: "கணக்கு இல்லையா?",
    registerLink: "இங்கே பதிவு செய்க",
    alreadyHaveAccount: "ஏற்கனவே கணக்கு உள்ளதா?",

    registerTitle: "புதிய கணக்கை உருவாக்கவும்",
    registerSubtitle:
      "நிரந்தர தரவுத்தள சேமிப்பகத்துடன் உங்கள் வேத மற்றும் கே.பி ஜோதிட வரைபடங்களைச் சேமித்து நிர்வகிக்க பதிவு செய்யவும்.",
    fieldUsername: "பயனர் பெயர் (Username)",
    fieldUsernamePlaceholder: "தனித்துவமான பயனர் பெயரைத் தேர்ந்தெடுக்கவும்",
    fieldEmail: "மின்னஞ்சல் முகவரி",
    fieldEmailPlaceholder: "செயலில் உள்ள மின்னஞ்சலை உள்ளிடவும்",
    fieldConfirmPassword: "கடவுச்சொல்லை உறுதிப்படுத்தவும்",
    fieldConfirmPasswordPlaceholder: "மீண்டும் கடவுச்சொல்லை உள்ளிடவும்",
    signUpButton: "கணக்கை உருவாக்கு",
    signingUp: "பதிவு செய்யப்படுகிறது...",
    registrationSuccess: "கணக்கு வெற்றிகரமாக உருவாக்கப்பட்டது!",
    passwordMismatch: "கடவுச்சொற்கள் பொருந்தவில்லை.",
    usernameRequirements:
      "3-30 எழுத்துகள், எண்கள், அடிக்கோடுகள் மற்றும் ஹைபன்கள் மட்டும்.",
    passwordRequirements: "குறைந்தபட்சம் 8 எழுத்துகள், எண்கள் மற்றும் எழுத்துகளுடன்.",

    forgotPasswordTitle: "கடவுச்சொல்லை மீட்டமைக்கவும்",
    forgotPasswordSubtitle:
      "கடவுச்சொல் மீட்டமைப்பு வழிமுறைகளைப் பெற உங்கள் பதிவுசெய்த மின்னஞ்சலை உள்ளிடவும்.",
    sendResetLink: "மீட்டமைப்பு இணைப்பை அனுப்புக",
    sendingResetLink: "அனுப்பப்படுகிறது...",
    resetLinkSent:
      "அந்த மின்னஞ்சல் கணக்குடன் இணைக்கப்பட்டிருந்தால், மீட்டமைப்பு வழிமுறைகள் அனுப்பப்பட்டுள்ளன.",
    backToLogin: "உள்நுழைவுப் பக்கத்திற்குத் திரும்புக",

    updatePasswordTitle: "புதிய கடவுச்சொல்லை அமைக்கவும்",
    updatePasswordSubtitle:
      "உங்கள் கணக்கைப் பாதுகாக்க புதிய கடவுச்சொல்லை உள்ளிடவும்.",
    firstLoginNotice:
      "முதல் முறை நிர்வாகி உள்நுழைவு: கணினியை அணுகுவதற்கு முன் ஆரம்ப கடவுச்சொல்லை மாற்ற வேண்டும்.",
    fieldNewPassword: "புதிய கடவுச்சொல்",
    updatePasswordButton: "கடவுச்சொல்லை மாற்று",
    updatingPassword: "மாற்றப்படுகிறது...",
    passwordUpdatedSuccess: "உங்கள் கடவுச்சொல் வெற்றிகரமாக மாற்றப்பட்டது.",

    userDashboardTitle: "பயனர் பலகை",
    userDashboardSubtitle:
      "உங்கள் ஜோதிட வரைபடங்கள் மற்றும் சுயவிவர விவரங்களை நிர்வகிக்கவும்.",
    adminDashboardTitle: "நிர்வாகக் கட்டுப்பாட்டு மையம்",
    adminDashboardSubtitle:
      "கணினி நிர்வாகம், பயனர் மேற்பார்வை மற்றும் எஃபிமெரிஸ் இயந்திரக் கண்காணிப்பு.",
    roleBadgeUser: "பயனர்",
    roleBadgeAdmin: "முதன்மை நிர்வாகி",
    savedHoroscopesTitle: "சேமிக்கப்பட்ட ஜோதிட ஜாதகங்கள்",
    savedHoroscopesPlaceholder:
      "ஜாதக தானியங்கி சேமிப்பு தரவுத்தள இணைப்பு பணி 3-க்காக தயார் செய்யப்பட்டுள்ளது. நீங்கள் ஜாதக பக்கத்திலிருந்து கணக்கீடுகளைச் செய்யலாம்.",
    memberSince: "இணைந்த தேதி",

    // Saved Horoscopes UI (Task 3)
    myHoroscopes: "எனது ஜாதகங்கள்",
    createNewHoroscope: "+ புதிய ஜாதகம்",
    serialNumberLabel: "வரிசை எண் #",
    birthDateLabel: "பிறந்த தேதி",
    birthTimeLabel: "பிறந்த நேரம்",
    birthPlaceLabel: "பிறந்த இடம்",
    actionEdit: "திருத்து",
    actionOpenHoroscope: "ஜாதகத்தைத் திற",
    searchHoroscopesPlaceholder: "பெயர் மூலம் தேடுக...",
    noSavedHoroscopes: "சேமிக்கப்பட்ட ஜாதகங்கள் எதுவும் இல்லை",
    noSavedHoroscopesDesc:
      "இங்கே நிர்வகிக்க உங்கள் முதல் வேத & கே.பி ஜாதகத்தை கணக்கிட்டுச் சேமியுங்கள்.",
    noSearchResults: "உங்கள் தேடலுக்கு ஏற்ற ஜாதகங்கள் எதுவும் கிடைக்கவில்லை.",
    clearSearch: "தேடலை அழி",
    editHoroscopeTitle: "சேமிக்கப்பட்ட பிறப்பு விவரங்களைத் திருத்து",
    editHoroscopeSubtitle:
      "பிறப்பு விவரங்களைப் புதுப்பிக்கவும் அல்லது புதிய கணிப்பை உருவாக்கவும்.",
    saveChangesButton: "மாற்றங்களைச் சேமி",
    savingChanges: "சேமிக்கப்படுகிறது...",
    recalculateAsNewButton: "புதிய ஜாதகமாகக் கணக்கிடுக",
    recalculatingAsNew: "புதிய ஜாதகம் கணக்கிடப்படுகிறது...",
    editedWithoutRecalcBadge: "விவரங்கள் மாற்றப்பட்டன",
    editedWithoutRecalcNotice:
      "சேமிக்கப்பட்ட கணிப்பிற்குப் பிறகு பிறப்பு விவரங்கள் மாற்றப்பட்டுள்ளன.",
    openHoroscopeStoredNotice:
      "சேமிக்கப்பட்ட கணிப்பு முடிவுகள் காட்டப்படுகின்றன. மறு கணக்கீடு செய்யப்படவில்லை.",
    backToSavedHoroscopes: "சேமிக்கப்பட்ட ஜாதகங்கள்",
    unnamedHoroscope: "பெயரிடப்படாத ஜாதகம்",
    locationUnavailable: "இடம் குறிப்பிடப்படவில்லை",
    autoSaveSuccess: "ஜாதகம் உங்கள் கணக்கில் சேமிக்கப்பட்டது",
    autoSaveFailed: "தானியங்கி சேமிப்பு தோல்வியடைந்தது",
    retrySave: "மீண்டும் சேமிக்க",
    savingToDatabase: "ஜாதகம் சேமிக்கப்படுகிறது...",
    pageIndicator: "பக்கம் {current} / {total}",
    prevPage: "முந்தையது",
    nextPage: "அடுத்தது",
    totalHoroscopes: "மொத்தம்: {count} ஜாதகங்கள்",
    deleteHoroscope: "நீக்கு",
    confirmDeleteHoroscope:
      "இந்த சேமிக்கப்பட்ட ஜாதகத்தை நிச்சயம் நீக்க விரும்புகிறீர்களா? இதை மீட்டெடுக்க முடியாது.",


    // Numerology
    navNumerology: "எண் கணிதம்",
    numerologyTitle: "எண் கணித பகுப்பாய்வு & விதி வரைபடம்",
    numerologySubtitle:
      "விதி சார்ந்த மூல எண்கள், 22-ஆர்கானா விதி அணி (Destiny Matrix), மற்றும் யுவான் பல பரிமாண பகுப்பாய்வு முறை.",
    cardTraditionalTitle: "பாரம்பரிய எண் கணிதம்",
    cardTraditionalDesc: "முழு பெயர் மற்றும் பிறந்த தேதியை அடிப்படையாகக் கொண்டு அடிப்படை மூல எண்களைக் கணக்கிடுங்கள்.",
    cardTraditionalCta: "பாரம்பரிய எண் கணிதத்தைத் திறக்க",
    cardDestinyTitle: "விதி அணி (Destiny Matrix)",
    cardDestinyDesc: "பிறந்த தேதியின் அடிப்படையில் 22 ஆர்கானா எண்களுடன் கூடிய தனிப்பயன் வரைபடத்தை உருவாக்குங்கள்.",
    cardDestinyCta: "விதி அணியைத் திறக்க",
    cardAdvancedTitle: "மேம்பட்ட பகுப்பாய்வு",
    cardAdvancedDesc: "யுவான் கட்டமைப்பு, லோ-ஷூ 3x3 கட்டம், 4 உன்னத காலங்கள் மற்றும் கர்ம கடன்களை ஆராயுங்கள்.",
    cardAdvancedCta: "மேம்பட்ட பகுப்பாய்வைத் திறக்க",
    savedNumerologyTitle: "சேமிக்கப்பட்ட எண் கணித அறிக்கைகள்",
    savedNumerologySubtitle: "தானாக சேமிக்கப்பட்ட உங்கள் முந்தைய எண் கணித அறிக்கைகள் மற்றும் விரிவான விளக்கங்கள்.",
    savedNumerologyEmpty: "இதுவரை எந்த எண் கணித அறிக்கையும் சேமிக்கப்படவில்லை. மேலே புதிய கணக்கீட்டை மேற்கொண்டு தானாக சேமியுங்கள்.",
    saveReportSuccess: "எண் கணித அறிக்கை உங்கள் பலகையில் வெற்றிகரமாக சேமிக்கப்பட்டது.",
    reopenReport: "அறிக்கையைத் திறக்க",
    printReport: "அச்சிடுக",
    exportPdf: "PDF ஏற்றுமதி",
    conventionPythagorean: "பித்தகோரியன் முறை (1-9)",
    conventionChaldean: "கால்டியன் முறை (1-8)",

    // Astrology Tools & Navigation Redesign
    navTools: "ஜோதிடக் கருவிகள்",
    toolsTitle: "ஜோதிடக் கருவிகள் | Astrology Tools",
    toolsSubtitle: "உங்கள் ஜாதகக் கணிப்புகள், கே.பி. ஜோதிட பகுப்பாய்வு மற்றும் எண் கணித கருவிகளை ஒரே இடத்தில் அணுகலாம்.",
    sectionHoroscopeTitle: "ஜாதகம் மற்றும் கே.பி. ஜோதிடம்",
    sectionHoroscopeTitleTa: "Horoscope / KP System",
    sectionHoroscopeDesc: "ஜாதகங்களை உருவாக்கவும் நிர்வகிக்கவும், கிரக நிலைகளை ஆராயவும், கே.பி ஜோதிடக் கணிப்புகளை அறியவும், மற்றும் தசா-புக்தி காலவரிசையை அணுகவும்.",
    sectionHoroscopeCta: "ஜாதகக் கருவிகளைத் திறக்க",
    sectionNumerologyTitle: "எண் கணிதம்",
    sectionNumerologyTitleTa: "Numerology",
    sectionNumerologyDesc: "எண் கணித மதிப்புகளைக் கணக்கிடுங்கள், பெயர்கள் மற்றும் பிறந்த தேதிகளை பகுப்பாய்வு செய்யுங்கள், மாற்று எழுத்துப்பிழைகளை ஒப்பிடுங்கள், மேலும் எண் கணித அறிக்கைகளை அணுகுங்கள்.",
    sectionNumerologyCta: "எண் கணிதக் கருவிகளைத் திறக்க",
    helpGuide: "உதவி & வழிகாட்டி",
    searchPlaceholder: "கருவிகள், ஜாதகங்களைத் தேடுக...",
    welcomeBack: "மீண்டும் நல்வரவு",
    homeQuickAccess: "விரைவு அணுகல் கருவிகள்",
    homeRecentCharts: "சமீபத்திய ஜாதகங்கள்",
    exploreCategories: "ஜோதிடக் கருவிகள் அடைவு",
  },
};

// 12 Rasis (Signs) Dictionary
export interface RasiItem {
  index: number; // 1-12
  nameEn: string;
  nameTa: string;
  lordEn: string;
  lordTa: string;
  symbol: string;
}

export const RASIS: Record<number, RasiItem> = {
  1: { index: 1, nameEn: "Aries", nameTa: "மேஷம்", lordEn: "Mars", lordTa: "செவ்வாய்", symbol: "♈" },
  2: { index: 2, nameEn: "Taurus", nameTa: "ரிஷபம்", lordEn: "Venus", lordTa: "சுக்கிரன்", symbol: "♉" },
  3: { index: 3, nameEn: "Gemini", nameTa: "மிதுனம்", lordEn: "Mercury", lordTa: "புதன்", symbol: "♊" },
  4: { index: 4, nameEn: "Cancer", nameTa: "கடகம்", lordEn: "Moon", lordTa: "சந்திரன்", symbol: "♋" },
  5: { index: 5, nameEn: "Leo", nameTa: "சிம்மம்", lordEn: "Sun", lordTa: "சூரியன்", symbol: "♌" },
  6: { index: 6, nameEn: "Virgo", nameTa: "கன்னி", lordEn: "Mercury", lordTa: "புதன்", symbol: "♍" },
  7: { index: 7, nameEn: "Libra", nameTa: "துலாம்", lordEn: "Venus", lordTa: "சுக்கிரன்", symbol: "♎" },
  8: { index: 8, nameEn: "Scorpio", nameTa: "விருச்சிகம்", lordEn: "Mars", lordTa: "செவ்வாய்", symbol: "♏" },
  9: { index: 9, nameEn: "Sagittarius", nameTa: "தனுசு", lordEn: "Jupiter", lordTa: "குரு", symbol: "♐" },
  10: { index: 10, nameEn: "Capricorn", nameTa: "மகரம்", lordEn: "Saturn", lordTa: "சனி", symbol: "♑" },
  11: { index: 11, nameEn: "Aquarius", nameTa: "கும்பம்", lordEn: "Saturn", lordTa: "சனி", symbol: "♒" },
  12: { index: 12, nameEn: "Pisces", nameTa: "மீனம்", lordEn: "Jupiter", lordTa: "குரு", symbol: "♓" },
};

// 9 Traditional Grahas + Outer Planets Dictionary
export interface GrahaItem {
  id: number;
  nameEn: string;
  nameTa: string;
  shortEn: string;
  shortTa: string;
  color: string;
}

export const GRAHAS: Record<string, GrahaItem> = {
  Sun: { id: 0, nameEn: "Sun (Surya)", nameTa: "சூரியன்", shortEn: "Su", shortTa: "சூரி", color: "#B45309" },
  Moon: { id: 1, nameEn: "Moon (Chandra)", nameTa: "சந்திரன்", shortEn: "Mo", shortTa: "சந்", color: "#3B82F6" },
  Mars: { id: 2, nameEn: "Mars (Mangala)", nameTa: "செவ்வாய்", shortEn: "Ma", shortTa: "செவ்", color: "#DC2626" },
  Mercury: { id: 3, nameEn: "Mercury (Budha)", nameTa: "புதன்", shortEn: "Me", shortTa: "புத", color: "#059669" },
  Jupiter: { id: 4, nameEn: "Jupiter (Guru)", nameTa: "குரு (வியாழன்)", shortEn: "Ju", shortTa: "குரு", color: "#D97706" },
  Venus: { id: 5, nameEn: "Venus (Shukra)", nameTa: "சுக்கிரன் (வெள்ளி)", shortEn: "Ve", shortTa: "சுக்", color: "#DB2777" },
  Saturn: { id: 6, nameEn: "Saturn (Shani)", nameTa: "சனி", shortEn: "Sa", shortTa: "சனி", color: "#4B5563" },
  Rahu: { id: 7, nameEn: "Rahu (North Node)", nameTa: "ராகு", shortEn: "Ra", shortTa: "ராகு", color: "#475569" },
  Ketu: { id: 8, nameEn: "Ketu (South Node)", nameTa: "கேது", shortEn: "Ke", shortTa: "கேது", color: "#78716C" },
  Uranus: { id: 9, nameEn: "Uranus", nameTa: "யுரேனஸ்", shortEn: "Ur", shortTa: "யுரே", color: "#0284C7" },
  Neptune: { id: 10, nameEn: "Neptune", nameTa: "நெப்டியூன்", shortEn: "Ne", shortTa: "நெப்", color: "#2563EB" },
  Pluto: { id: 11, nameEn: "Pluto", nameTa: "புளூட்டோ", shortEn: "Pl", shortTa: "புளூ", color: "#64748B" },
};

// 27 Nakshatras Dictionary
export interface NakshatraItem {
  index: number; // 1-27
  nameEn: string;
  nameTa: string;
  lordEn: string;
  lordTa: string;
}

export const NAKSHATRAS: Record<number, NakshatraItem> = {
  1: { index: 1, nameEn: "Ashwini", nameTa: "அஸ்வினி", lordEn: "Ketu", lordTa: "கேது" },
  2: { index: 2, nameEn: "Bharani", nameTa: "பரணி", lordEn: "Venus", lordTa: "சுக்கிரன்" },
  3: { index: 3, nameEn: "Krittika", nameTa: "கார்த்திகை", lordEn: "Sun", lordTa: "சூரியன்" },
  4: { index: 4, nameEn: "Rohini", nameTa: "ரோகிணி", lordEn: "Moon", lordTa: "சந்திரன்" },
  5: { index: 5, nameEn: "Mrigashira", nameTa: "மிருகசீரிஷம்", lordEn: "Mars", lordTa: "செவ்வாய்" },
  6: { index: 6, nameEn: "Ardra", nameTa: "திருவாதிரை", lordEn: "Rahu", lordTa: "ராகு" },
  7: { index: 7, nameEn: "Punarvasu", nameTa: "புனர்பூசம்", lordEn: "Jupiter", lordTa: "குரு" },
  8: { index: 8, nameEn: "Pushya", nameTa: "பூசம்", lordEn: "Saturn", lordTa: "சனி" },
  9: { index: 9, nameEn: "Ashlesha", nameTa: "ஆயில்யம்", lordEn: "Mercury", lordTa: "புதன்" },
  10: { index: 10, nameEn: "Magha", nameTa: "மகம்", lordEn: "Ketu", lordTa: "கேது" },
  11: { index: 11, nameEn: "Purva Phalguni", nameTa: "பூரம்", lordEn: "Venus", lordTa: "சுக்கிரன்" },
  12: { index: 12, nameEn: "Uttara Phalguni", nameTa: "உத்திரம்", lordEn: "Sun", lordTa: "சூரியன்" },
  13: { index: 13, nameEn: "Hasta", nameTa: "ஹஸ்தம்", lordEn: "Moon", lordTa: "சந்திரன்" },
  14: { index: 14, nameEn: "Chitra", nameTa: "சித்திரை", lordEn: "Mars", lordTa: "செவ்வாய்" },
  15: { index: 15, nameEn: "Swati", nameTa: "சுவாதி", lordEn: "Rahu", lordTa: "ராகு" },
  16: { index: 16, nameEn: "Vishakha", nameTa: "விசாகம்", lordEn: "Jupiter", lordTa: "குரு" },
  17: { index: 17, nameEn: "Anuradha", nameTa: "அனுஷம்", lordEn: "Saturn", lordTa: "சனி" },
  18: { index: 18, nameEn: "Jyeshtha", nameTa: "கேட்டை", lordEn: "Mercury", lordTa: "புதன்" },
  19: { index: 19, nameEn: "Mula", nameTa: "மூலம்", lordEn: "Ketu", lordTa: "கேது" },
  20: { index: 20, nameEn: "Purva Ashadha", nameTa: "பூராடம்", lordEn: "Venus", lordTa: "சுக்கிரன்" },
  21: { index: 21, nameEn: "Uttara Ashadha", nameTa: "உத்திராடம்", lordEn: "Sun", lordTa: "சூரியன்" },
  22: { index: 22, nameEn: "Shravana", nameTa: "திருவோணம்", lordEn: "Moon", lordTa: "சந்திரன்" },
  23: { index: 23, nameEn: "Dhanishta", nameTa: "அவிட்டம்", lordEn: "Mars", lordTa: "செவ்வாய்" },
  24: { index: 24, nameEn: "Shatabhisha", nameTa: "சதயம்", lordEn: "Rahu", lordTa: "ராகு" },
  25: { index: 25, nameEn: "Purva Bhadrapada", nameTa: "பூரட்டாதி", lordEn: "Jupiter", lordTa: "குரு" },
  26: { index: 26, nameEn: "Uttara Bhadrapada", nameTa: "உத்திரட்டாதி", lordEn: "Saturn", lordTa: "சனி" },
  27: { index: 27, nameEn: "Revati", nameTa: "ரேவதி", lordEn: "Mercury", lordTa: "புதன்" },
};

// Helper lookup functions
export function getRasiName(sign: number | string, lang: LanguageCode): string {
  if (typeof sign === "string") {
    const parsed = parseInt(sign, 10);
    if (!isNaN(parsed) && RASIS[parsed]) {
      return lang === "ta" ? RASIS[parsed].nameTa : RASIS[parsed].nameEn;
    }
    const match = Object.values(RASIS).find(
      (r) => r.nameEn.toLowerCase() === sign.toLowerCase() || r.nameTa === sign
    );
    if (match) {
      return lang === "ta" ? match.nameTa : match.nameEn;
    }
    return sign;
  }
  const r = RASIS[sign];
  if (!r) return `Sign ${sign}`;
  return lang === "ta" ? r.nameTa : r.nameEn;
}

export function getGrahaName(planetName: string, lang: LanguageCode): string {
  // Normalize key
  const match = Object.keys(GRAHAS).find(
    (k) => k.toLowerCase() === planetName.toLowerCase()
  );
  if (match) {
    return lang === "ta" ? GRAHAS[match].nameTa : GRAHAS[match].nameEn;
  }
  return planetName;
}

export function getGrahaShort(planetName: string, lang: LanguageCode): string {
  const match = Object.keys(GRAHAS).find(
    (k) => k.toLowerCase() === planetName.toLowerCase()
  );
  if (match) {
    return lang === "ta" ? GRAHAS[match].shortTa : GRAHAS[match].shortEn;
  }
  return planetName.slice(0, 2);
}

export function getNakshatraName(nakshatraName: string, lang: LanguageCode): string {
  if (lang === "en") return nakshatraName;
  const match = Object.values(NAKSHATRAS).find(
    (n) => n.nameEn.toLowerCase() === nakshatraName.toLowerCase()
  );
  return match ? match.nameTa : nakshatraName;
}

export function getLordName(lordEn: string, lang: LanguageCode): string {
  if (lang === "en") return lordEn;
  const match = Object.keys(GRAHAS).find(
    (k) => k.toLowerCase() === lordEn.toLowerCase()
  );
  return match ? GRAHAS[match].nameTa : lordEn;
}
