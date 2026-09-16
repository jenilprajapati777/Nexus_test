import unicodedata
import re

DEVANAGARI_TO_IAST = {
    'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū', 'ऋ': 'ṛ', 'ॠ': 'ṝ',
    'ऌ': 'ḷ', 'ॡ': 'ḹ', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
    'ा': 'ā', 'ि': 'i', 'ी': 'ī', 'ु': 'u', 'ू': 'ū', 'ृ': 'ṛ', 'ॄ': 'ṝ',
    'ॢ': 'ḷ', 'ॣ': 'ḹ', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
    'ं': 'ṃ', 'ः': 'ḥ', 'ँ': 'm̐', '्': '', 'ऽ': "'",
    'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'ṅa',
    'च': 'ca', 'छ': 'cha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'ña',
    'ट': 'ṭa', 'ठ': 'ṭha', 'ड': 'ḍa', 'ढ': 'ḍha', 'ण': 'ṇa',
    'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
    'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
    'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va',
    'श': 'śa', 'ष': 'ṣa', 'स': 'sa', 'ह': 'ha',
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
    '।': '|', '॥': '||'
}

class UnicodeNormalizer:
    """Handles Unicode normalization, punctuation cleaning, and script transliteration."""

    @staticmethod
    def normalize_unicode(text: str) -> str:
        if not text:
            return ""
        normalized = unicodedata.normalize("NFC", text)
        normalized = re.sub(r'॥', ' ॥ ', normalized)
        normalized = re.sub(r'।', ' । ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    @staticmethod
    def strip_diacritics(text: str) -> str:
        """Strips IAST diacritics to basic ASCII for flexible matching (e.g. hitopadeśa -> hitopadesa)."""
        replacements = {
            'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṝ': 'r', 'ḷ': 'l', 'ḹ': 'l',
            'ṃ': 'm', 'ḥ': 'h', 'ṅ': 'n', 'ñ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n',
            'ś': 's', 'ṣ': 's'
        }
        res = text.lower()
        for k, v in replacements.items():
            res = res.replace(k, v)
        return res

    @staticmethod
    def detect_script(text: str) -> str:
        devanagari_count = len(re.findall(r'[\u0900-\u097F]', text))
        iast_count = len(re.findall(r'[āīūṛṝḷḹṃḥṅñṭḍṇśṣ]', text))
        if devanagari_count > 0:
            return "devanagari"
        elif iast_count > 0:
            return "iast"
        else:
            return "slp1"

    @staticmethod
    def devanagari_to_iast(text: str) -> str:
        result = []
        i = 0
        n = len(text)
        
        devanagari_consonants = set('कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')
        devanagari_vowels_matras = {
            'ा': 'ā', 'ि': 'i', 'ी': 'ī', 'ु': 'u', 'ू': 'ū', 'ृ': 'ṛ', 'ॄ': 'ṝ',
            'ॢ': 'ḷ', 'ॣ': 'ḹ', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au'
        }
        devanagari_independent_vowels = {
            'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū', 'ऋ': 'ṛ', 'ॠ': 'ṝ',
            'ऌ': 'ḷ', 'ॡ': 'ḹ', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au'
        }
        
        while i < n:
            ch = text[i]
            if ch in devanagari_independent_vowels:
                result.append(devanagari_independent_vowels[ch])
            elif ch in devanagari_consonants:
                next_ch = text[i+1] if i + 1 < n else ''
                base_consonant = DEVANAGARI_TO_IAST[ch][:-1]
                if next_ch == '्':
                    result.append(base_consonant)
                    i += 1
                elif next_ch in devanagari_vowels_matras:
                    result.append(base_consonant + devanagari_vowels_matras[next_ch])
                    i += 1
                else:
                    result.append(base_consonant + 'a')
            elif ch in DEVANAGARI_TO_IAST:
                result.append(DEVANAGARI_TO_IAST[ch])
            else:
                result.append(ch)
            i += 1
            
        return "".join(result)

    @staticmethod
    def iast_to_devanagari(text: str) -> str:
        text_clean = UnicodeNormalizer.strip_diacritics(text)
        replacements = [
            ('ai', 'ऐ'), ('au', 'औ'), ('ā', 'आ'), ('ī', 'ई'), ('ū', 'ऊ'),
            ('ṛ', 'ऋ'), ('ṝ', 'ॠ'), ('ḷ', 'ऌ'), ('ṃ', 'ं'), ('ḥ', 'ः'),
            ('kha', 'ख'), ('gha', 'घ'), ('ṅa', 'ङ'), ('cha', 'छ'), ('jha', 'झ'),
            ('ña', 'ञ'), ('ṭha', 'ठ'), ('ḍha', 'ढ'), ('ṇa', 'ण'), ('tha', 'थ'),
            ('dha', 'ध'), ('pha', 'फ'), ('bha', 'भ'), ('śa', 'श'), ('ṣa', 'ष'),
            ('ka', 'क'), ('ga', 'ग'), ('ca', 'च'), ('ja', 'ज'), ('ṭa', 'ट'),
            ('ḍa', 'ड'), ('ta', 'त'), ('da', 'द'), ('na', 'न'), ('pa', 'प'),
            ('ba', 'ब'), ('ma', 'म'), ('ya', 'य'), ('ra', 'र'), ('la', 'ल'),
            ('va', 'व'), ('sa', 'स'), ('ha', 'ह'), ('a', 'अ'), ('i', 'इ'), ('u', 'उ')
        ]
        res = text
        for src, target in replacements:
            res = res.replace(src, target)
        return res
