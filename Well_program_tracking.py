import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# File untuk menyimpan data
DATA_FILE = "data/well_program_data.xlsx"
os.makedirs("data", exist_ok=True)

# Kolom yang diharapkan
REQUIRED_COLUMNS = [
    "No", "Well Name", "Well Program Name", "Program No", "Creation Date", "Due Date",
    "Status", "Doc Initiator", "Approval 1", "Approval 2", "Approval 3", "Approval 4", "Remarks"
]

# Opsi valid untuk dropdown
VALID_INITIATORS = ["DHARMAWAN RAHARJO", "R.AULIA MUHAMMAD RIZKY", "HIBAN"]
VALID_APPROVAL1_2 = ["KRISTIANTO WIBOWO", "YULIANTO AGUS", ""]
VALID_APPROVAL3 = ["BUDI RIVAI WIJAYA", ""]
VALID_APPROVAL4 = ["PE TEAM", ""]
VALID_STATUSES = ["COMPLETED", "INPROGRESS"]

# CSS untuk background gradasi
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #a1c4fd, #c2e9fb);
}
.table { 
    border-collapse: collapse; 
    width: 100%; 
    background-color: rgba(255, 255, 255, 0.9);
}
.table th, .table td { 
    border: 1px solid #ddd; 
    padding: 8px; 
}
.table th { 
    background-color: #f2f2f2; 
}
.dataframe { 
    border-collapse: collapse; 
    width: 100%; 
}
.dataframe th, .dataframe td { 
    border: 1px solid #ddd; 
    padding: 8px; 
}
.dataframe th { 
    background-color: #f2f2f2; 
}
</style>
""", unsafe_allow_html=True)

# Inisialisasi data jika belum ada atau perbarui struktur
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=REQUIRED_COLUMNS)
    df_init.to_excel(DATA_FILE, index=False)
else:
    # Periksa apakah kolom Due Date ada di file Excel yang sudah ada
    df_temp = pd.read_excel(DATA_FILE)
    if "Due Date" not in df_temp.columns:
        df_temp["Due Date"] = ""
        df_temp.to_excel(DATA_FILE, index=False)

# Load data
try:
    df = pd.read_excel(DATA_FILE)
    # Pastikan semua kolom yang diperlukan ada
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df.to_excel(DATA_FILE, index=False)
except Exception as e:
    st.error(f"Error membaca file Excel: {str(e)}")
    df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    df.to_excel(DATA_FILE, index=False)

# ====================== FRONT PAGE ======================
st.sidebar.title("Menu Navigasi")
page = st.sidebar.radio("Pilih Halaman", ["Well Program Monitoring", "Report Statistik"])

if page == "Well Program Monitoring":
    # ============== WELL PROGRAM MONITORING PAGE ==============
    st.title("Well Program Monitoring")
    
    # Fitur unggah file
    st.subheader("Unggah File Excel")
    uploaded_file = st.file_uploader("Upload file Excel (.xlsx)", type=["xlsx"])

    if uploaded_file:
        try:
            df_uploaded = pd.read_excel(uploaded_file)
            uploaded_columns = df_uploaded.columns.tolist()
            if uploaded_columns != REQUIRED_COLUMNS:
                st.error(f"Struktur kolom tidak sesuai. Harus: {REQUIRED_COLUMNS}, Ditemukan: {uploaded_columns}")
            else:
                errors = []
                for idx, row in df_uploaded.iterrows():
                    if pd.isna(row["Well Name"]):
                        errors.append(f"Baris {idx+2}: Well Name harus diisi")
                    if not pd.isna(row["Program No"]) and row["Program No"] in df["Program No"].values:
                        errors.append(f"Baris {idx+2}: Program No {row['Program No']} sudah ada")
                    if row["Status"] not in VALID_STATUSES:
                        errors.append(f"Baris {idx+2}: Status harus {VALID_STATUSES}")
                    if row["Doc Initiator"] not in VALID_INITIATORS:
                        errors.append(f"Baris {idx+2}: Doc Initiator harus {VALID_INITIATORS}")
                    if row["Approval 1"] not in VALID_APPROVAL1_2:
                        errors.append(f"Baris {idx+2}: Approval 1 harus {VALID_APPROVAL1_2}")
                    if row["Approval 2"] not in VALID_APPROVAL1_2:
                        errors.append(f"Baris {idx+2}: Approval 2 harus {VALID_APPROVAL1_2}")
                    if row["Approval 3"] not in VALID_APPROVAL3:
                        errors.append(f"Baris {idx+2}: Approval 3 harus {VALID_APPROVAL3}")
                    if row["Approval 4"] not in VALID_APPROVAL4:
                        errors.append(f"Baris {idx+2}: Approval 4 harus {VALID_APPROVAL4}")
                    try:
                        creation_date = pd.to_datetime(row["Creation Date"])
                        due_date = pd.to_datetime(row["Due Date"])
                        if pd.isna(creation_date) or pd.isna(due_date):
                            errors.append(f"Baris {idx+2}: Creation Date atau Due Date tidak valid")
                        elif due_date < creation_date:
                            errors.append(f"Baris {idx+2}: Due Date tidak boleh sebelum Creation Date")
                    except:
                        errors.append(f"Baris {idx+2}: Format Creation Date atau Due Date tidak valid")

                if errors:
                    st.error("Kesalahan dalam file:")
                    for err in errors:
                        st.write(err)
                else:
                    df_uploaded["Creation Date"] = pd.to_datetime(df_uploaded["Creation Date"], errors='coerce').dt.strftime("%d-%b-%y")
                    df_uploaded["Due Date"] = pd.to_datetime(df_uploaded["Due Date"], errors='coerce').dt.strftime("%d-%b-%y")
                    st.write("Preview Data:")
                    st.dataframe(df_uploaded[REQUIRED_COLUMNS])
                    if st.button("Submit Data"):
                        df = pd.concat([df, df_uploaded], ignore_index=True)
                        df["No"] = range(1, len(df) + 1)
                        df.to_excel(DATA_FILE, index=False)
                        st.success("Data berhasil disubmit!")
                        st.experimental_rerun()
        except Exception as e:
            st.error(f"Error membaca file: {str(e)}")

    # Form input manual
    st.subheader("Form Input Well Program")

    with st.form("well_program_form"):
        nama_well = st.text_input("Nama Well")
        well_name = st.text_input("Nama Dokumen Well Program (Opsional)")
        program_no = st.text_input("Nomor Program (Opsional)")
        creation_date = st.date_input("Tanggal Submit", value=datetime.today())
        due_date = st.date_input("Due Date", value=datetime.today() + timedelta(days=7))
        initiator = st.selectbox("Document Initiator", VALID_INITIATORS)
        approval1 = st.selectbox("Approval 1", VALID_APPROVAL1_2)
        approval2 = st.selectbox("Approval 2", VALID_APPROVAL1_2)
        approval3 = st.selectbox("Approval 3", VALID_APPROVAL3)
        approval4 = st.selectbox("Approval 4", VALID_APPROVAL4)
        remarks = st.text_input("Remarks")
        save_button = st.form_submit_button("Save")

        if save_button:
            if not nama_well:
                st.error("Nama Well harus diisi!")
            elif program_no and program_no in df["Program No"].values:
                st.error(f"Program No {program_no} sudah ada!")
            elif due_date < creation_date:
                st.error("Due Date tidak boleh sebelum Creation Date!")
            else:
                status = "COMPLETED" if all([approval1, approval2, approval3, approval4]) else "INPROGRESS"
                new_no = len(df) + 1
                new_data = {
                    "No": new_no,
                    "Well Name": nama_well,
                    "Well Program Name": well_name if well_name else "",
                    "Program No": program_no if program_no else "",
                    "Creation Date": creation_date.strftime("%d-%b-%y"),
                    "Due Date": due_date.strftime("%d-%b-%y"),
                    "Status": status,
                    "Doc Initiator": initiator,
                    "Approval 1": approval1,
                    "Approval 2": approval2,
                    "Approval 3": approval3,
                    "Approval 4": approval4,
                    "Remarks": remarks
                }
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                df.to_excel(DATA_FILE, index=False)
                st.success("Data berhasil disimpan!")
                st.experimental_rerun()

    # Fitur edit dan hapus
    st.subheader("Edit / Hapus Data")
    selected_index = st.number_input("Pilih index untuk edit/hapus (No):", min_value=1, max_value=len(df) if not df.empty else 1, step=1)

    if selected_index and not df.empty and not df[df["No"] == selected_index].empty:
        selected_row = df[df["No"] == selected_index].iloc[0]
        with st.form("edit_form"):
            edit_nama_well = st.text_input("Nama Well", selected_row["Well Name"])
            edit_well_name = st.text_input("Nama Dokumen Well Program (Opsional)", selected_row["Well Program Name"])
            edit_program_no = st.text_input("Nomor Program (Opsional)", selected_row["Program No"])
            try:
                edit_creation_date = st.date_input("Tanggal Submit", datetime.strptime(str(selected_row["Creation Date"]), "%d-%b-%y"))
                edit_due_date = st.date_input("Due Date", datetime.strptime(str(selected_row["Due Date"]), "%d-%b-%y") if selected_row["Due Date"] else datetime.today() + timedelta(days=7))
            except (ValueError, TypeError):
                edit_creation_date = st.date_input("Tanggal Submit", datetime.today())
                edit_due_date = st.date_input("Due Date", datetime.today() + timedelta(days=7))
            edit_initiator = st.selectbox("Document Initiator", VALID_INITIATORS,
                                         index=VALID_INITIATORS.index(selected_row["Doc Initiator"]) if selected_row["Doc Initiator"] in VALID_INITIATORS else 0)
            edit_approval1 = st.selectbox("Approval 1", VALID_APPROVAL1_2,
                                         index=VALID_APPROVAL1_2.index(selected_row["Approval 1"]) if selected_row["Approval 1"] in VALID_APPROVAL1_2 else 0)
            edit_approval2 = st.selectbox("Approval 2", VALID_APPROVAL1_2,
                                         index=VALID_APPROVAL1_2.index(selected_row["Approval 2"]) if selected_row["Approval 2"] in VALID_APPROVAL1_2 else 0)
            edit_approval3 = st.selectbox("Approval 3", VALID_APPROVAL3,
                                         index=VALID_APPROVAL3.index(selected_row["Approval 3"]) if selected_row["Approval 3"] in VALID_APPROVAL3 else 0)
            edit_approval4 = st.selectbox("Approval 4", VALID_APPROVAL4,
                                         index=VALID_APPROVAL4.index(selected_row["Approval 4"]) if selected_row["Approval 4"] in VALID_APPROVAL4 else 0)
            edit_remarks = st.text_input("Remarks", selected_row["Remarks"])
            update_button = st.form_submit_button("Update Data")
            delete_button = st.form_submit_button("Hapus Data")

            if update_button:
                if not edit_nama_well:
                    st.error("Nama Well harus diisi!")
                elif edit_program_no and edit_program_no != selected_row["Program No"] and edit_program_no in df["Program No"].values:
                    st.error(f"Program No {edit_program_no} sudah ada!")
                elif edit_due_date < edit_creation_date:
                    st.error("Due Date tidak boleh sebelum Creation Date!")
                else:
                    new_status = "COMPLETED" if all([edit_approval1, edit_approval2, edit_approval3, edit_approval4]) else "INPROGRESS"
                    df.loc[df["No"] == selected_index] = [
                        selected_index,
                        edit_nama_well,
                        edit_well_name if edit_well_name else "",
                        edit_program_no if edit_program_no else "",
                        edit_creation_date.strftime("%d-%b-%y"),
                        edit_due_date.strftime("%d-%b-%y"),
                        new_status,
                        edit_initiator,
                        edit_approval1,
                        edit_approval2,
                        edit_approval3,
                        edit_approval4,
                        edit_remarks
                    ]
                    df.to_excel(DATA_FILE, index=False)
                    st.success("Data berhasil diperbarui!")
                    st.experimental_rerun()

            if delete_button:
                df = df[df["No"] != selected_index].reset_index(drop=True)
                df["No"] = range(1, len(df) + 1)
                df.to_excel(DATA_FILE, index=False)
                st.success("Data berhasil dihapus!")
                st.experimental_rerun()
    else:
        if selected_index:
            st.error("Indeks tidak valid atau tidak ada data!")

elif page == "Report Statistik":
    # ============== REPORT STATISTIK PAGE ==============
    st.title("Report Statistik Well Program")
    
    # Tampilkan data dengan filter
    st.subheader("Data Well Program")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.write(" ")
    with col2:
        filter_status = st.selectbox("Filter Status", ["Semua", "COMPLETED", "INPROGRESS"])
    with col3:
        filter_approval1 = st.selectbox("Filter Approval 1", ["Semua", "Belum Diapprove", "Sudah Diapprove"])
    with col4:
        filter_approval2 = st.selectbox("Filter Approval 2", ["Semua", "Belum Diapprove", "Sudah Diapprove"])
    with col5:
        filter_approval3 = st.selectbox("Filter Approval 3", ["Semua", "Belum Diapprove", "Sudah Diapprove"])
    with col6:
        filter_approval4 = st.selectbox("Filter Approval 4", ["Semua", "Belum Diapprove", "Sudah Diapprove"])

    filtered_df = df.copy()
    if filter_status != "Semua":
        filtered_df = filtered_df[filtered_df["Status"] == filter_status]

    if filter_approval1 == "Belum Diapprove":
        filtered_df = filtered_df[filtered_df["Approval 1"] == ""]
    elif filter_approval1 == "Sudah Diapprove":
        filtered_df = filtered_df[filtered_df["Approval 1"].isin(["KRISTIANTO WIBOWO", "YULIANTO AGUS"])]

    if filter_approval2 == "Belum Diapprove":
        filtered_df = filtered_df[filtered_df["Approval 2"] == ""]
    elif filter_approval2 == "Sudah Diapprove":
        filtered_df = filtered_df[filtered_df["Approval 2"].isin(["KRISTIANTO WIBOWO", "YULIANTO AGUS"])]

    if filter_approval3 == "Belum Diapprove":
        filtered_df = filtered_df[filtered_df["Approval 3"] == ""]
    elif filter_approval3 == "Sudah Diapprove":
        filtered_df = filtered_df[filtered_df["Approval 3"] == "BUDI RIVAI WIJAYA"]

    if filter_approval4 == "Belum Diapprove":
        filtered_df = filtered_df[filtered_df["Approval 4"] == ""]
    elif filter_approval4 == "Sudah Diapprove":
        filtered_df = filtered_df[filtered_df["Approval 4"] == "PE TEAM"]

    ordered_columns = [
        "No", "Well Name", "Well Program Name", "Program No", "Creation Date", "Due Date",
        "Status", "Doc Initiator", "Approval 1", "Approval 2", "Approval 3", "Approval 4", "Remarks"
    ]
    st.dataframe(filtered_df[ordered_columns])

    # Daftar Well yang Belum Diapprove dengan Pengingat
    st.subheader("Daftar Well yang Belum Diapprove dengan Pengingat")

    today = datetime.today()
    unapproved_data = []
    for _, row in filtered_df.iterrows():
        approvals = [
            ("Approval 1", row["Approval 1"]),
            ("Approval 2", row["Approval 2"]),
            ("Approval 3", row["Approval 3"]),
            ("Approval 4", row["Approval 4"])
        ]
        due_date = pd.to_datetime(row["Due Date"], format="%d-%b-%y", errors='coerce')
        if pd.isna(due_date):
            reminder_status = "Invalid Due Date"
        else:
            delta = (due_date - today).days
            if delta < 0:
                reminder_status = "Overdue"
            elif delta <= 3:
                reminder_status = "Approaching Due Date"
            else:
                reminder_status = "On Track"

        for approver, value in approvals:
            if value == "":
                unapproved_data.append({
                    "No": row["No"],
                    "Well Name": row["Well Name"],
                    "Well Program Name": row["Well Program Name"],
                    "Program No": row["Program No"],
                    "Approver": approver,
                    "Creation Date": row["Creation Date"],
                    "Due Date": row["Due Date"],
                    "Reminder Status": reminder_status,
                    "Status": row["Status"]
                })

    unapproved_df = pd.DataFrame(unapproved_data)
    if not unapproved_df.empty:
        st.dataframe(unapproved_df[["No", "Well Name", "Well Program Name", "Program No", "Approver", "Creation Date", "Due Date", "Reminder Status", "Status"]])
    else:
        st.info("Tidak ada well yang belum diapprove berdasarkan filter saat ini.")

    # Statistik dan Grafik
    st.subheader("Statistik Status")
    if not filtered_df.empty:
        status_counts = filtered_df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        total = status_counts["Count"].sum()
        status_counts["Percentage"] = (status_counts["Count"] / total * 100).round(2) if total > 0 else 0

        fig_pie = px.pie(
            status_counts,
            names="Status",
            values="Count",
            title="Persentase Status Well Program (Filtered)",
            color_discrete_map={"COMPLETED": "#2ecc71", "INPROGRESS": "#e74c3c"},
            hover_data=["Percentage"],
            labels={"Percentage": "%"}
        )
        fig_pie.update_traces(textinfo="label+value+percent", textposition="inside")
        st.plotly_chart(fig_pie, use_container_width=True)

        no_approval3 = len(filtered_df[filtered_df["Approval 3"] == ""])
        no_approval4 = len(filtered_df[filtered_df["Approval 4"] == ""])
        approval_data = pd.DataFrame({
            "Approver": ["BUDI RIVAI WIJAYA", "PE TEAM"],
            "Belum Approve": [no_approval3, no_approval4]
        })
        
        total_unapproved = no_approval3 + no_approval4
        percentages = [0, 0] if total_unapproved == 0 else [(no_approval3 / total_unapproved * 100), (no_approval4 / total_unapproved * 100)]

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=approval_data["Approver"],
            y=approval_data["Belum Approve"],
            text=[f"{val}<br>{perc:.1f}%" for val, perc in zip(approval_data["Belum Approve"], percentages)],
            textposition="auto",
            marker_color=["#3498db", "#9b59b6"],
            name="Belum Approve"
        ))
        fig_bar.update_layout(
            title="Jumlah Well Program Belum Diapprove (Filtered)",
            xaxis_title="Approver",
            yaxis_title="Belum Diapprove",
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("Status Approval oleh BUDI RIVAI WIJAYA")
        budi_unapproved = len(filtered_df[filtered_df["Approval 3"] == ""])
        budi_approved = len(filtered_df[filtered_df["Approval 3"] == "BUDI RIVAI WIJAYA"])
        approval_status = pd.DataFrame({
            "Status": ["Belum Diapprove", "Sudah Diapprove"],
            "Jumlah": [budi_unapproved, budi_approved]
        })

        fig_budi = px.bar(
            approval_status,
            x="Status",
            y="Jumlah",
            title="Jumlah Well Program Belum/Sudah Diapprove oleh BUDI RIVAI WIJAYA",
            text="Jumlah",
            color="Status",
            color_discrete_map={"Belum Diapprove": "#e74c3c", "Sudah Diapprove": "#2ecc71"}
        )
        fig_budi.update_traces(textposition="auto")
        st.plotly_chart(fig_budi, use_container_width=True)

        st.subheader("Jumlah Well Program yang Dibuat per Bulan")
        filtered_df["Creation Date"] = pd.to_datetime(filtered_df["Creation Date"], format="%d-%b-%y", errors='coerce')
        filtered_df["Month-Year"] = filtered_df["Creation Date"].dt.strftime("%b %Y")
        monthly_counts = filtered_df["Month-Year"].value_counts().reset_index()
        monthly_counts.columns = ["Month-Year", "Jumlah Well"]
        monthly_counts["Date"] = pd.to_datetime(monthly_counts["Month-Year"], format="%b %Y", errors='coerce')
        monthly_counts = monthly_counts.sort_values("Date")

        fig_monthly = px.bar(
            monthly_counts,
            x="Month-Year",
            y="Jumlah Well",
            title="Jumlah Well Program yang Dibuat per Bulan",
            text="Jumlah Well",
            color_discrete_sequence=["#1f77b4"]
        )
        fig_monthly.update_traces(textposition="auto")
        st.plotly_chart(fig_monthly, use_container_width=True)

        st.subheader("Jumlah Well Program per Bulan (Berdasarkan Pilihan)")
        month_year_options = monthly_counts["Month-Year"].tolist() if not monthly_counts.empty else ["Tidak ada data"]
        selected_month_year = st.selectbox("Pilih Bulan", month_year_options)

        if selected_month_year != "Tidak ada data":
            selected_wells = filtered_df[filtered_df["Month-Year"] == selected_month_year]
            selected_counts = {"BUDI RIVAI WIJAYA": 0, "PE TEAM": 0}
            for _, row in selected_wells.iterrows():
                if row["Approval 3"] != "":
                    selected_counts["BUDI RIVAI WIJAYA"] += 1
                if row["Approval 4"] != "":
                    selected_counts["PE TEAM"] += 1

            selected_data = pd.DataFrame({
                "Approver": ["BUDI RIVAI WIJAYA", "PE TEAM"],
                "Jumlah Well": [selected_counts["BUDI RIVAI WIJAYA"], selected_counts["PE TEAM"]]
            })

            fig_selected = px.bar(
                selected_data,
                x="Approver",
                y="Jumlah Well",
                title=f"Jumlah Well Program pada {selected_month_year}",
                color="Approver",
                color_discrete_map={"BUDI RIVAI WIJAYA": "#3498db", "PE TEAM": "#9b59b6"},
                text="Jumlah Well"
            )
            fig_selected.update_traces(textposition="auto")
            st.plotly_chart(fig_selected, use_container_width=True)

    else:
        st.info("Belum ada data untuk ditampilkan.")