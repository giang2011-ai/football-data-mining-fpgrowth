import pandas as pd

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules

# =========================
# LOAD TRANSACTIONS
# =========================

df = pd.read_csv("transactions_wing.csv")

transactions = []

for item in df["features"]:

    transactions.append(item.split(","))

print("Total transactions:", len(transactions))

# =========================
# ONE HOT ENCODING
# =========================

te = TransactionEncoder()

te_array = te.fit(transactions).transform(transactions)

df_encoded = pd.DataFrame(
    te_array,
    columns=te.columns_
)

print("\n=== Encoded Data ===\n")
print(df_encoded.head())

# =========================
# FP-GROWTH
# =========================

frequent_itemsets = fpgrowth(
    df_encoded,
    min_support=0.1,
    use_colnames=True
)

frequent_itemsets = frequent_itemsets.sort_values(
    by="support",
    ascending=False
)

print("\n=== Frequent Itemsets ===\n")
print(frequent_itemsets)

# =========================
# ASSOCIATION RULES
# =========================

rules = association_rules(
    frequent_itemsets,
    metric="confidence",
    min_threshold=0.5
)

rules = rules.sort_values(
    by="lift",
    ascending=False
)

print("\n=== Association Rules ===\n")

print(
    rules[
        [
            "antecedents",
            "consequents",
            "support",
            "confidence",
            "lift"
        ]
    ]
)

# =========================
# SAVE RESULTS
# =========================

frequent_itemsets.to_csv(
    "wing_frequent_itemsets.csv",
    index=False
)

rules.to_csv(
    "wing_association_rules.csv",
    index=False
)

print("\nFiles exported successfully.")