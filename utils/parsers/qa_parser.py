import pandas as pd
from pathlib import Path

def process(excel_path: str, md_path: str):
    """
    处理 AI 业务问答表格，提取 Q&A 并转化为 Markdown 格式
    """
    # 动态获取项目根目录 (utils/parsers 往上三层是根目录 COMPANY_QNA_AGENT)
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
    
    # 拼接绝对路径，确保百分百能找到文件
    abs_excel_path = ROOT_DIR / excel_path
    abs_md_path = ROOT_DIR / md_path
    
    # 自动创建输出文件夹（如果不存在）
    abs_md_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. 读取 Excel 的 '汇总表'（跳过表头，指定第1行为列名）
    df = pd.read_excel(abs_excel_path, sheet_name='汇总表', header=1)

    # 2. 精准提取“问题”和“修正后的标准回复”两列，并剔除空行
    faq_df = df[['问题', '修正后的标准回复']].dropna(subset=['问题', '修正后的标准回复'])

    # 3. 转换为大模型最喜欢的 Markdown 问答格式
    md_content = "# 健研检测业务常见问题标准解答库 (FAQ)\n\n"
    md_content += "以下为公司各项业务的标准规范问答，当客户询问相关问题时，请严格参考以下标准回复进行回答：\n\n"

    for index, row in faq_df.iterrows():
        question = str(row['问题']).strip()
        answer = str(row['修正后的标准回复']).strip()
        
        md_content += f"### Q: {question}\n"
        md_content += f"**标准回复**：{answer}\n\n---\n\n"

    # 4. 保存为标准 Markdown 文件
    with open(abs_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✅ QA问答处理完毕: 成功提取 {len(faq_df)} 条数据 -> {abs_md_path.name}")