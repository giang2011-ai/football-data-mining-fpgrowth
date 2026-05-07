import pandas as pd
import json
import os

# --- 1. CẤU HÌNH ĐƯỜNG DẪN ---
# Bạn hãy sửa đường dẫn này trỏ đến thư mục chứa các file .json của bạn
base_path = r"E:/24022314/Năm 2/Kì 2 năm 2/Khai phá và phân tích dữ liệu/Seminar/data/"

def load_and_convert_to_transactions(directory):
    all_transactions = []
    event_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    
    print(f"Đang kiểm tra {len(event_files)} file...")

    for file_name in event_files:
        try:
            file_path = os.path.join(directory, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.json_normalize(data)

            # --- KIỂM TRA ĐIỀU KIỆN FILE SỰ KIỆN ---
            # Chỉ xử lý nếu file có cột 'type.name' và 'possession'
            if 'type.name' not in df.columns or 'possession' not in df.columns:
                # Đây là file danh sách hoặc cấu trúc, không phải file trận đấu -> Bỏ qua lặng lẽ
                continue

            # Xử lý player.name nếu thiếu
            if 'player.name' not in df.columns:
                df['player.name'] = 'System'
            
            df['player.name'] = df['player.name'].fillna('System')
            df['action_label'] = df['player.name'] + "_" + df['type.name']
            
            df = df.sort_values(['minute', 'second'])
            match_transactions = df.groupby('possession')['action_label'].apply(list).values.tolist()
            
            all_transactions.extend(match_transactions)
            print(f"Xử lý thành công dữ liệu trận đấu: {file_name}")
            
        except Exception as e:
            # Chỉ in lỗi nếu đó là lỗi bất thường khác
            print(f"Không thể đọc file {file_name}: {e}")
            continue

    return all_transactions

if __name__ == "__main__":
    transactions = load_and_convert_to_transactions(base_path)
    print(f"\nTổng cộng thu thập được {len(transactions)} chuỗi hành động từ các trận đấu.")
if __name__ == "__main__":
    transactions = load_and_convert_to_transactions(base_path)
    print(f"\nTổng cộng có {len(transactions)} chuỗi giao dịch để phân tích.")
# --- 4. THỰC THI ---
try:
    transactions = load_and_convert_to_transactions(base_path)
    
    # Hiển thị ví dụ 2 giao dịch đầu tiên
    print("\n--- VÍ DỤ DỮ LIỆU SAU KHI CONVERT ---")
    for i in range(2):
        print(f"Transaction {i+1}: {transactions[i][:5]}...") # In 5 hành động đầu của chuỗi

    # --- 5. LƯU DỮ LIỆU (Tùy chọn) ---
    # Lưu thành file CSV để bạn có thể mở kiểm tra hoặc dùng cho bước sau
    # df_final = pd.DataFrame({'transactions': transactions})
    # df_final.to_csv("football_transactions.csv", index=False)

except Exception as e:
    print(f"Lỗi: {e}")

# --- 6. HƯỚNG DẪN DÙNG CHO FP-GROWTH ---
"""
Sau khi có biến 'transactions', bạn dùng code này để chạy FP-Growth:

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth

te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df_onehot = pd.DataFrame(te_ary, columns=te.columns_)

# Tìm các tập phổ biến
frequent_itemsets = fpgrowth(df_onehot, min_support=0.01, use_colnames=True)
"""