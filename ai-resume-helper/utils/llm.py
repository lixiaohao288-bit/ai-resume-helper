"""
通用大模型适配器模块
支持任何兼容 OpenAI 格式的 API（智谱 GLM、DeepSeek、OpenAI 等）
"""

import json
import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def get_llm_config() -> dict:
    """
    获取大模型 API 配置

    Returns:
        dict: 包含 api_base_url 和 api_key 的配置字典
    """
    return {
        "api_base_url": os.getenv("API_BASE_URL", ""),
        "api_key": os.getenv("API_KEY", "")
    }


def stream_chat(messages: list, model: str = "glm-4.6v", temperature: float = 0.7):
    """
    流式调用大模型 API

    Args:
        messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
        model: 模型名称，默认 glm-4
        temperature: 温度参数，控制输出随机性

    Yields:
        str: 每次生成的文本片段
    """
    config = get_llm_config()

    if not config["api_base_url"] or not config["api_key"]:
        yield "[错误] 请检查环境变量配置：API_BASE_URL 和 API_KEY"
        return

    # 构建请求 URL（兼容各种 API 格式）
    base_url = config["api_base_url"].rstrip("/")
    url = f"{base_url}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": True
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=120
        )

        if response.status_code != 200:
            yield f"[错误] API 请求失败，状态码: {response.status_code}，响应: {response.text}"
            return

        # 解析 SSE 流式响应
        for line in response.iter_lines():
            if not line:
                continue

            line = line.decode('utf-8')

            # 处理 SSE 格式
            if line.startswith('data: '):
                data_str = line[6:]  # 去掉 "data: " 前缀

                if data_str.strip() == '[DONE]':
                    break

                try:
                    data = json.loads(data_str)

                    # 兼容不同 API 的响应格式
                    choices = data.get('choices', [])
                    if choices:
                        delta = choices[0].get('delta', {})
                        content = delta.get('content', '')

                        if content:
                            yield content

                except json.JSONDecodeError:
                    continue

    except requests.exceptions.Timeout:
        yield "[错误] API 请求超时，请稍后重试"
    except requests.exceptions.RequestException as e:
        yield f"[错误] 网络请求失败: {str(e)}"
    except Exception as e:
        yield f"[错误] 未知错误: {str(e)}"


def build_resume_prompt(resume_text: str, jd_text: str) -> list:
    """
    构建简历优化 Prompt

    Args:
        resume_text: 简历文本
        jd_text: 职位描述文本

    Returns:
        list: 消息列表
    """
    system_prompt = """你是一位专业的简历优化专家。你的任务是根据目标职位描述(JD)，帮助用户优化简历内容。

请遵循以下原则：
1. 突出与 JD 匹配的关键技能和经验
2. 使用量化数据描述成就（如：提升效率 30%、管理 10 人团队）
3. 优化语言表达，使其更加专业、简洁
4. 保持真实性，不编造虚假经历
5. 输出格式使用 Markdown，便于阅读

输出结构：
## 个人优势总结
## 建议优化的简历内容
（针对每个关键部分给出优化建议和示例）
## 面试准备建议"""

    user_prompt = f"""请帮我优化简历，使其更匹配目标职位。

【我的简历内容】
{resume_text}

【目标职位描述】
{jd_text}

请给出优化后的简历内容和建议。"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
