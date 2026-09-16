import re
from typing import List, Dict, Any, Optional

class MorphologicalAnalysis:
    def __init__(self, lemma: str, category: str, case_tense: str, number_person: str, rule_code: str):
        self.lemma = lemma
        self.category = category  # SUBANTA (noun/adj) or TINANTA (verb)
        self.case_tense = case_tense
        self.number_person = number_person
        self.rule_code = rule_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lemma": self.lemma,
            "category": self.category,
            "case_tense": self.case_tense,
            "number_person": self.number_person,
            "rule_code": self.rule_code
        }

class SanskritMorphologyEngine:
    """Rule-based Sanskrit Morphological Analyzer & Lemmatizer for Subanta and Tinanta forms."""

    def __init__(self):
        # Known Irregular/High-Frequency Sanskrit Dictionary mappings (Devanagari & IAST)
        self.lexicon = {
            # Verb paradigms
            "गच्छति": ("गम्", "TINANTA", "Lāṭ (Present)", "3rd Singular", "MORPH_VERB_01"),
            "गच्छन्ति": ("गम्", "TINANTA", "Lāṭ (Present)", "3rd Plural", "MORPH_VERB_02"),
            "गच्छसि": ("गम्", "TINANTA", "Lāṭ (Present)", "2nd Singular", "MORPH_VERB_03"),
            "गच्छामि": ("गम्", "TINANTA", "Lāṭ (Present)", "1st Singular", "MORPH_VERB_04"),
            "करोति": ("कृ", "TINANTA", "Lāṭ (Present)", "3rd Singular", "MORPH_VERB_05"),
            "कुर्वन्ति": ("कृ", "TINANTA", "Lāṭ (Present)", "3rd Plural", "MORPH_VERB_06"),
            "पश्यति": ("दृश्", "TINANTA", "Lāṭ (Present)", "3rd Singular", "MORPH_VERB_07"),
            "भवति": ("भू", "TINANTA", "Lāṭ (Present)", "3rd Singular", "MORPH_VERB_08"),
            "उवाच": ("वच्", "TINANTA", "Liṭ (Perfect)", "3rd Singular", "MORPH_VERB_09"),
            
            "gacchati": ("gam", "TINANTA", "Present", "3rd Singular", "MORPH_VERB_01"),
            "gacchanti": ("gam", "TINANTA", "Present", "3rd Plural", "MORPH_VERB_02"),
            "karoti": ("kṛ", "TINANTA", "Present", "3rd Singular", "MORPH_VERB_05"),
            "pasyati": ("dṛś", "TINANTA", "Present", "3rd Singular", "MORPH_VERB_07"),
            "uvāca": ("vac", "TINANTA", "Perfect", "3rd Singular", "MORPH_VERB_09"),
        }

        # Subanta Suffix Rules (Noun Declension stemmers)
        self.subanta_rules = [
            # Genitive Singular: -asya / -स्य -> base stem (e.g. kṛṣṇasya -> kṛṣṇa, rāmasya -> rāma)
            (r"(.*)स्य$", r"\1", "SUBANTA", "Genitive (6th)", "Singular", "MORPH_SUB_GEN_SG"),
            (r"(.*)asya$", r"\1a", "SUBANTA", "Genitive (6th)", "Singular", "MORPH_SUB_GEN_SG_IAST"),
            
            # Instrumental Singular: -eṇa / -ेण / -ena -> base stem (e.g. rāmeṇa -> rāma)
            (r"(.*)ेण$", r"\1अ", "SUBANTA", "Instrumental (3rd)", "Singular", "MORPH_SUB_INST_SG"),
            (r"(.*)eṇa$", r"\1a", "SUBANTA", "Instrumental (3rd)", "Singular", "MORPH_SUB_INST_SG_IAST"),
            (r"(.*)ena$", r"\1a", "SUBANTA", "Instrumental (3rd)", "Singular", "MORPH_SUB_INST_SG_IAST2"),
            
            # Ablative Singular: -āt / -ात् -> base stem (e.g. dharmāt -> dharma)
            (r"(.*)ात्$", r"\1अ", "SUBANTA", "Ablative (5th)", "Singular", "MORPH_SUB_ABL_SG"),
            (r"(.*)āt$", r"\1a", "SUBANTA", "Ablative (5th)", "Singular", "MORPH_SUB_ABL_SG_IAST"),
            
            # Dative Singular: -āya / -ाय -> base stem (e.g. rāmāya -> rāma)
            (r"(.*)ाय$", r"\1अ", "SUBANTA", "Dative (4th)", "Singular", "MORPH_SUB_DAT_SG"),
            (r"(.*)āya$", r"\1a", "SUBANTA", "Dative (4th)", "Singular", "MORPH_SUB_DAT_SG_IAST"),
            
            # Locative Plural: -eṣu / -ेेषु / -esu -> base stem (e.g. lokeṣu -> loka)
            (r"(.*)ेषु$", r"\1अ", "SUBANTA", "Locative (7th)", "Plural", "MORPH_SUB_LOC_PL"),
            (r"(.*)eṣu$", r"\1a", "SUBANTA", "Locative (7th)", "Plural", "MORPH_SUB_LOC_PL_IAST"),
            
            # Nominative Plural: -āḥ / -ाः -> base stem (e.g. devāḥ -> deva)
            (r"(.*)ाः$", r"\1अ", "SUBANTA", "Nominative (1st)", "Plural", "MORPH_SUB_NOM_PL"),
            (r"(.*)āḥ$", r"\1a", "SUBANTA", "Nominative (1st)", "Plural", "MORPH_SUB_NOM_PL_IAST"),
            
            # Accusative Singular: -am / -म् -> base stem (e.g. pustakam -> pustaka)
            (r"(.*)म्$", r"\1", "SUBANTA", "Accusative (2nd)", "Singular", "MORPH_SUB_ACC_SG"),
            (r"(.*)am$", r"\1a", "SUBANTA", "Accusative (2nd)", "Singular", "MORPH_SUB_ACC_SG_IAST"),
        ]

    def analyze(self, surface_token: str) -> Optional[MorphologicalAnalysis]:
        """Performs morphological analysis and returns lemma + declension/conjugation info."""
        if not surface_token:
            return None

        # Check exact lexicon match
        if surface_token in self.lexicon:
            lemma, cat, case_tense, num_pers, rule = self.lexicon[surface_token]
            return MorphologicalAnalysis(
                lemma=lemma,
                category=cat,
                case_tense=case_tense,
                number_person=num_pers,
                rule_code=rule
            )

        # Check subanta declension rules
        for pattern, repl, cat, case_tense, num_pers, rule_code in self.subanta_rules:
            if re.search(pattern, surface_token):
                lemma = re.sub(pattern, repl, surface_token)
                if len(lemma) > 1:
                    return MorphologicalAnalysis(
                        lemma=lemma,
                        category=cat,
                        case_tense=case_tense,
                        number_person=num_pers,
                        rule_code=rule_code
                    )

        # Default fallback: self as lemma
        return MorphologicalAnalysis(
            lemma=surface_token,
            category="UNANALYZED",
            case_tense="Base/Stem",
            number_person="Singular",
            rule_code="MORPH_IDENTITY"
        )
