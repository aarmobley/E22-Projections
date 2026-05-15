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
    /* Hide default button styling for campus cards */
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
    try:
        df = pd.read_csv(url)
        df['SundayDate'] = pd.to_datetime(df['SundayDate'])
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
    # Default to this coming Sunday or first available
    import datetime
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
    total = int(df_c['service_attendance'].sum())

    st.markdown(
        f'<div style="text-align:center;margin-bottom:16px;">'
        f'<div style="font-size:1.4rem;font-weight:800;color:#2c3e50;">{campus_name}</div>'
        f'<div style="font-size:2rem;font-weight:800;color:#C0392B;margin-top:4px;">{total:,}</div>'
        f'<div style="font-size:0.7rem;color:#aaa;text-transform:uppercase;letter-spacing:0.08em;">Projected Attendance</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    rows_html = ""
    for _, row in df_c.iterrows():
        att = int(row['service_attendance'])
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
            f'<td style="padding:14px;text-align:right;font-weight:700;font-size:1.05rem;">{att:,}</td>'
            f'<td style="padding:14px;text-align:right;">'
            f'<span style="padding:3px 10px;border-radius:6px;font-weight:600;font-size:0.82rem;color:{uc};background:{ubg};">{util}%</span></td>'
            f'<td style="padding:14px;text-align:right;color:#999;">{round(row["NormShare"] * 100, 1)}%</td>'
            f'</tr>'
        )

    st.markdown(
        '<div style="overflow-x:auto;">'
        '<table style="width:100%;border-collapse:collapse;font-size:0.9rem;">'
        '<thead><tr style="border-bottom:2px solid #C0392B;">'
        '<th style="text-align:left;padding:12px 14px;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;color:#aaa;">Service</th>'
        '<th style="text-align:right;padding:12px 14px;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;color:#aaa;">Projected</th>'
        '<th style="text-align:right;padding:12px 14px;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;color:#aaa;">Utilization</th>'
        '<th style="text-align:right;padding:12px 14px;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;color:#aaa;">Share</th>'
        '</tr></thead>'
        '<tbody>' + rows_html + '</tbody>'
        '</table></div>',
        unsafe_allow_html=True
    )

    st.write("")
    csv_out = df_c[['Campus', 'SundayDate', 'Service', 'service_attendance', 'AdultCapacity']].copy()
    csv_out['SundayDate'] = csv_out['SundayDate'].dt.strftime('%m-%d-%Y')
    st.download_button(
        f"Export {campus_name}",
        csv_out.to_csv(index=False),
        f"{campus_name.replace(' ', '_')}_Projections.csv",
        "text/csv"
    )


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
    Projected=('service_attendance', 'sum'),
    Services=('Service', 'count')
).reset_index().sort_values('Projected', ascending=False)

grand_total = int(df_totals['Projected'].sum())

st.markdown(
    f'<div style="text-align:center;margin:20px 0;">'
    f'<div style="font-size:2.2rem;font-weight:800;color:#C0392B;">{grand_total:,}</div>'
    f'<div style="font-size:0.72rem;color:#aaa;text-transform:uppercase;letter-spacing:0.08em;">Total Projected Attendance</div>'
    f'</div>',
    unsafe_allow_html=True
)

st.divider()


# ── Campus cards — tap to open dialog ────────────────────────────────────
for _, row in df_totals.iterrows():
    campus_name = row['Campus']
    c_total = int(row['Projected'])
    c_svcs = int(row['Services'])
    pct_of_total = round(c_total / grand_total * 100, 1) if grand_total > 0 else 0

    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;'
        f'background:#fff;border:1px solid #e0e4ea;border-radius:12px;padding:14px 18px;margin-bottom:4px;'
        f'box-shadow:0 1px 4px rgba(0,0,0,0.05);cursor:pointer;">'
        f'<div>'
        f'<div style="font-weight:700;font-size:1rem;color:#2c3e50;">{campus_name}</div>'
        f'<div style="font-size:0.7rem;color:#bbb;">{c_svcs} services · {pct_of_total}% of total</div>'
        f'</div>'
        f'<div style="font-weight:800;font-size:1.2rem;color:#C0392B;">{c_total:,}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="campus-btn">', unsafe_allow_html=True)
    if st.button(f"View {campus_name}", key=f"btn_{campus_name}"):
        show_campus(campus_name, df_date)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ── Export all ───────────────────────────────────────────────────────────
csv_all = df_date[['Campus', 'SundayDate', 'Service', 'service_attendance', 'AdultCapacity']].copy()
csv_all['SundayDate'] = csv_all['SundayDate'].dt.strftime('%m-%d-%Y')
st.download_button(
    "Export All Campuses (CSV)",
    csv_all.to_csv(index=False),
    f"All_Projections_{sel_date.strftime('%m-%d-%Y').replace('-', '_')}.csv",
    "text/csv"
)
