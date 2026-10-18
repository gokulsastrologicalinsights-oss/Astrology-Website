/**
 * Automated End-to-End API Integration Verification
 * Tests the real FastAPI backend against all frontend integration endpoints.
 */

const BASE_URL = "http://127.0.0.1:8000";

async function runTests() {
  console.log("=== Gokul's Astrological Insights - Frontend/Backend API Integration Test ===");
  console.log(`Connecting to: ${BASE_URL}\n`);

  let passed = 0;
  let failed = 0;

  // Test 1: GET /health
  try {
    process.stdout.write("1. Testing GET /health ... ");
    const res = await fetch(`${BASE_URL}/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.status !== "healthy") throw new Error(`Unexpected status: ${data.status}`);
    if (!data.engine?.rust_core_available) throw new Error("Rust core engine not available");
    console.log(`[PASS] Engine: ${data.engine.name} (${data.engine.version})`);
    passed++;
  } catch (err) {
    console.log(`[FAIL] ${err.message}`);
    failed++;
  }

  // Test 2: GET /api/v1/metadata
  try {
    process.stdout.write("2. Testing GET /api/v1/metadata ... ");
    const res = await fetch(`${BASE_URL}/api/v1/metadata`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!Array.isArray(data.supported_ayanamsas) || data.supported_ayanamsas.length === 0) {
      throw new Error("Missing supported ayanamsas");
    }
    if (!Array.isArray(data.supported_house_systems) || data.supported_house_systems.length === 0) {
      throw new Error("Missing supported house systems");
    }
    console.log(`[PASS] Found ${data.supported_ayanamsas.length} ayanamsas, ${data.supported_house_systems.length} house systems`);
    passed++;
  } catch (err) {
    console.log(`[FAIL] ${err.message}`);
    failed++;
  }

  // Test 3: POST /api/v1/horoscope/calculate (Vedic)
  const sampleBirth = {
    birth_date: "1995-10-24",
    birth_time: "14:30:00",
    timezone: "Asia/Kolkata",
    latitude: 13.0827,
    longitude: 80.2707,
    ayanamsa: 0, // Lahiri
    house_system: 2, // Placidus
    include_panchang: true,
    include_outer_planets: true,
  };

  try {
    process.stdout.write("3. Testing POST /api/v1/horoscope/calculate ... ");
    const res = await fetch(`${BASE_URL}/api/v1/horoscope/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(sampleBirth),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!data.ascendant || !data.planets || data.planets.length < 9) {
      throw new Error("Incomplete planetary or ascendant calculation");
    }
    if (!data.panchang || !data.panchang.tithi) {
      throw new Error("Missing panchang data");
    }
    console.log(`[PASS] Ascendant: ${data.ascendant.sign_name} (${data.ascendant.sign_name_tamil}), ${data.planets.length} planets`);
    passed++;
  } catch (err) {
    console.log(`[FAIL] ${err.message}`);
    failed++;
  }

  // Test 4: POST /api/v1/horoscope/dasa (Vimshottari)
  try {
    process.stdout.write("4. Testing POST /api/v1/horoscope/dasa ... ");
    const dasaReq = {
      birth_date: "1995-10-24",
      birth_time: "14:30:00",
      timezone: "Asia/Kolkata",
      latitude: 13.0827,
      longitude: 80.2707,
      depth: 3,
      ayanamsa: 0,
      target_date: "2026-10-17",
    };
    const res = await fetch(`${BASE_URL}/api/v1/horoscope/dasa`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dasaReq),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!data.birth_balance_formatted || !Array.isArray(data.dasa_tree) || data.dasa_tree.length === 0) {
      throw new Error("Invalid dasa hierarchy or balance");
    }
    console.log(`[PASS] Balance: ${data.birth_balance_formatted}, Tree: ${data.dasa_tree.length} Mahadashas`);
    passed++;
  } catch (err) {
    console.log(`[FAIL] ${err.message}`);
    failed++;
  }

  // Test 5: POST /api/v1/horoscope/kp (KP 249)
  try {
    process.stdout.write("5. Testing POST /api/v1/horoscope/kp ... ");
    const kpReq = {
      birth_date: "1995-10-24",
      birth_time: "14:30:00",
      timezone: "Asia/Kolkata",
      latitude: 13.0827,
      longitude: 80.2707,
      ayanamsa: 1, // KP Krishnamurti
      house_system: 2, // Placidus
    };
    const res = await fetch(`${BASE_URL}/api/v1/horoscope/kp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(kpReq),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!Array.isArray(data.planetary_positions) || !Array.isArray(data.cuspal_analysis)) {
      throw new Error("Invalid KP positions or cusps");
    }
    console.log(`[PASS] ${data.planetary_positions.length} KP planets, ${data.cuspal_analysis.length} cusps`);
    passed++;
  } catch (err) {
    console.log(`[FAIL] ${err.message}`);
    failed++;
  }

  // Test 6: Validation error handling on bad inputs
  try {
    process.stdout.write("6. Testing Validation Error Handling (422) ... ");
    const badReq = {
      birth_date: "invalid-date",
      birth_time: "bad-time",
      timezone: "",
      latitude: 150.0, // Invalid lat > 90
      longitude: 80.2707,
    };
    const res = await fetch(`${BASE_URL}/api/v1/horoscope/calculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(badReq),
    });
    if (res.status === 422) {
      const errData = await res.json();
      console.log(`[PASS] Correctly rejected with 422: "${errData.error}"`);
      passed++;
    } else {
      throw new Error(`Expected HTTP 422, got ${res.status}`);
    }
  } catch (err) {
    console.log(`[FAIL] ${err.message}`);
    failed++;
  }

  console.log(`\nResults: ${passed} passed, ${failed} failed out of ${passed + failed} tests.`);
  if (failed > 0) process.exit(1);
}

runTests();
