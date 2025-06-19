from openai import OpenAI
import json
import re

API = <API>
BASE_URL = <BASE URL>
MODEL = <MODEL>

client = OpenAI(
            api_key=API,
            base_url=BASE_URL,
        )
model_name = MODEL


def load_json_to_str(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        json_string = json.dumps(data, ensure_ascii=False, indent=4)
    return json_string



def judge_schema_matched(label_path, designed_path):
    label_json = load_json_to_str(label_path)
    designed_json = load_json_to_str(designed_path)
    prompt = f"""
    下面提供了两个json格式的数据库schema，分别是真实的(schema_true)和模型设计的(schema_designed)，两个schema的table数量和名字是一样的。请尝试匹配每个table的每个column，以及每个relationships.匹配规则如下：
    1.名称应该语义上是接近的
    2.其他属性应该不发生矛盾并尽可能重合
    最终输出的结果格式如下：
    {{
        "schema_true": {{
                "tables": [
                    {{
                        "name": "table_name",
                        "columns": [
                        {{
                            "name": "id",
                            "matched": true|false,
                        }},
                        {{
                            "name": "column_name",
                            "matched": true|false,
                        }}
                        ]
                    }}
                ],
                "relationships": [
                    {{
                        "name": "relationship_name",
                        "matched": true|false,
                    }}
                ]
        }},
        "schema_designed": {{
            "tables": [
                {{
                    "name": "table_name",
                    "columns": [
                    {{
                        "name": "id",
                        "matched": true|false,
                    }},
                    {{
                        "name": "column_name",
                        "matched": true|false,
                    }}
                    ]
                }}
            ],
            "relationships": [
                {{
                    "name": "relationship_name",
                    "matched": true|false,
                }}
            ]
        }}
    }}
    以下为提供的schema_true和schema_designed

    ####schema_true####
    {label_json}

    ####schema_designed####
    {designed_json}
    """
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    return response.choices[0].message.content

def extract_json_to_dict(text):
    """
    从文本中提取JSON格式内容并转换为Python字典
    
    参数:
    text (str): 包含JSON的文本内容
    
    返回:
    dict: 提取并转换后的字典，如果没找到有效JSON则返回None
    """
    # 寻找大括号匹配的JSON模式
    # 这个正则表达式寻找最外层的花括号及其内容
    json_pattern = r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}))*\})'
    
    matches = re.findall(json_pattern, text)
    
    if not matches:
        return None
    
    # 尝试解析找到的每个可能的JSON字符串
    for potential_json in matches:
        try:
            # 尝试解析为Python字典
            result = json.loads(potential_json)
            # 如果是字典类型，直接返回
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            # 解析失败，尝试下一个匹配项
            continue
    
    # 没有找到有效的JSON
    return None

def cal_metrics(result):
    label_tables = result["schema_true"]["tables"]
    designed_tables = result["schema_designed"]["tables"]
    label_relationships = result["schema_true"]["relationships"]
    designed_relationships = result["schema_designed"]["relationships"]
    
    metrics = {
        "table_precision": 0,
        "table_recall": 0,
        "relationship_precision": 0,
        "relationship_recall": 0,
    }
    count = 0
    correct_count = 0
    for table in label_tables:
        for column in table["columns"]:
            count += 1
            if column["matched"] == True:
                correct_count += 1
    metrics["table_recall"] = correct_count / count
    count = 0
    correct_count = 0
    for table in designed_tables:
        for column in table["columns"]:
            count += 1
            if column["matched"] == True:
                correct_count += 1
    metrics["table_precision"] = correct_count / count
    count = 0
    correct_count = 0
    for relationship in label_relationships:
        count += 1
        if relationship["matched"] == True:
            correct_count += 1
    metrics["relationship_recall"] = correct_count / count
    count = 0
    correct_count = 0
    for relationship in designed_relationships:
        count += 1
        if relationship["matched"] == True:
            correct_count += 1
    metrics["relationship_precision"] = correct_count / count
    return metrics

def evaluate(true_path: str, designed_path: str, task_name: str, show: bool = False):
    result = judge_schema_matched(true_path, designed_path)
    result = extract_json_to_dict(result)
    if show:
        print(result)
    metrics = cal_metrics(result)
    if show:
        print(metrics)
    metrics['task_name'] = task_name
    return metrics

if __name__ == "__main__":
    true_path = r"test2schema\validation\schemas_true\acts_as_taggable_on.json"
    designed_path = r"test2schema\validation\schemas_designed\acts_as_taggable_on.json"
    evaluate(true_path, designed_path, task_name="acts_as_taggable_on", show=True)
