import re



def extract_year(text: str):
    """
    Find a 4-digit publication year.
    Supports years from 1900-2099.
    """

    if not text:
        return None

    matches = re.findall(
        r"\b(19\d{2}|20\d{2})\b",
        text
    )

    if not matches:
        return None

    return int(matches[-1])



def extract_doi(text: str):

    if not text:
        return None

    pattern = (
        r"(?:https?://doi\.org/)?"
        r"(10\.\d{4,9}/"
        r"[-._;()/:A-Z0-9]+)"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    doi = match.group(1)

    return doi.rstrip(
        ".,;:)]}"
    )



def extract_url(text: str):

    if not text:
        return None

    pattern = r"https?://[^\s<>'\"]+"

    matches = re.findall(
        pattern,
        text
    )

    if not matches:
        return None

    return matches[0].rstrip(
        ".,;:)]}"
    )




def extract_arxiv_id(text: str):

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


def clean_reference_text(text: str):

    if not text:
        return ""

    text = text.strip()

   
    text = re.sub(
        r"^\s*(?:\[\d+\]|\d+[\.)])\s*",
        "",
        text
    )

  
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()




def looks_like_author_segment(segment: str):

    if not segment:
        return False

    segment = segment.strip()

  
    if re.search(
        r"\b[A-Z][A-Za-zÀ-ÿ'’-]+,\s*"
        r"(?:[A-Z]\.?\s*){1,4}$",
        segment
    ):
        return True

    
    if re.search(
        r"\b[A-Z][A-Za-zÀ-ÿ'’-]+\s+"
        r"(?:[A-Z]\.?\s*){1,3}"
        r"[A-Z][A-Za-zÀ-ÿ'’-]+$",
        segment
    ):
        return True

    if re.search(
        r"\bet\s+al\.?$",
        segment,
        re.IGNORECASE
    ):
        return True

    return False




def extract_authors(text: str):

    if not text:
        return []

    text = clean_reference_text(
        text
    )

    

    year_match = re.search(
        r"\b(?:19|20)\d{2}\b",
        text
    )

    before_year = (
        text[:year_match.start()]
        if year_match
        else text
    )

    
    et_al_match = re.search(
        r"\bet\s+al\.?",
        before_year,
        re.IGNORECASE
    )

    if et_al_match:

        author_part = before_year[
            :et_al_match.end()
        ].strip()

    else:

        

        parts = re.split(
            r"\.\s+(?=[A-Z])",
            before_year
        )

        author_part = ""

        if len(parts) > 1:

            possible = parts[0].strip()

            if (
                "," in possible
                or looks_like_author_segment(
                    possible
                )
            ):
                author_part = possible

        if not author_part:

            author_part = before_year.strip()

    author_part = re.sub(
        r"\bet\s+al\.?",
        "",
        author_part,
        flags=re.IGNORECASE
    ).strip(
        " ,.;:"
    )

    if not author_part:
        return []


    pattern = re.compile(
        r"""
        ([A-ZÀ-ÿ][A-Za-zÀ-ÿ'’-]+
        (?:,\s*
            (?:[A-ZÀ-ÿ]\.?\s*){1,4}
        )?)
        """,
        re.VERBOSE
    )

    matches = pattern.findall(
        author_part
    )

    authors = []

    for match in matches:

        author = re.sub(
            r"\s+",
            " ",
            match
        ).strip(
            " ,.;:"
        )

        if author:
            authors.append(
                author
            )

    

    if not authors:

        simple = re.search(
            r"\b([A-Z][A-Za-zÀ-ÿ'’-]+)"
            r"\s+et\s+al\.?",
            text,
            re.IGNORECASE
        )

        if simple:

            authors.append(
                simple.group(1)
            )

    return authors




def extract_title(text: str):

    if not text:
        return None

    text = clean_reference_text(
        text
    )

  
    quoted = re.findall(
        r'"([^"]{5,300})"',
        text
    )

    for candidate in quoted:

        if (
            "http://" not in candidate
            and "https://" not in candidate
            and not re.search(
                r"\bdoi\b",
                candidate,
                re.IGNORECASE
            )
        ):
            return candidate.strip()

    

    quoted = re.findall(
        r"'([^']{5,300})'",
        text
    )

    for candidate in quoted:

        if (
            "http://" not in candidate
            and "https://" not in candidate
        ):
            return candidate.strip()

    

    year_match = re.search(
        r"\b(?:19|20)\d{2}\b",
        text
    )

    if not year_match:
        return None

    before_year = text[
        :year_match.start()
    ].strip()

   
    before_year = re.sub(
        r"https?://\S+",
        "",
        before_year
    ).strip()


    et_al_match = re.search(
        r"\bet\s+al\.?\s*",
        before_year,
        re.IGNORECASE
    )

    if et_al_match:

        after_authors = before_year[
            et_al_match.end():
        ].strip(
            " .,:;-"
        )

        if after_authors:

          
            title_match = re.match(
                r"(.+?)(?:\.\s+|$)",
                after_authors
            )

            if title_match:

                candidate = (
                    title_match.group(1)
                    .strip(
                        " .,:;-"
                    )
                )

                if len(candidate) >= 5:

                    return candidate


    parts = re.split(
        r"\.\s+",
        before_year
    )

    cleaned_parts = [
        part.strip(
            " .,:;-"
        )
        for part in parts
        if part.strip(
            " .,:;-"
        )
    ]

    if len(cleaned_parts) >= 2:

       
       
        candidate = cleaned_parts[1]

        if (
            len(candidate) >= 5
            and not looks_like_author_segment(
                candidate
            )
        ):

            return candidate


    if cleaned_parts:

        candidate = cleaned_parts[-1]

        if (
            len(candidate) >= 5
            and not re.search(
                r"\b(?:Nature|Science|IEEE|ACM)"
                r"\b",
                candidate,
                re.IGNORECASE
            )
        ):

            return candidate

    return None




def parse_citation(text: str):

    if not text:

        return {
            "raw": text,
            "title": None,
            "authors": [],
            "year": None,
            "doi": None,
            "url": None,
            "arxiv_id": None,
        }

    return {

        "raw": text,

        "title": extract_title(
            text
        ),

        "authors": extract_authors(
            text
        ),

        "year": extract_year(
            text
        ),

        "doi": extract_doi(
            text
        ),

        "url": extract_url(
            text
        ),

        "arxiv_id": extract_arxiv_id(
            text
        ),
    }

# TEST


if __name__ == "__main__":

    tests = [

        (
            "Harris, C. R., Millman, K. J., "
            "van der Walt, S. J., et al. "
            "Array programming with NumPy. "
            "Nature, 2020."
        ),

        (
            "Jordan, M. I., & Mitchell, T. M. "
            "Machine learning: Trends, perspectives, "
            "and prospects. Science, 2015."
        ),

        (
            "LeCun, Y., Bengio, Y., & Hinton, G. "
            "Deep learning. Nature, 2015."
        ),

        (
            'Vaswani, A., Shazeer, N., Parmar, N., et al. '
            '"Attention Is All You Need." '
            "NeurIPS, 2017."
        ),

        (
            "Harris et al. (2020). "
            "Array programming with NumPy."
        ),

        (
            "Attention Is All You Need. "
            "https://arxiv.org/abs/1706.03762"
        ),
    ]

    for citation in tests:

        print()
        print("=" * 70)
        print("RAW:")
        print(citation)

        print()
        print("PARSED:")

        result = parse_citation(
            citation
        )

        for key, value in result.items():

            print(
                f"{key}: {value}"
            )