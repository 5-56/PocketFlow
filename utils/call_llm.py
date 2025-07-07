import os
from openai import OpenAI

def call_llm(prompt, model="gpt-4o", max_tokens=3000):
    """
    基础LLM调用函数
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM调用失败: {e}")
        return f"错误: 无法处理请求 - {str(e)}"

def analyze_with_llm(content, task, model="gpt-4o"):
    """
    专门用于分析任务的LLM调用
    """
    prompt = f"""
作为一个专业的文档分析师，请帮我完成以下任务：

### 任务描述
{task}

### 内容
{content}

### 要求
- 请提供详细且结构化的分析结果
- 使用JSON格式返回结果
- 确保分析准确和实用
"""
    return call_llm(prompt, model)

def generate_with_llm(instruction, context="", model="gpt-4o"):
    """
    专门用于生成任务的LLM调用
    """
    prompt = f"""
{instruction}

{f"参考信息：{context}" if context else ""}

请提供高质量的结果。
"""
    return call_llm(prompt, model)

if __name__ == "__main__":
    # 测试LLM调用
    test_prompt = "请用一句话介绍人工智能。"
    result = call_llm(test_prompt)
    print(f"测试结果: {result}")