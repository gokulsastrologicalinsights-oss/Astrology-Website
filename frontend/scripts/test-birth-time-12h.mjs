import assert from "node:assert/strict";
import { parse12HourTimeTo24, parse24To12 } from "../src/lib/formatters.ts";

console.log("=== Testing 12-Hour Birth Time Parser & Formatter ===");

// 1. Morning times (AM)
assert.deepStrictEqual(parse12HourTimeTo24("10:30", "AM"), {
  isValid: true,
  time24: "10:30:00",
});

assert.deepStrictEqual(parse12HourTimeTo24("09:15:30", "AM"), {
  isValid: true,
  time24: "09:15:30",
});

assert.deepStrictEqual(parse12HourTimeTo24("7:05", "AM"), {
  isValid: true,
  time24: "07:05:00",
});

// 2. Midnight (12 AM -> 00:xx:xx)
assert.deepStrictEqual(parse12HourTimeTo24("12:00", "AM"), {
  isValid: true,
  time24: "00:00:00",
});
assert.deepStrictEqual(parse12HourTimeTo24("12:45:10", "AM"), {
  isValid: true,
  time24: "00:45:10",
});

// 3. Noon (12 PM -> 12:xx:xx)
assert.deepStrictEqual(parse12HourTimeTo24("12:00", "PM"), {
  isValid: true,
  time24: "12:00:00",
});
assert.deepStrictEqual(parse12HourTimeTo24("12:30", "PM"), {
  isValid: true,
  time24: "12:30:00",
});

// 4. Afternoon & Evening times (PM)
assert.deepStrictEqual(parse12HourTimeTo24("1:15", "PM"), {
  isValid: true,
  time24: "13:15:00",
});
assert.deepStrictEqual(parse12HourTimeTo24("10:30", "PM"), {
  isValid: true,
  time24: "22:30:00",
});
assert.deepStrictEqual(parse12HourTimeTo24("11:59:59", "PM"), {
  isValid: true,
  time24: "23:59:59",
});

// 5. Normalizing dot as separator (10.30 -> 10:30)
assert.deepStrictEqual(parse12HourTimeTo24("10.30", "AM"), {
  isValid: true,
  time24: "10:30:00",
});

// 6. User typing/pasting AM/PM directly inside the text box
assert.deepStrictEqual(parse12HourTimeTo24("10:30 PM", "AM"), {
  isValid: true,
  time24: "22:30:00",
});
assert.deepStrictEqual(parse12HourTimeTo24("08:15 AM", "PM"), {
  isValid: true,
  time24: "08:15:00",
});

// 7. Validation rejects out-of-range hours, minutes, seconds
assert.strictEqual(parse12HourTimeTo24("00:30", "AM").isValid, false); // 0 is invalid in 12h
assert.strictEqual(parse12HourTimeTo24("13:00", "PM").isValid, false); // 13 is invalid in 12h
assert.strictEqual(parse12HourTimeTo24("10:60", "AM").isValid, false); // 60 is invalid minute
assert.strictEqual(parse12HourTimeTo24("10:30:75", "PM").isValid, false); // 75 is invalid second
assert.strictEqual(parse12HourTimeTo24("", "AM").isValid, false); // empty
assert.strictEqual(parse12HourTimeTo24("invalid", "AM").isValid, false); // gibberish

// 8. Testing parse24To12
assert.deepStrictEqual(parse24To12("10:30:00"), { time12: "10:30", period: "AM" });
assert.deepStrictEqual(parse24To12("22:30:00"), { time12: "10:30", period: "PM" });
assert.deepStrictEqual(parse24To12("00:00:00"), { time12: "12:00", period: "AM" });
assert.deepStrictEqual(parse24To12("12:00:00"), { time12: "12:00", period: "PM" });
assert.deepStrictEqual(parse24To12("13:15:45"), { time12: "01:15:45", period: "PM" });

console.log("All 12-hour birth time tests PASSED successfully!");
