"""
ML Threshold Routing

Demonstrates routing based on model performance metrics:
- Evaluate model performance
- Route to: deploy / review / retrain based on thresholds

Question: How do I make deploy/retrain decisions in ML pipelines?
"""

from prefect import flow, task
import random


@task
def load_data() -> dict:
    """Load training and test data"""
    return {
        "X_train": [[1, 2], [3, 4], [5, 6]],
        "y_train": [0, 1, 0],
        "X_test": [[2, 3], [4, 5]],
        "y_test": [0, 1]
    }


@task
def train_model(data: dict, model_name: str) -> dict:
    """Train a model (simulated)"""
    print(f"Training {model_name}...")
    return {"name": model_name, "trained": True}


@task
def evaluate_model(model: dict, data: dict) -> dict:
    """Evaluate model and return metrics (simulated)"""
    random.seed(hash(model["name"]) % 100)
    accuracy = random.uniform(0.65, 0.95)
    f1 = random.uniform(0.60, 0.92)

    return {
        "model": model["name"],
        "accuracy": accuracy,
        "f1": f1
    }


@flow
def train_and_evaluate(model_name: str) -> dict:
    """Train and evaluate a single model"""
    data = load_data()
    model = train_model(data, model_name)
    metrics = evaluate_model(model, data)
    print(f"  {model_name}: accuracy={metrics['accuracy']:.3f}, f1={metrics['f1']:.3f}")
    return metrics


@flow
def deploy_model(metrics: dict) -> str:
    """Deploy model to production"""
    print(f"[DEPLOY] Deploying {metrics['model']} to production")
    print(f"  Accuracy: {metrics['accuracy']:.3f}")
    print(f"  F1 Score: {metrics['f1']:.3f}")
    return f"deployed:{metrics['model']}"


@flow
def request_review(metrics: dict) -> str:
    """Request human review"""
    print(f"[REVIEW] Requesting review for {metrics['model']}")
    print(f"  Metrics in uncertain range")
    return f"review:{metrics['model']}"


@flow
def trigger_retrain(metrics: dict) -> str:
    """Trigger retraining pipeline"""
    print(f"[RETRAIN] Scheduling retraining for {metrics['model']}")
    print(f"  Performance below threshold")
    return f"retrain:{metrics['model']}"


@flow
def ml_routing_pipeline(
    models: list[str],
    deploy_threshold: float = 0.85,
    review_threshold: float = 0.75
) -> str:
    """
    ML pipeline with metric-based routing.

    Thresholds:
    - f1 >= deploy_threshold -> Deploy
    - review_threshold <= f1 < deploy_threshold -> Human review
    - f1 < review_threshold -> Retrain
    """
    print("=" * 50)
    print("ML ROUTING PIPELINE")
    print(f"Deploy threshold: {deploy_threshold}")
    print(f"Review threshold: {review_threshold}")
    print("=" * 50)
    print()

    # Train and evaluate all models
    print("[1] Training models...")
    results = []
    for model_name in models:
        result = train_and_evaluate(model_name)
        results.append(result)
    print()

    # Select best model
    print("[2] Selecting best model...")
    best = max(results, key=lambda x: x["f1"])
    print(f"  Best: {best['model']} with F1={best['f1']:.3f}")
    print()

    # Route based on F1 score
    print("[3] Routing decision...")
    f1 = best["f1"]

    if f1 >= deploy_threshold:
        print(f"  F1 ({f1:.3f}) >= {deploy_threshold}: DEPLOY")
        result = deploy_model(best)
    elif f1 >= review_threshold:
        print(f"  F1 ({f1:.3f}) in [{review_threshold}, {deploy_threshold}): REVIEW")
        result = request_review(best)
    else:
        print(f"  F1 ({f1:.3f}) < {review_threshold}: RETRAIN")
        result = trigger_retrain(best)

    print()
    print("=" * 50)
    print("Pipeline complete!")
    print("=" * 50)

    return result


if __name__ == "__main__":
    result = ml_routing_pipeline(
        models=["random_forest", "gradient_boost", "logistic_reg"],
        deploy_threshold=0.85,
        review_threshold=0.75
    )
    print(f"\nFinal result: {result}")
