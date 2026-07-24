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

    # 【旧方法】非流式生成回答（如果你其他地方还需要一次性出结果，可以保留）
    def generate_answer(self, query: str, context: str, system_prompt_template: str) -> str:
        """
        根据用户问题、检索到的文档上下文以及动态传入的 Prompt 模板生成回答
        """
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

    # 🚀【新修改的方法】流式生成回答 (Streaming) - 增加了 history 参数和处理逻辑
    def generate_answer_stream(self, query: str, context: str, system_prompt_template: str, history: list = None):
        """
        流式生成回答，返回一个 Python 生成器 (Generator)，支持多轮历史记忆
        """
        # 如果没有传入历史记录，默认为空列表
        if history is None:
            history = []
            
        formatted_system_prompt = system_prompt_template.format(context=context)
        
        # 1. 放入 System Prompt（包含系统人设与检索到的知识）
        messages = [
            {"role": "system", "content": formatted_system_prompt}
        ]
        
        # 2. 循环遍历前端传来的历史聊天记录，按顺序加入
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        # 3. 最后放入用户当前的最新提问
        messages.append({"role": "user", "content": query})

        try:
            # 开启 stream=True
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages, # 这里现在包含了完整的对话上下文
                temperature=0.1,
                stream=True  # 👈 核心开关
            )
            
            # 遍历流式返回的每一个数据块 (chunk)
            for chunk in response:
                # 检查数据块中是否包含文本增量 (delta)
                if chunk.choices and chunk.choices[0].delta.content:
                    # 使用 yield 将每个字逐个“吐”出去
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            # 如果流式输出过程中报错，也用 yield 传给前端显示
            yield f"\n[流式生成回答时发生系统错误：{e}]"

    # 🚀【新增功能】：基于历史记忆的 Query Rewrite 问题重写
    def rewrite_query(self, query: str, history: list) -> str:
        """
        根据历史记录，将用户的简短追问改写为指代明确的完整问题
        """
        # 如果没有历史记录，说明是第一轮对话，直接返回原问题
        if not history:
            return query
            
        # 提取最近的几轮对话（通常提取最后 2-3 轮就足够了，避免上下文过长）
        history_text = ""
        for msg in history[-3:]: 
            role_name = "用户" if msg["role"] == "user" else "AI客服"
            # 截取 AI 回答的前 100 个字即可，主要是为了知道主语是什么
            content_snippet = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            history_text += f"{role_name}: {content_snippet}\n"
            
      # 🚀 终极版 Rewrite Prompt：引入 Few-Shot 示例，彻底解决尺度把控问题
        rewrite_prompt = f"""你是一个高级意图分析器。你的任务是判断用户的最新提问是否需要依赖历史对话才能完整表意。

【核心判断逻辑】：
1. 如果用户的提问是关于某个特定材料的具体属性（例如：问价格、问检测周期、问送样数量、问套餐等），你必须补全历史对话中的材料名称！
2. 如果用户的提问是纯粹的通用业务流程、公司基本信息（例如：问如何包装、问公司地址、问工作时间、问付款方式等），则绝对不要添加材料名称，必须原样输出！

【学习以下示例，体会判断尺度】：
- 历史：[AI客服: 白色水泥的检测项目有...] + 最新提问：[那价格呢？] 
  -> 改写：[白色水泥的检测价格是多少？] （✔️ 材料属性，需补全）

- 历史：[AI客服: 钢筋的周期是3天...] + 最新提问：[送样数量是多少？] 
  -> 改写：[钢筋的送样数量是多少？] （✔️ 材料属性，需补全）

- 历史：[AI客服: 粉煤灰的价格是...] + 最新提问：[样品寄过来需要注意什么包装？] 
  -> 改写：[样品寄过来需要注意什么包装？] （❌ 通用流程，原样输出）

- 历史：[AI客服: 混凝土的合格标准...] + 最新提问：[你们周末上班吗？] 
  -> 改写：[你们周末上班吗？] （❌ 公司信息，原样输出）

绝对不要输出任何多余的解释、分析或标点符号，只输出最终的改写句子。

【对话历史】
{history_text}

【最新回复】: {query}
【改写后句子】:"""

        try:
            # 这里不需要流式输出，要求模型用最低的 temperature 快速、确定性地返回结果
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": rewrite_prompt}],
                temperature=0.0 
            )
            rewritten_query = response.choices[0].message.content.strip()
            return rewritten_query
        except Exception:
            # 如果大模型抽风报错，作为兜底方案，使用原问题继续后续流程
            return query