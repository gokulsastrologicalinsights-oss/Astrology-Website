"""Max Heindel & Augusta Foss Heindel "Astro-Diagnosis: A Guide to Healing" Registry.

Contains authoritative knowledge from:
1. Max Heindel & Augusta Foss Heindel (The Rosicrucian Fellowship, Oceanside, California)
   - "Astro-Diagnosis: A Guide to Healing" (Chapters I - X)
   - "The Message of the Stars" (Chapters I - IX)
2. Marcus Manilius (1st century AD, "Astronomica")
   - Classical Head-to-Toe Zodiacal Anatomy
"""

from typing import Dict, Any, List
from app.services.medical_astrology_engine.registry import ClassicalMedicalRuleDefinition

# ---------------------------------------------------------------------------
# 1. Treatise Metadata, Philosophy, & The 19 Golden Injunctions for the Healer
# ---------------------------------------------------------------------------

MAX_HEINDEL_METADATA: Dict[str, Any] = {
    "book_title": "Astro-Diagnosis: A Guide to Healing & The Message of the Stars",
    "book_title_ta": "ஜோதிட நோய்நிர்ணயம்: குணமளிக்கும் வழிகாட்டி மற்றும் விண்மீன்களின் செய்தி",
    "authors": "Max Heindel & Augusta Foss Heindel (The Rosicrucian Fellowship, Oceanside, CA)",
    "historical_foundation": "Marcus Manilius (1st Century AD Astronomica) & Rosicrucian Esoteric Astro-Diagnosis",
    "core_philosophy_en": (
        "Disease is fundamentally a lack of harmony between the spirit and the personality — a conflict "
        "between the lower and the higher man. In ninety-five cases out of every hundred, disease originates in wrong "
        "methods of living and ignorant violations of the laws of nature. The true healer never treats merely the physical "
        "symptom, but seeks the first cause in the horoscope. By removing the primary cause and guiding the patient "
        "into harmony with nature's cosmic laws, the cure follows as an inevitable consequence. The stars impel but do not compel; "
        "by will-power, self-control, and spiritual enlightenment, man may rule his stars."
    ),
    "core_philosophy_ta": (
        "நோய் என்பது ஆன்மாவிற்கும் உடலின் ஆளுமைக்கும் இடையே ஏற்படும் இசைவின்மையே ஆகும் (உயர் ஆன்மாவிற்கும் கீழ்நிலை "
        "மனதிற்குமான முரண்பாடு). நூற்றுக்கு தொண்ணூற்றைந்து சதவீத நோய்கள் தவறான வாழ்க்கை முறையினாலும் இயற்கையின் விதிகளை "
        "மீறுவதாலுமே ஏற்படுகின்றன. உண்மையான ஜோதிட மருத்துவர் வெறும் புற அறிகுறிகளை மட்டும் கவனிக்காமல், ஜாதகத்தின் வழியே "
        "நோய்க்கான மூலக் காரணத்தைக் கண்டறிகிறார். மூலக் காரணத்தை அகற்றி, இயற்கையின் நெறிமுறைகளுக்கு ஏற்ப வாழ வழிகாட்டுவதன் மூலம் "
        "நலமுறுதல் இயல்பாக நிகழ்கிறது. விண்மீன்கள் உந்துகின்றன, கட்டாயப்படுத்துவதில்லை; மன உறுதியாலும் ஆன்ம விழிப்பினாலும் மனிதன் தன் விதியை வெல்ல முடியும்."
    ),
    "healer_injunctions": [
        {
            "id": "1",
            "rule_en": "NEVER, NEVER predict the time of death to your patient. While there is life, there is HOPE. Predicting death makes you an executioner.",
            "rule_ta": "நோயாளியிடம் மரண காலத்தை ஒருபோதும் கணிக்கவோ கூறவோ கூடாது. உயிர் இருக்கும் வரை நம்பிக்கை உண்டு. மரணத்தை அறிவிப்பது நோயாளியின் நம்பிக்கையைக் கொல்வதாகும்.",
        },
        {
            "id": "2",
            "rule_en": "The LAW does not permit a layman to diagnose disease for others; only licensed physicians may do this. Keep astrological indications for holistic guidance.",
            "rule_ta": "சட்டப்படி மருத்துவர் மட்டுமே நோயை உறுதிப்படுத்த முடியும். ஜோதிடர் ஆன்மவியல் காரணங்களையும் முழுமையான நல்வாழ்வு ஆலோசனைகளையும் மட்டுமே பயன்படுத்த வேண்டும்.",
        },
        {
            "id": "3",
            "rule_en": "The wise healer will NEVER discuss disease with his patient nor pronounce scary medical names. Keep esoteric knowledge for your own guidance in healing.",
            "rule_ta": "புத்திசாலித்தனமான குணப்படுத்துபவர் நோயாளியிடம் நோயைப் பற்றியோ அதன் தீவிர பெயர்களையோ விவாதிக்க மாட்டார்; ஜோதிட அறிவை நோயாளிக்கு தைரியம் அளிக்க மட்டுமே பயன்படுத்த வேண்டும்.",
        },
        {
            "id": "4",
            "rule_en": "At all times keep the patient's mind away from thoughts of illness. Laugh and joke with him; cheerfulness is half the cure.",
            "rule_ta": "எப்போதும் நோயாளியின் மனதை நோயின் நினைவிலிருந்து விலக்கி வையுங்கள். மகிழ்ச்சியாகவும் புன்னகையுடனும் உரையாடுங்கள்; மனமகிழ்ச்சியே நோயைக் குணப்படுத்தும் பாதி மருந்தாகும்.",
        },
        {
            "id": "5",
            "rule_en": "Refrain from asking 'How do you feel?'. This draws consciousness back to the physical affliction. Greet with: 'What a beautiful day! I am glad to see you.'",
            "rule_ta": "'உடல்நிலை எப்படி இருக்கிறது?' என்று கேட்க வேண்டாம். அது உடலின் வலியை மீண்டும் நினைவூட்டும். 'இன்று இனிய நாள்! உங்களைக் காண்பதில் மகிழ்ச்சி' என உற்சாகமாக வாழ்த்துங்கள்.",
        },
        {
            "id": "6",
            "rule_en": "Request the patient to discontinue morbidly studying their own horoscope while under care, as adverse suggestions in the mind severely hinder recovery.",
            "rule_ta": "சிகிச்சையில் இருக்கும்போது நோயாளி தனது சொந்த ஜாதகத்தை பயத்துடன் ஆராய்வதைத் தவிர்க்கச் சொல்லுங்கள்; எதிர்மறை அச்சங்கள் குணமாவதைத் தடுக்கும்.",
        },
        {
            "id": "7",
            "rule_en": "Magnetic polarity principle: An ill patient expresses the negative receptive pole. The healer must actively radiate the opposite positive pole of vitality and cheerfulness.",
            "rule_ta": "காந்த துருவ விதி: நோயுற்றவர் எதிர்மறை (நெகட்டிவ்) ஏற்பு நிலையில் உள்ளார். குணப்படுத்துபவர் நேர்மறை (பாசிட்டிவ்) பிராண ஆற்றலையும் நம்பிக்கையையும் வீச வேண்டும்.",
        },
        {
            "id": "8",
            "rule_en": "When a man is ill, his vital ethers turn inward, leaving him hypersensitive to negative thoughts. The healer must live a life of pristine moral purity to transmit wholesome vibrations.",
            "rule_ta": "நோயுற்றபோது பிராண உடல் சுருங்கி உள்நோக்கும். அப்போது தீய அதிர்வுகள் எளிதில் தாக்கும். எனவே குணப்படுத்துபவர் மிகத் தூய்மையான நெறிசார்ந்த வாழ்க்கை வாழ வேண்டும்.",
        },
        {
            "id": "9",
            "rule_en": "If the healer's Saturn falls upon the Ascendant or 6th house of the patient, the healer will have little success in helping that particular individual.",
            "rule_ta": "குணப்படுத்துபவரின் சனி கிரகம் நோயாளியின் லக்னத்திலோ அல்லது 6-ம் வீட்டிலோ அமைந்தால், அவரால் அந்த நோயாளிக்கு பயனுள்ள உதவி செய்வது கடினம்.",
        },
        {
            "id": "10",
            "rule_en": "Healers with Sun in Scorpio or Scorpio rising possess natural healing magnetism and excel in restorative arts and surgery.",
            "rule_ta": "விருச்சிகத்தில் சூரியன் அல்லது விருச்சிக லக்னம் கொண்டவர்கள் இயல்பாகவே சிறந்த பிராண குணப்படுத்தும் ஆற்றலும் அறுவை சிகிச்சைத் திறனும் கொண்டவர்கள்.",
        },
        {
            "id": "11",
            "rule_en": "The Sun in fiery signs (Aries, Leo, Sagittarius) grants intense healing vital force and restorative power over the diseases of those signs.",
            "rule_ta": "சூரியன் நெருப்பு ராசிகளில் (மேஷம், சிம்மம், தனுசு) அமர்ந்தால் மிகுந்த பிராண குணப்படுத்தும் சக்தியையும் நோய்களை வெல்லும் ஆற்றலையும் தருகிறது.",
        },
        {
            "id": "12",
            "rule_en": "People born with Common signs on angles or Sun in common signs make the best nurses; their gentle aura brings a soothing, quieting influence to the sickroom.",
            "rule_ta": "உபய ராசிகள் (மிதுனம், கன்னி, தனுசு, மீனம்) கேந்திரங்களில் அமைந்தவர்கள் சிறந்த செவிலியர்களாக திகழ்கிறார்கள்; நோயாளியின் அறையை சாந்தப்படுத்தும் ஆற்றல் இவர்களிடம் உண்டு.",
        },
        {
            "id": "13",
            "rule_en": "When Saturn is the afflicter, the skin is dry and vital circulation sluggish. Rub the skin briskly with rough bath gloves to stimulate peripheral circulation.",
            "rule_ta": "சனி பாதகமாக இருக்கும்போது தோல் வறண்டு இரத்த ஓட்டம் மந்தமாகும். சொரசொரப்பான குளியல் துணியால் உடலைத் தேய்த்து புற இரத்த ஓட்டத்தைத் தூண்ட வேண்டும்.",
        },
        {
            "id": "14",
            "rule_en": "People with Virgo on the Ascendant or Sun in Virgo are natural dietitians and nurses, provided they guard against absorbing the patient's symptoms.",
            "rule_ta": "கன்னி லக்னம் அல்லது கன்னியில் சூரியன் உள்ளவர்கள் சிறந்த உணவு முறை நிபுணர்களாகவும் செவிலியர்களாகவும் இருப்பார்கள் (நோயாளியின் நோயை மனதளவில் உள்வாங்காமல் இருக்க வேண்டும்).",
        },
        {
            "id": "15",
            "rule_en": "To calm a patient with an afflicted or over-excited Mars, it is ideal to choose a Saturn planetary hour for therapies.",
            "rule_ta": "செவ்வாயின் கொதிப்பால் அவதிப்படும் நோயாளிக்கு அமைதி தர, சனி ஓரையில் சிகிச்சைகளைத் தொடங்குவது நற்பலன் தரும்.",
        },
        {
            "id": "16",
            "rule_en": "People with Saturn in the sixth house rarely succeed as professional healers, as their own constitutional vitality is impeded.",
            "rule_ta": "6-ம் வீட்டில் சனி உள்ளவர்கள் பிறரை குணப்படுத்தும் துறையில் வெற்றி பெறுவது அரிது, ஏனெனில் அவர்களின் சொந்த பிராண சக்தி தடைகளுக்கு உள்ளாகிறது.",
        },
        {
            "id": "17",
            "rule_en": "When the patient suffers from nervous disorders but Mars is unafflicted, apply manipulations or ministrations during a Sun or Mars hour.",
            "rule_ta": "நரம்பு தளர்ச்சி அல்லது மந்தநிலை உள்ளபோது செவ்வாய் கெடாமல் இருந்தால், சூரியன் அல்லது செவ்வாய் ஓரையில் சிகிச்சைகளை மேற்கொள்ள வேண்டும்.",
        },
        {
            "id": "18",
            "rule_en": "When the Moon is Waxing (New to Full), stimulants produce the maximum effect while sedatives are weakest; adjust therapeutic dosages accordingly.",
            "rule_ta": "சந்திரன் வளர்பிறையாக இருக்கும்போது (அமாவாசை முதல் பௌர்ணமி வரை) ஊக்க மருந்துகள் அதிக வீரியத்துடனும், அமைதிப்படுத்தும் மருந்துகள் குறைந்த வீரியத்துடனும் செயல்படும்.",
        },
        {
            "id": "19",
            "rule_en": "When the Moon is conjunct Saturn, stimulants have very little effect. When Moon is conjoined to Mars (especially in Aries), administer stimulants with extreme care.",
            "rule_ta": "சந்திரன் சனியுடன் இணையும் போது ஊக்க மருந்துகள் பலனளிப்பது குறைவு; சந்திரன் செவ்வாயுடன் இணைந்தால் (குறிப்பாக மேஷத்தில்) உஷ்ண ஊக்கிகளை மிக எச்சரிக்கையுடன் கையாள வேண்டும்.",
        },
    ],
}

# ---------------------------------------------------------------------------
# 2. Complete 12 Zodiac Signs Anatomy & Pathology (Marcus Manilius + Heindel)
# ---------------------------------------------------------------------------

HEINDEL_SIGNS_ANATOMY: List[Dict[str, Any]] = [
    {
        "sign_index": 1,
        "sign_name_en": "Aries",
        "sign_name_ta": "மேஷம்",
        "manilius_rulership": "The Head and Cranium (Caput)",
        "heindel_anatomical_systems": [
            "Brain", "Cerebral hemispheres", "Cranium", "Eyes", "Face", "Upper jaw", "Internal carotid arteries"
        ],
        "pathological_qualities": "Hot, dry, inflammatory; excess life force, quick temper, rushing blood.",
        "physiological_afflictions": [
            "Brain fever", "Neuralgia", "Insomnia", "Cerebral congestion", "Dizziness", "Headaches",
            "Baldness", "Eye affections", "Toothache", "Gumboils"
        ],
        "temperament_and_healing_reaction": (
            "Positive, aggressive, impulsive. Can withstand fevers 3-4 degrees higher than other signs. "
            "Responds rapidly to healing effort because the will is strong. Aries dislikes being ordered; "
            "the healer must ask diplomatically so the patient feels they are directing their own cure."
        ),
    },
    {
        "sign_index": 2,
        "sign_name_en": "Taurus",
        "sign_name_ta": "ரிஷபம்",
        "manilius_rulership": "The Neck and Throat (Cervix)",
        "heindel_anatomical_systems": [
            "Neck", "Throat", "Palate", "Larynx", "Tonsils", "Thyroid gland", "Lower jaw",
            "Occipital region", "Cerebellum", "Atlas", "Axis", "External carotid arteries",
            "Jugular veins", "Pharynx", "Cervical vertebrae"
        ],
        "pathological_qualities": "Cold, dry, earthy, stubborn; fear of sickness, luxurious appetite, fleshiness about neck.",
        "physiological_afflictions": [
            "Goiter", "Diphtheria", "Laryngitis", "Tonsillitis", "Croup", "Polypi", "Quinsy",
            "Glandular throat swelling", "Apoplexy"
        ],
        "temperament_and_healing_reaction": (
            "Negative, tenacious, stubborn. Holds on to disease tenaciously due to morbid fear of sickness. "
            "Never tell a Taurean they are seriously ill, as their anxiety will precipitate a crisis. "
            "Needs gentle reassurance, outdoor activity, and moderation in rich food."
        ),
    },
    {
        "sign_index": 3,
        "sign_name_en": "Gemini",
        "sign_name_ta": "மிதுனம்",
        "manilius_rulership": "The Shoulders, Arms, and Hands (Brachia)",
        "heindel_anatomical_systems": [
            "Shoulders", "Arms", "Hands", "Upper ribs", "Lungs", "Thymus gland", "Trachea",
            "Bronchi", "Capillaries", "Breath", "Oxygenation of blood"
        ],
        "pathological_qualities": "Airy, nervous, dual, restless; careless habits, shallow breathing.",
        "physiological_afflictions": [
            "Bronchitis", "Asthma", "Pneumonia", "Consumption (Tuberculosis)", "Pleurisy",
            "Corrupted blood", "Nervous disorders", "Anemia"
        ],
        "temperament_and_healing_reaction": (
            "Positive, flexible, common sign. Frequently careless of health habits. Responds quickly to treatment "
            "if given slight assistance. Greatly benefited by systematic deep breathing exercises and calisthenics."
        ),
    },
    {
        "sign_index": 4,
        "sign_name_en": "Cancer",
        "sign_name_ta": "கடகம்",
        "manilius_rulership": "The Chest, Breasts, and Stomach (Pectus)",
        "heindel_anatomical_systems": [
            "Stomach", "Esophagus", "Diaphragm", "Mammae (breasts)", "Lacteals", "Upper lobes of liver",
            "Thoracic duct", "Pancreas", "Serum of blood", "Peristalsis of stomach", "Chymification"
        ],
        "pathological_qualities": "Watery, negative, low vitality; emotional sensitivity, over-eating, sweet cravings.",
        "physiological_afflictions": [
            "Indigestion", "Dipsomania", "Gastric catarrh", "Hiccough", "Flatulency", "Dropsy", "Sclerosis"
        ],
        "temperament_and_healing_reaction": (
            "Negative, timid, suspicious yet loyal once faith is established. Lowest natural vitality of the zodiac; "
            "requires praise and encouragement. Saturn in Cancer creates intense craving for sweets and pastries, "
            "robbing stomach of fluids and disturbing kidneys."
        ),
    },
    {
        "sign_index": 5,
        "sign_name_en": "Leo",
        "sign_name_ta": "சிம்மம்",
        "manilius_rulership": "The Heart and Upper Back (Humeri & Dorsum)",
        "heindel_anatomical_systems": [
            "Heart", "Dorsal region of spine", "Spinal cord", "Aorta", "Superior and inferior vena cava",
            "Etheric solar fluid via Spleen"
        ],
        "pathological_qualities": "Fiery, fixed, ardent, vital; excessive expenditure of surplus energy.",
        "physiological_afflictions": [
            "Heart disease", "Angina pectoris", "Locomotor ataxia", "Hyperemia", "Spinal disease",
            "Spinal meningitis", "High fevers", "Disturbed spleen"
        ],
        "temperament_and_healing_reaction": (
            "Positive, noble, great vitality. Fights illness bravely without burdening others; when succumbing, "
            "is very sick but recovers quickly. Must avoid sudden violent exertion to protect cardiac tissues."
        ),
    },
    {
        "sign_index": 6,
        "sign_name_en": "Virgo",
        "sign_name_ta": "கன்னி",
        "manilius_rulership": "The Abdomen and Digestive Organs (Venter)",
        "heindel_anatomical_systems": [
            "Abdominal region", "Large and small intestines", "Lower lobes of liver", "Spleen",
            "Duodenum", "Chylification", "Peristalsis of bowels", "Sympathetic nervous system"
        ],
        "pathological_qualities": "Earthy, negative, cold, wiry; natural 6th sign of sickness, food faddism, hypochondria.",
        "physiological_afflictions": [
            "Peritonitis", "Malnutrition", "Dysentery", "Colic", "Constipation", "Diarrhea",
            "Cholera", "Typhoid", "Appendicitis", "Tapeworm", "Catarrh of bowels"
        ],
        "temperament_and_healing_reaction": (
            "Negative, analytical. Virgos absorb disease vibrations like sponges. Once in the clutches of illness, "
            "they actually 'enjoy' discussing symptoms and become chronic invalids unless treated with firm conviction. "
            "Make wonderful nurses if they remain emotionally detached."
        ),
    },
    {
        "sign_index": 7,
        "sign_name_en": "Libra",
        "sign_name_ta": "துலாம்",
        "manilius_rulership": "The Kidneys, Lumbar Region, and Hips (Lumbi)",
        "heindel_anatomical_systems": [
            "Kidneys", "Adrenals", "Lumbar region of spine", "Skin", "Ureters", "Vasomotor system"
        ],
        "pathological_qualities": "Airy, cardinal, fluctuating moods; Sun weak (fall of Sun / exaltation of Saturn).",
        "physiological_afflictions": [
            "Bright's disease", "Lumbago", "Suppression of urine (Saturn)", "Excessive urine (Jupiter)",
            "Nephritis", "Diabetes", "Renal calculi (kidney stones)", "Uremia", "Eczema"
        ],
        "temperament_and_healing_reaction": (
            "Cardinal, changeable. Swings between optimism and despair like scales. Discouragement directly poisons "
            "the kidneys. Must cultivate mental equilibrium, serene surroundings, and drink pure fluids."
        ),
    },
    {
        "sign_index": 8,
        "sign_name_en": "Scorpio",
        "sign_name_ta": "விருச்சிகம்",
        "manilius_rulership": "The Generative Organs and Genitals (Tuber)",
        "heindel_anatomical_systems": [
            "Bladder", "Urethra", "Genitals", "Prostate gland", "Descending colon", "Rectum",
            "Sigmoid flexure", "Pubic bone", "Nasal bones", "Red coloring matter in blood"
        ],
        "pathological_qualities": "Watery, fixed, martial; volcanic desires, secretiveness, unexpressed resentment.",
        "physiological_afflictions": [
            "Syphilis", "Hernia / rupture", "Gravel", "Fistula", "Piles (hemorrhoids)",
            "Diseases of uterus", "Urethral stricture", "Prostatic stricture", "Nasal catarrh"
        ],
        "temperament_and_healing_reaction": (
            "Fixed, determined. Scorpio natives possess immense regenerative power and make superior surgeons and healers. "
            "Health danger stems from unrestrained passion sapping generative force. Moral cleanliness and emotional serenity are paramount."
        ),
    },
    {
        "sign_index": 9,
        "sign_name_en": "Sagittarius",
        "sign_name_ta": "தனுசு",
        "manilius_rulership": "The Hips and Thighs (Femina)",
        "heindel_anatomical_systems": [
            "Hips", "Thighs", "Femur", "Ileum", "Coccygeal vertebrae", "Sacral region of spine",
            "Sciatic nerves", "Ischium", "Iliac arteries"
        ],
        "pathological_qualities": "Fiery, mutable, sporting, restless; excessive physical momentum, sports accidents.",
        "physiological_afflictions": [
            "Locomotor ataxia", "Sciatica", "Lumbago", "Rheumatism", "Hip disease", "Fractures and broken bones of femur"
        ],
        "temperament_and_healing_reaction": (
            "Gentle, frank, trusting; most easily cured of all patients, but highly suggestible to well-meaning friends. "
            "Protect the Sagittarian from negative visitors who suggest sickness or question the treatment."
        ),
    },
    {
        "sign_index": 10,
        "sign_name_en": "Capricorn",
        "sign_name_ta": "மகரம்",
        "manilius_rulership": "The Knees and Skeletal Articulations (Genua)",
        "heindel_anatomical_systems": [
            "Knees", "Skin", "Joints", "Skeletal system", "Hair", "Patella"
        ],
        "pathological_qualities": "Earthy, cardinal, cold, Saturnine; crystallization, dryness, chronic melancholy.",
        "physiological_afflictions": [
            "Eczema", "Erysipelas", "Leprosy", "Dislocation of bones", "Weak knees", "Dry sallow skin",
            "Stiff articulations", "Hypochondriasis"
        ],
        "temperament_and_healing_reaction": (
            "Wiry, persistent, stolid. Does not yield to disease readily, but once succumbing, clings to sickness stubbornly. "
            "May resist help if aware someone is trying to 'manage' them. Requires cheerfulness, sunlight, warmth, and humorous entertainment."
        ),
    },
    {
        "sign_index": 11,
        "sign_name_en": "Aquarius",
        "sign_name_ta": "கும்பம்",
        "manilius_rulership": "The Calves, Shins, and Ankles (Tibiae)",
        "heindel_anatomical_systems": [
            "Lower limbs", "Calves", "Shins", "Ankles", "Circulatory system", "Venous blood flow"
        ],
        "pathological_qualities": "Airy, fixed, nervous, alternating between Saturnine gloom and Uranian hysteria.",
        "physiological_afflictions": [
            "Varicose veins", "Swollen ankles", "Leg ache", "Nervous exhaustion",
            "Hypersensitive skin (crawling sensation like insects)"
        ],
        "temperament_and_healing_reaction": (
            "Ambitious, wiry, prone to overwork until bodily reserves collapse. Highly cooperative with healers. "
            "Valvular heart strain frequently manifests by reflex sympathy as swollen ankles."
        ),
    },
    {
        "sign_index": 12,
        "sign_name_en": "Pisces",
        "sign_name_ta": "மீனம்",
        "manilius_rulership": "The Feet and Toes (Pedis)",
        "heindel_anatomical_systems": [
            "Feet", "Toes", "Fibrin of blood", "Lymphatic system", "Adipose tissue"
        ],
        "pathological_qualities": "Watery, negative, lymphatic; love of ease and rich drinks, low recuperative power.",
        "physiological_afflictions": [
            "Bunions", "Gout", "Deformed feet and toes", "Tumors", "Dropsy", "Swelling of feet",
            "Alcohol or narcotic addictions when Moon/Neptune afflicted"
        ],
        "temperament_and_healing_reaction": (
            "Extremely sensitive to suggestions and emotional environment. Keep away overly sympathetic visitors "
            "who encourage discussion of sickness ('No sympathetic visitors allowed' rule). Requires a bright, cheerful room."
        ),
    },
]

# ---------------------------------------------------------------------------
# 3. Planetary Physiology & Pathological Qualities (Heindel Chapter II & VI)
# ---------------------------------------------------------------------------

HEINDEL_PLANETS_PHYSIOLOGY: List[Dict[str, Any]] = [
    {
        "planet": "Sun",
        "planet_ta": "சூரியன்",
        "salient_keyword": "Life",
        "anatomical_rulership": "Vital fluid specialized through spleen, distribution of heat, pons varolii, heart, oxygen",
        "pathological_quality": "Hot, dry, vital, constructive, expansive, tonic",
        "positive_expression": "Radiant health, indestructible vitality, moral courage, prompt recuperation",
        "afflicted_expression": "Feverish delirium, cerebral hyperemia, cardiac strain, loss of vitality, baldness",
    },
    {
        "planet": "Venus",
        "planet_ta": "சுக்கிரன்",
        "salient_keyword": "Coalition",
        "anatomical_rulership": "Throat, kidneys, thymus gland, venous circulation, sense of touch, ovaries",
        "pathological_quality": "Warm, lymphatic, relaxing, sedentary",
        "positive_expression": "Harmony of bodily fluids, healthy venous circulation, graceful poise, artistic peace",
        "afflicted_expression": "Extravagance, sluggishness, throat relaxed tissues, kidney congestion, sensual excesses",
    },
    {
        "planet": "Mercury",
        "planet_ta": "புதன்",
        "salient_keyword": "Reason",
        "anatomical_rulership": "Nerves, bronchial tubes, pulmonary circulation, thyroid, right cerebral hemisphere, vocal cords, sensory perception",
        "pathological_quality": "Cold, dry, nervous",
        "positive_expression": "Keen intellectual alertness, prompt neurological reflexes, clear articulation",
        "afflicted_expression": "Nervous breakdown, speech impediment, auditory impairment, mental gloom (with Saturn), restlessness",
    },
    {
        "planet": "Moon",
        "planet_ta": "சந்திரன்",
        "salient_keyword": "Fecundation",
        "anatomical_rulership": "Esophagus, stomach, uterus, ovaries, lymphatics, sympathetic nervous system, synovial fluid, alimentary canal",
        "pathological_quality": "Moist, cold, nutritive, receptive, collective, fluidic",
        "positive_expression": "Healthy digestion, wholesome cellular gestation, rhythmic monthly hormonal cycles",
        "afflicted_expression": "Fluidic retention, dropsy, acute recurring illnesses (7-day cycles), digestive disturbance, lunatic hysteria",
    },
    {
        "planet": "Saturn",
        "planet_ta": "சனி",
        "salient_keyword": "Obstruction",
        "anatomical_rulership": "Gall bladder, vagus (pneumogastric) nerve, teeth, skin, joints, ligaments, sigmoid flexure",
        "pathological_quality": "Cold, dry, chronic, contracting, crystallizing, binding, restricting, centripetal, obstructive",
        "positive_expression": "Endurance, structural bone density, defensive shielding against external infection",
        "afflicted_expression": "Crystallization, gallstones, dry sallow skin, stiff joints, chronic lingering invalidism, hypochondria",
    },
    {
        "planet": "Jupiter",
        "planet_ta": "குரு",
        "salient_keyword": "Idealism",
        "anatomical_rulership": "Liver, glycogen reserves, suprarenals, arterial circulation, fibrin of blood, disposition of fats",
        "pathological_quality": "Warm, moist, nourishing, expansive, corpulent, gourmandizing",
        "positive_expression": "Benevolent vitality, clean arterial flow, generous bodily warmth, rapid recuperative rebound",
        "afflicted_expression": "Fatty liver, apoplexy, plethoric arterial hypertension, gout, indolent growths",
    },
    {
        "planet": "Mars",
        "planet_ta": "செவ்வாய்",
        "salient_keyword": "Dynamic Energy",
        "anatomical_rulership": "Iron in blood, red coloring matter (hemoglobin), genitals, motor nerves, left cerebral hemisphere, rectum",
        "pathological_quality": "Hot, dry, inflammatory, energetic, eruptive, excessive, violent, positive",
        "positive_expression": "Dynamic muscular tone, robust hemoglobin, iron-willed recuperative stamina",
        "afflicted_expression": "High fevers, acute inflammation, hemorrhage, surgical lacerations, burns, eruptive skin boils",
    },
    {
        "planet": "Uranus",
        "planet_ta": "யுரேனஸ்",
        "salient_keyword": "Altruism",
        "anatomical_rulership": "Ethers, eyes, pituitary body, bodily gases, neural electricity",
        "pathological_quality": "Dry, spasmodic, electric, explosive, convulsive, disorganizing",
        "positive_expression": "Intuition, inventive original genius, spiritual aura attunement",
        "afflicted_expression": "Sudden nervous spasms, cramps, St. Vitus dance, electrical shock accidents, hysteria",
    },
    {
        "planet": "Neptune",
        "planet_ta": "நெப்டியூன்",
        "salient_keyword": "Divinity",
        "anatomical_rulership": "Pineal gland, spinal canal, subtle nerve fiber",
        "pathological_quality": "Comatose, shrinking, stunting, restricting, constricting",
        "positive_expression": "Cosmic consciousness, mystical inspiration, spiritual healing sensitivity",
        "afflicted_expression": "Unhealthy mediumship, alcoholic delirium tremens, drug hallucinations, comatose stupor",
    },
    {
        "planet": "Pluto",
        "planet_ta": "புளூட்டோ",
        "salient_keyword": "Regeneration",
        "anatomical_rulership": "Pancreas, cellular metabolism, deep excretory elimination",
        "pathological_quality": "Volcanic, transforming, eliminative, deep metamorphic",
        "positive_expression": "Cellular rebirth, profound systemic detoxification, survival under crisis",
        "afflicted_expression": "Metabolic breakdown, pancreatic degeneration, toxic cellular stagnation",
    },
]

# ---------------------------------------------------------------------------
# 4. Sense Organs Astrological Affinities (Heindel Chapter II)
# ---------------------------------------------------------------------------

HEINDEL_SENSE_ORGANS: List[Dict[str, str]] = [
    {
        "organ_en": "Eyes (Vision)",
        "organ_ta": "கண்கள் (பார்வை)",
        "astrological_rulers": "Aries, Uranus, Sun, Moon; Critical Nebulae: Pleiades (Taurus 29°), Ascelli (Leo 6°), Antares (Sagittarius 8°)",
        "pathological_notes_en": "Sun/Moon afflicted in Aries or conjoined with nebular fixed stars causes cataracts, glaucoma, or blindness.",
        "pathological_notes_ta": "சூரியன் அல்லது சந்திரன் மேஷத்திலோ அல்லது கிருத்திகை/மகம்/கேட்டை நட்சத்திர நெபுலா புள்ளிகளிலோ பாதிக்கப்பட்டால் கண் பார்வைக் குறைபாடுகள் தோன்றும்.",
    },
    {
        "organ_en": "Ears (Hearing)",
        "organ_ta": "காதுகள் (கேட்டல்)",
        "astrological_rulers": "Taurus, Mercury; 12th House / Capricorn",
        "pathological_notes_en": "Mercury in 12th house or in Capricorn afflicted by malefics impairs the auditory nerve and causes hearing loss.",
        "pathological_notes_ta": "புதன் 12-ம் வீட்டில் அல்லது மகரத்தில் சனியின் சேர்க்கை அல்லது பார்வையில் பாதிக்கப்பட்டால் செவிப்புலன் நரம்புகள் பாதிக்கப்படும்.",
    },
    {
        "organ_en": "Nose (Smell)",
        "organ_ta": "மூக்கு (நுகர்தல்)",
        "astrological_rulers": "Scorpio, Mars",
        "pathological_notes_en": "Scorpio rules nasal bones, cartilage, and mucous membrane; afflicted Scorpio causes chronic nasal catarrh and polypi.",
        "pathological_notes_ta": "விருச்சிகம் மூக்கு எலும்பு மற்றும் சளிச் சவ்வுகளை ஆள்கிறது; இங்கு செவ்வாய் அல்லது சனி பாதித்தால் நாசி சதை வளர்ச்சி, சைனஸ் ஏற்படும்.",
    },
    {
        "organ_en": "Tongue (Taste & Speech)",
        "organ_ta": "நாக்கு (சுவை & பேச்சு)",
        "astrological_rulers": "Taurus, Mercury",
        "pathological_notes_en": "Taurus rules larynx, vocal cords, and tongue; afflictions cause loss of speech, stammering, and taste blunting.",
        "pathological_notes_ta": "ரிஷபமும் புதனும் நாக்கு, குரல்வளையை ஆளுகின்றன; இவற்றின் பாதிப்பு பேச்சுத் தடுமாற்றம், தொண்டை அழற்சியை உண்டாக்கும்.",
    },
]

# ---------------------------------------------------------------------------
# 5. The Three Vicious Circles of Sympathy & Reflex Action (Heindel Chapter III)
# ---------------------------------------------------------------------------

HEINDEL_VICIOUS_CIRCLES: List[Dict[str, Any]] = [
    {
        "cross_name": "The Cardinal (Equinoctial) Cross",
        "cross_name_ta": "சர ராசி வட்டப் பிணைப்பு (Equinoctial Circle)",
        "signs_involved": ["Aries", "Cancer", "Libra", "Capricorn"],
        "organ_sympathies": "Head/Eyes (Aries) <-> Stomach (Cancer) <-> Kidneys/Skin (Libra) <-> Knees/Joints (Capricorn)",
        "clinical_mechanism": (
            "Doctors have noted strange sympathy between distant organs. Trouble in the stomach (Cancer) frequently "
            "manifests as eye glaucoma (Aries) or disturbed kidneys (Libra). Saturn in Cancer robs the stomach of fluids, "
            "invariably disturbing kidney elimination and causing stiff knee joints (Capricorn)."
        ),
        "clinical_examples": [
            "Glaucoma and eye strain whose real seat is rooted in digestive indigestion or kidney failure.",
            "Saturn in Cancer (fall): Extreme food likes/dislikes -> gastric catarrh -> kidney toxicity -> stiff knees.",
            "Headaches and migraines triggered by autointoxication from stomach and sluggish kidneys.",
        ],
    },
    {
        "cross_name": "The Fixed Cross",
        "cross_name_ta": "ஸ்திர ராசி வட்டப் பிணைப்பு (Fixed Circle)",
        "signs_involved": ["Taurus", "Leo", "Scorpio", "Aquarius"],
        "organ_sympathies": "Throat/Vocal (Taurus) <-> Heart/Spine (Leo) <-> Generative/Rectum/Nose (Scorpio) <-> Calves/Ankles (Aquarius)",
        "clinical_mechanism": (
            "Profound sympathy exists between the sex organs (Scorpio) and speech organs (Taurus). Tonsil or adenoid "
            "operations in childhood often create severe reproductive/childbirth difficulties at puberty. Valvular heart trouble "
            "(Leo) regularly precipitates dropsical swelling of the ankles (Aquarius)."
        ),
        "clinical_examples": [
            "Childhood vocal/tonsil surgeries producing menstrual disorders and difficult labor in later female life.",
            "Valvular heart disease (Leo) producing venous stasis and ankle edema (Aquarius).",
            "Removal of sex organs causing sudden shift in voice pitch (male voice becoming feminine, female voice masculine).",
        ],
    },
    {
        "cross_name": "The Mutable (Common) Cross",
        "cross_name_ta": "உபய ராசி வட்டப் பிணைப்பு (Common / Cadent Circle)",
        "signs_involved": ["Gemini", "Virgo", "Sagittarius", "Pisces"],
        "organ_sympathies": "Lungs/Breathing (Gemini) <-> Intestines/Spleen (Virgo) <-> Hips/Sciatic (Sagittarius) <-> Feet/Fibrin (Pisces)",
        "clinical_mechanism": (
            "Mutable signs rule the cadent houses (6th house of sickness & 12th house of hospitals). They produce "
            "more chronic invalids due to fluctuating willpower. Sympathy between feet (Pisces) and lungs (Gemini) "
            "is confirmed by the universal clinical experience: 'catching cold or pneumonia due to wet feet'. "
            "Intestinal stasis (Virgo) floods the bloodstream and strains pulmonary oxygenation."
        ),
        "clinical_examples": [
            "Wet and cold feet (Pisces) instantly precipitating acute bronchitis or pneumonia in lungs (Gemini).",
            "Sluggish intestinal toxemia (Virgo) undermining sciatic nerves (Sagittarius) and respiratory vitality.",
            "Lack of willpower in common signs allowing acute functional disorders to slip into chronic invalidism.",
        ],
    },
]

# ---------------------------------------------------------------------------
# 6. Hand and Finger Nail Astro-Diagnosis (Heindel Chapter X)
# ---------------------------------------------------------------------------

HEINDEL_NAIL_DIAGNOSIS_DATA: List[Dict[str, Any]] = [
    {
        "nail_type_en": "Heart Trouble Indications (Leo Type)",
        "nail_type_ta": "இதயக் கோளாறு நக அறிகுறிகள் (சிம்ம வகை)",
        "physical_indicators": "Large broad nail; blue half-moons (lunulae); blue palm lines; longitudinal lengthwise ridges; corners curving upwards away from flesh in chronic cases.",
        "pathological_significance": "Weakened cardiac circulation, valvular insufficiency, poor venous oxygenation.",
        "constitutional_correlation": "Leo Ascendant or Mars/Saturn square Venus afflicting the cardiac center.",
        "remedial_and_hygiene_guidance": "Avoid heavy athletic strain, maintain regular rest, avoid rich heavy meals that burden the heart.",
    },
    {
        "nail_type_en": "Liver & Hepatic Trouble (Jupiter Type)",
        "nail_type_ta": "கல்லீரல் & பித்தக் கோளாறு நக அறிகுறிகள் (குரு வகை)",
        "physical_indicators": "Large nail longer than normal; wedging into flesh on the sides; yellowish tint on nails and yellow lines in palm.",
        "pathological_significance": "Biliary stasis, liver enlargement, glycogen sluggishness, sluggish bowel detox.",
        "constitutional_correlation": "Jupiter afflicted by Saturn or Mars in Virgo/Cancer/Sagittarius.",
        "remedial_and_hygiene_guidance": "Eliminate fried and fatty foods, drink lemon water, incorporate daily walking and bitter leafy greens.",
    },
    {
        "nail_type_en": "Pulmonary & Lung Weakness (Gemini / Watery Type)",
        "nail_type_ta": "நுரையீரல் பலவீன நக அறிகுறிகள் (மிதுன வகை)",
        "physical_indicators": "Long slender claw-like nails; pale whitish hue; ridged lengthwise; thin delicate skin.",
        "pathological_significance": "Tubercular susceptibility, weak thoracic capacity, shallow pulmonary exchange, chronic coughs.",
        "constitutional_correlation": "Gemini rising or Saturn/Mars afflicting Sun or Mercury in common signs.",
        "remedial_and_hygiene_guidance": "Calisthenics, fresh sleeping apartment ventilation, rhythmic deep breathing exercises.",
    },
    {
        "nail_type_en": "Nervous Exhaustion (Mercury Type)",
        "nail_type_ta": "நரம்புத் தளர்ச்சி நக அறிகுறிகள் (புதன் வகை)",
        "physical_indicators": "Narrow, delicate, thin, brittle nails; white spots scattered across nail plates.",
        "pathological_significance": "Impoverished blood, anemia, nervous overwork, sensory tension.",
        "constitutional_correlation": "Mercury square or opposite Saturn or Uranus; prominent airy signs.",
        "remedial_and_hygiene_guidance": "Nervine rest, warm oil massage, reduction of intellectual hyper-stimulation, calm rose-colored environment.",
    },
    {
        "nail_type_en": "Temperamental Lack of Control (Nail Biting)",
        "nail_type_ta": "முன்கோபம் & கட்டுப்பாடின்மை (நகங்களைக் கடிக்கும் இயல்பு)",
        "physical_indicators": "Short, bitten, jagged nail beds; carrying chips on shoulder, easily wounded feelings.",
        "pathological_significance": "Explosive temper, lack of nervous self-control, subconscious emotional tension.",
        "constitutional_correlation": "Mars afflicted by Uranus or Mercury in fiery or cardinal signs.",
        "remedial_and_hygiene_guidance": "Cultivate conscious emotional pause, rhythmic slow breathing when irritated, artistic outlets.",
    },
    {
        "nail_type_en": "Spinal & Structural Weakness",
        "nail_type_ta": "முதுகெலும்பு பலவீன நக அறிகுறிகள்",
        "physical_indicators": "Concave top surface of nails ('spooned' nail plates / koilonychia).",
        "pathological_significance": "Spinal weakness, vertebral misalignment, calcium metabolic deficiency.",
        "constitutional_correlation": "Afflictions in Leo (dorsal spine) or Capricorn/Sagittarius (sacral/skeletal).",
        "remedial_and_hygiene_guidance": "Postural exercises, gentle spinal traction, sunlight therapy for mineral assimilation.",
    },
    {
        "nail_type_en": "The Thumb: Will vs Logic Proportion",
        "nail_type_ta": "பெருவிரல்: இச்சை & புத்தி சமநிலை",
        "physical_indicators": (
            "Well-proportioned: 1st phalanx (will) = 2/5th, 2nd phalanx (reason) = 3/5th. "
            "Tip reaches middle joint of index finger. Club-shaped thumb with short nail = ungovernable temper ('sees red'). "
            "Very long 1st phalanx = reckless impulse; very long 2nd phalanx = talker but not doer."
        ),
        "pathological_significance": "Reveals whether the patient has sufficient willpower to follow hygienic directions and overcome illness.",
        "constitutional_correlation": "Mount of Venus at base of thumb (vitality & desire); Mount of Luna (imagination & nervous balance).",
        "remedial_and_hygiene_guidance": "Healers must gauge patient will-power from the thumb before outlining extensive lifestyle regimes.",
    },
]

# ---------------------------------------------------------------------------
# 7. Planetary Antidotes, Metals, Gems, and Colors (Heindel pp. 72-73)
# ---------------------------------------------------------------------------

HEINDEL_PLANETARY_ANTIDOTES: List[Dict[str, Any]] = [
    {
        "afflicting_planet": "Mars (Excessive Heat, Fevers, Violence, Inflammation)",
        "afflicting_metal": "Iron",
        "antidote_planet": "Venus",
        "antidote_metal": "Copper",
        "antidote_gem": "Emerald / Moss Agate",
        "antidote_color": "Yellow / Soft Green",
        "polarity_law": (
            "Mars represents animal passion, physical friction, and inflammatory heat. Venus is the celestial opposite of Mars; "
            "her soothing love-ray and metal Copper act as a natural vibratory antidote for harsh martial vibrations. "
            "A person with excessive Mars should have minimal contact with raw iron and utilize copper and calm colors."
        ),
        "practical_application": "Drink water stored in copper vessels, wear soft green or yellow tones, avoid fiery spices.",
    },
    {
        "afflicting_planet": "Saturn (Cold Obstruction, Melancholy, Crystallization)",
        "afflicting_metal": "Lead",
        "antidote_planet": "Jupiter",
        "antidote_metal": "Tin",
        "antidote_gem": "Turquoise / Carbuncle",
        "antidote_color": "Sky Blue",
        "polarity_law": (
            "Saturn represents contraction, binding, cold, and obstruction. Jupiter is his celestial opposite; "
            "his expansive, benevolent warmth and metal Tin dissolve Saturnian crystallization and melancholia. "
            "Tin and sky-blue vibrations stimulate cheerfulness and arterial warmth."
        ),
        "practical_application": "Wear tin-based talismanic charms or sky-blue apparel, spend time in sunny rooms, cultivate jovial company.",
    },
]

# ---------------------------------------------------------------------------
# 8. Critical Nebular Spots & Fixed Stars (Aphorisms 20, 33)
# ---------------------------------------------------------------------------

HEINDEL_NEBULAR_SPOTS: List[Dict[str, Any]] = [
    {
        "name": "Pleiades",
        "zodiac_degree": "29° Taurus",
        "pathological_focus": "Severe Ocular Affections, Visual Weakness, Cataracts",
        "esoteric_mitigation": "When benevolence aspects this degree, loss of physical sight awakens inner clairvoyant second-sight.",
    },
    {
        "name": "Ascelli",
        "zodiac_degree": "6° Leo",
        "pathological_focus": "Ocular Inflammation, Corneal Affections, Impaired Visual Acuity",
        "esoteric_mitigation": "Encourages spiritual introspection and deep solar inner light.",
    },
    {
        "name": "Antares",
        "zodiac_degree": "8° Sagittarius",
        "pathological_focus": "Acute Eye Afflictions, Traumatic Eye Injuries, Blindness Risk",
        "esoteric_mitigation": "The most potent nebular spot. While malefic configurations harm physical sight, benefic aspects bestow profound second-sight.",
    },
]

# ---------------------------------------------------------------------------
# 9. The 43 Golden Aphorisms of Astro-Diagnosis (Heindel Chapter IX)
# ---------------------------------------------------------------------------

HEINDEL_APHORISMS_LIST: List[Dict[str, Any]] = [
    {
        "number": 1,
        "category": "Lunar Cycles",
        "aphorism_en": "The Moon may be regarded as the giver and the taker of life; carrying life forces from Sun to earth, and eventually producing death.",
        "aphorism_ta": "சந்திரன் உயிரை அளிப்பவராகவும் எடுப்பவராகவும் கருதப்படுகிறார்; சூரியனின் பிராண சக்தியை பூமிக்குக் கடத்துகிறார், முடிவில் மரணத்தையும் ஏற்படுத்துகிறார்.",
        "practical_implication": "Watch the Moon's phase and aspects continuously in all therapeutic schedules.",
    },
    {
        "number": 2,
        "category": "Lunar Cycles",
        "aphorism_en": "When the Moon is full, tides are higher, bones are fuller of marrow, and body temperature is highest in fevers.",
        "aphorism_ta": "பௌர்ணமி நாளில் கடல் அலைகள் உயர்வது போல், எலும்பு மஜ்ஜை நிரம்புகிறது; காய்ச்சலின் போது உடல் வெப்பம் உச்சமடைகிறது.",
        "practical_implication": "Anticipate fever spikes during the Full Moon; employ cooling hydropathy.",
    },
    {
        "number": 3,
        "category": "Natal Constitution",
        "aphorism_en": "During the first half of life (particularly childhood) the Moon has greatest rule; in the latter half, the Sun has strongest influence.",
        "aphorism_ta": "வாழ்வின் முதல் பாதியில் (குறிப்பாக குழந்தைப் பருவத்தில்) சந்திரன் ஆதிக்கமும், இரண்டாம் பாதியில் சூரியனின் ஆதிக்கமும் மேலோங்குகிறது.",
        "practical_implication": "Pediatric ailments correlate primarily to the Moon; adult degenerative issues to the Sun.",
    },
    {
        "number": 4,
        "category": "Natal Constitution",
        "aphorism_en": "The Moon has great influence over nervous, hysterical, and lunatic patients. They should never sleep with the moon shining on them.",
        "aphorism_ta": "மன அழுத்தம், நரம்புத் தளர்ச்சி, ஹிஸ்டீரியா நோயாளிகள் மீது சந்திரன் அதிக தாக்கம் செலுத்துகிறார். அவர்கள் நிலா வெளிச்சம் நேராகப் படும்படி தூங்கக் கூடாது.",
        "practical_implication": "Shield bedrooms of sensitive or insomnia patients from direct lunar rays.",
    },
    {
        "number": 5,
        "category": "Lunar Cycles",
        "aphorism_en": "At New Moon material forces are weakest. The waning moon (Full to New) is strongest for spiritual healing and elimination.",
        "aphorism_ta": "அமாவாசையில் உடலின் ஸ்தூல ஆற்றல் மிகக் குறைவாக இருக்கும். பௌர்ணமி முதல் அமாவாசை வரையிலான தேய்பிறை காலம் நச்சு நீக்கத்திற்கும் ஆன்மீக சிகிச்சைகளுக்கும் உகந்தது.",
        "practical_implication": "Schedule detoxification, cleansing fasts, and spiritual meditations during waning moon.",
    },
    {
        "number": 6,
        "category": "Surgical Precaution",
        "aphorism_en": "Do not perform an operation when the Moon is in the sign ruling that part of the body. (Ptolemy: 'Pierce not with iron that part of the body governed by the sign occupied by the Moon').",
        "aphorism_ta": "சந்திரன் எந்த ராசியில் சஞ்சரிக்கிறதோ, அந்த ராசிக்குரிய உடல் உறுப்பில் அறுவை சிகிச்சை செய்யக் கூடாது (தாலமியின் பொன்மொழி: 'சந்திரன் நிற்கும் ராசியின் உறுப்பை இரும்பால் துளைக்காதே').",
        "practical_implication": "Golden rule of surgical timing: avoid operations when transiting Moon occupies the governed organ sign.",
    },
    {
        "number": 7,
        "category": "Surgical Precaution",
        "aphorism_en": "Operations performed at exact change of the Moon are rarely successful. Choose waxing moon ('light of the moon'). Do not operate when Sun is in sign of the organ.",
        "aphorism_ta": "சந்திர மாற்ற தினங்களில் (அமாவாசை/பௌர்ணமி சந்தி) செய்யப்படும் அறுவை சிகிச்சைகள் அரிதாகவே வெற்றியடைகின்றன. வளர்பிறையைத் தேர்ந்தெடுக்கவும்; சூரியன் அந்த உறுப்பு ராசியில் இருக்கும்போதும் அறுவை சிகிச்சை செய்யக் கூடாது.",
        "practical_implication": "Avoid surgery at exact lunations; favor waxing lunar phases for tissue repair.",
    },
    {
        "number": 8,
        "category": "Lunar Cycles",
        "aphorism_en": "Disease reaches a critical turning point every 7 days (7th day square, 14th day opposition, 21st day square, 28th day cycle).",
        "aphorism_ta": "நோய்கள் ஒவ்வொரு 7 நாட்களுக்கும் ஒரு திருப்புமுனையை அடைகின்றன (7-ம் நாள் கேந்திர சதுரம், 14-ம் நாள் சமசப்தகம், 21-ம் நாள் மறு சதுரம், 28-ம் நாள் முழுச் சுற்று).",
        "practical_implication": "Carefully manage patient crisis on the 7th, 14th, and 21st days of an acute illness.",
    },
    {
        "number": 9,
        "category": "Natal Constitution",
        "aphorism_en": "The Moon rules acute disease; the Sun rules chronic disease.",
        "aphorism_ta": "சந்திரன் குறுகிய கால தீவிர நோய்களையும், சூரியன் நீண்ட கால நாள்பட்ட நோய்களையும் ஆளுகிறார்.",
        "practical_implication": "Trace acute flare-ups to lunar transits; evaluate chronic endurance via solar dignity.",
    },
    {
        "number": 10,
        "category": "Surgical Precaution",
        "aphorism_en": "Watch squares and oppositions of the Moon to transiting Sun, Mars, and Saturn when operating.",
        "aphorism_ta": "அறுவை சிகிச்சையின் போது சந்திரன் கோச்சார சூரியன், செவ்வாய், சனியுடன் 90° அல்லது 180° பார்வையில் இருப்பதைத் தவிர்க்க வேண்டும்.",
        "practical_implication": "Elective surgery must avoid lunar square or opposition to Mars (hemorrhage) or Saturn (hypothermia/collapse).",
    },
    {
        "number": 11,
        "category": "Natal Constitution",
        "aphorism_en": "The Moon has greatest rule over the health of woman, while the Sun influences the health of man.",
        "aphorism_ta": "பெண்களின் உடல்நலத்தில் சந்திரன் பிரதான ஆதிக்கம் செலுத்துகிறார்; ஆண்களின் உடல்நலத்தில் சூரியன் முதன்மை பெறுகிறார்.",
        "practical_implication": "Weigh Moon afflictions heavier in female nativities and Sun afflictions in male nativities.",
    },
    {
        "number": 12,
        "category": "Therapeutic Dosage",
        "aphorism_en": "From New to Full Moon stimulants produce the most effect and sedatives are weakest; decrease stimulant dose and increase sedatives.",
        "aphorism_ta": "அமாவாசை முதல் பௌர்ணமி வரை ஊக்கிகள் தீவிரமாகவும் அமைதிப்படுத்திகள் பலவீனமாகவும் செயல்படும்; ஊக்கிகளின் அளவைக் குறைத்து அமைதிப்படுத்திகளை அதிகரிக்க வேண்டும்.",
        "practical_implication": "Calibrate pharmacological and herbal dosages to waxing vs waning lunar phases.",
    },
    {
        "number": 13,
        "category": "Therapeutic Dosage",
        "aphorism_en": "When increasing Moon is in good aspect to radical Jupiter or Venus, cardiac stimulation produces most lasting results.",
        "aphorism_ta": "வளர்பிறை சந்திரன் ஜாதக குரு அல்லது சுக்கிரனுடன் சுப பார்வை பெறும்போது இதய ஊட்ட சிகிச்சைகள் நீடித்த பலனைத் தரும்.",
        "practical_implication": "Best timing for heart tonic therapies is during waxing Moon trine/sextile Venus or Jupiter.",
    },
    {
        "number": 14,
        "category": "Transits",
        "aphorism_en": "Good aspects to radical Moon from transiting Jupiter and Venus are very helpful in overcoming illness.",
        "aphorism_ta": "கோச்சார குரு மற்றும் சுக்கிரன் ஜாதக சந்திரன் மீது நல்ல பார்வை செலுத்தும் போது நோயில் இருந்து மீள்வது மிக எளிதாகிறது.",
        "practical_implication": "Look to transit Jupiter or Venus trines to natal Moon for optimal convalescence.",
    },
    {
        "number": 15,
        "category": "Natal Constitution",
        "aphorism_en": "Saturn placed in the 6th house of the horoscope at birth has a persistent tendency to lower vitality.",
        "aphorism_ta": "பிறப்பு ஜாதகத்தில் 6-ம் பாவத்தில் அமரும் சனி உடலின் நோய் எதிர்ப்பு சக்தியையும் பிராண பலத்தையும் குறைக்கும் தன்மையுடையவர்.",
        "practical_implication": "Native requires lifelong habits of regular rest, warm foods, and avoidance of chills.",
    },
    {
        "number": 16,
        "category": "Natal Constitution",
        "aphorism_en": "The sign and house of the Sun at birth is a vital locality; from its strength one may judge the patient's recuperative power.",
        "aphorism_ta": "சூரியன் நிற்கும் ராசியும் பாவமும் மிக முக்கியமானவை; அதன் பலத்தைக் கொண்டே நோயாளியின் குணமாகும் வேகத்தைக் கணிக்கலாம்.",
        "practical_implication": "Strong Sun in Aries/Leo/Sagittarius ensures rapid cellular recovery.",
    },
    {
        "number": 17,
        "category": "Natal Constitution",
        "aphorism_en": "Benefic aspects between Sun and Mars give great vitality. An evil aspect between Sun and Mars is better than no aspect at all.",
        "aphorism_ta": "சூரியன் மற்றும் செவ்வாய் இடையேயான சுப சேர்க்கை அதீத பலத்தைத் தரும்; இவற்றிடையே அசுப பார்வை இருந்தாலும் கூட, எந்த பார்வையும் இல்லாமல் இருப்பதை விட அது நன்று.",
        "practical_implication": "Mars-Sun aspects provide dynamic fighting vitality against bacterial onslaughts.",
    },
    {
        "number": 18,
        "category": "Diagnostic Discretion",
        "aphorism_en": "Aspects to Ascendant and Midheaven should be used with great discretion unless the minute of birth is verified.",
        "aphorism_ta": "பிறப்பு நேரம் மிகத் துல்லியமாக உறுதி செய்யப்படாதவரை லக்னம் மற்றும் பத்தாம் பாவ புள்ளியின் பார்வைகளை எச்சரிக்கையுடன் கையாள வேண்டும்.",
        "practical_implication": "Verify birth time against physical appearance and nail types before relying on degree cusps.",
    },
    {
        "number": 19,
        "category": "Critical Degrees",
        "aphorism_en": "Planets in critical degrees have a greater influence for good or evil than in other degrees.",
        "aphorism_ta": "முக்கிய சந்திகளிலும் நெருக்கடி பாகைகளிலும் நிற்கும் கிரகங்கள் அதீத நன்மையையோ அல்லது தீவிர தீமையையோ உண்டாக்கும்.",
        "practical_implication": "Examine planets in 0° or 29° of signs for intense constitutional reactions.",
    },
    {
        "number": 20,
        "category": "Fixed Stars",
        "aphorism_en": "Watch three nebular spots: Pleiades (29° Taurus), Ascelli (6° Leo), and Antares (8° Sagittarius); they powerfully affect eyesight.",
        "aphorism_ta": "மூன்று நட்சத்திர நெபுலா புள்ளிகளைக் கவனியுங்கள்: கிருத்திகை (ரிஷபம் 29°), மகம் (சிம்மம் 6°), கேட்டை (தனுசு 8°); இவை கண் பார்வையை பெரிதும் பாதிக்கும்.",
        "practical_implication": "Check Sun, Moon, or malefics on these coordinates for ocular vulnerability.",
    },
    {
        "number": 21,
        "category": "Natal Constitution",
        "aphorism_en": "A child with no aspect between Sun and Mars is subject to many childhood illnesses due to lack of muscular fighting heat.",
        "aphorism_ta": "சூரியனுக்கும் செவ்வாய்க்கும் இடையே எந்தத் தொடர்பும் இல்லாத குழந்தை, தற்காப்பு உஷ்ணம் இன்மையால் அடிக்கடி நோய்களுக்கு ஆளாகும்.",
        "practical_implication": "Nourish the child with iron-rich foods, sunlight, and invigorating play.",
    },
    {
        "number": 22,
        "category": "Environment Therapy",
        "aphorism_en": "Patients with planets in airy signs require abundant fresh air; fiery signs require sunlight; watery/earthy signs suffer from excessive sun.",
        "aphorism_ta": "காற்று ராசியினர் அதிக தூய காற்றையும், நெருப்பு ராசியினர் அதிக சூரிய ஒளியையும் விரும்புகிறார்கள்; நீர் மற்றும் நில ராசியினருக்கு அதிக வெயில் பாதகமாகும்.",
        "practical_implication": "Customize patient sickroom ventilation and sunlight exposure to natal elemental dominance.",
    },
    {
        "number": 23,
        "category": "Natal Constitution",
        "aphorism_en": "Fixed signs on angles with afflictions in common signs allows native to overcome disease. Common signs on angles with fixed afflictions succumbs easily.",
        "aphorism_ta": "ஸ்திர ராசிகள் கேந்திரத்தில் இருந்து உபய ராசிகளில் தோஷம் இருந்தால் நோய் குணமாகும்; உபய ராசிகள் கேந்திரத்தில் இருந்து ஸ்திர ராசிகளில் தோஷம் இருந்தால் நோயில் வீழ்வர்.",
        "practical_implication": "Angular stability determines constitutional tenacity to throw off disease.",
    },
    {
        "number": 24,
        "category": "Natal Constitution",
        "aphorism_en": "A well-aspected Sun in Aries or Leo gives radiant vitality and an innate ability to throw off disease.",
        "aphorism_ta": "மேஷம் அல்லது சிம்மத்தில் சுப பார்வை பெற்ற சூரியன் அபார பிராண சக்தியையும் நோய்களை அண்டவிடாத இயற்கை வலிமையையும் தருகிறார்.",
        "practical_implication": "Native rarely requires extensive pharmaceuticals; simple natural hygiene suffices.",
    },
    {
        "number": 25,
        "category": "Natal Constitution",
        "aphorism_en": "People with Aries rising or Sun/Mars in Aries develop very high temperatures quickly, blood rushing to head and skin.",
        "aphorism_ta": "மேஷ லக்னம் அல்லது மேஷத்தில் சூரியன்/செவ்வாய் உள்ளவர்கள் நோயுற்றால் தலைக்கும் தோலுக்கும் இரத்தம் பாய்ந்து அதிதீவிர காய்ச்சல் உடனடியாகத் தோன்றும்.",
        "practical_implication": "Apply prompt cold compresses to head; do not panic as Aries easily endures high fevers.",
    },
    {
        "number": 26,
        "category": "Natal Constitution",
        "aphorism_en": "Sun afflicted by Saturn or Moon square Sun yields low vitality. Watch progressed Moon and lunation transits.",
        "aphorism_ta": "சூரியன் சனியால் பாதிக்கப்பட்டாலோ அல்லது சந்திரன் சூரியனுடன் சதுரப் பார்வை பெற்றாலோ குறைந்த பிராண சக்தியே இருக்கும்.",
        "practical_implication": "Native must pace their daily exertions and avoid extreme physical fatigue.",
    },
    {
        "number": 27,
        "category": "Planetary Motion",
        "aphorism_en": "Retrograde planets give latent influence in disease; their effect is dormant until they turn direct in progression or transit.",
        "aphorism_ta": "வக்ர கிரகங்கள் நோயில் மறைமுக தாக்கத்தை அளிக்கின்றன; அவை நேர்கதியில் திரும்பும் போதே அவற்றின் உண்மையான பலன் வெளிப்படும்.",
        "practical_implication": "Dormant symptoms may flare into clinical manifestation when the afflicting planet turns direct.",
    },
    {
        "number": 28,
        "category": "Planetary Motion",
        "aphorism_en": "Planets turning from retrograde to direct move slowly; their influence is not as vital as when swiftly moving.",
        "aphorism_ta": "வக்ர நிவர்த்தியாகி மெதுவாக நகரும் கிரகங்களின் ஆற்றல் வேகமாக நகரும் நிலையை விட மந்தமாகவே செயல்படும்.",
        "practical_implication": "Convalescence proceeds slowly while key significators linger in stationary motion.",
    },
    {
        "number": 29,
        "category": "Planetary Dignity",
        "aphorism_en": "Planets are strong when in signs of their own nature, and when in aspect to planets in compatible signs.",
        "aphorism_ta": "கிரகங்கள் தங்கள் சுபாவத்திற்கு ஒத்த ராசிகளிலும், நட்பான ராசி கிரகங்களுடன் இணையும் போதும் வலிமை பெறுகின்றன.",
        "practical_implication": "Elemental compatibility between aspecting planets fosters physiological harmony.",
    },
    {
        "number": 30,
        "category": "Diagnostic Method",
        "aphorism_en": "When birth hour is unknown, a fairly accurate diagnosis can be obtained using a flat chart (Aries on 1st house).",
        "aphorism_ta": "பிறந்த நேரம் தெரியாத போது, மேஷத்தை முதல் வீடாகக் கொண்டு அமைக்கும் காலபுருஷ சக்கரம் மூலமும் துல்லியமாக ஆராயலாம்.",
        "practical_implication": "Flat Kalapurusha charts provide invaluable baseline organ vulnerability assessments.",
    },
    {
        "number": 31,
        "category": "Planetary Action",
        "aphorism_en": "Saturn's influence is contracting and binding, while Mars' influence is loosening, inflammatory, and eruptive.",
        "aphorism_ta": "சனியின் தாக்கம் சுருக்குதல், இறுக்குதல் மற்றும் அடைப்பைத் தரும்; செவ்வாயின் தாக்கம் தளர்வு, உஷ்ணம் மற்றும் வெடிப்பைத் தரும்.",
        "practical_implication": "Distinguish between Saturnine stricture/atrophy and Martial hemorrhage/ulceration.",
    },
    {
        "number": 32,
        "category": "Solar Vitality",
        "aphorism_en": "The Sun rules the vital etheric fluid specialized through the spleen; afflictions to Sun cause vitality breakdown.",
        "aphorism_ta": "மண்ணீரல் மூலம் உடலுக்குள் பரவும் பிராண எத்தர் திரவத்தை சூரியன் ஆள்கிறார்; சூரியன் கெட்டால் பிராண சக்தி வடிந்துவிடும்.",
        "practical_implication": "Support spleen and solar plexus through morning sunlight and deep conscious respiration.",
    },
    {
        "number": 33,
        "category": "Fixed Stars",
        "aphorism_en": "Radical Sun or Moon within orb of Pleiades (29° Taurus), Ascelli (6° Leo), or Antares (8° Sag) indicates serious eye trouble.",
        "aphorism_ta": "ஜாதக சூரியன் அல்லது சந்திரன் கிருத்திகை (29°), மகம் (6°), அல்லது கேட்டை (8°) பாகையில் இருந்தால் தீவிர கண் கோளாறுகள் ஏற்படும்.",
        "practical_implication": "Protect vision from glare and avoid eye surgeries during adverse transits to these points.",
    },
    {
        "number": 34,
        "category": "Sense Organs",
        "aphorism_en": "Mercury in the 12th house afflicted by malefics, or Mercury in Capricorn afflicted, will impair hearing.",
        "aphorism_ta": "புதன் 12-ம் வீட்டில் அசுப கிரகங்களால் பாதிக்கப்பட்டாலோ அல்லது மகரத்தில் பாதிக்கப்பட்டாலோ செவித்திறன் குறையும்.",
        "practical_implication": "Examine auditory nerves and avoid loud noise trauma for natives with this placement.",
    },
    {
        "number": 35,
        "category": "House Influences",
        "aphorism_en": "Watch malefic planets placed in 6th (sickness) or 12th (hospitals and confinement).",
        "aphorism_ta": "6-ம் பாவம் (நோய்) அல்லது 12-ம் பாவத்தில் (மருத்துவமனை அனுமதி) உள்ள அசுப கிரகங்களை மிகக் கவனமாக ஆராய வேண்டும்.",
        "practical_implication": "Malefics in 12th signal prolonged hospital confinement during their active dasha periods.",
    },
    {
        "number": 36,
        "category": "Planetary Detriment",
        "aphorism_en": "Antipathy between signs and planets (e.g. fiery Mars in watery Pisces, cold Saturn in fiery Aries) becomes a menace to health.",
        "aphorism_ta": "பகை ராசிகளில் கிரகங்கள் அமர்வது (எ.கா: நீரில் செவ்வாய், நெருப்பில் சனி) உடல் நலத்திற்கு பெரும் அச்சுறுத்தலாக மாறும்.",
        "practical_implication": "Elemental friction in fall/detriment signs triggers metabolic toxicity.",
    },
    {
        "number": 37,
        "category": "Natal Weakness",
        "aphorism_en": "The place where Saturn is found in the horoscope is most likely to be the weakest spot in the physical body.",
        "aphorism_ta": "ஜாதகத்தில் சனி அமர்ந்துள்ள ராசியும் பாவமுமே அந்த மனிதனின் உடலில் மிகவும் பலவீனமான, நோயால் எளிதில் தாக்கப்படும் பகுதியாகும்.",
        "practical_implication": "Focus preventive care directly upon the anatomical organ ruled by Saturn's natal house and sign.",
    },
    {
        "number": 38,
        "category": "Blood Chemistry",
        "aphorism_en": "Mars aids blood heat by dissolving iron (Mars metal), enabling hemoglobin to attract oxygen (a Sun element).",
        "aphorism_ta": "செவ்வாய் உடலில் இரும்புச்சத்தை கரைத்து வெப்பத்தை உண்டாக்குகிறது; இது சூரியனின் பிராணவாயுவை (ஆக்ஸிஜன்) இரத்தம் ஈர்க்க உதவுகிறது.",
        "practical_implication": "Anemia and cold extremities indicate deficient Martial dynamic ignition of solar oxygen.",
    },
    {
        "number": 39,
        "category": "Mental Hygiene",
        "aphorism_en": "A patient with Mercury square Saturn suffers from constitutional gloom; choose a cheerful sunny room with rose-colored walls.",
        "aphorism_ta": "புதன்-சனி சதுரப் பார்வை கொண்ட நோயாளி மனச்சோர்வால் வாடுவார்; அவருக்கு இளஞ்சிவப்பு (ரோஸ்) நிற சுவர்கள் கொண்ட சூரிய வெளிச்சம் உள்ள அறையைத் தேர்வு செய்யவும்.",
        "practical_implication": "Chromotherapy: Rose and warm tints antidote Saturnian melancholia and stimulate neurological joy.",
    },
    {
        "number": 40,
        "category": "Natal Constitution",
        "aphorism_en": "Leo on the Ascendant with Sun in Aries (exaltation) gives abundant vitality and supreme power to throw off disease.",
        "aphorism_ta": "சிம்ம லக்னமாகி சூரியன் மேஷத்தில் உச்சம் பெற்றால் அளப்பரிய பிராண சக்தியும் நோய்களை வெல்லும் மகா ஆற்றலும் உண்டாகும்.",
        "practical_implication": "Native possesses extraordinary natural self-healing and recuperative longevity.",
    },
    {
        "number": 41,
        "category": "Therapeutic Relief",
        "aphorism_en": "For Mars afflictions, seek relief when progressed Moon reaches good aspect of Venus. For Saturn afflictions, seek Moon-Jupiter aspects.",
        "aphorism_ta": "செவ்வாயின் நோய்களுக்கு சந்திரன் சுக்கிரனை சுபமாகப் பார்க்கும் போதும், சனியின் நோய்களுக்கு சந்திரன் குருவைப் பார்க்கும் போதும் நிவாரணம் கிட்டும்.",
        "practical_implication": "Venus antidotes Mars; Jupiter antidotes Saturn. Time therapeutic breakthroughs accordingly.",
    },
    {
        "number": 42,
        "category": "Disease Onset",
        "aphorism_en": "If the Moon is in conjunction with Saturn at the inception of an illness, expect the disease to be of long duration.",
        "aphorism_ta": "ஒரு நோய் தொடங்கும் நேரத்தில் சந்திரன் சனியுடன் இணைந்திருந்தால், அந்த நோய் நீண்ட காலம் நீடிக்கும் நாள்பட்ட நோயாக மாறும்.",
        "practical_implication": "Prepare the patient for long-term supportive therapy and prevent discouragement.",
    },
    {
        "number": 43,
        "category": "Disease Timing",
        "aphorism_en": "Disease related to the Moon changes within 28 days; disease related to the Sun is chronic, stubborn, and of long duration.",
        "aphorism_ta": "சந்திரன் சார்ந்த நோய் 28 நாட்களுக்குள் மாற்றம் அடையும்; சூரியன் சார்ந்த நோய் நாள்பட்டதாகவும் சிகிச்சைக்கு பிடிவாதமானதாகவும் இருக்கும்.",
        "practical_implication": "Reassure acute lunar patients of imminent recovery, while fortifying solar patients with patience.",
    },
]

# ---------------------------------------------------------------------------
# 10. Max Heindel Specific Evaluated Rules Registry
# ---------------------------------------------------------------------------

HEINDEL_RULES_REGISTRY: Dict[str, ClassicalMedicalRuleDefinition] = {
    "heindel_saturn_in_cancer": ClassicalMedicalRuleDefinition(
        id="heindel_saturn_in_cancer",
        name="Saturn in Cancer (Fall) - Stomach Dehydration & Reflex Kidney/Joint Impairment",
        name_tamil="கடகத்தில் சனி (நீச்ச ஆதிக்கம்) - இரைப்பை வறட்சி & சிறுநீரக/மூட்டு உபாதைகள்",
        source="Astro-Diagnosis: A Guide to Healing (Max Heindel)",
        chapter_verse="Chapter I & III: The Cardinal Vicious Circle",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Saturn in Cancer (4th zodiac sign)",
        mandatory_conditions=["Saturn occupies Cancer"],
        traditional_interpretation=(
            "Cancer rules the stomach, peristalsis, and blood serum. Saturn in Cancer (the sign of its fall) robs "
            "the corresponding organs of fluids, producing strange food likes and cravings for sweets/pastries. "
            "By reflex action through the Cardinal Vicious Circle, this digestive stagnation disturbs the kidneys (Libra) "
            "and stiffens the knee joints (Capricorn)."
        ),
        interpretation_tamil=(
            "கடகத்தில் சனி அமைவது இரைப்பையின் செரிமானத் திரவங்களை வற்றச் செய்து அஜீரணத்தை உண்டாக்குகிறது. "
            "இவர்கள் இனிப்பு மற்றும் மாவுப் பண்டங்களை அதிகம் விரும்புவர். சர ராசி வட்டப் பிணைப்பின் எதிரொலியாக இது துலாம் ராசி சிறுநீரகங்களையும், "
            "மகர ராசி முழங்கால் மூட்டுகளையும் பாதித்து விறைப்புத்தன்மையை ஏற்படுத்தும்."
        ),
        anatomical_system="Gastric Peristalsis, Blood Serum, Kidneys, and Knee Articulations",
        modifiers="Jupiter or Venus casting aspect on Cancer softens the digestive crystallization.",
        conflicting_indications="Moon well-placed in Taurus mitigates gastric fluid loss.",
        remedy_en="Cultivate frugal diet, strictly reduce refined sugars/pastries, and hydrate regularly.",
        remedy_ta="சுத்திகரிக்கப்பட்ட சர்க்கரை மற்றும் இனிப்புகளைத் தவிர்த்து, எளிய இயற்கை உணவுகளையும் போதிய நீரையும் பருக வேண்டும்.",
    ),
    "heindel_saturn_in_6th": ClassicalMedicalRuleDefinition(
        id="heindel_saturn_in_6th",
        name="Saturn in 6th House - Constitutional Lowering of Vitality & Lingering Complaints",
        name_tamil="6-ம் வீட்டில் சனி - பிராண சக்தி குறைவு & நாள்பட்ட மந்தமான உபாதைகள்",
        source="Astro-Diagnosis: A Guide to Healing (Max Heindel)",
        chapter_verse="Chapter VI & Aphorism 15",
        category="Vedic House Lord",
        system="vedic",
        required_placements="Saturn posited in the 6th House from Lagna",
        mandatory_conditions=["Saturn in 6th House"],
        traditional_interpretation=(
            "Saturn placed in the sixth house at birth persistently lowers constitutional vitality. "
            "Illnesses hang on obstinately and recuperation is slow, though Saturn confers a tenacious hold on life. "
            "Natives must stimulate peripheral circulation and avoid prolonged sedentary exposure."
        ),
        interpretation_tamil=(
            "பிறப்பு ஜாதகத்தில் 6-ம் பாவத்தில் சனி அமைவது உடலின் பிராண சக்தியை மட்டுப்படுத்துகிறது. "
            "நோய் எளிதில் விலகாமல் இழுத்தடிக்கும்; ஆனால் சனி உயிருக்கு நீண்ட ஆயுளையும் தருகிறார். உடலை கதகதப்பாக வைத்து இரத்த ஓட்டத்தைத் தூண்ட வேண்டும்."
        ),
        anatomical_system="Constitutional Immunity, Peripheral Circulation, Vagus Nerve",
        modifiers="Sun or Mars well-aspected elevates bodily heat and counteracts sluggishness.",
        conflicting_indications="Benefics in Lagna or 10th house grant resilience.",
        remedy_en="Daily brisk friction baths with rough gloves to stimulate circulation; warmth, sun, and active walks.",
        remedy_ta="குளியலின் போது கரடுமுரடான துணியால் உடலைத் தேய்த்து இரத்த ஓட்டத்தை அதிகரித்தல்; அதிகாலை நடைப்பயிற்சி.",
    ),
    "heindel_sun_in_6th": ClassicalMedicalRuleDefinition(
        id="heindel_sun_in_6th",
        name="Sun in 6th House - Obstruction of Solar Life-Fluid & Tendency to Prolonged Illness",
        name_tamil="6-ம் வீட்டில் சூரியன் - பிராண சக்தி ஓட்டத்தடை & நீண்ட நலிவுத்தன்மை",
        source="The Message of the Stars (Max Heindel)",
        chapter_verse="Chapter VIII: The Sun in the Twelve Houses",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Sun posited in the 6th House from Lagna",
        mandatory_conditions=["Sun in 6th House"],
        traditional_interpretation=(
            "As the Sun is the physical life-giver, its placement in the 6th house confines the solar vitality "
            "and obstructs the vital flow. Natives are particularly liable to frequent illnesses and slow recuperation. "
            "However, if the chart overcomes sickness, this position confers exceptional skill in chemistry, dietetics, and healing."
        ),
        interpretation_tamil=(
            "சூரியன் பிராண வாழ்வளிப்பவர் ஆவார். அவர் 6-ம் வீட்டில் அமையும் போது ஜீவ சக்தி மட்டுப்படுகிறது; நோய் வந்தால் குணமடைய "
            "நீண்ட காலம் எடுக்கும். ஆனால் இந்த அமைப்பை வென்றவர்கள் சிறந்த உணவுமுறை நிபுணர்களாகவும், வேதியியல் மற்றும் மருத்துவத் துறையில் வல்லுநர்களாகவும் விளங்குவர்."
        ),
        anatomical_system="Solar Vital Fluid, Spleen Specialized Ethers, Cellular Regeneration",
        modifiers="Sun trine Mars or Jupiter breaks the confinement and bestows radiant health.",
        conflicting_indications="Strong Lagna lord in Kendra neutralizes debility.",
        remedy_en="Daily Surya Namaskar at sunrise, pranayama, and light nourishing diet to assist splenic distribution.",
        remedy_ta="அதிகாலை சூரிய நமஸ்காரம், பிராணாயாமப் பயிற்சிகள் மற்றும் எளிய சத்தான உணவுகள்.",
    ),
    "heindel_sun_in_8th": ClassicalMedicalRuleDefinition(
        id="heindel_sun_in_8th",
        name="Sun in 8th House - Life-Giver in the House of Death-Dealing Forces",
        name_tamil="8-ம் வீட்டில் சூரியன் - ஆயுள் காரகன் மரண பாவத்தில் அமைதல்",
        source="The Message of the Stars (Max Heindel)",
        chapter_verse="Chapter VIII: The Sun in the Eighth House",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Sun in 8th House from Lagna",
        mandatory_conditions=["Sun in 8th House"],
        traditional_interpretation=(
            "The Eighth House is the angle through which death-dealing forces act; logically, the Lord of Life "
            "is out of place here and vitality is placed under severe testing. Hairbreadth escapes from crises are common. "
            "Conserving energy and living strictly in harmony with nature's laws is essential."
        ),
        interpretation_tamil=(
            "8-ம் பாவம் என்பது ஆயுள் போராட்டங்களை குறிக்கும் பாவமாகும். அங்கு ஜீவ காரகனான சூரியன் அமர்வது உடலின் "
            "உயிர் சக்தியை சோதனைகளுக்கு உள்ளாக்குகிறது. பல இக்கட்டான சூழல்களில் இருந்து தப்பிக்கும் யோகம் இருந்தாலும், பிராண சக்தியை வீணாக்காமல் காக்க வேண்டும்."
        ),
        anatomical_system="Core Vital Reserve, Autonomic Homeostasis, Excretory Axis",
        modifiers="Benefic aspects from Jupiter or Venus mitigate constitutional hazards.",
        conflicting_indications="Lagna lord exalted in Kendra.",
        remedy_en="Cultivate tranquil living, avoid rash hazards, chant Aditya Hridaya Stotram daily.",
        remedy_ta="ஆதித்ய ஹிருதய ஸ்தோத்திரம் பாராயணம் செய்தல்; தேவையற்ற அலைச்சல்களையும் பதற்றத்தையும் தவிர்த்தல்.",
    ),
    "heindel_sun_mars_fiery_fever": ClassicalMedicalRuleDefinition(
        id="heindel_sun_mars_fiery_fever",
        name="Sun-Mars Conjunction or Fiery Accentuation - High Fevers & Inflammatory Endurance",
        name_tamil="சூரியன்-செவ்வாய் சேர்க்கை / நெருப்பு ராசி ஆதிக்கம் - அதீத உஷ்ணக் காய்ச்சல் & எதிர்ப்புத்திறன்",
        source="Astro-Diagnosis: A Guide to Healing (Max Heindel)",
        chapter_verse="Chapter I & Aphorism 25",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Sun and Mars conjoined, or Mars in Aries/Leo with Sun",
        mandatory_conditions=["Sun and Mars conjoined or mutual aspect in Fire signs"],
        traditional_interpretation=(
            "Sun and Mars combined in fire signs produce super-abundance of vital energy. Blood races through veins "
            "like liquid fire. In illness, temperatures rise 3 to 4 degrees higher than in other people, yet the native "
            "possesses astonishing stamina to survive fevers that would prove fatal to others."
        ),
        interpretation_tamil=(
            "சூரியனும் செவ்வாயும் இணைவது இரத்த நாளங்களில் திரவ நெருப்பு போல் பிராணனைப் பாய்ச்சுகிறது. "
            "காய்ச்சல் வந்தால் உடல் வெப்பநிலை மற்றவர்களை விட 3-4 டிகிரி அதிகமாக ஏறும்; ஆனால் அதே சமயம் அதீத உஷ்ணத்தைத் தாங்கி உயிர் பிழைக்கும் அசாத்திய உடல் பலமும் இவர்களுக்கு உண்டு."
        ),
        anatomical_system="Hemoglobin, Arterial Pressure, Thermoregulation, Motor Cortex",
        modifiers="Saturn aspect cools the blood and prevents dangerous vascular pressure.",
        conflicting_indications="Moon or Venus aspecting introduces soothing lymphatic moisture.",
        remedy_en="Copper-charged water, cooling coconut water, avoiding red meat and pungent spices.",
        remedy_ta="வெட்டிவேர் மற்றும் சீரக நீர், இளநீர் பருகுதல்; காரம் மற்றும் அதிக உஷ்ண உணவுகளைத் தவிர்த்தல்.",
    ),
    "heindel_mercury_saturn_melancholy": ClassicalMedicalRuleDefinition(
        id="heindel_mercury_saturn_melancholy",
        name="Mercury Afflicted by Saturn - Nervous Melancholy & Chronic Pessimism",
        name_tamil="புதன்-சனி பாதிப்பு - நரம்புத் தளர்ச்சி, மனச்சோர்வு & அவநம்பிக்கை",
        source="Astro-Diagnosis: A Guide to Healing (Max Heindel)",
        chapter_verse="Chapter V & Aphorism 39",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Mercury conjunct, square, or opposite Saturn",
        mandatory_conditions=["Mercury afflicted by Saturn"],
        traditional_interpretation=(
            "Mercury rules the intellect and sensory nerves; Saturn contracts and binds. When Mercury is afflicted "
            "by Saturn, the native suffers from a stubborn, slow mind subject to melancholia and morbid worry. "
            "The environment should be sunny with rose-colored walls, cheerful music, and warm companionship."
        ),
        interpretation_tamil=(
            "புதன் நரம்புகளையும் அறிவையும் ஆள்கிறார்; சனி சுருக்கத்தையும் மந்தத்தையும் தருகிறார். இவ்விரு கிரகங்களின் "
            "முரண்பாடு தீவிர மனச்சோர்வு, அவநம்பிக்கை மற்றும் நரம்பு சோர்வை உண்டாக்கும். நோயாளிக்கு வெளிச்சமும், ரோஸ் நிற சுவர்களும், மகிழ்ச்சியான சூழலும் மிக அவசியம்."
        ),
        anatomical_system="Central Nervous System, Sensory Nerves, Mental Synaptic Motility",
        modifiers="Jupiter trine Mercury dispels gloom with philosophical optimism.",
        conflicting_indications="Moon well placed in cancer or Taurus with Venus.",
        remedy_en="Rose chromotherapy, joyful social companionship, listening to rhythmic uplifting music.",
        remedy_ta="ரோஸ் நிற ஒளி சிகிச்சை, நேர்மறை சிந்தனையாளர்களின் நட்பு, இனிமையான சங்கீதம் கேட்டல்.",
    ),
    "heindel_mercury_neptune_psychic": ClassicalMedicalRuleDefinition(
        id="heindel_mercury_neptune_psychic",
        name="Mercury or Moon Afflicted by Neptune - Sensory Delusions & Drug/Psychic Hypersensitivity",
        name_tamil="புதன் அல்லது சந்திரன் மீது நெப்டியூன் பாதிப்பு - நரம்பு மாயைகள் & போதை/மருந்து உணர்திறன்",
        source="Astro-Diagnosis: A Guide to Healing (Max Heindel)",
        chapter_verse="Chapter V: The Mentality",
        category="Vedic Conjunction/Aspect",
        system="vedic",
        required_placements="Mercury or Moon afflicted by Neptune (conjunction, square, or opposition)",
        mandatory_conditions=["Mercury or Moon afflicted by Neptune"],
        traditional_interpretation=(
            "Neptune is the higher octave of Mercury. Afflictions between Mercury or Moon and Neptune loosen the connection "
            "between the physical and vital bodies, producing extreme hypersensitivity, psychic impressions, nightmare delusions, "
            "and dangerous susceptibility to alcohol, narcotics, and ungrounded mediumship."
        ),
        interpretation_tamil=(
            "நெப்டியூன் புதனின் உயர் அதிர்வெண் ஆகும். சந்திரன் அல்லது புதன் நெப்டியூனால் பாதிக்கப்படும் போது ஸ்தூல உடலுக்கும் "
            "பிராண உடலுக்குமான பிணைப்பு தளர்வடைகிறது. இதனால் அதீத மாயைகள், தூக்கமின்மை, போதைப் பொருட்கள் மற்றும் மயக்க மருந்துகளால் விரைவாகப் பாதிக்கப்படும் தன்மை உண்டாகிறது."
        ),
        anatomical_system="Pineal Gland, Cerebrospinal Fluid, Higher Cognitive Aura",
        modifiers="Saturn trine brings grounding and firm mental crystallization.",
        conflicting_indications="Sun strong in Leo restores robust objective consciousness.",
        remedy_en="Strict avoidance of alcohol, sedatives, and seances; practice grounded outdoor physical labor.",
        remedy_ta="மது மற்றும் போதை மருந்துகளை அறவே தவிர்த்தல்; பூமி தொடர்பு கொண்ட எளிய உடல் உழைப்பு மற்றும் தியானம்.",
    ),
    "heindel_venus_scorpio_fall": ClassicalMedicalRuleDefinition(
        id="heindel_venus_scorpio_fall",
        name="Venus in Scorpio - Generative Vitality Sapping & Sensual Thermal Strain",
        name_tamil="விருச்சிகத்தில் சுக்கிரன் - பிறப்புறுப்பு நலிவு & உணர்ச்சிவசப்பட்ட பிராண விரயம்",
        source="The Message of the Stars (Max Heindel)",
        chapter_verse="Chapter IX: Venus in the Twelve Signs",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Venus in Scorpio (8th zodiac sign)",
        mandatory_conditions=["Venus occupies Scorpio"],
        traditional_interpretation=(
            "Scorpio rules the genitals and generative fire; Venus placed here is in her detriment/fall. "
            "The tender love-ray blends with martial passion, creating intense emotional desire that can sap "
            "constitutional vitality. Strictly conserving the generative life force is essential for long-term health."
        ),
        interpretation_tamil=(
            "சுக்கிரன் விருச்சிகத்தில் அமர்வது அவரது பகை/நீச்ச நிலையாகும். இது காம உணர்வுகளையும் உணர்ச்சி அலைகளையும் தூண்டி, "
            "உடலின் உயிர் அணுக்களையும் பிறப்புறுப்பு திசுக்களையும் பலவீனப்படுத்தக்கூடும். ஆன்ம ஒழுக்கமும் உணவுப் பழக்கமும் ஆரோக்கியத்திற்கு இன்றியமையாதது."
        ),
        anatomical_system="Generative Organs, Prostate, Ovaries, Venous Pelvic Plexus",
        modifiers="Jupiter aspect elevates passion into profound spiritual devotion and artistic sublimity.",
        conflicting_indications="Venus in own Nakshatra or conjunct Jupiter.",
        remedy_en="Practice sensory self-mastery, sublimate creative energies into fine arts and selfless devotion.",
        remedy_ta="சுய ஒழுக்கம், கலைகள் மற்றும் ஆன்மீக பக்தி வழியே உணர்ச்சி வேகங்களை நல்வழிப்படுத்துதல்.",
    ),
    "heindel_saturn_gemini_sagittarius_lungs": ClassicalMedicalRuleDefinition(
        id="heindel_saturn_gemini_sagittarius_lungs",
        name="Saturn in Gemini or Sagittarius Afflicting Sun - Pulmonary Vulnerability & Tubercular Tendency",
        name_tamil="மிதுனம் அல்லது தனுசில் சனி - நுரையீரல் பலவீனம் & சளி, காசநோய் பாதிப்பு",
        source="The Message of the Stars (Max Heindel)",
        chapter_verse="Chapter VIII: The Sun in Aspect with Other Planets",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Saturn in Gemini or Sagittarius afflicting the Sun",
        mandatory_conditions=["Saturn in Gemini or Sagittarius and aspecting Sun"],
        traditional_interpretation=(
            "Where constitutional resistance is fundamentally low, Saturn in Gemini or Sagittarius afflicting the Sun "
            "restricts the lung capillaries and limits blood oxygenation, creating chronic bronchial weakness and tubercular tendencies. "
            "Recuperation is prolonged."
        ),
        interpretation_tamil=(
            "மிதுனம் அல்லது தனுசில் சனி அமர்ந்து சூரியனைப் பாதிக்கும் போது நுரையீரல் நுண்குழாய்கள் சுருங்கி இரத்தத்தில் "
            "பிராணவாயு கலப்பது தடைபடுகிறது. இதனால் நாள்பட்ட இருமல், ஆஸ்துமா, மூச்சுக்குழாய் அழற்சி மற்றும் நுரையீரல் பலவீனம் தோன்றலாம்."
        ),
        anatomical_system="Lungs, Bronchial Capillaries, Thoracic Expansion, Oxygenation",
        modifiers="Jupiter aspect supports arterial circulation and fibrin homeostasis.",
        conflicting_indications="Mars well-aspected in fire signs maintains lung heat.",
        remedy_en="Sunlight air baths, steam inhalation with eucalyptus, rhythmic pranayama, avoiding damp lodgings.",
        remedy_ta="சூரிய ஒளி படும் தூய காற்று அறையில் வசிப்பது; துளசி மற்றும் யூகலிப்டஸ் மூலிகை ஆவி பிடித்தல்.",
    ),
    "heindel_mercury_12th_hearing": ClassicalMedicalRuleDefinition(
        id="heindel_mercury_12th_hearing",
        name="Mercury in 12th House or Capricorn Afflicted - Auditory Nerve Sensitivity",
        name_tamil="12-ம் வீட்டில் அல்லது மகரத்தில் புதன் பாதிப்பு - செவிப்புலன் நரம்பு பலவீனம்",
        source="Astro-Diagnosis: A Guide to Healing (Max Heindel)",
        chapter_verse="Aphorism 34",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Mercury in 12th House or in Capricorn afflicted by malefic",
        mandatory_conditions=["Mercury in 12th House or in Capricorn with malefic aspect"],
        traditional_interpretation=(
            "Mercury rules the auditory perception and vocal nerves. When situated in the 12th house (confinement) "
            "or in Capricorn (Saturn's sign) and afflicted by malefics, the delicate auditory nerves become impaired, "
            "predisposing to hearing loss or auditory hypersensitivity."
        ),
        interpretation_tamil=(
            "புதன் கேட்டல் உணர்வையும் செவி நரம்புகளையும் ஆள்கிறார். அவர் 12-ம் வீட்டில் அல்லது மகரத்தில் அசுபர்களால் "
            "பாதிக்கப்படும் போது காது கேளாமை, காதில் ரீங்கார சத்தம் அல்லது நரம்பு பலவீனம் ஏற்பட வாய்ப்புள்ளது."
        ),
        anatomical_system="Auditory Nerves, Tympanic Membrane, Eustachian Tube",
        modifiers="Jupiter conjunction or trine protects sensory nerve conductivity.",
        conflicting_indications="Mercury exalted or well placed with Venus.",
        remedy_en="Karna Poorana (warm herbal oil drops in ear under guidance), avoiding blaring acoustic noise.",
        remedy_ta="அதிக இரைச்சல் மற்றும் சத்தங்களைத் தவிர்த்தல்; தகுந்த மருத்துவர் ஆலோசனையுடன் காது பராமரிப்பு.",
    ),
    "heindel_common_signs_angular_vitality": ClassicalMedicalRuleDefinition(
        id="heindel_common_signs_angular_vitality",
        name="Common Signs on the Four Angles - Wavering Willpower & Chronic Relapse Vulnerability",
        name_tamil="நான்கு கேந்திரங்களில் உபய ராசிகள் - பலவீனமான மன உறுதி & நோய் மீள்தன்மை",
        source="Astro-Diagnosis: A Guide to Healing (Max Heindel)",
        chapter_verse="Chapter VII & Aphorism 23",
        category="Vedic Birth Chart",
        system="vedic",
        required_placements="Common signs (Gemini, Virgo, Sagittarius, Pisces) on the 4 angles (1, 4, 7, 10)",
        mandatory_conditions=["Ascendant is Gemini, Virgo, Sagittarius, or Pisces"],
        traditional_interpretation=(
            "When common signs occupy all four angles, the native's willpower tends to fluctuate. While receptive "
            "and eager to cooperate, they easily succumb to adverse suggestions from friends. The healer must "
            "repeat instructions frequently and provide an encouraging, firm atmosphere to prevent chronic invalidism."
        ),
        interpretation_tamil=(
            "லக்னம் உள்ளிட்ட நான்கு கேந்திரங்களிலும் உபய ராசிகள் அமைந்தால் மன உறுதி எளிதில் அலைபாயும். "
            "பிறரின் எதிர்மறைப் பேச்சுகளால் நோயின் பயம் அதிகரிக்கும். தொடர்ந்து ஊக்கமளிக்கும் சூழலும் ஆலோசனைகளும் இவர்களுக்கு தேவை."
        ),
        anatomical_system="Psychosomatic Willpower, Neuro-Immune Axis, Resilient Recovery",
        modifiers="Sun or Mars in fixed signs stiffens willpower and bolsters stamina.",
        conflicting_indications="Strong Saturn in 10th house confers steady discipline.",
        remedy_en="Shield the patient from gloomy visitors; provide clear, daily structured lifestyle routines.",
        remedy_ta="நோயாளியிடம் நோய் பற்றிப் பேசும் மனிதர்களைத் தவிர்ப்பது; தினசரி ஒழுங்கான நல்வாழ்வு அட்டவணை.",
    ),
    "heindel_fixed_signs_angles_resilience": ClassicalMedicalRuleDefinition(
        id="heindel_fixed_signs_angles_resilience",
        name="Fixed Signs on the Four Angles - Formidable Stamina & Disease Resistance",
        name_tamil="நான்கு கேந்திரங்களில் ஸ்திர ராசிகள் - அசாத்திய மன உறுதி & நோய் எதிர்ப்பு பலம்",
        source="Astro-Diagnosis: A Guide to Healing (Max Heindel)",
        chapter_verse="Chapter VII & The Message of the Stars",
        category="Vedic Mitigation",
        system="vedic",
        required_placements="Fixed signs (Taurus, Leo, Scorpio, Aquarius) on the 4 angles (1, 4, 7, 10)",
        mandatory_conditions=["Ascendant is Taurus, Leo, Scorpio, or Aquarius"],
        traditional_interpretation=(
            "When fixed signs occupy the angles, the native possesses iron determination and tremendous stamina. "
            "Though they may be slow to adapt and hold tenaciously to habits, once aroused they cooperate fully "
            "with the healer and achieve success over lingering afflictions."
        ),
        interpretation_tamil=(
            "கேந்திரங்களில் ஸ்திர ராசிகள் அமைவது இரும்பு போன்ற மன உறுதியையும் உடலின் அசாத்திய தாங்குதிறனையும் தரும். "
            "பழக்கவழக்கங்களில் பிடிவாதம் இருந்தாலும், இவர்கள் நோயை எதிர்த்துப் போராடி வெல்லும் மகத்தான ஆற்றல் கொண்டவர்கள்."
        ),
        anatomical_system="Skeletal Stamina, Immune Resilience, Dynamic Vital Core",
        modifiers="Afflicted Moon can make the fixity turn into stubborn fear of sickness.",
        conflicting_indications="Multiple planets in common signs soften the rigid tenacity.",
        remedy_en="Harness natural persistence towards constructive healing habits and physical exercise.",
        remedy_ta="இயற்கையான மன உறுதியைக் கொண்டு உடற்பயிற்சி மற்றும் நற்பழக்கங்களை உறுதியாகப் பின்பற்றுதல்.",
    ),
}
