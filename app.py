import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# 1. إعدادات الصفحة وتصميم الهاكرز (Cyber Theme)
# ---------------------------------------------------------
st.set_page_config(
    page_title="WORK // SYSTEM DATABASE",
    page_icon="⚡",
    layout="wide"
)

# تنسيق CSS مخصص للنمط الكحلي الداكن والأخضر النيون
st.markdown("""
    <style>
    .stApp {
        background-color: #020712;
        color: #00ff66;
        font-family: 'Courier New', monospace;
    }
    
    h1, h2, h3, label, .stMarkdown {
        color: #00ff66 !important;
        font-family: 'Courier New', monospace;
    }
    
    div[data-testid="stMetricValue"] {
        color: #00f0ff !important;
        font-size: 1.8rem !important;
    }
    
    div[data-testid="stMetric"] {
        background-color: #071226;
        border: 1px solid #00f0ff;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
    }
    
    .stButton>button {
        background-color: transparent;
        color: #00ff66;
        border: 2px solid #00ff66;
        border-radius: 6px;
        font-weight: bold;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #00ff66;
        color: #000000;
        box-shadow: 0 0 15px #00ff66;
    }

    input, select, textarea {
        background-color: #020b18 !important;
        color: #ffffff !important;
        border: 1px solid #00f0ff !important;
    }

    .stDataFrame {
        border: 1px solid #00f0ff;
        border-radius: 6px;
    }

    .cyber-card {
        background-color: #071226;
        border: 1px solid #00ff66;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.2);
        margin-top: 10px;
    }
    
    .wa-btn {
        display: block;
        text-align: center;
        background-color: #25D366;
        color: white !important;
        padding: 10px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. إدارة قاعدة البيانات (SQLite)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect('work_system.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            referred_by TEXT DEFAULT 'مباشر (بدون دعوة)',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def add_member(nickname, phone, referred_by):
    conn = sqlite3.connect('work_system.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO members (nickname, phone, referred_by) VALUES (?, ?, ?)',
                  (nickname, phone, referred_by if referred_by else 'مباشر (بدون دعوة)'))
        conn.commit()
        conn.close()
        return True, f"تم تسجيل العضو [{nickname}] بنجاح!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, f"اللقب [{nickname}] مسجل بالفعل في القاعدة!"

def get_all_members():
    conn = sqlite3.connect('work_system.db')
    df = pd.read_sql_query('SELECT * FROM members ORDER BY id DESC', conn)
    conn.close()
    return df

def get_referral_stats():
    conn = sqlite3.connect('work_system.db')
    query = '''
        SELECT referred_by as 'صاحب الدعوة', COUNT(*) as 'عدد الأشخاص'
        FROM members
        WHERE referred_by != 'مباشر (بدون دعوة)' AND referred_by != ''
        GROUP BY referred_by
        ORDER BY COUNT(*) DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ---------------------------------------------------------
# 3. الهيدر والإحصائيات
# ---------------------------------------------------------
st.title("⚡ WORK SYSTEM // نظام وورك")
st.caption("> SYSTEM DATABASE & REFERRAL TRACKER [CYBER EDITION]")

df_members = get_all_members()
df_ref = get_referral_stats()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="إجمالي الأعضاء", value=len(df_members))

top_inviter = df_ref.iloc[0]['صاحب الدعوة'] if not df_ref.empty else "لا يوجد"
top_count = int(df_ref.iloc[0]['عدد الأشخاص']) if not df_ref.empty else 0

with col2:
    st.metric(label="أكثر شخص جلب أعضاء", value=top_inviter)
with col3:
    st.metric(label="أعلى عدد إحالات", value=top_count)

st.divider()

# ---------------------------------------------------------
# 4. التبويبات والواجهات
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ [1] تسجيل عضو جديد", 
    "🏆 [2] قائمة الإحالات", 
    "🔍 [3] استعلام وتفاصيل العضو",
    "📂 [4] السجل الكامل"
])

# Tab 1: تسجيل عضو
with tab1:
    st.subheader("> إدخال بيانات العضو الجديد")
    
    with st.form("register_form", clear_on_submit=True):
        nickname = st.text_input("اللقب (اسم العضو في القروب):", placeholder="مثال: ميكاسا / LARS")
        phone = st.text_input("رقم الهاتف (مع رمز الدولة):", placeholder="مثال: 9647700000000")
        
        existing_nicknames = df_members['nickname'].tolist() if not df_members.empty else []
        referred_by = st.selectbox(
            "دخل من طرف مَن؟ (اختر من الأعضاء أو اترك الخيار الأول إذا دخل مباشرة):",
            ["مباشر (بدون دعوة)"] + existing_nicknames
        )
        
        custom_ref = st.text_input("أو اكتب اللقب يدوياً إذا لم يكن بالقائمة:")
        
        submitted = st.form_submit_button("EXECUTE_REGISTER // تسجيل العضو")
        
        if submitted:
            final_ref = custom_ref.strip() if custom_ref.strip() else referred_by
            if nickname and phone:
                success, msg = add_member(nickname.strip(), phone.strip(), final_ref)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("الرجاء كتابة اللقب ورقم الهاتف!")

# Tab 2: قائمة الإحالات
with tab2:
    st.subheader("> قائمة أكثر الأشخاص دعماً للقروب (REFERRAL_LEADERBOARD)")
    
    if not df_ref.empty:
        st.dataframe(df_ref, use_container_width=True)
        st.bar_chart(df_ref.set_index('صاحب الدعوة'))
    else:
        st.info("لا توجد إحالات مسجلة حتى الآن.")

# Tab 3: استعلام عن عضو
with tab3:
    st.subheader("> الاستعلام السريع عن بيانات عضو")
    
    if not df_members.empty:
        selected_member = st.selectbox("اختر لقب العضو للاستعلام:", df_members['nickname'].tolist())
        member_data = df_members[df_members['nickname'] == selected_member].iloc[0]
        
        clean_phone = ''.join(filter(str.isdigit, str(member_data['phone'])))
        
        st.markdown(f"""
            <div class="cyber-card">
                <h3>&gt; MEMBER_PROFILE: {member_data['nickname']}</h3>
                <p><strong>📱 رقم الهاتف:</strong> {member_data['phone']}</p>
                <p><strong>👤 دخل من طرف:</strong> {member_data['referred_by']}</p>
                <p><strong>📅 تاريخ الانضمام:</strong> {member_data['created_at']}</p>
                <a class="wa-btn" href="https://wa.me/{clean_phone}" target="_blank">📲 فتح محادثة الواتساب المباشرة</a>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("لا يوجد أعضاء مسجلين في القاعدة حتى الآن.")

# Tab 4: السجل الكامل
with tab4:
    st.subheader("> السجل الكامل لجميع أعضاء WORK")
    
    search_query = st.text_input("🔍 بحث وفلترة باللقب أو الرقم أو الداعي:")
    
    if not df_members.empty:
        if search_query:
            filtered_df = df_members[
                df_members['nickname'].str.contains(search_query, case=False, na=False) |
                df_members['phone'].str.contains(search_query, case=False, na=False) |
                df_members['referred_by'].str.contains(search_query, case=False, na=False)
            ]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df_members, use_container_width=True)
    else:
        st.info("القاعدة فارغة حالياً.")
  
