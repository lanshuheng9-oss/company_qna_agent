# core/vector_store/build_all.py
import os
import sys
from pathlib import Path

# 动态定位项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

# 直接导入你刚才写好的两个构建函数
from core.vector_store.build_qa import build_qa_only
from core.vector_store.build_guide import build_guide_only

def build_all():
    print("================ 🚀 开始一键构建完整知识库 ================")
    
    # 1. 强行清理旧数据库（确保每次都是全新干净的底座）
    persist_dir = ROOT_DIR / "chroma_db"
    if persist_dir.exists():
        print("正在清理旧的 Chroma 数据库...")
        os.system(f"rmdir /s /q {persist_dir}")

    # 2. 第一步：运行问答库切分与导入
    print("\n--- [阶段 1/2] 正在构建【AI业务问答库】 ---")
    build_qa_only()

    # 3. 第二步：运行指南库切分与追加
    print("\n--- [阶段 2/2] 正在构建并追加【检测受理指南库】 ---")
    build_guide_only()

    print("\n================ 🎉 知识库一键构建全部完成！ ================")

if __name__ == "__main__":
    build_all()