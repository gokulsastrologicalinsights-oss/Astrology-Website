import urllib.request
import json
import os

SUPABASE_URL = "https://pcwiopxewlxhwvddpndq.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBjd2lvcHhld2x4aHd2ZGRwbmRxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MjI0OTg5MywiZXhwIjoyMTA3ODI1ODkzfQ.RbiQ6PQoLSdBf6m6-HN52MHV9pnxEOMIQ2AqrYtOV0U"

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Prefer": "count=exact"
}

def query_table(endpoint):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        content_range = resp.headers.get("Content-Range")
        data = json.loads(resp.read().decode("utf-8"))
        return data, content_range

data, crange = query_table("saved_horoscopes?select=id,person_name,birth_date,birth_time,birthplace,latitude,longitude,ayanamsa_id,created_at&order=created_at.desc&limit=50")
print(f"Content-Range: {crange}")
print(f"Fetched: {len(data)}")
for d in data[:15]:
    print(d["id"], d["person_name"], d["birth_date"], d["birth_time"], d.get("birthplace"))
