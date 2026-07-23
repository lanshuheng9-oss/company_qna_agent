import sys
import os

# 将项目根目录加入环境路径，方便跨文件夹导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from openai import OpenAI
from config.config import settings

def test_connection():
    # 初始化客户端（连通百炼）
    client = OpenAI(
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.BASE_URL
    )

    print("正在请求百炼大模型...")
    
    response = client.chat.completions.create(
        model=settings.DEFAULT_MODEL,
        messages=[
            {"role": "user", "content": "你是人吗"}
        ]
    )

    print("\n[模型回答]:")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    test_connection()