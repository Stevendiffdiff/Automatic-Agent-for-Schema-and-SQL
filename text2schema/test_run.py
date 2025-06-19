# %%
import os
from prompt import *
from agent import Text2SchemaAgent as Agent
from tqdm import tqdm

from utils import integrated_task_disc
from evaluate import evaluate

agent = Agent(
    task_disc=None,
    sample_data=None,
    log_dir="logs/test2/",
    model_id=0,
)

task_disc_dir = "test2schema/validation/descriptions"
files = os.listdir(task_disc_dir, )
for i, file in tqdm(enumerate(files), total=len(files)):
    print(f"title = {file[:-4]}")
    agent.get_task_disc(task_disc=integrated_task_disc(os.path.join(task_disc_dir, file), "test2schema/validation/drawsql_templates_2_15.xlsx", file[:-4]))
    # print(agent.task_disc)
    agent.gene_reqs()
    # print(agent.reqs)
    agent.gene_ER()
    # print(agent.json_ER)
    agent.gene_schema()
    # print(agent.schema)
    agent.log_schema(
        reqs_file=f"test2schema/validation/reqs/{file[:-4]}.json",
        json_ER_file=f"test2schema/validation/ER_jsons/{file[:-4]}.json",
        code_ER_file=f"test2schema/validation/ER_codes/{file[:-4]}.py",
        schema_file=f"test2schema/validation/schemas_designed/{file[:-4]}.json"
    )
    agent.clear()
    evaluate(
        true_path=f"test2schema/validation/schemas_true/{file[:-4]}.json",
        designed_path=f"test2schema/validation/schemas_designed/{file[:-4]}.json",
        task_name=file[:-4],
        show=True,
    )
    break