# MLOps Pipeline

An end-to-end MLOps pipeline that automates model training, experiment tracking, and CI/CD triggering using Apache Airflow, MLflow, Kubernetes, and Jenkins.

## Architecture

```
Airflow DAG (daily)
    └── KubernetesPodOperator
            └── Runs training job inside a Kubernetes Pod
                    └── Trains RandomForest on Iris dataset
                    └── Logs accuracy + model artifact to MLflow
    └── Triggers Jenkins CI job on completion

Jenkins Pipeline
    └── Checkout from GitHub
    └── Build Docker image
    └── Deploy
```

## Stack

| Layer | Technology |
|---|---|
| Orchestration | Apache Airflow 2.6.2 |
| Model Training | scikit-learn, MLflow |
| Kubernetes Integration | KubernetesPodOperator |
| CI/CD | Jenkins |
| Containerization | Docker, Docker Compose |
| Message Broker | Redis (CeleryExecutor) |
| Database | PostgreSQL (Airflow backend) |

## Running Locally

```bash
cd airflow
docker-compose up -d
```

Services:

| Service | URL |
|---|---|
| Airflow UI | http://localhost:8082 |

## Airflow DAGs

### `train_and_deploy_pipeline`
- **Schedule:** Daily
- **Tasks:**
  1. `train_model` — spins up a Kubernetes Pod, runs `train_model.py`, logs results to MLflow
  2. `trigger_jenkins` — triggers the Jenkins CI job with the model tag as a parameter

### `trigger_jenkins_job`
- **Schedule:** Manual trigger
- **Tasks:**
  1. `trigger_ci` — triggers Jenkins build via HTTP

## Model Training (`train_model.py`)

- Dataset: Iris (scikit-learn built-in)
- Model: RandomForestClassifier (100 estimators)
- Tracked with MLflow:
  - Metric: `accuracy`
  - Artifact: trained model (`rf_model`)

## Project Structure

```
├── airflow/
│   ├── dags/
│   │   ├── train_and_trigger.py   # Main pipeline DAG
│   │   ├── train_model.py         # Model training script
│   │   └── trigger_jenkins.py     # Jenkins trigger DAG
│   └── docker-compose.yml
└── Jenkinsfile                    # CI/CD pipeline
```

## Key Concepts Demonstrated

- **Airflow + Kubernetes:** Running ML workloads inside Kubernetes Pods via `KubernetesPodOperator`
- **MLflow tracking:** Logging metrics and model artifacts from within a containerized training job
- **Pipeline orchestration:** Chaining model training and CI/CD triggering in a single DAG
- **CeleryExecutor:** Distributed task execution with Redis as broker
