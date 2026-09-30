# ASI_2025 - Machine Learning Operations Course

An educational repository for teaching Machine Learning Operations (MLOps) and production ML engineering practices. This course covers the complete ML lifecycle from data processing through deployment and monitoring, with heavy emphasis on containerization, orchestration, and modern ML tooling.



The Playlist: https://www.youtube.com/playlist?list=PLOiItT5FLNRqN9DeGbnXpw2SMehnAXpax



## 📚 Course Overview

**Repository:** https://github.com/wodecki/ASI_2025

**Python Version:** 3.10-3.11

**Package Manager:** `uv` (mandatory)

### Primary Technologies

- **Containerization:** Docker, Kubernetes
- **Cloud Platform:** Google Cloud Platform (GCP)
- **Data Processing:** pandas, DuckDB, BigQuery
- **ML Frameworks:** MLFlow, AutoGluon, scikit-learn
- **Web Frameworks:** FastAPI, Streamlit
- **Monitoring:** MLFlow, WandB, Locust
- **LLM Integration:** OpenAI API

## 🗂️ Repository Structure

```
ASI_2025/
├── slides/                           # Course presentation materials
│   ├── 0. Introduction/
│   ├── 1. Set-up/
│   ├── 2. BigData/
│   ├── 3. Model Lifecycle/
│   ├── 4. Software Engineering/
│   ├── 5. ML Pipelines/
│   ├── 6. Containerization/
│   ├── 7. AutoML/
│   ├── 8. Experiment tracking/
│   ├── 9. Data and Model Drift/
│   ├── 10. Kubernetes and Kubeflow/
│   └── 11. AI Architecture Design/
└── src/                              # Hands-on code examples
    ├── 1. Set-up/
    └── 2. BigData/
        └── 1. Data/
            ├── 1. pandas_vs_duckdb/          # Performance comparison demo
            └── 2. BigQuery Iowa Transfer/     # GCP data pipeline tutorial
   └── ... to be continued ...
```

## 🎯 Learning Modules

### Module 0: Introduction
Introduction to MLOps concepts, course structure, and learning objectives.

### Module 1: Set-up
Development environment configuration, Python setup, and tooling introduction.

### Module 2: BigData
- **pandas vs DuckDB Performance Comparison** - Benchmark data processing at scale (100M-1B records)
- **BigQuery Data Transfer** - Import public datasets to GCP infrastructure
- Efficient data processing patterns
- Cloud storage optimization

**Key Demos:**
- `src/2. BigData/1. Data/1. pandas_vs_duckdb/` - Compare pandas and DuckDB on large datasets
- `src/2. BigData/1. Data/2. BigQuery Iowa Transfer/` - Transfer Iowa Liquor Sales dataset from Google Public Datasets

### Module 3: Model Lifecycle
CRISP-DM methodology, data understanding, preparation, and modeling workflows.

### Module 4: Software Engineering
Best practices for production ML code: version control, testing, documentation, and code quality.

### Module 5: ML Pipelines
Building reproducible ML pipelines, data versioning, and workflow orchestration.

### Module 6: Containerization
- Docker fundamentals
- Single and multi-container applications
- Volume management
- Production deployment patterns

### Module 7: AutoML
Automated machine learning with PyCaret and AutoGluon for rapid prototyping.

### Module 8: Experiment Tracking
Weights & Biases (WandB) integration for experiment management and model versioning.

### Module 9: Data and Model Drift
Monitoring model performance, detecting drift, and triggering retraining pipelines.

### Module 10: Kubernetes and Kubeflow
Container orchestration, scaling ML workloads, and Kubeflow pipelines.

### Module 11: AI Architecture Design
System design patterns, microservices architecture, and production ML systems.

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or 3.11
- Docker Desktop (for containerization modules)
- Google Cloud Platform account (for cloud modules)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wodecki/ASI_2025.git
   cd ASI_2025
   ```

2. **Install uv package manager:**
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or via pip (one-time)
   pip install uv
   ```

3. **Navigate to a specific module:**
   ```bash
   cd "src/2. BigData/1. Data/1. pandas_vs_duckdb"
   ```

4. **Install dependencies:**
   ```bash
   uv sync
   ```

5. **Run examples:**
   ```bash
   uv run python bigdata_pandas_vs_duckdb.py
   ```

## 📧 Contact and Support

**Course Instructor:** Andrzej Wodecki, wodecki@pjwstk.edu.pl

**Repository Issues:** https://github.com/wodecki/ASI_2025/issues


## 📄 License

This educational material is provided for learning purposes. 

---

**Last Updated:** October 2025
**Course Year:** 2025
