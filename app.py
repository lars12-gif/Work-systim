import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------------------------------------
# 1. إعداد الصفحة (نظيف ومودرن Native)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Work System | Aurther",
    page_icon="⚡",
    layout="wide"
)

# ---------------------------------------------------------
# 2. إدارة قاعدة البيانات (مع إصلاح الحذف الجذري)
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

# --- دوال الحذف (مع تحويل الـ ID لـ int) ---
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

# --- دوال الإضافة والجلب ---
def add_host(host_name):
    host_name = host_name.strip()
    if not host_name or host_name == "مباشر (بدون دعوة)":
        return False, "الاسم غير صالح!"
    
    conn = sqlite3.connect('work_system.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO hosts (host_name) VALUES (?)', (host_name,))
        conn.commit()
        conn.close()
        return True, f"تمت إضافة [{host_name}] بنجاح."
    except sqlite3.IntegrityError:
        conn.close()
        return False, f"المستضيف [{host_name}] موجود مسبقاً."

def add_member(nickname, phone, referred_by):
    conn = sqlite3.connect('work_system.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO members (nickname, phone, referred_by) VALUES (?, ?, ?)',
                  (nickname, phone, referred_by if referred_by else 'مباشر (بدون دعوة)'))
        conn.commit()
        conn.close()
        return True, f"تم تسجيل [{nickname}] بنجاح."
    except sqlite3.IntegrityError:
        conn.close()
        return False, f"اللقب [{nickname}] مسجل مسبقاً."

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
# 3. القائمة الجانبية (بسيطة جداً)
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
        "⚙️ السجل والإعدادات"
    ]
)

df_members = get_all_members()
df_hosts = get_all_hosts()
df_ref = get_referral_stats()

# ---------------------------------------------------------
# 4. أقسام الصفحة (تصميم نظيف)
# ---------------------------------------------------------

if menu == "📊 لوحة التحكم":
    st.header("📊 لوحة التحكم")
    st.caption("نظرة سريعة على إحصائيات النظام.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("الأعضاء", len(df_members))
    col2.metric("المستضيفين", len(df_hosts))
    
    top_h = df_ref.iloc[0]['host'] if not df_ref.empty else "لا يوجد"
    top_c = int(df_ref.iloc[0]['count']) if not df_ref.empty else 0
    col3.metric("أقوى مستضيف", f"{top_h} ({top_c})")

    st.divider()
    st.subheader("آخر المنضمين")
    if not df_members.empty:
        st.dataframe(df_members.head(5)[['nickname', 'phone', 'referred_by', 'created_at']], use_container_width=True, hide_index=True)
    else:
        st.info("النظام فارغ حالياً.")

elif menu == "➕ إضافة عضو":
    st.header("➕ تسجيل عضو جديد")
    
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nickname = col1.text_input("اللقب:")
        phone = col2.text_input("رقم الهاتف:")
        
        hosts_list = df_hosts['host_name'].tolist() if not df_hosts.empty else []
        selected_host = st.selectbox("المستضيف (الداعي):", ["مباشر (بدون دعوة)"] + hosts_list)
        custom_host = st.text_input("أو مستضيف جديد (سيتم حفظه تلقائياً):")
        
        if st.form_submit_button("تسجيل العضو"):
            if nickname and phone:
                final_host = custom_host.strip() if custom_host.strip() else selected_host
                if custom_host.strip():
                    add_host(final_host)
                
                success, msg = add_member(nickname.strip(), phone.strip(), final_host)
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
            st.dataframe(df_ref.rename(columns={'host':'المستضيف', 'count':'عدد الأعضاء'}), use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد إحالات بعد.")
            
    with tab2:
        if not df_ref.empty:
            host_choice = st.selectbox("اختر المستضيف لعرض أعضائه:", df_ref['host'].tolist())
            invited = df_members[df_members['referred_by'] == host_choice]
            st.dataframe(invited[['nickname', 'phone', 'created_at']], use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد بيانات.")

elif menu == "🔍 استعلام":
    st.header("🔍 استعلام سريع")
    
    if not df_members.empty:
        search_target = st.selectbox("اختر العضو:", df_members['nickname'].tolist())
        target_info = df_members[df_members['nickname'] == search_target].iloc[0]
        
        st.info(f"""
        **الاسم:** {target_info['nickname']}  
        **الرقم:** {target_info['phone']}  
        **المستضيف:** {target_info['referred_by']}  
        **تاريخ الانضمام:** {target_info['created_at']}
        """)
        
        clean_num = ''.join(filter(str.isdigit, str(target_info['phone'])))
        st.markdown(f"[📲 تواصل عبر الواتساب](https://wa.me/{clean_num})")
    else:
        st.info("لا يوجد أعضاء.")

elif menu == "⚙️ السجل والإعدادات":
    st.header("⚙️ إدارة النظام")
    
    tab_del_member, tab_del_host = st.tabs(["🗑️ حذف عضو", "🗑️ إدارة قائمة المستضيفين"])
    
    with tab_del_member:
        st.subheader("حذف عضو من السجل")
        if not df_members.empty:
            member_to_del = st.selectbox("اختر العضو للحذف:", ["-- اختر --"] + df_members['nickname'].tolist())
            if member_to_del != "-- اختر --":
                target_m = df_members[df_members['nickname'] == member_to_del].iloc[0]
                if st.button("تأكيد الحذف", type="primary"):
                    delete_member_by_id(target_m['id'])
                    st.success(f"تم حذف {member_to_del} بنجاح.")
                    st.rerun()
        else:
            st.info("السجل فارغ.")
            
    with tab_del_host:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("إضافة مستضيف")
            with st.form("add_h_form", clear_on_submit=True):
                new_h = st.text_input("اسم المستضيف:")
                if st.form_submit_button("إضافة"):
                    if new_h:
                        ok, msg = add_host(new_h)
                        if ok: st.success(msg); st.rerun()
                        else: st.error(msg)
                        
        with col2:
            st.subheader("حذف مستضيف")
            if not df_hosts.empty:
                host_to_del = st.selectbox("اختر للحذف:", ["-- اختر --"] + df_hosts['host_name'].tolist())
                if host_to_del != "-- اختر --":
                    target_h = df_hosts[df_hosts['host_name'] == host_to_del].iloc[0]
                    if st.button("حذف المستضيف", type="primary"):
                        delete_host_by_id(target_h['id'])
                        st.success(f"تم حذف {host_to_del} بنجاح.")
                        st.rerun()
            else:
                st.info("لا يوجد مستضيفين.")
    
