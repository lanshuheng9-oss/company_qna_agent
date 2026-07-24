# core/vector_store/build_qa.py
import os
import sys
from pathlib import Path

# 动态定位项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

# 💡 核心修改：改为从 langchain_core 导入 Document
from langchain_core.documents import Document
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()
embeddings = DashScopeEmbeddings()

def build_qa_only():
    qa_file = ROOT_DIR / "data" / "processed" / "AI业务问答.md"
    persist_dir = ROOT_DIR / "chroma_db"

    print("1. 正在读取《AI业务问答.md》...")
    with open(qa_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 核心魔法：纯物理手工切分！看到 --- 就切一刀
    qa_blocks = content.split("---")
    
    documents = []
    for block in qa_blocks:
        block = block.strip()
        if block:  # 如果不是空行
            documents.append(Document(page_content=block, metadata={"source": "AI业务问答"}))

    print(f"2. 完美！成功提取了 {len(documents)} 个独立且完整的标准问答！")

    print("3. 正在存入 Chroma 数据库...")
    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(persist_dir)
    )
    print("🎉 问答库专属向量导入成功！")

if __name__ == "__main__":
    if os.path.exists("./chroma_db"):
        print("正在清理旧的混合数据库...")
        os.system("rmdir /s /q chroma_db")
    
    build_qa_only()