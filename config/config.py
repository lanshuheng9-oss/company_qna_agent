import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class Settings:
    # 从环境变量读取 API Key
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    
    # 阿里百炼 OpenAI 兼容接口地址
    BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 默认调用的模型名称（推荐通义千问 qwen-plus 或 qwen-turbo）
    DEFAULT_MODEL: str = "qwen-vl-max"

settings = Settings()

# 检查 Key 是否正确加载
if not settings.DASHSCOPE_API_KEY:
    print("警告：未找到 DASHSCOPE_API_KEY，请检查 .env 文件！")