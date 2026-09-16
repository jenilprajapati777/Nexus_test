import pytest
from app.evaluation.metrics import EvaluationMetricsEngine

def test_metrics_calculation():
    retrieved = ["doc1", "doc2", "doc3", "doc4", "doc5"]
    gold_rel = {"doc1": 3, "doc3": 2, "doc7": 1}

    eval_res = EvaluationMetricsEngine.evaluate_query(retrieved, gold_rel, k=5)
    
    assert eval_res["precision"] > 0
    assert eval_res["recall"] > 0
    assert eval_res["f1"] > 0
    assert eval_res["mrr"] == 1.0 # doc1 is rank 1
    assert eval_res["ndcg"] > 0
