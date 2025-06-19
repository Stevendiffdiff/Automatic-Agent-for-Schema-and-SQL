import gradio as gr
import mysql.connector  # 如果需要连接MySQL，取消注释此行
from openai import OpenAI
import re

# ====== LLM配置 ======

API = <API>
BASE_URL = <BASE URL>
MODEL = <MODEL>
PASSWORD_FOR_SQL = <PASSWORD>

client = OpenAI(
            api_key=API,
            base_url=BASE_URL,
        )
model_name = MODEL

def prompt_initial(user_input: str, schema_json = None) -> str:
    return f"""你是一个智能数据库构建助手。

用户的需求是：{user_input}

根据另一个智能 agent 给出的数据库结构 schema_json：
{schema_json}

请据此生成完整的建库 SQL 语句，包括所有需要的表结构、主键、字段类型。只输出 SQL 代码（使用 ```sql ... ``` 包裹）。"""

def prompt_chat(user_input: str, history: list) -> str:
    history_text = "\n".join([f"用户：{u}\n助手：{a}" for u, a in history])
    return f"""你是一个智能数据库查询助手。\n{history_text}\n用户：{user_input}\n请根据当前数据库设计生成 SQL 查询代码，只输出 SQL 代码。"""

def extract_sql(text):
    sql_match = re.findall(r"```sql\n(.*?)```", text, re.DOTALL)
    return sql_match[0].strip() if sql_match else text.strip()

# ====== MySQL配置（请替换为你自己的） ======
mysql_config = {
    "host": "localhost",
    "user": "root",
    "password": PASSWORD_FOR_SQL,
    "database": "test",  # 请确保 test 数据库已存在，或你可以写代码自动创建
    "port": 3306
}

chat_history = []

def generate_sql(user_input, chat_state):
    global chat_history
    is_first = len(chat_state) == 0
    prompt = prompt_initial(user_input) if is_first else prompt_chat(user_input, chat_state)
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    agent_full_output = response.choices[0].message.content
    sql_code = extract_sql(agent_full_output)
    chat_state.append((user_input, agent_full_output))
    chat_history = chat_state
    return agent_full_output, sql_code, chat_state

def execute_sql(sql_code):
    # ====== 执行 SQL（使用 MySQL）示例 ======
    # 这里示例代码是模拟执行，实际使用时需要安装mysql-connector-python，并配置mysql_config
    
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        cursor.execute(sql_code)
        if cursor.with_rows:
            result = cursor.fetchall()  # 获取查询结果
        else:
            result = f"执行成功，影响 {cursor.rowcount} 行。"
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        result = f"[SQL 执行失败] {e}"
    
    return result



with gr.Blocks() as demo:
    gr.Markdown("## 🤖 MySQL数据库构建与查询助手")

    chat_state = gr.State([])

    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(label="用户输入", lines=6)
            btn_generate = gr.Button("生成 SQL")
        with gr.Column():
            agent_output = gr.Textbox(label="Agent 回复", lines=6)

    with gr.Row():
        with gr.Column():
            sql_output = gr.Textbox(label="生成 SQL", lines=10)
            btn_execute = gr.Button("执行 SQL")
        with gr.Column():
            execution_output = gr.Textbox(label="执行结果", lines=6)

    btn_generate.click(
        fn=generate_sql,
        inputs=[user_input, chat_state],
        outputs=[agent_output, sql_output, chat_state]
    )

    btn_execute.click(
        fn=execute_sql,
        inputs=[sql_output],
        outputs=[execution_output]
    )

demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
