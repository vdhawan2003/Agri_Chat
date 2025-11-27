import pandas as pd
import re
from rank_bm25 import BM25Okapi
from difflib import get_close_matches
from rapidfuzz import fuzz
from backend.gemini_api import generate_gemini_response

# =====================================
# 📂 Load CSV (ONLY data source)
# =====================================

def load_csv():
    try:
        df = pd.read_csv("backend/data/agriculture_facts.csv")
        return df.to_dict(orient="records")
    except Exception as e:
        print("CSV Load Error:", e)
        return []

agri_facts = load_csv()

# =====================================
# 🧹 Text Normalizer
# =====================================

def normalize_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

# =====================================
# 🧠 Build BM25 RAG Index (CSV only)
# =====================================

documents = []
tokenized_docs = []

for row in agri_facts:
    term = row.get("Term", "")
    definition = row.get("Definition", "")
    doc = f"{term}. {definition}"
    documents.append(doc)
    tokenized_docs.append(normalize_text(doc).split())

bm25 = BM25Okapi(tokenized_docs)


def fuzzy_match_csv_term(query_norm: str, min_score: int = 70):
    """
    Fuzzy match the WHOLE query against CSV 'Term' entries.
    - Uses RapidFuzz WRatio (tolerant to typos + word order)
    - Gives a small bonus to multi-word terms (like 'drip irrigation')
    """
    best_row = None
    best_score = 0

    for row in agri_facts:
        term_raw = row.get("Term", "") or ""
        term_norm = normalize_text(term_raw)

        if not term_norm:
            continue

        score = fuzz.WRatio(query_norm, term_norm)

        # Bonus to more specific, multi-word terms
        if len(term_norm.split()) > 1:
            score += 5

        if score > best_score:
            best_score = score
            best_row = row

    if best_row is None or best_score < min_score:
        return None

    return f"{best_row.get('Term')}. {best_row.get('Definition')}"



# =====================================
# 🔍 RAG Retriever
# =====================================
def retrieve_rag(query):
    query_norm = normalize_text(query)

    # Step 1: Clean query by removing language & question words
    query_norm = re.sub(
        r"(in hindi|in english|translate|explain|define|meaning of|what is|describe)",
        "",
        query_norm
    ).strip()

    if not query_norm:
        return None

    # ================================
    # STEP 2: Exact term match
    # ================================
    for row in agri_facts:
        term_norm = normalize_text(row.get("Term", ""))
        if term_norm == query_norm:
            return f"{row.get('Term')}. {row.get('Definition')}"

    # ================================
    # STEP 3: STRONG FUZZY TERM MATCH
    # (runs BEFORE partial substring)
    # ================================
    fuzzy_hit = fuzzy_match_csv_term(query_norm, min_score=65)
    if fuzzy_hit:
        return fuzzy_hit

    # ================================
    # STEP 4: Strong partial match 
    # (word boundary safe, pick LONGEST term)
    # ================================
    partial_candidates = []

    for row in agri_facts:
        term_norm = normalize_text(row.get("Term", ""))
        if not term_norm:
            continue

        # check if the whole term appears as a word sequence
        if re.search(rf"\b{re.escape(term_norm)}\b", query_norm):
            partial_candidates.append((len(term_norm.split()), row))

    if partial_candidates:
        # choose the most specific (longest) term
        _, best_row = max(partial_candidates, key=lambda x: x[0])
        return f"{best_row.get('Term')}. {best_row.get('Definition')}"

    # ================================
    # STEP 5: BM25 fallback only if strong
    # ================================
    tokens = query_norm.split()
    if not tokens:
        return None

    scores = bm25.get_scores(tokens)
    best_score = max(scores) if scores is not None else 0

    if best_score < 4.0:
        return None

    best_index = scores.tolist().index(best_score)
    return documents[best_index]

# =====================================
# 🌾 MEGA AGRICULTURE KEYWORDS
# =====================================

BASE_AGRI_KEYWORDS = [

    # Core agriculture & farming
    "agriculture", "agricultural", "farming", "farmer", "farm", "cultivation", 
    "agronomy", "horticulture", "floriculture", "sericulture", "apiculture",
    "harvest", "harvesting", "yield", "productivity", "cropping", "cropland",
    "plantation", "seedbed", "nursery", "sowing", "transplanting",

    # Soil science
    "soil", "topsoil", "subsoil", "soil fertility", "soil erosion", "soil health",
    "soil texture", "soil structure", "soil profile", "soil horizon",
    "soil pH", "humus", "organic matter", "salinity", "alkalinity",
    "compaction", "soil microbes", "rhizobacteria", "mycorrhiza",
    "soil testing", "nutrient deficiency", "micronutrients", "macronutrients",

    # Water & irrigation
    "irrigation", "drip irrigation", "sprinkler irrigation", "micro irrigation",
    "flood irrigation", "canal irrigation", "furrow irrigation",
    "rainwater harvesting", "watershed management",
    "groundwater", "water table", "soil moisture",
    "water conservation", "evapotranspiration", "waterlogging", "drainage",

    # Crops & plant types
    "crop", "crops", "cereal", "millet", "rice", "wheat", "maize", "corn",
    "barley", "sorghum", "pulses", "lentil", "gram", "chickpea",
    "bean", "soybean", "groundnut", "oilseed", "mustard", "sunflower", "sesame",
    "cotton", "jute", "sugarcane", "tea", "coffee",
    "vegetable", "fruit", "horticulture crops",
    "tomato", "potato", "onion", "garlic", "chili", "banana", "mango",
    "apple", "papaya", "grapes",

    # Fertilizers & nutrients
    "fertilizer", "fertilizers", "organic fertilizer", "chemical fertilizer",
    "manure", "farmyard manure", "cow dung", "compost", "vermicompost",
    "green manure", "biofertilizer", "npk", "nitrogen", "phosphorus", "potassium",
    "urea", "dap", "single super phosphate", "micronutrient mixture",

    # Pests, diseases & protection
    "pest", "pesticide", "insecticide", "fungicide", "herbicide", "weedicide",
    "crop disease", "plant disease",
    "aphid", "bollworm", "armyworm", "whitefly", "thrips", "mealybug",
    "mites", "nematode", "rodent",
    "integrated pest management", "ipm", "biological control", "biopesticide",

    # Sustainable & organic farming
    "organic farming", "natural farming", "sustainable agriculture",
    "permaculture", "agroforestry", "regenerative agriculture",
    "cover crops", "intercropping", "mixed cropping", "strip cropping",
    "crop rotation", "no till farming", "mulching", "companion planting",
    "zbnf", "zero budget natural farming",

    # Livestock & allied sectors
    "livestock", "cattle", "cow", "buffalo", "goat", "sheep", "pig",
    "poultry", "chicken", "duck", "dairy farming",
    "fishery", "fisheries", "aquaculture", "shrimp farming",
    "fodder", "pasture", "grazing",

    # Climate & weather
    "climate", "climate change", "rainfall", "drought", "flood",
    "heat wave", "cold wave", "storm", "cyclone", "monsoon",
    "temperature", "humidity", "carbon sequestration",
    "greenhouse gas", "global warming",

    # Agricultural technology
    "precision agriculture", "precision farming", "smart farming",
    "digital farming", "agritech", "agri iot", "iot",
    "sensor", "satellite", "remote sensing",
    "drone", "drone farming", "gps", "gis",
    "solar pump", "solar irrigation", "solar farming",

    # Economics, policy & schemes
    "mandi", "wholesale market",
    "msp", "minimum support price",
    "subsidy", "farm subsidy",
    "loan", "kisan credit card",
    "crop insurance", "pmfb y", "pmfby",
    "pm kisan", "soil health card",
    "fpo", "farmer producer organization",
    "agri export", "cold storage",
    "warehouse", "food processing"
]

# ✅ Massive auto-keyword expansion from CSV
AUTO_KEYWORDS = set()

for row in agri_facts:
    term = str(row.get("Term", "")).lower()
    if term:
        AUTO_KEYWORDS.add(term)
        words = term.split()
        for w in words:
            AUTO_KEYWORDS.add(w)
        # also add bigrams
        for i in range(len(words)-1):
            AUTO_KEYWORDS.add(f"{words[i]} {words[i+1]}")

AGRI_KEYWORDS = set(BASE_AGRI_KEYWORDS) | AUTO_KEYWORDS

def is_agriculture_related(query):
    q = query.lower()
    return any(word in q for word in AGRI_KEYWORDS)

# =====================================
# 🌍 Multilingual Greetings / Farewells
# =====================================

GREETINGS = [
    "hi","hello","hey","namaste","नमस्ते","नमस्कार","ಹಲೋ","வணக்கம்","నమస్తే",
    "hola","bonjour","hallo","مرحبا","こんにちは","你好","안녕하세요"
]

FAREWELLS = [
    "bye","goodbye","see you","take care","adios","au revoir",
    "अलविदा","खुदा हाफिज","再见","さようなら","안녕"
]

LANGUAGES = [
    "english","hindi","marathi","tamil","telugu","kannada","bengali",
    "gujarati","urdu","french","spanish","german","arabic",
    "japanese","korean","chinese"
]


def extract_point_count(text: str) -> int:
    match = re.search(r"(\d+)\s*point", text)
    if match:
        return int(match.group(1))
    return 10  # default

# =====================================
# 🧠 MAIN CHAT FUNCTION
# =====================================
def chat_response(user_query: str) -> str:
    q = user_query.lower()
    point_count = extract_point_count(q)

    # ===== 1. Greetings =====
    if any(re.search(rf"\b{re.escape(g)}\b", q) for g in GREETINGS):
        return "🌿 Hello! I am AgriChat Buddy. Ask me anything about agriculture."

    # ===== 2. Farewells =====
    if any(re.search(rf"\b{re.escape(f)}\b", q) for f in FAREWELLS):
        return "👋 Goodbye! Wishing you healthy harvests 🌾"

    # ===== 3. Language detection =====
    target_lang = None
    for lang in LANGUAGES:
        if re.search(rf"\b{re.escape(lang)}\b", q):
            target_lang = lang
            break

    wants_translation = "translate" in q or any(f"in {lang}" in q for lang in LANGUAGES)
    wants_points = "point" in q or "points" in q or "steps" in q
    wants_explain = any(x in q for x in [
        "explain", "describe", "elaborate", "detail", "summarize", "summary", "meaning"
    ])

    # ===== 4. Domain gating =====
    if not is_agriculture_related(user_query) and not wants_translation:
        return "🌿 I only answer agriculture-related questions."

    # ===== 5. RAG Search =====
    rag_answer = retrieve_rag(user_query)

    # ===============================
    # ✅ CASE A: CSV FOUND
    # ===============================
    if rag_answer:

        if wants_translation:
            lang = target_lang or "Hindi"
            translated = generate_gemini_response(
                f"Translate the following text into {lang} and also provide clear transliteration. "
                f"Text:\n{rag_answer}"
            )
            return f"{rag_answer}\n\n🌍 Translation:\n{translated}"

        if wants_points:
            points = generate_gemini_response(
                f"Convert this into exactly {point_count} bullet points:\n{rag_answer}"
            )
            return f"{rag_answer}\n\n🔹 Points:\n{points}"

        if wants_explain:
            explained = generate_gemini_response(
                f"Explain this clearly in simple words:\n{rag_answer}"
            )
            return f"{rag_answer}\n\n🔎 Explanation:\n{explained}"

        return rag_answer

    # ===============================
    # ✅ CASE B: Not in CSV
    # ===============================
    if wants_translation:
        lang = target_lang or "Hindi"
        return generate_gemini_response(
            f"Translate this agriculture topic into {lang}:\n{user_query}"
        )

    if wants_points:
        return generate_gemini_response(
            f"Give exactly {point_count} bullet points about this agriculture topic:\n{user_query}"
        )

    if wants_explain:
        return generate_gemini_response(user_query)

    return "🌿 I don’t have this in my CSV yet, but it is an agriculture-related topic."
