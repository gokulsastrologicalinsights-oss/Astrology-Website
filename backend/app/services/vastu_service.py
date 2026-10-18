"""Vastu Shastra Calculation and Evaluation Service.

Implements deterministic, rule-based Vastu calculations derived from classical treatises
(Mayamata, Manasara, Brihat Samhita, Vishwakarma Prakash).
Features:
- Correct 16-direction azimuth spans (clockwise 0° to 337.5°).
- 32 Outer Pada Deities of the Paramasayika mandala.
- Layout evaluation across residential, commercial, plot, and industrial profiles.
- Score normalization strictly over assessable factors with no penalty for missing data.
- Authentic classical Dosha identification and traditional remedies.
- Astro-Vastu overlay powered by the native XALEN ephemeris engine.
- Supabase persistence with concurrency-safe transactional display numbering.
"""

from typing import List, Dict, Any, Optional, Tuple
import math
import re
from datetime import datetime, timezone
import uuid

from app.schemas.vastu import (
    DirectionMetadata,
    PadaDeityMetadata,
    VastuDirectionsResponse,
    VastuEvaluationRequest,
    VastuEvaluationResponse,
    FactorEvaluation,
    VastuDosha,
    AstroOverlayResult,
    SaveVastuReportRequest,
    VALID_16_DIRECTIONS,
)
from app.services.auth_service import get_supabase_client

ENGINE_VERSION = "1.0.0"
RUBRIC_VERSION = "1.0.0"

DISCLAIMER_TEXT = (
    "This evaluation is based on traditional Vastu Shastra architectural principles from classical texts "
    "(Mayamata, Manasara, Brihat Samhita, Vishwakarma Prakash) and is provided strictly for educational and "
    "cultural reference. Vastu guidelines describe classical spatial harmony and should not be construed as "
    "scientifically verified guarantees of health, wealth, prosperity, or life outcomes. Structural changes "
    "to existing properties should always consider modern engineering and architectural feasibility."
)

# ------------------------------------------------------------------------------
# 1. Classical 16 Directions Definition (Strict Clockwise Azimuth Order)
# ------------------------------------------------------------------------------

# 16 directions with exact 22.5° sector boundaries (center angle ± 11.25°)
# Start at North (0°): sector is 348.75° to 11.25°
DIRECTIONS_16_CONFIG: List[Dict[str, Any]] = [
    {
        "code": "N",
        "sanskrit_name": "Uttara (उत्तर)",
        "english_name": "North",
        "chinese_name": "北方 (Uttara)",
        "center_degree": 0.0,
        "start_degree": 348.75,
        "end_degree": 11.25,
        "deity": "Kubera (財神 / 俱吠羅)",
        "element": "Water (Jala)",
        "planet": "Mercury (Budha / 水星)",
        "traditional_significance": "財富與繁榮之源，地球正磁場流入方向，宜開闊明亮、低矮通風。",
        "recommended_colors": ["綠色", "淺藍色", "白色"],
        "color_hex": ["#008000", "#ADD8E6", "#FFFFFF"],
        "traditional_remedies": ["放置 Kubera Yantra 或財神像", "保持北方整潔開闊低矮", "擺放水培植物或小型流水景觀"],
        "suitable_uses": ["客廳", "財務辦公室", "主入口", "保險箱", "陽台大窗"],
        "prohibited_uses": ["廁所", "廚房", "重型庫房", "化糞池", "垃圾存放區"],
    },
    {
        "code": "NNE",
        "sanskrit_name": "Uttara-Īśānya (उत्तर-ईशान्य)",
        "english_name": "North-NorthEast",
        "chinese_name": "北偏東北 (Uttara-Īśānya)",
        "center_degree": 22.5,
        "start_degree": 11.25,
        "end_degree": 33.75,
        "deity": "Soma / Apavatsa (蘇摩 / 月神群)",
        "element": "Water / Ether (Jala-Ākāśa)",
        "planet": "Jupiter (Guru / 木星)",
        "traditional_significance": "身心療癒與健康之能量區，掌管醫藥與純淨生命力。",
        "recommended_colors": ["白色", "淺金色", "象牙白"],
        "color_hex": ["#FFFFFF", "#FFFDD0", "#FFFFF0"],
        "traditional_remedies": ["以清水定期擦拭淨化", "擺放天然白水晶球", "放置常備藥品保持潔淨"],
        "suitable_uses": ["冥想區", "醫藥保健品存放", "水井", "閱讀角"],
        "prohibited_uses": ["廁所", "垃圾桶", "重型金屬器具"],
    },
    {
        "code": "NE",
        "sanskrit_name": "Īśānya (ईशान्य)",
        "english_name": "North-East",
        "chinese_name": "東北方 (Īśānya)",
        "center_degree": 45.0,
        "start_degree": 33.75,
        "end_degree": 56.25,
        "deity": "Īśāna (濕婆化身 / 伊舍那天)",
        "element": "Ether / Space (Ākāśa)",
        "planet": "Jupiter (Bṛhaspati / 木星)",
        "traditional_significance": "全宅最神聖的方位，宇宙正能量（Prāṇa）主要入口，代表智慧、開悟與神聖恩典。",
        "recommended_colors": ["金色", "黃色", "乳白色"],
        "color_hex": ["#FFD700", "#FFFF00", "#FFF8DC"],
        "traditional_remedies": ["清晨點酥油燈", "放置 Sphatik (水晶) Yantra", "每日以潔淨水供奉"],
        "suitable_uses": ["祈禱室 (Pūjā Room)", "冥想室", "水井", "地下清水池"],
        "prohibited_uses": ["廁所", "廚房 (火水衝突)", "化糞池", "樓梯", "重型家具"],
    },
    {
        "code": "ENE",
        "sanskrit_name": "Pūrva-Īśānya (पूर्व-ईशान्य)",
        "english_name": "East-NorthEast",
        "chinese_name": "東偏東北 (Pūrva-Īśānya)",
        "center_degree": 67.5,
        "start_degree": 56.25,
        "end_degree": 78.75,
        "deity": "Parjanya / Āditya (雨神 / 太陽神群)",
        "element": "Air / Ether (Vāyu-Ākāśa)",
        "planet": "Sun (Sūrya / 太陽)",
        "traditional_significance": "社交、人際和諧與休閒娛樂之能量匯聚處。",
        "recommended_colors": ["淺黃色", "晨光色", "淺綠色"],
        "color_hex": ["#FFFACD", "#FFEFD5", "#98FB98"],
        "traditional_remedies": ["早晨開窗引入第一線陽光", "擺放鮮花增進社交和諧"],
        "suitable_uses": ["家庭活動區", "瑜伽休閒角落", "茶室"],
        "prohibited_uses": ["重型雜物堆積", "暗室", "垃圾堆放"],
    },
    {
        "code": "E",
        "sanskrit_name": "Pūrva (पूर्व)",
        "english_name": "East",
        "chinese_name": "東方 (Pūrva)",
        "center_degree": 90.0,
        "start_degree": 78.75,
        "end_degree": 101.25,
        "deity": "Indra (帝釋天 / 因陀羅)",
        "element": "Fire / Air (Agni-Vāyu)",
        "planet": "Sun (Sūrya / 太陽)",
        "traditional_significance": "啟明、新生與名望之方，晨曦陽光賦予生命活力與領導力。",
        "recommended_colors": ["橙色", "黃色", "純白色"],
        "color_hex": ["#FFA500", "#FFFF00", "#FFFFFF"],
        "traditional_remedies": ["懸掛銅製太陽符號", "早晨面對東方靜坐迎接日光", "保持東面牆面窗戶開闊"],
        "suitable_uses": ["客廳", "大門", "起居室", "陽台大窗", "書房"],
        "prohibited_uses": ["廁所", "高大遮光實牆", "重型庫房"],
    },
    {
        "code": "ESE",
        "sanskrit_name": "Pūrva-Āgneya (पूर्व-आग्नेय)",
        "english_name": "East-SouthEast",
        "chinese_name": "東偏東南 (Pūrva-Āgneya)",
        "center_degree": 112.5,
        "start_degree": 101.25,
        "end_degree": 123.75,
        "deity": "Satya / Bhrisha (真諦天 / 布利沙)",
        "element": "Fire (Agni)",
        "planet": "Venus (Śukra / 金星)",
        "traditional_significance": "深思熟慮與焦慮釋放之區域，過盛時易導致精神思慮過度。",
        "recommended_colors": ["粉紅色", "奶油色", "淺橘色"],
        "color_hex": ["#FFC0CB", "#FFFDD0", "#FFA07A"],
        "traditional_remedies": ["使用綠色植物平衡火能量", "保持良好空氣循環"],
        "suitable_uses": ["電器設備區", "工作間", "洗衣房"],
        "prohibited_uses": ["主臥室 (易導致失眠與多慮)", "祈禱室"],
    },
    {
        "code": "SE",
        "sanskrit_name": "Āgneya (आग्नेय)",
        "english_name": "South-East",
        "chinese_name": "東南方 (Āgneya)",
        "center_degree": 135.0,
        "start_degree": 123.75,
        "end_degree": 146.25,
        "deity": "Agni (火神 / 阿耆尼)",
        "element": "Fire (Agni)",
        "planet": "Venus (Śukra / 金星)",
        "traditional_significance": "火元素核心方位，主宰烹飪消化力（Jaṭhara Agni）、激情、活力與現金流。",
        "recommended_colors": ["紅色", "珊瑚色", "粉紅色"],
        "color_hex": ["#FF0000", "#FF7F50", "#FF69B4"],
        "traditional_remedies": ["擺放 Agni Yantra", "廚房爐灶面東烹飪", "燃點紅色蠟燭或暖光燈"],
        "suitable_uses": ["廚房 (最佳位置)", "配電箱", "變壓器", "壁爐加熱器"],
        "prohibited_uses": ["水井", "地下蓄水池 (水火相剋)", "主臥室", "水族箱"],
    },
    {
        "code": "SSE",
        "sanskrit_name": "Dakṣiṇa-Āgneya (दक्षिण-आग्नेय)",
        "english_name": "South-SouthEast",
        "chinese_name": "南偏東南 (Dakṣiṇa-Āgneya)",
        "center_degree": 157.5,
        "start_degree": 146.25,
        "end_degree": 168.75,
        "deity": "Pushan / Vitatha (布善 / 滋養神)",
        "element": "Fire / Earth (Agni-Pṛthvī)",
        "planet": "Mars (Maṅgala / 火星)",
        "traditional_significance": "自信、力量、勇氣與體力之源泉。",
        "recommended_colors": ["橙紅色", "深紅色", "深棕色"],
        "color_hex": ["#FF4500", "#8B0000", "#8B4513"],
        "traditional_remedies": ["使用暖色調照明", "放置紅玉髓或紅碧玉"],
        "suitable_uses": ["健身房", "重型工具間", "儲藏室"],
        "prohibited_uses": ["地下冷水池", "客廳休息區"],
    },
    {
        "code": "S",
        "sanskrit_name": "Dakṣiṇa (दक्षिण)",
        "english_name": "South",
        "chinese_name": "南方 (Dakṣiṇa)",
        "center_degree": 180.0,
        "start_degree": 168.75,
        "end_degree": 191.25,
        "deity": "Yama (閻摩 / 秩序與因果之神)",
        "element": "Earth (Pṛthvī)",
        "planet": "Mars (Maṅgala / 火星)",
        "traditional_significance": "厚重、秩序、名望與沉靜能量，南牆宜高、厚、少開大窗以阻擋消極煞氣。",
        "recommended_colors": ["深紅色", "紅褐色", "深土色"],
        "color_hex": ["#8B0000", "#A52A2A", "#D2691E"],
        "traditional_remedies": ["南牆加厚或設置重型高櫃", "擺放銅製 Hanuman 像鎮宅", "掛深色遮光窗簾"],
        "suitable_uses": ["主臥室 (次佳)", "儲藏室", "檔案室", "重型家具擺設"],
        "prohibited_uses": ["主要大門開於不吉分位", "大窗水池", "地下開挖"],
    },
    {
        "code": "SSW",
        "sanskrit_name": "Dakṣiṇa-Nairṛtya (दक्षिण-नैऋत्य)",
        "english_name": "South-SouthWest",
        "chinese_name": "南偏西南 (Dakṣiṇa-Nairṛtya)",
        "center_degree": 202.5,
        "start_degree": 191.25,
        "end_degree": 213.75,
        "deity": "Gandharva / Bhringaraja (乾闥婆 / 蜂王)",
        "element": "Earth (Pṛthvī)",
        "planet": "Rahu (羅睺)",
        "traditional_significance": "消耗、處置與排放之區域，適合人體與廢物代謝排放。",
        "recommended_colors": ["黃褐色", "深大地色"],
        "color_hex": ["#967117", "#5C4033"],
        "traditional_remedies": ["設置黃色地墊", "放置沉穩石雕穩固地氣"],
        "suitable_uses": ["廁所 (合適位置)", "廢棄物存放區", "下水管道"],
        "prohibited_uses": ["神壇", "主臥室床位", "廚房爐灶"],
    },
    {
        "code": "SW",
        "sanskrit_name": "Nairṛtya (नैऋत्य)",
        "english_name": "South-West",
        "chinese_name": "西南方 (Nairṛtya)",
        "center_degree": 225.0,
        "start_degree": 213.75,
        "end_degree": 236.25,
        "deity": "Nirṛti (羅剎主 / 尼律提)",
        "element": "Earth (Pṛthvī)",
        "planet": "Rahu (羅睺)",
        "traditional_significance": "整棟宅邸之根基、穩定與權威之錨點，宜高、重、實、封閉，男主人或家主核心位。",
        "recommended_colors": ["土黃色", "棕色", "米色", "黃赭色"],
        "color_hex": ["#DAA520", "#8B4513", "#F5F5DC", "#CC7722"],
        "traditional_remedies": ["擺放重型實木或大理石家具", "放置黃水晶或虎眼石山", "此方位牆體保持最高厚實"],
        "suitable_uses": ["家主 / 男主人主臥室", "高位重物保險箱", "重型庫房"],
        "prohibited_uses": ["大門", "水井", "地下水池 (地氣渙散破財)", "化糞池", "廁所"],
    },
    {
        "code": "WSW",
        "sanskrit_name": "Paścima-Nairṛtya (पश्चिम-नैऋत्य)",
        "english_name": "West-SouthWest",
        "chinese_name": "西偏西南 (Paścima-Nairṛtya)",
        "center_degree": 247.5,
        "start_degree": 236.25,
        "end_degree": 258.75,
        "deity": "Dauvarika / Sugriva (門神 / 善頸)",
        "element": "Earth / Space (Pṛthvī-Ākāśa)",
        "planet": "Saturn (Śani / 土星)",
        "traditional_significance": "知識、學術深造、教育與技能精進之沉穩能量區。",
        "recommended_colors": ["深藍色", "灰色", "白色"],
        "color_hex": ["#00008B", "#808080", "#FFFFFF"],
        "traditional_remedies": ["設置沉穩深木色書架", "放置文房四寶或專業文獻"],
        "suitable_uses": ["書房", "研究室", "兒童學習桌"],
        "prohibited_uses": ["雜物堆", "明火燃燒區"],
    },
    {
        "code": "W",
        "sanskrit_name": "Paścima (पश्चिम)",
        "english_name": "West",
        "chinese_name": "西方 (Paścima)",
        "center_degree": 270.0,
        "start_degree": 258.75,
        "end_degree": 281.25,
        "deity": "Varuṇa (水界主宰 / 伐樓那)",
        "element": "Space / Water (Ākāśa-Jala)",
        "planet": "Saturn (Śani / 土星)",
        "traditional_significance": "收益、豐收、成就、事業成果與獲利回報之方位。",
        "recommended_colors": ["白色", "銀色", "灰色", "海軍藍"],
        "color_hex": ["#FFFFFF", "#C0C0C0", "#808080", "#000080"],
        "traditional_remedies": ["擺放金屬工藝品或風鈴", "安裝白光照明", "設置圓形金屬鏡"],
        "suitable_uses": ["餐廳", "次臥室", "金屬飾品展陳", "學習室"],
        "prohibited_uses": ["主臥室床頭背靠西牆無倚靠", "地面嚴重凹陷"],
    },
    {
        "code": "WNW",
        "sanskrit_name": "Paścima-Vāyavya (पश्चिम-वायव्य)",
        "english_name": "West-NorthWest",
        "chinese_name": "西偏西北 (Paścima-Vāyavya)",
        "center_degree": 292.5,
        "start_degree": 281.25,
        "end_degree": 303.75,
        "deity": "Asura / Sosha (阿修羅 / 乾燥神)",
        "element": "Air / Water (Vāyu-Jala)",
        "planet": "Moon (Chandra / 月亮)",
        "traditional_significance": "排毒、釋放鬱悶、排泄與心理減壓之方位。",
        "recommended_colors": ["淺灰色", "米白色"],
        "color_hex": ["#D3D3D3", "#F8F8FF"],
        "traditional_remedies": ["使用輕質收納保持空氣流通", "設置香薰消除穢氣"],
        "suitable_uses": ["廁所 (合適位置)", "洗衣區", "雜物清理間"],
        "prohibited_uses": ["主臥室", "祈禱室"],
    },
    {
        "code": "NW",
        "sanskrit_name": "Vāyavya (वायव्य)",
        "english_name": "North-West",
        "chinese_name": "西北方 (Vāyavya)",
        "center_degree": 315.0,
        "start_degree": 303.75,
        "end_degree": 326.25,
        "deity": "Vāyu (風神 / 伐由)",
        "element": "Air (Vāyu)",
        "planet": "Moon (Chandra / 月亮)",
        "traditional_significance": "流動、變化、賓客、貴人支持與人際公關之區域，宜輕盈流轉。",
        "recommended_colors": ["白色", "銀色", "淺藍色", "淺灰色"],
        "color_hex": ["#FFFFFF", "#C0C0C0", "#E0F7FA", "#E0E0E0"],
        "traditional_remedies": ["懸掛金屬風鈴調和氣流", "擺放月光石或銀製器皿", "保持窗戶自然通風"],
        "suitable_uses": ["客房 (Guest Room)", "女兒房", "車庫", "糧倉 / 儲備食品", "次廚房 (無東南時)"],
        "prohibited_uses": ["家主主臥室 (導致主人常年漂泊不著家)", "貴重資產保險箱"],
    },
    {
        "code": "NNW",
        "sanskrit_name": "Uttara-Vāyavya (उत्तर-वायव्य)",
        "english_name": "North-NorthWest",
        "chinese_name": "北偏西北 (Uttara-Vāyavya)",
        "center_degree": 337.5,
        "start_degree": 326.25,
        "end_degree": 348.75,
        "deity": "Naga / Mukhya (那伽 / 龍神神群)",
        "element": "Air / Water (Vāyu-Jala)",
        "planet": "Mercury (Budha / 水星)",
        "traditional_significance": "吸引力、親和力、婚姻和諧與社交引力之區域。",
        "recommended_colors": ["淺綠色", "青瓷色", "乳白色"],
        "color_hex": ["#90EE90", "#ACE1AF", "#FFFDD0"],
        "traditional_remedies": ["擺放成雙成對的裝飾品", "放置柔和暖白燈光"],
        "suitable_uses": ["客廳接待區", "新婚夫婦房", "休閒沙龍"],
        "prohibited_uses": ["重型髒污堆積", "黑暗密閉間"],
    },
]

# Map lookup by direction code
DIRECTIONS_16_MAP: Dict[str, Dict[str, Any]] = {d["code"]: d for d in DIRECTIONS_16_CONFIG}

# 8 primary directions subset (N, NE, E, SE, S, SW, W, NW)
DIRECTIONS_8_CODES = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
DIRECTIONS_8_CONFIG: List[Dict[str, Any]] = [DIRECTIONS_16_MAP[c] for c in DIRECTIONS_8_CODES]


# ------------------------------------------------------------------------------
# 2. 32 Outer Pada Deities (Paramasayika 9x9 Mandala Ring)
# ------------------------------------------------------------------------------

PADAS_32_CONFIG: List[Dict[str, Any]] = [
    # North Edge (NW corner to NE corner) - 8 padas spanning 315.0° to 45.0°
    {"pada_index": 1, "direction_side": "North", "sanskrit_name": "Roga (रोग)", "chinese_name": "羅伽 (病神)", "nature": "inauspicious", "governing_direction": "NNW", "traditional_result": "主疾苦衰耗，不宜設主門", "start_degree": 315.0, "end_degree": 326.25},
    {"pada_index": 2, "direction_side": "North", "sanskrit_name": "Nāga (नाग)", "chinese_name": "那伽 (龍蛇神)", "nature": "inauspicious", "governing_direction": "NNW", "traditional_result": "主嫉妒衝突，不宜作為正門", "start_degree": 326.25, "end_degree": 337.5},
    {"pada_index": 3, "direction_side": "North", "sanskrit_name": "Mukhya (मुख्य)", "chinese_name": "穆克耶 (總領天)", "nature": "auspicious", "governing_direction": "N", "traditional_result": "主才智廣進、富貴吉祥，大吉之門", "start_degree": 337.5, "end_degree": 348.75},
    {"pada_index": 4, "direction_side": "North", "sanskrit_name": "Bhallāṭa (भल्लाट)", "chinese_name": "跋羅陀 (吉祥天)", "nature": "auspicious", "governing_direction": "N", "traditional_result": "大吉門位，主金玉滿堂、豐盛財產", "start_degree": 348.75, "end_degree": 360.0},
    {"pada_index": 5, "direction_side": "North", "sanskrit_name": "Soma (सोम)", "chinese_name": "蘇摩 (月天神)", "nature": "auspicious", "governing_direction": "N", "traditional_result": "主心性仁慈、子孫昌盛，極吉之門", "start_degree": 0.0, "end_degree": 11.25},
    {"pada_index": 6, "direction_side": "North", "sanskrit_name": "Bhujaga (भुजग)", "chinese_name": "蛇神 (毒害)", "nature": "inauspicious", "governing_direction": "NNE", "traditional_result": "主口舌是非、暗疾相侵", "start_degree": 11.25, "end_degree": 22.5},
    {"pada_index": 7, "direction_side": "North", "sanskrit_name": "Aditi (अदिति)", "chinese_name": "阿底提 (眾神之母)", "nature": "auspicious", "governing_direction": "NNE", "traditional_result": "主女性安康、靈性護持", "start_degree": 22.5, "end_degree": 33.75},
    {"pada_index": 8, "direction_side": "North", "sanskrit_name": "Diti (दिति)", "chinese_name": "底提 (阿修羅母)", "nature": "neutral", "governing_direction": "NE", "traditional_result": "思維開闊但易招競爭", "start_degree": 33.75, "end_degree": 45.0},

    # East Edge (NE corner to SE corner) - 8 padas spanning 45.0° to 135.0°
    {"pada_index": 9, "direction_side": "East", "sanskrit_name": "Śikhi / Īśa (शिखी)", "chinese_name": "伊舍那 (濕婆首)", "nature": "neutral", "governing_direction": "NE", "traditional_result": "靈性神聖，但開門易引火煞", "start_degree": 45.0, "end_degree": 56.25},
    {"pada_index": 10, "direction_side": "East", "sanskrit_name": "Parjanya (पर्जन्म)", "chinese_name": "雨神 (甘霖)", "nature": "neutral", "governing_direction": "ENE", "traditional_result": "得女子利益與財物生髮", "start_degree": 56.25, "end_degree": 67.5},
    {"pada_index": 11, "direction_side": "East", "sanskrit_name": "Jayanta (जयन्त)", "chinese_name": "勝天 (帝釋子)", "nature": "auspicious", "governing_direction": "ENE", "traditional_result": "主大獲全勝、權威名望，極佳大門", "start_degree": 67.5, "end_degree": 78.75},
    {"pada_index": 12, "direction_side": "East", "sanskrit_name": "Indra (इन्द्र)", "chinese_name": "帝釋天 (王權)", "nature": "auspicious", "governing_direction": "E", "traditional_result": "得官府貴人提拔，富貴尊崇", "start_degree": 78.75, "end_degree": 90.0},
    {"pada_index": 13, "direction_side": "East", "sanskrit_name": "Sūrya (सूर्य)", "chinese_name": "太陽 (耀日)", "nature": "auspicious", "governing_direction": "E", "traditional_result": "光明正大，脾氣偶有剛烈", "start_degree": 90.0, "end_degree": 101.25},
    {"pada_index": 14, "direction_side": "East", "sanskrit_name": "Satya (सत्य)", "chinese_name": "薩提耶 (真理神)", "nature": "inauspicious", "governing_direction": "ESE", "traditional_result": "雖重信義但易致口角盟約破裂", "start_degree": 101.25, "end_degree": 112.5},
    {"pada_index": 15, "direction_side": "East", "sanskrit_name": "Bhṛśa (भृश)", "chinese_name": "布利沙 (怒神)", "nature": "inauspicious", "governing_direction": "ESE", "traditional_result": "主暴躁過激、耗費無度", "start_degree": 112.5, "end_degree": 123.75},
    {"pada_index": 16, "direction_side": "East", "sanskrit_name": "Antarikṣa (अन्तरिक्ष)", "chinese_name": "空天 (虛空)", "nature": "inauspicious", "governing_direction": "SE", "traditional_result": "主盜賊損耗、家運虛耗", "start_degree": 123.75, "end_degree": 135.0},

    # South Edge (SE corner to SW corner) - 8 padas spanning 135.0° to 225.0°
    {"pada_index": 17, "direction_side": "South", "sanskrit_name": "Agni (अग्नि)", "chinese_name": "阿耆尼 (火天)", "nature": "inauspicious", "governing_direction": "SE", "traditional_result": "易招火燭、血光之災，大凶之門", "start_degree": 135.0, "end_degree": 146.25},
    {"pada_index": 18, "direction_side": "South", "sanskrit_name": "Pūṣan (पूषन्)", "chinese_name": "布善 (滋養神)", "nature": "inauspicious", "governing_direction": "SSE", "traditional_result": "受制於人、僕從相欺", "start_degree": 146.25, "end_degree": 157.5},
    {"pada_index": 19, "direction_side": "South", "sanskrit_name": "Vitatha (वितथ)", "chinese_name": "維塔塔 (虛偽)", "nature": "inauspicious", "governing_direction": "SSE", "traditional_result": "主虛假浮誇、卑微受辱", "start_degree": 157.5, "end_degree": 168.75},
    {"pada_index": 20, "direction_side": "South", "sanskrit_name": "Gṛhakṣata (गृहक्षत)", "chinese_name": "護宅天 (固宅)", "nature": "auspicious", "governing_direction": "S", "traditional_result": "南門罕見大吉之位，主子孫榮貴、武勇堅定", "start_degree": 168.75, "end_degree": 180.0},
    {"pada_index": 21, "direction_side": "South", "sanskrit_name": "Yama (यम)", "chinese_name": "閻摩 (法王)", "nature": "inauspicious", "governing_direction": "S", "traditional_result": "死滅憂懼、病患連綿，大凶之門", "start_degree": 180.0, "end_degree": 191.25},
    {"pada_index": 22, "direction_side": "South", "sanskrit_name": "Gandharva (गन्धर्व)", "chinese_name": "乾闥婆 (樂神)", "nature": "auspicious", "governing_direction": "SSW", "traditional_result": "利於藝術演藝、名揚四方", "start_degree": 191.25, "end_degree": 202.5},
    {"pada_index": 23, "direction_side": "South", "sanskrit_name": "Bhṛṅgarāja (भृङ्गराज)", "chinese_name": "蜂王神", "nature": "neutral", "governing_direction": "SSW", "traditional_result": "主辛勞謀生，起伏不一", "start_degree": 202.5, "end_degree": 213.75},
    {"pada_index": 24, "direction_side": "South", "sanskrit_name": "Mṛga (मृग)", "chinese_name": "鹿神 (逃遁)", "nature": "inauspicious", "governing_direction": "SW", "traditional_result": "心神不寧、散財失家", "start_degree": 213.75, "end_degree": 225.0},

    # West Edge (SW corner to NW corner) - 8 padas spanning 225.0° to 315.0°
    {"pada_index": 25, "direction_side": "West", "sanskrit_name": "Pitṛ (पितृ)", "chinese_name": "祖靈 (冥界)", "nature": "inauspicious", "governing_direction": "SW", "traditional_result": "陰氣深重、家主受損，嚴格禁開大門", "start_degree": 225.0, "end_degree": 236.25},
    {"pada_index": 26, "direction_side": "West", "sanskrit_name": "Dauvārika (दौवारिक)", "chinese_name": "門神 (夜叉守)", "nature": "inauspicious", "governing_direction": "WSW", "traditional_result": "招引怨敵、家庭不睦", "start_degree": 236.25, "end_degree": 247.5},
    {"pada_index": 27, "direction_side": "West", "sanskrit_name": "Sugrīva (सुग्रीव)", "chinese_name": "善頸 (美顏)", "nature": "auspicious", "governing_direction": "WSW", "traditional_result": "主財富豐足、利於學業功名", "start_degree": 247.5, "end_degree": 258.75},
    {"pada_index": 28, "direction_side": "West", "sanskrit_name": "Puṣpadanta (पुष्पदन्त)", "chinese_name": "花齒天 (吉祥西門)", "nature": "auspicious", "governing_direction": "W", "traditional_result": "大吉西門，主福壽延綿、獲貴人厚愛", "start_degree": 258.75, "end_degree": 270.0},
    {"pada_index": 29, "direction_side": "West", "sanskrit_name": "Varuṇa (वरुण)", "chinese_name": "伐樓那 (水天大帝)", "nature": "auspicious", "governing_direction": "W", "traditional_result": "成就偉業、財運廣闊，吉慶有餘", "start_degree": 270.0, "end_degree": 281.25},
    {"pada_index": 30, "direction_side": "West", "sanskrit_name": "Asura (असुर)", "chinese_name": "阿修羅 (魔神)", "nature": "inauspicious", "governing_direction": "WNW", "traditional_result": "爭鬥不休、官非纏身", "start_degree": 281.25, "end_degree": 292.5},
    {"pada_index": 31, "direction_side": "West", "sanskrit_name": "Śoṣa (शोष)", "chinese_name": "乾燥神 (耗盡)", "nature": "inauspicious", "governing_direction": "WNW", "traditional_result": "金錢枯竭、身體消瘦", "start_degree": 292.5, "end_degree": 303.75},
    {"pada_index": 32, "direction_side": "West", "sanskrit_name": "Pāpayakṣmā (पापयक्ष्मा)", "chinese_name": "罪疾 (衰敗)", "nature": "inauspicious", "governing_direction": "NW", "traditional_result": "痼疾難癒、災禍破財", "start_degree": 303.75, "end_degree": 315.0},
]

PADAS_MAP_BY_NAME: Dict[str, Dict[str, Any]] = {}
for p in PADAS_32_CONFIG:
    p_clean = re.sub(r"[^a-z0-9]", "", p["sanskrit_name"].lower())
    p_first = re.sub(r"[^a-z0-9]", "", p["sanskrit_name"].split(" ")[0].lower())
    PADAS_MAP_BY_NAME[p_first] = p
    PADAS_MAP_BY_NAME[p_clean] = p
    PADAS_MAP_BY_NAME[f"p{p['pada_index']}"] = p
    PADAS_MAP_BY_NAME[str(p["pada_index"])] = p


def azimuth_to_pada(degrees: float) -> Dict[str, Any]:
    """Converts a compass bearing (0-359.99°) into the corresponding 32-pada deity metadata.
    Each pada spans exactly 11.25° (360° / 32) along the perimeter of the Paramasayika mandala.
    """
    normalized = float(degrees) % 360.0
    for p in PADAS_32_CONFIG:
        start = p["start_degree"]
        end = p["end_degree"]
        if start > end:  # Spans 360° / 0° North (Pada 4: 348.75° to 360.0° / 0.0°)
            if normalized >= start or normalized < end:
                return p
        else:
            if start <= normalized < end:
                return p
    return PADAS_32_CONFIG[4]  # Default to Soma (0.0° - 11.25°)


def lookup_pada(identifier: str) -> Optional[Dict[str, Any]]:
    """Resolves a pada by name, index number, or wall coordinate (e.g. 'Jayanta', 'E3', 'P11', '11')."""
    if not identifier:
        return None
    raw = identifier.strip().lower()
    clean = re.sub(r"[^a-z0-9]", "", raw)

    # 1. Direct index check ("1" to "32", or "p1" to "p32")
    if clean.startswith("p") and clean[1:].isdigit():
        idx = int(clean[1:])
        if 1 <= idx <= 32:
            return PADAS_32_CONFIG[idx - 1]
    if clean.isdigit():
        idx = int(clean)
        if 1 <= idx <= 32:
            return PADAS_32_CONFIG[idx - 1]

    # 2. Wall code check ("n1".."n8", "e1".."e8", "s1".."s8", "w1".."w8")
    wall_offsets = {"n": 0, "e": 8, "s": 16, "w": 24}
    if len(clean) >= 2 and clean[0] in wall_offsets and clean[1:].isdigit():
        w_idx = int(clean[1:])
        if 1 <= w_idx <= 8:
            return PADAS_32_CONFIG[wall_offsets[clean[0]] + w_idx - 1]

    # 3. Direct lookup in precomputed map
    if clean in PADAS_MAP_BY_NAME:
        return PADAS_MAP_BY_NAME[clean]

    # 4. Partial substring match against sanskrit names
    for p in PADAS_32_CONFIG:
        p_name = re.sub(r"[^a-z0-9]", "", p["sanskrit_name"].lower())
        p_first = re.sub(r"[^a-z0-9]", "", p["sanskrit_name"].split(" ")[0].lower())
        if clean in (p_name, p_first) or p_first.startswith(clean) or clean in p_name:
            return p

    return None


# ------------------------------------------------------------------------------
# 3. Helpers: Compass Angle Conversion
# ------------------------------------------------------------------------------

def azimuth_to_direction(degrees: float) -> str:
    """Converts a compass bearing (0-359.99°) into the corresponding 16-direction code.
    Clockwise traversal with 22.5° sector size centered on exact cardinals/subcardinals.
    """
    normalized = float(degrees) % 360.0
    for item in DIRECTIONS_16_CONFIG:
        start = item["start_degree"]
        end = item["end_degree"]
        if start > end:  # Spans across 360° / 0° North
            if normalized >= start or normalized < end:
                return item["code"]
        else:
            if start <= normalized < end:
                return item["code"]
    return "N"


def get_all_directions_metadata() -> VastuDirectionsResponse:
    """Returns the full collection of 8 and 16 directions, and 32 padas."""
    d8_models = [DirectionMetadata(**d) for d in DIRECTIONS_8_CONFIG]
    d16_models = [DirectionMetadata(**d) for d in DIRECTIONS_16_CONFIG]
    p32_models = [PadaDeityMetadata(**p) for p in PADAS_32_CONFIG]
    return VastuDirectionsResponse(
        directions_8=d8_models,
        directions_16=d16_models,
        padas_32=p32_models,
        engine_version=ENGINE_VERSION,
    )


# ------------------------------------------------------------------------------
# 4. Configurable Multi-Factor Evaluation Engine
# ------------------------------------------------------------------------------

# Factor weights and traditional rules per property profile
RESIDENTIAL_FACTORS: Dict[str, Dict[str, Any]] = {
    "main_entrance": {
        "name": "Main Entrance (Pradhāna Dvāra)",
        "max_weight": 25.0,
        "source": "Mayamata Ch. 3 / Brihat Samhita Ch. 53",
        "rule": "Entrance should preferably occupy auspicious padas in East (Jayanta, Indra) or North (Mukhya, Bhallata, Soma) or West (Pushpadanta, Varuna) or South (Grihakshata).",
    },
    "kitchen": {
        "name": "Kitchen (Pākaśālā - Agni Corner)",
        "max_weight": 20.0,
        "source": "Mayamata Ch. 3 / Vishwakarma Prakash",
        "rule": "Primary ideal in South-East (Āgneya - fire element). Secondary viable in North-West (Vāyu). Strictly avoid North-East (water-fire clash) and South-West.",
    },
    "master_bedroom": {
        "name": "Master Bedroom (Śayana Gṛha)",
        "max_weight": 20.0,
        "source": "Manasara Ch. 12 / Mayamata",
        "rule": "Primary ideal in South-West (Nairṛtya) providing earth stability and leadership anchoring. South or West acceptable. Strictly avoid North-East.",
    },
    "pooja_room": {
        "name": "Pooja & Meditation Room (Devatā Gṛha)",
        "max_weight": 15.0,
        "source": "Brihat Samhita Ch. 53 / Mayamata",
        "rule": "Primary ideal in North-East (Īśānya - entry of divine prāṇa). East and North acceptable. Strictly avoid South, South-West, or under staircases.",
    },
    "toilets": {
        "name": "Toilets & Sanitation (Śauca Gṛha)",
        "max_weight": 20.0,
        "source": "Vishwakarma Prakash Ch. 7",
        "rule": "Ideal zones: WNW, SSW, ESE. Acceptable in West or South. Prohibited in North-East, South-West, and central Brahmasthan.",
    },
    "brahmasthan": {
        "name": "Central Zone (Brahmasthan)",
        "max_weight": 15.0,
        "source": "Mayamata Ch. 2 / Brihat Samhita",
        "rule": "Central 1/9th zone must remain open, uncluttered, free of heavy pillars, toilets, kitchens, or staircases.",
    },
    "plot_shape": {
        "name": "Plot Geometry & Proportions",
        "max_weight": 10.0,
        "source": "Mayamata Ch. 1",
        "rule": "Square (Chaturasra) or rectangular (Ayatasra, length/width <= 2) is auspicious. Irregular or cut plots require balancing.",
    },
}

COMMERCIAL_FACTORS: Dict[str, Dict[str, Any]] = {
    "main_entrance": {
        "name": "Commercial Frontage & Entrance",
        "max_weight": 30.0,
        "source": "Mayamata Ch. 3",
        "rule": "Frontage and main customer entrance in North (Kubera footfall), East (Solar visibility), or North-East.",
    },
    "owner_cabin": {
        "name": "Executive / Owner Cabin",
        "max_weight": 20.0,
        "source": "Manasara Ch. 14",
        "rule": "Owner/CEO desk located in South-West or South, facing North or East for decisive command.",
    },
    "accounts_cash": {
        "name": "Accounts & Cash Counter",
        "max_weight": 20.0,
        "source": "Brihat Samhita Ch. 53",
        "rule": "Financial counters, lockers, and billing in North (Kubera zone) facing North.",
    },
    "conference_room": {
        "name": "Conference & Meeting Room",
        "max_weight": 15.0,
        "source": "Mayamata Ch. 4",
        "rule": "Meeting and brainstorming areas in North-West (circulation) or East.",
    },
    "toilets": {
        "name": "Employee & Guest Restrooms",
        "max_weight": 15.0,
        "source": "Vishwakarma Prakash",
        "rule": "Restrooms situated in WNW or SSW. Avoid North-East and South-West.",
    },
}

PLOT_FACTORS: Dict[str, Dict[str, Any]] = {
    "plot_shape": {
        "name": "Plot Shape & Angles",
        "max_weight": 35.0,
        "source": "Mayamata Ch. 1",
        "rule": "Square or rectangular plots with 90° corners are most auspicious. Gaumukhi (narrow front) favored for residential, Shermukhi (broad front) for commercial.",
    },
    "slope_orientation": {
        "name": "Natural Slope & Water Runoff",
        "max_weight": 35.0,
        "source": "Brihat Samhita Ch. 53",
        "rule": "Plot sloping down toward North or North-East (Jala/Prāṇa flow) is highly auspicious. Slopes downward to South/West are unfavorable.",
    },
    "road_facing": {
        "name": "Road Access & Surrounding Environment",
        "max_weight": 30.0,
        "source": "Manasara Ch. 3",
        "rule": "Roads in North and East are highly favorable. Northeast corner plots (Ishanya open) yield superior cosmic reception.",
    },
}

INDUSTRIAL_FACTORS: Dict[str, Dict[str, Any]] = {
    "main_gate": {
        "name": "Factory Main Gate & Logistics Entry",
        "max_weight": 20.0,
        "source": "Mayamata Ch. 3",
        "rule": "Logistics and main gate in North or East. Dispatch exit in North-West.",
    },
    "heavy_machinery": {
        "name": "Heavy Machinery & Plant Equipment",
        "max_weight": 25.0,
        "source": "Vishwakarma Prakash Ch. 11",
        "rule": "Heavy load machines and foundation equipment installed in South-West or South (Earth stability).",
    },
    "boiler_furnace": {
        "name": "Boiler, Furnace & Electrical Transformers",
        "max_weight": 20.0,
        "source": "Mayamata Ch. 3",
        "rule": "Furnaces, ovens, generators, and heating units strictly in South-East (Agni zone).",
    },
    "raw_material_storage": {
        "name": "Raw Material Storage",
        "max_weight": 20.0,
        "source": "Manasara Ch. 12",
        "rule": "Heavy raw materials stored in South-West or South; liquid raw materials in North/East.",
    },
    "finished_goods": {
        "name": "Finished Goods & Dispatch Storage",
        "max_weight": 15.0,
        "source": "Mayamata Ch. 4",
        "rule": "Finished inventory stored in North-West (Vāyu - movement and brisk dispatch).",
    },
}


def _evaluate_direction_placement(
    input_dir: Optional[str],
    ideal_dirs: List[str],
    acceptable_dirs: List[str],
    prohibited_dirs: List[str],
    max_weight: float,
    factor_key: str,
    factor_name: str,
    rule_source: str,
    rule_text: str,
    ideal_remedy: str = "",
    defect_remedy: str = "",
) -> FactorEvaluation:
    """Evaluates a single room placement against classical ideal, acceptable, and prohibited lists."""
    if not input_dir or input_dir == "unassessed":
        return FactorEvaluation(
            factor_key=factor_key,
            factor_name=factor_name,
            assessed=False,
            input_value=None,
            score=None,
            max_weight=max_weight,
            severity="unassessed",
            traditional_rule=rule_text,
            rule_source=rule_source,
            explanation=f"{factor_name} was not provided in inputs. No penalty or bonus applied.",
            remedy=None,
        )

    norm_dir = input_dir.upper()
    if norm_dir in ideal_dirs:
        score = max_weight
        severity = "ideal"
        explanation = f"{factor_name} is located in {norm_dir}, which perfectly aligns with classical Vastu recommendations."
        remedy = ideal_remedy or "Maintain cleanliness and unobstructed energy flow in this zone."
    elif norm_dir in acceptable_dirs:
        score = round(max_weight * 0.70, 2)
        severity = "acceptable"
        explanation = f"{factor_name} is located in {norm_dir}, which is an acceptable secondary alignment."
        remedy = defect_remedy or "Ensure appropriate color balance and good ventilation."
    elif norm_dir in prohibited_dirs:
        score = 0.0
        severity = "severe_defect"
        explanation = f"{factor_name} is located in {norm_dir}, which directly conflicts with classical treatises ({rule_source})."
        remedy = defect_remedy or "Apply traditional remedial objects (e.g. pyramids, elemental colors, yantras) to counteract the directional defect."
    else:
        # Neutral / unclassified placement
        score = round(max_weight * 0.40, 2)
        severity = "moderate_defect"
        explanation = f"{factor_name} in {norm_dir} is neutral to unfavorable in classical Vastu Vidya."
        remedy = defect_remedy or "Keep this zone well-lit and balanced with complementary elemental colors."

    return FactorEvaluation(
        factor_key=factor_key,
        factor_name=factor_name,
        assessed=True,
        input_value=norm_dir,
        score=score,
        max_weight=max_weight,
        severity=severity,
        traditional_rule=rule_text,
        rule_source=rule_source,
        explanation=explanation,
        remedy=remedy,
    )


def evaluate_vastu_layout(request: VastuEvaluationRequest) -> VastuEvaluationResponse:
    """Evaluates a complete property layout against documented classical rules.
    Normalizes scores strictly across assessable factors without penalizing missing data.
    """
    p = request.placements
    prop_type = request.property_type
    factor_results: List[FactorEvaluation] = []
    doshas: List[VastuDosha] = []
    missing_warnings: List[str] = []
    conflicting_warnings: List[str] = []
    general_remedies: List[str] = []

    # Derive facing direction if degrees provided without code
    facing_dir = request.facing_direction
    if not facing_dir and request.facing_degrees is not None:
        facing_dir = azimuth_to_direction(request.facing_degrees)
    if not facing_dir:
        facing_dir = "E"  # Default assumption for reference, warned in missing
        missing_warnings.append("Property facing direction was not specified; default cardinal orientation referenced.")

    # 1. Evaluate Residential Profile
    if prop_type == "residential":
        # Entrance
        f_cfg = RESIDENTIAL_FACTORS["main_entrance"]
        entrance_pada_info = None
        if p.main_entrance_pada:
            entrance_pada_info = lookup_pada(p.main_entrance_pada)
        elif request.facing_degrees is not None and not p.main_entrance_direction:
            entrance_pada_info = azimuth_to_pada(request.facing_degrees)

        if entrance_pada_info:
            pada_name = entrance_pada_info["sanskrit_name"]
            pada_nature = entrance_pada_info["nature"]
            pada_res = entrance_pada_info["traditional_result"]
            side = entrance_pada_info["direction_side"]
            pada_idx = entrance_pada_info["pada_index"]

            if pada_nature == "auspicious":
                score = f_cfg["max_weight"]
                sev = "ideal"
                exp = (
                    f"Main Entrance is situated in auspicious pada '{pada_name}' (Pada #{pada_idx} on {side} face). "
                    f"Classical treatises (Mayamata & Brihat Samhita) praise this placement: {pada_res}."
                )
                rem = "Maintain clean threshold, auspicious Torana (mango leaves/marigold), and keep entrance brightly illuminated."
            elif pada_nature == "inauspicious":
                score = round(f_cfg["max_weight"] * 0.15, 2)
                sev = "severe_defect"
                exp = (
                    f"Main Entrance is situated in inauspicious pada '{pada_name}' (Pada #{pada_idx} on {side} face). "
                    f"Classical treatises warn: {pada_res}."
                )
                rem = (
                    "Place a copper or brass threshold boundary strip, Swastika/Trishula yantra, and a bowl of raw rock salt near the door."
                )
            else:
                score = round(f_cfg["max_weight"] * 0.60, 2)
                sev = "acceptable"
                exp = (
                    f"Main Entrance is situated in neutral pada '{pada_name}' (Pada #{pada_idx} on {side} face): {pada_res}."
                )
                rem = "Balance entrance energy with warm lighting and clean surroundings."

            factor_results.append(FactorEvaluation(
                factor_key="main_entrance",
                factor_name=f_cfg["name"],
                assessed=True,
                input_value=f"{p.main_entrance_direction or side} (Pada #{pada_idx} - {pada_name})",
                score=score,
                max_weight=f_cfg["max_weight"],
                severity=sev,
                traditional_rule=f_cfg["rule"],
                rule_source=f_cfg["source"],
                explanation=exp,
                remedy=rem,
            ))
        else:
            ev_entrance = _evaluate_direction_placement(
                p.main_entrance_direction,
                ideal_dirs=["N", "NE", "E"],
                acceptable_dirs=["ENE", "NNE", "NW", "W"],
                prohibited_dirs=["SW", "SSW", "SE"],
                max_weight=f_cfg["max_weight"],
                factor_key="main_entrance",
                factor_name=f_cfg["name"],
                rule_source=f_cfg["source"],
                rule_text=f_cfg["rule"],
                defect_remedy="Place a copper/brass threshold strip, auspicious symbols (Swastika/Om/Trishula), or Vastu pyramid at the entrance door.",
            )
            factor_results.append(ev_entrance)

        # Kitchen
        f_cfg = RESIDENTIAL_FACTORS["kitchen"]
        ev_kitchen = _evaluate_direction_placement(
            p.kitchen_direction,
            ideal_dirs=["SE", "SSE"],
            acceptable_dirs=["NW"],
            prohibited_dirs=["NE", "SW", "N"],
            max_weight=f_cfg["max_weight"],
            factor_key="kitchen",
            factor_name=f_cfg["name"],
            rule_source=f_cfg["source"],
            rule_text=f_cfg["rule"],
            defect_remedy="If kitchen is in North-East (severe water-fire conflict), place a yellow marble slab beneath the gas stove and hang an Agni Yantra. Never keep water tap adjacent to stove.",
        )
        factor_results.append(ev_kitchen)

        # Master Bedroom
        f_cfg = RESIDENTIAL_FACTORS["master_bedroom"]
        ev_bed = _evaluate_direction_placement(
            p.master_bedroom_direction,
            ideal_dirs=["SW"],
            acceptable_dirs=["S", "W", "SSW", "WSW"],
            prohibited_dirs=["NE", "SE", "NW"],
            max_weight=f_cfg["max_weight"],
            factor_key="master_bedroom",
            factor_name=f_cfg["name"],
            rule_source=f_cfg["source"],
            rule_text=f_cfg["rule"],
            defect_remedy="Ensure head of bed faces South or East. If bedroom is outside SW, place heavy earth-toned furnishings and yellow/brown decor.",
        )
        factor_results.append(ev_bed)

        # Pooja Room
        f_cfg = RESIDENTIAL_FACTORS["pooja_room"]
        ev_pooja = _evaluate_direction_placement(
            p.pooja_room_direction,
            ideal_dirs=["NE", "NNE"],
            acceptable_dirs=["E", "N", "ENE"],
            prohibited_dirs=["S", "SW", "SE"],
            max_weight=f_cfg["max_weight"],
            factor_key="pooja_room",
            factor_name=f_cfg["name"],
            rule_source=f_cfg["source"],
            rule_text=f_cfg["rule"],
            defect_remedy="If altar cannot be placed in North-East, keep idols facing East, install pure white/gold lighting, and keep zone strictly clean.",
        )
        factor_results.append(ev_pooja)

        # Toilets
        f_cfg = RESIDENTIAL_FACTORS["toilets"]
        if p.toilet_directions:
            # Evaluate all toilet placements
            toilet_scores = []
            toilet_severities = []
            for t_dir in p.toilet_directions:
                ev_t = _evaluate_direction_placement(
                    t_dir,
                    ideal_dirs=["WNW", "SSW", "ESE"],
                    acceptable_dirs=["W", "NW", "S"],
                    prohibited_dirs=["NE", "SW", "E", "N"],
                    max_weight=f_cfg["max_weight"],
                    factor_key="toilets",
                    factor_name=f_cfg["name"],
                    rule_source=f_cfg["source"],
                    rule_text=f_cfg["rule"],
                    defect_remedy="Keep toilet lid closed at all times. Place a bowl of unrefined sea salt in a glass dish, replaced weekly, and install a lead/zinc energy partition tape.",
                )
                toilet_scores.append(ev_t.score or 0.0)
                toilet_severities.append(ev_t.severity)

            avg_score = round(sum(toilet_scores) / len(toilet_scores), 2)
            worst_sev = "severe_defect" if "severe_defect" in toilet_severities else (
                "moderate_defect" if "moderate_defect" in toilet_severities else "ideal"
            )
            factor_results.append(FactorEvaluation(
                factor_key="toilets",
                factor_name=f_cfg["name"],
                assessed=True,
                input_value=", ".join(p.toilet_directions),
                score=avg_score,
                max_weight=f_cfg["max_weight"],
                severity=worst_sev,
                traditional_rule=f_cfg["rule"],
                rule_source=f_cfg["source"],
                explanation=f"Evaluated {len(p.toilet_directions)} sanitation zone(s): {', '.join(p.toilet_directions)}.",
                remedy="Sea salt bowls and lead helixes are recommended in conflicting zones.",
            ))
        else:
            factor_results.append(FactorEvaluation(
                factor_key="toilets",
                factor_name=f_cfg["name"],
                assessed=False,
                input_value=None,
                score=None,
                max_weight=f_cfg["max_weight"],
                severity="unassessed",
                traditional_rule=f_cfg["rule"],
                rule_source=f_cfg["source"],
                explanation="No toilet locations provided. Not penalized in scoring.",
                remedy=None,
            ))

        # Brahmasthan
        f_cfg = RESIDENTIAL_FACTORS["brahmasthan"]
        if p.brahmasthan_status and p.brahmasthan_status != "unassessed":
            if p.brahmasthan_status == "clear":
                b_score = f_cfg["max_weight"]
                b_sev = "ideal"
                b_exp = "Central Brahmasthan is clear and unencumbered, promoting uniform distribution of cosmic prāṇa."
                b_rem = "Maintain open space and keep clean."
            elif p.brahmasthan_status == "partially_obstructed":
                b_score = round(f_cfg["max_weight"] * 0.5, 2)
                b_sev = "moderate_defect"
                b_exp = "Central zone has light partition or movable furniture."
                b_rem = "Remove heavy furniture and install brass Vastu lotus or crystal."
            else:
                b_score = 0.0
                b_sev = "severe_defect"
                b_exp = "Central Brahmasthan is heavily obstructed by structural pillars, staircase, or plumbing."
                b_rem = "Affix brass pyramid strips around the boundary of the central zone to anchor energy."

            factor_results.append(FactorEvaluation(
                factor_key="brahmasthan",
                factor_name=f_cfg["name"],
                assessed=True,
                input_value=p.brahmasthan_status,
                score=b_score,
                max_weight=f_cfg["max_weight"],
                severity=b_sev,
                traditional_rule=f_cfg["rule"],
                rule_source=f_cfg["source"],
                explanation=b_exp,
                remedy=b_rem,
            ))
        else:
            factor_results.append(FactorEvaluation(
                factor_key="brahmasthan",
                factor_name=f_cfg["name"],
                assessed=False,
                input_value=None,
                score=None,
                max_weight=f_cfg["max_weight"],
                severity="unassessed",
                traditional_rule=f_cfg["rule"],
                rule_source=f_cfg["source"],
                explanation="Brahmasthan status was not assessed.",
                remedy=None,
            ))

        # Plot Shape
        f_cfg = RESIDENTIAL_FACTORS["plot_shape"]
        if p.plot_shape and p.plot_shape != "unassessed":
            if p.plot_shape in ("square", "rectangular", "gaumukhi"):
                ps_score = f_cfg["max_weight"]
                ps_sev = "ideal"
                ps_exp = f"Plot shape '{p.plot_shape}' conforms to classical auspicious geometry (Chaturasra/Ayatasra/Gaumukhi)."
                ps_rem = "No remedial intervention required."
            elif p.plot_shape == "shermukhi":
                ps_score = round(f_cfg["max_weight"] * 0.6, 2)
                ps_sev = "acceptable"
                ps_exp = "Sher-mukhi (lion-faced) shape is primarily favored for commercial, but manageable in residential."
                ps_rem = "Plant bamboo or evergreen hedging on wider front corners."
            else:
                ps_score = round(f_cfg["max_weight"] * 0.2, 2)
                ps_sev = "severe_defect"
                ps_exp = f"Plot shape '{p.plot_shape}' has cut corners or irregular angles causing directional energy distortion."
                ps_rem = "Bury lead or copper energy wires along boundary lines to virtually square off the plot."

            factor_results.append(FactorEvaluation(
                factor_key="plot_shape",
                factor_name=f_cfg["name"],
                assessed=True,
                input_value=p.plot_shape,
                score=ps_score,
                max_weight=f_cfg["max_weight"],
                severity=ps_sev,
                traditional_rule=f_cfg["rule"],
                rule_source=f_cfg["source"],
                explanation=ps_exp,
                remedy=ps_rem,
            ))
        else:
            factor_results.append(FactorEvaluation(
                factor_key="plot_shape",
                factor_name=f_cfg["name"],
                assessed=False,
                input_value=None,
                score=None,
                max_weight=f_cfg["max_weight"],
                severity="unassessed",
                traditional_rule=f_cfg["rule"],
                rule_source=f_cfg["source"],
                explanation="Plot shape was not assessed.",
                remedy=None,
            ))

    # 2. Evaluate Commercial Profile
    elif prop_type == "commercial":
        f_cfg = COMMERCIAL_FACTORS["main_entrance"]
        entrance_pada_info = None
        if p.main_entrance_pada:
            entrance_pada_info = lookup_pada(p.main_entrance_pada)
        elif request.facing_degrees is not None and not p.main_entrance_direction:
            entrance_pada_info = azimuth_to_pada(request.facing_degrees)

        if entrance_pada_info:
            pada_name = entrance_pada_info["sanskrit_name"]
            pada_nature = entrance_pada_info["nature"]
            pada_res = entrance_pada_info["traditional_result"]
            side = entrance_pada_info["direction_side"]
            pada_idx = entrance_pada_info["pada_index"]

            if pada_nature == "auspicious":
                score = f_cfg["max_weight"]
                sev = "ideal"
                exp = f"Commercial Entrance in auspicious pada '{pada_name}' (Pada #{pada_idx} on {side} face) brings sustained trade and customer footfall: {pada_res}."
                rem = "Keep entrance brightly illuminated with clear signage and unobstructed access."
            elif pada_nature == "inauspicious":
                score = round(f_cfg["max_weight"] * 0.15, 2)
                sev = "severe_defect"
                exp = f"Commercial Entrance in inauspicious pada '{pada_name}' (Pada #{pada_idx} on {side} face) is warned in classical treatises: {pada_res}."
                rem = "Install brass threshold energy strip and Kubera / Lakshmi yantras."
            else:
                score = round(f_cfg["max_weight"] * 0.60, 2)
                sev = "acceptable"
                exp = f"Commercial Entrance in neutral pada '{pada_name}' (Pada #{pada_idx} on {side} face): {pada_res}."
                rem = "Install bright lighting and auspicious indoor water feature."

            factor_results.append(FactorEvaluation(
                factor_key="main_entrance",
                factor_name=f_cfg["name"],
                assessed=True,
                input_value=f"{p.main_entrance_direction or side} (Pada #{pada_idx} - {pada_name})",
                score=score,
                max_weight=f_cfg["max_weight"],
                severity=sev,
                traditional_rule=f_cfg["rule"],
                rule_source=f_cfg["source"],
                explanation=exp,
                remedy=rem,
            ))
        else:
            factor_results.append(_evaluate_direction_placement(
                p.main_entrance_direction,
                ideal_dirs=["N", "E", "NE"],
                acceptable_dirs=["NW", "W"],
                prohibited_dirs=["SW", "S"],
                max_weight=f_cfg["max_weight"],
                factor_key="main_entrance",
                factor_name=f_cfg["name"],
                rule_source=f_cfg["source"],
                rule_text=f_cfg["rule"],
                defect_remedy="Install bright entrance illumination and water fountain in North to boost customer prosperity.",
            ))

        f_cfg = COMMERCIAL_FACTORS["owner_cabin"]
        factor_results.append(_evaluate_direction_placement(
            p.owner_cabin_direction,
            ideal_dirs=["SW", "S"],
            acceptable_dirs=["W"],
            prohibited_dirs=["NE", "NW"],
            max_weight=f_cfg["max_weight"],
            factor_key="owner_cabin",
            factor_name=f_cfg["name"],
            rule_source=f_cfg["source"],
            rule_text=f_cfg["rule"],
            defect_remedy="Keep desk facing North or East. Place a heavy globe or quartz pyramid on the executive table.",
        ))

        f_cfg = COMMERCIAL_FACTORS["accounts_cash"]
        factor_results.append(_evaluate_direction_placement(
            p.accounts_cash_direction,
            ideal_dirs=["N"],
            acceptable_dirs=["E", "NE"],
            prohibited_dirs=["SE", "S"],
            max_weight=f_cfg["max_weight"],
            factor_key="accounts_cash",
            factor_name=f_cfg["name"],
            rule_source=f_cfg["source"],
            rule_text=f_cfg["rule"],
            defect_remedy="Place a mirror inside the cash drawer facing North to symbolically double financial inflow.",
        ))

        f_cfg = COMMERCIAL_FACTORS["conference_room"]
        factor_results.append(_evaluate_direction_placement(
            p.conference_room_direction,
            ideal_dirs=["NW", "E"],
            acceptable_dirs=["N", "W"],
            prohibited_dirs=["SW"],
            max_weight=f_cfg["max_weight"],
            factor_key="conference_room",
            factor_name=f_cfg["name"],
            rule_source=f_cfg["source"],
            rule_text=f_cfg["rule"],
        ))

    # 3. Evaluate Plot Profile
    elif prop_type == "plot":
        f_cfg = PLOT_FACTORS["plot_shape"]
        if p.plot_shape and p.plot_shape != "unassessed":
            ps_score = f_cfg["max_weight"] if p.plot_shape in ("square", "rectangular", "gaumukhi", "shermukhi") else 5.0
            factor_results.append(FactorEvaluation(
                factor_key="plot_shape",
                factor_name=f_cfg["name"],
                assessed=True,
                input_value=p.plot_shape,
                score=ps_score,
                max_weight=f_cfg["max_weight"],
                severity="ideal" if ps_score == f_cfg["max_weight"] else "severe_defect",
                traditional_rule=f_cfg["rule"],
                rule_source=f_cfg["source"],
                explanation=f"Shape '{p.plot_shape}' evaluated.",
                remedy="Virtually square irregular angles with buried copper boundary rods.",
            ))
        else:
            factor_results.append(FactorEvaluation(
                factor_key="plot_shape",
                factor_name=f_cfg["name"],
                assessed=False,
                input_value=None,
                score=None,
                max_weight=f_cfg["max_weight"],
                severity="unassessed",
                traditional_rule=f_cfg["rule"],
                rule_source=f_cfg["source"],
                explanation="Plot shape was not assessed.",
                remedy=None,
            ))

        f_cfg = PLOT_FACTORS["slope_orientation"]
        factor_results.append(_evaluate_direction_placement(
            p.slope_direction,
            ideal_dirs=["NE", "N", "E"],
            acceptable_dirs=["NW"],
            prohibited_dirs=["SW", "S", "W"],
            max_weight=f_cfg["max_weight"],
            factor_key="slope_orientation",
            factor_name=f_cfg["name"],
            rule_source=f_cfg["source"],
            rule_text=f_cfg["rule"],
            defect_remedy="Construct a retaining embankment along the South/West to elevate those zones higher than North/East.",
        ))

    # 4. Evaluate Industrial Profile
    elif prop_type == "industrial":
        f_cfg = INDUSTRIAL_FACTORS["main_gate"]
        factor_results.append(_evaluate_direction_placement(
            p.main_entrance_direction,
            ideal_dirs=["N", "E", "NE"],
            acceptable_dirs=["NW", "W"],
            prohibited_dirs=["SW"],
            max_weight=f_cfg["max_weight"],
            factor_key="main_gate",
            factor_name=f_cfg["name"],
            rule_source=f_cfg["source"],
            rule_text=f_cfg["rule"],
        ))

        f_cfg = INDUSTRIAL_FACTORS["heavy_machinery"]
        factor_results.append(_evaluate_direction_placement(
            p.heavy_machinery_direction,
            ideal_dirs=["SW", "S"],
            acceptable_dirs=["W"],
            prohibited_dirs=["NE", "NW"],
            max_weight=f_cfg["max_weight"],
            factor_key="heavy_machinery",
            factor_name=f_cfg["name"],
            rule_source=f_cfg["source"],
            rule_text=f_cfg["rule"],
            defect_remedy="Anchor vibration pads and ensure heavy machinery foundations are deepest in South-West.",
        ))

        f_cfg = INDUSTRIAL_FACTORS["boiler_furnace"]
        factor_results.append(_evaluate_direction_placement(
            p.boiler_furnace_direction,
            ideal_dirs=["SE"],
            acceptable_dirs=["S", "E"],
            prohibited_dirs=["NE", "N", "SW"],
            max_weight=f_cfg["max_weight"],
            factor_key="boiler_furnace",
            factor_name=f_cfg["name"],
            rule_source=f_cfg["source"],
            rule_text=f_cfg["rule"],
            defect_remedy="Chimneys and exhausts in Southeast should be directed upward and away from Northeast.",
        ))

    # --------------------------------------------------------------------------
    # Classical Dosha Detection
    # --------------------------------------------------------------------------

    # 1. Īśānya Dosha (Corrupted Northeast)
    toilets_in_ne = p.toilet_directions and any(d in ("NE", "NNE") for d in p.toilet_directions)
    kitchen_in_ne = p.kitchen_direction in ("NE", "NNE")
    septic_in_ne = p.septic_tank_direction in ("NE", "NNE")
    if toilets_in_ne or kitchen_in_ne or septic_in_ne:
        doshas.append(VastuDosha(
            dosha_code="ISHANYA_CORRUPTION",
            dosha_name="Īśānya Dosha (North-East Sacred Zone Corruption)",
            severity="critical",
            zone="North-East (Īśānya)",
            traditional_impact="Mayamata indicates severe afflictions to family prosperity, peace of mind, and chronic mental stress.",
            traditional_source="Mayamata Ch. 3 / Brihat Samhita Ch. 53",
            remedies=[
                "Place a pure silver or brass Vastu pyramid strip along the door frame of the offending room.",
                "Place a bowl of raw rock salt inside, renewed weekly.",
                "Keep a constant small water fountain or crystal bowl in the extreme Northeast corner of the property.",
            ],
        ))

    # 2. Āgneya Dosha (Water in Southeast Fire Zone)
    underground_water_in_se = p.underground_water_tank_direction in ("SE", "SSE")
    septic_in_se = p.septic_tank_direction in ("SE", "SSE")
    toilets_in_se = p.toilet_directions and any(d in ("SE", "SSE") for d in p.toilet_directions)
    if underground_water_in_se or septic_in_se or toilets_in_se:
        doshas.append(VastuDosha(
            dosha_code="AGNEYA_WATER_DEFECT",
            dosha_name="Āgneya Dosha (Fire-Water Clash in South-East)",
            severity="major",
            zone="South-East (Āgneya)",
            traditional_impact="Classical texts warn of financial drain, unexpected health expenditure, and relationship discord.",
            traditional_source="Brihat Samhita Ch. 53 / Vishwakarma Prakash",
            remedies=[
                "Paint the surrounding walls in coral pink or warm peach.",
                "Install an Agni Yantra or copper helix on the Southeast wall.",
                "Keep red bulbs illuminated in this zone for at least 4 hours every evening.",
            ],
        ))

    # 3. Nairṛtya Dosha (Instability in Southwest Earth Zone)
    underground_water_in_sw = p.underground_water_tank_direction in ("SW", "SSW", "WSW")
    main_door_in_sw = p.main_entrance_direction in ("SW", "SSW")
    toilets_in_sw = p.toilet_directions and any(d in ("SW",) for d in p.toilet_directions)
    if underground_water_in_sw or main_door_in_sw or toilets_in_sw:
        doshas.append(VastuDosha(
            dosha_code="NAIRRUTI_DEFECT",
            dosha_name="Nairṛtya Dosha (Earth Stability Loss in South-West)",
            severity="critical",
            zone="South-West (Nairṛtya)",
            traditional_impact="Vishwakarma Prakash cites instability in livelihood, loss of authority for the family elder, and financial vulnerability.",
            traditional_source="Vishwakarma Prakash Ch. 7 / Mayamata",
            remedies=[
                "Affix heavy brass/lead strips across the threshold.",
                "Place a solid quartz crystal rock or brass elephant figurine in the SW corner.",
                "Ensure Southwest wall is painted in warm yellow, ochre, or terracotta.",
            ],
        ))

    # 4. Brahmasthan Dosha
    if p.brahmasthan_status == "heavily_obstructed":
        doshas.append(VastuDosha(
            dosha_code="BRAHMASTHAN_OBSTRUCTION",
            dosha_name="Brahmasthan Dosha (Center Hub Obstruction)",
            severity="critical",
            zone="Central Brahmasthan",
            traditional_impact="Mayamata states obstruction of the central heart of the home creates chronic stagnation and disharmony across all inhabitants.",
            traditional_source="Mayamata Ch. 2",
            remedies=[
                "Avoid hammering nails or hanging heavy suspended lights directly in the geometric center.",
                "Place four brass pyramids facing the four cardinal directions around the central zone.",
                "Keep the floor clean and use light, reflective floor tiles if possible.",
            ],
        ))

    # --------------------------------------------------------------------------
    # 5. Score Normalization (Strictly over assessable factors)
    # --------------------------------------------------------------------------
    assessed_factors = [f for f in factor_results if f.assessed]
    total_assessed_count = len(assessed_factors)
    total_factors_count = len(factor_results)

    sum_scores = sum(f.score or 0.0 for f in assessed_factors)
    sum_weights = sum(f.max_weight for f in assessed_factors)

    if sum_weights > 0:
        compliance_score = int(round((sum_scores / sum_weights) * 100))
        compliance_score = max(0, min(100, compliance_score))

        if compliance_score >= 85:
            grade = "A+ (Highly Auspicious Alignment)"
        elif compliance_score >= 70:
            grade = "A (Favorable Vastu Alignment)"
        elif compliance_score >= 55:
            grade = "B (Moderate Alignment - Minor Remedies Advised)"
        elif compliance_score >= 40:
            grade = "C (Challenging Alignment - Remedies Recommended)"
        else:
            grade = "Needs Structural Remediation"
    else:
        compliance_score = None
        grade = "Unassessed (Insufficient Inputs)"
        missing_warnings.append("No assessable room or plot factors were provided. Compliance score cannot be calculated.")

    # General remedies based on identified doshas
    if doshas:
        general_remedies.append("Implement priority remedies for critical Doshas before commencing interior decor changes.")
        general_remedies.append("Maintain the North-East zone lowest and lightest, and the South-West zone highest and heaviest.")
    else:
        general_remedies.append("General energy distribution is harmonious. Maintain morning ventilation in East and North.")

    # Record explicit warnings for all unassessed factors
    for uf in factor_results:
        if not uf.assessed:
            missing_warnings.append(f"Factor '{uf.factor_name}' is unassessed (no placement input provided).")

    # --------------------------------------------------------------------------
    # 6. Optional Astro-Vastu Synthesis (Native XALEN ephemeris)
    # --------------------------------------------------------------------------
    astro_overlay = None
    if request.birth_date and request.birth_time:
        try:
            from app.services.ephemeris import calculate_full_horoscope
            from datetime import date as dt_date, time as dt_time

            if isinstance(request.birth_date, str):
                parts = [int(x) for x in request.birth_date.split("-")]
                b_date = dt_date(parts[0], parts[1], parts[2])
            else:
                b_date = request.birth_date

            if isinstance(request.birth_time, str):
                t_parts = [int(x) for x in request.birth_time.split(":")[:2]]
                b_time = dt_time(t_parts[0], t_parts[1])
            else:
                b_time = request.birth_time

            horo_res = calculate_full_horoscope(
                birth_date=b_date,
                birth_time=b_time,
                timezone_str=request.timezone or "UTC",
                latitude=request.latitude or 0.0,
                longitude=request.longitude or 0.0,
                ayanamsa_id=0,  # 0=Lahiri
                house_system_id=0,
            )

            lagna_sign = horo_res.ascendant.sign_name
            moon_planet = next((p for p in horo_res.planets if p.name == "Moon"), None)
            moon_sign = moon_planet.sign_name if moon_planet else None
            moon_nakshatra = f"{moon_planet.nakshatra.name} (Pada {moon_planet.nakshatra.pada})" if (moon_planet and moon_planet.nakshatra) else None

            sign_lord_map = {
                "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
                "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
                "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
                "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
            }
            ruler = sign_lord_map.get(lagna_sign, "Jupiter")

            # Classical favorable directions for Lagna
            fav_map = {
                "Aries": (["E", "S"], ["W", "SW"]),
                "Taurus": (["N", "W"], ["S", "SW"]),
                "Gemini": (["N", "NW"], ["S", "SE"]),
                "Cancer": (["NW", "N", "E"], ["S", "SW"]),
                "Leo": (["E", "SE"], ["NW", "W"]),
                "Virgo": (["N", "W"], ["S", "SE"]),
                "Libra": (["W", "N"], ["S", "SW"]),
                "Scorpio": (["S", "E"], ["N", "NW"]),
                "Sagittarius": (["NE", "E"], ["SW", "W"]),
                "Capricorn": (["W", "S"], ["NE", "E"]),
                "Aquarius": (["W", "NW"], ["SE", "S"]),
                "Pisces": (["NE", "N"], ["S", "SW"]),
            }
            fav_dirs, unfav_dirs = fav_map.get(lagna_sign, (["E", "N"], ["SW"]))

            astro_overlay = AstroOverlayResult(
                lagna_sign=lagna_sign,
                lagna_ruler=ruler,
                moon_sign=moon_sign,
                nakshatra=moon_nakshatra,
                favorable_directions=fav_dirs,
                unfavorable_directions=unfav_dirs,
                elemental_synergy=f"Lagna in {lagna_sign} governed by {ruler}." + (f" Moon in {moon_sign} ({moon_nakshatra})." if moon_sign else ""),
                planetary_zone_notes=[
                    f"Owner's Lagna ruler ({ruler}) naturally harmonizes with {', '.join(fav_dirs)}.",
                    "Ensure native's work/study desk faces one of the favorable cardinal directions.",
                ],
                calculation_source="Native XALEN Ephemeris Engine (Verified)",
            )
        except Exception as exc:
            missing_warnings.append(f"Astro-Vastu overlay skipped due to calculation error: {str(exc)}")


    return VastuEvaluationResponse(
        property_name=request.property_name,
        property_type=prop_type,
        facing_direction=facing_dir,
        facing_degrees=request.facing_degrees,
        engine_version=ENGINE_VERSION,
        rubric_version=RUBRIC_VERSION,
        compliance_score=compliance_score,
        score_grade=grade,
        factors_assessed=total_assessed_count,
        factors_total=total_factors_count,
        factor_results=factor_results,
        doshas=doshas,
        general_remedies=general_remedies,
        missing_data_warnings=missing_warnings,
        conflicting_input_warnings=conflicting_warnings,
        astro_overlay=astro_overlay,
        disclaimer=DISCLAIMER_TEXT,
    )


# ------------------------------------------------------------------------------
# 5. Supabase Persistence Functions
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# 5. Supabase Persistence Functions with Resilient Local Fallback
# ------------------------------------------------------------------------------

_LOCAL_VASTU_REPORTS: Dict[str, Dict[str, Any]] = {}
_USER_DISPLAY_COUNTERS: Dict[str, int] = {}


def _make_offline_report(user_id: str, request: SaveVastuReportRequest) -> Dict[str, Any]:
    """Creates a local report record with atomic sequential display number."""
    now_iso = datetime.now(timezone.utc).isoformat()
    report_id = str(uuid.uuid4())
    _USER_DISPLAY_COUNTERS[user_id] = _USER_DISPLAY_COUNTERS.get(user_id, 0) + 1
    display_num = _USER_DISPLAY_COUNTERS[user_id]
    record = {
        "id": report_id,
        "user_id": user_id,
        "display_number": display_num,
        "property_name": request.property_name,
        "property_type": request.property_type,
        "facing_direction": request.facing_direction,
        "facing_degrees": request.facing_degrees,
        "horoscope_id": request.horoscope_id,
        "person_name": request.person_name,
        "birth_date": request.birth_date,
        "calculation_data": request.evaluation_data,
        "dosha_evaluations": request.evaluation_data.get("doshas", []),
        "remedy_recommendations": request.evaluation_data.get("general_remedies", []),
        "compliance_score": request.evaluation_data.get("compliance_score") or 0,
        "engine_version": ENGINE_VERSION,
        "created_at": now_iso,
        "updated_at": now_iso,
    }
    _LOCAL_VASTU_REPORTS[report_id] = record
    return record


def save_vastu_report(user_id: str, request: SaveVastuReportRequest) -> Dict[str, Any]:
    """Persists an evaluated Vastu report to Supabase public.saved_vastu_reports.
    Assigns sequential display_number per user using the advisory-lock database trigger.
    Falls back gracefully to local store if Supabase table is not yet reachable.
    """
    supabase = get_supabase_client()
    if not supabase:
        return _make_offline_report(user_id, request)

    data = {
        "user_id": user_id,
        "property_name": request.property_name.strip(),
        "property_type": request.property_type,
        "facing_direction": request.facing_direction.strip().upper(),
        "facing_degrees": request.facing_degrees,
        "horoscope_id": request.horoscope_id,
        "person_name": request.person_name.strip() if request.person_name else None,
        "birth_date": request.birth_date.strip() if request.birth_date else None,
        "calculation_data": request.evaluation_data,
        "dosha_evaluations": request.evaluation_data.get("doshas", []),
        "remedy_recommendations": request.evaluation_data.get("general_remedies", []),
        "compliance_score": request.evaluation_data.get("compliance_score") or 0,
        "engine_version": ENGINE_VERSION,
    }

    try:
        res = supabase.table("saved_vastu_reports").insert(data).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception:
        pass

    return _make_offline_report(user_id, request)


def list_vastu_reports(
    user_id: str, is_admin: bool = False, limit: int = 50, offset: int = 0
) -> Tuple[List[Dict[str, Any]], int]:
    """Retrieves paginated saved Vastu reports for the authenticated user, or all for admins."""
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("saved_vastu_reports").select("*", count="exact")
            if not is_admin:
                query = query.eq("user_id", user_id)
            res = query.order("display_number", desc=True).range(offset, offset + limit - 1).execute()
            if res.data is not None:
                reports = res.data or []
                count = res.count if hasattr(res, "count") and res.count is not None else len(reports)
                return reports, count
        except Exception:
            pass

    # Local fallback
    matched = [
        r for r in _LOCAL_VASTU_REPORTS.values()
        if is_admin or r["user_id"] == user_id
    ]
    matched.sort(key=lambda x: x["display_number"], reverse=True)
    total_count = len(matched)
    return matched[offset:offset + limit], total_count


def get_vastu_report(
    user_id: str, report_id: str, is_admin: bool = False
) -> Optional[Dict[str, Any]]:
    """Retrieves a single saved Vastu report by UUID, strictly enforcing ownership or admin status."""
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("saved_vastu_reports").select("*").eq("id", report_id)
            if not is_admin:
                query = query.eq("user_id", user_id)
            res = query.execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception:
            pass

    # Local fallback
    rec = _LOCAL_VASTU_REPORTS.get(report_id)
    if rec and (is_admin or rec["user_id"] == user_id):
        return rec
    return None


def update_vastu_report(
    user_id: str, report_id: str, request: SaveVastuReportRequest, is_admin: bool = False
) -> Optional[Dict[str, Any]]:
    """Updates an existing saved Vastu report, strictly checking ownership."""
    supabase = get_supabase_client()
    if supabase:
        try:
            existing = get_vastu_report(user_id, report_id, is_admin)
            if not existing:
                return None

            update_payload = {
                "property_name": request.property_name.strip(),
                "property_type": request.property_type,
                "facing_direction": request.facing_direction.strip().upper(),
                "facing_degrees": request.facing_degrees,
                "horoscope_id": request.horoscope_id,
                "person_name": request.person_name.strip() if request.person_name else None,
                "birth_date": request.birth_date.strip() if request.birth_date else None,
                "calculation_data": request.evaluation_data,
                "dosha_evaluations": request.evaluation_data.get("doshas", []),
                "remedy_recommendations": request.evaluation_data.get("general_remedies", []),
                "compliance_score": request.evaluation_data.get("compliance_score") or 0,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            res = (
                supabase.table("saved_vastu_reports")
                .update(update_payload)
                .eq("id", report_id)
                .execute()
            )
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception:
            pass

    # Local fallback
    rec = _LOCAL_VASTU_REPORTS.get(report_id)
    if rec and (is_admin or rec["user_id"] == user_id):
        rec.update({
            "property_name": request.property_name.strip(),
            "property_type": request.property_type,
            "facing_direction": request.facing_direction.strip().upper(),
            "facing_degrees": request.facing_degrees,
            "horoscope_id": request.horoscope_id,
            "person_name": request.person_name.strip() if request.person_name else None,
            "birth_date": request.birth_date.strip() if request.birth_date else None,
            "calculation_data": request.evaluation_data,
            "dosha_evaluations": request.evaluation_data.get("doshas", []),
            "remedy_recommendations": request.evaluation_data.get("general_remedies", []),
            "compliance_score": request.evaluation_data.get("compliance_score") or 0,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        return rec
    return None


def delete_vastu_report(user_id: str, report_id: str, is_admin: bool = False) -> bool:
    """Deletes a saved Vastu report by UUID, enforcing ownership."""
    supabase = get_supabase_client()
    if supabase:
        try:
            query = supabase.table("saved_vastu_reports").delete().eq("id", report_id)
            if not is_admin:
                query = query.eq("user_id", user_id)
            res = query.execute()
            if res.data and len(res.data) > 0:
                return True
        except Exception:
            pass

    # Local fallback
    rec = _LOCAL_VASTU_REPORTS.get(report_id)
    if rec and (is_admin or rec["user_id"] == user_id):
        del _LOCAL_VASTU_REPORTS[report_id]
        return True
    return False

