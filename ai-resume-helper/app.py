"""
AI 定制简历助手 - Flask 核心应用
提供简历上传、解析、AI 优化及流式输出功能
"""

import json
from flask import Flask, request, render_template, Response
from utils.parser import parse_resume
from utils.llm import stream_chat, build_resume_prompt

app = Flask(__name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'docx'}


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否合法"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')


@app.route('/api/optimize_resume', methods=['POST'])
def optimize_resume():
    """
    简历优化 API 接口

    接收参数：
        - resume_file: 简历文件（PDF/DOCX）
        - jd_text: 职位描述文本
        - model: 模型名称（可选，默认 glm-4）
        - temperature: 温度参数（可选，默认 0.7）

    返回：
        SSE 流式响应
    """

    # 校验文件上传
    if 'resume_file' not in request.files:
        return json.dumps({
            "success": False,
            "error": "未上传简历文件"
        }), 400, {'Content-Type': 'application/json'}

    file = request.files['resume_file']

    if file.filename == '':
        return json.dumps({
            "success": False,
            "error": "未选择文件"
        }), 400, {'Content-Type': 'application/json'}

    if not allowed_file(file.filename):
        return json.dumps({
            "success": False,
            "error": "不支持的文件格式，仅支持 PDF 和 DOCX"
        }), 400, {'Content-Type': 'application/json'}

    # 校验 JD 文本
    jd_text = request.form.get('jd_text', '').strip()
    if not jd_text:
        return json.dumps({
            "success": False,
            "error": "请输入目标职位描述"
        }), 400, {'Content-Type': 'application/json'}

    # 解析简历文件
    resume_text, parse_error = parse_resume(file)

    if parse_error:
        return json.dumps({
            "success": False,
            "error": parse_error
        }), 500, {'Content-Type': 'application/json'}

    # 获取模型参数
    model = request.form.get('model', 'glm-4.6v')
    try:
        temperature = float(request.form.get('temperature', '0.7'))
        temperature = max(0.0, min(1.0, temperature))  # 限制在 0-1 范围
    except ValueError:
        temperature = 0.7

    # 构建 Prompt
    messages = build_resume_prompt(resume_text, jd_text)

    def generate():
        """SSE 流式生成器"""
        try:
            for chunk in stream_chat(messages, model, temperature):
                # 格式化为 SSE 数据
                data = json.dumps({"content": chunk}, ensure_ascii=False)
                yield f"data: {data}\n\n"

            # 发送结束信号
            yield "data: [DONE]\n\n"

        except Exception as e:
            error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"

    # 返回 SSE 流式响应
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
