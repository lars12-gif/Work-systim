import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# 1. إعداد الصفحة وتأثيرات الماتريكس بلمسات Aurther
# ---------------------------------------------------------
st.set_page_config(
    page_title="WORK // CYBER SYSTEM BY AURTHER",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# خلفية الأرقام المتحركة (0 , 1) باللون الأحمر النيون
st.markdown("""
    <canvas id="matrixCanvas"></canvas>
    <script>
        const canvas = document.getElementById('matrixCanvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        const chars = '01';
        const fontSize = 16;
        let columns = Math.floor(canvas.width / fontSize);
        let rainDrops = Array(columns).fill(1);

        function drawMatrix() {
            ctx.fillStyle = 'rgba(5, 0, 2, 0.12)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = '#ff0033';
            ctx.font = fontSize + 'px monospace';

            columns = Math.floor(canvas.width / fontSize);
            if (rainDrops.length < columns) {
                while (rainDrops.length < columns) rainDrops.push(1);
            }

            for (let i = 0; i < rainDrops.length; i++) {
                const text = chars.charAt(Math.floor(Math.random() * chars.length));
                ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);

                if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    rainDrops[i] = 0;
                }
                rainDrops[i]++;
            }
        }
        setInterval(drawMatrix, 40);
    </script>

    <style>
    #matrixCanvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        opacity: 0.35;
        pointer-events: none;
    }

    .stApp {
        background: linear-gradient(180deg, #0a0003 0%, #000000 100%);
        color: #ffffff;
        font-family: 'Courier New', monospace;
    }

    section[data-testid="stSidebar"] {
        background-color: #0d0004 !important;
        border-right: 1px solid #ff0033 !important;
    }

    h1, h2, h3, h4, label, .stMarkdown {
        color: #ff3355 !important;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 5px rgba(255, 0, 51, 0.5);
    }

    div[data-testid="stMetricValue"] {
        color: #ff0033 !important;
        font-size: 2rem !important;
        font-weight: bold;
        text-shadow: 0 0 10px #ff0033;
    }
    div[data-testid="stMetric"] {
        background: rgba(20, 0, 6, 0.85);
        border: 1px solid #ff0033;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(255, 0, 51, 0.3);
    }

    input, select, textarea {
        background-color: #120005 !important;
        color: #ffffff !important;
        border: 1px solid #ff0033 !important;
        border-radius: 6px !important;
    }

    .stButton>button {
        background-color: rgba(20, 0, 6, 0.8);
        color: #ff3355;
        border: 1px solid #ff0033;
        border-radius: 6px;
        font-weight: bold;
        transition: all 0.3s ease;
        text-shadow: 0 0 5px #ff0033;
    }
    .stButton>button:hover {
        background-color: #ff0033;
        color: #ffffff;
        box-shadow: 0 0 20px #ff0033;
    }

    .red-card {
        background: rgba(20, 0, 6, 0.9);
        border: 1px solid #ff0033;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(255, 0, 51, 0.25);
        margin-bottom: 15px;
    }
    
    .founder-badge {
        background: linear-gradient(90deg, #ff0033 0%, #700016 100%);
        color: #ffffff;
        padding: 8px 15px;
        border-radius: 6px;
        font-weight: bold;
        letter-spacing: 1px;
        border: 1px solid #ff3355;
        box-shadow: 0 0 10px rgba(255, 0, 51, 0.5);
        display: inline-block;
        margin-top: 10px;
    }

    .badge-red {
        background-color: #ff0033;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: bold;
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
        margin-top: 10px;
        box-shadow: 0 0 10px rgba(37, 211, 102, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. إدارة قاعدة البيانات (SQLite) مع إصلاح تحويل ID
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

# --- دالة الحذف المضمونة مع تحويل ID الصريح ---
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
st.sidebar.title("🔴 WORK // TERMINAL")
st.sidebar.markdown('<div class="founder-badge">👑 FOUNDER: Aurther</div>', unsafe_allow_html=True)
st.sidebar.caption("نظام إدارة الأعضاء والمستضيفين")
st.sidebar.write("---")

menu = st.sidebar.radio(
    "انتقل إلى القسم:",
    [
        "📊 [1] لوحة التحكم الرئيسية",
        "⚡ [2] تسجيل عضو جديد",
        "👑 [3] قائمة وتأثير المستضيفين",
        "⚙️ [4] إدارة قائمة المستضيفين (إضافة/حذف)",
        "🔍 [5] استعلام عن عضو",
        "📂 [6] إدارة السجل وحذف الأعضاء"
    ]
)

st.sidebar.write("---")
st.sidebar.caption("© ALL RIGHTS RESERVED TO AURTHER")

df_members = get_all_members()
df_hosts = get_all_hosts()
df_ref = get_referral_stats()

# ---------------------------------------------------------
# 4. أقسام الصفحة
# ---------------------------------------------------------

# --- القسم الأول: لوحة التحكم ---
if menu == "📊 [1] لوحة التحكم الرئيسية":
    st.title("⚡ WORK // SYSTEM DASHBOARD")
    st.markdown("##### 🚀 Developed & Founded by **Aurther**")
    st.caption("> نظرة عامة على أحصائيات القروب والمستضيفين")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="إجمالي الأعضاء", value=len(df_members))
    with col2:
        st.metric(label="عدد المستضيفين المعتمدين", value=len(df_hosts))
    
    top_host = df_ref.iloc[0]['host'] if not df_ref.empty else "لا يوجد"
    top_count = int(df_ref.iloc[0]['count']) if not df_ref.empty else 0
    
    with col3:
        st.metric(label="أقوى مستضيف (Top Host)", value=f"{top_host} ({top_count})")

    st.write("---")
    st.subheader("> آخر الأعضاء المنضمين حديثاً")
    if not df_members.empty:
        st.dataframe(df_members.head(5)[['id', 'nickname', 'phone', 'referred_by', 'created_at']], use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد بيانات حتى الآن.")

# --- القسم الثاني: تسجيل عضو جديد ---
elif menu == "⚡ [2] تسجيل عضو جديد":
    st.title("⚡ REGISTER NEW MEMBER")
    st.caption("> إضافة عضو جديد لقاعدة بيانات WORK")
    
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
        
        custom_ref = st.text_input("أو اكتب اسم مستضيف جديد يدوياً (سيتم حفظه تلقائياً لقائمة المستضيفين):")
        
        submit_btn = st.form_submit_button("EXECUTE_REGISTER // تسجيل العضو")
        
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
                st.warning("يرجى كتابة اللقب ورقم الهاتف كاملاً!")

# --- القسم الثالث: قائمة وتأثير المستضيفين ---
elif menu == "👑 [3] قائمة وتأثير المستضيفين":
    st.title("👑 HOST TEAMS & LEADERBOARD")
    st.caption("> استعراض نتائج ودعوات المستضيفين والأعضاء القادمين عن طريقهم")
    
    if not df_ref.empty:
        st.subheader("> قائمة الترتيب حسب الدعوات")
        df_ref_ranked = df_ref.copy()
        df_ref_ranked.columns = ['المستضيف (صاحب الدعوة)', 'عدد الأشخاص المضافين']
        st.dataframe(df_ref_ranked, use_container_width=True, hide_index=True)
        
        st.write("---")
        st.subheader("> استعراض أعضاء مستضيف معين")
        
        selected_host = st.selectbox("اختر اسم المستضيف:", df_ref['host'].tolist())
        
        if selected_host:
            invited_members = df_members[df_members['referred_by'] == selected_host]
            
            st.markdown(f"""
                <div class="red-card">
                    <h2>👑 المستضيف: {selected_host}</h2>
                    <p>عدد الأعضاء القادمين عن طريقه: <span class="badge-red">{len(invited_members)} أعضاء</span></p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**الأعضاء الذين انضموا عن طريق [{selected_host}]:**")
            st.dataframe(invited_members[['id', 'nickname', 'phone', 'created_at']], use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد إحالات أو مستضيفين جلبوا أعضاء حتى الآن.")

# --- القسم الرابع: إدارة قائمة المستضيفين ---
elif menu == "⚙️ [4] إدارة قائمة المستضيفين (إضافة/حذف)":
    st.title("⚙️ MANAGE HOSTS LIST")
    st.caption("> التحكم الكامل بقائمة المستضيفين المعتمدين")
    
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        st.markdown('<div class="red-card">', unsafe_allow_html=True)
        st.subheader("➕ إضافة مستضيف جديد")
        with st.form("add_host_form", clear_on_submit=True):
            new_host_name = st.text_input("اسم المستضيف الجديد:")
            btn_add_h = st.form_submit_button("إضافة المستضيف للقائمة")
            
            if btn_add_h:
                if new_host_name:
                    ok, res_msg = add_host(new_host_name)
                    if ok:
                        st.success(res_msg)
                        st.rerun()
                    else:
                        st.error(res_msg)
                else:
                    st.warning("اكتب اسم المستضيف أولاً!")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_h2:
        st.markdown('<div class="red-card">', unsafe_allow_html=True)
        st.subheader("🗑️ حذف مستضيف من القائمة")
        
        if not df_hosts.empty:
            host_to_del = st.selectbox("اختر المستضيف المراد حذفه:", ["-- اختر --"] + df_hosts['host_name'].tolist())
            
            if host_to_del != "-- اختر --":
                host_row = df_hosts[df_hosts['host_name'] == host_to_del].iloc[0]
                st.warning(f"هل أنت تأكد من حذف المستضيف [{host_row['host_name']}]؟")
                
                if st.button(f"🔴 تأكيد حذف المستضيف [{host_row['host_name']}]"):
                    delete_host_by_id(host_row['id'])
                    st.success(f"تم حذف المستضيف [{host_row['host_name']}] بنجاح!")
                    st.rerun()
        else:
            st.info("لا يوجد مستضيفين مسجلين حالياً.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    st.subheader("> قائمة جميع المستضيفين المعتمدين")
    if not df_hosts.empty:
        st.dataframe(df_hosts[['id', 'host_name']], use_container_width=True, hide_index=True)

# --- القسم الخامس: استعلام عن عضو ---
elif menu == "🔍 [5] استعلام عن عضو":
    st.title("🔍 SEARCH MEMBER")
    
    if not df_members.empty:
        selected_m = st.selectbox("اختر اللقب للاستعلام:", df_members['nickname'].tolist())
        
        m_info = df_members[df_members['nickname'] == selected_m].iloc[0]
        clean_num = ''.join(filter(str.isdigit, str(m_info['phone'])))
        
        st.markdown(f"""
            <div class="red-card">
                <h3>🆔 MEMBER_PROFILE: {m_info['nickname']}</h3>
                <p><strong>الرقم:</strong> {m_info['phone']}</p>
                <p><strong>المستضيف (دخل من طرف):</strong> {m_info['referred_by']}</p>
                <p><strong>تاريخ الانضمام:</strong> {m_info['created_at']}</p>
                <a class="wa-btn" href="https://wa.me/{clean_num}" target="_blank">📲 تواصل مباشر عبر الواتساب</a>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("القاعدة فارغة حالياً.")

# --- القسم السادس: إدارة السجل وحذف الأعضاء ---
elif menu == "📂 [6] إدارة السجل وحذف الأعضاء":
    st.title("📂 DATABASE MANAGEMENT")
    st.caption("> فلترة السجل والتأكيد الصارم لحذف الأعضاء")
    
    if not df_members.empty:
        search_kw = st.text_input("🔍 فلترة السجل بالاسم، الرقم، أو الداعي:")
        
        display_df = df_members.copy()
        if search_kw:
            display_df = display_df[
                display_df['nickname'].str.contains(search_kw, case=False, na=False) |
                display_df['phone'].str.contains(search_kw, case=False, na=False) |
                display_df['referred_by'].str.contains(search_kw, case=False, na=False)
            ]
        
        st.dataframe(display_df[['id', 'nickname', 'phone', 'referred_by', 'created_at']], use_container_width=True, hide_index=True)
        
        st.write("---")
        st.subheader("🗑️ قسم حذف الأعضاء (حذف مباشر)")
        
        member_list = ["-- اختر العضو --"] + df_members['nickname'].tolist()
        selected_to_delete = st.selectbox("اختر العضو المراد مسحه تماماً من البيانات:", member_list)
        
        if selected_to_delete != "-- اختر العضو --":
            target_data = df_members[df_members['nickname'] == selected_to_delete].iloc[0]
            
            st.error(f"⚠️ تحذير: أنت على وشك حذف العضو [{target_data['nickname']}] (ID: #{target_data['id']})")
            
            if st.button(f"🔴 تأكيد حذف العضو [{target_data['nickname']}] الآن"):
                delete_member_by_id(target_data['id'])
                st.success(f"تم حذف العضو [{target_data['nickname']}] بنجاح من قاعدة البيانات!")
                st.rerun()
    else:
        st.info("لا يوجد أعضاء في قاعدة البيانات.")
