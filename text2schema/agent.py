from random import sample
from typing import Optional, List
from prompt import *
from utils import get_response
import os
import json
import warnings

class Text2SchemaAgent:
    def __init__(
            self, 
            task_disc: Optional[str] = None,
            sample_data: Optional[str] = None,
            log_dir: str = "./test1/",
            model_id: int = 0
            ):
        self.task_disc = task_disc
        self.sample_data = sample_data
        self.log_dir = log_dir
        self.model_id = model_id
        self.reqs = None
        self.code_ER = None
        self.json_ER = None
        self.schema = None

    # Obtain informations from outside...
    def get_task_disc(self, task_disc: Optional[str] = None, read_path: Optional[str] = None):
        assert isinstance(read_path, str) or isinstance(task_disc, str), "You need to offer at least one valid string for task_disc or read_path"
        if isinstance(read_path, str):
            if isinstance(task_disc, str):
                warnings.warn("Warning: you have provided both the task discription and the read file path. This will lead to the task discription being useless.")
            with open(read_path, "r", errors='ignore', encoding='utf-8') as f:
                task_disc = f.read()
                f.close()
        self.task_disc = task_disc

    def get_reqs(self, reqs: Optional[List[str]] = None, read_path: Optional[str] = None):
        assert isinstance(read_path, str) or isinstance(reqs, list), "You need to offer at least one valid List[str] for reqs or a string for read_path"
        if isinstance(read_path, str):
            if isinstance(reqs, str):
                warnings.warn("Warning: you have provided both the requirement list and the read file path. This will lead to the list being useless.")
            with open(read_path, "r", errors='ignore', encoding='utf-8') as f:
                reqs = json.load(f)
                f.close()
        self.reqs = reqs

    def get_code_ER(self, code_ER: Optional[str] = None, read_path: Optional[str] = None):
        assert isinstance(read_path, str) or isinstance(code_ER, str), "You need to offer at least one valid string for ER code or a string for read_path"
        if isinstance(read_path, str):
            if isinstance(code_ER, str):
                warnings.warn("Warning: you have provided both the code and the read file path. This will lead to the code being useless.")
            with open(read_path, "r", errors='ignore', encoding='utf-8') as f:
                code_ER = json.load(f)
                f.close()
        self.code_ER = code_ER

    def get_json_ER(self, json_ER: Optional[dict] = None, read_path: Optional[str] = None):
        assert isinstance(read_path, str) or isinstance(json_ER, dict), "You need to offer at least one valid dict for json_ER or a string for read_path"
        if isinstance(read_path, str):
            if isinstance(json_ER, str):
                warnings.warn("Warning: you have provided both the ER dict and the read file path. This will lead to the dict being useless.")
            with open(read_path, "r", errors='ignore', encoding='utf-8') as f:
                json_ER = json.load(f)
                f.close()
        self.json_ER = json_ER

    def get_schema(self, schema: Optional[dict] = None, read_path: Optional[str] = None):
        assert isinstance(read_path, str) or isinstance(schema, dict), "You need to offer at least one valid dict as schema or a string for read_path"
        if isinstance(read_path, str):
            if isinstance(schema, str):
                warnings.warn("Warning: you have provided both the schema and the read file path. This will lead to the schema being useless.")
            with open(read_path, "r", errors='ignore', encoding='utf-8') as f:
                schema = json.load(f)
                f.close()
        self.schema = schema

    # Get informations by the agent...
    def gene_reqs(self):
        reqs = get_response(prompt_req_analysis(self.task_disc, sample_data=self.sample_data), prompt_type=0, id=self.model_id)
        self.get_reqs(reqs)
        return reqs
    
    def gene_ER(self, q):
        assert self.reqs is not None, "You need to get requirements before making ER."
        dict_ER = get_response(prompt_ER(self.task_disc, sample_data=self.sample_data, reqs=self.reqs, aux_q=q), prompt_type=1, id=self.model_id)
        self.get_code_ER(dict_ER['code_ER'])
        self.get_json_ER(dict_ER['json_ER'])
        return dict_ER
    
    def gene_schema(self, q):
        assert self.reqs is not None, "You need to get requirements before making ER."
        assert self.code_ER is not None and self.json_ER is not None, "You need to get ER before making schema."
        schema = get_response(prompt_schema(self.task_disc, sample_data=self.sample_data, reqs=self.reqs, ER_json=self.json_ER, aux_q=q), prompt_type=2, id=self.model_id)
        self.get_schema(schema)
        return schema
    
    # Write the generated contents into the file.
    def log_schema(
            self, 
            file_dir: Optional[str] = None, 
            file_title: str = "", 
            reqs_file: Optional[str] = None, 
            json_ER_file: Optional[str] = None, 
            code_ER_file: Optional[str] = None,
            schema_file: Optional[str] = None,
            ):
        file_dir = file_dir if file_dir is not None else self.log_dir
        with open(os.path.join(file_dir, file_title + "reqs.json") if reqs_file is None else reqs_file, mode="w", encoding='utf-8') as f:
            json.dump(self.reqs, f, indent=2)
            f.close()
        with open(os.path.join(file_dir, file_title + "ER.json") if json_ER_file is None else json_ER_file, mode="w", encoding='utf-8') as f:
            json.dump(self.json_ER, f, indent=2)
            f.close()
        with open(os.path.join(file_dir, file_title + "ER.py") if code_ER_file is None else code_ER_file, mode="w", encoding='utf-8') as f:
            f.write(self.code_ER)
            f.close()
        with open(os.path.join(file_dir, file_title + "schema.json") if schema_file is None else schema_file, mode="w", encoding='utf-8') as f:
            json.dump(self.schema, f, indent=2)
            f.close()
        print(f"Finish logging. The contents have been written to {file_dir}.")

    def clear(self):
        self.task_disc = None
        self.reqs = None
        self.json_ER = None
        self.code_ER = None
        self.schema = None
    
