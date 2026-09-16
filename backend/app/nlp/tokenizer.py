import re
from typing import List, Dict, Any

class OffsetToken:
    def __init__(self, surface: str, start_char: int, end_char: int, token_index: int):
        self.surface = surface
        self.start_char = start_char
        self.end_char = end_char
        self.token_index = token_index

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surface": self.surface,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "token_index": self.token_index
        }

class SanskritTokenizer:
    """Tokenizes Sanskrit text while preserving exact character start/end offsets in original text."""

    @staticmethod
    def tokenize(original_text: str) -> List[OffsetToken]:
        """Extracts tokens with exact char offsets matching original_text."""
        tokens: List[OffsetToken] = []
        if not original_text:
            return tokens

        # Regex for Devanagari words, Latin/IAST words, and numbers
        # Pattern captures continuous Sanskrit/word characters
        pattern = re.compile(r'[\u0900-\u097F\wāīūṛṝḷḹṃḥṅñṭḍṇśṣA-Za-z0-9]+')
        
        token_idx = 0
        for match in pattern.finditer(original_text):
            surface = match.group(0)
            start_char = match.start()
            end_char = match.end()

            # Verify offset invariant locally
            assert original_text[start_char:end_char] == surface, f"Offset mismatch: '{original_text[start_char:end_char]}' != '{surface}'"
            
            tokens.append(OffsetToken(
                surface=surface,
                start_char=start_char,
                end_char=end_char,
                token_index=token_idx
            ))
            token_idx += 1

        return tokens

    @staticmethod
    def split_sentences(original_text: str) -> List[Dict[str, Any]]:
        """Splits verses/sentences based on dandas (|, ||) or newlines with offsets."""
        sentences = []
        if not original_text:
            return sentences

        pattern = re.compile(r'[^।॥\n\r]+[।॥]?')
        sentence_idx = 0
        for match in pattern.finditer(original_text):
            text = match.group(0).strip()
            if text:
                sentences.append({
                    "sentence_index": sentence_idx,
                    "text": text,
                    "start_char": match.start(),
                    "end_char": match.end()
                })
                sentence_idx += 1

        return sentences
