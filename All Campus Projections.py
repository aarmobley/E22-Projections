import re
import io
import datetime as dt

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Config / constants
# ---------------------------------------------------------------------------

PROJECTIONS_URL = "https://raw.githubusercontent.com/aarmobley/E22-Projections/main/Service_Projections.csv"
KIDS_URL = "https://raw.githubusercontent.com/aarmobley/E22-Projections/main/Kids%20to%20Adults%20%25.csv"
LOGO_URL = "https://raw.githubusercontent.com/aarmobley/CoE22/main/E22%20Logo.png"

DEFAULT_KIDS_RATIO = 0.20

# (Campus, ServiceDateTime as zero-padded HH:MM:SS) pairs to drop entirely.
BAD_SERVICES = {
    ("Arlington", "07:22:00"),
    ("Baymeadows", "07:22:00"),
    ("Wildlight", "07:22:00"),
}

st.set_page_config(
    page_title="E22 Weekly Service Projections",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Global CSS — hide sidebar, dialog sizing, dark-mode text colors, pills, banner
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* Hide the sidebar entirely */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}

    /* Dialog sizing: desktop min/max width, mobile near-full-width */
    div[data-testid="stDialog"] > div {
        min-width: 750px;
        max-width: 950px;
    }
    @media (max-width: 640px) {
        div[data-testid="stDialog"] > div {
            min-width: unset !important;
            max-width: 96vw !important;
            width: 96vw !important;
        }
    }

    /* Dark-mode friendly text inside the campus wizard dialog */
    .campus-title {
        color: #f1f3f4;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .campus-hint {
        color: #b8bcc0;
        font-size: 0.85rem;
        margin-bottom: 0.75rem;
    }
    .e22-table {
        width: 100%;
        border-collapse: collapse;
    }
    .e22-table th {
        color: #c8ccd0;
        text-align: left;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        border-bottom: 1px solid rgba(255,255,255,0.15);
        padding: 6px 10px;
    }
    .e22-table td {
        color: #e8eaed;
        padding: 6px 10px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .e22-table td.secondary {
        color: #c8ccd0;
    }

    /* Utilization pills */
    .pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .pill-red    { background: rgba(220, 53, 69, 0.18); color: #ff6b6b; }
    .pill-amber  { background: rgba(255, 193, 7, 0.18); color: #ffc94d; }
    .pill-green  { background: rgba(40, 167, 69, 0.18); color: #52c97c; }

    /* Notification banner */
    .e22-banner {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(220, 53, 69, 0.12);
        border: 1px solid rgba(220, 53, 69, 0.35);
        color: #ff8a8a;
        border-radius: 999px;
        padding: 6px 16px;
        font-size: 0.85rem;
        width: fit-content;
        margin: 0 auto 1.25rem auto;
    }

    .e22-header-wrap {
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .e22-header-wrap img {
        width: 150px;
        max-width: 60%;
        margin-bottom: 0.5rem;
    }
    .e22-header-wrap h1 {
        font-size: 1.6rem;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pad_time(value: str) -> str:
    """Zero-pad a HH:MM:SS (or H:MM:SS) time string.

    write.csv on the R side can drop a leading zero (e.g. '7:22:00'
    instead of '07:22:00'). This is the durable, app-side fix — do not
    remove even if the R pipeline appears to have stopped stripping it.
    """
    if pd.isna(value):
        return value
    value = str(value).strip()
    return re.sub(r"^(\d):", r"0\1:", value)


def to_12hr(padded_time: str) -> str:
    """Convert a zero-padded HH:MM:SS string to a human readable 12hr label."""
    if pd.isna(padded_time):
        return ""
    try:
        parsed = dt.datetime.strptime(str(padded_time)[:8], "%H:%M:%S")
    except ValueError:
        return str(padded_time)
    label = parsed.strftime("%I:%M %p").lstrip("0")
    return label


def parse_pct(value) -> float:
    """Parse a 'Kids to Adults %' style value into a 0-1 float. Falls back to NaN
    (caller decides the fallback ratio) on anything unparsable."""
    if pd.isna(value):
        return float("nan")
    s = str(value).strip().replace("%", "")
    try:
        num = float(s)
    except ValueError:
        return float("nan")
    # Values like 20 -> 0.20, values already like 0.20 stay as-is.
    return num / 100.0 if num > 1 else num


def utilization_pill(pct: float) -> str:
    if pct > 100:
        cls = "pill-red"
    elif pct > 80:
        cls = "pill-amber"
    else:
        cls = "pill-green"
    return f'<span class="pill {cls}">{pct:.0f}%</span>'


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def load_projections() -> pd.DataFrame:
    df = pd.read_csv(PROJECTIONS_URL)

    # 1. Zero-pad ServiceDateTime immediately after read. This is the
    #    essential, durable fix for the R-side time zero-stripping issue.
    df["ServiceDateTime"] = df["ServiceDateTime"].apply(pad_time)

    # 2. Tolerate a Quarter column (or its absence) — don't assume a fixed
    #    column set. We simply don't drop or require it.
    #    (No action needed beyond not hardcoding expected columns elsewhere.)

    # 3. Keep the AdultCapacity dedupe guard. This is redundant now that
    #    duplicates are resolved at the source, but it's safe to keep as
    #    a safeguard against future regressions (e.g. St. Johns 2200/2028,
    #    Orange Park 750/514).
    dedupe_keys = [c for c in ["CampusId", "Campus", "ServiceDateTime"] if c in df.columns]
    if dedupe_keys and "AdultCapacity" in df.columns:
        df = (
            df.sort_values("AdultCapacity", ascending=False)
            .drop_duplicates(subset=dedupe_keys, keep="first")
            .reset_index(drop=True)
        )

    # 4. Human-readable Service column.
    df["Service"] = df["ServiceDateTime"].apply(to_12hr)

    # 5. Kids ratios: load, clean, extract ServiceTime, parse ratio, build
    #    campus-level fallback, and merge onto the projections.
    kids_df = pd.read_csv(KIDS_URL)
    kids_df.columns = [str(c).strip() for c in kids_df.columns]

    # Find the column holding the percentage figure.
    pct_col = next(
        (c for c in kids_df.columns if "kids" in c.lower() and "adult" in c.lower()),
        None,
    )
    if pct_col is None:
        # fall back to any column with a % sign in a sample value
        pct_col = next(
            (c for c in kids_df.columns if kids_df[c].astype(str).str.contains("%").any()),
            None,
        )

    # Find (or build) the column holding a HH:MM:SS service time, via regex
    # extraction — the raw column may embed the time inside a longer string
    # (e.g. "Baymeadows - 07:22:00").
    time_source_col = None
    for c in kids_df.columns:
        sample = kids_df[c].astype(str)
        if sample.str.contains(r"\d{2}:\d{2}:\d{2}").any():
            time_source_col = c
            break

    if time_source_col is not None:
        kids_df["ServiceTime"] = kids_df[time_source_col].astype(str).str.extract(
            r"(\d{2}:\d{2}:\d{2})"
        )
    elif "ServiceDateTime" in kids_df.columns:
        kids_df["ServiceTime"] = kids_df["ServiceDateTime"].apply(pad_time)
    else:
        kids_df["ServiceTime"] = pd.NA

    campus_col = next((c for c in kids_df.columns if c.lower() == "campus"), None)

    if pct_col is not None:
        kids_df["KidsRatio"] = kids_df[pct_col].apply(parse_pct)
    else:
        kids_df["KidsRatio"] = float("nan")

    # Campus-level mean fallback for rows where the specific service ratio
    # is missing / unparsable.
    if campus_col is not None:
        campus_means = kids_df.groupby(campus_col)["KidsRatio"].mean()
        kids_df["KidsRatio"] = kids_df.apply(
            lambda r: r["KidsRatio"]
            if pd.notna(r["KidsRatio"])
            else campus_means.get(r[campus_col], float("nan")),
            axis=1,
        )

    kids_df["KidsRatio"] = kids_df["KidsRatio"].fillna(DEFAULT_KIDS_RATIO)

    merge_cols = ["KidsRatio"]
    left_on = []
    right_on = []
    if campus_col is not None and "Campus" in df.columns:
        left_on.append("Campus")
        right_on.append(campus_col)
    if "ServiceTime" in kids_df.columns:
        kids_df["ServiceTime"] = kids_df["ServiceTime"].apply(pad_time)
        left_on.append("ServiceDateTime")
        right_on.append("ServiceTime")

    if left_on:
        kids_small = kids_df[right_on + merge_cols].drop_duplicates()
        df = df.merge(
            kids_small,
            left_on=left_on,
            right_on=right_on,
            how="left",
        )
    if "KidsRatio" not in df.columns:
        df["KidsRatio"] = DEFAULT_KIDS_RATIO
    df["KidsRatio"] = df["KidsRatio"].fillna(DEFAULT_KIDS_RATIO)

    # 6. Kids / total attendance.
    df["kids_attendance"] = (df["service_attendance"] * df["KidsRatio"]).round().astype(int)
    df["total_attendance"] = df["service_attendance"] + df["kids_attendance"]

    # 7. Drop known bad service rows.
    if "Campus" in df.columns:
        mask = df.apply(
            lambda r: (r["Campus"], r["ServiceDateTime"]) in BAD_SERVICES, axis=1
        )
        df = df[~mask].reset_index(drop=True)

    return df


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div class="e22-header-wrap">
        <img src="{LOGO_URL}" alt="Church of Eleven22 logo" />
        <h1>Weekly Service Projections</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="e22-banner">
        🔔 Projections update weekly — data reflects the latest model run.
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    data = load_projections()
except Exception as e:
    st.error(f"Couldn't load projections data: {e}")
    st.stop()

if "picker_open" not in st.session_state:
    st.session_state.picker_open = False
if "picker_campus" not in st.session_state:
    st.session_state.picker_campus = None

campuses = sorted(data["Campus"].dropna().unique().tolist()) if "Campus" in data.columns else []


def open_picker():
    st.session_state.picker_open = True
    st.session_state.picker_campus = None


def select_campus(campus_name):
    st.session_state.picker_campus = campus_name


def back_to_all():
    st.session_state.picker_campus = None


@st.dialog("Campus Projections", width="large")
def campus_wizard():
    if st.session_state.picker_campus is None:
        st.markdown('<div class="campus-title">All Campuses</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="campus-hint">Select a campus to see its service breakdown.</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        for i, campus in enumerate(campuses):
            with cols[i % 2]:
                if st.button(campus, key=f"campus_btn_{campus}", use_container_width=True):
                    select_campus(campus)
                    st.rerun()
    else:
        campus = st.session_state.picker_campus
        if st.button("← All campuses", key="back_btn"):
            back_to_all()
            st.rerun()

        st.markdown(f'<div class="campus-title">{campus}</div>', unsafe_allow_html=True)

        campus_df = data[data["Campus"] == campus].copy()
        if "SundayDate" in campus_df.columns:
            campus_df = campus_df.sort_values(["SundayDate", "ServiceDateTime"])

        rows_html = ""
        for _, row in campus_df.iterrows():
            capacity = row.get("AdultCapacity", None)
            svc_att = row.get("service_attendance", 0)
            util_html = ""
            if capacity and capacity > 0:
                util_pct = (svc_att / capacity) * 100
                util_html = utilization_pill(util_pct)
            rows_html += (
                "<tr>"
                f"<td>{row.get('SundayDate', '')}</td>"
                f"<td>{row.get('Service', '')}</td>"
                f"<td class='secondary'>{int(svc_att):,}</td>"
                f"<td class='secondary'>{int(row.get('kids_attendance', 0)):,}</td>"
                f"<td>{int(row.get('total_attendance', 0)):,}</td>"
                f"<td>{util_html}</td>"
                "</tr>"
            )

        table_html = f"""
        <table class="e22-table">
            <thead>
                <tr>
                    <th>Sunday</th>
                    <th>Service</th>
                    <th>Adults</th>
                    <th>Kids</th>
                    <th>Total</th>
                    <th>Utilization</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """
        st.markdown(table_html, unsafe_allow_html=True)

        st.download_button(
            f"Download {campus} CSV",
            data=campus_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{campus.replace(' ', '_')}_projections.csv",
            mime="text/csv",
            key=f"dl_{campus}",
        )


col_a, col_b = st.columns([1, 1])
with col_a:
    if st.button("View Campuses", type="primary", use_container_width=True):
        open_picker()

with col_b:
    st.download_button(
        "Export All (CSV)",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name="all_campus_projections.csv",
        mime="text/csv",
        use_container_width=True,
    )

if st.session_state.picker_open:
    campus_wizard()
