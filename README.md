# ASI_2025 - Machine Learning Operations Course

**Akademickie Szkolenie Inżynierów (ASI) 2025**

An educational repository for teaching Machine Learning Operations (MLOps) and production ML engineering practices. This course covers the complete ML lifecycle from data processing through deployment and monitoring, with heavy emphasis on containerization, orchestration, and modern ML tooling.

## 📚 Course Overview

**Repository:** https://github.com/wodecki/ASI_2025
**Language:** Bilingual (English/Polish)
**Python Version:** 3.10-3.11
**Package Manager:** `uv` (mandatory)

### Primary Technologies

- **Containerization:** Docker, Kubernetes
- **Cloud Platform:** Google Cloud Platform (GCP)
- **Data Processing:** pandas, DuckDB, BigQuery
- **ML Frameworks:** AutoGluon, scikit-learn, PyCaret
- **Web Frameworks:** FastAPI, Streamlit
- **Monitoring:** WandB, Locust
- **LLM Integration:** OpenAI API

## 🗂️ Repository Structure

```
ASI_2025/
├── .claude/                          # Claude Code AI assistant configuration
│   ├── agents/                       # Specialized AI agents
│   │   ├── edu-code-modernizer.md
│   │   └── notebook-to-script-converter.md
│   └── CLAUDE.md                     # Project instructions for AI
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

## 📖 Key Educational Resources

### BigData Module Examples

#### 1. pandas vs DuckDB Performance Comparison

**Location:** `src/2. BigData/1. Data/1. pandas_vs_duckdb/`

Compare performance of pandas and DuckDB on datasets ranging from 100 million to 1 billion records.

**Key Learning:**
- DuckDB is 3-5x faster with 60-70% less memory usage
- Parallel processing advantages
- When to use each tool

**Quick Start:**
```bash
cd "src/2. BigData/1. Data/1. pandas_vs_duckdb"
uv sync
uv run python bigdata_pandas_vs_duckdb.py
```

#### 2. BigQuery Iowa Dataset Transfer

**Location:** `src/2. BigData/1. Data/2. BigQuery Iowa Transfer/`

Complete tutorial on transferring large datasets from Google Public Datasets to your GCP project.

**Key Learning:**
- Export BigQuery tables to Cloud Storage
- Data format optimization (CSV, Avro, Parquet)
- Cost optimization strategies
- Import workflows

**Prerequisites:**
- GCP account with billing enabled
- Basic BigQuery knowledge

## 🛠️ Development Standards

### Package Management

This project **exclusively uses `uv`** for Python package management.

**Never use pip or requirements.txt directly.** All dependencies are managed through `pyproject.toml`.

**Common commands:**
```bash
# Install dependencies
uv sync

# Add a new package
uv add pandas duckdb

# Add development dependency
uv add --dev pytest

# Run a script
uv run python script.py

# Run a command
uv run uvicorn main:app --host 0.0.0.0 --port 8003
```

### Code Style

This repository follows **pedagogical-first principles**:

1. **Atomic Concept Focus** - Each example teaches one concept clearly
2. **No Classes or Main Blocks** - Code is for interactive demonstration
3. **Modern Python** - Use Python 3.10+ features (type hints, match statements)
4. **Educational Comments** - Explain 'why', not 'what'
5. **Self-Documenting** - Variable names should be clear and educational

### Docker Standards

**Base images:**
- Preferred: `python:3.11-slim-bookworm`
- Legacy: `python:3.8-slim-buster`

**Standard Dockerfile pattern with uv:**
```dockerfile
FROM python:3.11-slim-bookworm
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies
COPY pyproject.toml .
RUN uv sync

# Copy application
COPY . .

CMD ["uv", "run", "python", "app.py"]
```

### GCP Integration

**Standard configurations:**
- **Project ID:** `ASI_2025-420908` (example)
- **Region:** `europe-west4` (Netherlands)
- **Storage:** Cloud Storage buckets + BigQuery datasets
- **Deployment:** Cloud Run for containerized services

## 📊 Technology Stack

| Category | Technologies | Module |
|----------|-------------|--------|
| **Data Processing** | pandas, DuckDB, BigQuery | 2 |
| **ML/AutoML** | AutoGluon, PyCaret, scikit-learn | 3, 7 |
| **Web Frameworks** | FastAPI, Streamlit, Uvicorn | 2-5 |
| **Containerization** | Docker, Kubernetes | 6, 10 |
| **Experiment Tracking** | WandB | 8 |
| **Load Testing** | Locust | 2 |
| **LLM Integration** | OpenAI API | 2 |
| **Cloud Platform** | GCP (Cloud Run, Artifact Registry, Compute Engine, BigQuery) | 2-11 |

## 🎓 Learning Path

### Recommended Progression

1. **Start with BigData Module (Module 2)**
   - Understand data at scale
   - Compare processing libraries
   - Learn cloud data pipelines

2. **Model Lifecycle (Module 3)**
   - Build your first ML models
   - Understand CRISP-DM methodology

3. **Containerization (Module 6)**
   - Package your applications
   - Learn Docker fundamentals

4. **ML Pipelines (Module 5)**
   - Create reproducible workflows
   - Automate training pipelines

5. **Deployment Patterns (Modules 2-3 examples)**
   - Local → Docker → Cloud deployment
   - FastAPI + Streamlit architecture

6. **Advanced Topics (Modules 7-11)**
   - AutoML, experiment tracking, drift detection
   - Kubernetes orchestration
   - System architecture design

## 📝 Exercises and Assignments

Each module includes hands-on exercises:

- **Easy:** Basic concepts and workflows
- **Medium:** Integration and optimization
- **Advanced:** Performance tuning and custom implementations

Example exercises are provided in module READMEs with:
- Clear objectives
- Starter code
- Evaluation criteria
- Discussion questions

## 🤝 Contributing

This is an educational repository. Contributions should focus on:

- Improving educational clarity
- Adding practical examples
- Fixing technical errors
- Updating deprecated dependencies

**Guidelines:**
- Use `uv` for dependency management
- Follow pedagogical-first code style
- Include clear documentation
- Test all code examples

## 📚 Additional Resources

### Official Documentation
- **DuckDB:** https://duckdb.org/docs/
- **pandas:** https://pandas.pydata.org/docs/
- **FastAPI:** https://fastapi.tiangolo.com/
- **Docker:** https://docs.docker.com/
- **BigQuery:** https://cloud.google.com/bigquery/docs
- **uv Package Manager:** https://github.com/astral-sh/uv

### Performance Benchmarks
- **Database Benchmark:** https://h2oai.github.io/db-benchmark/

### Cloud Resources
- **GCP Free Tier:** https://cloud.google.com/free
- **GCP Pricing Calculator:** https://cloud.google.com/products/calculator

## 🔧 Troubleshooting

### Common Issues

**Issue: `uv: command not found`**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or ~/.zshrc
```

**Issue: Python version mismatch**
```bash
# Check Python version
python --version

# Install Python 3.11 (macOS)
brew install python@3.11

# Install Python 3.11 (Ubuntu)
sudo apt install python3.11
```

**Issue: Docker daemon not running**
```bash
# Start Docker Desktop (macOS/Windows)
# Or start Docker service (Linux)
sudo systemctl start docker
```

**Issue: GCP authentication**
```bash
# Install gcloud CLI
# Then authenticate
gcloud auth login
gcloud config set project ASI_2025-420908
```

## 📧 Contact and Support

**Course Instructor:** [Contact information]
**Repository Issues:** https://github.com/wodecki/ASI_2025/issues

## 📄 License

This educational material is provided for learning purposes. Please check individual module licenses for specific datasets and external resources.

---

**Last Updated:** October 2025
**Course Year:** 2025
**Institution:** Akademickie Szkolenie Inżynierów (ASI)
