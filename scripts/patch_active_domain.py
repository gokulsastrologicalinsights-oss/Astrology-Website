# scripts/patch_active_domain.py
from pathlib import Path

path = Path("frontend/src/components/results/AstrologicalPredictionsSection.tsx")
content = path.read_text(encoding="utf-8")

old_text = '    "all" | "marriage_domain" | "career_wealth_domain" | "personality_stars_domain" | "life_events_domain" | "saravali_domain" | "advanced_engine"'
new_text = '    "all" | "bphs_domain" | "saravali_domain" | "marriage_domain" | "career_wealth_domain" | "personality_stars_domain" | "life_events_domain" | "advanced_engine"'

if old_text in content:
    content = content.replace(old_text, new_text, 1)
    path.write_text(content, encoding="utf-8")
    print("Successfully patched activeDomain type!")
else:
    print("Could not find old_text")
