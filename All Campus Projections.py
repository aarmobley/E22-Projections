import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pyodbc

st.set_page_config(page_title="CoE22 Projections", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_connection_string():
    return (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=" + st.secrets['db']['server'] + ";"
        "DATABASE=" + st.secrets['db']['database'] + ";"
        "UID=" + st.secrets['db']['username'] + ";"
        "PWD=" + st.secrets['db']['password'] + ";"
    )

def get_connection():
    return pyodbc.connect(get_connection_string())

st.markdown('<style>[data-testid="stSidebar"]{display:none;}[data-testid="stSidebarCollapsedControl"]{display:none;}</style>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;margin-bottom:20px;"><a href="https://e22projections.streamlit.app/" target="_blank" rel="noopener noreferrer" style="display:inline-block;background-color:#1f77b4;color:white;padding:8px 16px;border-radius:6px;text-decoration:none;font-size:14px;font-weight:500;box-shadow:0 2px 4px rgba(0,0,0,0.1);">Open in New Window for Downloads</a></div>', unsafe_allow_html=True)

query_params = st.query_params
if query_params.get('embedded','false') == 'true':
    st.markdown('<style>.stApp > header{display:none;}.stApp > div:first-child{display:none;}.main .block-container{padding-top:0.5rem;}</style>', unsafe_allow_html=True)

st.image("https://raw.githubusercontent.com/aarmobley/CoE22/main/E22%20Logo.png", width=90)

campus_coefficients = {
    'San Pablo': {
        '7:22':  {'intercept':-142.667110,'sunday_date':0.009315,'week_number':-0.056675,'Easter':8.531395,'Promotion Week':1.680988,'Back to School':1.680988,'Saturated Sunday':13.262508,'kids_projection':.08,'kids_easter':.08,'Christmas':5.896587},
        '9:00':  {'intercept':-171.987662,'sunday_date':0.011074,'week_number':-0.008375,'Guest Pastor':-1.329637,'Executive Pastor':-0.615583,'Pastor Joby':1.029747,'Easter':14.137845,'Promotion Week':1.400238,'Back to School':1.400238,'Saturated Sunday':7.225865,'kids_projection':0.20,'kids_easter':.12,'Christmas':4.600030},
        '11:22': {'intercept':-151.7846,'sunday_date':0.01,'week_number':-0.0726,'Guest Pastor':-1.6713,'Executive Pastor':-1.4246,'Pastor Joby':0.2733,'Easter':14.6459,'Promotion Week':3.4931,'Back to School':3.4931,'Saturated Sunday':6.2969,'kids_projection':.15,'kids_easter':.12,'kids_labor':17.64,'Christmas':9.5353,'Inclement Weather':.15},
        '4:22':  {'Total Attendance':.06}
    },
    'Arlington': {
        '9:00':  {'intercept':-38.65,'sunday_date':.002963,'week_number':.003602,'Guest Pastor':-.4529,'Executive Pastor':-.8438,'Pastor Joby':-.1221,'Easter':6.193,'BacktoSchool':.08546,'Saturated Sunday':.9908,'kids_projection':0.29,'kids_easter':.25},
        '11:22': {'intercept':-4.1528006,'sunday_date':0.0011252,'week_number':-.0178361,'Guest Pastor':-.7539401,'Executive Pastor':-.3526798,'Pastor Joby':.1628141,'Easter':5.4945168,'BacktoSchool':-.9172174,'Saturated Sunday':1.6824265,'kids_projection':.30,'kids_easter':.25},
        '7:22':  {'Total Attendance':.16}
    },
    'Baymeadows': {
        '9:00':  {'intercept':-67.30,'sunday_date':.004270,'week_number':-.001089,'Guest Pastor':-.3866,'Executive Pastor':-.2336,'Pastor Joby':.4164,'Easter':4.030,'Promotion Week':1.048,'Saturated Sunday':1.437,'kids_projection':0.24,'kids_easter':.19,'Christmas':-1.303112},
        '11:22': {'intercept':-43.74,'sunday_date':.003019,'week_number':-.005647,'Guest Pastor':-.6090,'Executive Pastor':-.2468,'Pastor Joby':.2159,'Easter':2.782,'Promotion Week':.4619,'Saturated Sunday':2.013,'kids_projection':0.21,'kids_easter':.19,'Christmas':-1.018843},
        '7:22':  {'Total Attendance':.16}
    },
    'Fleming Island': {
        '7:22':  {'intercept':-56.532818,'sunday_date':0.003535,'week_number':-0.017519,'Guest Pastor':-0.132035,'Executive Pastor':-0.818452,'Pastor Joby':-0.266790,'Easter':5.701672,'Promotion Week':1.144970,'Back To School':1.144970,'Saturated Sunday':8.582320,'kids_projection':.15,'kids_easter':.13,'Christmas':6.746094},
        '9:00':  {'intercept':-59.344,'sunday_date':0.0041,'week_number':-0.0079,'Guest Pastor':-0.0018,'Executive Pastor':-0.4856,'Pastor Joby':0.4656,'Easter':7.6926,'Promotion Week':1.2294,'Back To School':1.2294,'Saturated Sunday':2.1657,'kids_projection':0.27,'kids_easter':.20,'Christmas':2.5449},
        '11:22': {'intercept':-52.0234,'sunday_date':0.0038,'week_number':-0.0316,'Guest Pastor':-0.5974,'Executive Pastor':-0.5027,'Pastor Joby':-0.0229,'Easter':6.1344,'Promotion Week':1.8042,'Back To School':1.8042,'Saturated Sunday':3.6719,'kids_projection':0.27,'kids_easter':.21,'Christmas':4.6251},
    },
    'Jesup': {
        '9:00':  {'intercept':-73.607412,'sunday_date':0.004340,'week_number':0.014782,'Easter':3.489182,'Promotion Week':1.612629,'Back to School':1.612629,'Saturated Sunday':1.115047,'kids_projection':0.29,'kids_easter':.25,'Christmas':3.982514},
        '11:22': {'intercept':-23.31375,'sunday_date':0.00167,'week_number':-0.02805,'Easter':2.24195,'Promotion Week':1.30396,'Back to School':1.30396,'Saturated Sunday':2.74741,'kids_projection':.33,'kids_easter':.33,'Christmas':1.44838},
    },
    'Mandarin': {
        '9:00':  {'intercept':-50.25,'sunday_date':.003850,'week_number':-.000900,'Guest Pastor':-.3200,'Executive Pastor':-.2100,'Pastor Joby':.3800,'Easter':3.500,'Promotion Week':.900,'Saturated Sunday':1.200,'kids_projection':0.22,'kids_easter':.18,'Christmas':-1.100},
        '11:22': {'intercept':-35.60,'sunday_date':.002800,'week_number':-.004500,'Guest Pastor':-.5500,'Executive Pastor':-.2200,'Pastor Joby':.1900,'Easter':2.400,'Promotion Week':.4000,'Saturated Sunday':1.800,'kids_projection':0.20,'kids_easter':.17,'Christmas':-.900}
    },
    'North Jax': {
        '9:00':  {'intercept':-1717.7378,'sunday_date':0.1062,'week_number':-0.6172,'Saturated Sunday':156.4363,'Easter':125.3663,'Promotion Week':22.1525,'kids_projection':.32,'kids_easter':.27,'Christmas':71.7278},
        '11:22': {'intercept':-85.5483,'sunday_date':0.0206,'week_number':-0.2566,'Saturated Sunday':248.2769,'Easter':179.4513,'Promotion Week':92.1327,'Back to School':51.4164,'kids_projection':.23,'kids_easter':.29,'Christmas':20.1802},
        '7:22':  {'Total Attendance':.23}
    },
    'Orange Park': {
        '9:00':  {'intercept':-45.317708,'sunday_date':0.003027,'week_number':0.000409,'Guest Pastor':0.105776,'Executive Pastor':-0.054834,'Pastor Joby':0.545095,'Easter':5.713542,'BacktoSchool':1.382218,'Saturated Sunday':1.507777,'Christmas':1.679073,'Kids Projection':.27,'Kids Easter':.19},
        '11:22': {'intercept':-44.235901,'sunday_date':0.003001,'week_number':-0.026953,'Guest Pastor':-0.758658,'Executive Pastor':-0.305494,'Pastor Joby':-0.325970,'Easter':6.184421,'BacktoSchool':1.411250,'Saturated Sunday':1.431013,'Christmas':3.997914,'Kids Projection':.33,'Kids Easter':.23},
    },
    'Ponte Vedra': {
        '9:00':  {'intercept':-6.321507,'sunday_date':0.001285,'week_number':-0.012768,'Easter':5.188487,'Promotion Week':1.4468,'Back to School':1.443064,'Saturated Sunday':1.851372,'kids_projection':0.22,'kids_easter':.12,'Christmas':2.685164,'Inclement Weather':.15},
        '11:22': {'intercept':36.036786,'sunday_date':-0.001003,'week_number':-0.013473,'Easter':6.922727,'Promotion Week':1.979547,'Back to School':1.952,'Saturated Sunday':3.556182,'kids_projection':.15,'kids_easter':.12,'kids_labor':17.64,'Christmas':4.411963,'Inclement Weather':.15}
    },
    'St. Johns': {
        '9:00':  {'intercept':-7376.0256,'sunday_date':0.4081,'week_number':-0.7781,'Guest Pastor':-25.0405,'Executive Pastor':-10.8755,'Pastor Joby':-12.5410,'Easter':368.6713,'BacktoSchool':99.6941,'Saturated Sunday':144.4888,'Christmas':267.1487,'Kids Projection':.35,'Kids Easter':.24,'New Building':674.2372},
        '11:22': {'intercept':-5681.6164,'sunday_date':0.3158,'week_number':-1.4148,'Guest Pastor':-13.0240,'Executive Pastor':0.1442,'Pastor Joby':2.1450,'Easter':373.0117,'BacktoSchool':129.6823,'Saturated Sunday':156.1531,'Christmas':285.94632,'Kids Projection':.25,'Kids Easter':.15,'New Building':492.5563},
        '7:22':  {'Total Attendance':.20}
    }
}

campus_capacities = {
    'San Pablo':{'adult':3001,'kids':750},'Arlington':{'adult':850,'kids':225},
    'Baymeadows':{'adult':525,'kids':247},'Fleming Island':{'adult':766,'kids':250},
    'Jesup':{'adult':290,'kids':105},'Mandarin':{'adult':840,'kids':330},
    'North Jax':{'adult':700,'kids':350},'Orange Park':{'adult':700,'kids':262},
    'Ponte Vedra':{'adult':545,'kids':210},'St. Johns':{'adult':1948,'kids':559}
}

num_week = [w for _ in range(3) for w in range(1,53)]
if len(num_week) < 156: num_week.append(53)
start_date        = datetime(2025,1,5)
date_range        = [start_date + timedelta(weeks=i) for i in range(156)]
epoch             = datetime(1970,1,1)
date_mapping      = {d.strftime('%m-%d-%Y'):(d-epoch).days for d in date_range}
date_week_options = [d.strftime('%m-%d-%Y')+" (Week "+str(w)+")" for d,w in zip(date_range,num_week)]

def calculate_attendance(campus, service_time, coeff, num_date, week_num, pastor, event):
    we = coeff.get('week_number',0)*week_num
    sd = coeff.get('sunday_date',0)*num_date
    pe, ee = 0, 0
    if event != 'None':
        for k in [event, event.replace(' ',''), event.replace(' ','to'), event.replace(' ','_')]:
            if k in coeff: ee = coeff[k]; break
    else:
        pe = coeff.get(pastor,0)
    nb = coeff.get('New Building',0) if campus=='St. Johns' else 0
    pred = coeff.get('intercept',0) + sd + we + pe + ee + nb
    att  = pred if campus in ['St. Johns','North Jax'] else pred**2
    if event == 'Inclement Weather':
        r = coeff.get('Inclement Weather',0.15)
        att = att*(1-r) if r < 1 else att+r
    kk = 'kids_easter' if event=='Easter' else 'kids_projection'
    km = 0.2
    for k in [kk, kk.replace('_',' ').title(), 'Kids Projection','Kids Easter']:
        if k in coeff: km = coeff[k]; break
    return max(0,att), max(0,att*km)

def calculate_total_based_attendance(campus, svc, coeff, oa, ok):
    m = coeff.get('Total Attendance',0)
    return max(0,oa*m), max(0,ok*m)

def style_table(df, hover_color="#fdecea"):
    HIDE = {'Day','KidsRatio','AdultCapacity','Adult_Capacity_Percent','Kids_Capacity_Percent','Adult_Capacity_Limit','Kids_Capacity_Limit'}
    cols = list(df.columns)
    hdr  = "".join("<th"+((' class="mob-hide"') if c in HIDE else "")+">"+c+"</th>" for c in cols)
    rows = ""
    for i,(_,row) in enumerate(df.iterrows()):
        rc = "row-even" if i%2==0 else "row-odd"
        cells = ""
        for c in cols:
            v = row[c]
            a = "right" if isinstance(v,(int,float)) else "left"
            if isinstance(v,float) and v==int(v): v="{:,}".format(int(v))
            elif isinstance(v,(int,float)): v="{:,}".format(v)
            hc = "mob-hide" if c in HIDE else ""
            cells += '<td data-label="'+c+'" class="'+hc+'" style="text-align:'+a+'">'+str(v)+'</td>'
        rows += '<tr class="'+rc+'">'+cells+'</tr>'
    return (
        "<style>.modern-table-wrap{overflow-x:auto;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin:1rem 0;}"
        ".modern-table{width:100%;border-collapse:collapse;font-family:'Segoe UI',sans-serif;font-size:0.875rem;}"
        ".modern-table thead tr{background:#C0392B;color:white;text-align:left;letter-spacing:0.04em;font-size:0.8rem;text-transform:uppercase;}"
        ".modern-table thead th{padding:12px 16px;font-weight:600;white-space:nowrap;}"
        ".modern-table tbody tr.row-even{background-color:#ffffff;}.modern-table tbody tr.row-odd{background-color:#f4f7fb;}"
        ".modern-table tbody tr:hover{background-color:"+hover_color+";transition:background 0.15s ease;}"
        ".modern-table td{padding:10px 16px;border-bottom:1px solid #e8edf3;white-space:nowrap;color:#2c3e50;}"
        "@media(max-width:640px){.mob-hide{display:none !important;}.modern-table thead{display:none;}"
        ".modern-table tbody tr{display:block;margin-bottom:12px;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,0.07);overflow:hidden;}"
        ".modern-table tbody tr.row-even{background:#ffffff;}.modern-table tbody tr.row-odd{background:#f4f7fb;}"
        ".modern-table td{display:flex;justify-content:space-between;align-items:center;padding:9px 14px;border-bottom:1px solid #e8edf3;white-space:normal;font-size:0.82rem;}"
        ".modern-table td::before{content:attr(data-label);font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#aaa;flex-shrink:0;margin-right:12px;}}"
        "</style>"
        '<div class="modern-table-wrap"><table class="modern-table"><thead><tr>'+hdr+'</tr></thead><tbody>'+rows+'</tbody></table></div>'
    )

# ── Load Easter Excel ────────────────────────────────────────────────────
easter_url = "https://github.com/aarmobley/E22-Projections/raw/main/Updated%202026%20Easter%20Projections2.xlsx"
try:
    df_easter = pd.read_excel(easter_url, engine="openpyxl")
    if 'Service' in df_easter.columns:
        cleaned = []
        for val in df_easter['Service']:
            try:
                if hasattr(val,'strftime'): cleaned.append(val.strftime('%I:%M %p').lstrip('0'))
                else:
                    s = str(val).strip().replace(':00 ',' ').replace(':00','')
                    cleaned.append(s)
            except Exception: cleaned.append(str(val))
        df_easter['Service'] = cleaned
    easter_load_error = None
except Exception as e:
    df_easter = pd.DataFrame()
    easter_load_error = str(e)

tab1, tab2 = st.tabs(["📊 Projections", "📡 Live Attendance"])

# =====================================================================
with tab1:
# =====================================================================
    st.subheader("Easter 2026 Projections")

    data_2025_rows = [
        ('Arlington','Sun','Adults',682),('Arlington','Sun','Kids',148),('Arlington','Sun','Adults',556),('Arlington','Sun','Kids',90),('Arlington','Thu','Adults',217),('Arlington','Thu','Kids',41),
        ('Baymeadows','Sun','Adults',410),('Baymeadows','Sun','Kids',95),('Baymeadows','Sun','Adults',294),('Baymeadows','Sun','Kids',42),('Baymeadows','Thu','Adults',267),('Baymeadows','Thu','Kids',20),
        ('Fleming Island','Sat','Adults',479),('Fleming Island','Sat','Kids',110),('Fleming Island','Sat','Adults',609),('Fleming Island','Sat','Kids',157),
        ('Fleming Island','Sun','Adults',802),('Fleming Island','Sun','Kids',166),('Fleming Island','Sun','Adults',694),('Fleming Island','Sun','Kids',135),('Fleming Island','Thu','Adults',626),('Fleming Island','Thu','Kids',84),
        ('Jesup','Sun','Adults',270),('Jesup','Sun','Kids',52),('Jesup','Sun','Adults',139),('Jesup','Sun','Kids',43),('Jesup','Thu','Adults',101),('Jesup','Thu','Kids',21),
        ('Mandarin','Sun','Adults',869),('Mandarin','Sun','Kids',224),('Mandarin','Sun','Adults',525),('Mandarin','Sun','Kids',80),('Mandarin','Thu','Adults',322),('Mandarin','Thu','Kids',50),
        ('North Jax','Sat','Adults',394),('North Jax','Sat','Kids',71),('North Jax','Sun','Adults',566),('North Jax','Sun','Kids',149),('North Jax','Sun','Adults',589),('North Jax','Sun','Kids',122),('North Jax','Thu','Adults',252),('North Jax','Thu','Kids',48),
        ('Orange Park','Sun','Adults',436),('Orange Park','Sun','Kids',100),('Orange Park','Sun','Adults',354),('Orange Park','Sun','Kids',114),('Orange Park','Thu','Adults',149),('Orange Park','Thu','Kids',60),
        ('Palatka','Sun','Adults',190),('Palatka','Sun','Kids',60),
        ('Ponte Vedra','Sat','Adults',276),('Ponte Vedra','Sat','Kids',86),('Ponte Vedra','Sun','Adults',601),('Ponte Vedra','Sun','Kids',148),('Ponte Vedra','Sun','Adults',541),('Ponte Vedra','Sun','Kids',108),
        ('San Pablo','Sat','Adults',2452),('San Pablo','Sat','Kids',384),('San Pablo','Sat','Adults',2459),('San Pablo','Sat','Kids',271),
        ('San Pablo','Sun','Adults',913),('San Pablo','Sun','Kids',78),('San Pablo','Sun','Adults',3378),('San Pablo','Sun','Kids',359),('San Pablo','Sun','Adults',3121),('San Pablo','Sun','Kids',340),('San Pablo','Thu','Adults',3381),('San Pablo','Thu','Kids',259),
        ('St. Augustine','Sun','Adults',350),('St. Augustine','Sun','Kids',0),('St. Augustine','Sun','Adults',180),('St. Augustine','Sun','Kids',0),
        ('St. Johns','Sat','Adults',959),('St. Johns','Sat','Kids',246),('St. Johns','Sat','Adults',701),('St. Johns','Sat','Kids',152),('St. Johns','Sun','Adults',1320),('St. Johns','Sun','Kids',266),('St. Johns','Sun','Adults',1373),('St. Johns','Sun','Kids',272),
        ('Wildlight','Sun','Adults',407),('Wildlight','Sun','Kids',82),('Wildlight','Sun','Adults',364),('Wildlight','Sun','Kids',62),
    ]
    df_2025 = pd.DataFrame(data_2025_rows, columns=['Campus','Day','Category','Count'])

    try:
        if easter_load_error:
            raise Exception(easter_load_error)

        dd1,dd2,dd3 = st.columns(3)
        with dd1:
            days = sorted(df_easter['Day'].dropna().unique().tolist(), key=lambda x:{'Thu':0,'Sat':1,'Sun':2}.get(str(x),3)) if 'Day' in df_easter.columns else []
            day_pick = st.selectbox("Filter by Day", ["All"]+days)
        with dd2:
            campuses = sorted(df_easter['Campus'].dropna().unique().tolist()) if 'Campus' in df_easter.columns else []
            campus_pick = st.selectbox("Filter by Campus", ["All"]+campuses)
        with dd3:
            category_pick = st.selectbox("Filter by Category", ["Total","Adults","Kids"])

        df_show = df_easter.copy()
        if day_pick    != "All": df_show = df_show[df_show['Day']    == day_pick]
        if campus_pick != "All": df_show = df_show[df_show['Campus'] == campus_pick]

        base_cols = [c for c in df_show.columns if c not in ['Adults','Kids','Total','KidsRatio']]
        if category_pick == "Adults":
            show_cols = base_cols + [c for c in ['Adults','AdultCapacity'] if c in df_show.columns]; att_col = 'Adults'
        elif category_pick == "Kids":
            show_cols = base_cols + [c for c in ['Kids'] if c in df_show.columns]; att_col = 'Kids'
        else:
            show_cols = base_cols + [c for c in ['Adults','Kids','Total'] if c in df_show.columns]; att_col = 'Total'
        if category_pick != "Adults": show_cols = [c for c in show_cols if c != 'AdultCapacity']
        df_show = df_show[[c for c in show_cols if c in df_show.columns]]

        if att_col in df_show.columns: the_sum = int(df_show[att_col].sum())
        elif category_pick == "Total": the_sum = (int(df_show['Adults'].sum()) if 'Adults' in df_show.columns else 0)+(int(df_show['Kids'].sum()) if 'Kids' in df_show.columns else 0)
        else: the_sum = 0
        svc_count = len(df_show)

        df_2025f = df_2025.copy()
        if campus_pick != "All": df_2025f = df_2025f[df_2025f['Campus']==campus_pick]
        if day_pick    != "All": df_2025f = df_2025f[df_2025f['Day']==day_pick]
        if category_pick=="Adults":   sum_2025 = int(df_2025f[df_2025f['Category']=='Adults']['Count'].sum())
        elif category_pick=="Kids":   sum_2025 = int(df_2025f[df_2025f['Category']=='Kids']['Count'].sum())
        else:                         sum_2025 = int(df_2025f['Count'].sum())

        label_parts = [category_pick]
        if day_pick    != "All": label_parts.append(day_pick)
        if campus_pick != "All": label_parts.append(campus_pick)
        label_base = " - ".join(label_parts)
        yoy_delta  = the_sum - sum_2025
        dc = "#27ae60" if yoy_delta>=0 else "#c0392b"
        di = "▲" if yoy_delta>=0 else "▼"

        st.markdown(
            "<style>.stat-bar{display:flex;flex-wrap:wrap;background:#fff;border-radius:12px;border:1px solid #e0e4ea;box-shadow:0 1px 4px rgba(0,0,0,0.06);margin:1rem 0 1.5rem 0;overflow:hidden;}"
            ".stat-item{flex:1;min-width:140px;text-align:center;padding:18px 16px;box-sizing:border-box;}.stat-item+.stat-item{border-left:1px solid #e8edf3;}"
            "@media(max-width:600px){.stat-item{min-width:50%;flex-basis:50%;}.stat-item:nth-child(3){border-left:none;border-top:1px solid #e8edf3;}.stat-item:nth-child(4){border-top:1px solid #e8edf3;}}"
            ".stat-label{font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#aaa;margin-bottom:6px;}"
            ".stat-num{font-size:1.6rem;font-weight:800;line-height:1.1;}.stat-sub{font-size:0.72rem;color:#bbb;margin-top:3px;}</style>"
            '<div class="stat-bar">'
            '<div class="stat-item"><div class="stat-label">2026 Projection</div><div class="stat-num" style="color:#2c3e50;">'+"{:,}".format(the_sum)+'</div><div class="stat-sub">'+label_base+'</div></div>'
            '<div class="stat-item"><div class="stat-label">2025 Actual</div><div class="stat-num" style="color:#2c3e50;">'+"{:,}".format(sum_2025)+'</div><div class="stat-sub">'+label_base+'</div></div>'
            '<div class="stat-item"><div class="stat-label">YoY Difference</div><div class="stat-num" style="color:'+dc+';">'+di+' '+"{:,}".format(abs(yoy_delta))+'</div><div class="stat-sub">vs Last Year</div></div>'
            '<div class="stat-item"><div class="stat-label">Services Shown</div><div class="stat-num" style="color:#2c3e50;">'+str(svc_count)+'</div><div class="stat-sub">In current filter</div></div>'
            '</div>', unsafe_allow_html=True)

        if 'easter_expanded' not in st.session_state: st.session_state.easter_expanded = False
        df_preview = df_show if st.session_state.easter_expanded else df_show.head(8)
        st.markdown(style_table(df_preview), unsafe_allow_html=True)
        if len(df_show) > 8:
            remaining = len(df_show)-8
            btn_lbl = "▲ Show less" if st.session_state.easter_expanded else "▼ Show all "+str(remaining)+" more rows"
            st.markdown('<style>.expand-btn button{background:none!important;border:none!important;color:#C0392B!important;font-weight:600!important;font-size:0.82rem!important;padding:4px 0!important;cursor:pointer!important;box-shadow:none!important;}</style>', unsafe_allow_html=True)
            st.markdown('<div class="expand-btn">', unsafe_allow_html=True)
            if st.button(btn_lbl, key="easter_toggle"):
                st.session_state.easter_expanded = not st.session_state.easter_expanded
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.write("")
        st.download_button("Download Easter Projections (CSV)", df_show.to_csv(index=False), "Easter_2026_Projections.csv", "text/csv")

    except Exception as e:
        st.error("Could not load Easter projections file: " + str(e))

    st.divider()

    date_options      = st.selectbox("Select Sunday Date", date_week_options)
    selected_date_str = date_options.split(' ')[0]
    select_week       = int(date_options.split('Week ')[-1].strip(')'))
    select_pastor     = st.selectbox("Select a Pastor", ['Pastor Joby','Guest Pastor','Executive Pastor'])
    select_event      = st.selectbox("Select Event", ['None','Easter','Promotion Week','Saturated Sunday','Christmas','Back to School','Inclement Weather'])
    st.divider()

    if st.button("Generate All Campus Projections"):
        nd  = date_mapping[selected_date_str]
        acd = []
        for cn, cs in campus_coefficients.items():
            sa, sk = 0, 0
            for st_, sc_ in cs.items():
                if 'Total Attendance' in sc_ or 'intercept' not in sc_: continue
                aa, ka = calculate_attendance(cn,st_,sc_,nd,select_week,select_pastor,select_event)
                cap = campus_capacities.get(cn,{'adult':1000,'kids':250})
                sa += aa; sk += ka
                acd.append({'Campus':cn,'Service_Time':st_,'Date':selected_date_str,'Week':select_week,'Pastor':select_pastor,'Event':select_event,'Adult_Attendance':round(aa),'Kids_Attendance':round(ka),'Adult_Capacity_Percent':round((aa/cap['adult'])*100,1),'Kids_Capacity_Percent':round((ka/cap['kids'])*100,1),'Adult_Capacity_Limit':cap['adult'],'Kids_Capacity_Limit':cap['kids']})
            for st_, sc_ in cs.items():
                if 'Total Attendance' not in sc_: continue
                aa, ka = calculate_total_based_attendance(cn,st_,sc_,sa,sk)
                cap = campus_capacities.get(cn,{'adult':1000,'kids':250})
                acd.append({'Campus':cn,'Service_Time':st_,'Date':selected_date_str,'Week':select_week,'Pastor':select_pastor,'Event':select_event,'Adult_Attendance':round(aa),'Kids_Attendance':round(ka),'Adult_Capacity_Percent':round((aa/cap['adult'])*100,1),'Kids_Capacity_Percent':round((ka/cap['kids'])*100,1),'Adult_Capacity_Limit':cap['adult'],'Kids_Capacity_Limit':cap['kids']})
            ta = sa+sum(r['Adult_Attendance'] for r in acd if r['Campus']==cn and 'Total Attendance' in cs.get(r['Service_Time'],{}))
            tk = sk+sum(r['Kids_Attendance']  for r in acd if r['Campus']==cn and 'Total Attendance' in cs.get(r['Service_Time'],{}))
            acd.append({'Campus':cn+" - TOTAL",'Service_Time':'ALL','Date':selected_date_str,'Week':select_week,'Pastor':select_pastor,'Event':select_event,'Adult_Attendance':round(ta),'Kids_Attendance':round(tk),'Adult_Capacity_Percent':'N/A','Kids_Capacity_Percent':'N/A','Adult_Capacity_Limit':'N/A','Kids_Capacity_Limit':'N/A'})
        df_all = pd.DataFrame(acd)
        st.subheader("Preview of Projections")
        st.dataframe(df_all.head(40))
        csv = "# All Campus Attendance Projections\n# Generated: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"\n# Parameters: Date="+selected_date_str+", Week="+str(select_week)+", Pastor="+select_pastor+", Event="+select_event+"\n\n"+df_all.to_csv(index=False)
        st.download_button("Download All Campus Projections (CSV)", csv, "All_Campus_Projections_"+selected_date_str.replace('-','_')+".csv", "text/csv")


# =====================================================================
with tab2:
# =====================================================================
    st.subheader("📡 Live Attendance — Easter 2026")

    EASTER_2026_DATE = "2026-04-05"
    sc_campus_list   = sorted(df_easter['Campus'].dropna().unique().tolist()) if not df_easter.empty else sorted(campus_coefficients.keys())

    sc1,sc2,sc3 = st.columns(3)
    with sc1: sc_campus   = st.selectbox("Campus",   ["All"]+sc_campus_list, key="sc_campus")
    with sc2: sc_day      = st.selectbox("Day",      ["All","Thu","Sat","Sun"], key="sc_day")
    with sc3: sc_category = st.selectbox("Category", ["Total","Adults","Kids"], key="sc_category")

    QUERY = """
        SELECT Campus, ServiceTime, ServiceDay, MetricName, Value
        FROM _com_CoE22_RockMetrics
        WHERE SundayDate = ?
        AND MetricName IN ('Attendance - Adults', 'Attendance - Kids')
    """
    try:
        conn   = get_connection()
        df_raw = pd.read_sql(QUERY, conn, params=[EASTER_2026_DATE])
    except Exception as e:
        st.warning("Could not load actuals: " + str(e))
        df_raw = pd.DataFrame(columns=['Campus','ServiceTime','ServiceDay','MetricName','Value'])

    # Map full day name to abbreviation
    DAY_ABBREV = {'Sunday':'Sun','Saturday':'Sat','Thursday':'Thu','Tuesday':'Tue','Wednesday':'Wed'}

    def normalise_time(val):
        """Convert any time format to 12-hour label matching the Excel e.g. '5:22 PM'"""
        if val is None: return ''
        s = str(val).strip().lower()
        for fmt in ['%I:%M %p','%H:%M:%S','%H:%M']:
            try:
                t = datetime.strptime(s, fmt)
                # Format as "5:22 PM" — strip leading zero
                return t.strftime('%I:%M %p').lstrip('0')
            except ValueError:
                continue
        return str(val).strip()

    if not df_raw.empty:
        df_raw['SvcLabel'] = df_raw['ServiceTime'].apply(normalise_time)
        df_raw['Day']      = df_raw['ServiceDay'].map(DAY_ABBREV).fillna(df_raw['ServiceDay'])
        df_pivot = df_raw.pivot_table(index=['Campus','Day','SvcLabel'], columns='MetricName', values='Value', aggfunc='sum').reset_index()
        df_pivot.columns.name = None
        df_pivot = df_pivot.rename(columns={'Attendance - Adults':'Actual_Adults','Attendance - Kids':'Actual_Kids'})
        for c in ['Actual_Adults','Actual_Kids']:
            if c not in df_pivot.columns: df_pivot[c] = 0
        df_pivot['Actual_Total'] = df_pivot['Actual_Adults'] + df_pivot['Actual_Kids']
    else:
        df_pivot = pd.DataFrame(columns=['Campus','Day','SvcLabel','Actual_Adults','Actual_Kids','Actual_Total'])

    if not df_easter.empty:
        df_proj = df_easter.rename(columns={'Service':'SvcLabel','Adults':'Proj_Adults','Kids':'Proj_Kids','Total':'Proj_Total'})
        if 'Proj_Adults' not in df_proj.columns: df_proj['Proj_Adults'] = 0
        if 'Proj_Kids'   not in df_proj.columns: df_proj['Proj_Kids']   = 0
        if 'Proj_Total'  not in df_proj.columns: df_proj['Proj_Total']  = df_proj['Proj_Adults']+df_proj['Proj_Kids']
        df_proj = df_proj[['Campus','Day','SvcLabel','Proj_Adults','Proj_Kids','Proj_Total']]
    else:
        df_proj = pd.DataFrame(columns=['Campus','Day','SvcLabel','Proj_Adults','Proj_Kids','Proj_Total'])

    df_score = df_proj.merge(df_pivot, on=['Campus','Day','SvcLabel'], how='left')
    for c in ['Actual_Adults','Actual_Kids','Actual_Total']:
        if c not in df_score.columns: df_score[c] = 0
        df_score[c] = df_score[c].fillna(0).astype(int)


    if sc_campus != "All": df_score = df_score[df_score['Campus']==sc_campus]
    if sc_day    != "All": df_score = df_score[df_score['Day']==sc_day]

    proj_col = 'Proj_Adults' if sc_category=='Adults' else 'Proj_Kids' if sc_category=='Kids' else 'Proj_Total'
    act_col  = 'Actual_Adults' if sc_category=='Adults' else 'Actual_Kids' if sc_category=='Kids' else 'Actual_Total'

    t_proj   = int(df_score[proj_col].sum())
    t_actual = int(df_score[act_col].sum())
    t_pct    = round((t_actual-t_proj)/t_proj*100,1) if t_proj!=0 else 0
    pc = "#27ae60" if t_pct>=0 else "#c0392b"
    pi = "▲" if t_pct>=0 else "▼"
    sc_label = sc_category+(" - "+sc_campus if sc_campus!="All" else "")

    st.markdown(
        "<style>.sc-stat-bar{display:flex;flex-wrap:wrap;background:#fff;border-radius:12px;border:1px solid #e0e4ea;box-shadow:0 1px 4px rgba(0,0,0,0.06);margin:1rem 0 1.5rem 0;overflow:hidden;}"
        ".sc-stat-item{flex:1;min-width:140px;text-align:center;padding:18px 16px;box-sizing:border-box;}.sc-stat-item+.sc-stat-item{border-left:1px solid #e8edf3;}"
        "@media(max-width:600px){.sc-stat-item{min-width:50%;flex-basis:50%;}.sc-stat-item:nth-child(3){border-left:none;border-top:1px solid #e8edf3;}}"
        ".sc-label{font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#aaa;margin-bottom:6px;}"
        ".sc-num{font-size:1.6rem;font-weight:800;line-height:1.1;}.sc-sub{font-size:0.72rem;color:#bbb;margin-top:3px;}</style>"
        '<div class="sc-stat-bar">'
        '<div class="sc-stat-item"><div class="sc-label">Projected</div><div class="sc-num" style="color:#2c3e50;">'+"{:,}".format(t_proj)+'</div><div class="sc-sub">'+sc_label+'</div></div>'
        '<div class="sc-stat-item"><div class="sc-label">Actual</div><div class="sc-num" style="color:#2c3e50;">'+"{:,}".format(t_actual)+'</div><div class="sc-sub">'+sc_label+'</div></div>'
        '<div class="sc-stat-item"><div class="sc-label">vs Projection</div><div class="sc-num" style="color:'+pc+';">'+pi+' '+str(abs(t_pct))+'%</div><div class="sc-sub">Percent difference</div></div>'
        '</div>', unsafe_allow_html=True)

    st.divider()

    if 'live_campus_open' not in st.session_state: st.session_state.live_campus_open = None
    DAY_ORDER = {'Thu':0,'Sat':1,'Sun':2}
    df_score_sorted = df_score.sort_values(by=['Campus','Day','SvcLabel'], key=lambda col: col.map(DAY_ORDER) if col.name=='Day' else col).reset_index(drop=True)

    for campus in df_score_sorted['Campus'].unique().tolist():
        df_c     = df_score_sorted[df_score_sorted['Campus']==campus]
        c_proj   = int(df_c[proj_col].sum())
        c_actual = int(df_c[act_col].sum())
        c_diff   = c_actual-c_proj
        c_pct    = round(c_diff/c_proj*100,1) if c_proj!=0 else 0
        cc       = "#27ae60" if c_diff>=0 else "#c0392b"
        ci       = "▲" if c_diff>=0 else "▼"
        is_open  = st.session_state.live_campus_open == campus

        st.markdown(
            '<div style="background:#fff;border-radius:10px;border:1px solid #e0e4ea;box-shadow:0 1px 5px rgba(0,0,0,0.07);padding:16px 18px;margin-bottom:4px;display:flex;align-items:center;justify-content:space-between;">'
            '<div style="font-weight:700;font-size:1rem;color:#2c3e50;">'+campus+'</div>'
            '<div style="display:flex;gap:20px;align-items:center;">'
            '<div style="text-align:right;"><div style="font-size:0.68rem;color:#aaa;text-transform:uppercase;letter-spacing:0.06em;">Actual</div><div style="font-weight:800;font-size:1.05rem;color:#2c3e50;">'+"{:,}".format(c_actual)+'</div></div>'
            '<div style="text-align:right;"><div style="font-size:0.68rem;color:#aaa;text-transform:uppercase;letter-spacing:0.06em;">vs Proj</div><div style="font-weight:800;font-size:1.05rem;color:'+cc+';">'+ci+' '+str(abs(c_pct))+'%</div></div>'
            '</div></div>', unsafe_allow_html=True)

        if st.button("▲ Collapse" if is_open else "▼ View services", key="campus_"+campus):
            st.session_state.live_campus_open = None if is_open else campus
            st.rerun()

        if is_open:
            for _,row in df_c.iterrows():
                pv  = int(row[proj_col]); av = int(row[act_col])
                dv  = av-pv; pctv = round(dv/pv*100,1) if pv!=0 else 0
                rc  = "#27ae60" if dv>=0 else "#c0392b"
                ri  = "▲" if dv>=0 else "▼"
                st.markdown(
                    '<div style="display:flex;gap:10px;flex-wrap:wrap;background:#f4f7fb;border-radius:10px;border:1px solid #e0e4ea;padding:12px 16px;margin:4px 0 4px 16px;align-items:center;">'
                    '<div style="min-width:100px;"><div style="font-size:0.72rem;color:#aaa;">'+str(row.get('Day',''))+'</div><div style="font-weight:700;font-size:0.9rem;color:#2c3e50;">'+str(row['SvcLabel'])+'</div></div>'
                    '<div style="display:flex;gap:8px;flex-wrap:wrap;flex:1;">'
                    '<div style="background:#fff;border-radius:8px;border:1px solid #e0e4ea;padding:8px 12px;text-align:center;flex:1;min-width:70px;"><div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;color:#aaa;margin-bottom:2px;">Projected</div><div style="font-size:1.1rem;font-weight:800;color:#2c3e50;">'+"{:,}".format(pv)+'</div></div>'
                    '<div style="background:#fff;border-radius:8px;border:1px solid #e0e4ea;padding:8px 12px;text-align:center;flex:1;min-width:70px;"><div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;color:#aaa;margin-bottom:2px;">Actual</div><div style="font-size:1.1rem;font-weight:800;color:#2c3e50;">'+"{:,}".format(av)+'</div></div>'
                    '<div style="background:#fff;border-radius:8px;border:1px solid #e0e4ea;padding:8px 12px;text-align:center;flex:1;min-width:70px;"><div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;color:#aaa;margin-bottom:2px;">Diff</div><div style="font-size:1.1rem;font-weight:800;color:'+rc+';">'+ri+' '+"{:,}".format(abs(dv))+'</div></div>'
                    '<div style="background:#fff;border-radius:8px;border:1px solid #e0e4ea;padding:8px 12px;text-align:center;flex:1;min-width:70px;"><div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;color:#aaa;margin-bottom:2px;">Diff %</div><div style="font-size:1.1rem;font-weight:800;color:'+rc+';">'+ri+' '+str(abs(pctv))+'%</div></div>'
                    '</div></div>', unsafe_allow_html=True)
            st.write("")
