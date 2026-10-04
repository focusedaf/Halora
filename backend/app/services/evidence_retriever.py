import re
import math



DEFAULT_TOP_K = 5

MIN_CHUNK_LENGTH = 80

MAX_CHUNK_LENGTH = 1200




def normalize_text(text: str):
    """
    Normalize text for lexical similarity.
    """

    if not text:
        return ""

    text = text.lower()

   
    text = re.sub(
        r"\s+",
        " ",
        text
    )

   
    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def tokenize(text: str):
    """
    Convert text into a set of normalized tokens.
    """

    normalized = normalize_text(
        text
    )

    if not normalized:
        return set()

    return set(
        normalized.split()
    )



STOPWORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "of",
    "to",
    "in",
    "on",
    "for",
    "with",
    "and",
    "or",
    "as",
    "by",
    "from",
    "that",
    "this",
    "these",
    "those",
    "it",
    "its",
    "at",
    "into",
    "than",
    "then",
    "also",
    "their",
    "they",
    "them",
    "which",
    "where",
    "when",
    "who",
    "what",
    "how",
    "can",
    "may",
    "will",
    "would",
    "could",
    "should",
}


def meaningful_tokens(text: str):
    """
    Remove common stopwords.
    """

    tokens = tokenize(text)

    return {
        token
        for token in tokens
        if token not in STOPWORDS
        and len(token) > 2
    }




def lexical_similarity(
    query: str,
    text: str
):
    """
    Calculate Jaccard-style lexical similarity.

    This is intentionally lightweight so the demo
    does not depend on sentence-transformers.
    """

    query_tokens = meaningful_tokens(
        query
    )

    text_tokens = meaningful_tokens(
        text
    )

    if not query_tokens or not text_tokens:
        return 0.0

    intersection = (
        query_tokens
        & text_tokens
    )

    union = (
        query_tokens
        | text_tokens
    )

    if not union:
        return 0.0

    return (
        len(intersection)
        / len(union)
    )




def word_coverage(
    query: str,
    text: str
):
    """
    Measure how much of the claim's vocabulary
    appears inside the evidence passage.
    """

    query_tokens = meaningful_tokens(
        query
    )

    text_tokens = meaningful_tokens(
        text
    )

    if not query_tokens:
        return 0.0

    matched = (
        query_tokens
        & text_tokens
    )

    return (
        len(matched)
        / len(query_tokens)
    )




def split_sentences(text: str):
    """
    Split source text into reasonably sized sentences.
    """

    if not text:
        return []

    text = text.replace(
        "\r",
        "\n"
    )

    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        text
    )

    cleaned = []

    for sentence in sentences:

        sentence = re.sub(
            r"\s+",
            " ",
            sentence
        ).strip()

        if not sentence:
            continue

        if len(sentence) < MIN_CHUNK_LENGTH:
            continue

        cleaned.append(
            sentence
        )

    return cleaned



def chunk_text(
    text: str,
    max_length: int = MAX_CHUNK_LENGTH
):
    """
    Convert source document into evidence chunks.

    Adjacent sentences are grouped together so that
    evidence retains some surrounding context.
    """

    sentences = split_sentences(
        text
    )

    if not sentences:
        return []

    chunks = []

    current = ""

    for sentence in sentences:

        if not current:

            current = sentence

            continue

        candidate = (
            current
            + " "
            + sentence
        )

        if len(candidate) <= max_length:

            current = candidate

        else:

            chunks.append(
                current.strip()
            )

            current = sentence

    if current:

        chunks.append(
            current.strip()
        )

    return [
        chunk
        for chunk in chunks
        if len(chunk) >= MIN_CHUNK_LENGTH
    ]




def rank_evidence(
    claim: str,
    chunks
):
    """
    Rank source passages against the claim.

    Score combines:

        lexical similarity
        +
        claim word coverage
    """

    ranked = []

    for index, chunk in enumerate(
        chunks
    ):

        similarity = lexical_similarity(
            claim,
            chunk
        )

        coverage = word_coverage(
            claim,
            chunk
        )

      

        score = (
            similarity * 0.40
            + coverage * 0.60
        )

        ranked.append({
            "text": chunk,

            "similarity": round(
                similarity,
                4
            ),

            "coverage": round(
                coverage,
                4
            ),

            "retrieval_score": round(
                score,
                4
            ),

            "source_chunk_index": index,
        })

    ranked.sort(
        key=lambda item: item[
            "retrieval_score"
        ],
        reverse=True
    )

    return ranked




def retrieve_evidence(
    claim: str,
    source: dict,
    top_k: int = DEFAULT_TOP_K
):
    """
    Retrieve passages from the actual scholarly source
    that are most relevant to the claim.
    """

    if not claim:

        return {
            "status": "invalid_claim",
            "evidence": [],
        }

    if not source:

        return {
            "status": "no_source",
            "evidence": [],
        }

    if source.get(
        "status"
    ) != "success":

        return {
            "status": "source_unavailable",
            "evidence": [],
        }

    source_text = source.get(
        "text"
    )

    if not source_text:

        return {
            "status": "no_source_text",
            "evidence": [],
        }

   
    chunks = chunk_text(
        source_text
    )

    if not chunks:

        return {
            "status": "no_chunks",
            "evidence": [],
        }

    

    ranked = rank_evidence(
        claim,
        chunks
    )

 

    selected = ranked[
        :max(1, top_k)
    ]

  
    for index, item in enumerate(
        selected,
        start=1
    ):

        item["rank"] = index

    return {
        "status": "success",

        "evidence": selected,

        "total_chunks": len(
            chunks
        ),

        "retrieval_method": (
            "lexical_similarity"
        ),
    }



# TEST


if __name__ == "__main__":

    claim = (
        "NumPy is the primary array programming "
        "library for the Python language."
    )

    source = {
        "status": "success",

        "text": """
        NumPy is a community-developed,
        open-source library, which provides a
        multidimensional Python array object along
        with array-aware functions that operate on it.

        Now, 15 years later, NumPy underpins almost
        every Python library that does scientific or
        numerical computation.

        NumPy and its ecosystem are commonly taught
        in university courses and are the focus of
        community conferences and workshops worldwide.

        NumPy provides in-memory multidimensional,
        homogeneously typed arrays on CPUs.
        """
    }

    result = retrieve_evidence(
        claim=claim,
        source=source,
        top_k=5
    )

    print()
    print("=" * 60)
    print("EVIDENCE RETRIEVER TEST")
    print("=" * 60)

    print(
        "Status:",
        result["status"]
    )

    print(
        "Method:",
        result.get(
            "retrieval_method"
        )
    )

    print(
        "Total chunks:",
        result.get(
            "total_chunks"
        )
    )

    print()

    for item in result.get(
        "evidence",
        []
    ):

        print(
            f"[Evidence {item['rank']}]"
        )

        print(
            "Similarity:",
            item["similarity"]
        )

        print(
            "Coverage:",
            item["coverage"]
        )

        print(
            "Retrieval score:",
            item["retrieval_score"]
        )

        print(
            item["text"]
        )

        print("-" * 60)