# core/vector_store/build_kb.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from config.config import settings

def build_vector_database():
    print("1. 正在读取 data/ 目录下的 Markdown (.md) 文件...")
    
    # 核心修改：将 glob 改为匹配 "**/*.md"
    loader = DirectoryLoader(
        './data/processed',     # 重点：只读取加工后的热数据目录
        glob="**/*.md", 
        loader_cls=TextLoader, 
        loader_kwargs={'encoding': 'utf-8'}
    )
    documents = loader.load()
    print(f"   -> 成功读取了 {len(documents)} 个 Markdown 文件。")

    print("2. 正在将文档切分成小段落...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "，", " "]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"   -> 成功将文档切分成了 {len(chunks)} 个小段落。")

    print("3. 正在进行向量化并存入 Chroma 数据库...")
    embeddings = DashScopeEmbeddings(dashscope_api_key=settings.DASHSCOPE_API_KEY)
    
    persist_directory = "./chroma_db"
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print(f"✅ Markdown 知识库构建完成！数据已保存在 {persist_directory} 文件夹中。")

if __name__ == "__main__":
    build_vector_database()