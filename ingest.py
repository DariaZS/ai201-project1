"""
ingest.py
Loads documents (from URLs or local .txt files), cleans them, and splits
them into chunks for embedding.

Spec (from planning.md):
- Chunk size: 500 characters
- Overlap: 100 characters
- Sources: 10 Columbia-related URLs covering CS, housing, dining, ODS
"""

import os
import re

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# 1. Document sources (from planning.md Documents table)
# ---------------------------------------------------------------------------

SOURCES = [
    {
        "name": "cs_faq",
        "url": "https://www.cs.columbia.edu/undergrad-faq/",
        "description": "CS major questions, waivers, double counting",
    },
    {
        "name": "cs_program_overview",
        "url": "https://www.cs.columbia.edu/education/undergraduate/",
        "description": "Tracks, requirements, research opportunities",
    },
    {
        "name": "housing_lottery_points",
        "url": "https://www.housing.columbia.edu/content/point-values-lottery-numbers-selection-appointments",
        "description": "How lottery numbers and seniority points work",
    },
    {
        "name": "room_selection_guide",
        "url": "https://www.housing.columbia.edu/roomselection",
        "description": "Full room selection process and eligibility",
    },
    {
        "name": "bwog_housing_strategy",
        "url": "https://bwog.com/2026/02/columbia-housing-strategy-for-rising-sophomores/",
        "description": "Real student tips for rising sophomores",
    },
    {
        "name": "ods_registration",
        "url": "https://www.health.columbia.edu/services/register-disability-services",
        "description": "How to register for disability accommodations",
    },
    {
        "name": "spectator_ods_guide",
        "url": "https://www.columbiaspectator.com/spectrum/2022/12/04/a-guide-to-navigating-accommodations-with-disability-services/",
        "description": "Student perspective on navigating accommodations",
    },
    {
        "name": "morningside_eating_guide",
        "url": "https://www.columbiaspectator.com/arts-and-culture/2022/08/26/a-beginners-guide-to-morningside-heights-eating/",
        "description": "Best restaurants near campus",
    },
    {
        "name": "dining_halls_guide",
        "url": "https://tcadmission.com/2024/09/24/your-guide-to-the-best-dining-halls-at-columbia/",
        "description": "Which dining halls are worth visiting",
    },
    {
        "name": "seas_advising_guide",
        "url": "https://www.cc-seas.columbia.edu/csa/advising_seas",
        "description": "Credit requirements and academic policies",
    },
]

RAW_DIR = "docs/raw"
CLEAN_DIR = "docs/clean"

CHUNK_SIZE = 500
OVERLAP = 100


# ---------------------------------------------------------------------------
# 2. Fetch + save raw HTML/text
# ---------------------------------------------------------------------------

def fetch_document(url: str) -> str:
    """Fetch a URL and return raw HTML text."""
    headers = {"User-Agent": "Mozilla/5.0 (educational RAG project)"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text


def save_raw(name: str, content: str):
    os.makedirs(RAW_DIR, exist_ok=True)
    path = os.path.join(RAW_DIR, f"{name}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ---------------------------------------------------------------------------
# 3. Clean HTML -> plain text
# ---------------------------------------------------------------------------

def clean_html(html: str) -> str:
    """Strip HTML tags, nav/footer boilerplate, and excess whitespace."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove elements that are never useful content
    for tag in soup(["script", "style", "nav", "footer", "header", "form", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # Collapse excess whitespace and blank lines
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    text = "\n".join(lines)

    # Remove leftover HTML entities just in case
    text = re.sub(r"&[a-z]+;", " ", text)
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()


def save_clean(name: str, text: str):
    os.makedirs(CLEAN_DIR, exist_ok=True)
    path = os.path.join(CLEAN_DIR, f"{name}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


# ---------------------------------------------------------------------------
# 4. Chunking — sliding window, 500 chars, 100 overlap
# ---------------------------------------------------------------------------

def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences using punctuation boundaries.
    Not perfect (struggles with abbreviations like 'Dr.'), but good
    enough to avoid cutting mid-sentence, which is the main goal.
    """
    # Split after . ! or ? followed by a space and a capital letter or newline
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])|\n+', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks, respecting sentence boundaries.

    Instead of cutting at a raw character count (which slices mid-word
    or mid-sentence), we group whole sentences together until adding
    another sentence would exceed chunk_size. We then back up by a
    couple of sentences for the next chunk to create overlap, so facts
    near a boundary are still retrievable from at least one chunk.
    """
    if not text:
        return []

    sentences = split_into_sentences(text)
    if not sentences:
        return []

    chunks = []
    current = []
    current_len = 0
    i = 0

    while i < len(sentences):
        sentence = sentences[i]

        # If a single sentence is itself longer than chunk_size, it can
        # never "fit" no matter what we do. Treat it as its own chunk
        # immediately rather than looping forever trying to make it fit.
        if len(sentence) > chunk_size:
            if current:
                chunks.append(" ".join(current).strip())
                current = []
                current_len = 0
            chunks.append(sentence.strip())
            i += 1
            continue

        # If adding this sentence would exceed chunk_size and we already
        # have content, close out the current chunk.
        if current and current_len + len(sentence) + 1 > chunk_size:
            chunks.append(" ".join(current).strip())

            # Build overlap: step back through current chunk's sentences
            # until we've included roughly `overlap` characters worth,
            # so the next chunk repeats some trailing context.
            overlap_sentences = []
            overlap_len = 0
            for s in reversed(current):
                if overlap_len + len(s) > overlap:
                    break
                overlap_sentences.insert(0, s)
                overlap_len += len(s) + 1

            # Safety check: if overlap selection didn't shrink anything
            # (e.g. overlap >= chunk_size causing it to re-select everything),
            # force progress by clearing it instead of looping forever.
            if len(overlap_sentences) >= len(current):
                overlap_sentences = []
                overlap_len = 0

            current = overlap_sentences
            current_len = overlap_len
            continue  # re-process the same sentence against the new current

        current.append(sentence)
        current_len += len(sentence) + 1
        i += 1

    if current:
        chunks.append(" ".join(current).strip())

    return chunks


# ---------------------------------------------------------------------------
# 5. Pipeline runner
# ---------------------------------------------------------------------------

def run_pipeline():
    all_chunks = []  # list of dicts: {"text": ..., "source": ...}

    for source in SOURCES:
        clean_path = os.path.join(CLEAN_DIR, f"{source['name']}.txt")

        # If a manually-cleaned file already exists and has real content,
        # use it instead of re-scraping (handles JS-rendered / blocked sites)
        if os.path.exists(clean_path):
            with open(clean_path, "r", encoding="utf-8") as f:
                existing_text = f.read()
            if len(existing_text.strip()) > 200:
                print(f"Using manually-cleaned file for {source['name']}...")
                chunks = chunk_text(existing_text)
                for chunk in chunks:
                    all_chunks.append({"text": chunk, "source": source["name"]})
                print(f"  -> {len(chunks)} chunks (from manual file)")
                continue

        print(f"Fetching {source['name']}...")
        try:
            html = fetch_document(source["url"])
            save_raw(source["name"], html)

            cleaned = clean_html(html)
            save_clean(source["name"], cleaned)

            chunks = chunk_text(cleaned)
            for chunk in chunks:
                all_chunks.append({"text": chunk, "source": source["name"]})

            print(f"  -> {len(chunks)} chunks")

        except Exception as e:
            print(f"  FAILED: {e}")
            print(f"  -> Skipping. Consider manual copy-paste into docs/clean/{source['name']}.txt")

    print(f"\nTotal chunks across all documents: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    chunks = run_pipeline()

    # Print 5 representative chunks for inspection (required for README)
    print("\n--- Sample chunks for README ---\n")
    for i, c in enumerate(chunks[:5]):
        print(f"Chunk {i+1} (source: {c['source']}):")
        print(c["text"])
        print()