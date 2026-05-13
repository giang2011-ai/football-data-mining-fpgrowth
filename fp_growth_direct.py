import pandas as pd
import os
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

# =========================================================
# 1. CẤU HÌNH
# =========================================================
BASE_DIR = r"E:/24022314/Năm 2/Kì 2 năm 2/Khai phá và phân tích dữ liệu/Seminar/football-data-mining-fpgrowth"

INPUT_FILE = os.path.join(BASE_DIR, "direct_transactions.csv")
OUTPUT_FREQUENT_ITEMSETS = os.path.join(BASE_DIR, "direct_frequent_itemsets.csv")
OUTPUT_ASSOCIATION_RULES = os.path.join(BASE_DIR, "direct_association_rules.csv")

MIN_SUPPORT = 0.01       
MIN_CONFIDENCE = 0.5     


# =========================================================
# 2. ĐỌC FILE TRANSACTIONS
# =========================================================
def load_transactions(file_path):
    """
    Đọc file direct_transactions.csv.
    File có dạng:
        attack_id,features
        0,"Pass,Shot,Goal"
        1,"Pass,Pass,Cross"
    Trả về:
        [
            ['Pass', 'Shot', 'Goal'],
            ['Pass', 'Pass', 'Cross'],
            ...
        ]
    """
    df = pd.read_csv(file_path)

    if 'features' not in df.columns:
        raise ValueError("File CSV phải có cột 'features'.")

    transactions = []

    for feature_string in df['features'].dropna():
        items = [item.strip() for item in str(feature_string).split(',') if item.strip()]

        # Loại bỏ transaction rỗng
        if len(items) > 0:
            transactions.append(items)

    return transactions


# =========================================================
# 3. CHUYỂN DỮ LIỆU SANG ONE-HOT ENCODING
# =========================================================
def encode_transactions(transactions):
    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df_encoded = pd.DataFrame(te_array, columns=te.columns_)
    return df_encoded


# =========================================================
# 4. KHAI PHÁ FREQUENT ITEMSETS
# =========================================================
def mine_frequent_itemsets(df_encoded):
    frequent_itemsets = fpgrowth(
        df_encoded,
        min_support=MIN_SUPPORT,
        use_colnames=True
    )

    # Thêm cột số lượng phần tử trong itemset
    frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(len)

    return frequent_itemsets


# =========================================================
# 5. KHAI PHÁ ASSOCIATION RULES
# =========================================================
def mine_association_rules(frequent_itemsets):
    # Chỉ tạo luật nếu có itemset có từ 2 phần tử trở lên
    if frequent_itemsets.empty:
        return pd.DataFrame()

    max_len = frequent_itemsets['itemsets'].apply(len).max()
    if max_len < 2:
        return pd.DataFrame()

    rules = association_rules(
        frequent_itemsets,
        metric='confidence',
        min_threshold=MIN_CONFIDENCE
    )

    return rules


# =========================================================
# 6. CHUYỂN CỘT SET THÀNH CHUỖI
# =========================================================
def format_itemsets(df):
    if df.empty:
        return df

    df = df.copy()
    df['itemsets'] = df['itemsets'].apply(
        lambda x: ', '.join(sorted(list(x)))
    )
    return df


def format_rules(df):
    if df.empty:
        return df

    df = df.copy()

    df['antecedents'] = df['antecedents'].apply(
        lambda x: ', '.join(sorted(list(x)))
    )

    df['consequents'] = df['consequents'].apply(
        lambda x: ', '.join(sorted(list(x)))
    )

    return df


# =========================================================
# 7. MAIN
# =========================================================
if __name__ == "__main__":
    try:
        print("Đang đọc dữ liệu transactions...")
        transactions = load_transactions(INPUT_FILE)
        print(f"Số transaction: {len(transactions)}")

        if len(transactions) == 0:
            raise ValueError("Không có transaction nào trong file.")

        print("Đang mã hóa dữ liệu...")
        df_encoded = encode_transactions(transactions)

        print("Đang chạy FP-Growth...")
        frequent_itemsets = mine_frequent_itemsets(df_encoded)

        print(f"Tìm thấy {len(frequent_itemsets)} frequent itemsets.")

        # Lưu frequent itemsets
        frequent_itemsets_to_save = format_itemsets(frequent_itemsets)
        frequent_itemsets_to_save.to_csv(
            OUTPUT_FREQUENT_ITEMSETS,
            index=False
        )

        print(f"Đã lưu vào {OUTPUT_FREQUENT_ITEMSETS}")

        print("Đang tạo association rules...")
        rules = mine_association_rules(frequent_itemsets)

        if rules.empty:
            print("Không tìm thấy association rules.")
            pd.DataFrame().to_csv(
                OUTPUT_ASSOCIATION_RULES,
                index=False
            )
        else:
            print(f"Tìm thấy {len(rules)} association rules.")

            # Sắp xếp theo lift giảm dần
            rules = rules.sort_values('lift', ascending=False)

            # Chuyển antecedents/consequents sang chuỗi
            rules_to_save = format_rules(rules)

            # Lưu rules
            rules_to_save.to_csv(
                OUTPUT_ASSOCIATION_RULES,
                index=False
            )

            print(f"Đã lưu vào {OUTPUT_ASSOCIATION_RULES}")

        print("Hoàn thành.")

    except Exception as e:
        print(f"Lỗi: {e}")