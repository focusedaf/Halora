import json
import os

from dotenv import load_dotenv
from google import genai



load_dotenv()

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set."
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)



SYSTEM_PROMPT = """
You are an expert academic citation verifier.

Your job is to determine whether a claim made in a research
report is actually supported by the cited source paper.

Evaluate ONLY the provided source evidence.
Do not rely on your own knowledge.

IMPORTANT RULES:

1. Correct citation metadata does NOT mean the claim is correct.

2. SUPPORTED:
   The source explicitly states, demonstrates, reports, or
   logically establishes the claim.

3. PARTIALLY_SUPPORTED:
   The source supports only part of the claim, or the claim
   is somewhat stronger or broader than what the source establishes.

4. UNSUPPORTED:
   The source does not provide evidence for the claim.

5. CONTRADICTED:
   The source explicitly conflicts with the claim.

6. Do not invent evidence.

7. Do not use outside knowledge.

8. Semantic similarity alone does not prove factual support.

9. Quantitative claims require actual evidence from the source.
   If a claimed number, percentage, measurement, or result is
   not present in the evidence, treat it as unsupported or
   partially supported.

10. Carefully distinguish between what the paper says and what
    the report claims the paper says.

SCORING:

10 = Fully supported.
9  = Very strongly supported; only trivial wording differences.
8  = Clearly supported but slightly broader or less precise.
7  = Mostly supported with a small qualification.
6  = Partially supported.
5  = Mixed evidence or significant missing information.
4  = Weak support.
3  = Mostly unsupported.
2  = Strongly unsupported.
1  = Almost completely unsupported.
0  = Contradicted, fabricated, or completely unrelated.

Return ONLY valid JSON:

{
    "score": number,
    "classification": "supported" | "partially_supported" | "unsupported" | "contradicted",
    "reasoning": "short explanation",
    "key_differences": ["difference 1", "difference 2"]
}
"""




def parse_response(text: str):

    text = text.strip()

   
    if text.startswith("```"):

        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    try:

        result = json.loads(text)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Gemini returned invalid JSON:\n{text}"
        ) from e

    required = {
        "score",
        "classification",
        "reasoning",
        "key_differences"
    }

    missing = required - set(result.keys())

    if missing:

        raise ValueError(
            f"Missing fields: {missing}"
        )

  

    try:

        score = float(
            result["score"]
        )

    except (
        TypeError,
        ValueError
    ):

        score = 0

    score = max(
        0,
        min(
            10,
            score
        )
    )

    result["score"] = round(
        score,
        2
    )

   

    valid = {
        "supported",
        "partially_supported",
        "unsupported",
        "contradicted"
    }

    if result["classification"] not in valid:

        result["classification"] = "unsupported"


    if not isinstance(
        result["key_differences"],
        list
    ):

        result["key_differences"] = [
            str(
                result["key_differences"]
            )
        ]

    return result




def classify_score(score: float):

    if score < 1.25:

        return "major"

    elif score < 7.25:

        return "minor"

    else:

        return "exact"




def verify_claim(
    claim: str,
    source_title: str,
    evidence: list
):

    if not claim or not claim.strip():

        return {
            "status": "error",
            "score": 0,
            "classification": "major",
            "reasoning": (
                "No claim was provided."
            ),
            "key_differences": [],
            "evidence": []
        }

    if not evidence:

        return {
            "status": "no_evidence",
            "score": 0,
            "classification": "major",
            "reasoning": (
                "No relevant evidence was found "
                "in the source."
            ),
            "key_differences": [],
            "evidence": []
        }



    evidence_blocks = []

    for index, item in enumerate(
        evidence,
        start=1
    ):

        passage = item.get(
            "text",
            ""
        )

        similarity = item.get(
            "similarity",
            "N/A"
        )

        evidence_blocks.append(
            f"""
SOURCE PASSAGE {index}
Semantic similarity: {similarity}

{passage}
"""
        )

    evidence_text = "\n".join(
        evidence_blocks
    )



    prompt = f"""
SOURCE PAPER:
{source_title}

CLAIM FROM THE RESEARCH REPORT:
{claim}

RELEVANT PASSAGES RETRIEVED FROM THE SOURCE:
{evidence_text}

TASK:

Determine whether the source actually supports the claim.

Check every important part of the claim.

Pay particular attention to:

- factual statements
- numbers
- percentages
- measurements
- causal relationships
- comparisons
- strong/generalized statements
- claims that may go beyond what the source says

Return ONLY the JSON object specified in the system instructions.
"""

   

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "temperature": 0,
                "response_mime_type": "application/json"
            }
        )

        response_text = response.text

        result = parse_response(
            response_text
        )

    except Exception as e:

        return {
            "status": "llm_error",
            "score": 0,
            "classification": "major",
            "reasoning": (
                f"Gemini verification failed: {e}"
            ),
            "key_differences": [],
            "evidence": evidence
        }


    score = result["score"]

    final_classification = classify_score(
        score
    )

    return {
        "status": "success",

        
        "llm_classification": (
            result["classification"]
        ),

       
        "score": score,

        
        "classification": final_classification,

        "reasoning": (
            result["reasoning"]
        ),

        "key_differences": (
            result["key_differences"]
        ),

        "evidence": evidence
    }



# TEST

if __name__ == "__main__":

    print(
        "Using Gemini model:",
        MODEL
    )

    claim = (
        "NumPy is the primary array programming "
        "library for the Python language."
    )

    source_title = (
        "Array programming with NumPy"
    )

    evidence = [
        {
            "text": """
            Array programming provides a powerful,
            compact and expressive syntax for accessing,
            manipulating and operating on data in vectors,
            matrices and higher-dimensional arrays.

            NumPy is the primary array programming
            library for the Python language.

            It has an essential role in research analysis
            pipelines in fields as diverse as physics,
            chemistry, astronomy, geoscience, biology,
            psychology, materials science, engineering,
            finance and economics.
            """,

            "similarity": 0.94
        }
    ]

    result = verify_claim(
        claim=claim,
        source_title=source_title,
        evidence=evidence
    )

    print()
    print("CLAIM VERIFICATION")
    print("------------------")

    print(
        "Status:",
        result["status"]
    )

    print(
        "LLM classification:",
        result.get(
            "llm_classification"
        )
    )

    print(
        "Score:",
        result["score"],
        "/ 10"
    )

    print(
        "Final classification:",
        result["classification"]
    )

    print()
    print("Reasoning:")
    print(
        result["reasoning"]
    )

    print()
    print("Key differences:")

    differences = result.get(
        "key_differences",
        []
    )

    if differences:

        for difference in differences:

            print(
                "-",
                difference
            )

    else:

        print(
            "- None"
        )