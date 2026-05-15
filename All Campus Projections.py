import streamlit as st
import pandas as pd

st.set_page_config(page_title="CoE22 Projections", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stSidebar"]{display:none;}
    [data-testid="stSidebarCollapsedControl"]{display:none;}
    /* Force dropdowns to open downward */
    [data-baseweb="popover"] {
        margin-top: 0 !important;
    }
    [data-baseweb="menu"] {
        max-height: 300px !important;
    }
    /* Add breathing room below dropdowns */
    [data-testid="stSelectbox"] {
        margin-bottom: 16px !important;
    }
    /* Dialog: large on desktop, full screen on mobile */
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


# ── Dialog ───────────────────────────────────────────────────────────────
@st.dialog("Campus Projections", width="large")
def show_campus(campus_name, df):
    df_campus = df[df['Campus'] == campus_name].copy()
    campus_total = int(df_campus['service_attendance'].sum())

    st.markdown(f"### {campus_name}")
    st.metric("Projected Attendance", f"{campus_total:,}")

    rows_html = ""
    for _, row in df_campus.iterrows():
        att = int(row['service_attendance'])
        cap = int(row['AdultCapacity'])
        util = round(att / cap * 100) if cap > 0 else 0

        if util > 100:
            uc = "#dc2626"
        elif util > 80:
            uc = "#d97706"
        else:
            uc = "#059669"

        rows_html += (
            f'<tr style="border-bottom:1px solid #eee;">'
            f'<td style="padding:12px 14px;font-weight:600;">{row["Service"]}</td>'
            f'<td style="padding:12px 14px;text-align:right;font-weight:700;font-size:1.05rem;">{att:,}</td>'
            f'<td style="padding:12px 14px;text-align:right;color:#888;">{cap:,}</td>'
            f'<td style="padding:12px 14px;text-align:right;">'
            f'<span style="font-weight:600;color:{uc};">{util}%</span></td>'
            f'<td style="padding:12px 14px;text-align:right;color:#888;">{round(row["NormShare"] * 100, 1)}%</td>'
            f'</tr>'
        )

    st.markdown(
        '<div style="overflow-x:auto;margin-top:12px;">'
        '<table style="width:100%;border-collapse:collapse;font-size:0.9rem;">'
        '<thead><tr style="border-bottom:2px solid #C0392B;background:#fafafa;">'
        '<th style="text-align:left;padding:12px 14px;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;color:#888;">Service</th>'
        '<th style="text-align:right;padding:12px 14px;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;color:#888;">Projected</th>'
        '<th style="text-align:right;padding:12px 14px;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;color:#888;">Capacity</th>'
        '<th style="text-align:right;padding:12px 14px;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;color:#888;">Utilization</th>'
        '<th style="text-align:right;padding:12px 14px;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;color:#888;">Share</th>'
        '</tr></thead>'
        '<tbody>' + rows_html + '</tbody>'
        '</table></div>',
        unsafe_allow_html=True
    )

    st.write("")
    csv_out = df_campus[['Campus', 'SundayDate', 'Service', 'service_attendance', 'AdultCapacity']].copy()
    csv_out['SundayDate'] = csv_out['SundayDate'].dt.strftime('%m-%d-%Y')
    st.download_button(
        f"Download {campus_name} (CSV)",
        csv_out.to_csv(index=False),
        f"{campus_name.replace(' ', '_')}_Projections.csv",
        "text/csv"
    )


# ── Page ─────────────────────────────────────────────────────────────────
st.subheader("Weekly Service Projections")

# Dropdowns
d1, d2 = st.columns(2)

with d1:
    dates_sorted = sorted(df_all['SundayDate'].unique())
    date_labels = [d.strftime('%m-%d-%Y') for d in pd.to_datetime(dates_sorted)]
    date_sel = st.selectbox("Select Sunday Date", date_labels)

sel_date = pd.to_datetime(date_sel, format='%m-%d-%Y')
df_date = df_all[df_all['SundayDate'] == sel_date].copy()

with d2:
    campus_list = sorted(df_date['Campus'].unique().tolist())
    campus_sel = st.selectbox("Select Campus", ["—"] + campus_list,
                              help="Choose a campus to view service breakdown")

st.write("")
st.write("")

# Grand total
df_totals = df_date.groupby('Campus').agg(
    Projected=('service_attendance', 'sum'),
    Services=('Service', 'count')
).reset_index().sort_values('Campus')

grand_total = int(df_totals['Projected'].sum())
st.metric("All Campuses — Projected Attendance", f"{grand_total:,}")

st.divider()

# Campus summary cards
for _, row in df_totals.iterrows():
    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;'
        f'background:#fff;border:1px solid #e0e4ea;border-radius:10px;padding:12px 16px;margin-bottom:8px;'
        f'box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
        f'<div style="font-weight:700;font-size:1rem;color:#2c3e50;min-width:140px;">{row["Campus"]}</div>'
        f'<div style="display:flex;gap:20px;flex-wrap:wrap;align-items:center;">'
        f'<div style="text-align:center;"><div style="font-size:0.65rem;color:#aaa;text-transform:uppercase;letter-spacing:0.05em;">Projected</div>'
        f'<div style="font-weight:800;font-size:1.1rem;color:#C0392B;">{int(row["Projected"]):,}</div></div>'
        f'<div style="text-align:center;"><div style="font-size:0.65rem;color:#aaa;text-transform:uppercase;letter-spacing:0.05em;">Services</div>'
        f'<div style="font-weight:700;">{int(row["Services"])}</div></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

st.divider()

# Download all
csv_all = df_date[['Campus', 'SundayDate', 'Service', 'service_attendance', 'AdultCapacity']].copy()
csv_all['SundayDate'] = csv_all['SundayDate'].dt.strftime('%m-%d-%Y')
st.download_button(
    "Download All Campuses (CSV)",
    csv_all.to_csv(index=False),
    f"All_Projections_{date_sel.replace('-', '_')}.csv",
    "text/csv"
)

# Trigger dialog when campus is selected
if campus_sel != "—":
    show_campus(campus_sel, df_date)
    
