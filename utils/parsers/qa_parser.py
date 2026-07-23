import pandas as pd

def process(excel_path, md_path):
    print(f"🔄 正在处理业务问答数据：{excel_path} ...")
    try:
        df = pd.read_excel(excel_path, header=1)
        count = 0
        with open(md_path, 'w', encoding='utf-8') as f:
            for index, row in df.iterrows():
                question = str(row.get('问题', '')).strip()
                answer = str(row.get('修正后的标准回复', '')).strip()
                if not answer or answer == 'nan':
                    answer = str(row.get('正确回答', '')).strip()
                if question == 'nan' or answer == 'nan' or not question:
                    continue
                f.write(f"### 问题：{question}\n**标准回复**：{answer}\n\n---\n\n")
                count += 1
        print(f"✅ 问答数据处理完成！提取了 {count} 条问答对。\n")
    except Exception as e:
        print(f"❌ 问答数据处理失败: {e}\n")