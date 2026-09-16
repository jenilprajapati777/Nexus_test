import pytest
from app.search.indexer import search_indexer
from app.search.engine import SearchEngine
from app.nlp.pipeline import SanskritNLPPipeline

def test_search_engine_baseline_and_enhanced():
    pipeline = SanskritNLPPipeline()
    text = "अस्ति मगधदेशे चम्पकभिधाना अरण्यानी । रामेण सह गच्छति हितोपदेशः ॥"
    nlp_res = pipeline.process_document(text)

    doc_id = "test_doc_001"
    meta = {
        "title": "Hitopadesha Sample",
        "author": "Narayana Pandit",
        "chapter": "Prathama",
        "original_text": text,
        "corpus_id": "c1"
    }

    search_indexer.index_document(doc_id=doc_id, doc_metadata=meta, nlp_result=nlp_res)

    engine = SearchEngine()

    # Enhanced search for Sandhi / Lemma query 'hitopadesa' or 'ramena'
    enhanced_res = engine.search(query="hitopadesa", mode="enhanced", corpus_ids=["c1"])
    assert enhanced_res["total_hits"] >= 1
    hit = enhanced_res["hits"][0]
    assert hit["doc_id"] == doc_id
    assert len(hit["highlights"]) > 0

    # Baseline search for surface term 'गच्छति'
    baseline_res = engine.search(query="गच्छति", mode="baseline", corpus_ids=["c1"])
    assert baseline_res["total_hits"] >= 1
