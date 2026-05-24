import pandas as pd
import streamlit as st

st.set_page_config(page_title="Phân tích Log Ringcentral", layout="wide")
st.title("Công cụ Phân tích Log Cuộc gọi Ringcentral")

# Nút kéo thả file csv
uploaded_file = st.file_uploader(
    "Nhấp vào đây để chọn hoặc kéo thả file log Ringcentral (.csv) của anh vào",
    type=["csv"],
)

if uploaded_file is not None:
    st.success("Đã tải file lên thành công! Đang xử lý dữ liệu...")

    try:
        # Đọc dữ liệu từ file csv anh upload
        df = pd.read_csv(uploaded_file)

        # Cấu hình chuẩn xác theo đúng file thực tế của anh
        phone_col = "To"  # Số điện thoại khách hàng nhận cuộc gọi
        agent_col = "Extension"  # Cột chứa tên và mã nhân viên (Ví dụ: 209 - Kathy Bui)

        # Kiểm tra xem file upload có đúng 2 cột này không
        if phone_col not in df.columns or agent_col not in df.columns:
            st.error(
                "❌ File upload không khớp cấu trúc. Anh kiểm tra lại xem có đúng file có cột 'To' và 'Extension' không nhé."
            )
        else:
            # Loại bỏ các dòng trống dữ liệu ở cột Số điện thoại hoặc cột Nhân viên (nếu có)
            df = df.dropna(subset=[phone_col, agent_col])

            # Chuyển dữ liệu cột số điện thoại về dạng chữ để tránh lệch định dạng
            df[phone_col] = df[phone_col].astype(str).str.strip()
            df[agent_col] = df[agent_col].astype(str).str.strip()

            # --- TÍNH TOÁN SỐ LIỆU ---
            # 1. Bức tranh tổng toàn công ty
            tong_cuoc_goi = len(df)
            tong_phone_cong_ty = df[phone_col].nunique()

            # 2. Chi tiết từng nhân viên
            # Đếm tổng số cuộc gọi của từng người
            df_total_calls = (
                df.groupby(agent_col).size().reset_index(name="Tổng Số Cuộc Gọi")
            )
            # Đếm số phone duy nhất của từng người
            df_unique_calls = (
                df.groupby(agent_col)[phone_col]
                .nunique()
                .reset_index(name="Số Phone Duy Nhất Đã Gọi")
            )

            # Gộp dữ liệu tổng và dữ liệu lọc trùng của từng người lại làm một
            thong_ke_nv = pd.merge(df_total_calls, df_unique_calls, on=agent_col)

            # Sắp xếp thứ tự từ người gọi được nhiều số duy nhất nhất xuống ít nhất
            thong_ke_nv = thong_ke_nv.sort_values(
                by="Số Phone Duy Nhất Đã Gọi", ascending=False
            ).reset_index(drop=True)

            # Đánh số thứ tự (Hạng)
            thong_ke_nv.index = thong_ke_nv.index + 1
            thong_ke_nv = thong_ke_nv.reset_index().rename(
                columns={"index": "Hạng", agent_col: "Nhân Viên (Extension)"}
            )

            # --- HIỂN THỊ KẾT QUẢ ---
            st.markdown("---")
            st.subheader("📊 BỨC TRANH TỔNG TOÀN CÔNG TY")

            kpi1, kpi2 = st.columns(2)
            with kpi1:
                st.metric(
                    label="Tổng số cuộc gọi phát sinh", value=f"{tong_cuoc_goi:,}"
                )
            with kpi2:
                st.metric(
                    label="Tổng số phone DUY NHẤT đã liên hệ",
                    value=f"{tong_phone_cong_ty:,}",
                    help="Hệ thống đã gom tất cả data lại và loại bỏ hoàn toàn các số điện thoại bị trùng nhau giữa các nhân viên.",
                )

            st.markdown("---")
            st.subheader("👥 CHI TIẾT TỪNG NHÂN VIÊN")
            st.caption(
                "Bảng dữ liệu đã được sắp xếp giảm dần theo số lượng phone duy nhất cày được trong 60 ngày."
            )

            # Hiển thị bảng số liệu trực quan trên web app
            st.dataframe(thong_ke_nv, use_container_width=True, hide_index=True)

            # --- NÚT XUẤT FILE EXCEL BÁO CÁO ---
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
        st.error(f"Đã xảy ra lỗi trong quá trình xử lý dữ liệu: {e}")
else:
    st.info("Vui lòng upload file log cuộc gọi để hệ thống bắt đầu tính toán.")
