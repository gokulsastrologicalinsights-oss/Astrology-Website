# scripts/patch_repository.py
from pathlib import Path

path = Path("backend/app/services/remedy_engine/repository.py")
text = path.read_text(encoding="utf-8")

old_snippet = """            if res.data and len(res.data) > 0:
                for row in res.data:
                    local = REMEDIES_BY_CODE.get(row.get("code"))
                    if local:
                        for k, v in local.items():
                            if row.get(k) is None:
                                row[k] = v
                return res.data"""

new_snippet = """            if res.data and len(res.data) > 0:
                remote_codes = set()
                for row in res.data:
                    local = REMEDIES_BY_CODE.get(row.get("code"))
                    if local:
                        for k, v in local.items():
                            if row.get(k) is None:
                                row[k] = v
                    remote_codes.add(row.get("code"))
                extras = [r for r in VERIFIED_REMEDIES if r["code"] not in remote_codes]
                if graha:
                    extras = [r for r in extras if r.get("graha") == graha]
                if remedy_type:
                    extras = [r for r in extras if r.get("remedy_type") == remedy_type]
                if problem_slug:
                    extras = [r for r in extras if problem_slug in r.get("problem_slugs", [])]
                return res.data + extras"""

if old_snippet in text:
    text = text.replace(old_snippet, new_snippet, 1)
    path.write_text(text, encoding="utf-8")
    print("Patched list_remedies successfully!")
else:
    print("Old snippet not found!")
