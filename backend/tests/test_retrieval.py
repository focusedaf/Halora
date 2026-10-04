from citation_parser import parse_citation
from retrieval import retrieve_candidate


citation = """
Harris et al. (2020), "Array programming with NumPy",
https://doi.org/10.1038/s41586-020-2649-2
"""

submitted = parse_citation(citation)

# Give retrieval access to the original citation text
submitted["raw_text"] = citation

result = retrieve_candidate(
    submitted
)

print("\nRETRIEVAL")
print("---------")

print(
    "Status:",
    result["status"]
)

print(
    "Source:",
    result["source"]
)

print("\nBEST CANDIDATE")
print("--------------")

candidate = result["candidate"]

if candidate:

    print(
        "Title:",
        candidate.get("title")
    )

    print(
        "Authors:",
        candidate.get("authors")
    )

    print(
        "Year:",
        candidate.get("year")
    )

    print(
        "DOI:",
        candidate.get("doi")
    )

    print(
        "Title similarity:",
        candidate.get("title_similarity")
    )

    print(
        "Author similarity:",
        candidate.get("author_similarity")
    )

    print(
        "Ranking score:",
        candidate.get("ranking_score")
    )

else:

    print("No candidate found.")