import streamlit as st
import pandas as pd

st.set_page_config(page_title="CoE22 Projections", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stSidebar"]{display:none;}
    [data-testid="stSidebarCollapsedControl"]{display:none;}
    [data-testid="stDialog"] > div {min-width: 700px !important; max-width: 900px !important;}
    @media (max-width: 640px) {
        [data-testid="stDialog"] > div {
            min-width: 95vw !important;
            max-width: 98vw !important;
            margin: 0 auto !important;
            padding: 12px !important;
        }
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

        # Clean ServiceDateTime to readable format (19:22:00 → 7:22 PM)
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


# ── Page ─────────────────────────────────────────────────────────────────
st.subheader("Weekly Service Projections")

# Date dropdown
dates_sorted = sorted(df_all['SundayDate'].unique())
date_labels = [d.strftime('%m-%d-%Y') for d in pd.to_datetime(dates_sorted)]
date_sel = st.selectbox("Select Sunday Date", date_labels)

# Filter to selected date
sel_date = pd.to_datetime(date_sel, format='%m-%d-%Y')
df_date = df_all[df_all['SundayDate'] == sel_date].copy()

# Build campus totals for this date
df_totals = df_date.groupby('Campus').agg(
    Total=('service_attendance', 'sum'),
    Services=('Service', 'count')
).reset_index().sort_values('Campus')

grand_total = int(df_totals['Total'].sum())

# Grand total metric
st.metric("All Campuses — Projected Attendance", f"{grand_total:,}")

st.divider()


# ── Dialog for service detail ────────────────────────────────────────────
@st.dialog("Service Breakdown", width="large")
def show_campus_detail(campus_name, df):
    df_campus = df[df['Campus'] == campus_name].copy()
    campus_total = int(df_campus['service_attendance'].sum())

    st.markdown(f"### {campus_name}")
    st.metric("Total Projected", f"{campus_total:,}")

    # Build HTML table
    rows_html = ""
    for _, row in df_campus.iterrows():
        rows_html += (
            f'<tr style="border-bottom:1px solid #eee;">'
            f'<td style="padding:10px 12px;font-weight:600;">{row["Service"]}</td>'
            f'<td style="padding:10px 12px;text-align:right;">{int(row["service_attendance"]):,}</td>'
            f'<td style="padding:10px 12px;text-align:right;color:#888;">{int(row["AdultCapacity"]):,}</td>'
            f'<td style="padding:10px 12px;text-align:right;color:#888;">{round(row["NormShare"] * 100, 1)}%</td>'
            f'</tr>'
        )

    st.markdown(
        '<div style="overflow-x:auto;margin-top:12px;">'
        '<table style="width:100%;border-collapse:collapse;font-size:0.9rem;">'
        '<thead><tr style="border-bottom:2px solid #C0392B;">'
        '<th style="text-align:left;padding:10px 12px;">Service</th>'
        '<th style="text-align:right;padding:10px 12px;">Projected</th>'
        '<th style="text-align:right;padding:10px 12px;">Capacity</th>'
        '<th style="text-align:right;padding:10px 12px;">Share</th>'
        '</tr></thead>'
        '<tbody>' + rows_html + '</tbody>'
        '</table></div>',
        unsafe_allow_html=True
    )


# ── Campus cards ─────────────────────────────────────────────────────────
for _, row in df_totals.iterrows():
    campus_name = row['Campus']
    c_total = int(row['Total'])
    c_services = int(row['Services'])

    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;'
        f'background:#fff;border:1px solid #e0e4ea;border-radius:10px;padding:12px 16px;margin-bottom:8px;'
        f'box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
        f'<div style="font-weight:700;font-size:1rem;color:#2c3e50;min-width:140px;">{campus_name}</div>'
        f'<div style="display:flex;gap:20px;flex-wrap:wrap;align-items:center;">'
        f'<div style="text-align:center;"><div style="font-size:0.65rem;color:#aaa;text-transform:uppercase;letter-spacing:0.05em;">Projected</div><div style="font-weight:800;font-size:1.1rem;color:#C0392B;">{c_total:,}</div></div>'
        f'<div style="text-align:center;"><div style="font-size:0.65rem;color:#aaa;text-transform:uppercase;letter-spacing:0.05em;">Services</div><div style="font-weight:700;">{c_services}</div></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )
    if st.button("View Services", key=f"detail_{campus_name}"):
        show_campus_detail(campus_name, df_date)

st.divider()

st.download_button(
    "Download Projections (CSV)",
    df_date[['Campus', 'SundayDate', 'Service', 'service_attendance', 'AdultCapacity']].to_csv(index=False),
    f"Projections_{date_sel.replace('-', '_')}.csv",
    "text/csv"
)
