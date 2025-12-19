import pandas as pd
import random
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

# Define paths and database credentials
excel_file_path = '/home/andra/Documents/Kerjaan/engine-pribadi/Untitled 1.ods'
# csv_file_path = 'Create dags/create_new_dags.xlsx'
db_name = os.getenv('DB_NAME')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')

# Construct MongoDB connection string
client = MongoClient("mongodb://onlinenews_datalake:Kabayan2020@15.235.164.126:3003/?authSource=onlinenews_datalake&directConnection=true")
# client = MongoClient(f"mongodb://localhost:27017/")

# Connect to MongoDB
db = client[db_name]
collection = db['scraper']

# Function to generate random time format for DAG schedule
def random_time_format(Tier, Directory):
    random_minute = random.randint(0, 59)
    
    periods = {
        "pagi": (3, 11),
        "siang": (12, 16),
        "sore/malam": (17, 23)
    }
    
    random_hours = {period: random.randint(hours[0], hours[1]) for period, hours in periods.items()}
    return f"{random_minute} */1 * * *"
    # if Directory == "Fisik Onsite SC 01":
    #     return f"{random_minute} */1 * * *"
    # else:
    #     if Tier == "Untier":
    #         return f"{random_minute} {random_hours['pagi']},{random_hours['siang']},{random_hours['sore/malam']} * * *"
    #     elif Tier == "Tier1":
    #         return f"{random_minute} */1 * * *"
    #     elif Tier == "Tier2":
    #         return f"{random_minute} */2 * * *"
    #     elif Tier == "Tier3":
    #         return f"{random_minute} */3 * * *"
    #     elif Tier == "Tier4":
    #         return f"{random_minute} */4 * * *"

# Load Excel data
df = pd.read_excel(excel_file_path, index_col=0)
# DAG Template
dag_template = """from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import TaskInstance
from airflow.settings import Session
from airflow.utils.state import State
from airflow.models import Variable

def stop_previous_task(**kwargs):
    ti = kwargs['ti']
    dag_id = kwargs['dag_run'].dag_id
    task_id = 'run_{file_name}_script' 
    current_execution_date = kwargs['execution_date']

    print(f"Checking for running instances for DAG: {{dag_id}}, Task: {{task_id}}")

    session = Session()

    previous_instances = (
        session.query(TaskInstance)
        .filter(TaskInstance.dag_id == dag_id)
        .filter(TaskInstance.task_id == task_id)
        .filter(TaskInstance.execution_date < current_execution_date)
        .filter(TaskInstance.state == 'running')
        .all()
    )
    for prev_ti in previous_instances:
        prev_ti.set_state(State.FAILED)

        print(f"Task instance {{prev_ti}} with status {{prev_ti.state}} is running and has been forcefully completed.")

    session.commit()
    session.close()

default_args = {{
    'owner': 'kurasi_scraper',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
}}

dag_{file_name} = DAG(
    'run_{file_name}',
    default_args=default_args,
    description='DAG untuk menjalankan Scraper {file_name}',
    schedule_interval='{crontjob}',
    catchup=False,
    tags=['{file_name}']
)

task1 = BashOperator(
    task_id='run_{file_name}_script',
    bash_command={bash_command},
    dag=dag_{file_name},
)

stop_task = PythonOperator(
    task_id='stop_previous_task',
    python_callable=stop_previous_task,
    provide_context=True,
    dag=dag_{file_name},
)

task1.set_upstream(stop_task)

if __name__ == "__main__":
    dag_{file_name}.cli()
"""

# Path mappings for DAG directories
path_mappings = {
    "VM 1": os.getenv('VM_1'),
    "VM 2": os.getenv('VM_2'),
    "VM 3": os.getenv('VM_3'),
    "Fisik": os.getenv('Fisik'),
    "Fisik C2": os.getenv('Fisik_C2'),
    "Fisik Onsite SC 01": os.getenv('Onsite-sc01')
}

# Process each row in the DataFrame
# print(df)
# exit()
for index, row in df.iterrows():
    scraper_name = index
    file_name = index
    file_dag = row[0]
    tier_scraper = row[1]
    cakupan = row[5]
    domain = row[3]
    Directory = row[2]                          
    Tier = row[1]
    crontjob = random_time_format(Tier, Directory)
    status = row[6]

    # MongoDB operations
    # id_in_db = collection.find_one({'_id': file_name})
    # if id_in_db is not None:
    #     continue
    
    #tier 
    if tier_scraper == "Untier":
        tier = int(0)
    elif tier_scraper == "Tier1":
        tier = int(1)
    elif tier_scraper == "Tier2":
        tier = int(2)
    elif tier_scraper == "Tier3":
        tier = int(3)
    elif tier_scraper == "Tier4":
        tier = int(4)
    # Insert into MongoDB
    meta = {
        "_id": scraper_name,
        "status": 1,
        "enable": 1,
        "tier": tier,
        "cakupan": cakupan,
        "domain": domain
    }
    if collection.find_one({"_id": scraper_name}):
        print(f"scraper dengan _id '{scraper_name}' sudah ada, lewati insert.")
        continue
    collection.insert_one(meta)
    if status == 'WP':
        print(file_name +' : Scraper wordpres cukup insert saja')
        continue
    # Bash command based on Directory
    if Directory == "Fisik":
        bash_command = f'/home/kby-server/scraper/online-news-scraper/venv/bin/python3 /home/kby-server/scraper/online-news-scraper/Fisik/{file_dag}'
    elif Directory in ["VM 1", "VM 2", "VM 3", "Fisik 2", "Fisik C2", "Fisik Onsite SC 01"]:
        bash_command = f'Variable.get("AIRFLOW_PATH") + "{file_dag}"'
    else:
        print(f"Invalid Directory value: {Directory}")
        continue

    # Generate DAG content
    if '.' in file_name:
        name_file = file_name.replace('.', '_')
        dag_content = dag_template.format(file_name=name_file, crontjob=crontjob, bash_command=bash_command)
    else:
        dag_content = dag_template.format(file_name=file_name, crontjob=crontjob, bash_command=bash_command)
    
    # Create DAG file in the appropriate directory
    dag_directory = path_mappings.get(Directory)
    if dag_directory:
        dag_file_path = os.path.join(dag_directory, f"{file_dag}")
    
        with open(dag_file_path, "w") as file:
            file.write(dag_content)
        
        print(f"File '{dag_file_path}' has been created.")
    else:
        print(f"Invalid Directory value: {Directory}")
