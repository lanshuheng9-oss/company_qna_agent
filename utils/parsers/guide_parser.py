import pandas as pd
from pathlib import Path

def process(excel_path: str, md_path: str):
    """
    处理材料送检受理指南表格，提取核心字段并转化为【大白话结构块】的 Markdown
    """
    # 动态获取项目根目录
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
    
    # 拼接绝对路径
    abs_excel_path = ROOT_DIR / excel_path
    abs_md_path = ROOT_DIR / md_path
    
    # 自动创建输出文件夹（如果不存在）
    abs_md_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. 读取 Excel 文件中的 '汇总表'
    print(f"正在读取 Excel: {abs_excel_path.name} ...")
    df = pd.read_excel(abs_excel_path, sheet_name='汇总表', header=0)
    
    # 2. 处理所有可能存在的合并单元格留空现象（向下填充）
    ffill_columns = [
        '样品名称', 
        '承诺时效\n工作日', 
        '送样数量', 
        '送样依据/取样频率/取样方法\n常用套餐/委托书', 
        '送检/填单/受理注意事项'
    ]
    for col in ffill_columns:
        if col in df.columns:
            df[col] = df[col].ffill()
            
    # 3. 【核心魔法】解决“检验项目名称”变成数字的问题
    # 真正的项目名称在 'Unnamed: 3' 和 'Unnamed: 4' 列（因为 Excel 表头合并导致的）
    if 'Unnamed: 3' in df.columns and 'Unnamed: 4' in df.columns:
        # 清除换行符（如安\n定\n性）并处理 NaN
        df['Unnamed: 3'] = df['Unnamed: 3'].astype(str).str.replace('\n', '').replace('nan', pd.NA)
        df['Unnamed: 4'] = df['Unnamed: 4'].astype(str).str.replace('\n', '').replace('nan', pd.NA)
        
        # 向下填充主项目名称（解决子项目合并单元格的问题）
        df['Unnamed: 3_ffill'] = df['Unnamed: 3'].ffill()
        
        # 将主项目和子项目拼接，例如：安定性 (沸煮法)
        def get_full_item_name(row):
            name1 = str(row['Unnamed: 3_ffill']) if pd.notna(row['Unnamed: 3_ffill']) else ''
            name2 = str(row['Unnamed: 4']) if pd.notna(row['Unnamed: 4']) else ''
            if name2:
                return f"{name1} ({name2})"
            return name1
            
        df['完整检验项目'] = df.apply(get_full_item_name, axis=1)
    else:
        # 兼容防错
        print("⚠️ 警告：找不到 Unnamed 隐藏列，请检查 Excel 表头！")
        df['完整检验项目'] = df['检验项目（带✱为非建工资质参数）']
    
    # 4. 提取你指定的 8 个核心字段（注意：项目名称已换成了拼装好的 完整检验项目）
    target_columns = [
        '样品名称', 
        '完整检验项目', 
        '计费单位', 
        '收费标准（元）', 
        '承诺时效\n工作日', 
        '送样数量', 
        '送样依据/取样频率/取样方法\n常用套餐/委托书', 
        '送检/填单/受理注意事项'
    ]
    
    # 容错：检查列名是否都在
    missing_cols = [col for col in target_columns if col not in df.columns]
    if missing_cols:
        print(f"⚠️ 警告：找不到以下列：{missing_cols}，请核对 Excel 表头！")
        return
    
    # 过滤字段并重命名，让输出的 Markdown 表头更干净
    sub_df = df[target_columns].copy()
    sub_df.columns = [
        '样品名称', '检验项目', '计费单位', '收费标准', 
        '承诺时效', '送样数量', '送样依据与套餐', '注意事项'
    ]
    
    # 填充空值
    sub_df = sub_df.fillna("-")
    
    # 5. 拼装自然语言结构块！
    content_blocks = []
    for index, row in sub_df.iterrows():
        # 清除无效行（如果没有收费标准且没有具体的项目名称，直接跳过）
        if str(row['检验项目']) == "-" or str(row['检验项目']) == "" or str(row['收费标准']) == "-":
            continue
            
        # 把每一行拼装成一个包含完整信息的“大白话”卡片
        block = f"### {row['样品名称']} 的检测项目：{row['检验项目']}\n"
        block += f"- **所属样品/材料**：{row['样品名称']}\n"
        block += f"- **具体检验项目**：{row['检验项目']}\n"
        block += f"- **收费标准与单位**：{row['收费标准']} 元 / {row['计费单位']}\n"
        block += f"- **承诺时效**：{row['承诺时效']} 个工作日\n"
        block += f"- **所需送样数量**：{row['送样数量']}\n"
        block += f"- **送样依据与套餐说明**：{row['送样依据与套餐']}\n"
        block += f"- **相关注意事项**：{row['注意事项']}\n"
        
        content_blocks.append(block)
        
    # 用双换行符把所有块连接起来
    final_md_text = "\n\n---\n\n".join(content_blocks)
    
    # 6. 保存为 Markdown 文件
    with open(abs_md_path, "w", encoding="utf-8") as f:
        f.write("# 健研检测材料送检业务受理指南（核心版）\n\n")
        f.write("此文件为各项送检业务的核心指标与价格规范。为保证信息完整，以下内容按具体检测项目独立罗列。\n\n---\n\n")
        f.write(final_md_text)

    print(f"✅ 受理指南处理完毕: 成功转化为结构化文本，共提取 {len(content_blocks)} 个检测项目 -> {abs_md_path.name}")