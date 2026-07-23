import os
from parsers import qa_parser, guide_parser

if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)
    print("🚀 开始执行数据清洗流水线...\n")
    
    # 调用问答处理器
    qa_parser.process(
        excel_path="data/raw/AI业务问答汇总-20260616.xlsx", 
        md_path="data/processed/AI业务问答.md"
    )
    
    # 调用受理指南处理器
    guide_parser.process(
        excel_path="data/raw/健研检测材料送检业务受理指南(2026修订).xlsx", 
        md_path="data/processed/检测受理指南.md"
    )
    
    print("🎉 全部流水线执行完毕！数据已输出至 data/processed/ 目录。")