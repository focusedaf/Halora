from .citation_parser import parse_citation
from .response_parser import parse_response
from .source_retriever import retrieve_candidate_source
from .evidence_retriever import retrieve_evidence
from .claim_verifier import verify_claim
from .retrieval import retrieve_candidate



DEFAULT_TOP_K = 5




def safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    """

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def safe_dict(value):
    """
    Always return a dictionary.

    Prevents errors such as:

        None.get(...)
    """

    if isinstance(value, dict):
        return value

    return {}


def safe_list(value):
    """
    Always return a list.
    """

    if isinstance(value, list):
        return value

    return []


def safe_string(value, default=""):
    """
    Safely convert a value to string.
    """

    if value is None:
        return default

    try:
        return str(value)

    except Exception:
        return default


def normalize_citation_number(value):
    """
    Normalize citation identifiers.

    Examples:

        1          -> "1"
        "1"        -> "1"
        "[1]"      -> "1"
        "[[1]]"    -> "1"
        " [ 1 ] "  -> "1"

    This prevents reference lookup failures caused by
    inconsistent citation formatting.
    """

    if value is None:
        return ""

    value = safe_string(
        value
    ).strip()


    while (
        value.startswith("[")
        and value.endswith("]")
    ):

        value = value[1:-1].strip()

    return value.strip()



def get_final_verdict(
    verification,
    evidence
):

    verification = safe_dict(
        verification
    )

    evidence = safe_list(
        evidence
    )

  

    if not verification:

        return {

            "verdict":
                "ERROR",

            "confidence":
                0,

            "score":
                0,

            "reason":
                "No verification result was produced."
        }

    

    score = safe_float(
        verification.get(
            "score",
            0
        )
    )

    score = max(
        0.0,
        min(
            10.0,
            score
        )
    )

   

    classification = safe_string(

        verification.get(
            "llm_classification"
        )

        or verification.get(
            "classification"
        )

        or "unknown"

    ).lower().strip()

  

    reasoning = safe_string(

        verification.get(
            "reasoning"
        )

        or verification.get(
            "reason"
        )

        or ""
    )

    

    status = safe_string(

        verification.get(
            "status"
        )

        or ""

    ).lower().strip()

   


    if status in {

        "llm_error",

        "error",

        "verification_error"
    }:

        return {

            "verdict":
                "ERROR",

            "confidence":
                0,

            "score":
                score,

            "llm_classification":
                classification,

            "reason":
                (
                    reasoning
                    or
                    "Claim verification failed."
                )
        }

   
    if not evidence:

        return {

            "verdict":
                "UNSUPPORTED",

            "confidence":
                0,

            "score":
                score,

            "llm_classification":
                classification,

            "reason":
                "No supporting evidence was retrieved."
        }


    if classification == "supported":

        verdict = "SUPPORTED"

    elif classification in {

        "partially_supported",

        "partially supported",

        "partial",

        "partially-supported"
    }:

        verdict = "PARTIALLY SUPPORTED"

    elif classification == "contradicted":

        verdict = "CONTRADICTED"

    elif classification == "unsupported":

        verdict = "UNSUPPORTED"

    

    elif score >= 8.5:

        verdict = "SUPPORTED"

    elif score >= 6.0:

        verdict = "PARTIALLY SUPPORTED"

    elif score >= 1.25:

        verdict = "UNSUPPORTED"

    else:

        verdict = "CONTRADICTED"

   
    confidence = round(
        min(
            100,
            score * 10
        ),
        2
    )

    return {

        "verdict":
            verdict,

        "confidence":
            confidence,

        "score":
            score,

        "llm_classification":
            classification,

        "reason":
            reasoning
    }




def build_retrieval_summary(
    retrieval
):

    retrieval = safe_dict(
        retrieval
    )

    if not retrieval:
        return None

    candidate = safe_dict(

        retrieval.get(
            "candidate"
        )
    )

    candidates = safe_list(

        retrieval.get(
            "candidates"
        )
    )

    return {

        "status":
            retrieval.get(
                "status"
            ),

        "source":
            retrieval.get(
                "source"
            ),

        "candidate_count":
            len(candidates),

        "title_similarity":
            candidate.get(
                "title_similarity"
            ),

        "ranking_score":
            candidate.get(
                "ranking_score"
            )
    }




def build_source_summary(
    source
):

    source = safe_dict(
        source
    )

    if not source:
        return None

    return {

        "status":
            source.get(
                "status"
            ),

        "source":
            source.get(
                "source"
            ),

        "title":
            source.get(
                "title"
            ),

        "url":
            (
                source.get(
                    "final_url"
                )
                or
                source.get(
                    "url"
                )
            ),

        "content_type":
            source.get(
                "content_type"
            )
    }



def normalize_evidence(
    evidence
):

    if not isinstance(
        evidence,
        list
    ):

        return []

    normalized = []

    for item in evidence:

        if not isinstance(
            item,
            dict
        ):

            continue

        normalized.append({

            "rank":
                item.get(
                    "rank"
                ),

            "text":
                item.get(
                    "text",
                    ""
                ),

            "similarity":
                item.get(
                    "similarity",
                    0
                ),

            "coverage":
                item.get(
                    "coverage",
                    0
                )
        })

    return normalized



def build_verification_summary(
    verification
):

    verification = safe_dict(
        verification
    )

    if not verification:
        return None

    return {

        "status":
            verification.get(
                "status"
            ),

        "classification":
            (
                verification.get(
                    "llm_classification"
                )
                or
                verification.get(
                    "classification"
                )
            ),

        "score":
            verification.get(
                "score"
            ),

        "reasoning":
            (
                verification.get(
                    "reasoning",
                    ""
                )
                or
                verification.get(
                    "reason",
                    ""
                )
            ),

        "key_differences":
            safe_list(
                verification.get(
                    "key_differences"
                )
            )
    }




def build_candidate_summary(
    candidate
):

    candidate = safe_dict(
        candidate
    )

    if not candidate:
        return None

    return {

        "title":
            candidate.get(
                "title"
            ),

        "authors":
            candidate.get(
                "authors"
            ),

        "year":
            candidate.get(
                "year"
            ),

        "doi":
            candidate.get(
                "doi"
            ),

        "source":
            candidate.get(
                "source"
            ),

        "title_similarity":
            candidate.get(
                "title_similarity"
            ),

        "ranking_score":
            candidate.get(
                "ranking_score"
            )
    }



def verify_citation_claim(
    citation,
    claim,
    top_k=DEFAULT_TOP_K
):

    

    if not claim or not safe_string(
        claim
    ).strip():

        return {

            "status":
                "invalid_claim",

            "claim":
                claim,

            "citation":
                citation,

            "verification":
                None,

            "final_verdict": {

                "verdict":
                    "ERROR",

                "confidence":
                    0,

                "score":
                    0,

                "reason":
                    "Claim is empty."
            }
        }

    

    if not citation or not safe_string(
        citation
    ).strip():

        return {

            "status":
                "invalid_citation",

            "claim":
                claim,

            "citation":
                citation,

            "verification":
                None,

            "final_verdict": {

                "verdict":
                    "ERROR",

                "confidence":
                    0,

                "score":
                    0,

                "reason":
                    "Citation is empty."
            }
        }


    try:

        submitted = parse_citation(
            citation
        )

    except Exception as e:

        return {

            "status":
                "parse_error",

            "claim":
                claim,

            "citation":
                citation,

            "submitted":
                None,

            "verification":
                None,

            "final_verdict": {

                "verdict":
                    "ERROR",

                "confidence":
                    0,

                "score":
                    0,

                "reason":
                    (
                        "Citation parser failed: "
                        f"{e}"
                    )
            }
        }

    if not submitted:

        return {

            "status":
                "parse_error",

            "claim":
                claim,

            "citation":
                citation,

            "submitted":
                None,

            "verification":
                None,

            "final_verdict": {

                "verdict":
                    "ERROR",

                "confidence":
                    0,

                "score":
                    0,

                "reason":
                    "Citation could not be parsed."
            }
        }


    try:

        retrieval = retrieve_candidate(
            submitted
        )

    except Exception as e:

        return {

            "status":
                "retrieval_error",

            "claim":
                claim,

            "citation":
                citation,

            "submitted":
                submitted,

            "retrieval":
                None,

            "verification":
                None,

            "final_verdict": {

                "verdict":
                    "ERROR",

                "confidence":
                    0,

                "score":
                    0,

                "reason":
                    (
                        "Paper retrieval failed: "
                        f"{e}"
                    )
            }
        }

    retrieval_dict = safe_dict(
        retrieval
    )


    if (
        not retrieval_dict
        or
        retrieval_dict.get(
            "status"
        ) != "found"
    ):

        return {

            "status":
                "paper_not_found",

            "claim":
                claim,

            "citation":
                citation,

            "submitted":
                submitted,

            "retrieval":
                build_retrieval_summary(
                    retrieval_dict
                ),

            "verification":
                None,

            "final_verdict": {

                "verdict":
                    "PAPER NOT FOUND",

                "confidence":
                    0,

                "score":
                    0,

                "reason":
                    (
                        "No sufficiently matching "
                        "scholarly record was found."
                    )
            }
        }

   

    candidate = safe_dict(

        retrieval_dict.get(
            "candidate"
        )
    )

    if not candidate:

        return {

            "status":
                "paper_not_found",

            "claim":
                claim,

            "citation":
                citation,

            "submitted":
                submitted,

            "retrieval":
                build_retrieval_summary(
                    retrieval_dict
                ),

            "verification":
                None,

            "final_verdict": {

                "verdict":
                    "PAPER NOT FOUND",

                "confidence":
                    0,

                "score":
                    0,

                "reason":
                    (
                        "Retrieval succeeded but "
                        "no candidate was returned."
                    )
            }
        }



    try:

        source = retrieve_candidate_source(
            candidate
        )

    except Exception as e:

        return {

            "status":
                "source_retrieval_error",

            "claim":
                claim,

            "citation":
                citation,

            "submitted":
                submitted,

            "candidate":
                build_candidate_summary(
                    candidate
                ),

            "source":
                None,

            "verification":
                None,

            "final_verdict": {

                "verdict":
                    "SOURCE UNAVAILABLE",

                "confidence":
                    0,

                "score":
                    0,

                "reason":
                    (
                        "Source retrieval failed: "
                        f"{e}"
                    )
            }
        }

    source_dict = safe_dict(
        source
    )

    

    if (
        not source_dict
        or
        source_dict.get(
            "status"
        ) != "success"
    ):

        return {

            "status":
                "source_unavailable",

            "claim":
                claim,

            "citation":
                citation,

            "submitted":
                submitted,

            "candidate":
                build_candidate_summary(
                    candidate
                ),

            "source":
                build_source_summary(
                    source_dict
                ),

            "verification":
                None,

            "final_verdict": {

                "verdict":
                    "SOURCE UNAVAILABLE",

                "confidence":
                    0,

                "score":
                    0,

                "reason":
                    (
                        "The identified paper "
                        "could not be retrieved."
                    )
            }
        }



    try:

        evidence_result = retrieve_evidence(

            claim=claim,

            source=source_dict,

            top_k=top_k
        )

    except Exception as e:

        return {

            "status":
                "evidence_retrieval_error",

            "claim":
                claim,

            "citation":
                citation,

            "submitted":
                submitted,

            "candidate":
                build_candidate_summary(
                    candidate
                ),

            "source":
                build_source_summary(
                    source_dict
                ),

            "evidence":
                [],

            "verification":
                None,

            "final_verdict": {

                "verdict":
                    "UNSUPPORTED",

                "confidence":
                    0,

                "score":
                    0,

                "reason":
                    (
                        "Evidence retrieval failed: "
                        f"{e}"
                    )
            }
        }

    evidence_result_dict = safe_dict(
        evidence_result
    )

   

    if (
        not evidence_result_dict
        or
        evidence_result_dict.get(
            "status"
        ) != "success"
    ):

        return {

            "status":
                "no_evidence",

            "claim":
                claim,

            "citation":
                citation,

            "submitted":
                submitted,

            "candidate":
                build_candidate_summary(
                    candidate
                ),

            "source":
                build_source_summary(
                    source_dict
                ),

            "evidence":
                [],

            "verification":
                None,

            "final_verdict": {

                "verdict":
                    "UNSUPPORTED",

                "confidence":
                    0,

                "score":
                    0,

                "reason":
                    (
                        "No sufficiently relevant "
                        "evidence was retrieved."
                    )
            }
        }

 

    evidence = normalize_evidence(

        evidence_result_dict.get(
            "evidence"
        )
    )

    if not evidence:

        return {

            "status":
                "no_evidence",

            "claim":
                claim,

            "citation":
                citation,

            "submitted":
                submitted,

            "candidate":
                build_candidate_summary(
                    candidate
                ),

            "source":
                build_source_summary(
                    source_dict
                ),

            "evidence":
                [],

            "verification":
                None,

            "final_verdict": {

                "verdict":
                    "UNSUPPORTED",

                "confidence":
                    0,

                "score":
                    0,

                "reason":
                    (
                        "No supporting evidence "
                        "was retrieved from the source."
                    )
            }
        }

  

    source_title = (

        candidate.get(
            "title"
        )

        or

        source_dict.get(
            "title"
        )

        or
        ""
    )

    try:

        verification = verify_claim(

            claim=claim,

            source_title=source_title,

            evidence=evidence
        )

    except Exception as e:

        verification = {

            "status":
                "llm_error",

            "llm_classification":
                "error",

            "score":
                0,

            "reasoning":
                (
                    "Claim verification failed: "
                    f"{e}"
                ),

            "key_differences":
                []
        }

    verification = safe_dict(
        verification
    )

   

    final_verdict = get_final_verdict(

        verification=verification,

        evidence=evidence
    )

    

    return {

        "status":
            verification.get(
                "status",
                "unknown"
            ),

        "claim":
            claim,

        "citation":
            citation,

        "paper":
            build_candidate_summary(
                candidate
            ),

        "source":
            build_source_summary(
                source_dict
            ),

        "evidence":
            evidence,

        "verification":
            build_verification_summary(
                verification
            ),

        "final_verdict":
            final_verdict
    }




def verify_response(
    response,
    top_k=DEFAULT_TOP_K
):



    if not response or not safe_string(
        response
    ).strip():

        return {

            "status":
                "invalid_response",

            "response":
                response,

            "total_citations":
                0,

            "total_references":
                0,

            "total_cited_claims":
                0,

            "summary":
                {},

            "results":
                []
        }

  

    try:

        parsed = parse_response(
            response
        )

    except Exception as e:

        return {

            "status":
                "parser_error",

            "response":
                response,

            "total_citations":
                0,

            "total_references":
                0,

            "total_cited_claims":
                0,

            "summary":
                {},

            "results":
                [],

            "error":
                str(e)
        }

   

    parsed = safe_dict(
        parsed
    )

   

    citations = safe_list(

        parsed.get(
            "citations"
        )
    )

    references = parsed.get(
        "references"
    )

    if not isinstance(
        references,
        dict
    ):

        references = {}

    claims = safe_list(

        parsed.get(
            "claims"
        )
    )

  

    normalized_references = {}

    for key, value in references.items():

        normalized_key = normalize_citation_number(
            key
        )

        if not normalized_key:
            continue

        normalized_references[
            normalized_key
        ] = value

  

    results = []


    for item in claims:

        item = safe_dict(
            item
        )

       

        raw_citation = safe_string(

            item.get(
                "citation"
            )
        ).strip()

      

        citation_number = normalize_citation_number(

            raw_citation
        )

      
        claim = safe_string(

            item.get(
                "claim"
            )
        ).strip()

       

        context = safe_string(

            item.get(
                "context"
            )
            or
            claim
        ).strip()


        if not citation_number:

            continue


        reference = normalized_references.get(

            citation_number
        )

      

        if reference is not None:

            reference = safe_string(
                reference
            ).strip()

     
        if not reference:

            results.append({

                "citation":
                    f"[{citation_number}]",

                "reference_number":
                    citation_number,

                "claim":
                    claim,

                "context":
                    context,

                "reference_found":
                    False,

                "reference":
                    None,

                "metadata":
                    None,

                "verification":
                    None,

                "final_verdict": {

                    "verdict":
                        "REFERENCE NOT FOUND",

                    "confidence":
                        0,

                    "score":
                        0,

                    "reason":
                        (
                            "No matching reference "
                            f"was found for "
                            f"[{citation_number}]."
                        )
                }
            })

            continue


        try:

            metadata = parse_citation(
                reference
            )

        except Exception:

            metadata = None

        

        try:

            verification_result = (
                verify_citation_claim(

                    citation=reference,

                    claim=claim,

                    top_k=top_k
                )
            )

        except Exception as e:

            verification_result = {

                "status":
                    "pipeline_error",

                "claim":
                    claim,

                "citation":
                    reference,

                "verification":
                    None,

                "final_verdict": {

                    "verdict":
                        "ERROR",

                    "confidence":
                        0,

                    "score":
                        0,

                    "reason":
                        (
                            "Unexpected pipeline "
                            f"error: {e}"
                        )
                }
            }

        verification_result = safe_dict(

            verification_result
        )

      

        verification_data = safe_dict(

            verification_result.get(
                "verification"
            )
        )

        final_verdict = safe_dict(

            verification_result.get(
                "final_verdict"
            )
        )

       

        results.append({

            "citation":
                f"[{citation_number}]",

            "reference_number":
                citation_number,

            "claim":
                claim,

            "context":
                context,

            "reference_found":
                True,

            "reference":
                reference,

            "metadata":
                metadata,

            "verification":
                verification_data,

            "final_verdict":
                final_verdict
        })

  
    summary = {

        "verified":
            0,

        "partially_supported":
            0,

        "unsupported":
            0,

        "contradicted":
            0,

        "citation_mismatch":
            0,

        "source_not_found":
            0,

        "no_evidence":
            0,

        "verification_error":
            0,

        "reference_not_found":
            0
    }

   

    for result in results:

        result = safe_dict(
            result
        )

        final_verdict = safe_dict(

            result.get(
                "final_verdict"
            )
        )

        verification = safe_dict(

            result.get(
                "verification"
            )
        )

        verdict = safe_string(

            final_verdict.get(
                "verdict"
            )
        ).upper().strip()

        status = safe_string(

            verification.get(
                "status"
            )
        ).lower().strip()



        if verdict == "SUPPORTED":

            summary[
                "verified"
            ] += 1

      

        elif verdict == "PARTIALLY SUPPORTED":

            summary[
                "partially_supported"
            ] += 1

      

        elif verdict == "UNSUPPORTED":

            summary[
                "unsupported"
            ] += 1

        

        elif verdict == "CONTRADICTED":

            summary[
                "contradicted"
            ] += 1

      
        
      

        elif verdict == "PAPER NOT FOUND":

            summary[
                "source_not_found"
            ] += 1

      
      
      

        elif verdict == "SOURCE UNAVAILABLE":

            summary[
                "source_not_found"
            ] += 1

      
        
      

        elif verdict == "REFERENCE NOT FOUND":

            summary[
                "reference_not_found"
            ] += 1

      
     
      

        elif verdict == "ERROR":

            summary[
                "verification_error"
            ] += 1

      
       
      

        elif status == "no_evidence":

            summary[
                "no_evidence"
            ] += 1

      
      
      

        elif status in {

            "parse_error",

            "retrieval_error",

            "source_retrieval_error",

            "evidence_retrieval_error",

            "llm_error",

            "pipeline_error"
        }:

            summary[
                "verification_error"
            ] += 1

 

    return {

        "status":
            "success",

        "total_citations":
            len(citations),

        "total_references":
            len(normalized_references),

        "total_cited_claims":
            len(claims),

        "summary":
            summary,

        "results":
            results
    }




def print_response_result(
    result
):

    result = safe_dict(
        result
    )

    print()
    print("=" * 80)
    print("FULL AI RESPONSE VERIFICATION")
    print("=" * 80)

    print()

    print(
        "STATUS:",
        result.get(
            "status"
        )
    )

    print(
        "TOTAL CITATIONS:",
        result.get(
            "total_citations",
            0
        )
    )

    print(
        "TOTAL REFERENCES:",
        result.get(
            "total_references",
            0
        )
    )

    print(
        "TOTAL CITED CLAIMS:",
        result.get(
            "total_cited_claims",
            0
        )
    )

    print()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    summary = result.get(
        "summary"
    )

    summary = (
        summary
        if isinstance(
            summary,
            dict
        )
        else {}
    )

    for key, value in summary.items():

        print(
            f"{key}: {value}"
        )

    print()

    print("=" * 80)
    print("CITATION VERIFICATION RESULTS")
    print("=" * 80)

    results = safe_list(

        result.get(
            "results"
        )
    )

    for item in results:

        item = safe_dict(
            item
        )

        print()

        print(
            "Citation:",
            item.get(
                "citation"
            )
        )

        print(
            "Reference number:",
            item.get(
                "reference_number"
            )
        )

        print(
            "Claim:",
            item.get(
                "claim"
            )
        )

        print(
            "Reference found:",
            item.get(
                "reference_found"
            )
        )

        print(
            "Reference:",
            item.get(
                "reference"
            )
        )

        print(
            "Metadata:",
            item.get(
                "metadata"
            )
        )

        print()

        verdict = safe_dict(

            item.get(
                "final_verdict"
            )
        )

        print(
            "VERDICT:",
            verdict.get(
                "verdict",
                "UNKNOWN"
            )
        )

        print(
            "CONFIDENCE:",
            verdict.get(
                "confidence",
                0
            ),
            "%"
        )

        print(
            "SCORE:",
            verdict.get(
                "score",
                0
            ),
            "/ 10"
        )

        print(
            "REASON:",
            verdict.get(
                "reason",
                ""
            )
        )

        print(
            "-" * 80
        )

#test


if __name__ == "__main__":

    response = """

    Artificial intelligence has become an important part
    of modern scientific research. Researchers now use
    machine learning to analyze large datasets, automate
    repetitive tasks, and identify patterns that may be
    difficult to detect manually.

    Deep learning has significantly improved performance
    across tasks such as image recognition and speech
    recognition [1].

    The field has also introduced new model architectures.
    The Transformer architecture introduced self-attention,
    allowing models to capture relationships between tokens
    without relying on recurrence [2].

    However, these advances do not guarantee that generated
    information is always correct. Hallucinations occur
    when a language model generates statements that are not
    supported by reliable evidence [3].

    For scientific computing, Python has become an important
    part of the scientific-computing ecosystem, with NumPy
    providing core numerical array functionality [4].

    There are also many practical applications of these
    technologies in research, software development, and
    data analysis.

    ## References

    [1] LeCun, Y., Bengio, Y., & Hinton, G.
    Deep learning. Nature, 2015.

    [2] Vaswani, A., Shazeer, N., Parmar, N., et al.
    Attention Is All You Need. NeurIPS, 2017.

    [3] Ji, Z., Lee, N., Frieske, R., et al.
    Survey of Hallucination in Natural Language Generation.
    ACM Computing Surveys, 2023.

    [4] Harris, C. R., Millman, K. J., van der Walt, S. J.,
    et al. Array programming with NumPy. Nature, 2020.

    """

    result = verify_response(

        response=response,

        top_k=5
    )

    print_response_result(
        result
    )