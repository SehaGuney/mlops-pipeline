# MLOps Pipeline

An MLOps pipeline that automates model training, experiment tracking and CI triggering with Apache Airflow, Kubernetes, MLflow and Jenkins.

Built during my DevOps internship as a research task, to learn how these tools fit together in a training workflow.

## Architecture

```
Airflow DAG: train_and_deploy_pipeline (daily)
    │
    ├── train_model (KubernetesPodOperator)
    │       └── Runs the training job in a separate Kubernetes Pod
    │               ├── Trains a RandomForest model on the Iris dataset
    │               └── Logs accuracy and the model artifact to MLflow
    │
    └── trigger_jenkins (SimpleHttpOperator)
            └── Triggers the Jenkins job with the run timestamp as MODEL_TAG

Jenkins pipeline (Jenkinsfile)
    ├── Checkout from GitHub
    └── Build (placeholder)
```

Training runs in its own Pod instead of on the Airflow worker, so heavy workloads stay isolated from the scheduler and can be scaled independently.

## Stack

| Layer | Technology |
|---|---|
| Orchestration | Apache Airflow 2.6.2 (CeleryExecutor) |
| Training workload | KubernetesPodOperator |
| Model training | scikit-learn |
| Experiment tracking | MLflow |
| CI | Jenkins |
| Airflow backend | PostgreSQL 13, Redis 6 |
| Local setup | Docker Compose |

## Running Locally

### 1. Configure environment variables

```bash
cd airflow
cp .env.example .env
```

Generate a Fernet key and paste it into `AIRFLOW__CORE__FERNET_KEY` in `.env`:

```bash
docker run --rm apache/airflow:2.6.2 python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Replace every `change_me` value in `.env` with your own password. The `.env` file is ignored by Git.

### 2. Start the stack

```bash
docker compose up -d
```

The `airflow-init` service runs first: it waits for PostgreSQL, runs the database migrations and creates the admin user. The webserver, scheduler and worker start only after it finishes successfully.

| Service | URL | Login |
|---|---|---|
| Airflow UI | http://localhost:8082 | `_AIRFLOW_WWW_USER_USERNAME` / `_AIRFLOW_WWW_USER_PASSWORD` from `.env` |

### 3. Stop the stack

```bash
docker compose down        # stop containers, keep the database
docker compose down -v     # stop containers and delete the database volume
```

## External Dependencies

Docker Compose runs Airflow and its backend only. To run `train_and_deploy_pipeline` end to end, you also need:

- **Kubernetes cluster:** `KubernetesPodOperator` needs access to a cluster (kubeconfig) to start the training Pod.
- **Training image:** the Pod currently uses `python:3.9-slim`, which does not include `train_model.py`, scikit-learn or MLflow. An image with the script and its dependencies is required.
- **MLflow tracking server:** set `MLFLOW_TRACKING_URI` for the training Pod.
- **Jenkins:** create an Airflow HTTP connection named `jenkins_api` pointing to your Jenkins instance, with a user and API token, and a job named `mlops-ci`.

## Airflow DAGs

### `train_and_deploy_pipeline`

- **Schedule:** daily (`@daily`)
- **Tasks:**
  1. `train_model`: starts a Kubernetes Pod that runs `train_model.py` and logs results to MLflow
  2. `trigger_jenkins`: calls `job/mlops-ci/buildWithParameters` with `MODEL_TAG={{ ts_nodash }}`

### `trigger_jenkins_job`

- **Schedule:** manual
- **Tasks:**
  1. `trigger_ci`: triggers the Jenkins job over HTTP

## Model Training (`train_model.py`)

- **Dataset:** Iris (built into scikit-learn)
- **Model:** RandomForestClassifier (100 estimators)
- **Tracked with MLflow:**
  - Metric: `accuracy`
  - Artifact: trained model (`rf_model`)

The model itself is intentionally simple. The focus of the project is the pipeline around it.

## Project Structure

```
├── airflow/
│   ├── dags/
│   │   ├── train_and_trigger.py   # Main pipeline DAG
│   │   ├── train_model.py         # Training script run inside the Pod
│   │   └── trigger_jenkins.py     # Manual Jenkins trigger DAG
│   ├── docker-compose.yml         # Airflow, PostgreSQL, Redis
│   └── .env.example               # Environment variable template
├── Jenkinsfile                    # Jenkins pipeline
└── .gitignore
```

## Key Concepts

- **Airflow + Kubernetes:** running ML workloads in isolated Pods with `KubernetesPodOperator`
- **Experiment tracking:** logging metrics and model artifacts to MLflow from a containerized job
- **Pipeline orchestration:** chaining training and CI triggering in a single DAG
- **CeleryExecutor:** distributed task execution with Redis as the broker
- **Configuration management:** secrets kept out of the repository with `.env` files

## Roadmap

- [ ] Custom training image with `train_model.py` and its dependencies
- [ ] MLflow tracking server in Docker Compose
- [ ] Local Kubernetes setup (kind or Docker Desktop) for the training Pod
- [ ] Jenkins stages that build and push a Docker image for the trained model
