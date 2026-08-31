import streamlit as st
import pandas as pd
import re
from supabase import create_client, Client
import base64
import datetime
from io import BytesIO

# مكتبات الـ PDF واللغة العربية
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

# ---------------------------------------------------------
# 1. إعداد الصفحة الأساسي
# ---------------------------------------------------------
st.set_page_config(page_title="KONUHA | Work System", page_icon="🍃", layout="wide")

# ---------------------------------------------------------
# 2. تصميم الـ UI/UX (CSS خيالي، تأثيرات زجاجية، وخطوط)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
    }

    /* إخفاء شريط Streamlit */
    [data-testid="stHeader"], footer, #MainMenu { display: none !important; }
    
    /* خلفية الموقع داكنة مع تأثيرات */
    .stApp {
        background-color: #0b0f19;
        background-image: radial-gradient(circle at 15% 50%, rgba(20, 184, 166, 0.08), transparent 25%),
                          radial-gradient(circle at 85% 30%, rgba(16, 185, 129, 0.08), transparent 25%);
        color: #e2e8f0;
    }
    
    /* تصميم الزجاج الشفاف (Glassmorphism) للكروت */
    .glass-card {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    
    /* اسم النقابة النيون */
    .neon-text {
        font-size: 42px;
        font-weight: 900;
        color: #fff;
        text-shadow: 0 0 10px #10b981, 0 0 20px #10b981, 0 0 40px #047857;
        margin-bottom: 0;
        letter-spacing: 2px;
    }
    
    /* التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.03);
        padding: 10px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #94a3b8;
        border-radius: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. نظام الحماية بباسورد (Login System)
# ---------------------------------------------------------
# الباسورد الخاص بالإداريين (تقدر تغيره)
ADMIN_PASSWORD = "123" 

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown('<div class="glass-card"><h1 class="neon-text">KONUHA</h1><p>بوابة الدخول للإدارة</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("كلمة المرور 🔒:", type="password")
        if st.button("تسجيل الدخول", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة!")
    st.stop() # يوقف الكود هنا إذا ما مسجل دخول

# ---------------------------------------------------------
# 4. إعداد الاتصال بقاعدة البيانات
# ---------------------------------------------------------
SUPABASE_URL = "https://igskxyazuomofeqvkwcy.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_KEY_HERE" # حط المفتاح مالك هنا

@st.cache_resource
def init_supabase() -> Client:
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase = init_supabase()

def get_all_members():
    if not supabase: return pd.DataFrame(), False
    try:
        res = supabase.table("work_members").select("*").execute()
        data = res.data if res.data else []
        if data:
            df = pd.DataFrame(data)
            df['referred_by'] = df.get('referrer', 'مباشر')
            df['received_by'] = df.get('received_by', 'غير محدد')
            df['created_at'] = df.get('date', '')
            # ترتيب الأسماء أبجدياً
            if "nickname" in df.columns:
                df = df.sort_values(by="nickname", ascending=True)
            return df, True
        return pd.DataFrame(), True
    except:
        return pd.DataFrame(), False

def add_member(nickname, phone, referred_by, received_by):
    try:
        clean_p = re.sub(r'\D', '', str(phone).strip())
        new_entry = {
            "nickname": nickname.strip(),
            "phone": clean_p,
            "referrer": referred_by.strip() if referred_by else "مباشر",
            "received_by": received_by.strip() if received_by else "غير محدد",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        supabase.table("work_members").insert(new_entry).execute()
        return True
    except:
        return False

df_members, is_online = get_all_members()

# ---------------------------------------------------------
# 5. الهيدر الرئيسي للموقع (بعد الدخول)
# ---------------------------------------------------------
status_icon = "🟢" if is_online else "🔴"
st.markdown(f"""
<div class="glass-card">
    <h1 class="neon-text">🍃 KONUHA</h1>
    <p style="color: #94a3b8; font-size: 18px; margin-top: 10px;">Work System & Management</p>
    <div style="margin-top:15px; font-size:14px; color:#10b981;">{status_icon} Database Connected</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. استخراج ملف PDF (بترتيب أبجدي)
# ---------------------------------------------------------
def create_pdf(dataframe):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # يجب توفير ملف خط اسمه cairo.ttf في نفس مجلد السكربت ليدعم العربي
    try:
        pdf.add_font('Cairo', '', 'cairo.ttf', uni=True)
        pdf.set_font('Cairo', '', 14)
    except:
        pdf.set_font('Arial', '', 12) # بديل إذا ماكو ملف خط

    # العنوان
    title = "سجل ألقاب نقابة KONUHA"
    reshaped_title = arabic_reshaper.reshape(title)
    bidi_title = get_display(reshaped_title)
    pdf.cell(200, 10, txt=bidi_title, ln=True, align='C')
    pdf.ln(10)

    # إضافة الألقاب
    for index, row in dataframe.iterrows():
        text = f"اللقب: {row['nickname']} | المشرف: {row['referred_by']}"
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        pdf.cell(200, 10, txt=bidi_text, ln=True, align='R')
    
    return pdf.output(dest='S').encode('latin1')

# ---------------------------------------------------------
# 7. التبويبات الرئيسية
# ---------------------------------------------------------
tab_dash, tab_add, tab_hosts, tab_search, tab_export = st.tabs([
    "📊 لوحة القيادة", "➕ إضافة عضو", "👥 المستضيفين", "🔍 استعلام الألقاب", "📥 استخراج PDF"
])

with tab_dash:
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='glass-card'><h3>👥 الأعضاء</h3><h2>{len(df_members)}</h2></div>", unsafe_allow_html=True)
    
    hosts_count = len(df_members['referred_by'].unique()) if not df_members.empty else 0
    col2.markdown(f"<div class='glass-card'><h3>👑 المشرفين</h3><h2>{hosts_count}</h2></div>", unsafe_allow_html=True)
    
    if not df_members.empty:
        st.dataframe(df_members[['nickname', 'phone', 'referred_by', 'received_by', 'created_at']], use_container_width=True, hide_index=True)

with tab_add:
    st.subheader("إضافة عضو جديد للنقابة")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nick = col1.text_input("اللقب:")
        phone = col2.text_input("رقم الهاتف:")
        ref = col1.text_input("من طرف (المستضيف):")
        rec = col2.text_input("استقبل من طرف (الاستقبال):")
        
        if st.form_submit_button("➕ تسجيل العضو"):
            if nick and phone:
                if add_member(nick, phone, ref, rec):
                    st.toast('✅ تم تسجيل العضو بنجاح!', icon='🎉')
                    st.rerun()
                else:
                    st.error("حدث خطأ!")
            else:
                st.toast('⚠️ يرجى ملء اللقب والرقم', icon='⚠️')

with tab_hosts:
    st.subheader("إحصائيات المشرفين")
    if not df_members.empty:
        host_counts = df_members['referred_by'].value_counts().reset_index()
        host_counts.columns = ['المشرف', 'عدد الأعضاء']
        st.dataframe(host_counts, use_container_width=True, hide_index=True)

with tab_search:
    st.subheader("فحص الألقاب (مرتبة أبجدياً)")
    if not df_members.empty:
        all_nicknames = df_members['nickname'].tolist()
        search_target = st.selectbox("ابحث عن لقب للتأكد من توفره:", ["-- اختر أو ابحث --"] + all_nicknames)
        
        if search_target != "-- اختر أو ابحث --":
            info = df_members[df_members['nickname'] == search_target].iloc[0]
            st.info(f"📌 اللقب: {info['nickname']} | 📞 الرقم: {info['phone']} | 👑 المشرف: {info['referred_by']}")
            st.markdown(f"[💬 راسل العضو واتساب](https://wa.me/{info['phone']})")

with tab_export:
    st.subheader("📄 استخراج أرشيف KONUHA")
    st.write("استخراج جميع الألقاب المسجلة بالترتيب الأبجدي كملف PDF.")
    
    if not df_members.empty:
        if st.button("توليد ملف PDF", type="primary"):
            try:
                pdf_bytes = create_pdf(df_members)
                st.download_button(
                    label="📥 تحميل الملف",
                    data=pdf_bytes,
                    file_name=f"KONUHA_Members_{datetime.date.today()}.pdf",
                    mime="application/pdf"
                )
                st.toast("✅ تم التوليد بنجاح! اضغط للتحميل.", icon="📄")
            except Exception as e:
                st.error("ملاحظة: لكي يعمل الـ PDF باللغة العربية، يرجى وضع ملف خط باسم 'cairo.ttf' في نفس المجلد.")
    else:
        st.warning("لا توجد بيانات لاستخراجها.")
