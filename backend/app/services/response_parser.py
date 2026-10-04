import re




def normalize_whitespace(text: str) -> str:
    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def find_reference_heading(text: str):
    """
    Find common reference-section headings.

    Supports:

        References
        ## References
        ### References
        Bibliography
        Works Cited
        Sources

    Returns the match object or None.
    """

    if not text:
        return None

    pattern = re.compile(
        r"(?im)^[ \t]*(?:#{1,6}[ \t]*)?"
        r"(?:references?|bibliography|works[ \t]+cited|sources)"
        r"[ \t]*:?[ \t]*$"
    )

    return pattern.search(text)



def split_response_and_references(text: str):
    """
    Split a complete AI response into:

        main_response
        reference_section
        reference_heading

    Everything after the reference heading is treated as
    the reference section.
    """

    if not text:
        return "", "", None

    match = find_reference_heading(text)

    if not match:
        return text.strip(), "", None

    main_response = text[:match.start()].strip()

    reference_section = text[
        match.end():
    ].strip()

    return (
        main_response,
        reference_section,
        match.group(0).strip(),
    )




def extract_citations(text: str):
    """
    Extract numbered citations.

    Examples:

        [1]
        [2]
        [1, 2]
        [1-3]

    Returns individual citation numbers.
    """

    if not text:
        return []

    citations = []

    pattern = re.compile(
        r"\[(\d+(?:\s*[-,]\s*\d+)*)\]"
    )

    for match in pattern.finditer(text):

        value = match.group(1)

        parts = re.split(
            r"\s*,\s*",
            value
        )

        for part in parts:

            part = part.strip()

            range_match = re.fullmatch(
                r"(\d+)\s*-\s*(\d+)",
                part
            )

            if range_match:

                start = int(
                    range_match.group(1)
                )

                end = int(
                    range_match.group(2)
                )

                # Keep ranges deliberately limited.
                if end >= start and end - start <= 20:

                    for number in range(
                        start,
                        end + 1
                    ):

                        number_str = str(number)

                        if number_str not in citations:
                            citations.append(number_str)

                continue

            if part.isdigit():

                if part not in citations:
                    citations.append(part)

    return citations




def extract_citation_occurrences(text: str):
    """
    Return every citation occurrence with its position.

    Example:

        "Some claim [1]"

    becomes:

        {
            "citation": "1",
            "raw": "[1]",
            "start": ...,
            "end": ...
        }
    """

    occurrences = []

    if not text:
        return occurrences

    pattern = re.compile(
        r"\[(\d+(?:\s*[-,]\s*\d+)*)\]"
    )

    for match in pattern.finditer(text):

        value = match.group(1)

        parts = re.split(
            r"\s*,\s*",
            value
        )

        for part in parts:

            part = part.strip()

            range_match = re.fullmatch(
                r"(\d+)\s*-\s*(\d+)",
                part
            )

            if range_match:

                start = int(
                    range_match.group(1)
                )

                end = int(
                    range_match.group(2)
                )

                if end >= start and end - start <= 20:

                    for number in range(
                        start,
                        end + 1
                    ):

                        occurrences.append({
                            "citation": str(number),
                            "raw": match.group(0),
                            "start": match.start(),
                            "end": match.end(),
                        })

                continue

            if part.isdigit():

                occurrences.append({
                    "citation": part,
                    "raw": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                })

    return occurrences



def extract_references(reference_section: str):
    """
    Extract numbered references from the reference section.

    Supports:

        [1] Author...
        [2] Author...

    and:

        1. Author...
        2. Author...

    Multiline references are supported.
    """

    references = {}

    if not reference_section:
        return references

    text = reference_section.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

   

    pattern = re.compile(
        r"(?m)^[ \t]*(?:\[(\d+)\]|(\d+)[.)])[ \t]+"
    )

    matches = list(
        pattern.finditer(text)
    )

    if not matches:
        return references

    for index, match in enumerate(matches):

        number = (
            match.group(1)
            or match.group(2)
        )

        start = match.end()

        if index + 1 < len(matches):

            end = matches[
                index + 1
            ].start()

        else:

            end = len(text)

        reference = text[
            start:end
        ].strip()

        reference = normalize_whitespace(
            reference
        )

        if reference:

            references[number] = reference

    return references




def extract_claims(main_response: str):
    """
    Extract text associated with numbered citations.

    This is intentionally permissive.

    We are NOT trying to perfectly identify the exact
    grammatical claim yet.

    Instead, for every citation we take the surrounding
    sentence/paragraph up to the citation.

    Example:

        Deep learning has improved image recognition
        and speech recognition [1].

    becomes approximately:

        Deep learning has improved image recognition
        and speech recognition [1].

    """

    claims = []

    if not main_response:
        return claims

    occurrences = extract_citation_occurrences(
        main_response
    )

    if not occurrences:
        return claims

   

    for occurrence in occurrences:

        citation_number = occurrence[
            "citation"
        ]

        citation_start = occurrence[
            "start"
        ]

        citation_end = occurrence[
            "end"
        ]

       

        start = citation_start

        while start > 0:

            previous = main_response[
                start - 1
            ]

            if previous in ".!?":

                break

          
            if previous == "\n":

              
                before = main_response[
                    max(0, start - 3):start
                ]

                if "\n\n" in before:

                    break

            start -= 1

       

        claim = main_response[
            start:citation_end
        ].strip()

      
        claim = re.sub(
            r"^[\s>*\-•]+",
            "",
            claim
        ).strip()

        

        claim = normalize_whitespace(
            claim
        )
        # Remove citation marker from the claim itself.
        claim = re.sub(
            r"\s*\[\d+(?:\s*[-,]\s*\d+)*\]\s*$",
            "",
            claim
        ).strip()
       

        if not claim:
            continue

     

        if claim.startswith("#"):
            continue

       

        claims.append({
            "citation": citation_number,
            "claim": claim,
            "context": claim,
            "start": start,
            "end": citation_end,
        })

    return claims



def merge_same_citation_claims(claims):
    """
    Keep one claim per citation occurrence.

    We intentionally DO NOT merge different occurrences
    of the same citation because one paper may support
    multiple claims in the response.
    """

    return claims



def parse_response(text: str):
    """
    Parse a complete normal AI-generated response.

    The response may contain:

        - introductions
        - explanations
        - bullet points
        - headings
        - code
        - uncited text
        - cited claims
        - references

    Only citation-related information is extracted.
    """

    if not text:

        return {
            "response": text,
            "main_response": "",
            "reference_heading": None,
            "references": {},
            "citations": [],
            "claims": [],
            "total_citations": 0,
            "total_references": 0,
            "total_claims": 0,
        }


    (
        main_response,
        reference_section,
        reference_heading,
    ) = split_response_and_references(
        text
    )

   
    citations = extract_citations(
        main_response
    )

   

    references = extract_references(
        reference_section
    )

  

    claims = extract_claims(
        main_response
    )

   

    enriched_claims = []

    for claim in claims:

        citation_number = claim[
            "citation"
        ]

        reference = references.get(
            citation_number
        )

        enriched = {
            "citation": f"[{citation_number}]",
            "reference_number": citation_number,
            "claim": claim["claim"],
            "context": claim["context"],
            "reference": reference,
            "reference_found": reference is not None,
        }

        enriched_claims.append(
            enriched
        )

    return {
        "response": text,
        "main_response": main_response,
        "reference_heading": reference_heading,
        "references": references,
        "citations": citations,
        "claims": enriched_claims,
        "total_citations": len(citations),
        "total_references": len(references),
        "total_claims": len(enriched_claims),
    }



# TEST RESPONSE


if __name__ == "__main__":

    response = """
Artificial intelligence has become an important part of
modern scientific research. Researchers now use machine
learning to analyze large datasets, automate repetitive
tasks, and identify patterns that may be difficult to
detect manually.

Deep learning has significantly improved performance
across tasks such as image recognition and speech
recognition [1].

The field has also introduced new model architectures.
The Transformer architecture introduced self-attention,
allowing models to capture relationships between tokens
without relying on recurrence [2].

However, these advances do not guarantee that generated
information is always correct. Hallucinations occur when
a language model generates statements that are not
supported by reliable evidence [3].

For scientific computing, Python has become an important
part of the scientific-computing ecosystem, with NumPy
providing core numerical array functionality [4].

There are also many practical applications of these
technologies in research, including data analysis,
simulation, and automation.

## References

[1] LeCun, Y., Bengio, Y., & Hinton, G. Deep learning.
Nature, 2015.

[2] Vaswani, A., Shazeer, N., Parmar, N., et al.
Attention Is All You Need. NeurIPS, 2017.

[3] Ji, Z., Lee, N., Frieske, R., et al.
Survey of Hallucination in Natural Language Generation.
ACM Computing Surveys, 2023.

[4] Harris, C. R., Millman, K. J., van der Walt, S. J.,
et al. Array programming with NumPy. Nature, 2020.
"""

    result = parse_response(
        response
    )

    print()
    print("=" * 80)
    print("FULL RESPONSE PARSER TEST")
    print("=" * 80)

    print()

    print(
        "TOTAL CITATIONS:",
        result["total_citations"]
    )

    print(
        "TOTAL REFERENCES:",
        result["total_references"]
    )

    print(
        "TOTAL CITED CLAIMS:",
        result["total_claims"]
    )

    print()
    print("=" * 80)
    print("CITED CLAIMS")
    print("=" * 80)

    for item in result["claims"]:

        print()
        print("Citation:")
        print(
            item["citation"]
        )

        print(
            "Reference number:"
        )

        print(
            item["reference_number"]
        )

        print("Claim:")

        print(
            item["claim"]
        )

        print("Context:")

        print(
            item["context"]
        )

        print(
            "Reference found:"
        )

        print(
            item["reference_found"]
        )

        print("Reference:")

        print(
            item["reference"]
        )

    print()
    print("=" * 80)
    print("REFERENCES")
    print("=" * 80)

    for number, reference in result[
        "references"
    ].items():

        print()
        print(
            f"[{number}]"
        )

        print(
            reference
        )

    print()
    print("=" * 80)
    print("PARSER INTERNAL CHECK")
    print("=" * 80)

    print()

    print(
        "Reference heading:",
        result["reference_heading"]
    )

    print()

    print("Main response preview:")

    print(
        result["main_response"][:1000]
    )

    print()

    print(
        "Reference section preview:"
    )

    (
        _,
        reference_section,
        _
    ) = split_response_and_references(
        response
    )

    print(
        reference_section[:1000]
    )