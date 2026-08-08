import streamlit as st
import pandas as pd
import re
from supabase import create_client, Client

# ---------------------------------------------------------
# 1. إعداد الصفحة وإخفاء الهيدر بالكامل (إخفاء الأزرار والسهم)
# ---------------------------------------------------------
st.set_page_config(page_title="Work System | Aurther", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    /* إخفاء الشريط العلوي بالكامل دون استثناء (حذف السهم وأزرار GitHub والشير) */
    [data-testid="stHeader"] {
        display: none !important;
    }
    footer {
        display: none !important;
    }
    .viewerBadge_container__1QSob, 
    [data-testid="stStatusWidget"],
    #MainMenu {
        display: none !important;
    }
    
    /* ستايل كروت العرض والتصميم العصري */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .header-card {
        background: linear-gradient(135deg, #161b22, #21262d);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    /* تحسين شكل التبويبات العلوية البديلة للقائمة */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #161b22;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        border-radius: 8px;
        color: #8b949e;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #238636 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. إعداد الاتصال بـ Supabase
# ---------------------------------------------------------
SUPABASE_URL = "https://igskxyazuomofeqvkwcy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlnc2t4eWF6dW9tb2ZlcXZrd2N5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYxNTkyNTksImV4cCI6MjEwMTczNTI1OX0.HadeqymBYWETFaauKYFNtlD-ahg3GfoOGoH0XKu_mWg"

@st.cache_resource
def init_supabase() -> Client:
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase = init_supabase()

# ---------------------------------------------------------
# 3. جلب البيانات وحالة الاتصال
# ---------------------------------------------------------
def get_all_members():
    if not supabase:
        return pd.DataFrame(), False
    try:
        res = supabase.table("work_members").select("*").execute()
        data = res.data if res.data else []
        if data:
            df = pd.DataFrame(data)
            if "referrer" in df.columns:
                df["referred_by"] = df["referrer"]
            if "received_by" not in df.columns:
                df["received_by"] = "غير محدد"
            if "date" in df.columns:
                df["created_at"] = df["date"]
            return df, True
        return pd.DataFrame(columns=["id", "nickname", "phone", "referred_by", "received_by", "created_at"]), True
    except Exception:
        return pd.DataFrame(), False

def add_member_to_supabase(nickname, phone, referred_by, received_by):
    if not supabase:
        return False, "غير متصل بقاعدة البيانات!"
    try:
        clean_p = re.sub(r'\D', '', str(phone).strip())
        new_entry = {
            "nickname": nickname.strip(),
            "phone": clean_p,
            "referrer": referred_by.strip() if referred_by else "مباشر (بدون دعوة)",
            "received_by": received_by.strip() if received_by else "غير محدد",
            "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        supabase.table("work_members").insert(new_entry).execute()
        return True, f"تم تسجيل [{nickname}] بنجاح."
    except Exception as e:
        return False, f"خطأ في التسجيل: {e}"

def delete_member_from_supabase(phone):
    if supabase:
        try:
            supabase.table("work_members").delete().eq("phone", str(phone)).execute()
            return True
        except:
            return False
    return False

df_members, is_online = get_all_members()

# قائمة المستضيفين والإحصائيات
if not df_members.empty and "referred_by" in df_members.columns:
    hosts_list = [h for h in df_members["referred_by"].dropna().unique().tolist() if h and h != "مباشر (بدون دعوة)"]
    valid_m = df_members[(df_members["referred_by"] != "مباشر (بدون دعوة)") & (df_members["referred_by"] != "")]
    if not valid_m.empty:
        df_ref = valid_m["referred_by"].value_counts().reset_index()
        df_ref.columns = ["host", "count"]
    else:
        df_ref = pd.DataFrame(columns=["host", "count"])
else:
    hosts_list = []
    df_ref = pd.DataFrame(columns=["host", "count"])

# ---------------------------------------------------------
# 4. كارت العنوان الرئيسي ومؤشر الحالة
# ---------------------------------------------------------
status_badge = "🟢 متصل بقاعدة البيانات (Online)" if is_online else "🔴 غير متصل (Offline)"
status_color = "#25d366" if is_online else "#ff4d4d"

st.markdown(f"""
<div class="header-card">
    <h1 style="color: #58a6ff; margin: 0; font-size: 28px;">⚡ WORK SYSTEM</h1>
    <p style="color: #8b949e; margin: 5px 0 10px 0;">👑 Founder: Aurther</p>
    <span style="background: rgba(255,255,255,0.05); padding: 5px 15px; border-radius: 20px; color: {status_color}; font-weight: bold; font-size: 13px;">
        {status_badge}
    </span>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. التبويبات العلوية البديلة للقائمة الجانبية
# ---------------------------------------------------------
tab_dash, tab_add, tab_hosts, tab_search, tab_settings = st.tabs([
    "📊 لوحة التحكم",
    "➕ إضافة عضو",
    "👥 المستضيفين",
    "🔍 استعلام",
    "⚙️ السجل والإعدادات"
])

# --- 1. لوحة التحكم ---
with tab_dash:
    st.subheader("📊 لوحة التحكم والأعضاء")
    col1, col2, col3 = st.columns(3)
    col1.metric("الأعضاء", len(df_members))
    col2.metric("المستضيفين", len(hosts_list))
    top_h = df_ref.iloc[0]["host"] if not df_ref.empty else "لا يوجد"
    top_c = int(df_ref.iloc[0]["count"]) if not df_ref.empty else 0
    col3.metric("أقوى مستضيف", f"{top_h} ({top_c})")

    st.divider()
    if not df_members.empty:
        cols_to_show = ["nickname", "phone", "referred_by", "received_by", "created_at"]
        existing_cols = [c for c in cols_to_show if c in df_members.columns]
        st.dataframe(
            df_members[existing_cols].rename(columns={
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

# --- 2. إضافة عضو ---
with tab_add:
    st.subheader("➕ تسجيل عضو جديد")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nickname = col1.text_input("اللقب:")
        phone = col2.text_input("رقم الهاتف:")

        col3, col4 = st.columns(2)
        with col3:
            selected_host = st.selectbox("صاحب الدعوة (المستضيف):", ["مباشر (بدون دعوة)"] + hosts_list)
            custom_host = st.text_input("أو مستضيف جديد (يدوياً):")
        with col4:
            selected_receiver = st.selectbox("تم الاستقبال من طرف (الاستقبال):", ["غير محدد"] + hosts_list)
            custom_receiver = st.text_input("أو مسؤول استقبال جديد (يدوياً):")

        if st.form_submit_button("تأكيد تسجيل العضو"):
            if nickname and phone:
                final_host = custom_host.strip() if custom_host.strip() else selected_host
                final_receiver = custom_receiver.strip() if custom_receiver.strip() else selected_receiver
                success, msg = add_member_to_supabase(nickname.strip(), phone.strip(), final_host, final_receiver)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("يرجى ملء اللقب ورقم الهاتف.")

# --- 3. المستضيفين ---
with tab_hosts:
    st.subheader("👥 قائمة المستضيفين والإحالات")
    sub_t1, sub_t2 = st.tabs(["ترتيب المستضيفين", "أعضاء المستضيف"])
    
    with sub_t1:
        if not df_ref.empty:
            st.dataframe(df_ref.rename(columns={"host": "المستضيف", "count": "عدد الأعضاء"}), use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد إحالات بعد.")
            
    with sub_t2:
        if not df_ref.empty:
            host_choice = st.selectbox("اختر المستضيف لعرض أعضائه:", df_ref["host"].tolist())
            invited = df_members[df_members["referred_by"] == host_choice]
            cols_to_show = ["nickname", "phone", "received_by", "created_at"]
            existing_cols = [c for c in cols_to_show if c in invited.columns]
            st.dataframe(invited[existing_cols].rename(columns={"nickname": "اللقب", "phone": "الرقم", "received_by": "تم الاستقبال من طرف", "created_at": "التاريخ"}), use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد بيانات.")

# --- 4. استعلام ---
with tab_search:
    st.subheader("🔍 استعلام سريع عن عضو")
    if not df_members.empty:
        search_target = st.selectbox("اختر العضو للاستعلام:", df_members["nickname"].tolist())
        target_info = df_members[df_members["nickname"] == search_target].iloc[0]

        st.success(f"""
        📌 **بيانات العضو:** [{target_info['nickname']}]  
        📞 **الرقم:** {target_info['phone']}  
        👑 **صاحب الدعوة (المستضيف):** {target_info.get('referred_by', 'مباشر')}  
        🤝 **تم الاستقبال من طرف:** {target_info.get('received_by', 'غير محدد')}  
        📅 **تاريخ الانضمام:** {target_info.get('created_at', '')}
        """)

        clean_num = re.sub(r"\D", "", str(target_info["phone"]))
        st.markdown(f"[📲 تواصل مباشر عبر الواتساب](https://wa.me/{clean_num})")
    else:
        st.info("لا يوجد أعضاء في قاعدة البيانات.")

# --- 5. السجل والإعدادات ---
with tab_settings:
    st.subheader("⚙️ إدارة السجل والنظام")
    if not df_members.empty:
        member_to_del = st.selectbox("اختر العضو للحذف (سيحذف من الاستقبال والورك فوراً):", ["-- اختر --"] + df_members["nickname"].tolist())
        if member_to_del != "-- اختر --":
            target_m = df_members[df_members["nickname"] == member_to_del].iloc[0]
            if st.button("تأكيد الحذف النهائي", type="primary"):
                if delete_member_from_supabase(target_m["phone"]):
                    st.success(f"تم حذف {member_to_del} بنجاح من النظامين.")
                    st.rerun()
                else:
                    st.error("حدث خطأ أثناء الحذف.")
    else:
        st.info("السجل فارغ.")
