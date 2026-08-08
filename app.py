import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------
# 1. إعداد الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="Work System | Aurther", page_icon="⚡", layout="wide")

# ---------------------------------------------------------
# 2. الربط مع Google Sheets
# ---------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_file("bellona-504904-2c178e02693d.json", scopes=SCOPES)
    return gspread.authorize(creds)

def get_sheet(sheet_name):
    client = get_gspread_client()
    sh = client.open("BELLONA_DB")
    return sh.worksheet(sheet_name)

def get_all_members():
    try:
        sheet = get_sheet("members")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame(columns=["phone", "nickname", "referrer", "received_by", "date"])
        df.rename(columns={"referrer": "referred_by", "date": "created_at"}, inplace=True)
        return df
    except Exception as e:
        return pd.DataFrame(columns=["phone", "nickname", "referred_by", "received_by", "created_at"])

def get_all_hosts():
    try:
        sheet = get_sheet("hosts")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame(columns=["host_name"])
        return df
    except Exception as e:
        return pd.DataFrame(columns=["host_name"])

def add_host_to_sheet(host_name):
    sheet = get_sheet("hosts")
    sheet.append_row([host_name])

def add_member_to_sheet(nickname, phone, referred_by, received_by):
    sheet = get_sheet("members")
    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([str(phone), str(nickname), str(referred_by), str(received_by), now_str])

def delete_member_by_phone(phone):
    sheet = get_sheet("members")
    cell = sheet.find(str(phone))
    if cell:
        sheet.delete_rows(cell.row)

def delete_host_by_name(host_name):
    sheet = get_sheet("hosts")
    cell = sheet.find(str(host_name))
    if cell:
        sheet.delete_rows(cell.row)

def get_referral_stats():
    df = get_all_members()
    if df.empty or "referred_by" not in df.columns:
        return pd.DataFrame(columns=["host", "count"])
    filtered = df[(df["referred_by"] != "مباشر (بدون دعوة)") & (df["referred_by"] != "")]
    if filtered.empty:
        return pd.DataFrame(columns=["host", "count"])
    stats = filtered["referred_by"].value_counts().reset_index()
    stats.columns = ["host", "count"]
    return stats

# ---------------------------------------------------------
# 3. القائمة الجانبية
# ---------------------------------------------------------
st.sidebar.title("⚡ Work System")
st.sidebar.markdown("**👑 Founder:** Aurther")
st.sidebar.divider()

menu = st.sidebar.radio(
    "القائمة",
    [
        "📊 لوحة التحكم",
        "➕ إضافة عضو",
        "👥 المستضيفين",
        "🔍 استعلام",
        "⚙️ السجل والإعدادات",
    ],
)

df_members = get_all_members()
df_hosts = get_all_hosts()
df_ref = get_referral_stats()

# ---------------------------------------------------------
# 4. أقسام الصفحة
# ---------------------------------------------------------
if menu == "📊 لوحة التحكم":
    st.header("📊 لوحة التحكم")
    st.caption("نظرة سريعة على إحصائيات النظام اللحظية من Google Sheets.")

    col1, col2, col3 = st.columns(3)
    col1.metric("الأعضاء", len(df_members))
    col2.metric("المستضيفين", len(df_hosts))

    top_h = df_ref.iloc[0]["host"] if not df_ref.empty else "لا يوجد"
    top_c = int(df_ref.iloc[0]["count"]) if not df_ref.empty else 0
    col3.metric("أقوى مستضيف", f"{top_h} ({top_c})")

    st.divider()
    st.subheader("آخر المنضمين")
    if not df_members.empty:
        st.dataframe(
            df_members[[
                "nickname",
                "phone",
                "referred_by",
                "received_by",
                "created_at",
            ]].rename(columns={
                "nickname": "اللقب",
                "phone": "الرقم",
                "referred_by": "صاحب الدعوة",
                "received_by": "مسؤول الاستقبال",
                "created_at": "التاريخ",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("النظام فارغ حالياً.")

elif menu == "➕ إضافة عضو":
    st.header("➕ تسجيل عضو جديد")

    hosts_list = df_hosts["host_name"].tolist() if not df_hosts.empty else []

    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nickname = col1.text_input("اللقب:")
        phone = col2.text_input("رقم الهاتف:")

        col3, col4 = st.columns(2)
        with col3:
            selected_host = st.selectbox("صاحب الدعوة (المستضيف):", ["مباشر (بدون دعوة)"] + hosts_list)
            custom_host = st.text_input("أو مستضيف جديد (يدوياً):")

        with col4:
            selected_receiver = st.selectbox("مسؤول الاستقبال:", ["غير محدد"] + hosts_list)
            custom_receiver = st.text_input("أو مسؤول استقبال جديد (يدوياً):")

        if st.form_submit_button("تسجيل العضو"):
            if nickname and phone:
                final_host = custom_host.strip() if custom_host.strip() else selected_host
                if custom_host.strip() and custom_host.strip() not in hosts_list:
                    add_host_to_sheet(final_host)

                final_receiver = custom_receiver.strip() if custom_receiver.strip() else selected_receiver
                if custom_receiver.strip() and custom_receiver.strip() not in hosts_list:
                    add_host_to_sheet(final_receiver)

                add_member_to_sheet(nickname.strip(), phone.strip(), final_host, final_receiver)
                st.success(f"تم تسجيل [{nickname}] بنجاح.")
                st.rerun()
            else:
                st.warning("يرجى ملء اللقب ورقم الهاتف.")

elif menu == "👥 المستضيفين":
    st.header("👥 قائمة المستضيفين والإحالات")

    tab1, tab2 = st.tabs(["ترتيب المستضيفين", "أعضاء المستضيف"])

    with tab1:
        if not df_ref.empty:
            st.dataframe(
                df_ref.rename(columns={"host": "المستضيف", "count": "عدد الأعضاء"}),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("لا توجد إحالات بعد.")

    with tab2:
        if not df_ref.empty:
            host_choice = st.selectbox("اختر المستضيف لعرض أعضائه:", df_ref["host"].tolist())
            invited = df_members[df_members["referred_by"] == host_choice]
            st.dataframe(
                invited[[
                    "nickname",
                    "phone",
                    "received_by",
                    "created_at",
                ]].rename(columns={
                    "nickname": "اللقب",
                    "phone": "الرقم",
                    "received_by": "تم الاستقبال من طرف",
                    "created_at": "التاريخ",
                }),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("لا توجد بيانات.")

elif menu == "🔍 استعلام":
    st.header("🔍 استعلام سريع عن عضو")

    if not df_members.empty:
        search_target = st.selectbox("اختر العضو للاستعلام:", df_members["nickname"].tolist())
        target_info = df_members[df_members["nickname"] == search_target].iloc[0]

        st.success(f"""
        📌 **بيانات العضو:** [{target_info['nickname']}]  
        📞 **الرقم:** {target_info['phone']}  
        👑 **صاحب الدعوة (المستضيف):** {target_info['referred_by']}  
        🤝 **تم الاستقبال من طرف:** {target_info.get('received_by', 'غير محدد')}  
        📅 **تاريخ الانضمام:** {target_info['created_at']}
        """)

        clean_num = "".join(filter(str.isdigit, str(target_info["phone"])))
        st.markdown(f"[📲 تواصل مباشر عبر الواتساب](https://wa.me/{clean_num})")
    else:
        st.info("لا يوجد أعضاء في قاعدة البيانات.")

elif menu == "⚙️ السجل والإعدادات":
    st.header("⚙️ إدارة السجل والنظام")

    tab_del_member, tab_del_host = st.tabs(["🗑️ حذف عضو", "🗑️ إدارة قائمة المستضيفين/الاستقبال"])

    with tab_del_member:
        st.subheader("حذف عضو من السجل")
        if not df_members.empty:
            member_to_del = st.selectbox("اختر العضو للحذف:", ["-- اختر --"] + df_members["nickname"].tolist())
            if member_to_del != "-- اختر --":
                target_m = df_members[df_members["nickname"] == member_to_del].iloc[0]
                if st.button("تأكيد الحذف النهائي", type="primary"):
                    delete_member_by_phone(target_m["phone"])
                    st.success(f"تم حذف {member_to_del} بنجاح.")
                    st.rerun()
        else:
            st.info("السجل فارغ.")

    with tab_del_host:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("إضافة اسم للقائمة")
            with st.form("add_h_form", clear_on_submit=True):
                new_h = st.text_input("الاسم (مستضيف / استقبال):")
                if st.form_submit_button("إضافة"):
                    if new_h:
                        add_host_to_sheet(new_h.strip())
                        st.success(f"تمت إضافة [{new_h}] بنجاح.")
                        st.rerun()

        with col2:
            st.subheader("حذف اسم من القائمة")
            if not df_hosts.empty:
                host_to_del = st.selectbox("اختر الاسم للحذف:", ["-- اختر --"] + df_hosts["host_name"].tolist())
                if host_to_del != "-- اختر --":
                    if st.button("حذف الاسم", type="primary"):
                        delete_host_by_name(host_to_del)
                        st.success(f"تم حذف {host_to_del} بنجاح.")
                        st.rerun()
            else:
                st.info("القائمة فارغة.")
  
