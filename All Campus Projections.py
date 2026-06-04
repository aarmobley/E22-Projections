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
    .campus-btn button {
        background: none !important;
        border: none !important;
        padding: 0 !important;
        margin: -8px 0 !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    .campus-btn button:hover {
        background: none !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

if st.query_params.get('embedded', 'false') == 'true':
    st.markdown('<style>.stApp > header{display:none;}.stApp > div:first-child{display:none;}.main .block-container{padding-top:0.5rem;}</style>', unsafe_allow_html=True)

st.image("https://raw.githubusercontent.com/aarmobley/CoE22/main/E22%20Logo.png", width=130)


# ── Load CSV ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
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

        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)


df_all, load_error = load_projections()
if load_error:
    st.error(f"Could not load projections: {load_error}")
    st.stop()

dates_sorted = sorted(df_all['SundayDate'].unique())


# ── Session state for date index ─────────────────────────────────────────
if 'date_idx' not in st.session_state:
    today = pd.Timestamp.now().normalize()
    default_idx = 0
    for i, d in enumerate(dates_sorted):
        if pd.Timestamp(d) >= today:
            default_idx = i
            break
    st.session_state.date_idx = default_idx


# ── Dialog ───────────────────────────────────────────────────────────────
@st.dialog("Service Breakdown", width="large")
def show_campus(campus_name, df):
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
            f'<td style="padding:14px;font-weight:600;">{row["Service"]}</td>'
            f'<td style="padding:14px;text-align:right;font-weight:700;">{att:,}</td>'
            f'<td style="padding:14px;text-align:right;">{kids:,}</td>'
            f'<td style="padding:14px;text-align:right;font-weight:700;">{total:,}</td>'
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
        "text/csv"
    )


# ── Page ─────────────────────────────────────────────────────────────────
st.subheader("Weekly Service Projections")


# ── Date navigator ───────────────────────────────────────────────────────
idx = st.session_state.date_idx
sel_date = pd.Timestamp(dates_sorted[idx])

col_prev, col_date, col_next = st.columns([1, 4, 1])
with col_prev:
    if st.button("◀", key="prev", disabled=(idx == 0)):
        st.session_state.date_idx = max(0, idx - 1)
        st.rerun()
with col_date:
    st.markdown(
        f'<div style="text-align:center;">'
        f'<div style="font-size:1.5rem;font-weight:800;color:#2c3e50;">{sel_date.strftime("%B %d, %Y")}</div>'
        f'<div style="font-size:0.75rem;color:#aaa;text-transform:uppercase;letter-spacing:0.08em;">Week {sel_date.isocalendar()[1]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
with col_next:
    if st.button("▶", key="next", disabled=(idx >= len(dates_sorted) - 1)):
        st.session_state.date_idx = min(len(dates_sorted) - 1, idx + 1)
        st.rerun()


# ── Grand total ──────────────────────────────────────────────────────────
df_date = df_all[df_all['SundayDate'] == sel_date].copy()
df_totals = df_date.groupby('Campus').agg(
    Adults=('service_attendance', 'sum'),
    Kids=('kids_attendance', 'sum'),
    Total=('total_attendance', 'sum'),
    Services=('Service', 'count')
).reset_index().sort_values('Total', ascending=False)

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


# ── Campus cards ─────────────────────────────────────────────────────────
for _, row in df_totals.iterrows():
    campus_name = row['Campus']
    c_adults = int(row['Adults'])
    c_kids = int(row['Kids'])
    c_total = int(row['Total'])
    c_svcs = int(row['Services'])

    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;'
        f'background:#fff;border:1px solid #e0e4ea;border-radius:12px;padding:14px 18px;margin-bottom:4px;'
        f'box-shadow:0 1px 4px rgba(0,0,0,0.05);">'
        f'<div>'
        f'<div style="font-weight:700;font-size:1rem;color:#2c3e50;">{campus_name}</div>'
        f'<div style="font-size:0.7rem;color:#bbb;">{c_svcs} services</div>'
        f'</div>'
        f'<div style="display:flex;gap:16px;flex-wrap:wrap;align-items:center;">'
        f'<div style="text-align:center;"><div style="font-size:0.6rem;color:#aaa;text-transform:uppercase;">Adults</div><div style="font-weight:700;">{c_adults:,}</div></div>'
        f'<div style="text-align:center;"><div style="font-size:0.6rem;color:#aaa;text-transform:uppercase;">Kids</div><div style="font-weight:700;">{c_kids:,}</div></div>'
        f'<div style="text-align:center;"><div style="font-size:0.6rem;color:#aaa;text-transform:uppercase;">Total</div><div style="font-weight:800;color:#C0392B;">{c_total:,}</div></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="campus-btn">', unsafe_allow_html=True)
    if st.button(f"View {campus_name}", key=f"btn_{campus_name}"):
        show_campus(campus_name, df_date)
    st.markdown('</div>', unsafe_allow_html=True)

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
