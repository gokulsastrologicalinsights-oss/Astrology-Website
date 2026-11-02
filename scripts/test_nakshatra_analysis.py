import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.nakshatra_engine import analyze_saved_chart_nakshatras

sample_data = {
    'ascendant': {'sign_name': 'Taurus', 'degree_in_sign': 28.09, 'nakshatra': {'name': 'Mrigashira', 'pada': 2}},
    'planets': [
        {'name': 'Sun', 'sign_name': 'Cancer', 'degree_in_sign': 2.44, 'nakshatra': {'name': 'Punarvasu', 'pada': 4}, 'is_retrograde': False},
        {'name': 'Moon', 'sign_name': 'Gemini', 'degree_in_sign': 6.10, 'nakshatra': {'name': 'Mrigashira', 'pada': 4}, 'is_retrograde': False},
        {'name': 'Venus', 'sign_name': 'Taurus', 'degree_in_sign': 20.70, 'nakshatra': {'name': 'Rohini', 'pada': 4}, 'is_retrograde': False},
        {'name': 'Saturn', 'sign_name': 'Taurus', 'degree_in_sign': 17.07, 'nakshatra': {'name': 'Rohini', 'pada': 3}, 'is_retrograde': False},
        {'name': 'Mercury', 'sign_name': 'Gemini', 'degree_in_sign': 14.40, 'nakshatra': {'name': 'Ardra', 'pada': 3}, 'is_retrograde': False},
        {'name': 'Jupiter', 'sign_name': 'Gemini', 'degree_in_sign': 7.43, 'nakshatra': {'name': 'Ardra', 'pada': 1}, 'is_retrograde': False},
        {'name': 'Rahu', 'sign_name': 'Gemini', 'degree_in_sign': 11.28, 'nakshatra': {'name': 'Ardra', 'pada': 2}, 'is_retrograde': False},
    ]
}

res = analyze_saved_chart_nakshatras(sample_data, birth_date_str='2001-07-19')
print('Rules matched:', res['total_rules_matched'])
print('Critical cautions:', res['critical_cautions_count'])
print('Milestones:', res['milestones_count'])
print('Soul lessons:', res['soul_lessons_count'])
for r in res['matched_rules']:
    print(f"[{r['severity']}] {r['nakshatra']} | {r['technique_id']} -> {r['title_en']}")
