import re
import requests
from rapidfuzz.fuzz import ratio



USER_AGENT = (
    "CitationChecker/1.0 "
    "(mailto:your-email@example.com)"
)

REQUEST_TIMEOUT = 15

CROSSREF_ROWS = 10
SEMANTIC_SCHOLAR_LIMIT = 10
OPENALEX_PER_PAGE = 10

DEFAULT_MIN_TITLE_SIMILARITY = 60




def normalize_text(text: str):
    """
    Normalize text for title comparison.
    """

    if not text:
        return ""

    text = str(text).lower()

    # Remove LaTeX/BibTeX artifacts
    text = re.sub(r"[{}]", "", text)
    text = re.sub(r"\\[a-zA-Z]+", " ", text)

    # Normalize punctuation
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()




def title_similarity(title_a: str, title_b: str):
    """
    Calculate normalized Levenshtein similarity.

    Returns:
        0-100
    """

    a = normalize_text(title_a)
    b = normalize_text(title_b)

    if not a or not b:
        return 0

    return round(ratio(a, b))




def word_overlap(title_a: str, title_b: str):
    """
    Calculate lightweight word overlap.

    Returns:
        0-100
    """

    a = set(
        normalize_text(title_a).split()
    )

    b = set(
        normalize_text(title_b).split()
    )

    if not a or not b:
        return 0

    return round(
        len(a & b)
        / max(len(a), len(b))
        * 100
    )




def extract_surnames(authors):
    """
    Extract surnames from author names.

    Supports:
        Charles R. Harris
        Harris
        Harris et al.
    """

    surnames = set()

    for author in authors or []:

        if not author:
            continue

        author = str(author).strip()

        if not author:
            continue

        # Handle "Harris et al."
        author = re.sub(
            r"\s+et\s+al\.?$",
            "",
            author,
            flags=re.IGNORECASE
        )

        parts = author.split()

        if not parts:
            continue

        surname = re.sub(
            r"[^a-zA-ZÀ-ÿ'’-]",
            "",
            parts[-1]
        ).lower()

        if surname:
            surnames.add(surname)

    return surnames




def author_similarity(
    submitted_authors,
    candidate_authors
):
    """
    Compare submitted authors against candidate authors.

    Returns:
        0-100
    """

    submitted = extract_surnames(
        submitted_authors
    )

    candidate = extract_surnames(
        candidate_authors
    )

    if not submitted or not candidate:
        return 0

    matched = len(
        submitted & candidate
    )

    return round(
        matched
        / len(submitted)
        * 100
    )




def year_bonus(
    submitted_year,
    candidate_year
):
    """
    Small ranking bonus when publication years match.

    Returns:
        0 or 5
    """

    if not submitted_year or not candidate_year:
        return 0

    try:
        submitted_year = int(
            submitted_year
        )

        candidate_year = int(
            candidate_year
        )

    except (
        TypeError,
        ValueError
    ):
        return 0

    if submitted_year == candidate_year:
        return 5

    return 0




def make_request(
    url: str,
    params=None,
    headers=None
):
    """
    Centralized HTTP request helper.
    """

    request_headers = {
        "User-Agent": USER_AGENT
    }

    if headers:
        request_headers.update(
            headers
        )

    try:

        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
            headers=request_headers
        )

        if response.status_code != 200:
            return None

        return response

    except requests.RequestException as e:

        print(
            f"Request failed: {e}"
        )

        return None



def search_crossref(
    title: str,
    authors=None,
    year=None,
    rows: int = CROSSREF_ROWS
):
    """
    Search CrossRef using the citation title.
    """

    if not title:
        return []

    url = (
        "https://api.crossref.org/works"
    )

    params = {
        "query.title": title,
        "rows": rows,
    }

    response = make_request(
        url,
        params=params
    )

    if response is None:
        return []

    try:

        data = response.json()

        items = (
            data
            .get("message", {})
            .get("items", [])
        )

    except (
        ValueError,
        AttributeError
    ):

        return []

    results = []

    for item in items:

        if not isinstance(item, dict):
            continue

       
        titles = item.get(
            "title"
        )

        candidate_title = ""

        if isinstance(
            titles,
            list
        ) and titles:

            candidate_title = (
                titles[0]
                or ""
            )

       

        candidate_authors = []

        raw_authors = item.get(
            "author",
            []
        )

        if isinstance(
            raw_authors,
            list
        ):

            for author in raw_authors:

                if not isinstance(
                    author,
                    dict
                ):
                    continue

                name = " ".join(
                    filter(
                        None,
                        [
                            author.get(
                                "given"
                            ),
                            author.get(
                                "family"
                            )
                        ]
                    )
                )

                if name:
                    candidate_authors.append(
                        name
                    )

        

        candidate_year = None

        published = (
            item.get(
                "published-print"
            )
            or item.get(
                "published-online"
            )
            or item.get(
                "published"
            )
        )

        if isinstance(
            published,
            dict
        ):

            parts = published.get(
                "date-parts",
                []
            )

            if (
                isinstance(parts, list)
                and parts
                and isinstance(parts[0], list)
                and parts[0]
            ):

                candidate_year = (
                    parts[0][0]
                )

        

        similarity = title_similarity(
            title,
            candidate_title
        )

        overlap = word_overlap(
            title,
            candidate_title
        )

        author_score = author_similarity(
            authors,
            candidate_authors
        )

        score = (
            similarity * 0.70
            + author_score * 0.25
            + overlap * 0.05
            + year_bonus(
                year,
                candidate_year
            )
        )

        results.append({

            "source": "crossref",

            "title": candidate_title,

            "authors": candidate_authors,

            "year": candidate_year,

            "doi": item.get(
                "DOI"
            ),

            "publisher": item.get(
                "publisher"
            ),

            "type": item.get(
                "type"
            ),

            "url": item.get(
                "URL"
            ),

            "title_similarity": similarity,

            "word_overlap": overlap,

            "author_similarity": author_score,

            "ranking_score": round(
                score,
                2
            )
        })

    return results




def search_openalex(
    title: str,
    authors=None,
    year=None,
    per_page: int = OPENALEX_PER_PAGE
):
    """
    Search OpenAlex using title.

    Handles incomplete/null OpenAlex metadata safely.
    """

    if not title:
        return []

    url = (
        "https://api.openalex.org/works"
    )

    params = {
        "search": title,
        "per-page": per_page,
    }

    response = make_request(
        url,
        params=params
    )

    if response is None:
        return []

    try:

        data = response.json()

    except ValueError:

        return []

    raw_results = data.get(
        "results",
        []
    )

    if not isinstance(
        raw_results,
        list
    ):
        return []

    results = []

    for item in raw_results:

        if not isinstance(
            item,
            dict
        ):
            continue

      
        candidate_title = (
            item.get("title")
            or ""
        )

     
        candidate_authors = []

        authorships = item.get(
            "authorships"
        ) or []

        if isinstance(
            authorships,
            list
        ):

            for authorship in authorships:

                if not isinstance(
                    authorship,
                    dict
                ):
                    continue

                author = authorship.get(
                    "author"
                )

                if not isinstance(
                    author,
                    dict
                ):
                    continue

                name = author.get(
                    "display_name"
                )

                if name:
                    candidate_authors.append(
                        name
                    )

      

        candidate_year = item.get(
            "publication_year"
        )

        

        doi = item.get(
            "doi"
        ) or ""

        if isinstance(
            doi,
            str
        ):

            doi = re.sub(
                r"^https?://doi\.org/",
                "",
                doi,
                flags=re.IGNORECASE
            )

      

        primary_location = (
            item.get(
                "primary_location"
            )
            or {}
        )

        if not isinstance(
            primary_location,
            dict
        ):
            primary_location = {}

        source = (
            primary_location.get(
                "source"
            )
            or {}
        )

        if not isinstance(
            source,
            dict
        ):
            source = {}

        publisher = (
            source.get(
                "display_name"
            )
            or ""
        )

       

        candidate_url = (
            item.get("id")
            or ""
        )


        similarity = title_similarity(
            title,
            candidate_title
        )

        overlap = word_overlap(
            title,
            candidate_title
        )

        author_score = author_similarity(
            authors,
            candidate_authors
        )

        score = (
            similarity * 0.70
            + author_score * 0.25
            + overlap * 0.05
            + year_bonus(
                year,
                candidate_year
            )
        )

        results.append({

            "source": "openalex",

            "title": candidate_title,

            "authors": candidate_authors,

            "year": candidate_year,

            "doi": doi,

            "publisher": publisher,

            "type": item.get(
                "type"
            ),

            "url": candidate_url,

            "title_similarity": similarity,

            "word_overlap": overlap,

            "author_similarity": author_score,

            "ranking_score": round(
                score,
                2
            )
        })

    return results




def search_semantic_scholar(
    title: str,
    authors=None,
    year=None,
    limit: int = SEMANTIC_SCHOLAR_LIMIT
):
    """
    Search Semantic Scholar using title.
    """

    if not title:
        return []

    url = (
        "https://api.semanticscholar.org/"
        "graph/v1/paper/search"
    )

    params = {
        "query": title,
        "limit": limit,
        "fields": (
            "title,authors,year,"
            "externalIds,url,venue"
        ),
    }

    response = make_request(
        url,
        params=params
    )

    if response is None:
        return []

    try:

        data = response.json()

    except ValueError:

        return []

    raw_results = data.get(
        "data",
        []
    )

    if not isinstance(
        raw_results,
        list
    ):
        return []

    results = []

    for item in raw_results:

        if not isinstance(
            item,
            dict
        ):
            continue

      
        candidate_title = (
            item.get("title")
            or ""
        )

      

        candidate_authors = []

        raw_authors = item.get(
            "authors"
        ) or []

        if isinstance(
            raw_authors,
            list
        ):

            for author in raw_authors:

                if not isinstance(
                    author,
                    dict
                ):
                    continue

                name = author.get(
                    "name"
                )

                if name:
                    candidate_authors.append(
                        name
                    )


        candidate_year = item.get(
            "year"
        )

        # -------------------------------------------------
        # EXTERNAL IDS
        # -------------------------------------------------

        external_ids = (
            item.get(
                "externalIds"
            )
            or {}
        )

        if not isinstance(
            external_ids,
            dict
        ):
            external_ids = {}

        # -------------------------------------------------
        # SIMILARITY
        # -------------------------------------------------

        similarity = title_similarity(
            title,
            candidate_title
        )

        overlap = word_overlap(
            title,
            candidate_title
        )

        author_score = author_similarity(
            authors,
            candidate_authors
        )

        score = (
            similarity * 0.70
            + author_score * 0.25
            + overlap * 0.05
            + year_bonus(
                year,
                candidate_year
            )
        )

        results.append({

            "source": "semantic_scholar",

            "title": candidate_title,

            "authors": candidate_authors,

            "year": candidate_year,

            "doi": external_ids.get(
                "DOI"
            ),

            "arxiv_id": external_ids.get(
                "ArXiv"
            ),

            "publisher": (
                item.get(
                    "venue"
                )
                or ""
            ),

            "type": "article",

            "url": item.get(
                "url"
            ),

            "title_similarity": similarity,

            "word_overlap": overlap,

            "author_similarity": author_score,

            "ranking_score": round(
                score,
                2
            )
        })

    return results


# =========================================================
# ARXIV ID EXTRACTION
# =========================================================

def extract_arxiv_id(text: str):
    """
    Extract an arXiv identifier from text.
    """

    if not text:
        return None

    patterns = [

        r"arxiv\.org/(?:abs|pdf)/"
        r"([0-9]{4}\.[0-9]{4,5})",

        r"\barXiv\s*:\s*"
        r"([0-9]{4}\.[0-9]{4,5})",

        r"\b([0-9]{4}\.[0-9]{4,5})\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None


# =========================================================
# ARXIV LOOKUP
# =========================================================

def search_arxiv(arxiv_id: str):
    """
    Resolve an arXiv identifier.
    """

    if not arxiv_id:
        return None

    url = (
        "https://export.arxiv.org/api/"
        "query"
    )

    params = {
        "id_list": arxiv_id
    }

    response = make_request(
        url,
        params=params
    )

    if response is None:
        return None

    xml = response.text

    titles = re.findall(
        r"<title>(.*?)</title>",
        xml,
        re.DOTALL
    )

    if len(titles) >= 2:

        candidate_title = titles[1].strip()

    elif titles:

        candidate_title = titles[0].strip()

    else:

        return None

    candidate_title = re.sub(
        r"\s+",
        " ",
        candidate_title
    )

    author_names = re.findall(
        r"<name>(.*?)</name>",
        xml
    )

    authors = [

        re.sub(
            r"\s+",
            " ",
            author
        ).strip()

        for author in author_names
    ]

    published_match = re.search(
        r"<published>(\d{4})-",
        xml
    )

    year = None

    if published_match:

        year = int(
            published_match.group(1)
        )

    return {

        "source": "arxiv",

        "title": candidate_title,

        "authors": authors,

        "year": year,

        "doi": None,

        "arxiv_id": arxiv_id,

        "publisher": "arXiv",

        "type": "preprint",

        "url": (
            f"https://arxiv.org/abs/"
            f"{arxiv_id}"
        ),

        "title_similarity": None,

        "word_overlap": None,

        "author_similarity": None,

        "ranking_score": 100
    }


# =========================================================
# CANDIDATE DEDUPLICATION
# =========================================================

def deduplicate_candidates(
    candidates
):
    """
    Remove duplicate papers returned by multiple
    scholarly APIs.

    DOI is preferred as the unique identifier.
    Title is used as fallback.
    """

    unique = {}

    for candidate in candidates:

        if not isinstance(
            candidate,
            dict
        ):
            continue

        doi = candidate.get(
            "doi"
        )

        title = normalize_text(
            candidate.get(
                "title",
                ""
            )
        )

        if doi:

            key = (
                "doi",
                str(doi).lower()
            )

        elif title:

            key = (
                "title",
                title
            )

        else:

            continue

        if key not in unique:

            unique[key] = candidate

        else:

            existing = unique[key]

            if (
                candidate.get(
                    "ranking_score",
                    0
                )
                >
                existing.get(
                    "ranking_score",
                    0
                )
            ):

                unique[key] = candidate

    return list(
        unique.values()
    )


# =========================================================
# CANDIDATE RANKING
# =========================================================

def rank_candidates(
    submitted,
    candidates
):
    """
    Re-rank candidates using:

        Title similarity  -> 70%
        Author similarity -> 25%
        Word overlap      -> 5%
        Year match        -> +5 bonus

    Title remains the dominant signal.
    """

    ranked = []

    submitted_title = submitted.get(
        "title",
        ""
    )

    submitted_authors = submitted.get(
        "authors",
        []
    )

    submitted_year = submitted.get(
        "year"
    )

    for candidate in candidates:

        if not isinstance(
            candidate,
            dict
        ):
            continue

        title_score = title_similarity(
            submitted_title,
            candidate.get(
                "title",
                ""
            )
        )

        author_score = author_similarity(
            submitted_authors,
            candidate.get(
                "authors",
                []
            )
        )

        overlap_score = word_overlap(
            submitted_title,
            candidate.get(
                "title",
                ""
            )
        )

        year_score = year_bonus(
            submitted_year,
            candidate.get(
                "year"
            )
        )

        final_score = (
            title_score * 0.70
            + author_score * 0.25
            + overlap_score * 0.05
            + year_score
        )

        candidate = dict(
            candidate
        )

        candidate[
            "title_similarity"
        ] = title_score

        candidate[
            "author_similarity"
        ] = author_score

        candidate[
            "word_overlap"
        ] = overlap_score

        candidate[
            "ranking_score"
        ] = round(
            final_score,
            2
        )

        ranked.append(
            candidate
        )

    ranked.sort(
        key=lambda x: x.get(
            "ranking_score",
            0
        ),
        reverse=True
    )

    return ranked




def retrieve_candidate(
    submitted,
    min_title_similarity: int = DEFAULT_MIN_TITLE_SIMILARITY
):
    """
    Retrieve the most likely real paper.

    Cascade:

    1. Direct arXiv identifier
    2. CrossRef
    3. Semantic Scholar
    4. OpenAlex

    Returns both the best candidate and all ranked
    candidates.
    """

    if not isinstance(
        submitted,
        dict
    ):

        return {
            "status": "invalid_input",
            "candidate": None,
            "source": None,
            "candidates": []
        }

    title = (
        submitted.get(
            "title",
            ""
        )
        or ""
    )

    raw_text = (
        submitted.get(
            "raw_text",
            ""
        )
        or ""
    )

    

    arxiv_id = (
        submitted.get(
            "arxiv_id"
        )
        or extract_arxiv_id(
            raw_text
        )
    )

    if arxiv_id:

        arxiv_candidate = search_arxiv(
            arxiv_id
        )

        if arxiv_candidate:

            similarity = title_similarity(
                title,
                arxiv_candidate[
                    "title"
                ]
            )

            arxiv_candidate[
                "title_similarity"
            ] = similarity

            if (
                not title
                or similarity
                >= min_title_similarity
            ):

                return {

                    "status": "found",

                    "candidate": (
                        arxiv_candidate
                    ),

                    "source": "arxiv",

                    "candidates": [
                        arxiv_candidate
                    ]
                }

   

    crossref_candidates = (
        search_crossref(
            title,
            submitted.get(
                "authors"
            ),
            submitted.get(
                "year"
            )
        )
    )

   

    semantic_candidates = (
        search_semantic_scholar(
            title,
            submitted.get(
                "authors"
            ),
            submitted.get(
                "year"
            )
        )
    )

 

    openalex_candidates = (
        search_openalex(
            title,
            submitted.get(
                "authors"
            ),
            submitted.get(
                "year"
            )
        )
    )

    

    all_candidates = (
        crossref_candidates
        + semantic_candidates
        + openalex_candidates
    )

   

    all_candidates = (
        deduplicate_candidates(
            all_candidates
        )
    )

  

    ranked = rank_candidates(
        submitted,
        all_candidates
    )

    if not ranked:

        return {

            "status": "not_found",

            "candidate": None,

            "source": None,

            "candidates": []
        }

  

    best = ranked[0]

    best_title_similarity = (
        best.get(
            "title_similarity",
            0
        )
    )

    if (
        best_title_similarity
        < min_title_similarity
    ):

        return {

            "status": "not_found",

            "candidate": best,

            "source": best.get(
                "source"
            ),

            "candidates": ranked
        }

  
    return {

        "status": "found",

        "candidate": best,

        "source": best.get(
            "source"
        ),

        "candidates": ranked
    }