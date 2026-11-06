import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

from app.schemas.instant_revelation import InstantRevelationRequest
from app.services.instant_revelation.engine import InstantRevelationEngine

req = InstantRevelationRequest(
    birth_date="1992-08-14",
    birth_time="06:45:00",
    timezone="Asia/Kolkata",
    latitude=13.0827,
    longitude=80.2707,
    name="Test Client",
    consultation_time="2026-11-06T12:00:00+05:30",
)

res = InstantRevelationEngine.analyze(req)
print("Primary Arrival Reason TA:", res.primary_arrival_reason_ta)
print("Primary Arrival Reason EN:", res.primary_arrival_reason_en)
print("Bullets count:", len(res.arrival_reason_bullets))
for b in res.arrival_reason_bullets:
    print(f"[{b.id}] {b.headline_ta} -> {b.astrological_proof}")
