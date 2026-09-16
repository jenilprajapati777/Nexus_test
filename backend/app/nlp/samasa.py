import re
from typing import List, Dict, Any

class SamasaEngine:
    """Rule-based Samasa (Compound Word) Decomposition Engine."""

    def __init__(self):
        # Known common Sanskrit compound prefixes and constituent patterns
        self.known_prefixes = [
            ("राज", "rāja", "Rāja (Royal/King) Tatpuruṣa"),
            ("महा", "mahā", "Mahā (Great) Karmadhāraya"),
            ("धर्म", "dharma", "Dharma Tatpuruṣa/Dvandva"),
            ("सत्य", "satya", "Satya Tatpuruṣa"),
            ("सर्व", "sarva", "Sarva (All) Karmadhāraya"),
            ("सु", "su", "Su (Good) Avyayībhāva"),
            ("दुर्", "dur", "Dur (Bad/Difficult) Avyayībhāva"),
            ("निर्", "nir", "Nir (Without) Avyayībhāva"),
            ("अति", "ati", "Ati (Excessive) Avyayībhāva"),
            ("यथा", "yathā", "Yathā (According to) Avyayībhāva"),
        ]

    def decompose(self, token_surface: str) -> List[Dict[str, Any]]:
        """Decomposes a compound token into constituent components if matched."""
        components = []
        if len(token_surface) < 5:
            return components

        # Test known prefixes
        for dev_pref, iast_pref, samasa_type in self.known_prefixes:
            if token_surface.startswith(dev_pref) and len(token_surface) > len(dev_pref):
                remainder = token_surface[len(dev_pref):]
                components.append({
                    "compound_type": samasa_type,
                    "constituents": [dev_pref, remainder],
                    "confidence": 0.88,
                    "rule_code": f"SAMASA_{samasa_type.split()[0].upper()}"
                })
            elif token_surface.lower().startswith(iast_pref) and len(token_surface) > len(iast_pref):
                remainder = token_surface[len(iast_pref):]
                components.append({
                    "compound_type": samasa_type,
                    "constituents": [iast_pref, remainder],
                    "confidence": 0.88,
                    "rule_code": f"SAMASA_{samasa_type.split()[0].upper()}"
                })

        return components
