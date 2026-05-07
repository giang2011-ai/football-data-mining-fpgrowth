import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from convert_data import load_and_convert_to_transactions
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

# --- THIẾT LẬP ĐƯỜNG DẪN CHÍNH XÁC ---
BASE_PATH = r"E:/24022314/Năm 2/Kì 2 năm 2/Khai phá và phân tích dữ liệu/Seminar/football-data-mining-fpgrowth/data"
OUTPUT_DIR = r"E:/24022314/Năm 2/Kì 2 năm 2/Khai phá và phân tích dữ liệu/Seminar/football-data-mining-fpgrowth/outputs"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print(f"Đang xử lý dữ liệu từ: {BASE_PATH}")
raw_transactions = load_and_convert_to_transactions(BASE_PATH)

def analyze_and_plot_vertical():
    results_list = []
    
    # Bước 1: Tìm tên các đội/thực thể riêng biệt
    entities = set()
    for t in raw_transactions:
        for a in t:
            if "_" in a: entities.add(a.split('_')[0])
    entities.discard('System')

    for entity in sorted(list(entities)):
        # Lọc chuỗi cho riêng từng đội
        entity_trans = [[a for a in t if entity in a and "System" not in a] for t in raw_transactions]
        entity_trans = [t for t in entity_trans if len(t) >= 2]
        if len(entity_trans) < 5: continue

        te = TransactionEncoder()
        te_ary = te.fit(entity_trans).transform(entity_trans)
        df_onehot = pd.DataFrame(te_ary, columns=te.columns_)

        # Khai phá FP-Growth
        frequent_itemsets = fpgrowth(df_onehot, min_support=0.005, use_colnames=True)
        if frequent_itemsets.empty: continue
        
        # Sinh luật hiệp hội
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.1)

        for _, row in rules.iterrows():
            antecedents = list(row['antecedents'])
            consequents = list(row['consequents'])
            
            # Chỉ lấy các luật dẫn đến Shot hoặc Goal
            is_shot = any("Shot" in c for c in consequents)
            is_goal = any("Goal" in c for c in consequents)
            
            if is_shot or is_goal:
                # Tính Goal Rate: Nếu luật dẫn thẳng đến Goal thì tỷ lệ cao, 
                # nếu chỉ đến Shot thì tỷ lệ chuyển hóa thấp hơn
                g_rate = row['confidence'] * (0.8 if is_goal else 0.2)
                
                results_list.append({
                    'Entity': entity,
                    'Label': f"{entity}\n{str(antecedents)[:25]}...",
                    'Confidence': row['confidence'],
                    'Goal_Rate': g_rate
                })

    if not results_list:
        print("❌ Không tìm thấy mẫu hình nào. Hãy kiểm tra lại folder data.")
        return

    # Bước 2: Sắp xếp và lấy Top 10 chiến thuật
    df = pd.DataFrame(results_list).sort_values(by='Confidence', ascending=False).head(10)

    # --- BƯỚC 3: VẼ BIỂU ĐỒ DỌC ---
    x = np.arange(len(df['Label']))
    width = 0.35

    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Cột Confidence (Xác suất sút)
    rects1 = ax.bar(x - width/2, df['Confidence'], width, label='Xác suất dứt điểm (Confidence)', color='#3498db')
    
    # Cột Goal Rate (Tỷ lệ thành bàn) - Nhỏ hơn bên cạnh
    rects2 = ax.bar(x + width/2, df['Goal_Rate'], width*0.7, label='Tỷ lệ ghi bàn dự kiến (Goal %)', color='#e67e22')

    ax.set_ylabel('Tỷ lệ (%)')
    ax.set_title(f'Phân tích Chiến thuật theo Đội bóng (Dữ liệu: {len(raw_transactions)} trận)', fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(df['Label'], rotation=30, ha='right')
    ax.legend()

    # Gán nhãn số liệu lên đầu cột
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1%}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    # Lưu ảnh vào folder outputs
    output_path = os.path.join(OUTPUT_DIR, 'final_tactics_chart.png')
    plt.savefig(output_path)
    print(f"✅ BIỂU ĐỒ ĐÃ LƯU TẠI: {output_path}")
    plt.show()

if __name__ == "__main__":
    analyze_and_plot_vertical()