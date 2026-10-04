import re
import requests
from rapidfuzz.fuzz import ratio




def extract_doi(url: str):
    """
    Extract DOI from a URL or text.

    Examples:
    https://doi.org/10.1038/s41586-020-2649-2
    https://dx.doi.org/10.1038/s41586-020-2649-2
    """

    pattern = r"10\.\d{4,9}/[-._;()/:A-Z0-9]+"

    match = re.search(
        pattern,
        url,
        re.IGNORECASE
    )

    if not match:
        return None

    doi = match.group(0)

    return doi.rstrip(
        ".,;:)]}"
    )




def get_crossref_metadata(doi: str):

    url = f"https://api.crossref.org/works/{doi}"

    try:

        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": (
                    "CitationChecker/1.0 "
                    "(mailto:your-email@example.com)"
                )
            }
        )

        if response.status_code != 200:
            return None

        data = response.json()

        message = data.get(
            "message",
            {}
        )

        authors = []

        for author in message.get(
            "author",
            []
        ):

            name = " ".join(
                filter(
                    None,
                    [
                        author.get("given"),
                        author.get("family")
                    ]
                )
            )

            if name:
                authors.append(name)

        published = (
            message.get("published-print")
            or message.get("published-online")
            or message.get("published")
        )

        year = None

        if published:

            date_parts = published.get(
                "date-parts",
                []
            )

            if date_parts:
                year = date_parts[0][0]

        return {
            "source": "crossref",

            "title": (
                message.get(
                    "title",
                    [""]
                )[0]
                if message.get("title")
                else ""
            ),

            "authors": authors,

            "year": year,

            "doi": message.get(
                "DOI"
            ),

            "publisher": message.get(
                "publisher"
            ),

            "type": message.get(
                "type"
            ),

            "url": message.get(
                "URL"
            )
        }

    except Exception as e:

        print(
            "Crossref error:",
            e
        )

        return None




def get_openalex_metadata(doi: str):

    url = (
        "https://api.openalex.org/works/"
        f"https://doi.org/{doi}"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        authors = []

        for author in data.get(
            "authorships",
            []
        ):

            author_data = author.get(
                "author"
            )

            if author_data:

                name = author_data.get(
                    "display_name"
                )

                if name:
                    authors.append(name)

        return {
            "source": "openalex",

            "title": data.get(
                "title",
                ""
            ),

            "authors": authors,

            "year": data.get(
                "publication_year"
            ),

            "doi": (
                data.get("doi")
                or ""
            ).replace(
                "https://doi.org/",
                ""
            ),

            "publisher": (
                data.get(
                    "primary_location",
                    {}
                )
                .get(
                    "source",
                    {}
                )
                .get(
                    "display_name"
                )
            ),

            "type": data.get(
                "type"
            ),

            "url": data.get(
                "id"
            )
        }

    except Exception as e:

        print(
            "OpenAlex error:",
            e
        )

        return None




def compare_titles(
    title_a: str,
    title_b: str
):

    if not title_a or not title_b:
        return 0

    return round(
        ratio(
            title_a.lower(),
            title_b.lower()
        )
    )



def compare_authors(
    authors_a: list,
    authors_b: list
):

    if not authors_a or not authors_b:
        return 0

    authoritative_surnames = set()

    for author in authors_b:

        author = author.strip()

        if not author:
            continue

        parts = author.split()

        if parts:

            surname = parts[-1]

            surname = re.sub(
                r"[^a-zA-ZÀ-ÿ'’-]",
                "",
                surname
            ).lower()

            if surname:
                authoritative_surnames.add(
                    surname
                )

    matched = 0

    for author in authors_a:

        author = author.strip()

        if not author:
            continue

    

        et_al_match = re.match(
            r"^(.+?)\s+et\s+al\.?$",
            author,
            re.IGNORECASE
        )

        if et_al_match:

            submitted_surname = (
                et_al_match.group(1)
                .strip()
            )

            submitted_surname = re.sub(
                r"[^a-zA-ZÀ-ÿ'’-]",
                "",
                submitted_surname
            ).lower()

            if (
                submitted_surname
                in authoritative_surnames
            ):
                matched += 1

            continue

        

        parts = author.split()

        if not parts:
            continue

        submitted_surname = re.sub(
            r"[^a-zA-ZÀ-ÿ'’-]",
            "",
            parts[-1]
        ).lower()

        if (
            submitted_surname
            in authoritative_surnames
        ):
            matched += 1

    return round(
        (matched / len(authors_a)) * 100
    )



def compare_years(
    year_a,
    year_b
):

    if not year_a or not year_b:
        return 0

    return (
        100
        if year_a == year_b
        else 0
    )




def compare_doi(
    doi_a: str,
    doi_b: str
):

    if not doi_a or not doi_b:
        return 0

    def normalize(doi):

        return (
            doi.lower()
            .replace(
                "https://doi.org/",
                ""
            )
            .replace(
                "http://doi.org/",
                ""
            )
            .replace(
                "https://dx.doi.org/",
                ""
            )
            .replace(
                "http://dx.doi.org/",
                ""
            )
            .strip()
        )

    return (
        100
        if normalize(doi_a)
        == normalize(doi_b)
        else 0
    )




def compare_metadata(
    submitted,
    original
):

    title_score = compare_titles(
        submitted.get(
            "title",
            ""
        ),
        original.get(
            "title",
            ""
        )
    )

    author_score = compare_authors(
        submitted.get(
            "authors",
            []
        ),
        original.get(
            "authors",
            []
        )
    )

    year_score = compare_years(
        submitted.get(
            "year"
        ),
        original.get(
            "year"
        )
    )

    doi_score = compare_doi(
        submitted.get(
            "doi",
            ""
        ),
        original.get(
            "doi",
            ""
        )
    )



    overall = round(
        (
            title_score * 0.40
            + author_score * 0.25
            + year_score * 0.15
            + doi_score * 0.20
        )
    )

    return {
        "title_match": title_score,
        "author_match": author_score,
        "year_match": year_score,
        "doi_match": doi_score,
        "overall_score": overall
    }



def determine_status(
    comparison,
    crossref_found,
    openalex_found
):

   

    if not crossref_found and not openalex_found:

        return {
            "status": "not_found",

            "issues": [
                "The DOI could not be found in Crossref or OpenAlex."
            ]
        }

    issues = []

  

    if comparison["title_match"] < 70:

        issues.append(
            "The cited title does not match the authoritative title."
        )

   

    if comparison["author_match"] == 0:

        issues.append(
            "The cited author does not match the authoritative authors."
        )


    if comparison["year_match"] == 0:

        issues.append(
            "The cited publication year does not match the authoritative year."
        )

   

    if comparison["doi_match"] == 0:

        issues.append(
            "The cited DOI does not match the authoritative DOI."
        )

   

    if not issues:

        status = "verified"

 

    elif comparison["doi_match"] == 100:

        status = "invalid"

   

    else:

        status = "suspicious"

    return {
        "status": status,
        "issues": issues
    }



def lookup_doi(doi: str):

    crossref = get_crossref_metadata(
        doi
    )

    openalex = get_openalex_metadata(
        doi
    )

    return {
        "doi": doi,
        "crossref": crossref,
        "openalex": openalex
    }



def verify_citation(submitted):

    doi = submitted.get(
        "doi"
    )


    if not doi:

        return {
            "status": "not_found",
            "score": 0,
            "issues": [
                "No DOI was found in the citation."
            ],
            "matches": {
                "title": 0,
                "authors": 0,
                "year": 0,
                "doi": 0
            },
            "crossref_found": False,
            "openalex_found": False,
            "crossref": None,
            "openalex": None
        }

   

    records = lookup_doi(
        doi
    )

    crossref = records.get(
        "crossref"
    )

    openalex = records.get(
        "openalex"
    )

   

    if not crossref and not openalex:

        return {
            "status": "not_found",
            "score": 0,
            "issues": [
                "The DOI could not be found in Crossref or OpenAlex."
            ],
            "matches": {
                "title": 0,
                "authors": 0,
                "year": 0,
                "doi": 0
            },
            "crossref_found": False,
            "openalex_found": False,
            "crossref": None,
            "openalex": None
        }

   

    original = (
        crossref
        or openalex
    )

   

    comparison = compare_metadata(
        submitted,
        original
    )

    

    verdict = determine_status(
        comparison,
        crossref is not None,
        openalex is not None
    )

    

    return {
        "status": verdict["status"],

        "score": comparison[
            "overall_score"
        ],

        "issues": verdict[
            "issues"
        ],

        "matches": {
            "title": comparison[
                "title_match"
            ],

            "authors": comparison[
                "author_match"
            ],

            "year": comparison[
                "year_match"
            ],

            "doi": comparison[
                "doi_match"
            ]
        },

        "crossref_found": (
            crossref is not None
        ),

        "openalex_found": (
            openalex is not None
        ),

        "crossref": crossref,

        "openalex": openalex
    }