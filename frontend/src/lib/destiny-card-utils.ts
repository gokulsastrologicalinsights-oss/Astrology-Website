/**
 * Gokul's Astrological Insights - Destiny Card Utilities
 * Extracts verified astrological identity data from FullHoroscopeResult
 * and renders high-resolution, exportable share cards on HTML5 Canvas.
 */

import type { FullHoroscopeResult } from "./types.ts";
import type { LanguageCode } from "./translations.ts";
import { getRasiName, getNakshatraName, getLordName } from "./translations.ts";

export interface DestinyCardData {
  isVerified: boolean;
  personName: string;
  // Ascendant / Lagna
  ascendantSignEn: string;
  ascendantSignTa: string;
  ascendantDegree: number;
  ascendantNakshatraEn?: string;
  ascendantNakshatraTa?: string;
  ascendantPada?: number;
  // Moon Sign / Chandra Rasi
  moonSignEn: string;
  moonSignTa: string;
  moonDegree: number;
  // Birth Star / Janma Nakshatra
  nakshatraEn: string;
  nakshatraTa: string;
  pada: number;
  starLordEn: string;
  starLordTa: string;
  // Mahadasha
  dasaLordEn: string;
  dasaLordTa: string;
  antardashaLordEn?: string;
  antardashaLordTa?: string;
  isCurrentDasa: boolean;
  // Optional Sun Sign
  sunSignEn?: string;
  sunSignTa?: string;
  sunDegree?: number;
  // Metadata & Verification
  ayanamsaName: string;
  calculationEngine: string;
  birthDateDisplay?: string;
  julianDayUt1?: number;
}

/**
 * Extracts and strictly verifies core astrological identity from authoritative calculation results.
 * Returns null if mandatory data (Ascendant, Moon Sign, Nakshatra, Pada, Dasa) is missing or incomplete.
 */
export function extractDestinyCardData(
  result: FullHoroscopeResult | null,
  includeBirthDate: boolean = false
): DestinyCardData | null {
  if (!result || !result.horoscope) {
    return null;
  }

  const { horoscope, dasa, clientInputs } = result;

  // 1. Verify Ascendant (Lagna)
  const ascendant = horoscope.ascendant;
  if (!ascendant || !ascendant.sign_name || ascendant.sign_index < 1 || ascendant.sign_index > 12) {
    return null;
  }

  const ascSignEn = ascendant.sign_name;
  const ascSignTa = ascendant.sign_name_tamil || getRasiName(ascendant.sign_index, "ta");
  const ascDeg = ascendant.degree_in_sign ?? 0;
  const ascNakEn = ascendant.nakshatra?.name;
  const ascNakTa = ascNakEn ? getNakshatraName(ascNakEn, "ta") : undefined;
  const ascPada = ascendant.nakshatra?.pada;

  // 2. Verify Moon Sign & Janma Nakshatra
  const moonPlanet = horoscope.planets?.find(
    (p) => p.name.toLowerCase() === "moon" || p.name.toLowerCase() === "chandra"
  );

  if (!moonPlanet || !moonPlanet.sign_name || moonPlanet.sign_index < 1 || moonPlanet.sign_index > 12) {
    return null;
  }

  const moonSignEn = moonPlanet.sign_name;
  const moonSignTa = moonPlanet.sign_name_tamil || getRasiName(moonPlanet.sign_index, "ta");
  const moonDeg = moonPlanet.degree_in_sign ?? 0;

  // Nakshatra and Pada: check moonPlanet.nakshatra first, then fallback to dasa.nakshatra
  const nakDetail = moonPlanet.nakshatra || dasa?.nakshatra;
  if (!nakDetail || !nakDetail.name || typeof nakDetail.pada !== "number") {
    return null;
  }

  const nakEn = nakDetail.name;
  const nakTa = getNakshatraName(nakEn, "ta");
  const pada = nakDetail.pada;
  const starLordEn = nakDetail.lord || getLordName(nakEn, "en");
  const starLordTa = getLordName(starLordEn, "ta");

  // 3. Verify Active Mahadasha or Birth Mahadasha
  let dasaLordEn = "";
  let antardashaLordEn: string | undefined = undefined;
  let isCurrentDasa = false;

  if (dasa?.active_period?.mahadasha) {
    dasaLordEn = dasa.active_period.mahadasha;
    antardashaLordEn = dasa.active_period.antardasha;
    isCurrentDasa = true;
  } else if (dasa?.birth_dasa_lord) {
    dasaLordEn = dasa.birth_dasa_lord;
    isCurrentDasa = false;
  } else if (dasa?.dasa_tree?.[0]?.lord) {
    dasaLordEn = dasa.dasa_tree[0].lord;
    isCurrentDasa = false;
  } else {
    // If dasa is completely missing, we do not fabricate random dasa
    return null;
  }

  const dasaLordTa = getLordName(dasaLordEn, "ta");
  const antardashaLordTa = antardashaLordEn ? getLordName(antardashaLordEn, "ta") : undefined;

  // 4. Optional Sun Sign
  const sunPlanet = horoscope.planets?.find(
    (p) => p.name.toLowerCase() === "sun" || p.name.toLowerCase() === "surya"
  );
  const sunSignEn = sunPlanet?.sign_name;
  const sunSignTa = sunPlanet ? (sunPlanet.sign_name_tamil || getRasiName(sunPlanet.sign_index, "ta")) : undefined;
  const sunDegree = sunPlanet?.degree_in_sign;

  // 5. Person Name & Metadata
  const rawName = clientInputs?.fullName?.trim();
  const personName = rawName && rawName.length > 0 ? rawName : "";

  // 6. Birth Date formatting (only if explicitly requested by user)
  let birthDateDisplay: string | undefined = undefined;
  if (includeBirthDate && clientInputs?.birthDate) {
    birthDateDisplay = clientInputs.birthDate;
  }

  const ayanamsaName = horoscope.metadata?.ayanamsa_name || "Lahiri";
  const calculationEngine = horoscope.metadata?.engine || "XALEN Astronomical Engine";
  const julianDayUt1 = horoscope.metadata?.julian_day_ut1;

  return {
    isVerified: true,
    personName,
    ascendantSignEn: ascSignEn,
    ascendantSignTa: ascSignTa,
    ascendantDegree: ascDeg,
    ascendantNakshatraEn: ascNakEn,
    ascendantNakshatraTa: ascNakTa,
    ascendantPada: ascPada,
    moonSignEn,
    moonSignTa,
    moonDegree: moonDeg,
    nakshatraEn: nakEn,
    nakshatraTa: nakTa,
    pada,
    starLordEn,
    starLordTa,
    dasaLordEn,
    dasaLordTa,
    antardashaLordEn,
    antardashaLordTa,
    isCurrentDasa,
    sunSignEn,
    sunSignTa,
    sunDegree,
    ayanamsaName,
    calculationEngine,
    birthDateDisplay,
    julianDayUt1,
  };
}

/**
 * Formats a degree decimal into compact degrees and arc-minutes (e.g. 14° 32')
 */
export function formatCompactDeg(deg: number): string {
  const d = Math.floor(deg);
  const m = Math.floor((deg - d) * 60);
  return `${d}° ${String(m).padStart(2, "0")}'`;
}

/**
 * Draws rounded rectangle path on Canvas 2D context
 */
function drawRoundedRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number
) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

/**
 * Renders the Destiny Card onto an HTML5 Canvas at 1200x1500 resolution.
 */
export function renderDestinyCardToCanvas(
  canvas: HTMLCanvasElement,
  data: DestinyCardData,
  lang: LanguageCode = "en"
): void {
  const width = 1200;
  const height = 1500;
  canvas.width = width;
  canvas.height = height;

  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const isTa = lang === "ta";

  // 1. Deep Cosmic Obsidian Background
  const bgGrad = ctx.createLinearGradient(0, 0, 0, height);
  bgGrad.addColorStop(0, "#0E0501");
  bgGrad.addColorStop(0.3, "#1C0B02");
  bgGrad.addColorStop(0.7, "#280F04");
  bgGrad.addColorStop(1, "#090300");
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, width, height);

  // 2. Warm Radial Light Aura from top center
  const radialAura = ctx.createRadialGradient(width / 2, 220, 20, width / 2, 220, 600);
  radialAura.addColorStop(0, "rgba(229, 169, 60, 0.22)");
  radialAura.addColorStop(0.5, "rgba(180, 80, 10, 0.08)");
  radialAura.addColorStop(1, "rgba(0, 0, 0, 0)");
  ctx.fillStyle = radialAura;
  ctx.fillRect(0, 0, width, height);

  // 3. Deterministic subtle stars (no Math.random in draw cycle)
  ctx.fillStyle = "rgba(245, 206, 80, 0.4)";
  const starCoords = [
    [100, 120, 1.5], [1100, 180, 2], [220, 340, 1], [980, 400, 1.5],
    [140, 600, 1.2], [1050, 750, 1.8], [90, 950, 1.4], [1110, 1100, 2],
    [180, 1300, 1.5], [1020, 1350, 1.2], [300, 140, 1], [900, 220, 1.4],
    [500, 80, 1.5], [700, 90, 1.2], [80, 1200, 1], [1120, 500, 1.6],
    [350, 480, 1.2], [850, 650, 1.5], [150, 780, 1.1], [1040, 920, 1.3]
  ];
  starCoords.forEach(([sx, sy, sr]) => {
    ctx.beginPath();
    ctx.arc(sx, sy, sr, 0, Math.PI * 2);
    ctx.fill();
  });

  // 4. Subtle Concentric Yantra Watermarks (Center)
  ctx.save();
  ctx.strokeStyle = "rgba(212, 165, 42, 0.05)";
  ctx.lineWidth = 1.5;
  [180, 260, 340, 420].forEach((rad) => {
    ctx.beginPath();
    ctx.arc(width / 2, 750, rad, 0, Math.PI * 2);
    ctx.stroke();
  });
  ctx.restore();

  // 5. Ornate Double Gold Border
  // Outer Border
  ctx.strokeStyle = "#C8961A";
  ctx.lineWidth = 4;
  drawRoundedRect(ctx, 36, 36, width - 72, height - 72, 24);
  ctx.stroke();

  // Inner Border
  ctx.strokeStyle = "rgba(212, 165, 42, 0.45)";
  ctx.lineWidth = 1.5;
  drawRoundedRect(ctx, 48, 48, width - 96, height - 96, 18);
  ctx.stroke();

  // Corner Flourishes (4 corners)
  const drawCornerFlourish = (cx: number, cy: number, rot: number) => {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(rot);
    ctx.strokeStyle = "#F5CE50";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(12, 12);
    ctx.lineTo(44, 12);
    ctx.moveTo(12, 12);
    ctx.lineTo(12, 44);
    ctx.stroke();

    ctx.fillStyle = "#F5CE50";
    ctx.beginPath();
    ctx.arc(22, 22, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  };

  drawCornerFlourish(48, 48, 0); // Top Left
  drawCornerFlourish(width - 48, 48, Math.PI / 2); // Top Right
  drawCornerFlourish(width - 48, height - 48, Math.PI); // Bottom Right
  drawCornerFlourish(48, height - 48, -Math.PI / 2); // Bottom Left

  // 6. Header Emblem: Sacred ॐ / ௐ
  const emblemX = width / 2;
  const emblemY = 145;

  ctx.save();
  // Halo ring
  ctx.beginPath();
  ctx.arc(emblemX, emblemY, 44, 0, Math.PI * 2);
  ctx.fillStyle = "rgba(212, 165, 42, 0.12)";
  ctx.fill();
  ctx.strokeStyle = "rgba(245, 206, 80, 0.75)";
  ctx.lineWidth = 2;
  ctx.stroke();

  // Sacred glyph
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = "#F5CE50";
  ctx.font = isTa
    ? "bold 44px 'Noto Serif Tamil', 'Latha', 'Vijaya', serif"
    : "bold 48px 'Cormorant Garamond', 'Cinzel', serif";
  ctx.fillText(isTa ? "ௐ" : "ॐ", emblemX, emblemY + 2);
  ctx.restore();

  // 7. Brand Title & Header
  ctx.textAlign = "center";
  ctx.textBaseline = "top";

  // Sub-brand
  ctx.font = "600 16px 'Jost', 'Inter', sans-serif";
  ctx.fillStyle = "#E5A93C";
  ctx.letterSpacing = "3px";
  ctx.fillText(
    isTa ? "கோகுலின் ஜோதிட நுண்ணறிவு · அதிகாரப்பூர்வ வேத ஜாதகம்" : "GOKUL'S ASTROLOGICAL INSIGHTS · VEDIC EXCELLENCE",
    width / 2,
    215
  );

  // Main Card Title
  ctx.font = "bold 38px 'Cormorant Garamond', 'Cinzel', 'Noto Serif Tamil', serif";
  ctx.fillStyle = "#FFF8EE";
  ctx.fillText(isTa ? "வேத விதி அட்டை" : "VEDIC DESTINY CARD", width / 2, 245);

  // Tapering Gold Line with Diamond
  const drawDivider = (yPos: number) => {
    ctx.save();
    const gradLine = ctx.createLinearGradient(160, yPos, width - 160, yPos);
    gradLine.addColorStop(0, "rgba(212, 165, 42, 0)");
    gradLine.addColorStop(0.3, "rgba(212, 165, 42, 0.7)");
    gradLine.addColorStop(0.5, "rgba(245, 206, 80, 1)");
    gradLine.addColorStop(0.7, "rgba(212, 165, 42, 0.7)");
    gradLine.addColorStop(1, "rgba(212, 165, 42, 0)");
    ctx.strokeStyle = gradLine;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(160, yPos);
    ctx.lineTo(width - 160, yPos);
    ctx.stroke();

    // Central diamond
    ctx.fillStyle = "#F5CE50";
    ctx.beginPath();
    ctx.moveTo(width / 2, yPos - 5);
    ctx.lineTo(width / 2 + 5, yPos);
    ctx.lineTo(width / 2, yPos + 5);
    ctx.lineTo(width / 2 - 5, yPos);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  };

  drawDivider(300);

  // 8. Person's Name & Profile Section
  const displayName = data.personName && data.personName.trim().length > 0
    ? data.personName.trim()
    : isTa ? "வேத சாதகர்" : "Vedic Seeker";

  ctx.font = "bold 44px 'Cormorant Garamond', 'Cinzel', 'Noto Serif Tamil', serif";
  ctx.fillStyle = "#F5CE50";
  ctx.fillText(displayName, width / 2, 325);

  let curY = 385;
  if (data.birthDateDisplay) {
    ctx.font = "500 17px 'Jost', 'Inter', sans-serif";
    ctx.fillStyle = "#C8B496";
    ctx.fillText(`${isTa ? "பிறந்த தேதி" : "Date of Birth"}: ${data.birthDateDisplay}`, width / 2, curY);
    curY += 32;
  }

  drawDivider(curY);

  // 9. Core Astrological Grid: 4 Prominent Pillar Cards
  const gridTop = curY + 36;
  const colWidth = 510;
  const cardHeight = 220;
  const leftColX = 75;
  const rightColX = width - 75 - colWidth;
  const row1Y = gridTop;
  const row2Y = gridTop + cardHeight + 24;

  interface PillarConfig {
    x: number;
    y: number;
    icon: string;
    label: string;
    mainValue: string;
    subValue1: string;
    subValue2?: string;
    accentColor: string;
  }

  const pillars: PillarConfig[] = [
    // 1. Ascendant / Lagna
    {
      x: leftColX,
      y: row1Y,
      icon: "⚡",
      label: isTa ? "லக்னம் (உதய ராசி)" : "ASCENDANT (LAGNA)",
      mainValue: isTa ? data.ascendantSignTa : data.ascendantSignEn,
      subValue1: `${isTa ? "பாகை" : "Degree"}: ${formatCompactDeg(data.ascendantDegree)}`,
      subValue2: data.ascendantNakshatraEn
        ? `${isTa ? "நட்சத்திரம்" : "Star"}: ${isTa ? data.ascendantNakshatraTa : data.ascendantNakshatraEn}${
            data.ascendantPada ? ` (${data.ascendantPada})` : ""
          }`
        : undefined,
      accentColor: "#FF7A1A",
    },
    // 2. Moon Sign / Chandra Rasi
    {
      x: rightColX,
      y: row1Y,
      icon: "☽",
      label: isTa ? "சந்திர ராசி (ராசி)" : "MOON SIGN (RASI)",
      mainValue: isTa ? data.moonSignTa : data.moonSignEn,
      subValue1: `${isTa ? "பாகை" : "Degree"}: ${formatCompactDeg(data.moonDegree)}`,
      subValue2: isTa ? "மனோகாரகன் · சந்திர ஆதிக்கம்" : "Mind & Consciousness · Chandra",
      accentColor: "#C8D0E0",
    },
    // 3. Birth Star / Janma Nakshatra & Pada
    {
      x: leftColX,
      y: row2Y,
      icon: "✦",
      label: isTa ? "ஜன்ம நட்சத்திரம் & பாதம்" : "BIRTH STAR (NAKSHATRA)",
      mainValue: `${isTa ? data.nakshatraTa : data.nakshatraEn} - ${isTa ? `பாதம் ${data.pada}` : `Pada ${data.pada}`}`,
      subValue1: `${isTa ? "நட்சத்திர அதிபதி" : "Star Lord"}: ${isTa ? data.starLordTa : data.starLordEn}`,
      subValue2: isTa ? "கர்ம மற்றும் பிறவி விண்மீன்" : "Karmic Destiny Constellation",
      accentColor: "#F5CE50",
    },
    // 4. Mahadasha
    {
      x: rightColX,
      y: row2Y,
      icon: "⌛",
      label: data.isCurrentDasa
        ? (isTa ? "தற்போதைய மகா தசா" : "ACTIVE MAHADASHA")
        : (isTa ? "ஜன்ம மகா தசா" : "BIRTH MAHADASHA"),
      mainValue: `${isTa ? data.dasaLordTa : data.dasaLordEn} ${isTa ? "தசா" : "Dasa"}`,
      subValue1: data.antardashaLordEn
        ? `${isTa ? "அந்தர்தசா" : "Antardasha"}: ${isTa ? data.antardashaLordTa : data.antardashaLordEn}`
        : (isTa ? "விம்சோத்தரி தசா இயக்கம்" : "Vimshottari Planetary Period"),
      subValue2: isTa ? "காலச்சக்கர ஆளுகை" : "Vedic Chronocrator Cycle",
      accentColor: "#EEC040",
    },
  ];

  pillars.forEach((p) => {
    ctx.save();
    // Card Background Box
    const cardBg = ctx.createLinearGradient(p.x, p.y, p.x + colWidth, p.y + cardHeight);
    cardBg.addColorStop(0, "rgba(36, 16, 6, 0.85)");
    cardBg.addColorStop(1, "rgba(22, 9, 3, 0.95)");
    ctx.fillStyle = cardBg;
    drawRoundedRect(ctx, p.x, p.y, colWidth, cardHeight, 14);
    ctx.fill();

    // Card Border
    ctx.strokeStyle = "rgba(212, 165, 42, 0.38)";
    ctx.lineWidth = 1.5;
    drawRoundedRect(ctx, p.x, p.y, colWidth, cardHeight, 14);
    ctx.stroke();

    // Top subtle highlight line
    ctx.strokeStyle = p.accentColor;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(p.x + 24, p.y);
    ctx.lineTo(p.x + colWidth - 24, p.y);
    ctx.stroke();

    // Header Label & Icon
    ctx.textAlign = "left";
    ctx.textBaseline = "top";

    // Icon
    ctx.font = "22px sans-serif";
    ctx.fillStyle = p.accentColor;
    ctx.fillText(p.icon, p.x + 24, p.y + 24);

    // Label
    ctx.font = "600 13px 'Jost', 'Inter', sans-serif";
    ctx.fillStyle = "#D4AF37";
    ctx.letterSpacing = "1.5px";
    ctx.fillText(p.label, p.x + 58, p.y + 27);

    // Main Value
    ctx.font = "bold 30px 'Cormorant Garamond', 'Cinzel', 'Noto Serif Tamil', serif";
    ctx.fillStyle = "#FFF8EE";
    ctx.fillText(p.mainValue, p.x + 24, p.y + 70);

    // Secondary line 1
    ctx.font = "500 16px 'Jost', 'Inter', sans-serif";
    ctx.fillStyle = "#F0D5AA";
    ctx.fillText(p.subValue1, p.x + 24, p.y + 124);

    // Secondary line 2
    if (p.subValue2) {
      ctx.font = "400 14px 'Jost', 'Inter', sans-serif";
      ctx.fillStyle = "#A89078";
      ctx.fillText(p.subValue2, p.x + 24, p.y + 158);
    }
    ctx.restore();
  });

  // 10. Auxiliary Banner: Surya Rasi / Sun Sign & Ayanamsa
  const bannerY = row2Y + cardHeight + 28;
  const bannerWidth = width - 150;
  const bannerHeight = 110;
  const bannerX = 75;

  ctx.save();
  const bannerBg = ctx.createLinearGradient(bannerX, bannerY, bannerX + bannerWidth, bannerY + bannerHeight);
  bannerBg.addColorStop(0, "rgba(42, 18, 5, 0.7)");
  bannerBg.addColorStop(0.5, "rgba(60, 24, 6, 0.85)");
  bannerBg.addColorStop(1, "rgba(42, 18, 5, 0.7)");
  ctx.fillStyle = bannerBg;
  drawRoundedRect(ctx, bannerX, bannerY, bannerWidth, bannerHeight, 14);
  ctx.fill();

  ctx.strokeStyle = "rgba(212, 165, 42, 0.35)";
  ctx.lineWidth = 1.2;
  drawRoundedRect(ctx, bannerX, bannerY, bannerWidth, bannerHeight, 14);
  ctx.stroke();

  // Content inside Banner: 2 columns
  // Left side: Sun Sign
  ctx.textAlign = "left";
  ctx.textBaseline = "middle";

  const sunSignText = data.sunSignEn
    ? `${isTa ? data.sunSignTa : data.sunSignEn}${
        typeof data.sunDegree === "number" ? ` (${formatCompactDeg(data.sunDegree)})` : ""
      }`
    : "—";

  ctx.font = "600 13px 'Jost', 'Inter', sans-serif";
  ctx.fillStyle = "#D4AF37";
  ctx.fillText(`☉  ${isTa ? "சூரிய ராசி (ஆன்ம காரகன்)" : "SUN SIGN (SURYA RASI)"}`, bannerX + 28, bannerY + 38);

  ctx.font = "bold 24px 'Cormorant Garamond', 'Cinzel', 'Noto Serif Tamil', serif";
  ctx.fillStyle = "#FFF8EE";
  ctx.fillText(sunSignText, bannerX + 28, bannerY + 75);

  // Right side: Ayanamsa & Frame
  ctx.textAlign = "right";
  ctx.font = "600 13px 'Jost', 'Inter', sans-serif";
  ctx.fillStyle = "#D4AF37";
  ctx.fillText(`⚙  ${isTa ? "கணிப்பு முறை & அயனாம்சம்" : "CALCULATION AYANAMSA"}`, bannerX + bannerWidth - 28, bannerY + 38);

  ctx.font = "500 19px 'Jost', 'Inter', sans-serif";
  ctx.fillStyle = "#F5CE50";
  ctx.fillText(`${data.ayanamsaName} (${isTa ? "நிராயன முறை" : "Nirayana Sidereal"})`, bannerX + bannerWidth - 28, bannerY + 75);
  ctx.restore();

  // 11. Auspicious Blessing / Sacred Verse Watermark
  const verseY = bannerY + bannerHeight + 50;
  ctx.save();
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.font = "italic 18px 'Cormorant Garamond', 'Noto Serif Tamil', Georgia, serif";
  ctx.fillStyle = "rgba(240, 213, 170, 0.65)";
  const sacredVerse = isTa
    ? "“யாதும் ஊரே யாவரும் கேளிர் · நன்மை தீமை பிறர்தர வாரா”"
    : "“सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः · May cosmic harmony illuminate your path”";
  ctx.fillText(sacredVerse, width / 2, verseY);
  ctx.restore();

  // 12. Footer Authenticity Seal & Verification Badge
  const footerLineY = height - 165;
  drawDivider(footerLineY);

  ctx.textAlign = "center";
  ctx.textBaseline = "top";

  // Verification Seal
  ctx.font = "bold 15px 'Jost', 'Inter', sans-serif";
  ctx.fillStyle = "#22C55E";
  ctx.fillText(
    isTa
      ? "✓ XALEN துல்லிய வானியல் எபிமெரிஸ் கணிப்பு மூலம் சரிபார்க்கப்பட்டது"
      : "✓ VERIFIED CALCULATION · XALEN HIGH-PRECISION EPHEMERIS ENGINE",
    width / 2,
    footerLineY + 22
  );

  // Privacy notice
  ctx.font = "400 13px 'Jost', 'Inter', sans-serif";
  ctx.fillStyle = "#A89078";
  ctx.fillText(
    isTa
      ? "துல்லிய இருப்பிட அட்ச/தீர்க்க ரேகைகள் தனியுரிமை கருதி பாதுகாக்கப்பட்டுள்ளன · அதிகாரப்பூர்வ வேத ஜாதக சாரம்"
      : "Sensitive coordinates protected for user privacy · Official Verified Vedic Horoscope Identity",
    width / 2,
    footerLineY + 50
  );

  // Web branding
  ctx.font = "600 14px 'Jost', 'Inter', sans-serif";
  ctx.fillStyle = "#E5A93C";
  ctx.fillText("gokul-astrology.com", width / 2, footerLineY + 80);
}

/**
 * Triggers a direct client-side PNG download from the rendered Destiny Card.
 */
export async function downloadDestinyCardPng(
  data: DestinyCardData,
  lang: LanguageCode = "en"
): Promise<void> {
  const canvas = document.createElement("canvas");
  renderDestinyCardToCanvas(canvas, data, lang);

  return new Promise<void>((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error("Failed to generate Destiny Card blob"));
        return;
      }
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      const safeName = (data.personName || "Vedic-Seeker")
        .trim()
        .replace(/[^a-zA-Z0-9\u0B80-\u0BFF_-]/g, "_");
      link.download = `Destiny-Card-${safeName}-${lang}.png`;
      link.href = url;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      resolve();
    }, "image/png");
  });
}
