import urllib.request
import json

url = 'https://pcwiopxewlxhwvddpndq.supabase.co/rest/v1/saved_horoscopes?select=id,person_name,calculation_result&limit=1'
headers = {
    'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBjd2lvcHhld2x4aHd2ZGRwbmRxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MjI0OTg5MywiZXhwIjoyMTA3ODI1ODkzfQ.RbiQ6PQoLSdBf6m6-HN52MHV9pnxEOMIQ2AqrYtOV0U',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBjd2lvcHhld2x4aHd2ZGRwbmRxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MjI0OTg5MywiZXhwIjoyMTA3ODI1ODkzfQ.RbiQ6PQoLSdBf6m6-HN52MHV9pnxEOMIQ2AqrYtOV0U'
}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    row = data[0]
    calc = row.get('calculation_result', {})
    h = calc.get('horoscope', {})
    asc = h.get('ascendant', {})
    planets = h.get('planets', [])
    print(f"Person: {row.get('person_name')}")
    print(f"Ascendant: Sign {asc.get('sign_name')} ({asc.get('degree_in_sign'):.2f}°), Nakshatra: {asc.get('nakshatra', {}).get('name')} Pada {asc.get('nakshatra', {}).get('pada')}")
    for p in planets:
        nak = p.get('nakshatra', {})
        print(f"{p.get('name')}: Sign {p.get('sign_name')} ({p.get('degree_in_sign'):.2f}°), House {p.get('house')}, Nak: {nak.get('name')} Pada {nak.get('pada')}")
