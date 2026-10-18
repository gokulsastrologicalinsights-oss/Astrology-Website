import { HoroscopeResponse, PlanetInfo } from "./types";

/**
 * Builds a derived Navamsa (D9) HoroscopeResponse.
 * If horoscope.varga_d1_d9?.d9_chart is already available from backend, uses that.
 * Otherwise, calculates accurate classical Navamsa positions (BPHS Ch. 6) for all planets and ascendant.
 */
export function buildNavamsaHoroscope(horoscope: HoroscopeResponse): HoroscopeResponse {
  if (horoscope.varga_d1_d9?.d9_chart) {
    return horoscope.varga_d1_d9.d9_chart as unknown as HoroscopeResponse;
  }

  const computeD9Position = (signIndex: number, degInSign: number) => {
    // Navamsa sign start based on element:
    // Fire (1, 5, 9): 1 (Mesham)
    // Earth (2, 6, 10): 10 (Makaram)
    // Air (3, 7, 11): 7 (Thulam)
    // Water (4, 8, 12): 4 (Katakam)
    const element = signIndex % 4;
    let startSign = 1;
    if (element === 1) startSign = 1;
    else if (element === 2) startSign = 10;
    else if (element === 3) startSign = 7;
    else startSign = 4;

    const padaIndex = Math.min(8, Math.max(0, Math.floor(degInSign / (30 / 9))));
    const d9SignIndex = ((startSign - 1 + padaIndex) % 12) + 1;
    const d9Deg = (degInSign % (30 / 9)) * 9;
    return { signIndex: d9SignIndex, deg: d9Deg };
  };

  const ascD9 = computeD9Position(
    horoscope.ascendant.sign_index,
    horoscope.ascendant.degree_in_sign
  );

  const d9Planets: PlanetInfo[] = horoscope.planets.map((p) => {
    const pD9 = computeD9Position(p.sign_index, p.degree_in_sign);
    return {
      ...p,
      sign_index: pD9.signIndex,
      degree_in_sign: pD9.deg,
      longitude: (pD9.signIndex - 1) * 30 + pD9.deg,
    };
  });

  return {
    ...horoscope,
    ascendant: {
      ...horoscope.ascendant,
      sign_index: ascD9.signIndex,
      degree_in_sign: ascD9.deg,
      degree: (ascD9.signIndex - 1) * 30 + ascD9.deg,
    },
    planets: d9Planets,
  };
}

/**
 * Builds a derived Bhava Chakra (பாவக சக்கரம்) HoroscopeResponse.
 * Places each planet in the zodiac sign corresponding to its calculated bhava (house 1-12)
 * relative to the Ascendant sign.
 */
export function buildBhavaHoroscope(horoscope: HoroscopeResponse): HoroscopeResponse {
  const ascSign = horoscope.ascendant.sign_index;
  const bhavaPlanets: PlanetInfo[] = horoscope.planets.map((p) => {
    const houseNum =
      p.house && p.house >= 1 && p.house <= 12
        ? p.house
        : ((p.sign_index - ascSign + 12) % 12) + 1;
    const bhavaSignIndex = ((ascSign - 1 + (houseNum - 1)) % 12) + 1;
    return {
      ...p,
      sign_index: bhavaSignIndex,
    };
  });

  return {
    ...horoscope,
    planets: bhavaPlanets,
  };
}
