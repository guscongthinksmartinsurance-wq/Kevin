import pandas as pd

# 1. Đọc file log từ Ringcentral (Anh đổi lại tên file cho đúng thực tế nhé)
df = pd.read_csv("ringcentral_logs.csv")

# LƯU Ý: Anh kiểm tra xem trong file của anh, cột số điện thoại tên là gì, cột tên nhân viên tên là gì rồi thay vào đây:
phone_col = "Customer Phone"  # Tên cột số điện thoại khách hàng
agent_col = "Agent Name"  # Tên cột tên nhân viên

# --- PHẦN 1: BỨC TRANH TỔNG TOÀN CÔNG TY ---
# Gom hết data lại, xem cả công ty đã "cày" được bao nhiêu số phone không trùng nhau
tong_so_duy_nhat_cong_ty = df[phone_col].nunique()

print("-" * 50)
print(
    f"BỨC TRANH TỔNG: Toàn công ty đã gọi tổng cộng {tong_so_duy_nhat_cong_ty:,} số điện thoại duy nhất."
)
print("-" * 50)


# --- PHẦN 2: CHI TIẾT THEO TỪNG NHÂN VIÊN ---
# Đếm số điện thoại duy nhất của từng người (ai trùng của người đó thì tự trừ, người khác gọi vẫn tính)
thong_ke_nhan_vien = df.groupby(agent_col)[phone_col].nunique().reset_index()

# Đổi tên cột cho dễ đọc
thong_ke_nhan_vien.columns = ["Tên Nhân Viên", "Số Phone Duy Nhất Đã Gọi"]

# Sắp xếp từ người gọi nhiều nhất xuống ít nhất để anh dễ đánh giá Top Performers
thong_ke_nhan_vien = thong_ke_nhan_vien.sort_values(
    by="Số Phone Duy Nhất Đã Gọi", ascending=False
)

# In kết quả ra màn hình
print("\nCHI TIẾT TỪNG NHÂN VIÊN (Đã loại trùng của riêng từng người):")
print(thong_ke_nhan_vien.to_string(index=False))

# --- PHẦN 3: XUẤT BÁO CÁO (Tùy chọn) ---
# Nếu anh muốn xuất cái bảng này ra file Excel gửi cho team hoặc lưu trữ:
# thong_ke_nhan_vien.to_excel('bao_cao_60_ngay_cuoc_goi.xlsx', index=False)