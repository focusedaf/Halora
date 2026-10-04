import re
import requests
import trafilatura

from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity




print("Loading semantic retrieval model...")

retrieval_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Loading NLI verification model...")

nli_model = CrossEncoder(
    "cross-encoder/nli-deberta-v3-base"
)

print("Models loaded.")



def extract_urls(text: str):
    pattern = r'https?://[^\s<>"\']+'

    urls = re.findall(pattern, text)

    return [
        clean_url(url)
        for url in urls
    ]


def clean_url(url: str):
    return url.rstrip(".,;:)]}")




def extract_page(url: str):

    try:

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/154.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        )

        response.raise_for_status()

        html = response.text

      

        title_match = re.search(
            r"<title[^>]*>(.*?)</title>",
            html,
            re.IGNORECASE | re.DOTALL,
        )

        title = ""

        if title_match:

            title = re.sub(
                r"\s+",
                " ",
                title_match.group(1)
            ).strip()

        

        lower_html = html.lower()

        blocked_indicators = [
            "your request has been blocked",
            "access denied",
            "request blocked",
            "automated process",
            "automated request",
            "verify you are human",
            "captcha",
            "checking your browser",
            "unusual traffic",
            "bot detection",
            "security check",
            "cloudflare",
        ]

        for indicator in blocked_indicators:

            if indicator in lower_html:

                return {
                    "status": "blocked",
                    "title": title,
                    "text": None,
                    "status_code": response.status_code,
                }


        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            include_links=False,
            include_images=False,
            favor_precision=True,
        )

        if not extracted:

            return {
                "status": "unreachable",
                "title": title,
                "text": None,
                "status_code": response.status_code,
            }

        extracted = extracted.strip()

        if len(extracted) < 100:

            return {
                "status": "unreachable",
                "title": title,
                "text": None,
                "status_code": response.status_code,
            }

        return {
            "status": "success",
            "title": title,
            "text": extracted[:50000],
            "status_code": response.status_code,
        }

    except requests.exceptions.Timeout:

        return {
            "status": "unreachable",
            "title": None,
            "text": None,
            "status_code": None,
        }

    except requests.exceptions.ConnectionError:

        return {
            "status": "unreachable",
            "title": None,
            "text": None,
            "status_code": None,
        }

    except requests.exceptions.HTTPError:

        return {
            "status": "unreachable",
            "title": None,
            "text": None,
            "status_code": (
                response.status_code
                if "response" in locals()
                else None
            ),
        }

    except Exception as e:

        print("Extraction error:", e)

        return {
            "status": "unreachable",
            "title": None,
            "text": None,
            "status_code": None,
        }




def extract_claim(text: str, url: str):

    position = text.find(url)

    if position == -1:

        return text.strip()[:500]

    before_url = text[:position].strip()

    if not before_url:
        return ""

    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        before_url
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    if sentences:

        return sentences[-1]

    return before_url[:500]




def split_into_passages(text: str):

    paragraphs = re.split(
        r"\n{2,}",
        text
    )

    passages = []

    for paragraph in paragraphs:

        paragraph = re.sub(
            r"\s+",
            " ",
            paragraph
        ).strip()

        if len(paragraph) < 50:
            continue

       
        if len(paragraph) > 1500:

            sentences = re.split(
                r"(?<=[.!?])\s+",
                paragraph
            )

            current = ""

            for sentence in sentences:

                if len(current) + len(sentence) > 1200:

                    if current:
                        passages.append(
                            current.strip()
                        )

                    current = sentence

                else:

                    current += " " + sentence

            if current:
                passages.append(
                    current.strip()
                )

        else:

            passages.append(
                paragraph
            )

    return passages




def find_evidence(
    claim: str,
    source: str,
    top_k: int = 3
):

    passages = split_into_passages(
        source
    )

    if not passages:

        return []

  
    claim_embedding = retrieval_model.encode(
        [claim],
        normalize_embeddings=True
    )

    passage_embeddings = retrieval_model.encode(
        passages,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    similarities = cosine_similarity(
        claim_embedding,
        passage_embeddings
    )[0]

    ranked_indices = similarities.argsort()[::-1]

    results = []

    for index in ranked_indices[:top_k]:

        results.append({
            "text": passages[index],
            "similarity": float(
                similarities[index]
            )
        })

    return results




def verify_claim(
    claim: str,
    evidence: list
):

    if not evidence:

        return {
            "status": "unsupported",
            "confidence": 0,
            "reason": "No relevant evidence was found.",
            "evidence": None,
        }

    best_result = None

    for item in evidence:

        passage = item["text"]

        scores = nli_model.predict(
            [(claim, passage)]
        )

       
        scores = scores[0]

     
        exp_scores = __import__("numpy").exp(
            scores - max(scores)
        )

        probabilities = (
            exp_scores / exp_scores.sum()
        )

        labels = {}

        for index, label in enumerate(
            nli_model.model.config.id2label.values()
        ):

            labels[label.lower()] = float(
                probabilities[index]
            )

        entailment = labels.get(
            "entailment",
            0
        )

        contradiction = labels.get(
            "contradiction",
            0
        )

        neutral = labels.get(
            "neutral",
            0
        )

        result = {
            "passage": passage,
            "entailment": entailment,
            "contradiction": contradiction,
            "neutral": neutral,
            "similarity": item["similarity"],
        }

        if (
            best_result is None
            or entailment > best_result["entailment"]
        ):

            best_result = result

    entailment = best_result["entailment"]
    contradiction = best_result["contradiction"]
    neutral = best_result["neutral"]

    

    if (
        entailment >= 0.70
        and entailment > contradiction
    ):

        status = "supported"

        confidence = round(
            entailment * 100
        )

        reason = (
            "The source evidence supports "
            "the cited claim."
        )

    elif (
        contradiction >= 0.60
        and contradiction > entailment
    ):

        status = "unsupported"

        confidence = round(
            contradiction * 100
        )

        reason = (
            "The source evidence contradicts "
            "the cited claim."
        )

    else:

        status = "partial"

        confidence = round(
            max(
                entailment,
                neutral
            ) * 100
        )

        reason = (
            "The source contains related "
            "information, but it does not "
            "clearly establish the claim."
        )

    return {
        "status": status,
        "confidence": confidence,
        "reason": reason,
        "evidence": best_result["passage"],
        "entailment": round(
            entailment * 100
        ),
        "contradiction": round(
            contradiction * 100
        ),
        "neutral": round(
            neutral * 100
        ),
    }



def check_citation(
    text: str,
    url: str
):

    claim = extract_claim(
        text,
        url
    )

    page = extract_page(url)

  

    if page["status"] == "blocked":

        return {
            "url": url,
            "claim": claim,
            "status": "blocked",
            "confidence": 0,
            "source_title": page["title"],
            "evidence": None,
            "message": (
                "The source blocked automated "
                "access. The citation could "
                "not be verified."
            ),
        }

    
    if page["status"] == "unreachable":

        return {
            "url": url,
            "claim": claim,
            "status": "unreachable",
            "confidence": 0,
            "source_title": page["title"],
            "evidence": None,
            "message": (
                "The source could not be "
                "accessed or did not contain "
                "usable text."
            ),
        }

    

    evidence = find_evidence(
        claim,
        page["text"],
        top_k=3
    )

   

    verification = verify_claim(
        claim,
        evidence
    )

    return {
        "url": url,
        "claim": claim,
        "status": verification["status"],
        "confidence": verification["confidence"],
        "source_title": page["title"],
        "evidence": verification["evidence"],
        "entailment": verification["entailment"],
        "contradiction": verification["contradiction"],
        "neutral": verification["neutral"],
        "message": verification["reason"],
    }




def check_response(text: str):

    urls = extract_urls(text)

    if not urls:

        return {
            "score": 0,
            "citation_count": 0,
            "citations": [],
            "message": "No citations were found.",
        }

    results = []

    for url in urls:

        result = check_citation(
            text,
            url
        )

        results.append(result)

    

    verifiable = [
        result
        for result in results
        if result["status"]
        in {
            "supported",
            "partial",
            "unsupported",
        }
    ]

    if verifiable:

        score = round(
            sum(
                result["confidence"]
                for result in verifiable
            )
            / len(verifiable)
        )

    else:

        score = 0

    return {
        "score": score,
        "citation_count": len(results),
        "citations": results,
    }