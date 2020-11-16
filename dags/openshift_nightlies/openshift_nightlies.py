import sys
import os
import logging 
import json

sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))
log = logging.getLogger("airflow.task.operators")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
log.addHandler(handler) 

from datetime import timedelta
from airflow import DAG
from airflow.utils.dates import days_ago
from tasks.install_cluster import task
from airflow.operators.bash_operator import BashOperator



with open("/opt/airflow/dags/repo/dags/openshift_nightlies/vars/common.json") as arg_file:
    common_args = json.load(arg_file)

metadata_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'openshift_version': "4.7",
    'platform': 'AWS'
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}


default_args = {**common_args, **metadata_args}

dag = DAG(
    'oc_scale',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
)



install_cluster = task.get_task(dag, default_args["tasks"]["install"]["platform"], default_args["tasks"]["install"]["version"], default_args["tasks"]["install"]["config"])

run_network_benchmarks = BashOperator(
    task_id='run_network_benchmarks',
    depends_on_past=False,
    bash_command='sleep 5',
    retries=3,
    dag=dag,
)

install_cluster >> run_network_benchmarks