# core/llm_engine/chat_model.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from openai import OpenAI
from config.config import settings

class ChatModel:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.BASE_URL
        )
        self.model = settings.DEFAULT_MODEL

    # 注意这里的参数多了一个 system_prompt_template
    def generate_answer(self, query: str, context: str, system_prompt_template: str) -> str:
        """
        根据用户问题、检索到的文档上下文以及动态传入的 Prompt 模板生成回答
        """
        # 将检索到的文档填入外部传进来的 {context} 槽位中
        formatted_system_prompt = system_prompt_template.format(context=context)
        
        messages = [
            {"role": "system", "content": formatted_system_prompt},
            {"role": "user", "content": query}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1, 
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"生成回答时发生系统错误：{e}"