import pandas as pd
import os

# =====================
# LOAD EVENTS
# =====================

events_folder = "data"

all_matches = []

for file in os.listdir(events_folder):

    if file.endswith(".json"):

        path = os.path.join(events_folder, file)

        df = pd.read_json(path)

        all_matches.append(df)

df = pd.concat(all_matches, ignore_index=True)

print("Total events:", len(df))

# =====================
# FIND GOALS
# =====================

def is_goal(row):

    try:
        return row["shot"]["outcome"]["name"] == "Goal"
    except:
        return False

goals = df[df.apply(is_goal, axis=1)]

print("Goals found:", len(goals))

# =====================
# EXTRACT WING FEATURES
# =====================

transactions = []

for idx, goal in goals.iterrows():

    possession_id = goal["possession"]

    chain = df[df["possession"] == possession_id]

    features = set()

    for _, row in chain.iterrows():

        # CROSS
        try:
            if row["pass"].get("cross", False):
                features.add("cross")
        except:
            pass

        # WING PLAY
        try:
            y = row["location"][1]

            if y < 12 or y > 68:
                features.add("wing_play")

        except:
            pass

        # HEADER
        try:
            if row["shot"]["body_part"]["name"] == "Head":
                features.add("header")

        except:
            pass

        # CUTBACK
        try:

            if row["type"]["name"] == "Pass":

                start_x = row["location"][0]
                end_x = row["pass"]["end_location"][0]

                # bóng ở sát biên ngang
                if start_x > 100:

                    # chuyền ngược lại
                    if end_x < start_x:

                        features.add("cutback")


        except:
            pass

    features.add("goal")

    # header chỉ hợp lệ nếu có cross
    if "header" in features and "cross" not in features:
        features.remove("header")

    transactions.append(list(features))

# =====================
# EXPORT CSV
# =====================

df_transactions = pd.DataFrame({
    "attack_id": range(len(transactions)),
    "features": [",".join(x) for x in transactions]
})

df_transactions.to_csv(
    "transactions_wing.csv",
    index=False
)

print(df_transactions.head())