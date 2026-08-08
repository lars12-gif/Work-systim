import streamlit as st
import pandas as pd
import re
from supabase import create_client, Client

# ---------------------------------------------------------
# 1. إعداد الصفحة وتعديل الـ CSS لإخفاء GitHub وإبقاء السهم
# ---------------------------------------------------------
st.set_page_config(page_title="Work System | Aurther", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    /* إخفاء زر GitHub والخيارات الإضافية فقط من الشريط العلوي مع إبقاء زر السهم شغال */
    [data-testid="stActionButtonElements"], 
    [data-testid="stAppDeployButton"], 
    #MainMenu {
        display: none !important;
    }
    
    /* إخفاء الحقوق والعلامة المائية بالأسفل */
    footer {
        display: none !important;
    }
    .viewerBadge_container__1QSob, 
    [data-testid="stStatusWidget"] {
        display: none !important;
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
# 3. دوال الجلب والحفظ المباشر
# ---------------------------------------------------------
def get_all_members():
    if not supabase:
        return pd.DataFrame(), False
    try:
        res = supabase.table("members").select("*").execute()
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
        supabase.table("members").insert(new_entry).execute()
        return True, f"تم تسجيل [{nickname}] بنجاح."
    except Exception as e:
        return False, f"خطأ في التسجيل: {e}"

def delete_member_from_supabase(phone):
    if supabase:
        try:
            supabase.table("members").delete().eq("phone", str(phone)).execute()
            return True
        except:
            return False
    return False

# جلب البيانات وحالة الاتصال
df_members, is_online = get_all_members()

# قائمة المستضيفين تلقائياً من الإحالات
if not df_members.empty and "referred_by" in df_members.columns:
    hosts_list = [h for h in df_members["referred_by"].dropna().unique().tolist() if h and h != "مباشر (بدون دعوة)"]
else:
    hosts_list = []

# إحصائيات المستضيفين (النقاط)
if not df_members.empty and "referred_by" in df_members.columns:
    valid_m = df_members[(df_members["referred_by"] != "مباشر (بدون دعوة)") & (df_members["referred_by"] != "")]
    if not valid_m.empty:
        df_ref = valid_m["referred_by"].value_counts().reset_index()
        df_ref.columns = ["host", "count"]
    else:
        df_ref = pd.DataFrame(columns=["host", "count"])
else:
    df_ref = pd.DataFrame(columns=["host", "count"])

# ---------------------------------------------------------
# 4. القائمة الجانبية ومؤشر الاتصال
# ---------------------------------------------------------
st.sidebar.title("⚡ Work System")
st.sidebar.markdown("**👑 Founder:** Aurther")

# مؤشر حالة الاتصال الأونلاين/أوفلاين
if is_online:
    st.sidebar.markdown("<div style='color: #25d366; font-weight: bold;'>🟢 متصل بقاعدة البيانات (Online)</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<div style='color: #ff4d4d; font-weight: bold;'>🔴 غير متصل (Offline)</div>", unsafe_allow_html=True)

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

# ---------------------------------------------------------
# 5. أقسام الصفحة
# ---------------------------------------------------------

if menu == "📊 لوحة التحكم":
    st.header("📊 لوحة التحكم")
    st.caption("نظرة سريعة على إحصائيات النظام.")

    col1, col2, col3 = st.columns(3)
    col1.metric("الأعضاء", len(df_members))
    col2.metric("المستضيفين", len(hosts_list))

    top_h = df_ref.iloc[0]["host"] if not df_ref.empty else "لا يوجد"
    top_c = int(df_ref.iloc[0]["count"]) if not df_ref.empty else 0
    col3.metric("أقوى مستضيف", f"{top_h} ({top_c})")

    st.divider()
    st.subheader("آخر المنضمين")
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

elif menu == "➕ إضافة عضو":
    st.header("➕ تسجيل عضو جديد")

    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nickname = col1.text_input("اللقب:")
        phone = col2.text_input("رقم الهاتف:")

        col3, col4 = st.columns(2)
        with col3:
            selected_host = st.selectbox(
                "صاحب الدعوة (المستضيف):", ["مباشر (بدون دعوة)"] + hosts_list
            )
            custom_host = st.text_input("أو مستضيف جديد (يدوياً):")

        with col4:
            selected_receiver = st.selectbox(
                "تم الاستقبال من طرف (الاستقبال):", ["غير محدد"] + hosts_list
            )
            custom_receiver = st.text_input("أو مسؤل استقبال جديد (يدوياً):")

        if st.form_submit_button("تسجيل العضو"):
            if nickname and phone:
                final_host = custom_host.strip() if custom_host.strip() else selected_host
                final_receiver = custom_receiver.strip() if custom_receiver.strip() else selected_receiver

                success, msg = add_member_to_supabase(
                    nickname.strip(), phone.strip(), final_host, final_receiver
                )
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
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
            host_choice = st.selectbox(
                "اختر المستضيف لعرض أعضائه:", df_ref["host"].tolist()
            )
            invited = df_members[df_members["referred_by"] == host_choice]
            cols_to_show = ["nickname", "phone", "received_by", "created_at"]
            existing_cols = [c for c in cols_to_show if c in invited.columns]
            st.dataframe(
                invited[existing_cols].rename(columns={
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
        search_target = st.selectbox(
            "اختر العضو للاستعلام:", df_members["nickname"].tolist()
        )
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

elif menu == "⚙️ السجل والإعدادات":
    st.header("⚙️ إدارة السجل والنظام")

    st.subheader("🗑️ حذف عضو من السجل الموحد")
    if not df_members.empty:
        member_to_del = st.selectbox(
            "اختر العضو للحذف (سيحذف من الاستقبال والورك فوراً):", ["-- اختر --"] + df_members["nickname"].tolist()
        )
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
            
