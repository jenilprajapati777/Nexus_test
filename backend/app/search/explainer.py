from typing import Dict, Any, List

class MatchExplainer:
    """Generates detailed linguistic explanation traces for why a Sanskrit search result matched."""

    @staticmethod
    def explain_hit(hit_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Formats comprehensive rule-by-rule explanation trace."""
        doc_id = hit_data.get("doc_id")
        score = hit_data.get("score")
        matches = hit_data.get("match_details", [])

        explanation_steps = []
        rule_breakdown = {}

        for idx, m in enumerate(matches, 1):
            matched_type = m.get("matched_type", "Surface")
            matched_term = m.get("matched_term", "")
            surface = m.get("surface", "")
            start_c = m.get("start_char")
            end_c = m.get("end_char")
            rule_info = m.get("rule_info") or {}

            step_desc = f"Match #{idx}: Token '{surface}' at offset [{start_c}:{end_c}] matched query term '{matched_term}' via {matched_type}."
            
            detail_info = {
                "step": idx,
                "surface_token": surface,
                "matched_type": matched_type,
                "matched_term": matched_term,
                "start_char": start_c,
                "end_char": end_c,
                "rule_info": rule_info,
                "description": step_desc
            }

            if "Sandhi" in matched_type:
                detail_info["explanation"] = f"Sandhi rule applied: {rule_info.get('description', 'Sandhi Split')}. Split components: {rule_info.get('split_parts')}"
            elif "Morphological" in matched_type:
                detail_info["explanation"] = f"Morphological lemma matched: '{surface}' is an inflected form of stem '{rule_info.get('lemma')}'. Case/Tense: {rule_info.get('case_tense')}, Number: {rule_info.get('number_person')}."
            elif "Samasa" in matched_type:
                detail_info["explanation"] = f"Samasa Compound decomposed: '{surface}' decomposed into constituents: {rule_info.get('constituents')} ({rule_info.get('compound_type')})."
            else:
                detail_info["explanation"] = f"Exact surface form lexical match."

            explanation_steps.append(detail_info)

        return {
            "doc_id": doc_id,
            "query": query,
            "total_score": score,
            "total_matches": len(matches),
            "explanation_steps": explanation_steps
        }
