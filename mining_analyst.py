import pandas as pd
from convert_data import load_and_convert_to_transactions
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

# --- 1. LẤY DỮ LIỆU ---
base_path = r"E:/24022314/Năm 2/Kì 2 năm 2/Khai phá và phân tích dữ liệu/Seminar/data/"
transactions = load_and_convert_to_transactions(base_path)

# --- 2. MÃ HÓA DỮ LIỆU (ONE-HOT ENCODING) ---
# Chuyển đổi list các hành động thành ma trận 0-1 để máy tính hiểu được
te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df_onehot = pd.DataFrame(te_ary, columns=te.columns_)

# --- 3. CHẠY THUẬT TOÁN FP-GROWTH ---
# Tìm các tập hành động thường xuyên xuất hiện cùng nhau (min_support = 1%)
print("\nĐang xây dựng cây FP-Tree và tìm tập phổ biến...")
frequent_itemsets = fpgrowth(df_onehot, min_support=0.01, use_colnames=True)

# --- 4. TẠO LUẬT HIỆP HỘI (DỰ ĐOÁN) ---
# Tìm quy luật có độ tin cậy (confidence) trên 30%
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.3)

# --- 5. LỌC QUY LUẬT DẪN ĐẾN CÚ SÚT (SHOT) ---
# Đây là phần quan trọng nhất để dự đoán bàn thắng
# Chúng ta tìm xem những hành động nào thường dẫn đến 'Shot'
predict_shots = rules[rules['consequents'].apply(lambda x: any('Shot' in item for item in x))]

# Sắp xếp theo Lift (chỉ số đo lường độ mạnh của quy luật)
predict_shots = predict_shots.sort_values(by='lift', ascending=False)

print("\n--- CÁC MẪU HÌNH DẪN ĐẾN CÚ SÚT ĐƯỢC DỰ ĐOÁN ---")
print(predict_shots[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head(10))