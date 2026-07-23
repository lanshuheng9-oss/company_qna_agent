import pandas as pd
import os

def process(excel_path, md_path):
    all_sheets = pd.read_excel(excel_path, sheet_name=None)
    
    with open(md_path, 'w', encoding='utf-8') as f:
        for sheet_name, df in all_sheets.items():
            print(f"正在扫描工作表: {sheet_name}...")
            
            df.columns = [str(col).strip().replace('\n', '') for col in df.columns]
            
            if '样品名称' not in df.columns:
                print(f"  -> ⚠️ 跳过: 未检测到标准数据表头")
                continue
                
            print(f"  -> ✅ 检测到有效数据，开始解析...")
            
            df['样品名称'] = df['样品名称'].ffill()
            if '送样数量' in df.columns:
                df['送样数量'] = df['送样数量'].ffill()
            
            last_col_name = df.columns[-1] 
            df[last_col_name] = df[last_col_name].ffill()

            for product_name, group in df.groupby('样品名称'):
                if pd.isna(product_name) or str(product_name).strip() == '':
                    continue
                    
                sample_qty = str(group['送样数量'].iloc[0]).replace('\n', '') if '送样数量' in group.columns else "未说明"
                extra_info = str(group[last_col_name].iloc[0]).replace('\n', ' ')
                
                items = []
                for _, row in group.iterrows():
                    # 【核心修复区】：扩大匹配范围，并增加防呆过滤
                    item_cols = [c for c in group.columns if '项目' in c or '参数' in c]
                    price_cols = [c for c in group.columns if '收费' in c or '标准' in c or '价格' in c]
                    
                    if item_cols and price_cols:
                        item_name = ""
                        # 遍历找到的所有疑似项目列
                        for col in item_cols:
                            val = str(row[col]).strip().replace('\n', '')
                            # 关键判断：如果内容不是空的，且【不是纯数字（排除了序号）】
                            if val != 'nan' and val != '' and not val.isdigit():
                                item_name = val
                                break # 找到了真正的文字就停止寻找
                        
                        price = str(row[price_cols[0]]).strip()
                        
                        # 如果真正的项目名和价格都找到了，才写进去
                        if item_name and price != 'nan':
                            items.append(f"{item_name}（{price}元）")
                            
                items_str = "、".join(items) if items else "无单独项目"
                
                text_block = f"### 产品名称：{product_name}\n"
                text_block += f"- 所属大类：{sheet_name}\n"
                text_block += f"- 送样数量要求：{sample_qty}\n"
                text_block += f"- 常用套餐及取样说明：{extra_info}\n"
                text_block += f"- 支持的单项检测及单价：{items_str}\n\n"
                
                f.write(text_block)
                
    print(f"\n🎉 《受理指南》全表解析完成！已生成：{md_path}")

if __name__ == "__main__":
    process("../../data/raw/健研检测材料送检业务受理指南(2026修订).xlsx", "../../data/processed/检测受理指南.md")