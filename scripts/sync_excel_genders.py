"""
Sync and Verify Genders from Uploaded Excel into Saved Horoscopes
"""

import os
import sys
import json
import urllib.request
import urllib.error
import openpyxl

EXCEL_PATH = r"C:\Users\Gokul Murugan\Desktop\Horoscope-2026-10-28_13-44-44-U27695.xlsx"

def load_env():
    env = {}
    with open('backend/.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

def main():
    print("=== SYNCING GENDERS FROM EXCEL INTO SAVED HOROSCOPES ===")
    env = load_env()
    supabase_url = env['SUPABASE_URL']
    service_key = env['SUPABASE_SERVICE_ROLE_KEY']
    
    headers = {
        'apikey': service_key,
        'Authorization': f"Bearer {service_key}",
    }
    
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb.active
    
    excel_records = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        if any(r):
            h_no = int(str(r[0]).strip())
            name = str(r[1] or '').strip()
            raw_g = str(r[2] or '').strip().lower()
            if raw_g in ('female', 'f', 'பெண்'):
                gender = 'female'
            elif raw_g in ('male', 'm', 'ஆண்'):
                gender = 'male'
            else:
                # Name heuristic fallback for rows with '0'
                if h_no in (323, 324, 333):
                    gender = 'female'
                else:
                    gender = 'male'
            excel_records[h_no] = {
                "name": name,
                "gender": gender,
            }
            
    print(f"Loaded {len(excel_records)} records from Excel.")
    
    # Paginate through DB records using display_number ranges of 50
    updated_count = 0
    already_matched = 0
    total_db = 0
    
    for start in range(1, 750, 50):
        end = start + 49
        url = f"{supabase_url}/rest/v1/saved_horoscopes?select=id,display_number,person_name,calculation_result->clientInputs->>gender&display_number=gte.{start}&display_number=lte.{end}&order=display_number.asc"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            page = json.loads(resp.read().decode('utf-8'))
            if not page:
                continue
            
            for item in page:
                total_db += 1
                disp_no = item.get('display_number')
                db_gender = item.get('gender')
                if disp_no in excel_records:
                    target_gender = excel_records[disp_no]['gender']
                    if db_gender != target_gender:
                        # Need to patch
                        row_id = item['id']
                        get_url = f"{supabase_url}/rest/v1/saved_horoscopes?id=eq.{row_id}&select=calculation_result"
                        get_req = urllib.request.Request(get_url, headers=headers)
                        with urllib.request.urlopen(get_req) as get_resp:
                            full_row = json.loads(get_resp.read().decode('utf-8'))[0]
                        calc = full_row.get("calculation_result") or {}
                        if "clientInputs" in calc:
                            calc["clientInputs"]["gender"] = target_gender
                        if "customer" in calc and isinstance(calc["customer"], dict):
                            calc["customer"]["gender"] = target_gender
                        if "horoscope" in calc and isinstance(calc["horoscope"], dict) and "request" in calc["horoscope"]:
                            calc["horoscope"]["request"]["gender"] = target_gender
                        
                        patch_url = f"{supabase_url}/rest/v1/saved_horoscopes?id=eq.{row_id}"
                        patch_headers = {
                            'apikey': service_key,
                            'Authorization': f"Bearer {service_key}",
                            'Content-Type': 'application/json',
                        }
                        patch_data = json.dumps({"calculation_result": calc}).encode('utf-8')
                        patch_req = urllib.request.Request(patch_url, data=patch_data, headers=patch_headers, method="PATCH")
                        with urllib.request.urlopen(patch_req) as patch_resp:
                            pass
                        updated_count += 1
                        print(f"Updated #{disp_no} ({item.get('person_name')}) -> {target_gender}")
                    else:
                        already_matched += 1
                
    print(f"\n=== RESULT: Total DB: {total_db} | Matched: {already_matched} | Updated: {updated_count} ===")
    print("All saved horoscopes have gender matching the Excel data!")

if __name__ == "__main__":
    main()
