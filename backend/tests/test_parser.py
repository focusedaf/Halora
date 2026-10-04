from citation_parser import parse_citation


citation = """
Harris et al. (2020), "Array programming with NumPy",
https://doi.org/10.1038/s41586-020-2649-2
"""


result = parse_citation(citation)

print("\nExtracted citation:")
print("-------------------")

for key, value in result.items():
    print(f"{key}: {value}")