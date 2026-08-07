import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# 1. إعدادات الصفحة وتصميم سايبر هاكر الحديث
# ---------------------------------------------------------
st.set_page_config(
    page_title="WORK // CYBER DATABASE",
    page_icon="⚡",
    layout="wide"
)

# تصميم CSS احترافي (أزرق غامق جداً + أخضر نيون + أزرق كهربائي)
st.markdown("""
    <style>
    /* الخلفية الرئيسية */
    .stApp {
        background-color: #020713;
        color: #00ff66;
        font-family: 'Fira Code', 'Segoe UI', monospace;
    }
    
    /* العناوين والروابط */
    h1, h2, h3, h4, label, .stMarkdown {
        color: #00ff66 !important;
        font-family: 'Fira Code', monospace;
    }
    
    /* إحصائيات الهيدر */
    div[data-testid="stMetricValue"] {
        color: #00f0ff !important;
        font-size: 2.2rem !important;
        font-weight: bold;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #071226 0%, #030a17 100%);
        border: 1px solid #00f0ff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.25);
    }

    /* الأزرار العادية */
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

    /* الحقول القابلة للإدخال */
    input, select, textarea {
        background-color: #050e1f !important;
        color: #ffffff !important;
        border: 1px solid #00f0ff !important;
        border-radius: 6px !important;
    }

    /* كروت العرض الهكر */
    .cyber-card {
        background: #061329;
        border: 1px solid #00ff66;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.2);
        margin-bottom: 15px;
    }
    
    .host-card {
        background: #031024;
        border: 1px solid #00f0ff;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }

    /* زر الواتساب */
    .wa-btn {
        display: inline-block;
        width: 100%;
        text-align: center;
        background-color: #25D366;
        color: white !important;
        padding: 12px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        box-shadow: 0 0 10px rgba(37, 211, 102, 0.4);
    }
    .wa-btn:hover {
        background-color: #1ebc57;
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
        return True, f"تم إضافة العضو [{nickname}] إلى قاعدة البيانات بنجاح!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, f"اللقب [{nickname}] مسجل بـالفعل في القروب!"

def delete_member(member_id):
    conn = sqlite3.connect('work_system.db')
    c = conn.cursor()
    c.execute('DELETE FROM members WHERE id = ?', (member_id,))
    conn.commit()
    conn.close()

def get_all_members():
    conn = sqlite3.connect('work_system.db')
    df = pd.read_sql_query('SELECT * FROM members ORDER BY id DESC', conn)
    conn.close()
    return df

def get_referral_stats():
    conn = sqlite3.connect('work_system.db')
    query = '''
        SELECT referred_by as 'المستضيف (صاحب الدعوة)', COUNT(*) as 'عدد الأعضاء المضافين'
        FROM members
        WHERE referred_by != 'مباشر (بدون دعوة)' AND referred_by != ''
        GROUP BY referred_by
        ORDER BY COUNT(*) DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ---------------------------------------------------------
# 3. الهيدر والإحصائيات الرئيسية
# ---------------------------------------------------------
st.title("⚡ WORK SYSTEM // نظام وورك الإداري")
st.caption("> WORK GROUP MEMBER TRACKER & HOST REFERRAL SYSTEM")

df_members = get_all_members()
df_ref = get_referral_stats()

m1, m2, m3 = st.columns(3)
with m1:
    st.metric(label="📊 إجمالي الأعضاء المسجلين", value=len(df_members))

top_host = df_ref.iloc[0]['المستضيف (صاحب الدعوة)'] if not df_ref.empty else "لا يوجد"
top_count = int(df_ref.iloc[0]['عدد الأعضاء المضافين']) if not df_ref.empty else 0

with m2:
    st.metric(label="👑 أقوى مستضيف (Top Host)", value=top_host)
with m3:
    st.metric(label="🔥 أعلى إحالات تم جلبها", value=top_count)

st.write("---")

# ---------------------------------------------------------
# 4. الأقسام والتبويبات
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⚡ [1] تسجيل عضو جديد", 
    "🏆 [2] ترتيب المستضيفين والإحالات", 
    "👥 [3] قائمة المستضيفين والتفاصيل",
    "🔍 [4] استعلام عن عضو",
    "📂 [5] إدارة السجل وحذف الأعضاء"
])

# --- Tab 1: تسجيل عضو جديد ---
with tab1:
    st.subheader("> تسجيل عضو جديد بالقروب")
    
    with st.form("add_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            nickname = st.text_input("اللقب في القروب:", placeholder="مثال: ميكاسا / LARS")
        with col_b:
            phone = st.text_input("رقم الهاتف (مع المفتاح):", placeholder="مثال: 9647700000000")
            
        existing_nicknames = df_members['nickname'].tolist() if not df_members.empty else []
        
        referred_by_select = st.selectbox(
            "اختر المستضيف (دخل من طرف مَن؟):",
            ["مباشر (بدون دعوة)"] + existing_nicknames
        )
        
        custom_ref = st.text_input("أو اكتب اسم مستضيف جديد يدوياً:")
        
        submit_btn = st.form_submit_button("EXECUTE_REGISTER // تسجيل البيانات")
        
        if submit_btn:
            final_host = custom_ref.strip() if custom_ref.strip() else referred_by_select
            if nickname and phone:
                success, msg = add_member(nickname.strip(), phone.strip(), final_host)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("الرجاء كتابة اللقب ورقم الهاتف كاملاً!")

# --- Tab 2: ترتيب المستضيفين ---
with tab2:
    st.subheader("> ترتيب المستضيفين حسب الأعضاء المضافين (REFERRAL LEADERBOARD)")
    
    if not df_ref.empty:
        # إضافة رتب للأعضاء
        df_ref_ranked = df_ref.copy()
        ranks = ["🥇 المركز الأول", "🥈 المركز الثاني", "🥉 المركز الثالث"] + [f"المركز {i}" for i in range(4, len(df_ref_ranked) + 1)]
        df_ref_ranked.insert(0, "الترتيب", ranks[:len(df_ref_ranked)])
        
        st.dataframe(df_ref_ranked, use_container_width=True, hide_index=True)
        st.bar_chart(df_ref.set_index('المستضيف (صاحب الدعوة)'))
    else:
        st.info("لا توجد إحالات أو دعوات مسجلة حتى الآن.")

# --- Tab 3: تفاصيل المستضيفين والأعضاء القادمين عن طريقهم ---
with tab3:
    st.subheader("> قائمة المستضيفين واستعراض الأعضاء القادمين من طرفهم")
    
    if not df_ref.empty:
        hosts_list = df_ref['المستضيف (صاحب الدعوة)'].tolist()
        selected_host = st.selectbox("اختر المستضيف للبحث عن أعضائه:", hosts_list)
        
        if selected_host:
            invited_df = df_members[df_members['referred_by'] == selected_host][['id', 'nickname', 'phone', 'created_at']]
            
            st.markdown(f"""
                <div class="host-card">
                    <h4>👑 المستضيف: <span style="color:#00f0ff;">{selected_host}</span></h4>
                    <p>إجمالي الأعضاء المضافين عن طريقه: <strong>{len(invited_df)} عضو</strong></p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**الأعضاء القادمين من طرف [{selected_host}]:**")
            st.dataframe(invited_df, use_container_width=True, hide_index=True)
    else:
        st.info("لا يوجد مستضيفين مسجلين حالياً.")

# --- Tab 4: الاستعلام عن عضو ---
with tab4:
    st.subheader("> البحث عن بيانات عضو معين")
    
    if not df_members.empty:
        selected_m = st.selectbox("اختر لقب العضو من القائمة:", df_members['nickname'].tolist())
        
        m_info = df_members[df_members['nickname'] == selected_m].iloc[0]
        clean_num = ''.join(filter(str.isdigit, str(m_info['phone'])))
        
        st.markdown(f"""
            <div class="cyber-card">
                <h3>&gt; MEMBER: {m_info['nickname']}</h3>
                <p><strong>🆔 ID النظام:</strong> #{m_info['id']}</p>
                <p><strong>📱 رقم الهاتف:</strong> {m_info['phone']}</p>
                <p><strong>👤 دخل من طرف (المستضيف):</strong> <span style="color:#00f0ff;">{m_info['referred_by']}</span></p>
                <p><strong>📅 تاريخ التسجيل:</strong> {m_info['created_at']}</p>
                <br>
                <a class="wa-btn" href="https://wa.me/{clean_num}" target="_blank">📲 تواصل مباشر عبر الواتساب</a>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("لا يوجد أعضاء في قاعدة البيانات.")

# --- Tab 5: السجل وحذف الأعضاء ---
with tab5:
    st.subheader("> السجل الكامل وإدارة حذف الأعضاء")
    
    if not df_members.empty:
        search_kw = st.text_input("🔍 فلترة السجل (بالاسم، الرقم، أو المستضيف):")
        
        display_df = df_members.copy()
        if search_kw:
            display_df = display_df[
                display_df['nickname'].str.contains(search_kw, case=False, na=False) |
                display_df['phone'].str.contains(search_kw, case=False, na=False) |
                display_df['referred_by'].str.contains(search_kw, case=False, na=False)
            ]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.write("---")
        st.subheader("🗑️ حذف عضو من النظام")
        
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            member_to_del = st.selectbox("اختر العضو المراد مسحه:", ["-- اختر العضو --"] + df_members['nickname'].tolist())
        
        if member_to_del != "-- اختر العضو --":
            target_data = df_members[df_members['nickname'] == member_to_del].iloc[0]
            st.warning(f"هل أنت تأكد من مسح العضو [{target_data['nickname']}] (رقم: {target_data['phone']})؟")
            
            with col_del2:
                st.write(" ")
                st.write(" ")
                if st.button("❌ تأكيد الحذف"):
                    delete_member(target_data['id'])
                    st.success(f"تم حذف العضو [{target_data['nickname']}] بنجاح.")
                    st.rerun()
    else:
        st.info("القاعدة فارغة تماماً.")
    
