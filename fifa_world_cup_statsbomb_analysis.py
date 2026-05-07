import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- 1. HÀM VẼ SÂN BÓNG (Tương đương pitch() trong R) ---
def draw_pitch(ax, theme="green"):
    background = "#77BD77" if theme == "green" else "#224C56"
    line_color = "white"
    
    # Thân sân
    rect = patches.Rectangle((0, 0), 120, 80, linewidth=2, edgecolor=line_color, facecolor=background, zorder=0)
    ax.add_patch(rect)
    
    # Vạch giữa sân
    plt.plot([60, 60], [0, 80], color=line_color)
    ax.add_patch(patches.Circle((60, 40), 9.15, color=line_color, fill=False))
    plt.plot(60, 40, "o", color=line_color)
    
    # Vòng cấm địa (Penalty Areas)
    # Trái
    ax.add_patch(patches.Rectangle((0, 18), 18, 44, color=line_color, fill=False))
    ax.add_patch(patches.Rectangle((0, 30), 6, 20, color=line_color, fill=False))
    # Phải
    ax.add_patch(patches.Rectangle((102, 18), 18, 44, color=line_color, fill=False))
    ax.add_patch(patches.Rectangle((114, 30), 6, 20, color=line_color, fill=False))
    
    # Khung thành (Goal posts)
    ax.add_patch(patches.Rectangle((-2, 36), 2, 8, color=line_color, fill=False))
    ax.add_patch(patches.Rectangle((120, 36), 2, 8, color=line_color, fill=False))

    plt.xlim(-5, 125)
    plt.ylim(-5, 85)
    plt.axis('off')

# --- 2. ĐỌC DỮ LIỆU (Tương đương phần Files trong R) ---
# Giả sử đường dẫn folder tương tự
base_path = r"E:/24022314/Năm 2/Kì 2 năm 2/Khai phá và phân tích dữ liệu/Seminar/data/"

def load_match_events(match_id):
    with open(f"{base_path}{match_id}.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.json_normalize(data)

# --- 3. PHÂN TÍCH TRẬN CHUNG KẾT (France vs Croatia) ---
match_id = "8658"
df_events = load_match_events(match_id)

# Lọc các sự kiện Sút (Shots)
shots = df_events[df_events['type.name'] == 'Shot'].copy()

# Tách tọa độ từ list [x, y]
shots[['x', 'y']] = pd.DataFrame(shots['location'].tolist(), index=shots.index)

# --- 4. VẼ BIỂU ĐỒ XG (Expected Goals) ---
fig, ax = plt.subplots(figsize=(12, 8))
draw_pitch(ax, theme="blue")

# Phân tách đội
france_shots = shots[shots['team.name'] == 'France']
croatia_shots = shots[shots['team.name'] == 'Croatia']

# Vẽ cú sút của Pháp (Vòng tròn xanh)
plt.scatter(france_shots['x'], france_shots['y'], 
            s=france_shots['shot.statsbomb_xg'] * 500, 
            c='blue', label='France', alpha=0.6)

# Vẽ cú sút của Croatia (Vòng tròn đỏ - lật ngược sân để đối đầu)
plt.scatter(120 - croatia_shots['x'], 80 - croatia_shots['y'], 
            s=croatia_shots['shot.statsbomb_xg'] * 500, 
            c='red', label='Croatia', alpha=0.6)

plt.title("France vs Croatia - Expected Goals (xG) Map", color="white", fontsize=15)
plt.legend(loc='lower center', ncol=2)
plt.show()

# --- 5. BẢN ĐỒ CHUYỀN BÓNG CỦA MESSI ---
# (Trận France vs Argentina match_id = 7580)
match_id_messi = "7580"
df_messi_match = load_match_events(match_id_messi)

# Lọc Messi chuyền bóng
messi_passes = df_messi_match[
    (df_messi_match['type.name'] == 'Pass') & 
    (df_messi_match['player.name'] == 'Lionel Andrés Messi Cuccittini')
].copy()

# Tách tọa độ điểm đầu và điểm cuối
messi_passes[['x', 'y']] = pd.DataFrame(messi_passes['location'].tolist(), index=messi_passes.index)
messi_passes[['end_x', 'end_y']] = pd.DataFrame(messi_passes['pass.end_location'].tolist(), index=messi_passes.index)

fig, ax = plt.subplots(figsize=(12, 8))
draw_pitch(ax, theme="green")

for i, row in messi_passes.iterrows():
    color = 'yellow' if row['pass.height.name'] == 'Ground Pass' else 'red'
    # Vẽ mũi tên chuyền bóng
    ax.annotate("", xy=(row['end_x'], row['end_y']), xytext=(row['x'], row['y']),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.5))

plt.title("Lionel Messi's Pass Map vs France", fontsize=15)
plt.show()