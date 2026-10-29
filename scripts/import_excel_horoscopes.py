"""
Bulk Import Script for Customer Horoscopes
Reads Horoscope-2026-10-28_13-44-44-U27695.xlsx from Desktop,
performs full high-precision Vedic astrological calculations (Horoscope, Dasa, KP),
provisions authoritative customer profiles, and persists all records into Supabase.
"""

import os
import sys
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
import json
import uuid
import time
import re
import urllib.request
import urllib.error
from datetime import datetime, date, time as dtime, timedelta

sys.path.insert(0, '.')
sys.path.insert(0, os.path.abspath('backend'))

import openpyxl

from app.schemas.horoscope import HoroscopeRequest
from app.schemas.dasa import DasaRequest
from app.schemas.kp import KpRequest
from app.routers.horoscope import calculate_horoscope
from app.routers.dasa import calculate_horoscope_dasa
from app.routers.kp import calculate_horoscope_kp
from scratch.test_geo import GEO_DICT

EXCEL_PATH = r"C:\Users\Gokul Murugan\Desktop\Horoscope-2026-10-28_13-44-44-U27695.xlsx"
ADMIN_USER_ID = "4719b6a8-0452-4bfa-ab87-6733190c3de3"

def load_env():
    env = {}
    with open('backend/.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

ENV = load_env()
SUPABASE_URL = ENV['SUPABASE_URL']
SERVICE_ROLE_KEY = ENV['SUPABASE_SERVICE_ROLE_KEY']

HEADERS = {
    'apikey': SERVICE_ROLE_KEY,
    'Authorization': f"Bearer {SERVICE_ROLE_KEY}",
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def normalize_phone(raw_phone):
    if not raw_phone:
        return "+91", None, None, None
    raw = str(raw_phone).strip()
    if raw.startswith("+966"):
        digits = re.sub(r'\D', '', raw[4:])
        return "+966", digits, f"+966{digits}", f"966{digits}"
    elif raw.startswith("+91"):
        digits = re.sub(r'\D', '', raw[3:])
        return "+91", digits, f"+91{digits}", f"91{digits}"
    else:
        digits = re.sub(r'\D', '', raw)
        if len(digits) == 10:
            return "+91", digits, f"+91{digits}", f"91{digits}"
        elif len(digits) > 10 and digits.startswith("91"):
            nat = digits[2:]
            return "+91", nat, f"+91{nat}", digits
        return "+91", digits, None, None

def serialize_pydantic(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    elif hasattr(obj, "dict"):
        return obj.dict()
    return obj

def compact_dasa_tree(tree, max_depth=3):
    if not isinstance(tree, list) or max_depth <= 0:
        return []
    compacted = []
    for node in tree:
        compact_node = {
            "lord": node.get("lord"),
            "level": node.get("level"),
            "start_jd": node.get("start_jd"),
            "end_jd": node.get("end_jd"),
            "duration_days": node.get("duration_days"),
            "duration_years": node.get("duration_years"),
            "start_date_iso": node.get("start_date_iso"),
            "end_date_iso": node.get("end_date_iso"),
        }
        for field in [
            "theoretical_start_jd", "theoretical_end_jd", "theoretical_duration_days",
            "theoretical_duration_years", "theoretical_start_date_iso", "theoretical_end_date_iso",
            "is_active", "is_active_at_birth", "star_lord", "benefit_bhavas", "benefit_bhavas_detail",
            "period_lord_occupied", "star_lord_occupied", "period_lord_owned", "star_lord_owned"
        ]:
            if field in node and node[field] is not None:
                compact_node[field] = node[field]
                
        sub_periods = node.get("sub_periods") or node.get("children")
        if max_depth > 1 and isinstance(sub_periods, list) and len(sub_periods) > 0:
            compact_node["sub_periods"] = compact_dasa_tree(sub_periods, max_depth - 1)
        compacted.append(compact_node)
    return compacted

def clean_old_records():
    print("Cleaning up old test records...")
    url = f"{SUPABASE_URL}/rest/v1/saved_horoscopes?user_id=eq.{ADMIN_USER_ID}"
    req = urllib.request.Request(url, headers=HEADERS, method="DELETE")
    try:
        with urllib.request.urlopen(req) as resp:
            print("Old saved_horoscopes cleared.")
    except Exception as e:
        print("Note on clearing saved_horoscopes:", e)

    url = f"{SUPABASE_URL}/rest/v1/customers?user_id=eq.{ADMIN_USER_ID}"
    req = urllib.request.Request(url, headers=HEADERS, method="DELETE")
    try:
        with urllib.request.urlopen(req) as resp:
            print("Old customers cleared.")
    except Exception as e:
        print("Note on clearing customers:", e)

def post_batch(endpoint, items):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    payload_bytes = json.dumps(items).encode('utf-8')
    req = urllib.request.Request(url, data=payload_bytes, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8')
        print(f"Error posting batch of {len(items)} to {endpoint}: {e.code} {err_msg}")
        # If batch fails, fallback to row by row
        if len(items) > 1:
            print("Falling back to single row insertions...")
            for it in items:
                post_batch(endpoint, [it])
            return 200
        else:
            raise

def main():
    print("=== STARTING BULK IMPORT OF CUSTOMER HOROSCOPES ===")
    clean_old_records()
    
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb.active
    
    raw_rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if any(r):
            raw_rows.append(r)
            
    print(f"Total rows read from Excel: {len(raw_rows)}")
    
    # Sort ascending by horoscope number (1 to 707) so insertion is sequential
    parsed_rows = []
    for r in raw_rows:
        h_no = int(str(r[0]).strip())
        parsed_rows.append((h_no, r))
    parsed_rows.sort(key=lambda x: x[0])
    
    base_time = datetime(2026, 10, 1, 0, 0, 0)
    
    customer_list_for_json = []
    created_customers = {} # normalized_phone -> customer_id
    
    horoscope_batch = []
    customer_batch = []
    
    total = len(parsed_rows)
    t_start = time.time()
    
    BATCH_SIZE = 3
    
    for i, (h_no_int, r) in enumerate(parsed_rows, 1):
        _, name_raw, gender_raw, phone_raw, place_raw, dob = r
        person_name = str(name_raw or '').strip()
        gender = "female" if str(gender_raw or '').strip().lower() == "female" else "male"
        place_key = str(place_raw or '').strip().lower()
        geo = GEO_DICT[place_key]
        
        b_date = dob.date()
        b_time = dob.time()
        
        # Phone handling
        country_code, nat_phone, norm_phone, wa_digits = normalize_phone(phone_raw)
        
        # Deduplicate customer if phone is shared
        if norm_phone and norm_phone in created_customers:
            cust_id = created_customers[norm_phone]
        else:
            cust_id = str(uuid.uuid4())
            if norm_phone:
                created_customers[norm_phone] = cust_id
                
            c_record = {
                "id": cust_id,
                "user_id": ADMIN_USER_ID,
                "full_name": person_name,
                "birth_date": b_date.isoformat(),
                "country_code": country_code,
                "phone_number": nat_phone,
                "normalized_phone": norm_phone,
                "whatsapp_number": wa_digits,
                "created_at": (base_time + timedelta(seconds=h_no_int)).isoformat() + "Z",
                "updated_at": (base_time + timedelta(seconds=h_no_int)).isoformat() + "Z"
            }
            customer_batch.append(c_record)
            customer_list_for_json.append({
                **c_record,
                "is_legacy_without_phone": not bool(norm_phone)
            })

        # Calculations
        h_req = HoroscopeRequest(
            birth_date=b_date,
            birth_time=b_time,
            timezone=geo["tz"],
            latitude=geo["lat"],
            longitude=geo["lon"],
            ayanamsa=0,
            house_system=0,
            include_panchang=True,
            include_outer_planets=True,
            include_nabhasha=True,
            include_ashtakavarga=True,
            include_vedic_yogas=True,
            include_doshas=True,
            gender=gender
        )
        h_res = calculate_horoscope(h_req)
        
        d_req = DasaRequest(
            birth_date=b_date,
            birth_time=b_time,
            timezone=geo["tz"],
            latitude=geo["lat"],
            longitude=geo["lon"],
            depth=3,
            ayanamsa=0,
            house_system=0
        )
        d_res = calculate_horoscope_dasa(d_req)
        
        kp_req = KpRequest(
            birth_date=b_date,
            birth_time=b_time,
            timezone=geo["tz"],
            latitude=geo["lat"],
            longitude=geo["lon"],
            ayanamsa=1,
            house_system=2
        )
        kp_res = calculate_horoscope_kp(kp_req)
        
        d_dict = serialize_pydantic(d_res)
        d_dict["dasa_tree"] = compact_dasa_tree(d_dict["dasa_tree"], 3)
        
        record_created_at = (base_time + timedelta(seconds=h_no_int)).isoformat() + "Z"
        
        snapshot = {
            "schema_version": "1.0.0",
            "idempotency_key": f"calc_{h_no_int}_{dob.strftime('%Y%m%d%H%M%S')}",
            "calculatedAt": record_created_at,
            "clientInputs": {
                "fullName": person_name,
                "latitude": geo["lat"],
                "longitude": geo["lon"],
                "timezone": geo["tz"],
                "birthDate": b_date.isoformat(),
                "birthTime": b_time.strftime("%H:%M:%S"),
                "ayanamsaId": 0,
                "locationName": geo["name"],
                "houseSystemId": 0,
                "isTimeConfirmed": True,
                "gender": gender
            },
            "customer": {
                "id": cust_id,
                "full_name": person_name,
                "birth_date": b_date.isoformat(),
                "country_code": country_code,
                "phone_number": nat_phone or "",
                "whatsapp_number": wa_digits or "",
                "normalized_phone": norm_phone or ""
            },
            "horoscope": serialize_pydantic(h_res),
            "dasa": d_dict,
            "kp": serialize_pydantic(kp_res)
        }
        
        horo_record = {
            "id": str(uuid.uuid4()),
            "user_id": ADMIN_USER_ID,
            "display_number": h_no_int,
            "person_name": person_name,
            "birth_date": b_date.isoformat(),
            "birth_time": b_time.strftime("%H:%M:%S"),
            "timezone": geo["tz"],
            "birthplace": geo["name"],
            "latitude": geo["lat"],
            "longitude": geo["lon"],
            "ayanamsa_id": 0,
            "house_system_id": 0,
            "calculation_result": snapshot,
            "customer_id": cust_id,
            "created_at": record_created_at,
            "updated_at": record_created_at
        }
        horoscope_batch.append(horo_record)
        
        # Flush batches every BATCH_SIZE horoscopes
        if len(horoscope_batch) >= BATCH_SIZE or i == total:
            if customer_batch:
                post_batch("customers", customer_batch)
                customer_batch = []
            post_batch("saved_horoscopes", horoscope_batch)
            horoscope_batch = []
            
            elapsed = time.time() - t_start
            rate = i / elapsed
            remaining = (total - i) / rate if rate > 0 else 0
            if i % 15 == 0 or i == total:
                print(f"[{i:3d}/{total}] Imported up to Horoscope #{h_no_int:03d} ({person_name}) | Elapsed: {elapsed:.1f}s | Est. remaining: {remaining:.1f}s")

    # Update admin user metadata last_horoscope_seq to 707
    print("Updating admin user last_horoscope_seq = 707...")
    url = f"{SUPABASE_URL}/auth/v1/admin/users/{ADMIN_USER_ID}"
    user_payload = {"user_metadata": {"last_horoscope_seq": 707}}
    req = urllib.request.Request(
        url,
        data=json.dumps(user_payload).encode('utf-8'),
        headers=HEADERS,
        method="PUT"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print("Admin user metadata updated to 707.")
    except Exception as e:
        print("Note on updating metadata:", e)
        
    # Save local customer file
    local_cust_file = os.path.join("data", "customers.json")
    with open(local_cust_file, "w", encoding="utf-8") as f:
        json.dump(customer_list_for_json, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(customer_list_for_json)} customers to {local_cust_file}.")
    
    print(f"=== ALL {total} HOROSCOPES IMPORTED SUCCESSFULLY in {time.time()-t_start:.1f}s ===")

if __name__ == "__main__":
    main()
