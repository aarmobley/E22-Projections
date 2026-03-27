import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pyodbc

# ── MUST be first Streamlit command ──────────────────────────────────────
st.set_page_config(
    page_title="CoE22 Projections",
    layout="wide",
    initial_sidebar_state="collapsed")

# ── DB connection helper ─────────────────────────────────────────────────
@st.cache_resource
def get_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={st.secrets['db']['server']};"
        f"DATABASE={st.secrets['db']['database']};"
        f"UID={st.secrets['db']['username']};"
        f"PWD={st.secrets['db']['password']};"
    )
    return pyodbc.connect(conn_str)

# ── Shared CSS / Logo ────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stSidebarCollapsedControl"] {display: none;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <a href="https://e22projections.streamlit.app/"
       target="_blank" rel="noopener noreferrer"
       style="display:inline-block;background-color:#1f77b4;color:white;
              padding:8px 16px;border-radius:6px;text-decoration:none;
              font-size:14px;font-weight:500;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
        Open in New Window for Downloads
    </a>
</div>
""", unsafe_allow_html=True)

query_params = st.query_params
embedded = query_params.get('embedded', 'false') == 'true'
if embedded:
    st.markdown("""
    <style>
        .stApp > header {display: none;}
        .stApp > div:first-child {display: none;}
        .main .block-container {padding-top: 0.5rem;}
    </style>
    """, unsafe_allow_html=True)

logo_file = "https://raw.githubusercontent.com/aarmobley/CoE22/main/E22%20Logo.png"
st.image(logo_file, width=90)

# ── Shared data / helpers ────────────────────────────────────────────────
campus_coefficients = {
    'San Pablo': {
        '7:22': {
            'intercept': -142.667110, 'sunday_date': 0.009315, 'week_number': -0.056675,
            'Easter': 8.531395, 'Promotion Week': 1.680988, 'Back to School': 1.680988,
            'Saturated Sunday': 13.262508, 'kids_projection': .08, 'kids_easter': .08, 'Christmas': 5.896587
        },
        '9:00': {
            'intercept': -171.987662, 'sunday_date': 0.011074, 'week_number': -0.008375,
            'Guest Pastor': -1.329637, 'Executive Pastor': -0.615583, 'Pastor Joby': 1.029747,
            'Easter': 14.137845, 'Promotion Week': 1.400238, 'Back to School': 1.400238,
            'Saturated Sunday': 7.225865, 'kids_projection': 0.20, 'kids_easter': .12, 'Christmas': 4.600030
        },
        '11:22': {
            'intercept': -151.7846, 'sunday_date': 0.01, 'week_number': -0.0726,
            'Guest Pastor': -1.6713, 'Executive Pastor': -1.4246, 'Pastor Joby': 0.2733,
            'Easter': 14.6459, 'Promotion Week': 3.4931, 'Back to School': 3.4931,
            'Saturated Sunday': 6.2969, 'kids_projection': .15, 'kids_easter': .12,
            'kids_labor': 17.64, 'Christmas': 9.5353, 'Inclement Weather': .15
        },
        '4:22': {'Total Attendance': .06}
    },
    'Arlington': {
        '9:00': {
            'intercept': -38.65, 'sunday_date': .002963, 'week_number': .003602,
            'Guest Pastor': -.4529, 'Executive Pastor': -.8438, 'Pastor Joby': -.1221,
            'Easter': 6.193, 'BacktoSchool': .08546, 'Saturated Sunday': .9908,
            'kids_projection': 0.29, 'kids_easter': .25
        },
        '11:22': {
            'intercept': -4.1528006, 'sunday_date': 0.0011252, 'week_number': -.0178361,
            'Guest Pastor': -.7539401, 'Executive Pastor': -.3526798, 'Pastor Joby': .1628141,
            'Easter': 5.4945168, 'BacktoSchool': -.9172174, 'Saturated Sunday': 1.6824265,
            'kids_projection': .30, 'kids_easter': .25
        },
        '7:22': {'Total Attendance': .16}
    },
    'Baymeadows': {
        '9:00': {
            'intercept': -67.30, 'sunday_date': .004270, 'week_number': -.001089,
            'Guest Pastor': -.3866, 'Executive Pastor': -.2336, 'Pastor Joby': .4164,
            'Easter': 4.030, 'Promotion Week': 1.048, 'Saturated Sunday': 1.437,
            'kids_projection': 0.24, 'kids_easter': .19, 'Christmas': -1.303112
        },
        '11:22': {
            'intercept': -43.74, 'sunday_date': .003019, 'week_number': -.005647,
            'Guest Pastor': -.6090, 'Executive Pastor': -.2468, 'Pastor Joby': .2159,
            'Easter': 2.782, 'Promotion Week': .4619, 'Saturated Sunday': 2.013,
            'kids_projection': 0.21, 'kids_easter': .19, 'Christmas': -1.018843
        },
        '7:22': {'Total Attendance': .16}
    },
    'Fleming Island': {
        '7:22': {
            'intercept': -56.532818, 'sunday_date': 0.003535, 'week_number': -0.017519,
            'Guest Pastor': -0.132035, 'Executive Pastor': -0.818452, 'Pastor Joby': -0.266790,
            'Easter': 5.701672, 'Promotion Week': 1.144970, 'Back To School': 1.144970,
            'Saturated Sunday': 8.582320, 'kids_projection': .15, 'kids_easter': .13, 'Christmas': 6.746094
        },
        '9:00': {
            'intercept': -59.344, 'sunday_date': 0.0041, 'week_number': -0.0079,
            'Guest Pastor': -0.0018, 'Executive Pastor': -0.4856, 'Pastor Joby': 0.4656,
            'Easter': 7.6926, 'Promotion Week': 1.2294, 'Back To School': 1.2294,
            'Saturated Sunday': 2.1657, 'kids_projection': 0.27, 'kids_easter': .20, 'Christmas': 2.5449
        },
        '11:22': {
            'intercept': -52.0234, 'sunday_date': 0.0038, 'week_number': -0.0316,
            'Guest Pastor': -0.5974, 'Executive Pastor': -0.5027, 'Pastor Joby': -0.0229,
            'Easter': 6.1344, 'Promotion Week': 1.8042, 'Back To School': 1.8042,
            'Saturated Sunday': 3.6719, 'kids_projection': 0.27, 'kids_easter': .21, 'Christmas': 4.6251
        },
    },
    'Jesup': {
        '9:00': {
            'intercept': -73.607412, 'sunday_date': 0.004340, 'week_number': 0.014782,
            'Easter': 3.489182, 'Promotion Week': 1.612629, 'Back to School': 1.612629,
            'Saturated Sunday': 1.115047, 'kids_projection': 0.29, 'kids_easter': .25, 'Christmas': 3.982514
        },
        '11:22': {
            'intercept': -23.31375, 'sunday_date': 0.00167, 'week_number': -0.02805,
            'Easter': 2.24195, 'Promotion Week': 1.30396, 'Back to School': 1.30396,
            'Saturated Sunday': 2.74741, 'kids_projection': .33, 'kids_easter': .33, 'Christmas': 1.44838
        },
    },
    'Mandarin': {
        '9:00': {
            'intercept': -50.25, 'sunday_date': .003850, 'week_number': -.000900,
            'Guest Pastor': -.3200, 'Executive Pastor': -.2100, 'Pastor Joby': .3800,
            'Easter': 3.500, 'Promotion Week': .900, 'Saturated Sunday': 1.200,
            'kids_projection': 0.22, 'kids_easter': .18, 'Christmas': -1.100
        },
        '11:22': {
            'intercept': -35.60, 'sunday_date': .002800, 'week_number': -.004500,
            'Guest Pastor': -.5500, 'Executive Pastor': -.2200, 'Pastor Joby': .1900,
            'Easter': 2.400, 'Promotion Week': .4000, 'Saturated Sunday': 1.800,
            'kids_projection': 0.20, 'kids_easter': .17, 'Christmas': -.900
        }
    },
    'North Jax': {
        '9:00': {
            'intercept': -1717.7378, 'sunday_date': 0.1062, 'week_number': -0.6172,
            'Saturated Sunday': 156.4363, 'Easter': 125.3663, 'Promotion Week': 22.1525,
            'kids_projection': .32, 'kids_easter': .27, 'Christmas': 71.7278
        },
        '11:22': {
            'intercept': -85.5483, 'sunday_date': 0.0206, 'week_number': -0.2566,
            'Saturated Sunday': 248.2769, 'Easter': 179.4513, 'Promotion Week': 92.1327,
            'Back to School': 51.4164, 'kids_projection': .23, 'kids_easter': .29, 'Christmas': 20.1802
        },
        '7:22': {'Total Attendance': .23}
    },
    'Orange Park': {
        '9:00': {
            'intercept': -45.317708, 'sunday_date': 0.003027, 'week_number': 0.000409,
            'Guest Pastor': 0.105776, 'Executive Pastor': -0.054834, 'Pastor Joby': 0.545095,
            'Easter': 5.713542, 'BacktoSchool': 1.382218, 'Saturated Sunday': 1.507777,
            'Christmas': 1.679073, 'Kids Projection': .27, 'Kids Easter': .19
        },
        '11:22': {
            'intercept': -44.235901, 'sunday_date': 0.003001, 'week_number': -0.026953,
            'Guest Pastor': -0.758658, 'Executive Pastor': -0.305494, 'Pastor Joby': -0.325970,
            'Easter': 6.184421, 'BacktoSchool': 1.411250, 'Saturated Sunday': 1.431013,
            'Christmas': 3.997914, 'Kids Projection': .33, 'Kids Easter': .23
        },
    },
    'Ponte Vedra': {
        '9:00': {
            'intercept': -6.321507, 'sunday_date': 0.001285, 'week_number': -0.012768,
            'Easter': 5.188487, 'Promotion Week': 1.4468, 'Back to School': 1.443064,
            'Saturated Sunday': 1.851372, 'kids_projection': 0.22, 'kids_easter': .12,
            'Christmas': 2.685164, 'Inclement Weather': .15
        },
        '11:22': {
            'intercept': 36.036786, 'sunday_date': -0.001003, 'week_number': -0.013473,
            'Easter': 6.922727, 'Promotion Week': 1.979547, 'Back to School': 1.952,
            'Saturated Sunday': 3.556182, 'kids_projection': .15, 'kids_easter': .12,
            'kids_labor': 17.64, 'Christmas': 4.411963, 'Inclement Weather': .15
        }
    },
    'St. Johns': {
        '9:00': {
            'intercept': -7376.0256, 'sunday_date': 0.4081, 'week_number': -0.7781,
            'Guest Pastor': -25.0405, 'Executive Pastor': -10.8755, 'Pastor Joby': -12.5410,
            'Easter': 368.6713, 'BacktoSchool': 99.6941, 'Saturated Sunday': 144.4888,
            'Christmas': 267.1487, 'Kids Projection': .35, 'Kids Easter': .24, 'New Building': 674.2372
        },
        '11:22': {
            'intercept': -5681.6164, 'sunday_date': 0.3158, 'week_number': -1.4148,
            'Guest Pastor': -13.0240, 'Executive Pastor': 0.1442, 'Pastor Joby': 2.1450,
            'Easter': 373.0117, 'BacktoSchool': 129.6823, 'Saturated Sunday': 156.1531,
            'Christmas': 285.94632, 'Kids Projection': .25, 'Kids Easter': .15, 'New Building': 492.5563
        },
        '7:22': {'Total Attendance': .20}
    }
}

campus_capacities = {
    'San Pablo':      {'adult': 3001, 'kids': 750},
    'Arlington':      {'adult': 850,  'kids': 225},
    'Baymeadows':     {'adult': 525,  'kids': 247},
    'Fleming Island': {'adult': 766,  'kids': 250},
    'Jesup':          {'adult': 290,  'kids': 105},
    'Mandarin':       {'adult': 840,  'kids': 330},
    'North Jax':      {'adult': 700,  'kids': 350},
    'Orange Park':    {'adult': 700,  'kids': 262},
    'Ponte Vedra':    {'adult': 545,  'kids': 210},
    'St. Johns':      {'adult': 1948, 'kids': 559}
}

num_week = [week for _ in range(3) for week in range(1, 53)]
if len(num_week) < 156:
    num_week.append(53)

start_date        = datetime(2025, 1, 5)
date_range        = [start_date + timedelta(weeks=i) for i in range(156)]
epoch             = datetime(1970, 1, 1)
date_mapping      = {d.strftime('%m-%d-%Y'): (d - epoch).days for d in date_range}
date_week_options = [f"{d.strftime('%m-%d-%Y')} (Week {w})" for d, w in zip(date_range, num_week)]


def calculate_attendance(campus, service_time, coefficients, numerical_date, week_num, pastor, event):
    weeknum_effect    = coefficients.get('week_number', 0) * week_num
    sundaydate_effect = coefficients.get('sunday_date', 0) * numerical_date
    pastor_effect, event_effect = 0, 0
    if event != 'None':
        for key in [event, event.replace(' ', ''), event.replace(' ', 'to'), event.replace(' ', '_')]:
            if key in coefficients:
                event_effect = coefficients[key]
                break
    else:
        pastor_effect = coefficients.get(pastor, 0)
    new_building_effect = coefficients.get('New Building', 0) if campus == 'St. Johns' else 0
    intercept   = coefficients.get('intercept', 0)
    prediction  = intercept + sundaydate_effect + weeknum_effect + pastor_effect + event_effect + new_building_effect
    adult_att   = prediction if campus in ['St. Johns', 'North Jax'] else prediction ** 2
    if event == 'Inclement Weather':
        r = coefficients.get('Inclement Weather', 0.15)
        adult_att = adult_att * (1 - r) if r < 1 else adult_att + r
    kids_key = 'kids_easter' if event == 'Easter' else 'kids_projection'
    kids_mult = 0.2
    for k in [kids_key, kids_key.replace('_', ' ').title(), 'Kids Projection', 'Kids Easter']:
        if k in coefficients:
            kids_mult = coefficients[k]
            break
    return max(0, adult_att), max(0, adult_att * kids_mult)


def calculate_total_based_attendance(campus, service_time, coefficients, other_adult, other_kids):
    m = coefficients.get('Total Attendance', 0)
    return max(0, other_adult * m), max(0, other_kids * m)


def style_table(df, hover_color="#fdecea"):
    headers   = "".join("<th>" + col + "</th>" for col in df.columns)
    rows_html = ""
    for i, (_, row) in enumerate(df.iterrows()):
        row_class = "row-even" if i % 2 == 0 else "row-odd"
        cells = ""
        for col in df.columns:
            val   = row[col]
            align = "right" if isinstance(val, (int, float)) else "left"
            if isinstance(val, float) and val == int(val):
                val = "{:,}".format(int(val))
            elif isinstance(val, (int, float)):
                val = "{:,}".format(val)
            cells += '<td style="text-align:' + align + '">' + str(val) + '</td>'
        rows_html += '<tr class="' + row_class + '">' + cells + '</tr>'
    return """
    <style>
        .modern-table-wrap {overflow-x:auto;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin:1rem 0;}
        .modern-table {width:100%;border-collapse:collapse;font-family:'Segoe UI',sans-serif;font-size:0.875rem;}
        .modern-table thead tr {background:#C0392B;color:white;text-align:left;letter-spacing:0.04em;font-size:0.8rem;text-transform:uppercase;}
        .modern-table thead th {padding:12px 16px;font-weight:600;white-space:nowrap;}
        .modern-table tbody tr.row-even {background-color:#ffffff;}
        .modern-table tbody tr.row-odd  {background-color:#f4f7fb;}
        .modern-table tbody tr:hover    {background-color:""" + hover_color + """;transition:background 0.15s ease;}
        .modern-table td {padding:10px 16px;border-bottom:1px solid #e8edf3;white-space:nowrap;color:#2c3e50;}
    </style>
    <div class="modern-table-wrap">
        <table class="modern-table">
            <thead><tr>""" + headers + """</tr></thead>
            <tbody>""" + rows_html + """</tbody>
        </table>
    </div>"""


# ── TABS ─────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 Projections", "🎯 Scorecard"])


# =====================================================================
with tab1:
# =====================================================================

    # -----------------------------------------------------------------
    # EASTER 2026 PROJECTIONS
    # -----------------------------------------------------------------
    st.subheader("Easter 2026 Projections")

    data_2025_rows = [
        ('Arlington','Sun','Adults',682),('Arlington','Sun','Kids',148),
        ('Arlington','Sun','Adults',556),('Arlington','Sun','Kids',90),
        ('Arlington','Thu','Adults',217),('Arlington','Thu','Kids',41),
        ('Baymeadows','Sun','Adults',410),('Baymeadows','Sun','Kids',95),
        ('Baymeadows','Sun','Adults',294),('Baymeadows','Sun','Kids',42),
        ('Baymeadows','Thu','Adults',267),('Baymeadows','Thu','Kids',20),
        ('Fleming Island','Sat','Adults',479),('Fleming Island','Sat','Kids',110),
        ('Fleming Island','Sat','Adults',609),('Fleming Island','Sat','Kids',157),
        ('Fleming Island','Sun','Adults',802),('Fleming Island','Sun','Kids',166),
        ('Fleming Island','Sun','Adults',694),('Fleming Island','Sun','Kids',135),
        ('Fleming Island','Thu','Adults',626),('Fleming Island','Thu','Kids',84),
        ('Jesup','Sun','Adults',270),('Jesup','Sun','Kids',52),
        ('Jesup','Sun','Adults',139),('Jesup','Sun','Kids',43),
        ('Jesup','Thu','Adults',101),('Jesup','Thu','Kids',21),
        ('Mandarin','Sun','Adults',869),('Mandarin','Sun','Kids',224),
        ('Mandarin','Sun','Adults',525),('Mandarin','Sun','Kids',80),
        ('Mandarin','Thu','Adults',322),('Mandarin','Thu','Kids',50),
        ('North Jax','Sat','Adults',394),('North Jax','Sat','Kids',71),
        ('North Jax','Sun','Adults',566),('North Jax','Sun','Kids',149),
        ('North Jax','Sun','Adults',589),('North Jax','Sun','Kids',122),
        ('North Jax','Thu','Adults',252),('North Jax','Thu','Kids',48),
        ('Orange Park','Sun','Adults',436),('Orange Park','Sun','Kids',100),
        ('Orange Park','Sun','Adults',354),('Orange Park','Sun','Kids',114),
        ('Orange Park','Thu','Adults',149),('Orange Park','Thu','Kids',60),
        ('Palatka','Sun','Adults',190),('Palatka','Sun','Kids',60),
        ('Ponte Vedra','Sat','Adults',276),('Ponte Vedra','Sat','Kids',86),
        ('Ponte Vedra','Sun','Adults',601),('Ponte Vedra','Sun','Kids',148),
        ('Ponte Vedra','Sun','Adults',541),('Ponte Vedra','Sun','Kids',108),
        ('San Pablo','Sat','Adults',2452),('San Pablo','Sat','Kids',384),
        ('San Pablo','Sat','Adults',2459),('San Pablo','Sat','Kids',271),
        ('San Pablo','Sun','Adults',913),('San Pablo','Sun','Kids',78),
        ('San Pablo','Sun','Adults',3378),('San Pablo','Sun','Kids',359),
        ('San Pablo','Sun','Adults',3121),('San Pablo','Sun','Kids',340),
        ('San Pablo','Thu','Adults',3381),('San Pablo','Thu','Kids',259),
        ('St. Augustine','Sun','Adults',350),('St. Augustine','Sun','Kids',0),
        ('St. Augustine','Sun','Adults',180),('St. Augustine','Sun','Kids',0),
        ('St. Johns','Sat','Adults',959),('St. Johns','Sat','Kids',246),
        ('St. Johns','Sat','Adults',701),('St. Johns','Sat','Kids',152),
        ('St. Johns','Sun','Adults',1320),('St. Johns','Sun','Kids',266),
        ('St. Johns','Sun','Adults',1373),('St. Johns','Sun','Kids',272),
        ('Wildlight','Sun','Adults',407),('Wildlight','Sun','Kids',82),
        ('Wildlight','Sun','Adults',364),('Wildlight','Sun','Kids',62),
    ]
    df_2025 = pd.DataFrame(data_2025_rows, columns=['Campus','Day','Category','Count'])

    easter_url = "https://github.com/aarmobley/E22-Projections/raw/main/Updated%202026%20Easter%20Projections2.xlsx"

    try:
        df_easter = pd.read_excel(easter_url, engine="openpyxl")

        if 'Service' in df_easter.columns:
            cleaned = []
            for val in df_easter['Service']:
                try:
                    if hasattr(val, 'strftime'):
                        cleaned.append(val.strftime('%I:%M %p').lstrip('0'))
                    else:
                        s = str(val).strip().replace(':00 ', ' ').replace(':00', '')
                        cleaned.append(s)
                except Exception:
                    cleaned.append(str(val))
            df_easter['Service'] = cleaned

        dd1, dd2, dd3 = st.columns(3)
        with dd1:
            if 'Day' in df_easter.columns:
                days = sorted(df_easter['Day'].dropna().unique().tolist(),
                              key=lambda x: {'Thu': 0, 'Sat': 1, 'Sun': 2}.get(str(x), 3))
                day_pick = st.selectbox("Filter by Day", ["All"] + days)
            else:
                day_pick = "All"
        with dd2:
            if 'Campus' in df_easter.columns:
                campuses = sorted(df_easter['Campus'].dropna().unique().tolist())
                campus_pick = st.selectbox("Filter by Campus", ["All"] + campuses)
            else:
                campus_pick = "All"
        with dd3:
            category_pick = st.selectbox("Filter by Category", ["Total", "Adults", "Kids"])

        df_show = df_easter.copy()
        if day_pick    != "All": df_show = df_show[df_show['Day']    == day_pick]
        if campus_pick != "All": df_show = df_show[df_show['Campus'] == campus_pick]

        base_cols = [c for c in df_show.columns if c not in ['Adults','Kids','Total','KidsRatio']]
        if category_pick == "Adults":
            show_cols = base_cols + [c for c in ['Adults','AdultCapacity'] if c in df_show.columns]
            att_col   = 'Adults'
        elif category_pick == "Kids":
            show_cols = base_cols + [c for c in ['Kids'] if c in df_show.columns]
            att_col   = 'Kids'
        else:
            show_cols = base_cols + [c for c in ['Adults','Kids','Total'] if c in df_show.columns]
            att_col   = 'Total'

        if category_pick != "Adults":
            show_cols = [c for c in show_cols if c != 'AdultCapacity']
        df_show = df_show[[c for c in show_cols if c in df_show.columns]]

        if att_col in df_show.columns:
            the_sum = int(df_show[att_col].sum())
        elif category_pick == "Total":
            the_sum = (int(df_show['Adults'].sum()) if 'Adults' in df_show.columns else 0) + \
                      (int(df_show['Kids'].sum())   if 'Kids'   in df_show.columns else 0)
        else:
            the_sum = 0
        svc_count = len(df_show)

        df_2025f = df_2025.copy()
        if campus_pick != "All": df_2025f = df_2025f[df_2025f['Campus'] == campus_pick]
        if day_pick    != "All": df_2025f = df_2025f[df_2025f['Day']    == day_pick]

        if category_pick == "Adults":
            sum_2025 = int(df_2025f[df_2025f['Category'] == 'Adults']['Count'].sum())
        elif category_pick == "Kids":
            sum_2025 = int(df_2025f[df_2025f['Category'] == 'Kids']['Count'].sum())
        else:
            sum_2025 = int(df_2025f['Count'].sum())

        label_parts = [category_pick]
        if day_pick    != "All": label_parts.append(day_pick)
        if campus_pick != "All": label_parts.append(campus_pick)
        label_base = " - ".join(label_parts)
        yoy_delta  = the_sum - sum_2025

        diff_color = "#27ae60" if yoy_delta >= 0 else "#c0392b"
        diff_icon  = "▲" if yoy_delta >= 0 else "▼"
        diff_bg    = "#eafaf1" if yoy_delta >= 0 else "#fdedec"

        # ── Metric cards (built with string concat to avoid f-string brace conflicts) ──
        card_style = (
            "flex:1;min-width:160px;border-radius:14px;"
            "box-shadow:0 2px 10px rgba(0,0,0,0.08);padding:20px 24px;"
        )
        label_style  = "font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#888;margin-bottom:6px;"
        sub_style    = "font-size:0.8rem;color:#aaa;margin-bottom:4px;"
        num_style    = "font-size:2rem;font-weight:800;line-height:1.1;"

        red_card  = card_style + 'background:#fff;border-top:4px solid #C0392B;'
        cards_html = (
            '<div style="display:flex;gap:16px;margin:1rem 0 1.5rem 0;flex-wrap:wrap;">'

            + '<div style="' + red_card + '">'
            + '<div style="' + label_style + '">2026 Projection</div>'
            + '<div style="' + sub_style   + '">' + label_base + '</div>'
            + '<div style="' + num_style   + 'color:#2c3e50;">' + "{:,}".format(the_sum) + '</div>'
            + '</div>'

            + '<div style="' + red_card + '">'
            + '<div style="' + label_style + '">2025 Actual</div>'
            + '<div style="' + sub_style   + '">' + label_base + '</div>'
            + '<div style="' + num_style   + 'color:#2c3e50;">' + "{:,}".format(sum_2025) + '</div>'
            + '</div>'

            + '<div style="' + card_style + 'background:' + diff_bg + ';border-top:4px solid ' + diff_color + ';">'
            + '<div style="' + label_style + '">YoY Difference</div>'
            + '<div style="' + sub_style   + '">vs Last Year</div>'
            + '<div style="' + num_style   + 'color:' + diff_color + ';">' + diff_icon + ' ' + "{:,}".format(abs(yoy_delta)) + '</div>'
            + '</div>'

            + '<div style="' + red_card + '">'
            + '<div style="' + label_style + '">Services Shown</div>'
            + '<div style="' + sub_style   + '">In current filter</div>'
            + '<div style="' + num_style   + 'color:#2c3e50;">' + str(svc_count) + '</div>'
            + '</div>'

            + '</div>'
        )

        st.markdown(cards_html, unsafe_allow_html=True)

        st.markdown(style_table(df_show), unsafe_allow_html=True)
        st.write("")

        st.download_button(
            label="Download Easter Projections (CSV)",
            data=df_show.to_csv(index=False),
            file_name="Easter_2026_Projections.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error("Could not load Easter projections file: " + str(e))
        st.info("Make sure the Excel file is uploaded to the GitHub repo.")

    st.divider()

    # -----------------------------------------------------------------
    # WEEKLY PROJECTIONS
    # -----------------------------------------------------------------
    date_options      = st.selectbox("Select Sunday Date", date_week_options)
    selected_date_str = date_options.split(' ')[0]
    select_week       = int(date_options.split('Week ')[-1].strip(')'))

    pastor_options = ['Pastor Joby', 'Guest Pastor', 'Executive Pastor']
    event_options  = ['None', 'Easter', 'Promotion Week', 'Saturated Sunday', 'Christmas', 'Back to School', 'Inclement Weather']

    select_pastor = st.selectbox("Select a Pastor", pastor_options)
    select_event  = st.selectbox("Select Event",    event_options)

    st.divider()

    if st.button("Generate All Campus Projections"):
        numerical_date  = date_mapping[selected_date_str]
        all_campus_data = []

        for campus_name, campus_services in campus_coefficients.items():
            std_adult, std_kids = 0, 0

            for svc_time, svc_coeff in campus_services.items():
                if 'Total Attendance' in svc_coeff or 'intercept' not in svc_coeff:
                    continue
                adult_att, kids_att = calculate_attendance(
                    campus_name, svc_time, svc_coeff,
                    numerical_date, select_week, select_pastor, select_event)
                cap = campus_capacities.get(campus_name, {'adult': 1000, 'kids': 250})
                std_adult += adult_att
                std_kids  += kids_att
                all_campus_data.append({
                    'Campus': campus_name, 'Service_Time': svc_time,
                    'Date': selected_date_str, 'Week': select_week,
                    'Pastor': select_pastor, 'Event': select_event,
                    'Adult_Attendance': round(adult_att),
                    'Kids_Attendance':  round(kids_att),
                    'Adult_Capacity_Percent': round((adult_att / cap['adult']) * 100, 1),
                    'Kids_Capacity_Percent':  round((kids_att  / cap['kids'])  * 100, 1),
                    'Adult_Capacity_Limit': cap['adult'],
                    'Kids_Capacity_Limit':  cap['kids']
                })

            for svc_time, svc_coeff in campus_services.items():
                if 'Total Attendance' not in svc_coeff:
                    continue
                adult_att, kids_att = calculate_total_based_attendance(
                    campus_name, svc_time, svc_coeff, std_adult, std_kids)
                cap = campus_capacities.get(campus_name, {'adult': 1000, 'kids': 250})
                all_campus_data.append({
                    'Campus': campus_name, 'Service_Time': svc_time,
                    'Date': selected_date_str, 'Week': select_week,
                    'Pastor': select_pastor, 'Event': select_event,
                    'Adult_Attendance': round(adult_att),
                    'Kids_Attendance':  round(kids_att),
                    'Adult_Capacity_Percent': round((adult_att / cap['adult']) * 100, 1),
                    'Kids_Capacity_Percent':  round((kids_att  / cap['kids'])  * 100, 1),
                    'Adult_Capacity_Limit': cap['adult'],
                    'Kids_Capacity_Limit':  cap['kids']
                })

            total_adults = std_adult + sum(
                r['Adult_Attendance'] for r in all_campus_data
                if r['Campus'] == campus_name and
                   'Total Attendance' in campus_services.get(r['Service_Time'], {}))
            total_kids = std_kids + sum(
                r['Kids_Attendance'] for r in all_campus_data
                if r['Campus'] == campus_name and
                   'Total Attendance' in campus_services.get(r['Service_Time'], {}))
            all_campus_data.append({
                'Campus': campus_name + " - TOTAL", 'Service_Time': 'ALL',
                'Date': selected_date_str, 'Week': select_week,
                'Pastor': select_pastor, 'Event': select_event,
                'Adult_Attendance': round(total_adults),
                'Kids_Attendance':  round(total_kids),
                'Adult_Capacity_Percent': 'N/A', 'Kids_Capacity_Percent': 'N/A',
                'Adult_Capacity_Limit':   'N/A', 'Kids_Capacity_Limit':   'N/A'
            })

        df_all = pd.DataFrame(all_campus_data)
        st.subheader("Preview of Projections")
        st.dataframe(df_all.head(40))

        csv_data  = "# All Campus Attendance Projections\n"
        csv_data += "# Generated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n"
        csv_data += "# Parameters: Date=" + selected_date_str + ", Week=" + str(select_week) + ", Pastor=" + select_pastor + ", Event=" + select_event + "\n\n"
        csv_data += df_all.to_csv(index=False)

        st.download_button(
            label="Download All Campus Projections (CSV)",
            data=csv_data,
            file_name="All_Campus_Projections_" + selected_date_str.replace('-', '_') + ".csv",
            mime="text/csv"
        )


# =====================================================================
with tab2:
# =====================================================================
    st.subheader("🎯 Scorecard — coming soon")
    # Paste scorecard code here when ready
