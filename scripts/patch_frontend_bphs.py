# scripts/patch_frontend_bphs.py
from pathlib import Path

path = Path("frontend/src/components/results/AstrologicalPredictionsSection.tsx")
content = path.read_text(encoding="utf-8")

# 1. Add ScrollText to imports if missing
if "ScrollText," not in content:
    content = content.replace("  Clock,\n} from \"lucide-react\";", "  Clock,\n  ScrollText,\n} from \"lucide-react\";")

# 2. Add bphs_classics to QUICK_FILTER_PILLS
if '"bphs_classics"' not in content:
    target_pill = '{ id: "all", label_en: "All Topics (230+)", label_ta: "அனைத்தும் (230+)", icon: Sparkles },'
    replacement_pill = """{ id: "all", label_en: "All Topics (230+)", label_ta: "அனைத்தும் (230+)", icon: Sparkles },
  { id: "bphs_classics", label_en: "Parashara Hora (BPHS)", label_ta: "பராசர ஹோரா சாஸ்திரம்", icon: ScrollText, isHighlight: true },"""
    content = content.replace(target_pill, replacement_pill)

# 3. Add bphs_domain to PredictionDomainConfig id type
if '"bphs_domain"' not in content:
    content = content.replace(
        'id: "all" | "marriage_domain"',
        'id: "all" | "bphs_domain" | "saravali_domain" | "marriage_domain"'
    )

# 4. Add bphs_domain to PREDICTION_DOMAINS array
bphs_domain_block = """  {
    id: "bphs_domain",
    label_en: "Parashara Hora (BPHS)",
    label_ta: "பராசர ஹோரா சாஸ்திரம்",
    icon: ScrollText,
    colorClass: "text-purple-950 bg-purple-50/90 border-purple-300 hover:bg-purple-100",
    activeColorClass: "bg-gradient-to-r from-purple-800 via-indigo-900 to-purple-950 text-white shadow-sm ring-2 ring-purple-400/50",
    subPills: [
      { id: "all", label_en: "All BPHS Rules", label_ta: "அனைத்து பராசர விதிகள்", icon: ScrollText },
      { id: "bphs_bhava_lords", label_en: "12 Bhava Lords (144 Combinations)", label_ta: "144 பாவாதிபதி பலன்கள்", slug: "bphs_bhava_lords", icon: Crown },
      { id: "bphs_yogakarakas", label_en: "Yogakarakas & Lagna Lords", label_ta: "யோககாரகர்கள் & லக்னாதிபதிகள்", slug: "bphs_yogakarakas", icon: Sparkles },
      { id: "bphs_dhana_yogas", label_en: "Special Dhana Yogas", label_ta: "சிறப்பு தன யோகங்கள்", slug: "bphs_dhana_yogas", icon: Coins },
      { id: "bphs_daridra_yogas", label_en: "Daridra Yogas & Penury", label_ta: "தரித்திர யோகங்கள்", slug: "bphs_daridra_yogas", icon: AlertCircle },
      { id: "bphs_stri_jataka", label_en: "Stri Jataka & Visha Kanya", label_ta: "ஸ்திரீ ஜாதகம் & விஷ கன்யா", slug: "bphs_stri_jataka", icon: Heart },
      { id: "bphs_shapas_curses", label_en: "8 Past Life Curses & Remedies", label_ta: "8 சாபங்களும் பரிகாரங்களும்", slug: "bphs_shapas_curses", icon: ShieldAlert },
      { id: "bphs_inauspicious_births", label_en: "Inauspicious Births & Gandanta", label_ta: "கண்டாந்தம் & அசுப ஜனனம்", slug: "bphs_inauspicious_births", icon: Flame },
      { id: "bphs_upagrahas_arudhas", label_en: "Arudha Padas & Upagrahas", label_ta: "ஆரூட பாதங்கள் & உபகிரகங்கள்", slug: "bphs_upagrahas_arudhas", icon: Layers },
    ],
  },
"""

if 'id: "bphs_domain"' not in content:
    saravali_marker = '  {\n    id: "saravali_domain",'
    content = content.replace(saravali_marker, bphs_domain_block + saravali_marker)

# 5. Add bphs to domainMatchCounts
domain_counts_target = 'saravali: matched.filter((r) => r.category_slug === "saravali_classics" || r.rule_id?.startsWith("RULE-SARAVALI") || r.source_reference?.toLowerCase().includes("saravali")).length,'
domain_counts_repl = """bphs: matched.filter((r) => r.category_slug?.startsWith("bphs_") || r.rule_id?.startsWith("RULE-BPHS") || r.source_reference?.toLowerCase().includes("parashara")).length,
      saravali: matched.filter((r) => r.category_slug === "saravali_classics" || r.rule_id?.startsWith("RULE-SARAVALI") || r.source_reference?.toLowerCase().includes("saravali")).length,"""

content = content.replace(domain_counts_target, domain_counts_repl)

# 6. Add bphs filtering in displayedRules
filter_target = '} else if (activeDomain === "saravali_domain") {'
filter_repl = """} else if (activeDomain === "bphs_domain") {
      if (activeSubFilter !== "all") {
        list = list.filter((r) => r.subcategory === activeSubFilter || r.category_slug === activeSubFilter);
      } else {
        list = list.filter((r) => r.category_slug?.startsWith("bphs_") || r.rule_id?.startsWith("RULE-BPHS") || r.source_reference?.toLowerCase().includes("parashara"));
      }
    } else if (activeDomain === "saravali_domain") {"""

content = content.replace(filter_target, filter_repl)

# 7. Add badgeCount check for bphs_domain
badge_target = 'domain.id === "all"'
badge_repl = """domain.id === "all"
                ? domainCounts.all
                : domain.id === "bphs_domain"
                ? domainCounts.bphs"""

content = content.replace(
    'domain.id === "all"\n                ? domainCounts.all',
    badge_repl
)

path.write_text(content, encoding="utf-8")
print("Successfully patched frontend AstrologicalPredictionsSection.tsx!")
