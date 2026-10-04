from metadata import (
    extract_doi,
    lookup_doi
)


url = (
    "https://doi.org/"
    "10.1038/s41586-020-2649-2"
)


doi = extract_doi(url)

print("DOI:")
print(doi)

print("\nMetadata:")

result = lookup_doi(doi)

print(result)