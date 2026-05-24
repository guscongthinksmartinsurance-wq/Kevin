import pandas as pd
import streamlit as st

st.set_page_config(page_title="Phân tích Log Ringcentral", layout="wide")

st.title("Công cụ Phân tích Log Cuộc gọi Ringcentral")

# 1. Nút kéo thả file
uploaded_file = st.file_uploader(
    "Nhấp vào đây để chọn hoặc kéo thả file log Ringcentral (.csv) của anh vào",
    type=["csv"],
)

if uploaded_file is not None:
    st.success("Đã tải file lên thành công! Đang xử lý dữ liệu...")

    # 2. Đọc dữ liệu (Sử dụng khối try-except để phòng trường hợp file bị lệch format)
    try:
        df = pd.read_csv(uploaded_file)

        # CẤU HÌNH TÊN CỘT: Anh kiểm tra xem tên cột trong file thực tế có đúng như này không nha.
        # Nếu file của anh dùng tên khác (ví dụ: 'From', 'To', 'Name'), anh chỉ cần đổi chữ trong ngoặc kép lại cho đúng.
        phone_col = "Customer Phone"  # Cột số điện thoại khách hàng
        agent_col = "Agent Name"  # Cột tên nhân viên
        agent_id_col = "Extension"  # Cột mã số nhân viên

        # Kiểm tra xem các cột có tồn tại trong file không
        missing_cols = [
            col
            for col in [phone_col, agent_col, agent_id_col]
            if col not in df.columns
        ]
        if missing_cols:
            st.error(
                f"File của anh thiếu các cột sau: {', '.join(missing_cols)}. Anh kiểm tra lại tên cột trong file csv nhé!"
            )
        else:
            # 3. TIẾN HÀNH TÍNH TOÁN
            # Bức tranh tổng toàn công ty
            tong_cuoc_goi = len(df)
            tong_phone_cong_ty = df[phone_col].nunique()

            # Chi tiết từng nhân viên
            df_total_calls = (
                df.groupby([agent_id_col, agent_col])
                .size()
                .reset_index(name="Tổng Số Cuộc Gọi")
            )
            df_unique_calls = (
                df.groupby([agent_id_col, agent_col])[phone_col]
                .nunique()
                .reset_index(name="Số Phone Duy Nhất Đã Gọi")
            )

            # Gộp và sắp xếp thứ tự
            thong_ke_nv = pd.merge(
                df_total_calls, df_unique_calls, on=[agent_id_col, agent_col]
            )
            thong_ke_nv = thong_ke_nv.sort_values(
                by="Số Phone Duy Nhất Đã Gọi", ascending=False
            ).reset_index(drop=True)
            thong_ke_nv.index = thong_ke_nv.index + 1
            thong_ke_nv = thong_ke_nv.reset_index().rename(
                columns={"index": "Hạng"}
            )

            # 4. HIỂN THỊ KẾT QUẢ LÊN GIAO DIỆN WEB
            st.markdown("---")
            st.subheader("📊 BỨC TRANH TỔNG TOÀN CÔNG TY")

            # Tạo 2 cột chỉ số nhìn cho trực quan
            kpi1, kpi2 = st.columns(2)
            with kpi1:
                st.metric(
                    label="Tổng số cuộc gọi phát sinh", value=f"{tong_cuoc_goi:,}"
                )
            with kpi2:
                st.metric(
                    label="Tổng số phone DUY NHẤT đã liên hệ",
                    value=f"{tong_phone_cong_ty:,}",
                    help="Đã lọc sạch trùng lặp giữa các nhân viên với nhau",
                )

            st.markdown("---")
            st.subheader("👥 CHI TIẾT TỪNG NHÂN VIÊN")
            st.caption(
                "Đã sắp xếp theo thứ tự giảm dần dựa trên số lượng phone duy nhất cày được"
            )

            # Hiện bảng số liệu chi tiết của 60 người
            st.dataframe(thong_ke_nv, use_container_width=True, hide_index=True)

            # 5. TẠO NÚT TẢI FILE EXCEL BÁO CÁO NGAY TRÊN WEB
            # Chuyển data thành file excel lưu tạm trong bộ nhớ để user tải về
            @st.cache_data
            def convert_df_to_excel(df_data):
                import io

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df_data.to_excel(
                        writer, sheet_name="Chi Tiet Nhan Vien", index=False
                    )
                return output.getvalue()

            excel_data = convert_df_to_excel(thong_ke_nv)

            st.download_button(
                label="📥 Tải File Báo Cáo Excel Hoàn Chỉnh",
                data=excel_data,
                file_name="Bao_Cao_Cuoc_Goi_Chi_Tiet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    except Exception as e:
        st.error(f"Đã xảy ra lỗi trong quá trình đọc dữ liệu: {e}")

else:
    st.info("Vui lòng upload file log cuộc gọi để hệ thống bắt đầu tính toán.")
