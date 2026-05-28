import json
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# ==========================================
# BOOK NAME MAPPING
# ==========================================

BOOK_NAMES = {
    "gn": "Genesis",
    "ex": "Exodus",
    "lv": "Leviticus",
    "nm": "Numbers",
    "dt": "Deuteronomy",
    "js": "Joshua",
    "jdg": "Judges",
    "rt": "Ruth",
    "1sm": "1 Samuel",
    "2sm": "2 Samuel",
    "1ki": "1 Kings",
    "2ki": "2 Kings",
    "1ch": "1 Chronicles",
    "2ch": "2 Chronicles",
    "ezr": "Ezra",
    "ne": "Nehemiah",
    "et": "Esther",
    "job": "Job",
    "ps": "Psalms",
    "pr": "Proverbs",
    "ec": "Ecclesiastes",
    "so": "Song of Solomon",
    "is": "Isaiah",
    "jr": "Jeremiah",
    "lm": "Lamentations",
    "ez": "Ezekiel",
    "dn": "Daniel",
    "ho": "Hosea",
    "jl": "Joel",
    "am": "Amos",
    "ob": "Obadiah",
    "jn": "Jonah",
    "mi": "Micah",
    "na": "Nahum",
    "hk": "Habakkuk",
    "zp": "Zephaniah",
    "hg": "Haggai",
    "zc": "Zechariah",
    "ml": "Malachi",
    "mt": "Matthew",
    "mk": "Mark",
    "lk": "Luke",
    "jnn": "John",
    "ac": "Acts",
    "rm": "Romans",
    "1co": "1 Corinthians",
    "2co": "2 Corinthians",
    "gl": "Galatians",
    "ep": "Ephesians",
    "ph": "Philippians",
    "cl": "Colossians",
    "1th": "1 Thessalonians",
    "2th": "2 Thessalonians",
    "1tm": "1 Timothy",
    "2tm": "2 Timothy",
    "tt": "Titus",
    "phm": "Philemon",
    "hb": "Hebrews",
    "jm": "James",
    "1pe": "1 Peter",
    "2pe": "2 Peter",
    "1jn": "1 John",
    "2jn": "2 John",
    "3jn": "3 John",
    "jd": "Jude",
    "re": "Revelation"
}

# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# ==========================================
# INITIALIZE CHROMADB
# ==========================================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="bible_verses"
)

# ==========================================
# LOAD BIBLE JSON
# ==========================================

BIBLE_PATH = "../data/bible.json"

print("Loading Bible dataset...")

with open(BIBLE_PATH, "r", encoding="utf-8-sig") as f:
    bible_data = json.load(f)

print(f"Loaded {len(bible_data)} books")

# ==========================================
# PROCESS DATA
# ==========================================

documents = []
embeddings = []
metadatas = []
ids = []

counter = 0

for book_data in tqdm(bible_data):

    abbrev = book_data.get("abbrev")

    book_name = BOOK_NAMES.get(
        abbrev,
        abbrev
    )

    chapters = book_data.get("chapters", [])

    for chapter_index, chapter in enumerate(chapters):

        chapter_number = chapter_index + 1

        for verse_index, verse_text in enumerate(chapter):

            verse_number = verse_index + 1

            if not verse_text.strip():
                continue

            reference = (
                f"{book_name} "
                f"{chapter_number}:{verse_number}"
            )

            document_text = (
                f"{reference} - {verse_text}"
            )

            # Generate embedding
            embedding = model.encode(
                document_text
            ).tolist()

            # Store
            documents.append(document_text)

            embeddings.append(embedding)

            ids.append(str(counter))

            metadatas.append({
                "reference": reference,
                "book": book_name,
                "chapter": chapter_number,
                "verse": verse_number,
                "text": verse_text
            })

            counter += 1

# ==========================================
# SAVE TO CHROMADB
# ==========================================

print("Saving embeddings to ChromaDB...")

BATCH_SIZE = 1000

for i in range(0, len(documents), BATCH_SIZE):

    collection.add(
        ids=ids[i:i+BATCH_SIZE],
        documents=documents[i:i+BATCH_SIZE],
        embeddings=embeddings[i:i+BATCH_SIZE],
        metadatas=metadatas[i:i+BATCH_SIZE]
    )

    print(
        f"Inserted batch "
        f"{i} - {i + BATCH_SIZE}"
    )

# ==========================================
# VERIFY INSERTION
# ==========================================

count = collection.count()

print(f"\nTotal verses stored: {count}")

# ==========================================
# TEST SEARCH
# ==========================================

test_query = "What does Bible say about love?"

query_embedding = model.encode(
    test_query
).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print("\nTop Results:\n")

for doc, meta in zip(
    results["documents"][0],
    results["metadatas"][0]
):

    print(
        f"{meta['reference']}\n"
        f"{meta['text']}\n"
    )

print("Bible ingestion complete.")