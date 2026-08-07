import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# 1. إعداد الصفحة وتصميم هادئ ومودرن (Modern Slate)
# ---------------------------------------------------------
st.set_page_config(
    page_title="WORK // SYSTEM BY AURTHER",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم عصري مريح للعين (Dark Slate + Soft Cyan & Indigo)
st.markdown("""
    <style>
    /* الخلفية العامة */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    }

    /* الشريط الجانبي */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155 !important;
    }

    /* العناوين والنصوص */
    h1, h2, h3, h4, label, .stMarkdown {
        color: #f8fafc !important;
        font-family: system-ui, -apple-system, sans-serif;
    }

    /* الإحصائيات (Metrics) */
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* حقول الإدخال والقوائم */
    input, select, textarea {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    /* الأزرار المودرن */
    .stButton>button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 16px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }

    /* الكروت العصريّة (Modern Cards) */
    .modern-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 16px;
    }
    
    .founder-badge {
        background: linear-gradient(135deg, #6366f1 0%, #3b82f6 100%);
        color: #ffffff;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        display: inline-block;
        margin-top: 8px;
        letter-spacing: 0.5px;
    }

    .badge-soft {
        background-color: #0284c7;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* زر الواتساب */
    .wa-btn {
        display: block;
        text-align: center;
        background-color: #10b981;
        color: white !important;
        padding: 10px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        margin-top: 12px;
        transition: 0.2s;
    }
    .wa-btn:hover {
        background-color: #059669;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. إدارة قاعدة البيانات (SQLite) مع تحويل ID الصريح
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS hosts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host_name TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- دالة الحذف المضمنة مع تحويل ID الصريح لضمان التنفيذ ---
def delete_member_by_id(member_id):
    conn = sqlite3.connect('work_system.db')
    c = conn.cursor()
    c.execute('DELETE FROM members WHERE id = ?', (int(member_id),))
    conn.commit()
    conn.close()

def delete_host_by_id(host_id):
    conn = sqlite3.connect('work_system.db')
    c = conn.cursor()
    c.execute('DELETE FROM hosts WHERE id = ?', (int(host_id),))
    conn.commit()
    conn.close()

# --- وظائف الإضافة والجلب ---
def add_host(host_name):
    host_name = host_name.strip()
    if not host_name or host_name == "مباشر (بدون دعوة)":
        return False, "اسم غير صالـح!"
    conn = sqlite3.connect('work_system.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO hosts (host_name) VALUES (?)', (host_name,))
        conn.commit()
        conn.close()
        return True, f"تمت إضافة المستضيف [{host_name}] بنجاح!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, f"المستضيف [{host_name}] موجود بـالفعل!"

def add_member(nickname, phone, referred_by):
    conn = sqlite3.connect('work_system.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO members (nickname, phone, referred_by) VALUES (?, ?, ?)',
                  (nickname, phone, referred_by if referred_by else 'مباشر (بدون دعوة)'))
        conn.commit()
        conn.close()
        return True, f"تمت إضافة العضو [{nickname}] بنجاح!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, f"اللقب [{nickname}] مسجل بـالفعل في القاعدة!"

def get_all_hosts():
    conn = sqlite3.connect('work_system.db')
    df = pd.read_sql_query('SELECT * FROM hosts ORDER BY host_name ASC', conn)
    conn.close()
    return df

def get_all_members():
    conn = sqlite3.connect('work_system.db')
    df = pd.read_sql_query('SELECT * FROM members ORDER BY id DESC', conn)
    conn.close()
    return df

def get_referral_stats():
    conn = sqlite3.connect('work_system.db')
    query = '''
        SELECT referred_by as 'host', COUNT(*) as 'count'
        FROM members
        WHERE referred_by != 'مباشر (بدون دعوة)' AND referred_by != ''
        GROUP BY referred_by
        ORDER BY count DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ---------------------------------------------------------
# 3. القائمة الجانبية وحقوق Aurther
# ---------------------------------------------------------
st.sidebar.title("⚡ WORK SYSTEM")
st.sidebar.markdown('<div class="founder-badge">👑 FOUNDER: Aurther</div>', unsafe_allow_html=True)
st.sidebar.caption("نظام إدارة أعضاء القروب والمستضيفين")
st.sidebar.write("---")

menu = st.sidebar.radio(
    "القائمة الرئيسية:",
    [
        "📊 [1] لوحة التحكم",
        "⚡ [2] تسجيل عضو جديد",
        "👑 [3] قائمة الإحالات",
        "⚙️ [4] إدارة المستضيفين",
        "🔍 [5] استعلام عن عضو",
        "📂 [6] إدارة السجل والحذف"
    ]
)

st.sidebar.write("---")
st.sidebar.caption("© All Rights Reserved to **Aurther**")

df_members = get_all_members()
df_hosts = get_all_hosts()
df_ref = get_referral_stats()

# ---------------------------------------------------------
# 4. أقسام الصفحة
# ---------------------------------------------------------

# --- القسم الأول: لوحة التحكم ---
if menu == "📊 [1] لوحة التحكم":
    st.title("📊 WORK // DASHBOARD")
    st.markdown("##### Developed & Founded by **Aurther**")
    st.caption("نظرة عامة على أحصائيات الأعضاء والمستضيفين")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="إجمالي الأعضاء", value=len(df_members))
    with col2:
        st.metric(label="عدد المستضيفين", value=len(df_hosts))
    
    top_host = df_ref.iloc[0]['host'] if not df_ref.empty else "لا يوجد"
    top_count = int(df_ref.iloc[0]['count']) if not df_ref.empty else 0
    
    with col3:
        st.metric(label="أقوى مستضيف", value=f"{top_host} ({top_count})")

    st.write("---")
    st.subheader("آخر الأعضاء المنضمين حديثاً")
    if not df_members.empty:
        st.dataframe(df_members.head(5)[['id', 'nickname', 'phone', 'referred_by', 'created_at']], use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد بيانات مسجلة بعد.")

# --- القسم الثاني: تسجيل عضو جديد ---
elif menu == "⚡ [2] تسجيل عضو جديد":
    st.title("⚡ تسجيل عضو جديد")
    st.caption("إدخال بيانات العضو إلى القائمة")
    
    with st.form("add_member_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            nickname = st.text_input("اللقب في القروب:", placeholder="مثال: ميكاسا / LARS")
        with col_b:
            phone = st.text_input("رقم الهاتف (مع رمز الدولة):", placeholder="مثال: 9647700000000")
            
        hosts_list = df_hosts['host_name'].tolist() if not df_hosts.empty else []
        
        referred_by_select = st.selectbox(
            "اختر المستضيف (دخل من طرف مَن؟):",
            ["مباشر (بدون دعوة)"] + hosts_list
        )
        
        custom_ref = st.text_input("أو اكتب اسم مستضيف جديد (سيحفظ تلقائياً بالقائمة):")
        
        submit_btn = st.form_submit_button("تسجيل العضو الآن")
        
        if submit_btn:
            if nickname and phone:
                if custom_ref.strip():
                    final_host = custom_ref.strip()
                    add_host(final_host)
                else:
                    final_host = referred_by_select

                success, msg = add_member(nickname.strip(), phone.strip(), final_host)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("يرجى إدخال اللقب ورقم الهاتف!")

# --- القسم الثالث: قائمة الإحالات ---
elif menu == "👑 [3] قائمة الإحالات":
    st.title("👑 قائمة المستضيفين والإحالات")
    st.caption("ترتيب المستضيفين حسب عدد الأعضاء القادمين عن طريقهم")
    
    if not df_ref.empty:
        st.subheader("جدول الترتيب")
        df_ref_ranked = df_ref.copy()
        df_ref_ranked.columns = ['المستضيف (صاحب الدعوة)', 'عدد الأعضاء المضافين']
        st.dataframe(df_ref_ranked, use_container_width=True, hide_index=True)
        
        st.write("---")
        st.subheader("عرض فريق مستضيف معين")
        
        selected_host = st.selectbox("اختر اسم المستضيف:", df_ref['host'].tolist())
        
        if selected_host:
            invited_members = df_members[df_members['referred_by'] == selected_host]
            
            st.markdown(f"""
                <div class="modern-card">
                    <h3>👑 المستضيف: {selected_host}</h3>
                    <p>عدد الأعضاء القادمين عن طريقه: <span class="badge-soft">{len(invited_members)} أعضاء</span></p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write(f"الأعضاء المضافين عن طريق **[{selected_host}]**:")
            st.dataframe(invited_members[['id', 'nickname', 'phone', 'created_at']], use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد إحالات مسجلة بعد.")

# --- القسم الرابع: إدارة المستضيفين ---
elif menu == "⚙️ [4] إدارة المستضيفين":
    st.title("⚙️ إدارة قائمة المستضيفين")
    st.caption("إضافة أو حذف مستضيفين معتمدين")
    
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.subheader("➕ إضافة مستضيف جديد")
        with st.form("add_host_form", clear_on_submit=True):
            new_host_name = st.text_input("اسم المستضيف:")
            btn_add_h = st.form_submit_button("إضافة المستضيف")
            
            if btn_add_h:
                if new_host_name:
                    ok, res_msg = add_host(new_host_name)
                    if ok:
                        st.success(res_msg)
                        st.rerun()
                    else:
                        st.error(res_msg)
                else:
                    st.warning("يرجى كتابة اسم المستضيف!")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_h2:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.subheader("🗑️ حذف مستضيف من القائمة")
        
        if not df_hosts.empty:
            host_to_del = st.selectbox("اختر المستضيف للـحذف:", ["-- اختر --"] + df_hosts['host_name'].tolist())
            
            if host_to_del != "-- اختر --":
                host_row = df_hosts[df_hosts['host_name'] == host_to_del].iloc[0]
                st.warning(f"هل أنت تأكد من حذف المستضيف [{host_row['host_name']}]؟")
                
                if st.button(f"حذف المستضيف [{host_row['host_name']}]"):
                    delete_host_by_id(host_row['id'])
                    st.success(f"تم حذف المستضيف [{host_row['host_name']}] بنجاح!")
                    st.rerun()
        else:
            st.info("لا يوجد مستضيفين مسجلين حالياً.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    st.subheader("قائمة المستضيفين المعتمدين")
    if not df_hosts.empty:
        st.dataframe(df_hosts[['id', 'host_name']], use_container_width=True, hide_index=True)

# --- القسم الخامس: استعلام عن عضو ---
elif menu == "🔍 [5] استعلام عن عضو":
    st.title("🔍 استعلام سليم عن عضو")
    
    if not df_members.empty:
        selected_m = st.selectbox("اختر اللقب للاستعلام:", df_members['nickname'].tolist())
        
        m_info = df_members[df_members['nickname'] == selected_m].iloc[0]
        clean_num = ''.join(filter(str.isdigit, str(m_info['phone'])))
        
        st.markdown(f"""
            <div class="modern-card">
                <h3>👤 العضو: {m_info['nickname']}</h3>
                <p><strong>رقم الهاتف:</strong> {m_info['phone']}</p>
                <p><strong>المستضيف (دخل من طرف):</strong> {m_info['referred_by']}</p>
                <p><strong>تاريخ الانضمام:</strong> {m_info['created_at']}</p>
                <a class="wa-btn" href="https://wa.me/{clean_num}" target="_blank">📲 فتح محادثة الواتساب المباشرة</a>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("القاعدة فارغة حالياً.")

# --- القسم السادس: إدارة السجل وحذف الأعضاء ---
elif menu == "📂 [6] إدارة السجل والحذف":
    st.title("📂 إدارة السجل وحذف الأعضاء")
    st.caption("البحث في القواعد والحذف النهائي للأعضاء")
    
    if not df_members.empty:
        search_kw = st.text_input("🔍 بحث وفلترة بالسجل:")
        
        display_df = df_members.copy()
        if search_kw:
            display_df = display_df[
                display_df['nickname'].str.contains(search_kw, case=False, na=False) |
                display_df['phone'].str.contains(search_kw, case=False, na=False) |
                display_df['referred_by'].str.contains(search_kw, case=False, na=False)
            ]
        
        st.dataframe(display_df[['id', 'nickname', 'phone', 'referred_by', 'created_at']], use_container_width=True, hide_index=True)
        
        st.write("---")
        st.subheader("🗑️ حذف عضو من النظام")
        
        member_list = ["-- اختر العضو --"] + df_members['nickname'].tolist()
        selected_to_delete = st.selectbox("اختر العضو المراد مسحه:", member_list)
        
        if selected_to_delete != "-- اختر العضو --":
            target_data = df_members[df_members['nickname'] == selected_to_delete].iloc[0]
            
            st.error(f"تنبيه: أنت على وشك مسح العضو [{target_data['nickname']}] (ID: #{target_data['id']})")
            
            if st.button(f"تأكيد حذف العضو [{target_data['nickname']}] الآن"):
                delete_member_by_id(target_data['id'])
                st.success(f"تم مسح العضو [{target_data['nickname']}] بنجاح!")
                st.rerun()
    else:
        st.info("لا يوجد أعضاء مسجلين.")
                
