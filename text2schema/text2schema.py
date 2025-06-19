import gradio as gr
import os
import json
import subprocess
from agent import Text2SchemaAgent as Agent
import base64
import shutil

TEMP_DIR = "temp/"
file_reqs = os.path.join(TEMP_DIR, "reqs.json")
file_code_ER = os.path.join(TEMP_DIR, "code_ER.py")
file_json_ER = os.path.join(TEMP_DIR, "json_ER.json")
file_schema = os.path.join(TEMP_DIR, "schema.json")

agent = Agent(
    task_disc=None,
    sample_data=None,
    log_dir="temp/",
    model_id=0,
)

# 标记任务阶段
completed_steps = {
    "功能设计": False,
    "ER图设计": False,
    "schema设计": False,
}
json_title = "Unavailable"
python_title = "Unavailable"

def handle_user_input(q, mode):
    global json_title, python_title
    r = f"当前任务：{mode}"
    try:
        if mode == "功能设计":
            agent.get_task_disc(task_disc=q)
            r = agent.gene_reqs()
            with open(file_reqs, "w", encoding="utf-8") as f:
                json.dump(agent.reqs, f, indent=2, ensure_ascii=False)
            completed_steps["功能设计"] = True
            json_title = "功能设计"
            q = f"任务描述：\n{q[:100]}. . .\n**DOING --功能设计--**"
        elif mode == "ER图设计":
            if not completed_steps["功能设计"]:
                return "", "请先完成功能设计！"
            r = "已生成ER图设计..."
            agent.get_reqs(read_path=file_reqs)
            agent.gene_ER(q)
            with open(file_json_ER, "w", encoding="utf-8") as f:
                json.dump(agent.json_ER, f, indent=2, ensure_ascii=False)
            with open(file_code_ER, "w", encoding="utf-8") as f:
                f.write(agent.code_ER)
            completed_steps["ER图设计"] = True
            json_title = "ER 设计"
            python_title = "ER可视化程序"
            q = f"任务描述：\n{agent.task_disc[:100]}. . .\n功能设计：\n{str(agent.reqs)[:100]}. . .\n**DOING --ER图设计--**\n{q}"
        elif mode == "schema设计":
            if not completed_steps["ER图设计"]:
                return "", "请先完成ER图设计！"
            r = "已生成schema设计..."
            agent.get_json_ER(read_path=file_json_ER)
            agent.gene_schema(q)
            with open(file_schema, "w", encoding="utf-8") as f:
                json.dump(agent.schema, f, indent=2, ensure_ascii=False)
            completed_steps["schema设计"] = True
            json_title = "Schema设计"
            python_title = "ER可视化程序"
            q = f"任务描述：\n{agent.task_disc[:100]}. . .\n功能设计：\n{str(agent.reqs)[:100]}. . .\nER图设计：\n{str(agent.json_ER)[:100]}. . .\n**DOING --Schema设计--**\n{q}"
    except AssertionError as e:
        return "", str(e)
    return q, str(r)

def load_file_text(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def load_file_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return "保存成功 ✅"

def run_py_file():
    result = subprocess.run(["python", file_code_ER], capture_output=True, text=True)
    pdf_path = "temp/ER.pdf"

    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f"""
            <iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="600px" style="border:none;"></iframe>
            """
            return result.stdout or result.stderr, gr.update(visible=True, value=pdf_display)
    else:
        return "❌ 未生成 ER.pdf 文件", gr.update(visible=False)

def clear_all():
    global json_title, python_title
    try:
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
    except:
        pass
    os.makedirs(TEMP_DIR, exist_ok=True)
    agent.clear()
    completed_steps.update({"功能设计": False, "ER图设计": False, "schema设计": False})
    json_title = python_title = "Unavailable"
    return [], "", "", "", gr.update(visible=False)

css = """
.gradio-chat-message {
    font-family: 'Microsoft YaHei', SimSun, Arial, sans-serif !important;
}
"""
with gr.Blocks(title="数据库任务前端", css=css) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 💬 对话窗口")

            chatbot = gr.Chatbot(label="沟通历史", height=600, type="messages")
            mode = gr.Dropdown(["功能设计", "ER图设计", "schema设计"], label="任务类型", value="功能设计")
            txt = gr.Textbox(placeholder="在这里输入任务描述或要求/按回车运行相应任务", show_label=False)

            def process_user(q, m, history):
                q_, r_ = handle_user_input(q, m)
                history = history + [
                    {"role": "user", "content": q_},
                    {"role": "assistant", "content": r_}
                ]
                json_content = ""
                py_content = ""
                ask_show_image = gr.update(visible=False)
                if m == "功能设计":
                    json_content = load_file_json(file_reqs)
                elif m == "ER图设计":
                    json_content = load_file_json(file_json_ER)
                    py_content = load_file_text(file_code_ER)
                elif m == "schema设计":
                    json_content = load_file_json(file_schema)
                    py_content = load_file_text(file_code_ER)

                return "", history, json_content, py_content, ask_show_image, gr.update(label=json_title), gr.update(label=python_title)

            clear_btn = gr.Button("🧹 清空历史记录")
            clear_btn.click(
                clear_all,
                outputs=[chatbot, txt, gr.Code(visible=False), gr.Code(visible=False), gr.HTML()]
            )

        with gr.Column(scale=2):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📄 JSON 编辑区")
                    json_text = gr.Code(
                        label=json_title, 
                        language="json", 
                        interactive=True, 
                        lines=20,
                        max_lines=20,
                    )
                    json_save_btn = gr.Button("确认 JSON 修改")
                    json_save_out = gr.Textbox(visible=False)
                    json_save_btn.click(
                        lambda text: save_file(file_reqs if not completed_steps["ER图设计"] else (file_json_ER if not completed_steps["schema设计"] else file_schema), text),
                        inputs=json_text,
                        outputs=json_save_out
                    )

                with gr.Column():
                    gr.Markdown("### 🐍 Python 编辑区")
                    py_code = gr.Code(
                        label=python_title, 
                        language="python", 
                        interactive=True, 
                        lines=20,
                        max_lines=20,
                    )
                    py_save_btn = gr.Button("确认 Python 修改")
                    py_save_out = gr.Textbox(visible=False)
                    py_save_btn.click(lambda text: save_file(file_code_ER, text) if completed_steps["ER图设计"] else lambda text: "文件不可用！", inputs=py_code, outputs=py_save_out)

            with gr.Row():
                with gr.Column():
                    gr.Markdown("### ▶️ 执行 Python 代码")
                    run_btn = gr.Button("执行代码")
                    py_output = gr.Textbox(label="执行输出", lines=3)

                    gr.Markdown("### 📌 是否展示 ER 图？")
                    toggle_display = gr.Radio(["是", "否"], label="展示 ER 图", value="否")
                    er_preview = gr.HTML(label="📄 ER图预览", visible=False)

                    toggle_display.change(
                        lambda x: gr.update(visible=(x == "是")),
                        inputs=toggle_display,
                        outputs=er_preview
                    )
                    run_btn.click(fn=run_py_file, outputs=[py_output, er_preview])

            txt.submit(
                process_user,
                inputs=[txt, mode, chatbot],
                outputs=[txt, chatbot, json_text, py_code, er_preview, json_text, py_code]
            )
            clear_btn.click(
                clear_all,
                outputs=[chatbot, txt, json_text, py_code, er_preview]
            )

if __name__ == "__main__":
    demo.launch()