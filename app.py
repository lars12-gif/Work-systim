import streamlit as st
import pandas as pd
import re
from supabase import create_client, Client
import datetime
from io import BytesIO

# مكتبات الـ PDF واللغة العربية والرسم (PNG)
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------
# 1. إعداد الصفحة الأساسي
# ---------------------------------------------------------
st.set_page_config(page_title="KONUHA | Work System By Aurther", page_icon="👑", layout="wide")

# ---------------------------------------------------------
# 2. تصميم الـ UI/UX وحقوقك بكل مكان
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
    }

    [data-testid="stHeader"], footer, #MainMenu { display: none !important; }
    
    .stApp {
        background-color: #0b0f19;
        background-image: radial-gradient(circle at 15% 50%, rgba(20, 184, 166, 0.08), transparent 25%),
                          radial-gradient(circle at 85% 30%, rgba(16, 185, 129, 0.08), transparent 25%);
        color: #e2e8f0;
        padding-bottom: 60px;
    }
    
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
    }
    
    .neon-text {
        font-size: 42px;
        font-weight: 900;
        color: #fff;
        text-shadow: 0 0 10px #10b981, 0 0 20px #10b981, 0 0 40px #047857;
        margin-bottom: 0;
        letter-spacing: 2px;
    }
    
    .aurther-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(11, 15, 25, 0.85);
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(16, 185, 129, 0.3);
        color: #10b981;
        text-align: center;
        padding: 12px;
        font-size: 15px;
        font-weight: 900;
        z-index: 9999;
        letter-spacing: 1px;
    }

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
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
    }
</style>

<div class="aurther-footer">
    👑 Developed & Designed By Aurther | KONUHA System © 2026
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. نظام الحماية بباسورد (Login)
# ---------------------------------------------------------
ADMIN_PASSWORD = "123" 

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div class="glass-card">
        <h1 class="neon-text">KONUHA</h1>
        <p>بوابة الدخول للإدارة</p>
        <p style="color:#10b981; font-weight:bold; font-size:12px;">🛡️ Secured By Aurther</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("كلمة المرور 🔒:", type="password")
        if st.button("تسجيل الدخول", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة!")
    st.stop()

# ---------------------------------------------------------
# 4. إعداد الاتصال بقاعدة البيانات
# ---------------------------------------------------------
SUPABASE_URL = "https://igskxyazuomofeqvkwcy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlnc2t4eWF6dW9tb2ZlcXZrd2N5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYxNTkyNTksImV4cCI6MjEwMTczNTI1OX0.HadeqymBYWETFaauKYFNtlD-ahg3GfoOGoH0XKu_mWg"

@st.cache_resource
def init_supabase() -> Client:
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

supabase = init_supabase()

def get_all_members():
    if not supabase: 
        return pd.DataFrame(), False
    try:
        res = supabase.table("work_members").select("*").execute()
        data = res.data if res.data else []
        if data:
            df = pd.DataFrame(data)
            df['referred_by'] = df.get('referrer', 'مباشر')
            df['received_by'] = df.get('received_by', 'غير محدد')
            df['created_at'] = df.get('date', '')
            if "nickname" in df.columns:
                df = df.sort_values(by="nickname", ascending=True)
            return df, True
        return pd.DataFrame(columns=["nickname", "phone", "referred_by", "received_by", "created_at"]), True
    except Exception:
        return pd.DataFrame(), False

def add_member(nickname, phone, referred_by, received_by):
    if not supabase:
        return False, "غير متصل بقاعدة البيانات!"
    try:
        clean_p = re.sub(r'\D', '', str(phone).strip())
        new_entry = {
            "nickname": nickname.strip(),
            "phone": clean_p,
            "referrer": referred_by.strip() if referred_by else "مباشر",
            "received_by": received_by.strip() if received_by else "غير محدد",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        supabase.table("work_members").insert(new_entry).execute()
        return True, "تم التسجيل بنجاح"
    except Exception as e:
        return False, f"خطأ من سوبابيس: {e}"

# --- الدالة الجديدة للحذف الجماعي ---
def delete_members(phones_list):
    if not supabase: return False
    try:
        # يمسح كل الأعضاء اللي أرقامهم موجودة بالقائمة دفعة وحدة
        supabase.table("work_members").delete().in_("phone", phones_list).execute()
        return True
    except Exception as e:
        return False

df_members, is_online = get_all_members()

# ---------------------------------------------------------
# 5. الهيدر الرئيسي
# ---------------------------------------------------------
status_badge = "🟢 متصل بقاعدة البيانات (Online)" if is_online else "🔴 غير متصل بقاعدة البيانات (Offline)"
status_color = "#10b981" if is_online else "#ef4444"

st.markdown(f"""
<div class="glass-card">
    <h1 class="neon-text">🍃 KONUHA</h1>
    <p style="color: #94a3b8; font-size: 18px; margin-top: 10px;">Work System & Management</p>
    <div style="margin-top:5px; font-size:12px; color:#3b82f6;">👑 Founder: Aurther</div>
    <div style="margin-top:15px; font-size:14px; color:{status_color}; font-weight: bold;">{status_badge}</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. دوال الاستخراج (PDF, Excel, PNG)
# ---------------------------------------------------------
def create_pdf(dataframe):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    try:
        pdf.add_font('Janna', fname='janna.ttf')
        pdf.set_font('Janna', size=14)
    except:
        pdf.set_font('Arial', size=14)

    title = "سجل أعضاء نقابة KONUHA"
    reshaped_title = arabic_reshaper.reshape(title)
    bidi_title = get_display(reshaped_title)
    pdf.cell(190, 10, text=bidi_title, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)

    for index, row in dataframe.iterrows():
        text = f"اللقب: {row['nickname']} | الرقم: {row['phone']} | المشرف: {row['referred_by']} | الاستقبال: {row['received_by']}"
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        pdf.cell(190, 10, text=bidi_text, new_x="LMARGIN", new_y="NEXT", align='R')
    
    pdf.set_y(-20)
    try:
        pdf.set_font('Janna', size=10)
    except:
        pdf.set_font('Arial', size=10)
    footer_text = get_display(arabic_reshaper.reshape("👑 Developed By Aurther - KONUHA 2026"))
    pdf.cell(0, 10, text=footer_text, align='C')

    return bytes(pdf.output())

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='أعضاء KONUHA')
    return output.getvalue()

def create_png(dataframe):
    width = 1300
    header_height = 200
    row_height = 70
    margin_bottom = 120 
    height = header_height + (len(dataframe) * row_height) + margin_bottom

    img = Image.new('RGB', (width, height), color='#0b0f19')
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype('janna.ttf', 75)
        sub_font = ImageFont.truetype('janna.ttf', 35)
        text_font = ImageFont.truetype('janna.ttf', 26)
        footer_font = ImageFont.truetype('janna.ttf', 30)
    except:
        title_font = sub_font = text_font = footer_font = ImageFont.load_default()

    title_text = "KONUHA"
    draw.text((width//2, 80), title_text, font=title_font, fill="#10b981", anchor="mm")
    
    sub_text = f"سجل الأعضاء الرسمي | التاريخ: {datetime.date.today()}"
    reshaped_sub = get_display(arabic_reshaper.reshape(sub_text))
    draw.text((width//2, 150), reshaped_sub, font=sub_font, fill="#94a3b8", anchor="mm")

    draw.line([(100, 190), (1200, 190)], fill="#10b981", width=3)

    y_pos = header_height + 20
    for index, row in dataframe.iterrows():
        row_text = f"اللقب: {row['nickname']}   |   الرقم: {row['phone']}   |   المشرف: {row['referred_by']}   |   الاستقبال: {row['received_by']}"
        reshaped_text = get_display(arabic_reshaper.reshape(row_text))
        
        draw.rounded_rectangle([(80, y_pos - 10), (1220, y_pos + 50)], radius=12, fill="#111827", outline="#1f2937", width=2)
        draw.text((1200, y_pos + 20), reshaped_text, font=text_font, fill="#e2e8f0", anchor="rm")
        y_pos += row_height

    footer_text = "⚡ Powered & Developed by Aurther - 2026 👑"
    draw.text((width//2, height - 50), footer_text, font=footer_font, fill="#3b82f6", anchor="mm")

    output = BytesIO()
    img.save(output, format='PNG')
    return output.getvalue()

# ---------------------------------------------------------
# 7. التبويبات الرئيسية
# ---------------------------------------------------------
tab_dash, tab_add, tab_hosts, tab_search, tab_export, tab_delete = st.tabs([
    "📊 لوحة القيادة", "➕ إضافة عضو", "👥 المشرفين", "🔍 استعلام", "📥 تصدير", "🗑️ إدارة وحذف"
])

with tab_dash:
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='glass-card'><h3>👥 الأعضاء</h3><h2>{len(df_members)}</h2></div>", unsafe_allow_html=True)
    
    hosts_count = len(df_members['referred_by'].unique()) if not df_members.empty else 0
    col2.markdown(f"<div class='glass-card'><h3>👑 المشرفين</h3><h2>{hosts_count}</h2></div>", unsafe_allow_html=True)
    
    if not df_members.empty:
        st.dataframe(df_members[['nickname', 'phone', 'referred_by', 'received_by', 'created_at']].rename(columns={
            'nickname': 'اللقب', 'phone': 'الرقم', 'referred_by': 'صاحب الدعوة', 'received_by': 'مسؤول الاستقبال', 'created_at': 'التاريخ'
        }), use_container_width=True, hide_index=True)

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
                success, msg = add_member(nick, phone, ref, rec)
                if success:
                    st.toast('👑 Aurther System: تم تسجيل العضو بنجاح!', icon='🎉')
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.toast('⚠️ يرجى ملء اللقب والرقم', icon='⚠️')

with tab_hosts:
    st.subheader("إحصائيات المشرفين (شاملة)")
    if not df_members.empty:
        df_ref = df_members['referred_by'].value_counts().reset_index()
        df_ref.columns = ['المشرف', 'الدعوات']
        
        df_rec = df_members['received_by'].value_counts().reset_index()
        df_rec.columns = ['المشرف', 'الاستقبالات']
        
        df_hosts_merged = pd.merge(df_ref, df_rec, on='المشرف', how='outer').fillna(0)
        df_hosts_merged['الدعوات'] = df_hosts_merged['الدعوات'].astype(int)
        df_hosts_merged['الاستقبالات'] = df_hosts_merged['الاستقبالات'].astype(int)
        df_hosts_merged['المجموع الكلي'] = df_hosts_merged['الدعوات'] + df_hosts_merged['الاستقبالات']
        
        df_hosts_merged = df_hosts_merged.sort_values(by='المجموع الكلي', ascending=False)
        st.dataframe(df_hosts_merged, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد بيانات حالياً.")

with tab_search:
    st.subheader("فحص الألقاب (مرتبة أبجدياً)")
    if not df_members.empty:
        all_nicknames = df_members['nickname'].tolist()
        search_target = st.selectbox("ابحث عن لقب للتأكد من توفره:", ["-- اختر أو ابحث --"] + all_nicknames)
        
        if search_target != "-- اختر أو ابحث --":
            info = df_members[df_members['nickname'] == search_target].iloc[0]
            st.info(f"📌 اللقب: {info['nickname']} | 📞 الرقم: {info['phone']} | 👑 المشرف: {info['referred_by']} | 🤝 الاستقبال: {info['received_by']}")
            st.markdown(f"[💬 راسل العضو واتساب](https://wa.me/{info['phone']})")

with tab_export:
    st.subheader("📄 استخراج أرشيف KONUHA")
    
    if not df_members.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("ملف PDF (للطباعة):")
            try:
                pdf_bytes = create_pdf(df_members)
                st.download_button(label="📥 تحميل PDF", data=pdf_bytes, file_name=f"KONUHA_{datetime.date.today()}.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"خطأ: {e}")
        
        with col2:
            st.write("ملف Excel (للأرشفة):")
            excel_bytes = to_excel(df_members[['nickname', 'phone', 'referred_by', 'received_by', 'created_at']].rename(columns={'nickname': 'اللقب', 'phone': 'الرقم', 'referred_by': 'صاحب الدعوة', 'received_by': 'الاستقبال', 'created_at': 'التاريخ'}))
            st.download_button(label="📊 تحميل Excel", data=excel_bytes, file_name=f"KONUHA_{datetime.date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            
        with col3:
            st.write("ملف PNG (للمشاركة فخم):")
            try:
                png_bytes = create_png(df_members)
                st.download_button(label="🖼️ تحميل صورة", data=png_bytes, file_name=f"KONUHA_{datetime.date.today()}.png", mime="image/png", use_container_width=True)
            except Exception as e:
                st.error(f"تأكد من تنصيب مكتبة Pillow. {e}")
    else:
        st.warning("لا توجد بيانات لاستخراجها.")

# --- التبويب الجديد للحذف ---
with tab_delete:
    st.subheader("🗑️ طرد الأعضاء القدامى (حذف نهائي)")
    st.error("⚠️ تنبيه: أي عضو تحذفه منا راح ينمسح نهائياً من الداتا بيس وما يرجع.")
    
    if not df_members.empty:
        # ربط الاسم بالرقم حتى نمسح بالرقم ونضمن الدقة
        member_dict = dict(zip(df_members['nickname'], df_members['phone']))
        all_nicks = df_members['nickname'].tolist()
        
        selected_nicks = st.multiselect("📌 حدد الأعضاء اللي تريد تطردهم (تقدر تختار أكثر من واحد):", options=all_nicks)
        
        if st.button("🚨 تأكيد الحذف", type="primary"):
            if selected_nicks:
                phones_to_delete = [member_dict[nick] for nick in selected_nicks]
                success = delete_members(phones_to_delete)
                if success:
                    st.toast('👑 Aurther System: تم مسح الأعضاء المحددین بنجاح!', icon='🗑️')
                    st.rerun()
                else:
                    st.error("حدث خطأ أثناء الاتصال بقاعدة البيانات لغرض الحذف.")
            else:
                st.warning("رجاءً حدد عضو واحد على الأقل قبل ما تضغط على زر الحذف.")
    else:
        st.info("النظام فارغ حالياً، ماكو أحد تطرده.")
