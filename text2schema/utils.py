import enum
from matplotlib import table
from openai import OpenAI
import json
from tqdm import tqdm
import numpy as np
import pandas as pd
from enum import Enum
from typing import List
from time import sleep
from prompt import *

API = <API>
BASE_URL = <BASE URL>
MODEL = <MODEL>

class PromptType(Enum):
    req_analysis: int = 0
    ER: int = 1
    schema: int = 2

def extract_dict_from_string(s: str) -> dict:
    start = s.find('{')
    end = s.rfind('}')
    if start == -1 or end == -1 or start > end:
        raise ValueError("No valid JSON dict found in the string.")
    json_str = s[start:end+1]
    return json.loads(json_str)
    

def extract_list_from_string(s: str) -> list:
    start = s.find('[')
    end = s.rfind(']')
    if start == -1 or end == -1 or start > end:
        raise ValueError("No valid JSON list found in the string.")
    json_str = s[start:end+1]
    return json.loads(json_str)


def get_response(
    prompt: str,
    prompt_type: PromptType,
    id: int = 0,
):
    '''Get responses from the agent.
    Args: 
        prompt: the prompt text.
        prompt_type: the prompt type, including 0, 1, 2.
        id: model id. **0** -> qwen-max 

    Returns:
        str: the returned response.
    '''

    if id == 0:
        agent = OpenAI(
            api_key=API,
            base_url=BASE_URL,
        )
        model_name = MODEL
    elif id == 1:
        raise NotImplementedError("Sorry, this api is not available.")
        # agent = OpenAI(
        #     api_key="",
        #     base_url="https://api.openai.com/v1",
        # )
        # model_name = "gpt-4o-mini"
    else:
        raise NotImplementedError("Sorry, this model has not been supported yet... Try another model!")
    
    count = 0
    while count < 5:
        try:
            response = agent.chat.completions.create(
                messages=[{
                    "role": "system",
                    "content": "You are a bilingual database design engineer. Please complete the corresponding tasks according to the following instructions."
                },
                {
                    "role": "user",
                    "content": prompt
                }],
                model=model_name,
                stream=False,
                max_tokens=8000,
                temperature=0.2,
            ).choices[0].message.content

            response = extract_dict_from_string(response) if prompt_type==1 or prompt_type==2 else extract_list_from_string(response)
            return response
        except Exception as e:
            print(f"An error occurred when processing the response. Prompt type = {prompt_type}, {e}\nCURRENT RESPONSE = {response}")
            response = None
            sleep(1)
    
def integrated_task_disc(task_disc_path: str, table_disc_path: str, task_name: Optional[str] = None) -> str:
    s = ""
    with open(task_disc_path, "r", errors='ignore') as f:
        s = f.read()
        f.close()
    task_name = task_disc_path[:-4] if task_name is None else task_name
    table_list = pd.read_excel(table_disc_path, usecols=['identify_name', 'table_names'])
    table_list = table_list[table_list['identify_name']==task_name]['table_names'].values[0]
    s = s + f"And please make sure that **your schema only contains tables as listed:**\n{table_list}. You can only generate these tables with exactly the same names."
    return s
    

    
            

