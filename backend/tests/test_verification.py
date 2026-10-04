from citation_parser import parse_citation
from metadata import verify_citation

citation = """
Harris et al. (2020), "Array programming with NumPy",
https://doi.org/10.1038/s41586-020-2649-2
"""

submitted = parse_citation(citation)

result = verify_citation(submitted)


print("\nVERIFICATION")
print("------------")

print("Status:", result["status"])
print("Score:", result["score"])

print(
    "Crossref:",
    result["crossref_found"]
)

print(
    "OpenAlex:",
    result["openalex_found"]
)

print("\nMatches")
print("-------")

for key, value in result["matches"].items():
    print(
        f"{key}: {value}%"
    )

print("\nIssues")
print("------")

if result["issues"]:

    for issue in result["issues"]:
        print(
            f"- {issue}"
        )

else:
    print("- None")