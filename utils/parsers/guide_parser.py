import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def process(excel_path, md_path):
    print(f"🔄 正在处理送检受理指南数据：{excel_path} ...")
    try:
        df = pd.read_excel(excel_path, sheet_name='汇总表')
        df = df.rename(columns={'Unnamed: 3': '项目主类', 'Unnamed: 4': '项目子类'})
        
        df = df[df['样品名称'] != '样品名称']
        is_category = df['样品名称'].notna() & df['项目主类'].isna() & df['检验依据'].isna()
        df = df[~is_category].copy()
        
        ffill_cols = ['样品名称', '检验依据', '送样数量', '送样依据/取样频率/取样方法\n常用套餐/委托书', '送检/填单/受理注意事项', '承诺时效\n工作日']
        df[ffill_cols] = df[ffill_cols].ffill()
        df['项目主类'] = df['项目主类'].ffill()
        df = df.dropna(subset=['项目主类', '收费标准（元）'], how='all')

        count = 0
        with open(md_path, 'w', encoding='utf-8') as f:
            grouped = df.groupby('样品名称', sort=False)
            for name, group in grouped:
                first_row = group.iloc[0]
                f.write(f"# 样品名称：{name}\n")
                f.write(f"- **检验依据**：{first_row.get('检验依据', '暂无')}\n")
                f.write(f"- **送样数量要求**：{first_row.get('送样数量', '暂无')}\n")
                
                time_limit = str(first_row.get('承诺时效\n工作日', '暂无')).replace('\n', '')
                if time_limit != 'nan':
                    f.write(f"- **出具报告承诺时效**：{time_limit} 个工作日\n\n")
                else:
                    f.write("\n")
                
                rules = str(first_row.get('送样依据/取样频率/取样方法\n常用套餐/委托书', '暂无'))
                if rules != 'nan' and rules.strip():
                    f.write(f"### 取样与送样规范\n{rules}\n\n")
                    
                notes = str(first_row.get('送检/填单/受理注意事项', '暂无'))
                if notes != 'nan' and notes.strip():
                    f.write(f"### 送检及填单注意事项\n{notes}\n\n")
                    
                f.write(f"### 检测项目及收费明细\n")
                for _, row in group.iterrows():
                    item_main = str(row.get('项目主类', '')).replace('\n', '')
                    item_sub = str(row.get('项目子类', '')).replace('\n', '') if pd.notna(row.get('项目子类')) else ''
                    
                    full_item = f"{item_main}（{item_sub}）" if item_sub else item_main
                    fee = row.get('收费标准（元）', '未知')
                    unit = row.get('计费单位', '未知')
                    if full_item == 'nan': continue
                    unit_str = f" / {unit}" if str(unit) != 'nan' else ""
                    f.write(f"- {full_item}：{fee}元{unit_str}\n")
                f.write("\n---\n\n")
                count += 1
        print(f"✅ 受理指南处理完成！提取了 {count} 种材料标准。\n")
    except Exception as e:
        print(f"❌ 受理指南处理失败: {e}\n")