import pandas as pd
import json
import os
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

# =========================================================
# 1. CẤU HÌNH
# =========================================================
# Thư mục chứa các file event JSON
base_path = r"E:/24022314/Năm 2/Kì 2 năm 2/Khai phá và phân tích dữ liệu/Seminar/football-data-mining-fpgrowth/data"

# Ngưỡng cho FP-Growth
MIN_SUPPORT = 0.01
MIN_CONFIDENCE = 0.5


# =========================================================
# 2. HÀM PHÂN LOẠI KIỂU TẤN CÔNG
# =========================================================
def classify_attack(df_possession):
    """
    Phân loại pha tấn công thành:
    - wing: tấn công biên
    - direct: tấn công trực diện

    Quy tắc đơn giản:
    - Nếu có nhiều hành động xảy ra ở hai biên (y < 20 hoặc y > 60)
      => wing
    - Ngược lại => direct
    """
    if 'location' not in df_possession.columns:
        return 'direct'

    wing_count = 0
    total_count = 0

    for loc in df_possession['location']:
        if isinstance(loc, list) and len(loc) >= 2:
            x, y = loc[0], loc[1]
            total_count += 1

            # Hai biên sân StatsBomb: y gần 0 hoặc gần 80
            if y < 20 or y > 60:
                wing_count += 1

    if total_count == 0:
        return 'direct'

    # Nếu ít nhất 40% hành động diễn ra ở biên
    if wing_count / total_count >= 0.4:
        return 'wing'
    else:
        return 'direct'


# =========================================================
# 3. ĐỌC DỮ LIỆU VÀ TẠO TRANSACTIONS
# =========================================================
def load_and_convert_to_transactions(directory):
    wing_transactions = []
    direct_transactions = []

    event_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    print(f"Đang kiểm tra {len(event_files)} file...")

    for file_name in event_files:
        try:
            file_path = os.path.join(directory, file_name)

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            df = pd.json_normalize(data)

            # Kiểm tra file event
            if 'type.name' not in df.columns or 'possession' not in df.columns:
                continue

            # Bổ sung player.name nếu thiếu
            if 'player.name' not in df.columns:
                df['player.name'] = 'System'

            df['player.name'] = df['player.name'].fillna('System')

            # Tạo nhãn hành động
            df['action_label'] = (
                df['player.name'].astype(str)
                + "_"
                + df['type.name'].astype(str)
            )

            # Sắp xếp theo thời gian
            sort_cols = [col for col in ['minute', 'second'] if col in df.columns]
            if sort_cols:
                df = df.sort_values(sort_cols)

            # Gom theo từng possession
            for _, df_possession in df.groupby('possession'):
                transaction = df_possession['action_label'].tolist()

                # Bỏ các possession quá ngắn
                if len(transaction) < 2:
                    continue

                attack_type = classify_attack(df_possession)

                if attack_type == 'wing':
                    wing_transactions.append(transaction)
                else:
                    direct_transactions.append(transaction)

            print(f"Xử lý thành công: {file_name}")

        except Exception as e:
            print(f"Không thể đọc file {file_name}: {e}")
            continue

    return wing_transactions, direct_transactions


# =========================================================
# 4. LƯU TRANSACTIONS RA CSV
# =========================================================
def save_transactions(transactions, output_file):
    formatted_transactions = [",".join(t) for t in transactions]
    df = pd.DataFrame({'features': formatted_transactions})
    df.to_csv(output_file, index_label='attack_id')
    print(f"Đã lưu {len(transactions)} transactions vào {output_file}")


# =========================================================
# 5. CHẠY FP-GROWTH VÀ ASSOCIATION RULES
# =========================================================
def mine_patterns(transactions, prefix):
    if len(transactions) == 0:
        print(f"Không có dữ liệu cho {prefix}")
        return

    print(f"\nĐang khai phá dữ liệu cho nhóm: {prefix}")

    # One-hot encoding
    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df_encoded = pd.DataFrame(te_array, columns=te.columns_)

    # Frequent itemsets
    frequent_itemsets = fpgrowth(
        df_encoded,
        min_support=MIN_SUPPORT,
        use_colnames=True
    )

    # Thêm cột độ dài itemset
    frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(len)

    # Chuyển itemsets thành chuỗi để dễ đọc
    frequent_itemsets['itemsets'] = frequent_itemsets['itemsets'].apply(
        lambda x: ', '.join(sorted(list(x)))
    )

    # Lưu frequent itemsets
    fi_file = f"{prefix}_frequent_itemsets.csv"
    frequent_itemsets.to_csv(fi_file, index=False)
    print(f"Đã lưu frequent itemsets vào {fi_file}")

    # Nếu không có itemset đủ lớn thì không tạo luật
    if frequent_itemsets.empty:
        print(f"Không tìm thấy frequent itemsets cho {prefix}")
        return

    # Cần tạo lại frequent itemsets gốc (dạng frozenset)
    frequent_itemsets_raw = fpgrowth(
        df_encoded,
        min_support=MIN_SUPPORT,
        use_colnames=True
    )

    # Chỉ tạo luật nếu có itemset có ít nhất 2 phần tử
    if frequent_itemsets_raw['itemsets'].apply(len).max() < 2:
        print(f"Không đủ itemsets để tạo association rules cho {prefix}")
        return

    # Association rules
    rules = association_rules(
        frequent_itemsets_raw,
        metric='confidence',
        min_threshold=MIN_CONFIDENCE
    )

    if rules.empty:
        print(f"Không tìm thấy association rules cho {prefix}")
        return

    # Chuyển antecedents/consequents thành chuỗi
    rules['antecedents'] = rules['antecedents'].apply(
        lambda x: ', '.join(sorted(list(x)))
    )
    rules['consequents'] = rules['consequents'].apply(
        lambda x: ', '.join(sorted(list(x)))
    )

    # Sắp xếp theo lift giảm dần
    rules = rules.sort_values('lift', ascending=False)

    # Lưu rules
    rules_file = f"{prefix}_association_rules.csv"
    rules.to_csv(rules_file, index=False)
    print(f"Đã lưu association rules vào {rules_file}")


# =========================================================
# 6. MAIN
# =========================================================
if __name__ == "__main__":
    try:
        # Tạo transactions
        wing_transactions, direct_transactions = load_and_convert_to_transactions(
            base_path
        )

        print("\n========== THỐNG KÊ ==========")
        print(f"Số pha tấn công biên: {len(wing_transactions)}")
        print(f"Số pha tấn công trực diện: {len(direct_transactions)}")

        # Lưu transactions
        save_transactions(wing_transactions, "wing_transactions.csv")
        save_transactions(direct_transactions, "direct_transactions.csv")

        # Khai phá frequent itemsets và association rules
        mine_patterns(wing_transactions, "wing")
        mine_patterns(direct_transactions, "direct")

        print("\nHoàn thành toàn bộ quá trình.")

    except Exception as e:
        print(f"Lỗi: {e}")