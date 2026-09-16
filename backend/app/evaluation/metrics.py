import math
from typing import List, Dict, Any

class EvaluationMetricsEngine:
    """Calculates IR metrics: Precision@K, Recall@K, F1, MRR, nDCG@K comparing Baseline vs Enhanced search."""

    @staticmethod
    def calculate_dcg(relevances: List[int], k: int) -> float:
        """Calculates Discounted Cumulative Gain (DCG@K)."""
        dcg = 0.0
        for i, rel in enumerate(relevances[:k], start=1):
            if i == 1:
                dcg += rel
            else:
                dcg += rel / math.log2(i)
        return dcg

    @staticmethod
    def calculate_ndcg(retrieved_doc_ids: List[str], gold_relevance: Dict[str, int], k: int = 10) -> float:
        """Calculates Normalized Discounted Cumulative Gain (nDCG@K)."""
        if not gold_relevance:
            return 0.0

        # Gain scores for retrieved docs
        relevances = [gold_relevance.get(doc_id, 0) for doc_id in retrieved_doc_ids[:k]]
        actual_dcg = EvaluationMetricsEngine.calculate_dcg(relevances, k)

        # Ideal DCG
        ideal_relevances = sorted(gold_relevance.values(), reverse=True)
        ideal_dcg = EvaluationMetricsEngine.calculate_dcg(ideal_relevances, k)

        if ideal_dcg == 0:
            return 0.0
        return round(actual_dcg / ideal_dcg, 4)

    @staticmethod
    def evaluate_query(retrieved_doc_ids: List[str], gold_relevance: Dict[str, int], k: int = 5) -> Dict[str, float]:
        """Calculates P@K, R@K, F1, MRR, nDCG@K for a single query result set."""
        if not retrieved_doc_ids or not gold_relevance:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "mrr": 0.0, "ndcg": 0.0}

        relevant_docs = set([doc_id for doc_id, score in gold_relevance.items() if score > 0])
        total_relevant = len(relevant_docs)

        top_k_retrieved = retrieved_doc_ids[:k]
        retrieved_relevant = [doc_id for doc_id in top_k_retrieved if doc_id in relevant_docs]

        # Precision@K
        precision = len(retrieved_relevant) / min(k, len(top_k_retrieved)) if top_k_retrieved else 0.0

        # Recall@K
        recall = len(retrieved_relevant) / total_relevant if total_relevant > 0 else 0.0

        # F1-Score
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # MRR (Mean Reciprocal Rank)
        mrr = 0.0
        for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
            if doc_id in relevant_docs:
                mrr = 1.0 / rank
                break

        # nDCG@K
        ndcg = EvaluationMetricsEngine.calculate_ndcg(retrieved_doc_ids, gold_relevance, k=k)

        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "mrr": round(mrr, 4),
            "ndcg": round(ndcg, 4)
        }

    @staticmethod
    def run_ablation_study(
        benchmark_queries: List[Dict[str, Any]],
        search_engine_instance
    ) -> Dict[str, Any]:
        """Executes Ablation Study comparing Baseline Search vs Enhanced Search across all benchmark queries."""
        baseline_metrics = {"precision": 0.0, "recall": 0.0, "f1": 0.0, "mrr": 0.0, "ndcg": 0.0}
        enhanced_metrics = {"precision": 0.0, "recall": 0.0, "f1": 0.0, "mrr": 0.0, "ndcg": 0.0}

        detailed_results = []
        n_queries = len(benchmark_queries)

        if n_queries == 0:
            return {
                "baseline_summary": baseline_metrics,
                "enhanced_summary": enhanced_metrics,
                "improvements": {},
                "query_details": []
            }

        for bq in benchmark_queries:
            q_text = bq["query_text"]
            gold_rel = bq["gold_relevance"]

            # Run Baseline Search
            b_res = search_engine_instance.search(query=q_text, mode="baseline", top_k=10)
            b_retrieved = [h["doc_id"] for h in b_res.get("hits", [])]
            b_eval = EvaluationMetricsEngine.evaluate_query(b_retrieved, gold_rel, k=5)

            # Run Enhanced Search
            e_res = search_engine_instance.search(query=q_text, mode="enhanced", top_k=10)
            e_retrieved = [h["doc_id"] for h in e_res.get("hits", [])]
            e_eval = EvaluationMetricsEngine.evaluate_query(e_retrieved, gold_rel, k=5)

            for key in baseline_metrics:
                baseline_metrics[key] += b_eval[key]
                enhanced_metrics[key] += e_eval[key]

            detailed_results.append({
                "query": q_text,
                "description": bq.get("description", ""),
                "baseline": b_eval,
                "enhanced": e_eval
            })

        # Average metrics across queries
        for key in baseline_metrics:
            baseline_metrics[key] = round(baseline_metrics[key] / n_queries, 4)
            enhanced_metrics[key] = round(enhanced_metrics[key] / n_queries, 4)

        # Percentage Improvements
        improvements = {}
        for key in baseline_metrics:
            b_val = baseline_metrics[key]
            e_val = enhanced_metrics[key]
            if b_val > 0:
                improvements[key] = round(((e_val - b_val) / b_val) * 100, 2)
            else:
                improvements[key] = 100.0 if e_val > 0 else 0.0

        return {
            "total_queries_evaluated": n_queries,
            "baseline_summary": baseline_metrics,
            "enhanced_summary": enhanced_metrics,
            "improvements_pct": improvements,
            "query_details": detailed_results
        }
