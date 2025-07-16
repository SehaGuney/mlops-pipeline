from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'seha',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='trigger_jenkins_job',
    default_args=default_args,
    description='Airflow’dan Jenkins CI job’ı tetikle',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
) as dag:

    trigger = SimpleHttpOperator(
        task_id='trigger_ci',
        http_conn_id='jenkins_api',
        endpoint='job/mlops-ci/build',     # Senin job adın neyse onu yaz
        method='POST',
        headers={"Content-Type": "application/json"},
        response_check=lambda response: response.status_code == 201,
        log_response=True,
    )
