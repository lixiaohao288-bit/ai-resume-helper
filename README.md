# AI 定制简历助手

一个基于 Flask + 大模型的智能简历优化工具。上传你的简历，输入目标职位描述，AI 将自动为你定制匹配的简历内容。

## 功能特性

- 支持 PDF/DOCX 简历文件上传
- 根据职位描述（JD）智能优化简历
- SSE 流式输出，打字机效果实时展示
- Markdown 实时渲染
- 支持多种 OpenAI 兼容 API（智谱 GLM、DeepSeek 等）

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/lixiaohao288-bit/ai-resume-helper.git
cd ai-resume-helper
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 配置：

```
API_BASE_URL=https://open.bigmodel.cn/api/paas/v4
API_KEY=your_api_key_here
```

### 5. 启动服务

```bash
python app.py
```

访问 http://localhost:5000 即可使用。

## 项目结构

```
ai-resume-helper/
├── app.py                 # Flask 核心应用
├── requirements.txt       # Python 依赖
├── .env.example           # 环境变量模板
├── utils/
│   ├── parser.py          # PDF/DOCX 文件解析
│   └── llm.py             # 大模型 API 适配器
└── templates/
    └── index.html         # 前端页面
```

## API 接口

### POST /api/optimize_resume

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| resume_file | File | 是 | 简历文件（PDF/DOCX） |
| jd_text | String | 是 | 目标职位描述 |
| model | String | 否 | 模型名称，默认 glm-4.6v |
| temperature | Float | 否 | 温度参数 0-1，默认 0.7 |

返回 SSE 流式响应。

## 技术栈

- **后端**: Flask、pdfplumber、python-docx
- **前端**: Tailwind CSS、Marked.js
- **AI**: 支持 OpenAI 兼容 API

## License

MIT
