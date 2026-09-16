from typing import Dict, Any, List
from app.nlp.normalizer import UnicodeNormalizer
from app.nlp.tokenizer import SanskritTokenizer
from app.nlp.sandhi import SandhiEngine
from app.nlp.morphology import SanskritMorphologyEngine
from app.nlp.samasa import SamasaEngine

class SanskritNLPPipeline:
    """Sequential Sanskrit NLP Processor combining Unicode Normalization, Tokenization,
    Sandhi Splitting, Morphological Lemmatization, and Samasa Decomposition while
    preserving exact original text offsets."""

    def __init__(self):
        self.normalizer = UnicodeNormalizer()
        self.tokenizer = SanskritTokenizer()
        self.sandhi_engine = SandhiEngine()
        self.morphology_engine = SanskritMorphologyEngine()
        self.samasa_engine = SamasaEngine()

    def process_document(self, original_text: str) -> Dict[str, Any]:
        """Runs the complete NLP analysis pipeline over document text."""
        # 1. Normalize Unicode (for display/analysis reference)
        normalized_text = self.normalizer.normalize_unicode(original_text)
        script = self.normalizer.detect_script(original_text)

        # 2. Sentence & Verse tokenization with offsets
        sentences = self.tokenizer.split_sentences(original_text)

        # 3. Word Tokenization with exact char offsets
        raw_tokens = self.tokenizer.tokenize(original_text)

        # 4. Enrich each token with Sandhi, Morphology, Samasa, and Transliteration
        enriched_tokens = []
        for tok in raw_tokens:
            surface = tok.surface
            start_c = tok.start_char
            end_c = tok.end_char

            # Verify exact offset invariant
            assert original_text[start_c:end_c] == surface, f"Invariant Failure: '{original_text[start_c:end_c]}' != '{surface}'"

            # Transliteration
            iast_form = self.normalizer.devanagari_to_iast(surface) if script == "devanagari" else surface
            devanagari_form = self.normalizer.iast_to_devanagari(surface) if script == "iast" else surface

            # Sandhi Candidate Splits
            sandhi_splits = self.sandhi_engine.split_token(surface)

            # Morphological Lemmatization
            morph_analysis = self.morphology_engine.analyze(surface)
            lemma = morph_analysis.lemma if morph_analysis else surface

            # Samasa Decomposition
            samasa_components = self.samasa_engine.decompose(surface)

            enriched_tokens.append({
                "token_index": tok.token_index,
                "surface": surface,
                "start_char": start_c,
                "end_char": end_c,
                "script": script,
                "iast": iast_form,
                "devanagari": devanagari_form,
                "lemma": lemma,
                "morphology": morph_analysis.to_dict() if morph_analysis else None,
                "sandhi_splits": sandhi_splits,
                "samasa_components": samasa_components
            })

        return {
            "original_text_preserved": True,
            "script": script,
            "character_count": len(original_text),
            "word_count": len(enriched_tokens),
            "sentence_count": len(sentences),
            "sentences": sentences,
            "tokens": enriched_tokens
        }
