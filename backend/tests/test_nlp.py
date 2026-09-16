import pytest
from app.nlp.pipeline import SanskritNLPPipeline
from app.nlp.sandhi import SandhiEngine
from app.nlp.morphology import SanskritMorphologyEngine
from app.nlp.tokenizer import SanskritTokenizer

def test_sanskrit_tokenizer_offset_invariant():
    text = "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः । hitopadesa"
    tokens = SanskritTokenizer.tokenize(text)
    assert len(tokens) > 0
    for tok in tokens:
        # Verify character offset slice matches token surface exactly
        assert text[tok.start_char:tok.end_char] == tok.surface

def test_sandhi_splits():
    engine = SandhiEngine()
    splits = engine.split_token("hitopadeśa")
    assert len(splits) > 0
    split_parts = splits[0]["split_parts"]
    assert "hita" in split_parts or "उ" in split_parts or "u" in split_parts

def test_morphology_lemmatizer():
    engine = SanskritMorphologyEngine()
    analysis = engine.analyze("rāmeṇa")
    assert analysis is not None
    assert analysis.lemma == "rāma"
    assert analysis.case_tense == "Instrumental (3rd)"

def test_full_nlp_pipeline():
    pipeline = SanskritNLPPipeline()
    sample_text = "रामेण सह गच्छति हितोपदेशः ॥"
    result = pipeline.process_document(sample_text)
    assert result["original_text_preserved"] is True
    assert result["character_count"] == len(sample_text)
    assert len(result["tokens"]) > 0
