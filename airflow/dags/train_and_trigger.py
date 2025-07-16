from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'seha',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='train_and_deploy_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
) as dag:

    train = KubernetesPodOperator(
        task_id='train_model',
        namespace='default',
        image='python:3.9-slim',
        cmds=['python','/opt/airflow/dags/train_model.py'],
        volumes=[],
        volume_mounts=[],
        get_logs=True,
    )

    trigger_ci = SimpleHttpOperator(
        task_id='trigger_jenkins',
        http_conn_id='jenkins_api',
        endpoint='job/mlops-ci/buildWithParameters',
        method='POST',
        data={"MODEL_TAG": "{{ ts_nodash }}"},
        headers={"Content-Type": "application/json"},
        response_check=lambda r: r.status_code in [200,201,202],
        log_response=True,
    )

    train >> trigger_ci
