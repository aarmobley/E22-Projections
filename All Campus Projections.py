import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="CoE22 Projections", layout="wide", initial_sidebar_state="collapsed")

# ── CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"]{display:none;}
    [data-testid="stSidebarCollapsedControl"]{display:none;}
    button[data-baseweb="tab"]{font-size:1rem !important;font-weight:700 !important;}
</style>
""", unsafe_allow_html=True)

if st.query_params.get('embedded','false') == 'true':
    st.markdown('<style>.stApp > header{display:none;}.stApp > div:first-child{display:none;}.main .block-container{padding-top:0.5rem;}</style>', unsafe_allow_html=True)

st.image("https://raw.githubusercontent.com/aarmobley/CoE22/main/E22%20Logo.png", width=130)


# ── Cache Easter Excel ───────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_easter_excel():
    url = "https://github.com/aarmobley/E22-Projections/raw/main/Updated%202026%20Easter%20Projections2.xlsx"
    try:
        df = pd.read_excel(url, engine="openpyxl")
        if 'Service' in df.columns:
            cleaned = []
            for val in df['Service']:
                try:
                    if hasattr(val, 'strftime'):
                        cleaned.append(val.strftime('%I:%M %p').lstrip('0'))
                    else:
                        s = str(val).strip().replace(':00 ', ' ').replace(':00', '')
                        cleaned.append(s)
                except Exception:
                    cleaned.append(str(val))
            df['Service'] = cleaned
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)


# ── Campus coefficients ──────────────────────────────────────────────────
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


# ── Date setup ───────────────────────────────────────────────────────────
num_week = [w for _ in range(3) for w in range(1, 53)]
if len(num_week) < 156:
    num_week.append(53)
start_date = datetime(2025, 1, 5)
date_range = [start_date + timedelta(weeks=i) for i in range(156)]
epoch = datetime(1970, 1, 1)
date_mapping = {d.strftime('%m-%d-%Y'): (d - epoch).days for d in date_range}
date_week_options = [d.strftime('%m-%d-%Y') + " (Week " + str(w) + ")" for d, w in zip(date_range, num_week)]


# ── Calculation functions ────────────────────────────────────────────────
def calculate_attendance(campus, svc, coeff, num_date, week_num, pastor, event):
    we = coeff.get('week_number', 0) * week_num
    sd = coeff.get('sunday_date', 0) * num_date
    pe, ee = 0, 0
    if event != 'None':
        for k in [event, event.replace(' ', ''), event.replace(' ', 'to'), event.replace(' ', '_')]:
            if k in coeff:
                ee = coeff[k]
                break
    else:
        pe = coeff.get(pastor, 0)
    nb = coeff.get('New Building', 0) if campus == 'St. Johns' else 0
    pred = coeff.get('intercept', 0) + sd + we + pe + ee + nb
    att = pred if campus in ['St. Johns', 'North Jax'] else pred ** 2
    if event == 'Inclement Weather':
        r = coeff.get('Inclement Weather', 0.15)
        att = att * (1 - r) if r < 1 else att + r
    kk = 'kids_easter' if event == 'Easter' else 'kids_projection'
    km = 0.2
    for k in [kk, kk.replace('_', ' ').title(), 'Kids Projection', 'Kids Easter']:
        if k in coeff:
            km = coeff[k]
            break
    return max(0, att), max(0, att * km)


def calculate_total_based(campus, svc, coeff, oa, ok):
    m = coeff.get('Total Attendance', 0)
    return max(0, oa * m), max(0, ok * m)


def generate_projections(selected_date_str, select_week, select_pastor, select_event):
    nd = date_mapping[selected_date_str]
    all_data = []

    for cn, cs in campus_coefficients.items():
        sa, sk = 0, 0
        campus_rows = []

        # Standard services
        for st_, sc_ in cs.items():
            if 'Total Attendance' in sc_ or 'intercept' not in sc_:
                continue
            aa, ka = calculate_attendance(cn, st_, sc_, nd, select_week, select_pastor, select_event)
            cap = campus_capacities.get(cn, {'adult': 1000, 'kids': 250})
            sa += aa
            sk += ka
            campus_rows.append({
                'Campus': cn, 'Service': st_,
                'Adults': round(aa), 'Kids': round(ka), 'Total': round(aa + ka),
                'Adult %': str(round((aa / cap['adult']) * 100)) + '%',
                'Kids %': str(round((ka / cap['kids']) * 100)) + '%'
            })

        # Total-based services
        for st_, sc_ in cs.items():
            if 'Total Attendance' not in sc_:
                continue
            aa, ka = calculate_total_based(cn, st_, sc_, sa, sk)
            cap = campus_capacities.get(cn, {'adult': 1000, 'kids': 250})
            sa += aa
            sk += ka
            campus_rows.append({
                'Campus': cn, 'Service': st_,
                'Adults': round(aa), 'Kids': round(ka), 'Total': round(aa + ka),
                'Adult %': str(round((aa / cap['adult']) * 100)) + '%',
                'Kids %': str(round((ka / cap['kids']) * 100)) + '%'
            })

        # Campus total row
        campus_rows.append({
            'Campus': cn, 'Service': 'TOTAL',
            'Adults': round(sa), 'Kids': round(sk), 'Total': round(sa + sk),
            'Adult %': '', 'Kids %': ''
        })

        all_data.extend(campus_rows)

    return pd.DataFrame(all_data)


# ── TABS ─────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Easter 2026", "Weekly Projections"])


# =====================================================================
# TAB 1: EASTER 2026
# =====================================================================
with tab1:
    st.subheader("Easter 2026 Projections - April 5, 2026")

    df_easter, easter_load_error = load_easter_excel()

    try:
        if easter_load_error:
            raise Exception(easter_load_error)

        dd1, dd2, dd3 = st.columns(3)
        with dd1:
            days = sorted(df_easter['Day'].dropna().unique().tolist(),
                          key=lambda x: {'Thu': 0, 'Sat': 1, 'Sun': 2}.get(str(x), 3)) if 'Day' in df_easter.columns else []
            day_pick = st.selectbox("Filter by Day", ["All"] + days, key="easter_day")
        with dd2:
            campuses = sorted(df_easter['Campus'].dropna().unique().tolist()) if 'Campus' in df_easter.columns else []
            campus_pick = st.selectbox("Filter by Campus", ["All"] + campuses, key="easter_campus")
        with dd3:
            category_pick = st.selectbox("Filter by Category", ["Total", "Adults", "Kids"], key="easter_cat")

        df_show = df_easter.copy()
        if day_pick != "All":
            df_show = df_show[df_show['Day'] == day_pick]
        if campus_pick != "All":
            df_show = df_show[df_show['Campus'] == campus_pick]

        base_cols = [c for c in df_show.columns if c not in ['Adults', 'Kids', 'Total', 'KidsRatio']]
        if category_pick == "Adults":
            show_cols = base_cols + [c for c in ['Adults', 'AdultCapacity'] if c in df_show.columns]
            att_col = 'Adults'
        elif category_pick == "Kids":
            show_cols = base_cols + [c for c in ['Kids'] if c in df_show.columns]
            att_col = 'Kids'
        else:
            show_cols = base_cols + [c for c in ['Adults', 'Kids', 'Total'] if c in df_show.columns]
            att_col = 'Total'
        if category_pick != "Adults":
            show_cols = [c for c in show_cols if c != 'AdultCapacity']
        df_show = df_show[[c for c in show_cols if c in df_show.columns]]

        if att_col in df_show.columns:
            the_sum = int(df_show[att_col].sum())
        else:
            the_sum = 0
        svc_count = len(df_show)

        m1, m2 = st.columns(2)
        with m1:
            parts = [category_pick]
            if day_pick != "All":
                parts.append(day_pick)
            if campus_pick != "All":
                parts.append(campus_pick)
            st.metric(" - ".join(parts), f"{the_sum:,}")
        with m2:
            st.metric("Services Shown", svc_count)

        st.dataframe(df_show, use_container_width=True, hide_index=True)

        st.download_button("Download Easter Projections (CSV)",
                           df_show.to_csv(index=False),
                           "Easter_2026_Projections.csv", "text/csv")

    except Exception as e:
        st.error(f"Could not load Easter projections: {e}")


# =====================================================================
# TAB 2: WEEKLY PROJECTIONS
# =====================================================================
with tab2:
    st.subheader("Weekly Campus Projections")

    # --- Controls row ---
    c1, c2 = st.columns(2)
    with c1:
        date_sel = st.selectbox("Select Sunday Date", date_week_options, key="wk_date")
    with c2:
        pastor_sel = st.selectbox("Select a Pastor", ['Pastor Joby', 'Guest Pastor', 'Executive Pastor'], key="wk_pastor")

    event_sel = st.selectbox("Select Event", ['None', 'Easter', 'Promotion Week', 'Saturated Sunday', 'Christmas', 'Back to School', 'Inclement Weather'], key="wk_event")

    sel_date_str = date_sel.split(' ')[0]
    sel_week = int(date_sel.split('Week ')[-1].strip(')'))

    # --- Generate projections ---
    if st.button("Generate Projections", key="gen_btn"):
        df_proj = generate_projections(sel_date_str, sel_week, pastor_sel, event_sel)
        st.session_state['df_proj'] = df_proj
        st.session_state['proj_params'] = f"{sel_date_str} | {pastor_sel} | {event_sel}"

    if 'df_proj' in st.session_state:
        df_proj = st.session_state['df_proj']

        # Grand totals (from TOTAL rows)
        df_totals = df_proj[df_proj['Service'] == 'TOTAL'].copy()
        grand_adults = int(df_totals['Adults'].sum())
        grand_kids = int(df_totals['Kids'].sum())
        grand_total = int(df_totals['Total'].sum())

        st.markdown(f"**{st.session_state['proj_params']}**")

        g1, g2, g3 = st.columns(3)
        with g1:
            st.metric("Total Adults", f"{grand_adults:,}")
        with g2:
            st.metric("Total Kids", f"{grand_kids:,}")
        with g3:
            st.metric("Grand Total", f"{grand_total:,}")

        st.divider()

        # --- Campus cards with popover ---
        campus_list = sorted(df_totals['Campus'].unique().tolist())

        for campus_name in campus_list:
            campus_total_row = df_totals[df_totals['Campus'] == campus_name].iloc[0]
            c_adults = int(campus_total_row['Adults'])
            c_kids = int(campus_total_row['Kids'])
            c_total = int(campus_total_row['Total'])

            col_name, col_adults, col_kids, col_total, col_detail = st.columns([3, 1.5, 1.5, 1.5, 1.5])

            with col_name:
                st.markdown(f"**{campus_name}**")
            with col_adults:
                st.markdown(f"Adults: **{c_adults:,}**")
            with col_kids:
                st.markdown(f"Kids: **{c_kids:,}**")
            with col_total:
                st.markdown(f"Total: **{c_total:,}**")
            with col_detail:
                with st.popover("View Services"):
                    df_campus = df_proj[(df_proj['Campus'] == campus_name) & (df_proj['Service'] != 'TOTAL')].copy()
                    st.markdown(f"### {campus_name}")
                    st.dataframe(
                        df_campus[['Service', 'Adults', 'Kids', 'Total', 'Adult %', 'Kids %']],
                        use_container_width=True, hide_index=True
                    )

        st.divider()

        # Download
        st.download_button(
            "Download All Projections (CSV)",
            df_proj.to_csv(index=False),
            f"Projections_{sel_date_str.replace('-', '_')}.csv",
            "text/csv"
        )
