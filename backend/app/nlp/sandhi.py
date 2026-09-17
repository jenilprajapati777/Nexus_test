import re
from typing import List, Dict, Any, Tuple

class SandhiRule:
    def __init__(self, rule_id: str, category: str, pattern: str, replace_part1: str, replace_part2: str, description: str):
        self.rule_id = rule_id
        self.category = category # SVARA, VISARGA, VYANJANA
        self.pattern = pattern
        self.replace_part1 = replace_part1
        self.replace_part2 = replace_part2
        self.description = description

class SandhiEngine:
    """Rule-based Sanskrit Sandhi splitter and candidate generator. okay"""

    def __init__(self):
        self.rules: List[SandhiRule] = [
            # Svara Sandhi (Vowels) - Devanagari & IAST
            # Guna: a/ā + i/ī -> e (e.g. hitopadeśa, narendra)
            SandhiRule("SANDHI_SVARA_01", "SVARA", r"(.*[अ-हa-z])े([क-हa-z].*)", r"\1अ", r"इ\2", "Guṇa Sandhi: a/ā + i/ī -> e"),
            SandhiRule("SANDHI_SVARA_02", "SVARA", r"(.*[अ-हa-z])ो([क-हa-z].*)", r"\1अ", r"उ\2", "Guṇa Sandhi: a/ā + u/ū -> o"),
            SandhiRule("SANDHI_SVARA_03", "SVARA", r"(.*[अ-हa-z])ा([क-हa-z].*)", r"\1अ", r"अ\2", "Dīrgha Sandhi: a/ā + a/ā -> ā"),
            
            # Yan Sandhi: i/ī + vowel -> y
            SandhiRule("SANDHI_SVARA_04", "SVARA", r"(.*[अ-हa-z])्य([आइईउऊऋएऐओऔa-z].*)", r"\1ि", r"\2", "Yaṇ Sandhi: i/ī + vowel -> y"),
            SandhiRule("SANDHI_SVARA_05", "SVARA", r"(.*[अ-हa-z])्व([आइईउऊऋएऐओऔa-z].*)", r"\1ु", r"\2", "Yaṇ Sandhi: u/ū + vowel -> v"),
            
            # Avagraha Sandhi: e/o + a -> e/o + ऽ
            SandhiRule("SANDHI_SVARA_06", "SVARA", r"(.*[अ-हa-z])ऽ([क-हa-z].*)", r"\1", r"अ\2", "Purvarupa Sandhi: e/o + ऽ -> e/o + a"),
            
            # Visarga Sandhi
            SandhiRule("SANDHI_VISARGA_01", "VISARGA", r"(.*[अ-हa-z])स्ते(.*)", r"\1ः", r"ते\2", "Visarga to s before t: ḥ + t -> st"),
            SandhiRule("SANDHI_VISARGA_02", "VISARGA", r"(.*[अ-हa-z])श्च(.*)", r"\1ः", r"च\2", "Visarga to ś before c: ḥ + c -> śc"),
            SandhiRule("SANDHI_VISARGA_03", "VISARGA", r"(.*[अ-हa-z])ो([गघङजझञडढणदधनबभमयरलवह].*)", r"\1ः", r"\2", "Visarga to o before voiced consonant"),
            SandhiRule("SANDHI_VISARGA_04", "VISARGA", r"(.*[अ-हa-z])र([अ-हa-z].*)", r"\1ः", r"\2", "Visarga to r before voiced sound"),
            
            # Vyanjana Sandhi (Consonant)
            SandhiRule("SANDHI_VYANJANA_01", "VYANJANA", r"(.*[अ-हa-z])च्छ(.*)", r"\1त्", r"श्रुत\2", "Chutva Sandhi: t + ś -> cch"),
            SandhiRule("SANDHI_VYANJANA_02", "VYANJANA", r"(.*[अ-हa-z])च्च(.*)", r"\1त्", r"च\2", "Schutva Sandhi: t + c -> cc"),
            SandhiRule("SANDHI_VYANJANA_03", "VYANJANA", r"(.*[अ-हa-z])ज्ज(.*)", r"\1त्", r"ज\2", "Schutva Sandhi: t + j -> jj"),
            
            # IAST Specific Sandhi Rules
            SandhiRule("SANDHI_IAST_01", "SVARA", r"(.*[a-z])e([a-z].*)", r"\1a", r"i\2", "Guṇa Sandhi IAST: a + i -> e"),
            SandhiRule("SANDHI_IAST_02", "SVARA", r"(.*[a-z])o([a-z].*)", r"\1a", r"u\2", "Guṇa Sandhi IAST: a + u -> o"),
            SandhiRule("SANDHI_IAST_03", "SVARA", r"(.*[a-z])ā([a-z].*)", r"\1a", r"a\2", "Dīrgha Sandhi IAST: a + a -> ā"),
            SandhiRule("SANDHI_IAST_04", "VISARGA", r"(.*[a-z])ste(.*)", r"\1ḥ", r"te\2", "Visarga IAST: ḥ + t -> st"),
            SandhiRule("SANDHI_IAST_05", "VISARGA", r"(.*[a-z])śca(.*)", r"\1ḥ", r"ca\2", "Visarga IAST: ḥ + c -> śc"),
        ]

    def split_token(self, token_surface: str) -> List[Dict[str, Any]]:
        """Generates candidate Sandhi splits for a given word token."""
        splits = []
        if len(token_surface) < 3:
            return splits

        for rule in self.rules:
            match = re.match(rule.pattern, token_surface, re.IGNORECASE)
            if match:
                part1 = match.expand(rule.replace_part1)
                part2 = match.expand(rule.replace_part2)
                
                # Filter out trivial splits
                if len(part1) > 0 and len(part2) > 0:
                    splits.append({
                        "rule_id": rule.rule_id,
                        "category": rule.category,
                        "description": rule.description,
                        "split_parts": [part1, part2],
                        "confidence": 0.85
                    })

        return splits
