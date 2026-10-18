/**
 * Curated list of major Indian and International cities with verified coordinates and IANA time zones.
 * Serves as an instant offline/pre-populated dataset for the birth place search.
 */

export interface PredefinedCity {
  name: string;
  stateOrCountry: string;
  latitude: number;
  longitude: number;
  timezone: string;
}

export const MAJOR_CITIES: PredefinedCity[] = [
  // Tamil Nadu & South India
  { name: "Chennai", stateOrCountry: "Tamil Nadu, India", latitude: 13.0827, longitude: 80.2707, timezone: "Asia/Kolkata" },
  { name: "Madurai", stateOrCountry: "Tamil Nadu, India", latitude: 9.9252, longitude: 78.1198, timezone: "Asia/Kolkata" },
  { name: "Coimbatore", stateOrCountry: "Tamil Nadu, India", latitude: 11.0168, longitude: 76.9558, timezone: "Asia/Kolkata" },
  { name: "Tiruchirappalli", stateOrCountry: "Tamil Nadu, India", latitude: 10.7905, longitude: 78.7047, timezone: "Asia/Kolkata" },
  { name: "Salem", stateOrCountry: "Tamil Nadu, India", latitude: 11.6643, longitude: 78.1460, timezone: "Asia/Kolkata" },
  { name: "Tirunelveli", stateOrCountry: "Tamil Nadu, India", latitude: 8.7139, longitude: 77.7567, timezone: "Asia/Kolkata" },
  { name: "Erode", stateOrCountry: "Tamil Nadu, India", latitude: 11.3410, longitude: 77.7172, timezone: "Asia/Kolkata" },
  { name: "Vellore", stateOrCountry: "Tamil Nadu, India", latitude: 12.9165, longitude: 79.1325, timezone: "Asia/Kolkata" },
  { name: "Thanjavur", stateOrCountry: "Tamil Nadu, India", latitude: 10.7870, longitude: 79.1378, timezone: "Asia/Kolkata" },
  { name: "Kanchipuram", stateOrCountry: "Tamil Nadu, India", latitude: 12.8342, longitude: 79.7036, timezone: "Asia/Kolkata" },
  { name: "Dindigul", stateOrCountry: "Tamil Nadu, India", latitude: 10.3673, longitude: 77.9803, timezone: "Asia/Kolkata" },
  { name: "Nagercoil", stateOrCountry: "Tamil Nadu, India", latitude: 8.1833, longitude: 77.4119, timezone: "Asia/Kolkata" },
  { name: "Kumbakonam", stateOrCountry: "Tamil Nadu, India", latitude: 10.9602, longitude: 79.3845, timezone: "Asia/Kolkata" },
  { name: "Puducherry", stateOrCountry: "India", latitude: 11.9416, longitude: 79.8083, timezone: "Asia/Kolkata" },
  { name: "Bengaluru", stateOrCountry: "Karnataka, India", latitude: 12.9716, longitude: 77.5946, timezone: "Asia/Kolkata" },
  { name: "Mysuru", stateOrCountry: "Karnataka, India", latitude: 12.2958, longitude: 76.6394, timezone: "Asia/Kolkata" },
  { name: "Hyderabad", stateOrCountry: "Telangana, India", latitude: 17.3850, longitude: 78.4867, timezone: "Asia/Kolkata" },
  { name: "Visakhapatnam", stateOrCountry: "Andhra Pradesh, India", latitude: 17.6868, longitude: 83.2185, timezone: "Asia/Kolkata" },
  { name: "Vijayawada", stateOrCountry: "Andhra Pradesh, India", latitude: 16.5062, longitude: 80.6480, timezone: "Asia/Kolkata" },
  { name: "Thiruvananthapuram", stateOrCountry: "Kerala, India", latitude: 8.5241, longitude: 76.9366, timezone: "Asia/Kolkata" },
  { name: "Kochi", stateOrCountry: "Kerala, India", latitude: 9.9312, longitude: 76.2673, timezone: "Asia/Kolkata" },
  { name: "Kozhikode", stateOrCountry: "Kerala, India", latitude: 11.2588, longitude: 75.7804, timezone: "Asia/Kolkata" },

  // Pan-India Metros & Major Centers
  { name: "Mumbai", stateOrCountry: "Maharashtra, India", latitude: 19.0760, longitude: 72.8777, timezone: "Asia/Kolkata" },
  { name: "Pune", stateOrCountry: "Maharashtra, India", latitude: 18.5204, longitude: 73.8567, timezone: "Asia/Kolkata" },
  { name: "Nagpur", stateOrCountry: "Maharashtra, India", latitude: 21.1458, longitude: 79.0882, timezone: "Asia/Kolkata" },
  { name: "New Delhi", stateOrCountry: "Delhi, India", latitude: 28.6139, longitude: 77.2090, timezone: "Asia/Kolkata" },
  { name: "Kolkata", stateOrCountry: "West Bengal, India", latitude: 22.5726, longitude: 88.3639, timezone: "Asia/Kolkata" },
  { name: "Ahmedabad", stateOrCountry: "Gujarat, India", latitude: 23.0225, longitude: 72.5714, timezone: "Asia/Kolkata" },
  { name: "Surat", stateOrCountry: "Gujarat, India", latitude: 21.1702, longitude: 72.8311, timezone: "Asia/Kolkata" },
  { name: "Jaipur", stateOrCountry: "Rajasthan, India", latitude: 26.9124, longitude: 75.7873, timezone: "Asia/Kolkata" },
  { name: "Lucknow", stateOrCountry: "Uttar Pradesh, India", latitude: 26.8467, longitude: 80.9462, timezone: "Asia/Kolkata" },
  { name: "Varanasi", stateOrCountry: "Uttar Pradesh, India", latitude: 25.3176, longitude: 82.9739, timezone: "Asia/Kolkata" },
  { name: "Patna", stateOrCountry: "Bihar, India", latitude: 25.5941, longitude: 85.1376, timezone: "Asia/Kolkata" },
  { name: "Bhopal", stateOrCountry: "Madhya Pradesh, India", latitude: 23.2599, longitude: 77.4126, timezone: "Asia/Kolkata" },
  { name: "Indore", stateOrCountry: "Madhya Pradesh, India", latitude: 22.7196, longitude: 75.8577, timezone: "Asia/Kolkata" },
  { name: "Chandigarh", stateOrCountry: "India", latitude: 30.7333, longitude: 76.7794, timezone: "Asia/Kolkata" },

  // Global Diaspora & International Cities
  { name: "Singapore", stateOrCountry: "Singapore", latitude: 1.3521, longitude: 103.8198, timezone: "Asia/Singapore" },
  { name: "Kuala Lumpur", stateOrCountry: "Malaysia", latitude: 3.1390, longitude: 101.6869, timezone: "Asia/Kuala_Lumpur" },
  { name: "Penang", stateOrCountry: "Malaysia", latitude: 5.4141, longitude: 100.3288, timezone: "Asia/Kuala_Lumpur" },
  { name: "Colombo", stateOrCountry: "Sri Lanka", latitude: 6.9271, longitude: 79.8612, timezone: "Asia/Colombo" },
  { name: "Jaffna", stateOrCountry: "Sri Lanka", latitude: 9.6615, longitude: 80.0255, timezone: "Asia/Colombo" },
  { name: "Dubai", stateOrCountry: "United Arab Emirates", latitude: 25.2048, longitude: 55.2708, timezone: "Asia/Dubai" },
  { name: "Abu Dhabi", stateOrCountry: "United Arab Emirates", latitude: 24.4539, longitude: 54.3773, timezone: "Asia/Dubai" },
  { name: "Doha", stateOrCountry: "Qatar", latitude: 25.2854, longitude: 51.5310, timezone: "Asia/Qatar" },
  { name: "Kuwait City", stateOrCountry: "Kuwait", latitude: 29.3759, longitude: 47.9774, timezone: "Asia/Kuwait" },
  { name: "London", stateOrCountry: "United Kingdom", latitude: 51.5074, longitude: -0.1278, timezone: "Europe/London" },
  { name: "Birmingham", stateOrCountry: "United Kingdom", latitude: 52.4862, longitude: -1.8904, timezone: "Europe/London" },
  { name: "Paris", stateOrCountry: "France", latitude: 48.8566, longitude: 2.3522, timezone: "Europe/Paris" },
  { name: "Berlin", stateOrCountry: "Germany", latitude: 52.5200, longitude: 13.4050, timezone: "Europe/Berlin" },
  { name: "Frankfurt", stateOrCountry: "Germany", latitude: 50.1109, longitude: 8.6821, timezone: "Europe/Berlin" },
  { name: "New York", stateOrCountry: "NY, United States", latitude: 40.7128, longitude: -74.0060, timezone: "America/New_York" },
  { name: "San Francisco", stateOrCountry: "CA, United States", latitude: 37.7749, longitude: -122.4194, timezone: "America/Los_Angeles" },
  { name: "San Jose", stateOrCountry: "CA, United States", latitude: 37.3382, longitude: -121.8863, timezone: "America/Los_Angeles" },
  { name: "Los Angeles", stateOrCountry: "CA, United States", latitude: 34.0522, longitude: -118.2437, timezone: "America/Los_Angeles" },
  { name: "Chicago", stateOrCountry: "IL, United States", latitude: 41.8781, longitude: -87.6298, timezone: "America/Chicago" },
  { name: "Dallas", stateOrCountry: "TX, United States", latitude: 32.7767, longitude: -96.7970, timezone: "America/Chicago" },
  { name: "Houston", stateOrCountry: "TX, United States", latitude: 29.7604, longitude: -95.3698, timezone: "America/Chicago" },
  { name: "Atlanta", stateOrCountry: "GA, United States", latitude: 33.7490, longitude: -84.3880, timezone: "America/New_York" },
  { name: "Seattle", stateOrCountry: "WA, United States", latitude: 47.6062, longitude: -122.3321, timezone: "America/Los_Angeles" },
  { name: "Toronto", stateOrCountry: "ON, Canada", latitude: 43.6532, longitude: -79.3832, timezone: "America/Toronto" },
  { name: "Vancouver", stateOrCountry: "BC, Canada", latitude: 49.2827, longitude: -123.1207, timezone: "America/Vancouver" },
  { name: "Sydney", stateOrCountry: "NSW, Australia", latitude: -33.8688, longitude: 151.2093, timezone: "Australia/Sydney" },
  { name: "Melbourne", stateOrCountry: "VIC, Australia", latitude: -37.8136, longitude: 144.9631, timezone: "Australia/Melbourne" },
  { name: "Auckland", stateOrCountry: "New Zealand", latitude: -36.8485, longitude: 174.7633, timezone: "Pacific/Auckland" },
  { name: "Tokyo", stateOrCountry: "Japan", latitude: 35.6762, longitude: 139.6503, timezone: "Asia/Tokyo" },
];

export const COMMON_TIMEZONES: { label: string; value: string; offset: string }[] = [
  { label: "India Standard Time (IST - Asia/Kolkata)", value: "Asia/Kolkata", offset: "+05:30" },
  { label: "Sri Lanka Time (Asia/Colombo)", value: "Asia/Colombo", offset: "+05:30" },
  { label: "Singapore / Malaysia Time (SGT - Asia/Singapore)", value: "Asia/Singapore", offset: "+08:00" },
  { label: "Gulf Standard Time (GST - Asia/Dubai)", value: "Asia/Dubai", offset: "+04:00" },
  { label: "Greenwich Mean Time / BST (Europe/London)", value: "Europe/London", offset: "+00:00" },
  { label: "Central European Time (Europe/Paris)", value: "Europe/Paris", offset: "+01:00" },
  { label: "Eastern Time (US & Canada - America/New_York)", value: "America/New_York", offset: "-05:00" },
  { label: "Central Time (US & Canada - America/Chicago)", value: "America/Chicago", offset: "-06:00" },
  { label: "Mountain Time (US & Canada - America/Denver)", value: "America/Denver", offset: "-07:00" },
  { label: "Pacific Time (US & Canada - America/Los_Angeles)", value: "America/Los_Angeles", offset: "-08:00" },
  { label: "Australian Eastern Time (Australia/Sydney)", value: "Australia/Sydney", offset: "+10:00" },
  { label: "Australian Western Time (Australia/Perth)", value: "Australia/Perth", offset: "+08:00" },
  { label: "New Zealand Time (Pacific/Auckland)", value: "Pacific/Auckland", offset: "+12:00" },
  { label: "Japan Standard Time (Asia/Tokyo)", value: "Asia/Tokyo", offset: "+09:00" },
  { label: "Coordinated Universal Time (UTC)", value: "UTC", offset: "+00:00" },
];
