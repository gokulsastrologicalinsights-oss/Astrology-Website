"""Destiny Matrix Calculation Engine.

Implements the 22 Major Arcana reduction method, octagram matrix vertex calculation,
karmic tails, life purpose breakdown, age timelines (0-80 years), and couples compatibility.
Clean-room implementation derived strictly from verified mathematical rules.
"""

from typing import Dict, List, Tuple, Any, Optional


# ------------------------------------------------------------------------------
# 1. Arcana Reducer
# ------------------------------------------------------------------------------

def reduce_arcana(val: int) -> int:
    """Destiny Matrix modulo-22 reduction.
    If val <= 22: returns val.
    If val > 22: sums digits repeatedly until <= 22.
    """
    if val <= 0:
        return 1
    while val > 22:
        val = sum(int(d) for d in str(val))
    return max(1, val)


# ------------------------------------------------------------------------------
# 2. Arcana Details Database (English and Tamil)
# ------------------------------------------------------------------------------

ARCANA_DETAILS: Dict[int, Dict[str, Any]] = {
    1: {
        "name_en": "The Magician (Creative Power & Manifestation)",
        "name_ta": "மந்திரவாதி (படைப்பாற்றல் & செயல் வலிமை)",
        "meaning_en": "Energy of pioneering ideas, active will, and boundless creative potential.",
        "meaning_ta": "புதிய சிந்தனைகள், வலுவான மன உறுதி மற்றும் அளப்பரிய படைப்புத்திறன் கொண்ட ஆற்றல்.",
        "positive_en": "Optimistic, independent, inventive, and capable of manifesting thoughts into reality.",
        "positive_ta": "நேர்மறை சிந்தனையாளர், சுதந்திரமானவர், புதியவற்றை உருவாக்கும் திறன் கொண்டவர்.",
        "negative_en": "Self-doubt, manipulation, arrogance, or procrastination.",
        "negative_ta": "சுய சந்தேகம், ஏமாற்றுதல், அகந்தை அல்லது காரியங்களை தள்ளிப்போடுதல்.",
        "recommendations_en": "Trust your initial impulses and build projects that empower others.",
        "recommendations_ta": "உங்கள் உள்ளுணர்வை நம்புங்கள், மற்றவர்களுக்கு பயனளிக்கும் திட்டங்களை முன்னெடுங்கள்.",
    },
    2: {
        "name_en": "The High Priestess (Intuition & Hidden Wisdom)",
        "name_ta": "உயர் குருதேவி (உள்ளுணர்வு & மறைஞானம்)",
        "meaning_en": "Energy of deep intuition, diplomacy, observation, and sacred mysteries.",
        "meaning_ta": "ஆழ்ந்த உள்ளுணர்வு, சமாதானப் போக்கு, கவனிக்கும் திறன் மற்றும் மறைஞான ஆற்றல்.",
        "positive_en": "Empathetic, discreet, natural psychologist, and keeper of confidences.",
        "positive_ta": "பிறர் மனதை உணர்பவர், ரகசியம் காப்பவர், சிறந்த ஆலோசகர்.",
        "negative_en": "Gossip, duplicity, passive-aggression, or emotional coldness.",
        "negative_ta": "புறம்பேசுதல், இரட்டை வேடம், உணர்வற்ற தன்மை.",
        "recommendations_en": "Cultivate your inner voice through silence and avoid spreading rumors.",
        "recommendations_ta": "மௌனத்தின் மூலம் உள்ளுணர்வை வளருங்கள், வதந்திகளைத் தவிருங்கள்.",
    },
    3: {
        "name_en": "The Empress (Fertility & Abundance)",
        "name_ta": "பேரரசி (செழிப்பு & தாய்மை)",
        "meaning_en": "Energy of beauty, maternity, worldly wealth, and sensory fulfillment.",
        "meaning_ta": "அழகு, தாய்மை, பொருள் செழிப்பு மற்றும் வசதியான வாழ்க்கை கொண்ட ஆற்றல்.",
        "positive_en": "Gracious, prosperous, artistic, hospitable, and nourishing to all endeavors.",
        "positive_ta": "அன்பானவர், வளமானவர், விருந்தோம்பல் மற்றும் கலையார்வம் மிக்கவர்.",
        "negative_en": "Controlling behavior, domestic tyranny, materialism, or neglect of health.",
        "negative_ta": "அதிகார ஆதிக்கம், பேராசை, குடும்பத்தில் அடக்குமுறை.",
        "recommendations_en": "Nurture life without smothering; manage finances with generosity.",
        "recommendations_ta": "அளவுக்கு மீறிய ஆதிக்கத்தை தவிர்த்து, பாசத்தோடு வழிநடத்துங்கள்.",
    },
    4: {
        "name_en": "The Emperor (Authority & Structure)",
        "name_ta": "பேரரசர் (அதிகாரம் & ஒழுங்கமைப்பு)",
        "meaning_en": "Energy of sovereignty, discipline, responsibility, and civic order.",
        "meaning_ta": "அதிகாரம், ஒழுக்கம், பொறுப்பு மற்றும் சமூகக் கட்டமைப்பு ஆற்றல்.",
        "positive_en": "Strong leader, organized executive, protective guardian, and just ruler.",
        "positive_ta": "வலிமையான தலைவர், நேர்மையான நிர்வாகி, அனைவரையும் பாதுகாப்பவர்.",
        "negative_en": "Despotism, anger issues, rigidity, or fear of losing control.",
        "negative_ta": "சர்வாதிகாரப் போக்கு, கோபம், நெகிழ்வற்ற குணம்.",
        "recommendations_en": "Lead with wisdom rather than force; empower your subordinates.",
        "recommendations_ta": "அதிகாரத்தை விட ஞானத்தால் வழிநடத்துங்கள், மற்றவர்களுக்கு வாய்ப்பளியுங்கள்.",
    },
    5: {
        "name_en": "The Hierophant (Wisdom, Tradition & Law)",
        "name_ta": "மதகுரு (ஞானம், பாரம்பரியம் & அறநெறி)",
        "meaning_en": "Energy of ethical guidance, spiritual truth, teaching, and heritage.",
        "meaning_ta": "அறநெறி வழிகாட்டல், ஆன்மீக உண்மை, கல்வி மற்றும் பாரம்பரியப் பெருமை.",
        "positive_en": "Revered teacher, moral counselor, seeker of knowledge, and family unifier.",
        "positive_ta": "மதிப்பிற்குரிய ஆசிரியர், நல்வழிகாட்டி, குடும்ப ஒற்றுமையை பேணுபவர்.",
        "negative_en": "Dogmatism, hypocrisy, excessive preaching, or rebellion against truth.",
        "negative_ta": "மூடநம்பிக்கை, போலித்தனம், மற்றவர்கள் மீது கருத்துக்களை திணிப்பது.",
        "recommendations_en": "Share wisdom freely and practice the principles you preach.",
        "recommendations_ta": "நீங்கள் போதிக்கும் நற்பண்புகளை உங்கள் வாழ்க்கையிலும் கடைபிடியுங்கள்.",
    },
    6: {
        "name_en": "The Lovers (Choice, Romance & Beauty)",
        "name_ta": "காதலர்கள் (தேர்வு, அன்பு & அழகுணர்வு)",
        "meaning_en": "Energy of unconditional love, aesthetics, partnership, and decisive values.",
        "meaning_ta": "நிபந்தனையற்ற அன்பு, கலையுணர்வு, கூட்டுறவு மற்றும் தெளிவான தெரிவு.",
        "positive_en": "Charming, diplomatic, affectionate, refined taste, and loyal friend.",
        "positive_ta": "வசீகரமானவர், அன்பானவர், உயர்ந்த ரசனை மற்றும் உண்மைத் தோழர்.",
        "negative_en": "Vanity, codependency, chronic doubt, or obsession with external praise.",
        "negative_ta": "வீண் ஆடம்பரம், பிறர் பாராட்டை எதிர்பார்ப்பது, முடிவெடுக்கத் தயங்குவது.",
        "recommendations_en": "Choose from your authentic heart rather than fear of rejection.",
        "recommendations_ta": "பயமின்றி உங்கள் மனசாட்சிக்கு உண்மையாய் நேர்மையான தேர்வை செய்யுங்கள்.",
    },
    7: {
        "name_en": "The Chariot (Victory, Motion & Direction)",
        "name_ta": "தேரோட்டி (வெற்றி, இயக்கம் & இலக்கு)",
        "meaning_en": "Energy of goal conquest, travel, mobility, and resolute focus.",
        "meaning_ta": "இலக்கு நோக்கிய பயணம், வெற்றி, பயணம் மற்றும் அசைக்க முடியாத உழைப்பு.",
        "positive_en": "Determined, courageous, inspiring team leader, and unstoppable achiever.",
        "positive_ta": "உறுதியானவர், தைரியமானவர், குழுவை வெற்றிகரமாக வழிநடத்துபவர்.",
        "negative_en": "Aggression, burnout, reckless driving, or stopping halfway.",
        "negative_ta": "ஆக்கிரமிப்பு குணம், அதிக சோர்வு, பாதியில் கைவிடுதல்.",
        "recommendations_en": "Define clear milestones and maintain inner balance while accelerating.",
        "recommendations_ta": "தெளிவான இலக்குகளை நிர்ணயித்து, நிதானத்தோடு வெற்றி பெறுங்கள்.",
    },
    8: {
        "name_en": "Justice (Balance, Truth & Cause-and-Effect)",
        "name_ta": "நீதி (சமநிலை, உண்மை & கர்ம விதி)",
        "meaning_en": "Energy of karmic justice, objective truth, law, and balance.",
        "meaning_ta": "கர்ம நியாயம், பாரபட்சமற்ற உண்மை, சட்டம் மற்றும் சமநிலை ஆற்றல்.",
        "positive_en": "Impartial, clear-sighted, honorable, rational, and accountable.",
        "positive_ta": "நடுநிலையானவர், நேர்மையானவர், சட்டத்திற்கு மதிப்பளிப்பவர்.",
        "negative_en": "Blaming others, victimization, resentment, or legal disputes.",
        "negative_ta": "மற்றவர்கள் மீது பழிபோடுதல், விரக்தி, வழக்குகளில் சிக்குதல்.",
        "recommendations_en": "Recognize that external reality mirrors your internal choices.",
        "recommendations_ta": "உங்கள் செயல்களே உங்கள் விதியை நிர்ணயிக்கின்றன என்பதை உணருங்கள்.",
    },
    9: {
        "name_en": "The Hermit (Wisdom, Solitude & Deep Knowledge)",
        "name_ta": "ஞானி (அறிவு, தனிமை & ஆழ்ந்த தத்துவம்)",
        "meaning_en": "Energy of deep intellect, spiritual depth, contemplation, and counsel.",
        "meaning_ta": "ஆழ்ந்த சிந்தனை, தத்துவ ஆராய்ச்சி, தனிமை மற்றும் வழிகாட்டல் ஆற்றல்.",
        "positive_en": "Wise mentor, profound researcher, peaceful soul, and ascetic clarity.",
        "positive_ta": "ஞான வழிகாட்டி, சிறந்த ஆய்வாளர், அமைதியை விரும்புபவர்.",
        "negative_en": "Depressive isolation, intellectual snobbery, or fear of love.",
        "negative_ta": "தனிமைச் சிறை, தலைக்கனம், பாசத்தை வெளிப்படுத்தத் தயங்குவது.",
        "recommendations_en": "Share your distilled wisdom with the world; do not hide in total retreat.",
        "recommendations_ta": "உங்கள் அறிவை உலகிற்கு வழங்குங்கள், முற்றிலும் தனிமையில் ஒதுங்காதீர்கள்.",
    },
    10: {
        "name_en": "Wheel of Fortune (Destiny Flow, Cycles & Luck)",
        "name_ta": "விதி சக்கரம் (காலச் சுழற்சி & அதிர்ஷ்டம்)",
        "meaning_en": "Energy of serendipity, synchronicities, financial luck, and easy flow.",
        "meaning_ta": "தற்செயல் நன்மைகள், காலச் சுழற்சி, பணவரவு மற்றும் இயல்பான வெற்றி.",
        "positive_en": "Optimistic, adaptable, naturally blessed, and trusts cosmic timing.",
        "positive_ta": "அதிர்ஷ்டசாலி, காலத்தின் மாற்றத்திற்கு எளிதில் தகவமைப்பவர்.",
        "negative_en": "Passive laziness, fatalism, gambling addictions, or anxiety about cycles.",
        "negative_ta": "சோம்பல், விதியை நொந்து கொள்வது, சூதாட்டம் அல்லது வீண் கவலை.",
        "recommendations_en": "Flow with the current without surrendering your conscious rudder.",
        "recommendations_ta": "காலத்தின் ஓட்டத்தோடு ஒத்துழைத்து, விவேகமாக வாய்ப்புகளைப் பயன்படுத்துங்கள்.",
    },
    11: {
        "name_en": "Strength (Vitality, Resilience & Compassionate Power)",
        "name_ta": "வலிமை (உடல்திறன், சகிப்புத்தன்மை & அன்பு சக்தி)",
        "meaning_en": "Energy of stamina, animal magnetism, athletic vigor, and gentle strength.",
        "meaning_ta": "உடல்திறன், ஆரோக்கியம், அசாத்திய தைரியம் மற்றும் அன்பால் வெல்லும் ஆற்றல்.",
        "positive_en": "Tireless worker, charismatic defender, courageous, and athletic.",
        "positive_ta": "சளைக்காமல் உழைப்பவர், மற்றவர்களைக் காப்பவர், மன உறுதி கொண்டவர்.",
        "negative_en": "Tyranny, brute force, self-harm, or suppressing animal instincts.",
        "negative_ta": "அடக்குமுறை, அதிக முரட்டுத்தனம், கோபத்தை கட்டுப்படுத்த முடியாமை.",
        "recommendations_en": "Tame external conflicts with gentleness rather than confrontation.",
        "recommendations_ta": "வன்முறையன்றி பொறுமையாலும் அன்பினாலும் சவால்களை வெல்லுங்கள்.",
    },
    12: {
        "name_en": "The Hanged Man (Service, Empathy & Higher Perspective)",
        "name_ta": "தியாகி (சேவை, இரக்கம் & புதிய பார்வை)",
        "meaning_en": "Energy of selfless service, alternative views, artistic vision, and patience.",
        "meaning_ta": "தன்னலமற்ற சேவை, மாறுபட்ட கோணம், கருணை மற்றும் தியாக உணர்வு.",
        "positive_en": "Deeply compassionate, innovative thinker, altruistic, and intuitive.",
        "positive_ta": "கருணை உள்ளம், புதுமையான சிந்தனை, சமுதாய நலனில் அக்கறை கொண்டவர்.",
        "negative_en": "Victim complex, inability to say no, addictions, or prolonged paralysis.",
        "negative_ta": "சுயபரிதாபம், 'இல்லை' என்று சொல்ல முடியாமை, தவறான பழக்கங்கள்.",
        "recommendations_en": "Serve others without sacrificing your own self-respect and boundaries.",
        "recommendations_ta": "உங்கள் சுயமரியாதையை இழக்காமல் மற்றவர்களுக்கு ஆதரவளியுங்கள்.",
    },
    13: {
        "name_en": "Transformation / Rebirth (Release of the Old)",
        "name_ta": "மறுபிறப்பு (மாற்றம் & புதிய தொடக்கம்)",
        "meaning_en": "Energy of radical renewal, shedding outdated patterns, and fearless change.",
        "meaning_ta": "பழையதை கைவிட்டு புதிய மறுமலர்ச்சி பெறும் ஆற்றல்.",
        "positive_en": "Fearless reformer, capable of dramatic personal rebirth, decisive.",
        "positive_ta": "தைரியமான சீர்திருத்தவாதி, கடின சூழ்நிலைகளிலிருந்து மீண்டும் எழுபவர்.",
        "negative_en": "Clinging to the past, destructive nihilism, or imposing chaos.",
        "negative_ta": "கடந்த காலத்தை மறக்க முடியாமை, அழிவுப் போக்கு, வீண் குழப்பம்.",
        "recommendations_en": "Release dead weight gracefully to welcome new blessings.",
        "recommendations_ta": "பயனற்ற பழைய எண்ணங்களை உதறிவிட்டு புதிய தொடக்கத்தை வரவேற்கவும்.",
    },
    14: {
        "name_en": "Temperance (Harmony, Art & Moderation)",
        "name_ta": "சமரச தேவதை (கலை, மிதவாதம் & மன அமைதி)",
        "meaning_en": "Energy of balance, fine art, emotional healing, and gentle synthesis.",
        "meaning_ta": "சமநிலை, நுண்கலை, மன அமைதி மற்றும் ஆற்றுப்படுத்தும் ஆற்றல்.",
        "positive_en": "Patient, artistic, emotionally balanced, soothing presence, and moderate.",
        "positive_ta": "பொறுமையானவர், கலையார்வம் மிக்கவர், அனைவரோடும் இணங்கிச் செல்பவர்.",
        "negative_en": "Gluttony, impatience, mood swings, or total stagnation.",
        "negative_ta": "பொறுமையின்மை, கட்டுப்பாடற்ற பழக்கங்கள், மனநிலை ஊசலாட்டம்.",
        "recommendations_en": "Practice moderation in all things and connect with nature regularly.",
        "recommendations_ta": "அனைத்து விஷயங்களிலும் மிதமான தன்மையை கடைபிடித்து அமைதி பெறுங்கள்.",
    },
    15: {
        "name_en": "The Passion (Charisma, Temptation & Shadow Integration)",
        "name_ta": "வசீகரம் (செல்வாக்கு, நிழல் சக்தி & ஆளுமை)",
        "meaning_en": "Energy of magnetic attraction, wealth potential, humor, and psychological mastery.",
        "meaning_ta": "ஈர்க்கும் கவர்ச்சி, செல்வம் ஈட்டும் திறன், நகைச்சுவை மற்றும் ஆளுமை.",
        "positive_en": "Charismatic speaker, highly lucrative negotiator, insightful, and vibrant.",
        "positive_ta": "வசீகரப் பேச்சாளர், வியாபாரத்தில் திறமையானவர், உற்சாகமானவர்.",
        "negative_en": "Greed, substance abuse, sexual manipulation, or jealousy.",
        "negative_ta": "பேராசை, பொறாமை, தவறான ஆசைகளுக்கு அடிமையாதல்.",
        "recommendations_en": "Use your magnetism to liberate rather than manipulate.",
        "recommendations_ta": "உங்கள் செல்வாக்கை மற்றவர்களை நல்வழிப்படுத்த பயன்படுத்துங்கள்.",
    },
    16: {
        "name_en": "The Spiritual Awakening (Breakthrough & Rebuilding)",
        "name_ta": "ஆன்மீக விழிப்புணர்வு (புதிய கட்டமைப்பு & விடுதலை)",
        "meaning_en": "Energy of lightning breakthroughs, spiritual realization, and structural renewal.",
        "meaning_ta": "திடீர் விழிப்புணர்வு, ஆன்மீக மறுமலர்ச்சி மற்றும் புதிய கட்டமைப்பு.",
        "positive_en": "Spiritual catalyst, unshakeable resilience, master rebuilder.",
        "positive_ta": "எந்த பின்னடைவிலிருந்தும் மீண்டு வரும் அசாத்திய உறுதி கொண்டவர்.",
        "negative_en": "Ego collapse, sudden anger, emotional explosions, or trauma fixation.",
        "negative_ta": "அகந்தை முறிவு, திடீர் கோப வெடிப்பு, மன அழுத்தம்.",
        "recommendations_en": "Build your life on spiritual foundations that cannot be shattered.",
        "recommendations_ta": "அழியாத அறநெறிகள் மற்றும் ஆன்மீகத்தின் மீது உங்கள் வாழ்வை அமையுங்கள்.",
    },
    17: {
        "name_en": "The Star (Talent, Hope, Radiance & Inspiration)",
        "name_ta": "நட்சத்திரம் (திறமை, நம்பிக்கை & பிரகாசம்)",
        "meaning_en": "Energy of public recognition, artistic genius, fame, and optimism.",
        "meaning_ta": "புகழ், கலைத்திறன், நம்பிக்கை மற்றும் பிரகாசமான எதிர்காலம்.",
        "positive_en": "Inspiring, gifted, naturally recognized, optimistic, and generous.",
        "positive_ta": "அனைவராலும் அங்கீகரிக்கப்படுபவர், திறமையானவர், நம்பிக்கை தருபவர்.",
        "negative_en": "Star sickness, pride, ungrounded fantasy, or fear of obscurity.",
        "negative_ta": "தலைக்கனம், வீண் பகட்டு, யதார்த்தமற்ற கற்பனைகளில் வாழ்வது.",
        "recommendations_en": "Shine your light to illuminate the road for others, not just yourself.",
        "recommendations_ta": "உங்கள் புகழையும் திறமையையும் சமுதாய நலனுக்காக அர்ப்பணியுங்கள்.",
    },
    18: {
        "name_en": "The Moon (Subconscious, Mystery & Imagination)",
        "name_ta": "சந்திரன் (ஆழ்மனம், மர்மம் & கற்பனைத்திறன்)",
        "meaning_en": "Energy of vivid imagination, lucid dreams, esoteric depth, and psychic gifts.",
        "meaning_ta": "கற்பனை வளம், கனவுகள், ஆழ்மன உணர்வுகள் மற்றும் ஆன்மீக ரகசியங்கள்.",
        "positive_en": "Deeply intuitive, imaginative writer, magical creator, and sensitive.",
        "positive_ta": "உயர்ந்த கற்பனை வளம், எழுத்தாளர், உள்ளுணர்வு வழிகாட்டுதல் கொண்டவர்.",
        "negative_en": "Fears, phobias, living in illusions, deceit, or escapism.",
        "negative_ta": "வீண் பயங்கள், மாயை, ஏமாற்றங்கள் மற்றும் மனக்குழப்பம்.",
        "recommendations_en": "Ground your imaginative visions into concrete artistic expressions.",
        "recommendations_ta": "உங்கள் கற்பனைகளை கலை மற்றும் எழுத்து மூலம் நிஜமாக்குங்கள்.",
    },
    19: {
        "name_en": "The Sun (Prosperity, Leadership & Radiance)",
        "name_ta": "சூரியன் (செல்வாக்கு, மகிழ்ச்சி & பிரகாசம்)",
        "meaning_en": "Energy of warmth, joy, abundance, public acclaim, and noble generosity.",
        "meaning_ta": "மகிழ்ச்சி, ஒளி, செல்வம், பெருந்தன்மை மற்றும் சமூக மரியாதை.",
        "positive_en": "Warm, joyful, natural center of attraction, wealthy, and benevolent.",
        "positive_ta": "அன்பானவர், மகிழ்ச்சியானவர், அனைவரையும் அரவணைக்கும் வள்ளல்.",
        "negative_en": "Arrogance, scorching others with anger, narcissism, or exhaustion.",
        "negative_ta": "ஆணவம், சுயநலம், மற்றவர்களை எரிச்சலூட்டும் குணம்.",
        "recommendations_en": "Warm people like the morning sun; do not burn them with your ego.",
        "recommendations_ta": "சூரியனைப் போல அனைவருக்கும் நலம் பயக்கும் கருணையை வெளிப்படுத்துங்கள்.",
    },
    20: {
        "name_en": "The Annunciation (Ancestral Healing & Rebirth)",
        "name_ta": "குலமறுமலர்ச்சி (முன்னோர் ஆசி & ஆன்மீக விழிப்பு)",
        "meaning_en": "Energy of family lineage healing, ancestral wisdom, and fateful awakening.",
        "meaning_ta": "குடும்ப ஒற்றுமை, முன்னோர் ஆசி மற்றும் குல பெருமையை மீட்டெடுக்கும் ஆற்றல்.",
        "positive_en": "Unifies family branches, heals generational trauma, prophetic vision.",
        "positive_ta": "குடும்பத்தை இணைப்பவர், வம்சாவளி பெருமைகளை காப்பவர்.",
        "negative_en": "Condemning family members, holding generational grudges, or fear of change.",
        "negative_ta": "குடும்பத்தாரை பழித்தல், பரம்பரை பகை, அவநம்பிக்கை.",
        "recommendations_en": "Forgive ancestral shortcomings and establish a higher moral legacy.",
        "recommendations_ta": "குடும்ப முரண்பாடுகளை மன்னித்து பரஸ்பர அன்பை உருவாக்குங்கள்.",
    },
    21: {
        "name_en": "The World (Global Expansion, Peace & Synthesis)",
        "name_ta": "உலகம் (சர்வதேச விரிவு, அமைதி & முழுமை)",
        "meaning_en": "Energy of planetary citizenship, international success, peace, and diplomacy.",
        "meaning_ta": "சர்வதேச வெற்றி, உலக அமைதி, மொழியறிவு மற்றும் விரிவான பார்வை.",
        "positive_en": "Cosmopolitan, visionary diplomat, multilingual, unites cultures.",
        "positive_ta": "உலகளாவிய பார்வை கொண்டவர், பல கலாச்சாரங்களை இணைக்கும் பாலம்.",
        "negative_en": "Narrow xenophobia, hostility towards the world, or fear of expansion.",
        "negative_ta": "குறுகிய மனப்பான்மை, புதியவற்றை எதிர்க்கும் சுபாவம்.",
        "recommendations_en": "Expand your horizons globally; see all human beings as one family.",
        "recommendations_ta": "யாதும் ஊரே யாவரும் கேளிர் என்ற உயரிய உலகளாவிய பார்வையை கடைபிடியுங்கள்.",
    },
    22: {
        "name_en": "The Master / Freedom (Spiritual Liberation & Innocence)",
        "name_ta": "விடுதலை / பேரறிவு (ஆன்மீக சுதந்திரம் & தூய்மை)",
        "meaning_en": "Energy of absolute freedom, childlike wonder, trust, and untethered genius.",
        "meaning_ta": "முழுமையான சுதந்திரம், கபடற்ற மனம், ஆன்மீக தூய்மை மற்றும் ஞானம்.",
        "positive_en": "Free-spirited, boundary-breaker, joyful, spontaneous, and enlightened.",
        "positive_ta": "சுதந்திரப் பறவை, தடைகளை உடைப்பவர், ஆனந்தமாக வாழ்பவர்.",
        "negative_en": "Recklessness, irresponsibility, imprisonment (physical or mental), or chaos.",
        "negative_ta": "பொறுப்பற்ற தன்மை, சட்டதிட்டங்களை மீறுதல், வீண் விபரீதம்.",
        "recommendations_en": "Exercise freedom with awareness that every action bears fruit.",
        "recommendations_ta": "சுதந்திரத்தை விவேகத்துடனும் பொறுப்புணர்வுடனும் அனுபவியுங்கள்.",
    },
}


def get_arcana_info(arcana_num: int, node_id: str, label: str, lang: str = "en") -> Dict[str, Any]:
    """Format node detail dictionary with appropriate language."""
    data = ARCANA_DETAILS.get(arcana_num, ARCANA_DETAILS[1])
    is_ta = (lang == "ta")
    return {
        "node_id": node_id,
        "label": label,
        "arcana_number": arcana_num,
        "arcana_name": data["name_ta"] if is_ta else data["name_en"],
        "meaning": data["meaning_ta"] if is_ta else data["meaning_en"],
        "positive_traits": data["positive_ta"] if is_ta else data["positive_en"],
        "negative_traps": data["negative_ta"] if is_ta else data["negative_en"],
        "recommendations": data["recommendations_ta"] if is_ta else data["recommendations_en"],
    }


# ------------------------------------------------------------------------------
# 3. Main Matrix Calculation
# ------------------------------------------------------------------------------

def calculate_destiny_matrix(birth_date: str, lang: str = "en") -> Dict[str, Any]:
    """Calculate the complete 22-Arcana Destiny Matrix octagram."""
    parts = birth_date.strip().split("-")
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])

    # 1. Personal Square (Orthogonal)
    day_arcana = reduce_arcana(day)
    month_arcana = reduce_arcana(month)
    year_digits_sum = sum(int(d) for d in str(year))
    year_arcana = reduce_arcana(year_digits_sum)

    # Bottom (Karmic Tail Base)
    karmic_tail_base = reduce_arcana(day_arcana + month_arcana + year_arcana)

    # Center (Comfort Zone)
    comfort_zone = reduce_arcana(day_arcana + month_arcana + year_arcana + karmic_tail_base)

    # 2. Ancestral Square (Diagonal)
    father_spirit = reduce_arcana(day_arcana + month_arcana)
    mother_spirit = reduce_arcana(month_arcana + year_arcana)
    father_matter = reduce_arcana(day_arcana + karmic_tail_base)
    mother_matter = reduce_arcana(year_arcana + karmic_tail_base)

    # 3. Karmic Tail Triad
    k1 = karmic_tail_base
    k2 = reduce_arcana(comfort_zone + karmic_tail_base)
    k3 = reduce_arcana(k1 + k2)
    karmic_tail_triad = [k1, k2, k3]

    # 4. Lines & Junctions
    # Money & Love lines
    money_entrance = reduce_arcana(year_arcana + comfort_zone)
    love_entrance = reduce_arcana(karmic_tail_base + comfort_zone)
    love_money_balance = reduce_arcana(money_entrance + love_entrance)

    # 5. Purpose Calculations
    sky_line = month_arcana + karmic_tail_base
    earth_line = day_arcana + year_arcana
    personal_purpose = reduce_arcana(sky_line + earth_line)

    father_line = father_spirit + mother_matter
    mother_line = mother_spirit + father_matter
    social_purpose = reduce_arcana(father_line + mother_line)

    spiritual_purpose = reduce_arcana(personal_purpose + social_purpose)
    planetary_purpose = reduce_arcana(social_purpose + spiritual_purpose)

    # 6. Age Timeline (0 to 80 years)
    age_points_raw = [
        (0, day_arcana, "Birth & Early Childhood", "பிறப்பு & குழந்தைப்பருவம்"),
        (10, father_spirit, "Youth Exploration & Education", "இளமை & கல்விப்பருவம்"),
        (20, month_arcana, "Adulthood & Spiritual Awakenings", "இளம்பருவம் & ஆன்மீக நாட்டம்"),
        (30, mother_spirit, "Career Building & Partnerships", "தொழில் & குடும்ப வாழ்க்கை"),
        (40, year_arcana, "Midlife Mastery & Wealth Realization", "நடுத்தர வயது & செல்வச் சேர்க்கை"),
        (50, mother_matter, "Social Contribution & Mentorship", "சமூக சேவை & அனுபவ வழிகாட்டல்"),
        (60, karmic_tail_base, "Karmic Resolution & Spiritual Peace", "கர்ம வினைகள் அமைதி அடைதல்"),
        (70, father_matter, "Wisdom Maturation & Legacy", "முதுமை ஞானம் & வழித்தோன்றல்கள்"),
        (80, day_arcana, "Cycle Completion & Transcendent Peace", "வாழ்வின் முழுமை & மோட்ச அமைதி"),
    ]

    age_timeline = []
    is_ta = (lang == "ta")
    for age, arc, th_en, th_ta in age_points_raw:
        arc_info = ARCANA_DETAILS.get(arc, ARCANA_DETAILS[1])
        desc = (
            f"Arcana {arc}: {arc_info['name_en']}. Energy focuses on {arc_info['meaning_en']}"
            if not is_ta else
            f"ஆர்கானா {arc}: {arc_info['name_ta']}. இந்த வயதில் {arc_info['meaning_ta']}"
        )
        age_timeline.append({
            "age": age,
            "arcana_number": arc,
            "theme": th_ta if is_ta else th_en,
            "description": desc,
        })

    # 7. Formatted Node Objects
    labels = {
        "day": ("Personal Identity (Youth)", "சுய அடையாளம் (இளமை)"),
        "month": ("Spiritual Guidance & Inspiration", "ஆன்மீக வழிகாட்டுதல்"),
        "year": ("Material Realization & Finances", "பொருளாதார வளர்ச்சி"),
        "karmic_tail": ("Karmic Foundation (Past Life)", "கர்ம வேர் (முற்பிறவி கடன்)"),
        "comfort": ("Comfort Zone & Core Vibration", "மன அமைதி மண்டலம்"),
        "father_spirit": ("Father's Spiritual Lineage", "தந்தைவழி ஆன்மீக ஆற்றல்"),
        "mother_spirit": ("Mother's Spiritual Lineage", "தாய்வழி ஆன்மீக ஆற்றல்"),
        "father_matter": ("Father's Material Lineage", "தந்தைவழி பொருள் ஆற்றல்"),
        "mother_matter": ("Mother's Material Lineage", "தாய்வழி பொருள் ஆற்றல்"),
        "love": ("Relationship & Romantic Harmony", "காதல் & இல்லற நல்லுறவு"),
        "money": ("Wealth Flow & Financial Channels", "செல்வ வளம் & தொழில் வழிகள்"),
    }

    day_node = get_arcana_info(day_arcana, "day", labels["day"][1] if is_ta else labels["day"][0], lang)
    month_node = get_arcana_info(month_arcana, "month", labels["month"][1] if is_ta else labels["month"][0], lang)
    year_node = get_arcana_info(year_arcana, "year", labels["year"][1] if is_ta else labels["year"][0], lang)
    karmic_node = get_arcana_info(karmic_tail_base, "karmic_tail", labels["karmic_tail"][1] if is_ta else labels["karmic_tail"][0], lang)
    comfort_node = get_arcana_info(comfort_zone, "comfort", labels["comfort"][1] if is_ta else labels["comfort"][0], lang)

    fs_node = get_arcana_info(father_spirit, "father_spirit", labels["father_spirit"][1] if is_ta else labels["father_spirit"][0], lang)
    ms_node = get_arcana_info(mother_spirit, "mother_spirit", labels["mother_spirit"][1] if is_ta else labels["mother_spirit"][0], lang)
    fm_node = get_arcana_info(father_matter, "father_matter", labels["father_matter"][1] if is_ta else labels["father_matter"][0], lang)
    mm_node = get_arcana_info(mother_matter, "mother_matter", labels["mother_matter"][1] if is_ta else labels["mother_matter"][0], lang)

    love_node = get_arcana_info(love_entrance, "love_line", labels["love"][1] if is_ta else labels["love"][0], lang)
    money_node = get_arcana_info(money_entrance, "money_line", labels["money"][1] if is_ta else labels["money"][0], lang)

    # 8. Synthesized Insights
    strengths = [day_node["positive_traits"], comfort_node["positive_traits"]]
    challenges = [karmic_node["negative_traps"], day_node["negative_traps"]]
    careers = [
        f"Alters with Arcana {year_arcana} ({year_node['arcana_name']}) in money sector",
        f"Best suited in fields invoking {month_node['arcana_name']}",
    ]
    finances = [
        f"Money line opens via {money_node['arcana_name']}. Avoid greed and debt traps.",
        f"Karmic balance point is Arcana {love_money_balance}.",
    ]
    loves = [
        f"Love channel governed by {love_node['arcana_name']}.",
        "Harmonious relationships emerge when past life karmic patterns are consciously healed.",
    ]

    synthesis = (
        f"Your Destiny Matrix is anchored by Day Arcana {day_arcana} and Month Arcana {month_arcana}, "
        f"converging at the Soul Comfort Zone of Arcana {comfort_zone}. "
        f"Your Personal Purpose (Ages 20-40) is Arcana {personal_purpose}, transitioning to Social Purpose {social_purpose} (Ages 40-60). "
        f"By resolving the Karmic Tail triad ({k1}-{k2}-{k3}), you liberate your wealth and relationship potentials."
        if not is_ta else
        f"உங்கள் விதி அணி (Destiny Matrix) நாள் ஆர்கானா {day_arcana} மற்றும் மாத ஆர்கானா {month_arcana} ஆகியவற்றால் ஆளப்பட்டு, "
        f"மைய மன அமைதி மண்டலம் {comfort_zone}-ல் ஒருமுகப்படுகிறது. "
        f"உங்கள் தனிப்பட்ட நோக்கம் {personal_purpose}, சமூக நோக்கம் {social_purpose}. "
        f"கர்ம வால் எண்களை ({k1}-{k2}-{k3}) நல்ல செயல்களால் தீர்க்கும் போது முழுமையான வாழ்வில் வெற்றி கைகூடும்."
    )

    return {
        "day_arcana": day_node,
        "month_arcana": month_node,
        "year_arcana": year_node,
        "karmic_tail_base": karmic_node,
        "karmic_tail_triad": karmic_tail_triad,
        "comfort_zone": comfort_node,
        "father_spirit": fs_node,
        "mother_spirit": ms_node,
        "father_matter": fm_node,
        "mother_matter": mm_node,
        "love_line": love_node,
        "money_line": money_node,
        "purpose": {
            "personal_purpose": personal_purpose,
            "social_purpose": social_purpose,
            "spiritual_purpose": spiritual_purpose,
            "planetary_purpose": planetary_purpose,
        },
        "age_timeline": age_timeline,
        "strengths": strengths,
        "challenges": challenges,
        "career_tendencies": careers,
        "financial_tendencies": finances,
        "love_themes": loves,
        "overall_synthesis": synthesis,
    }


def calculate_compatibility(
    dob1: str, dob2: str, name1: str = "Partner 1", name2: str = "Partner 2", lang: str = "en"
) -> Dict[str, Any]:
    """Calculate couples compatibility by synthesizing two Destiny Matrices."""
    m1 = calculate_destiny_matrix(dob1, lang)
    m2 = calculate_destiny_matrix(dob2, lang)

    rel_purpose = reduce_arcana(m1["purpose"]["personal_purpose"] + m2["purpose"]["personal_purpose"])
    couple_karma = reduce_arcana(m1["karmic_tail_base"]["arcana_number"] + m2["karmic_tail_base"]["arcana_number"])
    shared_finance = reduce_arcana(m1["money_line"]["arcana_number"] + m2["money_line"]["arcana_number"])
    love_harmony = reduce_arcana(m1["love_line"]["arcana_number"] + m2["love_line"]["arcana_number"])

    is_ta = (lang == "ta")
    synth = (
        f"The union between {name1} and {name2} generates a Relationship Purpose of Arcana {rel_purpose}. "
        f"Their joint financial capacity resonates with Arcana {shared_finance}, while romantic harmony vibrates at Arcana {love_harmony}. "
        f"The primary karmic challenge to transcend together is Arcana {couple_karma}."
        if not is_ta else
        f"{name1} மற்றும் {name2} இடையேயான திருமணப் பந்தம் ஆர்கானா {rel_purpose} என்ற உயர்ந்த கூட்டு நோக்கத்தை உருவாக்குகிறது. "
        f"இருவரின் கூட்டு நிதி வளம் ஆர்கானா {shared_finance}, அன்புப் பிணைப்பு ஆர்கானா {love_harmony} ஆக விளங்குகிறது."
    )

    return {
        "person1_name": name1,
        "person2_name": name2,
        "relationship_purpose": rel_purpose,
        "couple_karmic_task": couple_karma,
        "shared_finance": shared_finance,
        "love_harmony": love_harmony,
        "compatibility_synthesis": synth,
    }
