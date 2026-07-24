# core/vector_store/build_guide.py
import os
import sys
import time
from pathlib import Path
from tqdm import tqdm

# 动态定位项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()
embeddings = DashScopeEmbeddings()

def build_guide_only():
    guide_file = ROOT_DIR / "data" / "processed" / "检测受理指南.md"
    persist_dir = ROOT_DIR / "chroma_db"

    print("1. 正在读取长篇文档《检测受理指南.md》...")
    # 确保文件存在，防止报错
    if not guide_file.exists():
        print(f"找不到文件：{guide_file}")
        return

    loader = TextLoader(str(guide_file), encoding="utf-8")
    docs = loader.load()

    print("2. 采用【大切分策略】保留上下文连贯性...")
    guide_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""]
    )
    split_docs = guide_splitter.split_documents(docs)
    
    # 给指南数据打上专属标签，方便大模型区分
    for doc in split_docs:
        doc.metadata["source"] = "检测受理指南"

    print(f"   -> 成功将指南切分成了 {len(split_docs)} 个逻辑段落。")

    print("3. 正在将《指南》数据追加到现有的 Chroma 数据库中...")
    
    # ⚠️ 核心区别：这里是直接连接现有数据库，而不是新建！
    vectorstore = Chroma(
        persist_directory=str(persist_dir), 
        embedding_function=embeddings
    )
    
    batch_size = 100 
    batches = [split_docs[i:i + batch_size] for i in range(0, len(split_docs), batch_size)]
    
    for batch in tqdm(batches, desc="指南向量化进度", unit="批次"):
        vectorstore.add_documents(documents=batch)
        time.sleep(0.5)

    print("\n🎉 《检测受理指南》已成功追加到数据库！")

if __name__ == "__main__":
    # ⚠️ 这里绝对不能有清理 chroma_db 的代码，否则会把刚才的 Q&A 删掉！
    build_guide_only()