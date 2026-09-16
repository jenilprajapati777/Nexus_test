from typing import Dict, Any, List
from collections import defaultdict
from app.nlp.normalizer import UnicodeNormalizer

class SanskritSearchIndexer:
    """Inverted Indexer storing multi-layer linguistic tokens alongside exact original character offsets."""

    def __init__(self):
        # Inverted index structure: field -> term -> list of occurrences
        # occurrence: { "doc_id": str, "token_index": int, "start_char": int, "end_char": int, "matched_type": str, "rule_info": dict }
        self.index: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
            "surface": defaultdict(list),
            "normalized": defaultdict(list),
            "iast": defaultdict(list),
            "sandhi": defaultdict(list),
            "lemma": defaultdict(list),
            "samasa": defaultdict(list)
        }
        self.doc_store: Dict[str, Dict[str, Any]] = {}

    def index_document(self, doc_id: str, doc_metadata: Dict[str, Any], nlp_result: Dict[str, Any]):
        """Indexes a document's NLP output."""
        self.doc_store[doc_id] = {
            "metadata": doc_metadata,
            "nlp_result": nlp_result
        }

        tokens = nlp_result.get("tokens", [])
        for tok in tokens:
            token_idx = tok["token_index"]
            start_c = tok["start_char"]
            end_c = tok["end_char"]

            base_occurrence = {
                "doc_id": doc_id,
                "token_index": token_idx,
                "start_char": start_c,
                "end_char": end_c,
                "surface": tok["surface"]
            }

            # 1. Surface Indexing
            surf_key = tok["surface"].lower()
            self.index["surface"][surf_key].append({
                **base_occurrence,
                "matched_type": "Surface Match",
                "matched_term": tok["surface"],
                "score_weight": 3.0
            })

            # 2. Transliteration (IAST / Devanagari) Indexing
            iast_key = tok.get("iast", "").lower()
            if iast_key:
                self.index["iast"][iast_key].append({
                    **base_occurrence,
                    "matched_type": "Script Transliteration",
                    "matched_term": tok.get("iast"),
                    "score_weight": 2.5
                })
                # Strip diacritics variant (e.g. hitopadeśaḥ -> hitopadesah / hitopadesa)
                stripped_iast = UnicodeNormalizer.strip_diacritics(iast_key)
                if stripped_iast != iast_key:
                    self.index["iast"][stripped_iast].append({
                        **base_occurrence,
                        "matched_type": "IAST Normalization (Diacritics)",
                        "matched_term": stripped_iast,
                        "score_weight": 2.2
                    })
                
            dev_key = tok.get("devanagari", "").lower()
            if dev_key and dev_key != surf_key:
                self.index["normalized"][dev_key].append({
                    **base_occurrence,
                    "matched_type": "Devanagari Normalization",
                    "matched_term": tok.get("devanagari"),
                    "score_weight": 2.5
                })

            # 3. Morphological Lemma Indexing
            lemma_key = tok.get("lemma", "").lower()
            if lemma_key:
                morph_info = tok.get("morphology") or {}
                self.index["lemma"][lemma_key].append({
                    **base_occurrence,
                    "matched_type": "Morphological Lemma Match",
                    "matched_term": lemma_key,
                    "rule_info": morph_info,
                    "score_weight": 2.0
                })

            # 4. Sandhi Split Indexing
            sandhi_splits = tok.get("sandhi_splits", [])
            for split in sandhi_splits:
                rule_id = split["rule_id"]
                desc = split["description"]
                parts = split["split_parts"]
                for part in parts:
                    part_key = part.lower()
                    self.index["sandhi"][part_key].append({
                        **base_occurrence,
                        "matched_type": "Sandhi Split Expansion",
                        "matched_term": part_key,
                        "rule_info": {"rule_id": rule_id, "description": desc, "split_parts": parts},
                        "score_weight": 1.8
                    })

            # 5. Samasa Compound Indexing
            samasa_components = tok.get("samasa_components", [])
            for sam in samasa_components:
                rule_code = sam.get("rule_code")
                constits = sam.get("constituents", [])
                for part in constits:
                    part_key = part.lower()
                    self.index["samasa"][part_key].append({
                        **base_occurrence,
                        "matched_type": "Samasa Compound Decomposition",
                        "matched_term": part_key,
                        "rule_info": {"rule_code": rule_code, "compound_type": sam.get("compound_type"), "constituents": constits},
                        "score_weight": 1.5
                    })

# Global Index Instance
search_indexer = SanskritSearchIndexer()
