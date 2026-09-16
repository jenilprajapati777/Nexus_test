import math
from typing import List, Dict, Any
from collections import defaultdict
from app.search.indexer import search_indexer
from app.nlp.normalizer import UnicodeNormalizer

class SearchEngine:
    """Sanskrit IR Query Execution Engine supporting Baseline and Enhanced Search modes."""

    def __init__(self):
        self.normalizer = UnicodeNormalizer()

    def search(
        self,
        query: str,
        mode: str = "enhanced", # baseline vs enhanced
        corpus_ids: List[str] = None,
        author_filter: str = None,
        chapter_filter: str = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """Executes search and returns ranked hits with match highlights and explanations."""
        if not query:
            return {"hits": [], "total": 0, "query": query, "mode": mode}

        query_terms = [t.lower() for t in query.strip().split() if t.strip()]
        doc_scores: Dict[str, float] = defaultdict(float)
        doc_match_details: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for term in query_terms:
            # 1. BASELINE SEARCH: Only check exact surface matches
            surface_matches = search_indexer.index["surface"].get(term, [])
            for hit in surface_matches:
                doc_id = hit["doc_id"]
                doc_scores[doc_id] += hit["score_weight"] * 1.5
                doc_match_details[doc_id].append(hit)

            if mode == "enhanced":
                # 2. ENHANCED SEARCH: Query across Transliterated, Normalized, Sandhi, Lemma, and Samasa fields
                
                # Devanagari / IAST Transliteration matches
                iast_term = self.normalizer.devanagari_to_iast(term)
                dev_term = self.normalizer.iast_to_devanagari(term)
                stripped_term = self.normalizer.strip_diacritics(term)

                term_candidates = set([
                    term, iast_term, dev_term, stripped_term,
                    term + "h", term + "ḥ", stripped_term + "h"
                ])

                for t_variant in term_candidates:
                    # Transliteration index
                    for hit in search_indexer.index["iast"].get(t_variant, []):
                        doc_id = hit["doc_id"]
                        doc_scores[doc_id] += hit["score_weight"]
                        doc_match_details[doc_id].append(hit)
                        
                    for hit in search_indexer.index["normalized"].get(t_variant, []):
                        doc_id = hit["doc_id"]
                        doc_scores[doc_id] += hit["score_weight"]
                        doc_match_details[doc_id].append(hit)

                    # Morphological Lemma matches
                    for hit in search_indexer.index["lemma"].get(t_variant, []):
                        doc_id = hit["doc_id"]
                        doc_scores[doc_id] += hit["score_weight"]
                        doc_match_details[doc_id].append(hit)

                    # Sandhi Split matches
                    for hit in search_indexer.index["sandhi"].get(t_variant, []):
                        doc_id = hit["doc_id"]
                        doc_scores[doc_id] += hit["score_weight"]
                        doc_match_details[doc_id].append(hit)

                    # Samasa Compound matches
                    for hit in search_indexer.index["samasa"].get(t_variant, []):
                        doc_id = hit["doc_id"]
                        doc_scores[doc_id] += hit["score_weight"]
                        doc_match_details[doc_id].append(hit)

        # Apply Filters & Deduplicate Match Highlights per Document
        ranked_results = []
        for doc_id, score in sorted(doc_scores.items(), key=lambda x: x[1], reverse=True):
            doc_data = search_indexer.doc_store.get(doc_id)
            if not doc_data:
                continue

            meta = doc_data["metadata"]
            
            # Apply Corpus / Author / Chapter filters
            if corpus_ids and meta.get("corpus_id") not in corpus_ids:
                continue
            if author_filter and author_filter.lower() not in meta.get("author", "").lower():
                continue
            if chapter_filter and chapter_filter.lower() not in meta.get("chapter", "").lower():
                continue

            matches = doc_match_details[doc_id]
            original_text = meta.get("original_text", "")

            # Sort and merge character offsets for highlighting
            unique_highlights = []
            seen_spans = set()
            for m in matches:
                span_key = (m["start_char"], m["end_char"])
                if span_key not in seen_spans:
                    seen_spans.add(span_key)
                    # Verify original text invariant
                    matched_str = original_text[m["start_char"]:m["end_char"]]
                    unique_highlights.append({
                        "start_char": m["start_char"],
                        "end_char": m["end_char"],
                        "matched_text": matched_str,
                        "matched_type": m.get("matched_type", "Exact"),
                        "matched_term": m.get("matched_term", "")
                    })

            # Create snippet snippet surrounding first match
            snippet = original_text[:300] + "..." if len(original_text) > 300 else original_text
            if unique_highlights:
                first_start = unique_highlights[0]["start_char"]
                snippet_start = max(0, first_start - 60)
                snippet_end = min(len(original_text), first_start + 140)
                snippet = ("..." if snippet_start > 0 else "") + original_text[snippet_start:snippet_end] + ("..." if snippet_end < len(original_text) else "")

            ranked_results.append({
                "doc_id": doc_id,
                "score": round(score, 3),
                "title": meta.get("title", "Untitled Document"),
                "author": meta.get("author", "Unknown"),
                "chapter": meta.get("chapter", "General"),
                "corpus_id": meta.get("corpus_id"),
                "original_text": original_text,
                "snippet": snippet,
                "highlights": unique_highlights,
                "match_count": len(matches),
                "match_details": matches
            })

        return {
            "query": query,
            "mode": mode,
            "total_hits": len(ranked_results),
            "hits": ranked_results[:top_k]
        }
