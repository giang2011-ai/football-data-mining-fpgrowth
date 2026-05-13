###Phân tích chiến thuật bóng đá từ dữ liệu sự kiện World Cup 2018 bằng thuật toán FP-Growth.

## Giới thiệu

Đây là bài tập cuối kỳ môn Data Mining với mục tiêu khai phá các mẫu chiến thuật dẫn đến bàn thắng từ dữ liệu sự kiện bóng đá của FIFA World Cup 2018.

Dữ liệu được lấy từ bộ dữ liệu mở của StatsBomb, bao gồm toàn bộ các hành động diễn ra trong trận đấu như chuyền bóng, rê bóng, tạt bóng, dứt điểm, v.v.

Dự án thực hiện các bước:

1. Tiền xử lý dữ liệu JSON của StatsBomb và chuyển sang định dạng CSV.
2. Phân loại các tình huống tấn công thành:
   - `wing_attack`: Tấn công biên.
   - `direct_attack`: Tấn công trực diện.
3. Tạo tập giao dịch (transactions).
4. Áp dụng thuật toán FP-Growth để tìm:
   - Frequent Itemsets.
   - Association Rules.
5. Phân tích các chiến thuật có xác suất dẫn đến bàn thắng cao nhất.
6. Trực quan hóa các đường tấn công tiêu biểu.

---

## Nguồn dữ liệu

- Dataset: FIFA World Cup 2018 Event Data.
- Provider: StatsBomb.
- Link: https://www.kaggle.com/datasets/sawya34/football-world-cup-2018-dataset

---

## Cấu trúc thư mục

```text
football-data-mining-fpgrowth/
│
├── data/                                  
├── outputs/                               
├── fifa-world-cup-statsbomb-event-data-introduction_files/
│
├── convert_data.py                         
├── wing_analysis.py                        
├── fp_growth_wing.py                       # FP-Growth cho wing_attack
├── fp_growth_direct.py                     # FP-Growth cho direct_attack
├── mining_analyst.py                       # Tổng hợp và phân tích luật kết hợp
├── visualize_attack_paths.py               # Vẽ sơ đồ đường tấn công
├── fifa_world_cup_statsbomb_analysis.py    # Phân tích dữ liệu ban đầu
│
├── wing_transactions.csv
├── direct_transactions.csv
│
├── wing_frequent_itemsets.csv
├── direct_frequent_itemsets.csv
│
├── wing_association_rules.csv
├── direct_association_rules.csv
│
├── seminar_tactical_insights.md            # Báo cáo phân tích chiến thuật
└── README.md