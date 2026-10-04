import re
import requests
import trafilatura




REQUEST_TIMEOUT = 15

MAX_SOURCE_TEXT = 100000

USER_AGENT = (
    "CitationChecker/1.0 "
    "(academic citation verification project)"
)

CROSSREF_API = "https://api.crossref.org/works"

OPENALEX_API = "https://api.openalex.org/works"

SEMANTIC_SCHOLAR_API = (
    "https://api.semanticscholar.org/graph/v1/paper/search"
)



def safe_dict(value):

    if isinstance(value, dict):
        return value

    return {}


def safe_list(value):

    if isinstance(value, list):
        return value

    return []


def safe_string(value):

    if value is None:
        return ""

    try:
        return str(value).strip()

    except Exception:
        return ""




def clean_url(url):

    if not url:
        return None

    if not isinstance(url, str):
        return None

    url = url.strip()

    if not url:
        return None

    return url.rstrip(
        ".,;:)]}"
    )




def normalize_doi(doi):

    if not doi:
        return None

    doi = safe_string(doi)

    doi = re.sub(
        r"^https?://(dx\.)?doi\.org/",
        "",
        doi,
        flags=re.IGNORECASE
    )

    doi = re.sub(
        r"^doi:\s*",
        "",
        doi,
        flags=re.IGNORECASE
    )

    return doi.strip()


def doi_to_url(doi):

    doi = normalize_doi(
        doi
    )

    if not doi:
        return None

    return (
        "https://doi.org/"
        + doi
    )




def fetch_url(url):

    url = clean_url(
        url
    )

    if not url:
        return None

    try:

        response = requests.get(

            url,

            timeout=REQUEST_TIMEOUT,

            headers={

                "User-Agent":
                    USER_AGENT,

                "Accept":
                    (
                        "text/html,"
                        "application/xhtml+xml,"
                        "application/pdf,"
                        "application/json,"
                        "*/*;q=0.8"
                    ),

                "Accept-Language":
                    "en-US,en;q=0.9",
            },

            allow_redirects=True,
        )

        response.raise_for_status()

        return response

    except requests.exceptions.Timeout:

        return None

    except requests.exceptions.RequestException:

        return None



def fetch_json(
    url,
    params=None
):

    url = clean_url(
        url
    )

    if not url:
        return None

    try:

        response = requests.get(

            url,

            params=params,

            timeout=REQUEST_TIMEOUT,

            headers={
                "User-Agent":
                    USER_AGENT,

                "Accept":
                    "application/json",
            },

            allow_redirects=True,
        )

        response.raise_for_status()

        return response.json()

    except Exception:

        return None




def is_blocked(html):

    if not html:
        return False

    lower = html.lower()

    indicators = [

        "access denied",

        "request blocked",

        "your request has been blocked",

        "verify you are human",

        "captcha",

        "checking your browser",

        "unusual traffic",

        "bot detection",

        "security check",

        "cloudflare",

        "enable javascript",

    ]

    return any(
        indicator in lower
        for indicator in indicators
    )




def extract_html_title(html):

    if not html:
        return ""

    match = re.search(

        r"<title[^>]*>(.*?)</title>",

        html,

        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return ""

    title = re.sub(

        r"\s+",

        " ",

        match.group(1)
    ).strip()

    return title



def extract_html_content(html):

    if not html:
        return None

    try:

        extracted = trafilatura.extract(

            html,

            include_comments=False,

            include_tables=True,

            include_links=False,

            include_images=False,

            favor_precision=True,
        )

    except Exception:

        return None

    if not extracted:
        return None

    extracted = re.sub(

        r"\n{3,}",

        "\n\n",

        extracted
    ).strip()

    if len(extracted) < 100:
        return None

    return extracted



def extract_pdf_content(content):

    try:

        from pypdf import PdfReader

        from io import BytesIO

        reader = PdfReader(
            BytesIO(content)
        )

        pages = []

        for page in reader.pages:

            try:

                text = page.extract_text()

                if text:

                    text = text.strip()

                    if text:

                        pages.append(
                            text
                        )

            except Exception:

                continue

        if not pages:
            return None

        text = "\n\n".join(
            pages
        )

        text = re.sub(

            r"\n{3,}",

            "\n\n",

            text
        ).strip()

        if len(text) < 100:
            return None

        return text

    except Exception as e:

        print(
            "PDF extraction error:",
            e
        )

        return None




def build_result(

    status,

    source,

    url=None,

    final_url=None,

    title=None,

    text=None,

    content_type=None,

    attempts=None,

):

    result = {

        "status":
            status,

        "source":
            source,

        "url":
            url,

        "final_url":
            final_url,

        "title":
            title,

        "text":
            text,

        "content_type":
            content_type,

    }

    if attempts is not None:

        result["attempts"] = attempts

    return result




def retrieve_source(

    url,

    source_name="unknown"

):

    url = clean_url(
        url
    )

    if not url:

        return build_result(

            status="invalid_url",

            source=source_name,
        )

    response = fetch_url(
        url
    )

    if response is None:

        return build_result(

            status="unreachable",

            source=source_name,

            url=url,
        )

    final_url = str(
        response.url
    )

    content_type = (

        response.headers

        .get(
            "Content-Type",
            ""
        )

        .lower()
    )

   
    if (

        "application/pdf"

        in content_type

        or final_url.lower().endswith(
            ".pdf"
        )

    ):

        text = extract_pdf_content(

            response.content
        )

        if not text:

            return build_result(

                status="unreadable",

                source=source_name,

                url=url,

                final_url=final_url,

                content_type=content_type,
            )

        return build_result(

            status="success",

            source=source_name,

            url=url,

            final_url=final_url,

            title=None,

            text=text[
                :MAX_SOURCE_TEXT
            ],

            content_type=content_type,
        )

   

    html = response.text

    title = extract_html_title(
        html
    )

    if is_blocked(
        html
    ):

        return build_result(

            status="blocked",

            source=source_name,

            url=url,

            final_url=final_url,

            title=title,

            content_type=content_type,
        )

    text = extract_html_content(
        html
    )

    if not text:

        return build_result(

            status="unreadable",

            source=source_name,

            url=url,

            final_url=final_url,

            title=title,

            content_type=content_type,
        )

    return build_result(

        status="success",

        source=source_name,

        url=url,

        final_url=final_url,

        title=title,

        text=text[
            :MAX_SOURCE_TEXT
        ],

        content_type=content_type,
    )




def get_candidate_title(
    candidate
):

    candidate = safe_dict(
        candidate
    )

    title = (

        candidate.get("title")

        or candidate.get(
            "display_name"
        )

        or ""
    )

    return safe_string(
        title
    )




def get_candidate_authors(
    candidate
):

    candidate = safe_dict(
        candidate
    )

    authors = candidate.get(
        "authors"
    )

    if not authors:

        authors = candidate.get(
            "author"
        )

    if isinstance(
        authors,
        list
    ):

        names = []

        for author in authors:

            if isinstance(
                author,
                str
            ):

                names.append(
                    author
                )

            elif isinstance(
                author,
                dict
            ):

                name = (

                    author.get(
                        "name"
                    )

                    or author.get(
                        "display_name"
                    )

                    or ""
                )

                if name:

                    names.append(
                        str(name)
                    )

        return names

    if isinstance(
        authors,
        str
    ):

        return [
            authors
        ]

    return []




def normalize_title(
    title
):

    title = safe_string(
        title
    ).lower()

    title = re.sub(
        r"[^a-z0-9\s]",
        " ",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    ).strip()

    return title




def title_similarity(
    title_a,
    title_b
):

    a = normalize_title(
        title_a
    )

    b = normalize_title(
        title_b
    )

    if not a or not b:
        return 0.0

    if a == b:
        return 1.0

    words_a = set(
        a.split()
    )

    words_b = set(
        b.split()
    )

    if not words_a or not words_b:
        return 0.0

    intersection = (
        words_a
        & words_b
    )

    union = (
        words_a
        | words_b
    )

    return round(

        len(intersection)
        / max(1, len(union)),

        4
    )



def search_crossref(
    candidate
):

    candidate = safe_dict(
        candidate
    )

    title = get_candidate_title(
        candidate
    )

    if not title:
        return []


    params = {

        "query.title":
            title,

        "rows":
            5,

        "select":
            (
                "DOI,title,author,"
                "published,URL,link"
            )
    }

    data = fetch_json(

        CROSSREF_API,

        params=params
    )

    if not isinstance(
        data,
        dict
    ):
        return []

    message = safe_dict(
        data.get("message")
    )

    items = safe_list(
        message.get("items")
    )

    results = []

    for item in items:

        item = safe_dict(
            item
        )

        titles = safe_list(
            item.get("title")
        )

        result_title = (

            titles[0]

            if titles

            else ""
        )

        similarity = title_similarity(

            title,

            result_title
        )

        if similarity < 0.35:
            continue

        results.append(
            item
        )

    results.sort(

        key=lambda x:
            title_similarity(

                title,

                (
                    safe_list(
                        x.get("title")
                    )[0]
                    if safe_list(
                        x.get("title")
                    )
                    else ""
                )
            ),

        reverse=True
    )

    return results



def search_openalex(
    candidate
):

    candidate = safe_dict(
        candidate
    )

    title = get_candidate_title(
        candidate
    )

    if not title:
        return []


    params = {

        "search":
            title,

        "per-page":
            5,

        "select":
            (
                "id,doi,title,"
                "display_name,"
                "publication_year,"
                "authorships,"
                "primary_location,"
                "locations,"
                "open_access"
            )
    }

    data = fetch_json(

        OPENALEX_API,

        params=params
    )

    if not isinstance(
        data,
        dict
    ):
        return []

    results = safe_list(
        data.get("results")
    )

    filtered = []

    for item in results:

        item = safe_dict(
            item
        )

        result_title = (

            item.get("display_name")

            or item.get("title")

            or ""
        )

        similarity = title_similarity(

            title,

            result_title
        )

        if similarity < 0.35:
            continue

        filtered.append(
            item
        )

    filtered.sort(

        key=lambda x:
            title_similarity(

                title,

                (
                    x.get(
                        "display_name"
                    )
                    or x.get(
                        "title"
                    )
                    or ""
                )
            ),

        reverse=True
    )

    return filtered




def search_semantic_scholar(
    candidate
):

    candidate = safe_dict(
        candidate
    )

    title = get_candidate_title(
        candidate
    )

    if not title:
        return []


    params = {

        "query":
            title,

        "limit":
            5,

        "fields":
            (
                "title,"
                "authors,"
                "year,"
                "url,"
                "openAccessPdf,"
                "externalIds"
            )
    }

    data = fetch_json(

        SEMANTIC_SCHOLAR_API,

        params=params
    )

    if not isinstance(
        data,
        dict
    ):
        return []

    results = safe_list(
        data.get("data")
    )

    filtered = []

    for item in results:

        item = safe_dict(
            item
        )

        result_title = item.get(
            "title"
        ) or ""

        similarity = title_similarity(

            title,

            result_title
        )

        if similarity < 0.35:
            continue

        filtered.append(
            item
        )

    filtered.sort(

        key=lambda x:
            title_similarity(

                title,

                x.get("title")
                or ""
            ),

        reverse=True
    )

    return filtered




def retrieve_from_openalex(
    openalex_record
):

    record = safe_dict(
        openalex_record
    )

    if not record:
        return None

    locations = []

    primary = safe_dict(

        record.get(
            "primary_location"
        )
    )

    if primary:

        locations.append(
            primary
        )

    raw_locations = safe_list(

        record.get(
            "locations"
        )
    )

    for location in raw_locations:

        location = safe_dict(
            location
        )

        if location and (
            location not in locations
        ):

            locations.append(
                location
            )

   

    for location in locations:

        pdf_info = safe_dict(

            location.get(
                "pdf"
            )
        )

        pdf_url = (

            pdf_info.get(
                "url"
            )

            or location.get(
                "pdf_url"
            )
        )

        if not pdf_url:
            continue

        result = retrieve_source(

            pdf_url,

            source_name=
                "openalex_pdf"
        )

        if result.get(
            "status"
        ) == "success":

            return result

   

    for location in locations:

        landing = (

            location.get(
                "landing_page_url"
            )

            or location.get(
                "url"
            )
        )

        if not landing:
            continue

        result = retrieve_source(

            landing,

            source_name=
                "openalex"
        )

        if result.get(
            "status"
        ) == "success":

            return result


    doi = record.get(
        "doi"
    )

    if doi:

        result = retrieve_source(

            doi_to_url(
                doi
            ),

            source_name=
                "openalex_doi"
        )

        if result.get(
            "status"
        ) == "success":

            return result

    return None




def retrieve_from_crossref(
    crossref_record
):

    record = safe_dict(
        crossref_record
    )

    if not record:
        return None


    links = safe_list(
        record.get(
            "link"
        )
    )

    for link in links:

        link = safe_dict(
            link
        )

        url = link.get(
            "URL"
        )

        if not url:
            continue

        result = retrieve_source(

            url,

            source_name=
                "crossref_link"
        )

        if result.get(
            "status"
        ) == "success":

            return result

    

    url = record.get(
        "URL"
    )

    if url:

        result = retrieve_source(

            url,

            source_name=
                "crossref"
        )

        if result.get(
            "status"
        ) == "success":

            return result


    doi = record.get(
        "DOI"
    )

    if doi:

        result = retrieve_source(

            doi_to_url(
                doi
            ),

            source_name=
                "crossref_doi"
        )

        if result.get(
            "status"
        ) == "success":

            return result

    return None



def retrieve_from_semantic_scholar(
    record
):

    record = safe_dict(
        record
    )

    if not record:
        return None

    oa_pdf = safe_dict(

        record.get(
            "openAccessPdf"
        )
    )

    pdf_url = oa_pdf.get(
        "url"
    )

    if pdf_url:

        result = retrieve_source(

            pdf_url,

            source_name=
                "semantic_scholar_pdf"
        )

        if result.get(
            "status"
        ) == "success":

            return result

    

    url = record.get(
        "url"
    )

    if url:

        result = retrieve_source(

            url,

            source_name=
                "semantic_scholar"
        )

        if result.get(
            "status"
        ) == "success":

            return result

    return None



def retrieve_candidate_source(
    candidate
):

    candidate = safe_dict(
        candidate
    )

    if not candidate:

        return build_result(

            status="no_candidate",

            source=None,
        )

    attempts = []

    title = get_candidate_title(
        candidate
    )

   

    arxiv_id = candidate.get(
        "arxiv_id"
    )

    if arxiv_id:

        arxiv_id = safe_string(
            arxiv_id
        )

        arxiv_urls = [

            (
                "https://arxiv.org/pdf/"
                + arxiv_id
                + ".pdf"
            ),

            (
                "https://arxiv.org/abs/"
                + arxiv_id
            ),
        ]

        for url in arxiv_urls:

            result = retrieve_source(

                url,

                source_name=
                    "arxiv"
            )

            attempts.append(
                result
            )

            if result.get(
                "status"
            ) == "success":

                return result


    direct_urls = [

        (
            candidate.get(
                "pdf_url"
            ),
            "candidate_pdf"
        ),

        (
            candidate.get(
                "open_access_url"
            ),
            "open_access"
        ),

        (
            candidate.get(
                "landing_page_url"
            ),
            "landing_page"
        ),

        (
            candidate.get(
                "url"
            ),
            "candidate_url"
        ),

    ]

    for url, source_name in direct_urls:

        url = clean_url(
            url
        )

        if not url:
            continue

        result = retrieve_source(

            url,

            source_name=
                source_name
        )

        attempts.append(
            result
        )

        if result.get(
            "status"
        ) == "success":

            return result

   

    openalex_record = (

        candidate.get(
            "openalex"
        )

        or candidate.get(
            "openalex_record"
        )
    )

    if openalex_record:

        result = retrieve_from_openalex(

            openalex_record
        )

        if result:

            attempts.append(
                result
            )

            if result.get(
                "status"
            ) == "success":

                return result


    crossref_record = (

        candidate.get(
            "crossref"
        )

        or candidate.get(
            "crossref_record"
        )
    )

    if crossref_record:

        result = retrieve_from_crossref(

            crossref_record
        )

        if result:

            attempts.append(
                result
            )

            if result.get(
                "status"
            ) == "success":

                return result


    if title:

        openalex_results = (
            search_openalex(
                candidate
            )
        )

        for record in openalex_results:

            result = (
                retrieve_from_openalex(
                    record
                )
            )

            if result:

                attempts.append(
                    result
                )

                if result.get(
                    "status"
                ) == "success":

                    return result

   

    if title:

        crossref_results = (
            search_crossref(
                candidate
            )
        )

        for record in crossref_results:

            result = (
                retrieve_from_crossref(
                    record
                )
            )

            if result:

                attempts.append(
                    result
                )

                if result.get(
                    "status"
                ) == "success":

                    return result

   

    if title:

        semantic_results = (
            search_semantic_scholar(
                candidate
            )
        )

        for record in semantic_results:

            result = (
                retrieve_from_semantic_scholar(
                    record
                )
            )

            if result:

                attempts.append(
                    result
                )

                if result.get(
                    "status"
                ) == "success":

                    return result


    doi = (

        candidate.get(
            "doi"
        )

        or candidate.get(
            "DOI"
        )
    )

    if doi:

        doi_url = doi_to_url(
            doi
        )

        if doi_url:

            result = retrieve_source(

                doi_url,

                source_name="doi"
            )

            attempts.append(
                result
            )

            if result.get(
                "status"
            ) == "success":

                return result

    

    blocked = any(

        safe_dict(
            attempt
        ).get(
            "status"
        ) == "blocked"

        for attempt in attempts
    )

    if blocked:

        status = "blocked"

    elif attempts:

        status = safe_dict(

            attempts[-1]

        ).get(

            "status",

            "unreachable"
        )

    else:

        status = "unreachable"

    return build_result(

        status=status,

        source=None,

        attempts=attempts,
    )




def retrieve_sources_for_citations(
    citations
):

    results = []

    for item in safe_list(
        citations
    ):

        item = safe_dict(
            item
        )

        candidate = item.get(
            "candidate"
        )

        source_result = (
            retrieve_candidate_source(
                candidate
            )
        )

        result = dict(
            item
        )

        result[
            "source_result"
        ] = source_result

        results.append(
            result
        )

    return results




if __name__ == "__main__":

    test_candidate = {

        "title":
            "Attention Is All You Need",

        "authors":
            [
                "Vaswani",
                "Shazeer",
                "Parmar"
            ],

        "year":
            2017,
    }

    test = retrieve_candidate_source(
        test_candidate
    )

    print()
    print("=" * 70)
    print("SOURCE RETRIEVAL TEST")
    print("=" * 70)

    print(
        "Status:",
        test.get("status")
    )

    print(
        "Source:",
        test.get("source")
    )

    print(
        "Title:",
        test.get("title")
    )

    print(
        "Final URL:",
        test.get("final_url")
    )

    print(
        "Content type:",
        test.get("content_type")
    )

    text = test.get(
        "text"
    )

    if text:

        print(
            "\nExtracted characters:",
            len(text)
        )

        print()
        print(
            "SOURCE PREVIEW"
        )

        print(
            "--------------"
        )

        print(
            text[:2000]
        )

    else:

        print(
            "\nNo source text extracted."
        )

        print()
        print(
            "ATTEMPTS:"
        )

        for i, attempt in enumerate(

            safe_list(
                test.get(
                    "attempts"
                )
            ),

            1
        ):

            attempt = safe_dict(
                attempt
            )

            print(

                f"{i}. "
                f"{attempt.get('source')} "
                f"-> "
                f"{attempt.get('status')} "
                f"| "
                f"{attempt.get('url')}"
            )