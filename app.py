import pandas as pd
import re
import streamlit as st
from supabase import Client, create_client

# ---------------------------------------------------------
# 1. إعداد الصفحة (Native Minimalist) مع إخفاء الأشرطة بالـ CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Work System | Aurther", page_icon="⚡", layout="wide"
)

st.markdown(
    """
<style>
    /* إخفاء الشريط العلوي وأزرار GitHub والعلامات المائية */
    [data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    .viewerBadge_container__1QSob, [data-testid="stStatusWidget"], #MainMenu { display: none !important; }
</style>
""",
    unsafe_allow_html=True,
)

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


# --- دوال التعامل مع البيانات ---
def get_all_members():
  if not supabase:
    return pd.DataFrame()
  try:
    res = supabase.table("members").select("*").execute()
    data = res.data if res.data else []
    if data:
      df = pd.DataFrame(data)
      if "referrer" in df.columns and "referred_by" not in df.columns:
        df["referred_by"] = df["referrer"]
      if "received_by" not in df.columns:
        df["received_by"] = "غير محدد"
      if "date" in df.columns and "created_at" not in df.columns:
        df["created_at"] = df["date"]
      return df
    return pd.DataFrame(
        columns=[
            "id",
            "nickname",
            "phone",
            "referred_by",
            "received_by",
            "created_at",
        ]
    )
  except:
    return pd.DataFrame()


def get_all_hosts():
  # استخراج قائمة المستضيفين تلقائياً من الإحالات أو إرجاع القائمة الافتراضية
  df_m = get_all_members()
  if not df_m.empty and "referred_by" in df_m.columns:
    hosts = (
        df_m["referred_by"]
        .dropna()
        .unique()
        .tolist()
    )
    hosts = [h for h in hosts if h and h != "مباشر (بدون دعوة)"]
    return pd.DataFrame({"id": range(1, len(hosts) + 1), "host_name": hosts})
  return pd.DataFrame(columns=["id", "host_name"])


def add_member(nickname, phone, referred_by, received_by):
  if not supabase:
    return False, "غير متصل بقاعدة البيانات!"
  try:
    clean_p = re.sub(r"\D", "", str(phone).strip())
    new_entry = {
        "nickname": nickname.strip(),
        "phone": clean_p,
        "referrer": (
            referred_by.strip() if referred_by else "مباشر (بدون دعوة)"
        ),
        "received_by": received_by.strip() if received_by else "غير محدد",
        "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    supabase.table("members").insert(new_entry).execute()
    return True, f"تم تسجيل [{nickname}] بنجاح."
  except Exception as e:
    return False, f"خطأ في التسجيل: {e}"


def delete_member_by_phone(phone):
  if supabase:
    try:
      supabase.table("members").delete().eq("phone", str(phone)).execute()
      return True
    except:
      return False
  return False


def get_referral_stats():
  df_m = get_all_members()
  if not df_m.empty and "referred_by" in df_m.columns:
    valid_m = df_m[
        (df_m["referred_by"] != "مباشر (بدون دعوة)")
        & (df_m["referred_by"] != "")
    ]
    if not valid_m.empty:
      ref_counts = (
          valid_m["referred_by"]
          .value_counts()
          .reset_index()
      )
      ref_counts.columns = ["host", "count"]
      return ref_counts
  return pd.DataFrame(columns=["host", "count"])


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
# 4. أقسام الصفحة (القديمة نفسها بدون أي تعديل بالشكل)
# ---------------------------------------------------------

if menu == "📊 لوحة التحكم":
  st.header("📊 لوحة التحكم")
  st.caption("نظرة سريعة على إحصائيات النظام.")

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
        final_host = (
            custom_host.strip() if custom_host.strip() else selected_host
        )
        final_receiver = (
            custom_receiver.strip()
            if custom_receiver.strip()
            else selected_receiver
        )

        success, msg = add_member(
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

  tab_del_member, tab_del_host = st.tabs(
      ["🗑️ حذف عضو", "🗑️ إدارة قائمة المستضيفين/الاستقبال"]
  )

  with tab_del_member:
    st.subheader("حذف عضو من السجل")
    if not df_members.empty:
      member_to_del = st.selectbox(
          "اختر العضو للحذف:", ["-- اختر --"] + df_members["nickname"].tolist()
      )
      if member_to_del != "-- اختر --":
        target_m = df_members[df_members["nickname"] == member_to_del].iloc[0]
        if st.button("تأكيد الحذف النهائي", type="primary"):
          if delete_member_by_phone(target_m["phone"]):
            st.success(f"تم حذف {member_to_del} بنجاح من النظامين.")
            st.rerun()
          else:
            st.error("حدث خطأ أثناء الحذف.")
    else:
      st.info("السجل فارغ.")

  with tab_del_host:
    st.info(
        "تتم إدارة قائمة المستضيفين تلقائياً بناءً على الأعضاء والإحالات"
        " المسجلة."
      )
        
