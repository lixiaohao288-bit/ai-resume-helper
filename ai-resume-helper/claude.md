# AI 定制简历助手 - 项目记忆锚点

> 本文件是项目的全局记忆库，记录核心架构、模块作用、API 接口及修改日志。

---

## 📁 目录结构

```
ai-resume-helper/
├── app.py                    # Flask 核心应用（路由与流式响应）
├── requirements.txt          # Python 依赖
├── .env.example              # 环境变量示例
├── claude.md                 # 本文件（记忆锚点）
├── utils/
│   ├── __init__.py           # 包初始化
│   ├── parser.py             # PDF/DOCX 文件解析器
│   └── llm.py                # 通用大模型适配器
└── templates/
    └── index.html            # 前端单页面（Tailwind CSS + 原生 JS）
```

---

## 🧩 核心模块作用

### `app.py` - Flask 核心应用
- **路由 `/`**：渲染前端主页
- **路由 `POST /api/optimize_resume`**：接收简历文件 + JD 文本，返回 SSE 流式响应
- 异常处理：文件格式校验（400）、解析失败（500）、API 错误（503）

### `utils/parser.py` - 文件解析器
- `parse_pdf(file_stream)`：使用 pdfplumber 提取 PDF 文本
- `parse_docx(file_stream)`：使用 python-docx 提取 DOCX 文本（含表格）
- `parse_resume(file_storage)`：统一入口，返回 `(text, error)` 元组

### `utils/llm.py` - 通用大模型适配器
- `get_llm_config()`：从 `.env` 读取 API 配置
- `stream_chat(messages, model, temperature)`：**流式调用**大模型 API
- `build_resume_prompt(resume_text, jd_text)`：构建简历优化 Prompt
- **特性**：完全解耦，支持任何兼容 OpenAI 格式的 API

### `templates/index.html` - 前端页面
- 技术栈：Tailwind CSS (CDN) + Marked.js + FontAwesome
- 核心功能：
  - 文件拖拽上传
  - 实时 SSE 流式渲染（打字机效果）
  - Markdown 实时渲染
  - 一键复制 + Toast 提示

---

## 🔌 API 接口文档

### `POST /api/optimize_resume`

**请求格式**：`multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `resume_file` | File | ✅ | 简历文件（PDF/DOCX） |
| `jd_text` | String | ✅ | 目标职位描述文本 |
| `model` | String | ❌ | 模型名称，默认 `glm-4` |
| `temperature` | Float | ❌ | 温度参数 0-1，默认 `0.7` |

**响应格式**：`text/event-stream` (SSE)

```
data: {"content": "生成的文本片段"}
data: {"content": "更多文本..."}
data: [DONE]
```

**错误响应**：`application/json`

```json
{
  "success": false,
  "error": "错误信息"
}
```

---

## 🌊 流式输出实现要点

### 后端 (Flask + Generator)
```python
def generate():
    for chunk in stream_chat(messages, model, temperature):
        yield f"data: {json.dumps({'content': chunk})}\n\n"
    yield "data: [DONE]\n\n"

return Response(generate(), mimetype='text/event-stream')
```

### 前端 (Fetch + ReadableStream)
```javascript
const reader = response.body.getReader();
while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    // 解析 SSE 格式，提取 content
    // 使用 marked.parse() 实时渲染
}
```

---

## 🔧 环境配置

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑 .env，填入 API 配置
API_BASE_URL=https://open.bigmodel.cn/api/paas/v4
API_KEY=your_api_key_here

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
python app.py
```

访问 http://localhost:5000 即可使用。

---

## 📝 Changelog

### 2024-01-XX - v1.0.0 (初始版本)
- ✅ 完成项目架构搭建
- ✅ 实现 PDF/DOCX 文件解析
- ✅ 实现通用大模型适配器（支持 OpenAI 兼容 API）
- ✅ 实现 SSE 流式输出
- ✅ 实现高颜值前端 UI（Tailwind CSS）
- ✅ 实现打字机效果 + Markdown 实时渲染
- ✅ 实现一键复制 + Toast 提示

---

## 🎯 未来优化方向

- [ ] 支持更多文件格式（图片 OCR、纯文本）
- [ ] 添加简历模板生成功能
- [ ] 用户历史记录存储
- [ ] 多语言支持
- [ ] 移动端适配优化
