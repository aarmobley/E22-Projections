import streamlit as st
import pandas as pd

st.set_page_config(page_title="CoE22 Projections", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stSidebar"]{display:none;}
    [data-testid="stSidebarCollapsedControl"]{display:none;}
    [data-testid="stDialog"] > div {
        min-width: 750px !important;
        max-width: 950px !important;
    }
    @media (max-width: 640px) {
        [data-testid="stDialog"] > div {
            min-width: 96vw !important;
            max-width: 99vw !important;
            min-height: 85vh !important;
            margin: 0 auto !important;
            padding: 10px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

if st.query_params.get('embedded', 'false') == 'true':
    st.markdown('<style>.stApp > header{display:none;}.stApp > div:first-child{display:none;}.main .block-container{padding-top:0.5rem;}</style>', unsafe_allow_html=True)

st.image("https://raw.githubusercontent.com/aarmobley/CoE22/main/E22%20Logo.png", width=130)


# ── Load CSV ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_projections():
    url = "https://raw.githubusercontent.com/aarmobley/E22-Projections/main/Service_Projections.csv"
    kids_url = "https://raw.githubusercontent.com/aarmobley/E22-Projections/main/Kids%20to%20Adults%20%25.csv"
    try:
        df = pd.read_csv(url)
        df['SundayDate'] = pd.to_datetime(df['SundayDate'])

        # Clean ServiceDateTime to readable format
        cleaned = []
        for val in df['ServiceDateTime']:
            try:
                s = str(val).strip()
                parts = s.split(':')
                h = int(parts[0])
                m = parts[1]
                ampm = 'AM' if h < 12 else 'PM'
                h12 = h if h <= 12 else h - 12
                if h12 == 0:
                    h12 = 12
                cleaned.append(f"{h12}:{m} {ampm}")
            except Exception:
                cleaned.append(str(val))
        df['Service'] = cleaned

        # Load kids ratios — service-level join
        kids_df = pd.read_csv(kids_url)
        kids_df.columns = kids_df.columns.str.strip()

        # Extract just the time from ServiceDateTime (strip the 1899 date prefix)
        kids_df['ServiceTime'] = kids_df['ServiceDateTime'].astype(str).str.extract(r'(\d{2}:\d{2}:\d{2})')[0]

        # Parse the percentage column
        ratio_col = [c for c in kids_df.columns if 'Kids to Adults' in c]
        if ratio_col:
            kids_df['KidsRatio'] = pd.to_numeric(
                kids_df[ratio_col[0]].astype(str).str.replace('%', ''), errors='coerce'
            ) / 100
        else:
            kids_df['KidsRatio'] = 0.20
        kids_df['KidsRatio'] = kids_df['KidsRatio'].fillna(0)

        # Build campus-level fallback (average across services)
        campus_fallback = kids_df.groupby('Campus')['KidsRatio'].mean().reset_index()
        campus_fallback.columns = ['Campus', 'FallbackRatio']

        # Join on Campus + ServiceDateTime
        df = df.merge(
            kids_df[['Campus', 'ServiceTime', 'KidsRatio']],
            left_on=['Campus', 'ServiceDateTime'],
            right_on=['Campus', 'ServiceTime'],
            how='left'
        )

        # Fill missing with campus fallback
        df = df.merge(campus_fallback, on='Campus', how='left')
        df['KidsRatio'] = df['KidsRatio'].fillna(df['FallbackRatio']).fillna(0.20)
        df.drop(columns=['ServiceTime', 'FallbackRatio'], inplace=True, errors='ignore')

        df['kids_attendance'] = (df['service_attendance'] * df['KidsRatio']).round().astype(int)
        df['total_attendance'] = df['service_attendance'] + df['kids_attendance']

        # Remove services that don't actually exist at certain campuses
        bad_services = [
            ('Arlington', '07:22:00'),
            ('Baymeadows', '07:22:00'),
            ('Wildlight', '07:22:00'),
        ]
        for campus, svc in bad_services:
            df = df[~((df['Campus'] == campus) & (df['ServiceDateTime'] == svc))]

        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)


df_all, load_error = load_projections()
if load_error:
    st.error(f"Could not load projections: {load_error}")
    st.stop()

dates_sorted = sorted(df_all['SundayDate'].unique())


# ── Session state ────────────────────────────────────────────────────────
if 'date_idx' not in st.session_state:
    today = pd.Timestamp.now().normalize()
    default_idx = 0
    for i, d in enumerate(dates_sorted):
        if pd.Timestamp(d) >= today:
            default_idx = i
            break
    st.session_state.date_idx = default_idx

if 'picker_open' not in st.session_state:
    st.session_state.picker_open = False
if 'picker_campus' not in st.session_state:
    st.session_state.picker_campus = None


# ── Campus breakdown (rendered INSIDE the dialog) ────────────────────────
def render_campus_breakdown(campus_name, df):
    df_c = df[df['Campus'] == campus_name].copy()
    total_adults = int(df_c['service_attendance'].sum())
    total_kids = int(df_c['kids_attendance'].sum())
    total_all = int(df_c['total_attendance'].sum())

    st.markdown(
        f'<div style="text-align:center;margin-bottom:16px;">'
        f'<div style="font-size:1.4rem;font-weight:800;color:#2c3e50;">{campus_name}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    t1, t2, t3 = st.columns(3)
    with t1:
        st.metric("Adults", f"{total_adults:,}")
    with t2:
        st.metric("Kids", f"{total_kids:,}")
    with t3:
        st.metric("Total", f"{total_all:,}")

    rows_html = ""
    for _, row in df_c.iterrows():
        att = int(row['service_attendance'])
        kids = int(row['kids_attendance'])
        total = int(row['total_attendance'])
        cap = int(row['AdultCapacity'])
        util = round(att / cap * 100) if cap > 0 else 0
        if util > 100:
            uc, ubg = "#dc2626", "#fef2f2"
        elif util > 80:
            uc, ubg = "#d97706", "#fffbeb"
        else:
            uc, ubg = "#059669", "#f0fdf4"

        rows_html += (
            f'<tr style="border-bottom:1px solid #f0f0f0;">'
            f'<td style="padding:14px;font-weight:600;color:#2c3e50;">{row["Service"]}</td>'
            f'<td style="padding:14px;text-align:right;font-weight:700;color:#2c3e50;">{att:,}</td>'
            f'<td style="padding:14px;text-align:right;color:#2c3e50;">{kids:,}</td>'
            f'<td style="padding:14px;text-align:right;font-weight:700;color:#2c3e50;">{total:,}</td>'
            f'<td style="padding:14px;text-align:right;">'
            f'<span style="padding:3px 10px;border-radius:6px;font-weight:600;font-size:0.82rem;color:{uc};background:{ubg};">{util}%</span></td>'
            f'</tr>'
        )

    st.markdown(
        '<div style="overflow-x:auto;">'
        '<table style="width:100%;border-collapse:collapse;font-size:0.9rem;">'
        '<thead><tr style="border-bottom:2px solid #C0392B;">'
        '<th style="text-align:left;padding:12px 14px;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;color:#aaa;">Service</th>'
        '<th style="text-align:right;padding:12px 14px;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;color:#aaa;">Adults</th>'
        '<th style="text-align:right;padding:12px 14px;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;color:#aaa;">Kids</th>'
        '<th style="text-align:right;padding:12px 14px;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;color:#aaa;">Total</th>'
        '<th style="text-align:right;padding:12px 14px;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;color:#aaa;">Utilization</th>'
        '</tr></thead>'
        '<tbody>' + rows_html + '</tbody>'
        '</table></div>',
        unsafe_allow_html=True
    )

    st.write("")
    csv_out = df_c[['Campus', 'SundayDate', 'Service', 'service_attendance', 'kids_attendance', 'total_attendance', 'AdultCapacity']].copy()
    csv_out.columns = ['Campus', 'SundayDate', 'Service', 'Adults', 'Kids', 'Total', 'AdultCapacity']
    csv_out['SundayDate'] = csv_out['SundayDate'].dt.strftime('%m-%d-%Y')
    st.download_button(
        f"Export {campus_name}",
        csv_out.to_csv(index=False),
        f"{campus_name.replace(' ', '_')}_Projections.csv",
        "text/csv",
        key=f"dl_{campus_name}"
    )


# ── Campus list (rendered INSIDE the dialog) ─────────────────────────────
def render_campus_list(df):
    df_totals = df.groupby('Campus').agg(
        Adults=('service_attendance', 'sum'),
        Kids=('kids_attendance', 'sum'),
        Total=('total_attendance', 'sum'),
        Services=('Service', 'count')
    ).reset_index().sort_values('Campus')

    st.markdown(
        '<div style="font-size:0.8rem;color:#888;margin-bottom:10px;">'
        'Select a campus to see its service-level breakdown.</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(2)
    for i, (_, row) in enumerate(df_totals.iterrows()):
        with cols[i % 2]:
            label = f"{row['Campus']}  ·  {int(row['Total']):,}"
            if st.button(label, key=f"pick_{row['Campus']}", use_container_width=True):
                st.session_state.picker_campus = row['Campus']
                st.rerun()


# ── The single "wizard" dialog ───────────────────────────────────────────
@st.dialog("Campus Projections", width="large")
def campus_explorer(df):
    if st.session_state.picker_campus is None:
        render_campus_list(df)
    else:
        if st.button("← All campuses", key="back_to_list"):
            st.session_state.picker_campus = None
            st.rerun()
        render_campus_breakdown(st.session_state.picker_campus, df)


# ── Page ─────────────────────────────────────────────────────────────────
st.subheader("Weekly Service Projections")

# ── Date selector ─────────────────────────────────────────────────────
date_labels = [pd.Timestamp(d).strftime('%B %d, %Y') for d in dates_sorted]

today = pd.Timestamp.now().normalize()
default_idx = 0
for i, d in enumerate(dates_sorted):
    if pd.Timestamp(d) >= today:
        default_idx = i
        break

col_spacer1, col_date, col_spacer2 = st.columns([2, 3, 2])
with col_date:
    date_pick = st.selectbox("Select Sunday Date", date_labels, index=default_idx)
sel_date = pd.Timestamp(dates_sorted[date_labels.index(date_pick)])


# ── Grand total ──────────────────────────────────────────────────────────
df_date = df_all[df_all['SundayDate'] == sel_date].copy()
df_totals = df_date.groupby('Campus').agg(
    Adults=('service_attendance', 'sum'),
    Kids=('kids_attendance', 'sum'),
    Total=('total_attendance', 'sum'),
    Services=('Service', 'count')
).reset_index().sort_values('Campus')

grand_adults = int(df_totals['Adults'].sum())
grand_kids = int(df_totals['Kids'].sum())
grand_total = int(df_totals['Total'].sum())

st.markdown(
    f'<div style="text-align:center;margin:20px 0;">'
    f'<div style="font-size:2.2rem;font-weight:800;color:#C0392B;">{grand_total:,}</div>'
    f'<div style="font-size:0.72rem;color:#aaa;text-transform:uppercase;letter-spacing:0.08em;">Total Projected Attendance</div>'
    f'<div style="font-size:0.85rem;color:#888;margin-top:4px;">Adults: {grand_adults:,} &nbsp;·&nbsp; Kids: {grand_kids:,}</div>'
    f'</div>',
    unsafe_allow_html=True
)

st.divider()


# ── Single "View Campuses" button → opens the wizard dialog ──────────────
col_l, col_c, col_r = st.columns([2, 3, 2])
with col_c:
    if st.button("View Campuses", type="primary", use_container_width=True):
        st.session_state.picker_campus = None
        st.session_state.picker_open = True

if st.session_state.picker_open:
    campus_explorer(df_date)

st.divider()


# ── Export all ───────────────────────────────────────────────────────────
csv_all = df_date[['Campus', 'SundayDate', 'Service', 'service_attendance', 'kids_attendance', 'total_attendance', 'AdultCapacity']].copy()
csv_all.columns = ['Campus', 'SundayDate', 'Service', 'Adults', 'Kids', 'Total', 'AdultCapacity']
csv_all['SundayDate'] = csv_all['SundayDate'].dt.strftime('%m-%d-%Y')
st.download_button(
    "Export All Campuses (CSV)",
    csv_all.to_csv(index=False),
    f"All_Projections_{sel_date.strftime('%m-%d-%Y').replace('-', '_')}.csv",
    "text/csv"
)
