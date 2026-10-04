# =========================================================
# final_verdict.py
#
# Final decision layer for citation hallucination detection.
#
# Pipeline:
#
# Citation
#    ↓
# Candidate retrieval
#    ↓
# Source retrieval
#    ↓
# Evidence retrieval
#    ↓
# Gemini claim verification
#    ↓
# FINAL VERDICT
# =========================================================

from typing import Dict, Any




MIN_TITLE_SIMILARITY = 60


EXACT_THRESHOLD = 7.25
MINOR_THRESHOLD = 1.25



VALID_VERDICTS = {
    "verified",
    "partially_supported",
    "unsupported",
    "contradicted",
    "citation_mismatch",
    "source_not_found",
    "no_evidence",
    "verification_error",
}


def evaluate_paper_match(
    candidate: Dict[str, Any] | None
):
    """
    Determine how confidently the retrieved candidate
    matches the submitted citation.

    Returns a normalized result.
    """

    if not candidate:

        return {
            "matched": False,
            "confidence": 0,
            "reason": "No candidate paper was found."
        }

    title_similarity = float(
        candidate.get(
            "title_similarity",
            0
        )
        or 0
    )

    author_similarity = float(
        candidate.get(
            "author_similarity",
            0
        )
        or 0
    )

    word_overlap = float(
        candidate.get(
            "word_overlap",
            0
        )
        or 0
    )

    

    if title_similarity >= 90:

        confidence = 100

    elif title_similarity >= 80:

        confidence = 90

    elif title_similarity >= 70:

        confidence = 80

    elif title_similarity >= MIN_TITLE_SIMILARITY:

        confidence = 70

    else:

        confidence = max(
            0,
            title_similarity
        )


    if title_similarity >= 70:

        if author_similarity >= 80:

            confidence += 5

        elif author_similarity >= 50:

            confidence += 2

    confidence = min(
        100,
        round(confidence)
    )

    matched = (
        title_similarity
        >= MIN_TITLE_SIMILARITY
    )

    if matched:

        reason = (
            "The retrieved paper has sufficient "
            "title similarity to the submitted citation."
        )

    else:

        reason = (
            "The retrieved paper does not have "
            "sufficient title similarity to the "
            "submitted citation."
        )

    return {
        "matched": matched,
        "confidence": confidence,
        "reason": reason
    }


def evaluate_claim_support(
    verification: Dict[str, Any] | None
):
    """
    Normalize the output from the Gemini verifier.

    This function does NOT ask Gemini anything.

    It only interprets the already-generated result.
    """

    if not verification:

        return {
            "status": "verification_error",
            "score": 0,
            "classification": "major",
            "reasoning": (
                "No claim verification result was returned."
            )
        }

    status = verification.get(
        "status"
    )

    if status == "llm_error":

        return {
            "status": "verification_error",
            "score": 0,
            "classification": "major",
            "reasoning": verification.get(
                "reasoning",
                "LLM verification failed."
            )
        }

    if status == "no_evidence":

        return {
            "status": "no_evidence",
            "score": 0,
            "classification": "major",
            "reasoning": verification.get(
                "reasoning",
                "No evidence was available."
            )
        }

    score = float(
        verification.get(
            "score",
            0
        )
        or 0
    )

    classification = verification.get(
        "classification",
        "major"
    )

    return {
        "status": "success",
        "score": score,
        "classification": classification,
        "reasoning": verification.get(
            "reasoning",
            ""
        )
    }




def generate_final_verdict(
    candidate: Dict[str, Any] | None,
    verification: Dict[str, Any] | None
):
    """
    Generate the final citation verdict.

    IMPORTANT:

    The final verdict is deterministic.

    Gemini is responsible for evaluating whether the
    retrieved evidence supports the claim.

    This function decides how that result combines
    with citation/paper matching.
    """

    
    paper_match = evaluate_paper_match(
        candidate
    )

    

    claim_support = evaluate_claim_support(
        verification
    )

   

    if not candidate:

        return {
            "verdict": "source_not_found",
            "severity": "major",

            "confidence": 0,

            "paper_match": paper_match,

            "claim_support": claim_support,

            "score": 0,

            "reasoning": (
                "The cited paper could not be "
                "identified in the scholarly sources."
            ),

            "recommendation": (
                "Verify the citation metadata manually."
            )
        }

    

    if not paper_match["matched"]:

        return {
            "verdict": "citation_mismatch",
            "severity": "major",

            "confidence": (
                paper_match["confidence"]
            ),

            "paper_match": paper_match,

            "claim_support": claim_support,

            "score": claim_support.get(
                "score",
                0
            ),

            "reasoning": (
                "The retrieved scholarly paper does not "
                "match the cited paper sufficiently. "
                "Therefore claim verification against "
                "this source cannot establish citation "
                "correctness."
            ),

            "recommendation": (
                "Check the citation title, authors, "
                "year, DOI, or other metadata."
            )
        }

   

    if claim_support["status"] == (
        "verification_error"
    ):

        return {
            "verdict": "verification_error",
            "severity": "unknown",

            "confidence": 0,

            "paper_match": paper_match,

            "claim_support": claim_support,

            "score": 0,

            "reasoning": claim_support[
                "reasoning"
            ],

            "recommendation": (
                "Retry claim verification."
            )
        }

   

    if claim_support["status"] == (
        "no_evidence"
    ):

        return {
            "verdict": "no_evidence",
            "severity": "major",

            "confidence": (
                paper_match["confidence"]
            ),

            "paper_match": paper_match,

            "claim_support": claim_support,

            "score": 0,

            "reasoning": (
                "The cited paper was identified, "
                "but the evidence retrieval stage "
                "did not find sufficiently relevant "
                "passages supporting the claim."
            ),

            "recommendation": (
                "Inspect the source paper manually "
                "or improve evidence retrieval."
            )
        }

   

    score = claim_support.get(
        "score",
        0
    )

    llm_classification = claim_support.get(
        "classification",
        "unsupported"
    )

   

    if llm_classification == "contradicted":

        return {
            "verdict": "contradicted",
            "severity": "critical",

            "confidence": (
                paper_match["confidence"]
            ),

            "paper_match": paper_match,

            "claim_support": claim_support,

            "score": score,

            "reasoning": (
                claim_support["reasoning"]
            ),

            "recommendation": (
                "The cited source conflicts with "
                "the claim. Review or remove the claim."
            )
        }


    if (
        llm_classification == "supported"
        and score >= EXACT_THRESHOLD
    ):

        return {
            "verdict": "verified",
            "severity": "none",

            "confidence": (
                paper_match["confidence"]
            ),

            "paper_match": paper_match,

            "claim_support": claim_support,

            "score": score,

            "reasoning": (
                claim_support["reasoning"]
            ),

            "recommendation": (
                "Citation appears to be correctly "
                "supported by the source."
            )
        }

    

    if (
        llm_classification
        == "partially_supported"
    ):

        return {
            "verdict": "partially_supported",
            "severity": "minor",

            "confidence": (
                paper_match["confidence"]
            ),

            "paper_match": paper_match,

            "claim_support": claim_support,

            "score": score,

            "reasoning": (
                claim_support["reasoning"]
            ),

            "recommendation": (
                "Review the claim wording. "
                "The source supports only part "
                "of the statement."
            )
        }


    if (
        llm_classification == "unsupported"
    ):

        return {
            "verdict": "unsupported",
            "severity": "major",

            "confidence": (
                paper_match["confidence"]
            ),

            "paper_match": paper_match,

            "claim_support": claim_support,

            "score": score,

            "reasoning": (
                claim_support["reasoning"]
            ),

            "recommendation": (
                "The source does not provide "
                "sufficient evidence for the claim."
            )
        }



    return {
        "verdict": "unsupported",
        "severity": "major",

        "confidence": (
            paper_match["confidence"]
        ),

        "paper_match": paper_match,

        "claim_support": claim_support,

        "score": score,

        "reasoning": (
            claim_support["reasoning"]
        ),

        "recommendation": (
            "The citation could not be confidently "
            "verified."
        )
    }




def format_verdict(
    result: Dict[str, Any]
):
    """
    Convert final verdict into readable terminal output.
    """

    print()
    print("=" * 60)
    print("FINAL CITATION VERDICT")
    print("=" * 60)

    print(
        "VERDICT:",
        result.get(
            "verdict",
            "unknown"
        ).upper()
    )

    print(
        "SEVERITY:",
        result.get(
            "severity",
            "unknown"
        ).upper()
    )

    print(
        "CONFIDENCE:",
        f"{result.get('confidence', 0)}%"
    )

    print(
        "SUPPORT SCORE:",
        f"{result.get('score', 0)}/10"
    )

    print()
    print("REASONING")
    print("---------")

    print(
        result.get(
            "reasoning",
            ""
        )
    )

    print()
    print("RECOMMENDATION")
    print("--------------")

    print(
        result.get(
            "recommendation",
            ""
        )
    )

    print("=" * 60)



def build_final_result(
    pipeline_result: Dict[str, Any]
):
    """
    Accept the combined result produced by the pipeline.

    Expected structure:

    {
        "candidate": {...},
        "verification": {...}
    }

    Returns the complete final verdict.
    """

    if not isinstance(
        pipeline_result,
        dict
    ):

        return {
            "verdict": "verification_error",
            "severity": "unknown",
            "confidence": 0,
            "score": 0,
            "reasoning": (
                "Invalid pipeline result."
            ),
            "recommendation": (
                "Check pipeline integration."
            )
        }

    candidate = pipeline_result.get(
        "candidate"
    )

    verification = pipeline_result.get(
        "verification"
    )

    return generate_final_verdict(
        candidate,
        verification
    )




if __name__ == "__main__":

    

    candidate = {

        "source": "crossref",

        "title": (
            "Array programming with NumPy"
        ),

        "authors": [
            "Charles R. Harris",
            "K. Jarrod Millman",
            "Stéfan J. van der Walt"
        ],

        "year": 2020,

        "doi": (
            "10.1038/s41586-020-2649-2"
        ),

        "title_similarity": 100,

        "author_similarity": 100,

        "word_overlap": 100,

        "ranking_score": 100
    }

   

    verification = {

        "status": "success",

        "llm_classification": "supported",

        "score": 10,

        "classification": "exact",

        "reasoning": (
            "The source explicitly states that "
            "NumPy is the primary array programming "
            "library for Python."
        ),

        "key_differences": [],

        "evidence": []
    }

    result = generate_final_verdict(
        candidate,
        verification
    )

    format_verdict(
        result
    )