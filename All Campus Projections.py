import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


st.set_page_config(
    page_title="CoE22 Projections",
    layout="wide",
    initial_sidebar_state="collapsed")

# Hide sidebar completely
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stSidebarCollapsedControl"] {display: none;}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <a href="https://e22projections.streamlit.app/" 
       target="_blank" 
       rel="noopener noreferrer"
       onclick="window.open(this.href, '_blank'); return false;"
       style="display: inline-block; 
              background-color: #1f77b4; 
              color: white; 
              padding: 8px 16px; 
              border-radius: 6px; 
              text-decoration: none; 
              font-size: 14px;
              font-weight: 500;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);
              cursor: pointer;">
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
st.image(logo_file, width=150)


# =====================================================================
# EASTER 2026 PROJECTIONS
# =====================================================================

st.subheader("Easter 2026 Projections - April 5, 2026")

easter_excel_url = "https://github.com/aarmobley/E22-Projections/raw/main/Updated%202026%20Easter%20Projections.xlsx"

try:
    df_easter = pd.read_excel(easter_excel_url, engine="openpyxl")

    # Clean ServiceDateTime - remove :00 seconds (5:22:00 PM → 5:22 PM)
    if 'ServiceDateTime' in df_easter.columns:
        cleaned = []
        for val in df_easter['ServiceDateTime']:
            s = str(val).strip()
            s = s.replace(':00 ', ' ').replace(':00', '')
            cleaned.append(s)
        df_easter['ServiceDateTime'] = cleaned

    # Filter dropdowns side by side
    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        if 'Day' not in df_easter.columns:
            st.warning("Day column not found in Excel.")
            day_filter = "All"
        else:
            day_list = df_easter['Day'].dropna().unique().tolist()
            day_sorted = sorted(day_list, key=lambda x: {'Thu': 0, 'Sat': 1, 'Sun': 2}.get(x, 3))
            day_options = ["All"] + day_sorted
            day_filter = st.selectbox("Filter by Day", day_options)

    with filter_col2:
        if 'Campus' in df_easter.columns:
            campus_list = sorted(df_easter['Campus'].dropna().unique().tolist())
            campus_options = ["All"] + campus_list
            campus_filter = st.selectbox("Filter by Campus", campus_options)
        else:
            campus_filter = "All"

    # Apply filters
    df_easter_filtered = df_easter.copy()
    if day_filter != "All":
        df_easter_filtered = df_easter_filtered[df_easter_filtered['Day'] == day_filter]
    if campus_filter != "All":
        df_easter_filtered = df_easter_filtered[df_easter_filtered['Campus'] == campus_filter]

    # Find attendance column
    att_col = None
    if 'service_attendance' in df_easter.columns:
        att_col = 'service_attendance'
    elif 'Projected' in df_easter.columns:
        att_col = 'Projected'
    else:
        numeric_cols = df_easter.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            att_col = numeric_cols[0]

    # Display metrics
    if att_col:
        filtered_total = df_easter_filtered[att_col].sum()
        num_services = len(df_easter_filtered)

        met_col1, met_col2 = st.columns(2)
        with met_col1:
            label = "Total"
            if day_filter != "All" or campus_filter != "All":
                parts = []
                if day_filter != "All":
                    parts.append(day_filter)
                if campus_filter != "All":
                    parts.append(campus_filter)
                label = "Total (" + " - ".join(parts) + ")"
            st.metric(label, f"{filtered_total:,.0f}")
        with met_col2:
            st.metric("Services Shown", num_services)

    # Display the dataframe
    st.dataframe(df_easter_filtered, use_container_width=True, hide_index=True)

    # Download button
    easter_csv = df_easter_filtered.to_csv(index=False)
    st.download_button(
        label="Download Easter Projections (CSV)",
        data=easter_csv,
        file_name="Easter_2026_Projections.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Could not load Easter projections file: {e}")
    st.info("Make sure the Excel file is uploaded to the GitHub repo.")


st.divider()


# =====================================================================
# WEEKLY PROJECTIONS
# =====================================================================

campus_coefficients = {
    'San Pablo': {
        '7:22': {
            'intercept': -142.667110,
            'sunday_date': 0.009315,
            'week_number': -0.056675,
            'Easter': 8.531395,
            'Promotion Week': 1.680988,
            'Back to School': 1.680988,
            'Saturated Sunday': 13.262508,
            'kids_projection': .08,
            'kids_easter': .08,
            'Christmas': 5.896587
        },
        '9:00': {
            'intercept': -171.987662,
            'sunday_date': 0.011074,
            'week_number': -0.008375,
            'Guest Pastor': -1.329637,
            'Executive Pastor': -0.615583,
            'Pastor Joby': 1.029747,
            'Easter': 14.137845,
            'Promotion Week': 1.400238,
            'Back to School': 1.400238,
            'Saturated Sunday': 7.225865,
            'kids_projection': 0.20,
            'kids_easter': .12,
            'Christmas': 4.600030
        },
        '11:22': {
            'intercept': -151.7846,
            'sunday_date': 0.01,
            'week_number': -0.0726,
            'Guest Pastor': -1.6713,
            'Executive Pastor': -1.4246,
            'Pastor Joby': 0.2733,
            'Easter': 14.6459,
            'Promotion Week': 3.4931,
            'Back to School': 3.4931,
            'Saturated Sunday': 6.2969,
            'kids_projection': .15,
            'kids_easter': .12,
            'kids_labor': 17.64,
            'Christmas': 9.5353,
            'Inclement Weather': .15
        },
        '4:22': {
            'Total Attendance': .06
        }
    },
    'Arlington': {
        '9:00': {
            'intercept': -38.65,
            'sunday_date': .002963,
            'week_number': .003602,
            'Guest Pastor': -.4529,
            'Executive Pastor': -.8438,
            'Pastor Joby': -.1221,
            'Easter': 6.193,
            'BacktoSchool': .08546,
            'Saturated Sunday': .9908,
            'kids_projection': 0.29,
            'kids_easter': .25
        },
        '11:22': {
            'intercept': -4.1528006,
            'sunday_date': 0.0011252,
            'week_number': -.0178361,
            'Guest Pastor': -.7539401,
            'Executive Pastor': -.3526798,
            'Pastor Joby': .1628141,
            'Easter': 5.4945168,
            'BacktoSchool': -.9172174,
            'Saturated Sunday': 1.6824265,
            'kids_projection': .30,
            'kids_easter': .25
        },
        '7:22': {
            'Total Attendance': .16
        }
    },
    'Baymeadows': {
        '9:00': {
            'intercept': -67.30,
            'sunday_date': .004270,
            'week_number': -.001089,
            'Guest Pastor': -.3866,
            'Executive Pastor': -.2336,
            'Pastor Joby': .4164,
            'Easter': 4.030,
            'Promotion Week': 1.048,
            'Saturated Sunday': 1.437,
            'kids_projection': 0.24,
            'kids_easter': .19,
            'Christmas': -1.303112
        },
        '11:22': {
            'intercept': -43.74,
            'sunday_date': .003019,
            'week_number': -.005647,
            'Guest Pastor': -.6090,
            'Executive Pastor': -.2468,
            'Pastor Joby': .2159,
            'Easter': 2.782,
            'Promotion Week': .4619,
            'Saturated Sunday': 2.013,
            'kids_projection': 0.21,
            'kids_easter': .19,
            'Christmas': -1.018843
        },
        '7:22': {
            'Total Attendance': .16
        }
    },
    'Fleming Island': {
        '7:22': {
            'intercept': -56.532818,
            'sunday_date': 0.003535,
            'week_number': -0.017519,
            'Guest Pastor': -0.132035,
            'Executive Pastor': -0.818452,
            'Pastor Joby': -0.266790,
            'Easter': 5.701672,
            'Promotion Week': 1.144970,
            'Back To School': 1.144970,
            'Saturated Sunday': 8.582320,
            'kids_projection': .15,
            'kids_easter': .13,
            'Christmas': 6.746094
        },
        '9:00': {
            'intercept': -59.344,
            'sunday_date': 0.0041,
            'week_number': -0.0079,
            'Guest Pastor': -0.0018,
            'Executive Pastor': -0.4856,
            'Pastor Joby': 0.4656,
            'Easter': 7.6926,
            'Promotion Week': 1.2294,
            'Back To School': 1.2294,
            'Saturated Sunday': 2.1657,
            'kids_projection': 0.27,
            'kids_easter': .20,
            'Christmas': 2.5449
        },
        '11:22': {
            'intercept': -52.0234,
            'sunday_date': 0.0038,
            'week_number': -0.0316,
            'Guest Pastor': -0.5974,
            'Executive Pastor': -0.5027,
            'Pastor Joby': -0.0229,
            'Easter': 6.1344,
            'Promotion Week': 1.8042,
            'Back To School': 1.8042,
            'Saturated Sunday': 3.6719,
            'kids_projection': 0.27,
            'kids_easter': .21,
            'Christmas': 4.6251
        },
    },
    'Jesup': {
        '9:00': {
            'intercept': -73.607412,
            'sunday_date': 0.004340,
            'week_number': 0.014782,
            'Easter': 3.489182,
            'Promotion Week': 1.612629,
            'Back to School': 1.612629,
            'Saturated Sunday': 1.115047,
            'kids_projection': 0.29,
            'kids_easter': .25,
            'Christmas': 3.982514
        },
        '11:22': {
            'intercept': -23.31375,
            'sunday_date': 0.00167,
            'week_number': -0.02805,
            'Easter': 2.24195,
            'Promotion Week': 1.30396,
            'Back to School': 1.30396,
            'Saturated Sunday': 2.74741,
            'kids_projection': .33,
            'kids_easter': .33,
            'Christmas': 1.44838
        },
    },
    'Mandarin': {
        '9:00': {
            'intercept': -50.25,
            'sunday_date': .003850,
            'week_number': -.000900,
            'Guest Pastor': -.3200,
            'Executive Pastor': -.2100,
            'Pastor Joby': .3800,
            'Easter': 3.500,
            'Promotion Week': .900,
            'Saturated Sunday': 1.200,
            'kids_projection': 0.22,
            'kids_easter': .18,
            'Christmas': -1.100
        },
        '11:22': {
            'intercept': -35.60,
            'sunday_date': .002800,
            'week_number': -.004500,
            'Guest Pastor': -.5500,
            'Executive Pastor': -.2200,
            'Pastor Joby': .1900,
            'Easter': 2.400,
            'Promotion Week': .4000,
            'Saturated Sunday': 1.800,
            'kids_projection': 0.20,
            'kids_easter': .17,
            'Christmas': -.900
        }
    },
    'North Jax': {
        '9:00': {
            'intercept': -1717.7378,
            'sunday_date': 0.1062,
            'week_number': -0.6172,
            'Saturated Sunday': 156.4363,
            'Easter': 125.3663,
            'Promotion Week': 22.1525,
            'kids_projection': .32,
            'kids_easter': .27,
            'Christmas': 71.7278
        },
        '11:22': {
            'intercept': -85.5483,
            'sunday_date': 0.0206,
            'week_number': -0.2566,
            'Saturated Sunday': 248.2769,
            'Easter': 179.4513,
            'Promotion Week': 92.1327,
            'Back to School': 51.4164,
            'kids_projection': .23,
            'kids_easter': .29,
            'Christmas': 20.1802
        },
        '7:22': {
            'Total Attendance': .23
        }
    },
    'Orange Park': {
        '9:00': {
            'intercept': -45.317708,
            'sunday_date': 0.003027,
            'week_number': 0.000409,
            'Guest Pastor': 0.105776,
            'Executive Pastor': -0.054834,
            'Pastor Joby': 0.545095,
            'Easter': 5.713542,
            'BacktoSchool': 1.382218,
            'Saturated Sunday': 1.507777,
            'Christmas': 1.679073,
            'Kids Projection': .27,
            'Kids Easter': .19
        },
        '11:22': {
            'intercept': -44.235901,
            'sunday_date': 0.003001,
            'week_number': -0.026953,
            'Guest Pastor': -0.758658,
            'Executive Pastor': -0.305494,
            'Pastor Joby': -0.325970,
            'Easter': 6.184421,
            'BacktoSchool': 1.411250,
            'Saturated Sunday': 1.431013,
            'Christmas': 3.997914,
            'Kids Projection': .33,
            'Kids Easter': .23
        },
    },
    'Ponte Vedra': {
        '9:00': {
            'intercept': -6.321507,
            'sunday_date': 0.001285,
            'week_number': -0.012768,
            'Easter': 5.188487,
            'Promotion Week': 1.4468,
            'Back to School': 1.443064,
            'Saturated Sunday': 1.851372,
            'kids_projection': 0.22,
            'kids_easter': .12,
            'Christmas': 2.685164,
            'Inclement Weather': .15
        },
        '11:22': {
            'intercept': 36.036786,
            'sunday_date': -0.001003,
            'week_number': -0.013473,
            'Easter': 6.922727,
            'Promotion Week': 1.979547,
            'Back to School': 1.952,
            'Saturated Sunday': 3.556182,
            'kids_projection': .15,
            'kids_easter': .12,
            'kids_labor': 17.64,
            'Christmas': 4.411963,
            'Inclement Weather': .15
        }
    },
    'St. Johns': {
        '9:00': {
            'intercept': -7376.0256,
            'sunday_date': 0.4081,
            'week_number': -0.7781,
            'Guest Pastor': -25.0405,
            'Executive Pastor': -10.8755,
            'Pastor Joby': -12.5410,
            'Easter': 368.6713,
            'BacktoSchool': 99.6941,
            'Saturated Sunday': 144.4888,
            'Christmas': 267.1487,
            'Kids Projection': .35,
            'Kids Easter': .24,
            'New Building': 674.2372
        },
        '11:22': {
            'intercept': -5681.6164,
            'sunday_date': 0.3158,
            'week_number': -1.4148,
            'Guest Pastor': -13.0240,
            'Executive Pastor': 0.1442,
            'Pastor Joby': 2.1450,
            'Easter': 373.0117,
            'BacktoSchool': 129.6823,
            'Saturated Sunday': 156.1531,
            'Christmas': 285.94632,
            'Kids Projection': .25,
            'Kids Easter': .15,
            'New Building': 492.5563
        },
        '7:22': {
            'Total Attendance': .20
        }
    }
}

campus_capacities = {
    'San Pablo': {'adult': 3001, 'kids': 750},
    'Arlington': {'adult': 850, 'kids': 225},
    'Baymeadows': {'adult': 525, 'kids': 247},
    'Fleming Island': {'adult': 766, 'kids': 250},
    'Jesup': {'adult': 290, 'kids': 105},
    'Mandarin': {'adult': 840, 'kids': 330},
    'North Jax': {'adult': 700, 'kids': 350},
    'Orange Park': {'adult': 700, 'kids': 262},
    'Ponte Vedra': {'adult': 545, 'kids': 210},
    'St. Johns': {'adult': 1948, 'kids': 559}
}


# Important Dates: 
# - 08-10-2025 (Promotion Week)  
# - 09-14-2025 (Saturated Sunday)
# - 12-24-2025 (Christmas)
# - 01-04-2026 (Back to School)
# - 04-05-2026 (Easter)


num_week = [week for _ in range(3) for week in range(1, 53)]
if len(num_week) < 156:
    num_week.append(53)

start_date = datetime(2025, 1, 5)
date_range = [start_date + timedelta(weeks=i) for i in range(156)]

epoch = datetime(1970, 1, 1)
date_mapping = {date.strftime('%m-%d-%Y'): (date - epoch).days for date in date_range}

date_week_options = [f"{date.strftime('%m-%d-%Y')} (Week {week})" for date, week in zip(date_range, num_week)]

date_options = st.selectbox("Select Sunday Date", date_week_options)

selected_date_str = date_options.split(' ')[0]
select_week = int(date_options.split('Week ')[-1].strip(')'))

pastor_options = ['Pastor Joby', 'Guest Pastor', 'Executive Pastor']
event_options = ['None', 'Easter', 'Promotion Week', 'Saturated Sunday', 'Christmas', 'Back to School', 'Inclement Weather']

select_pastor = st.selectbox("Select a Pastor", pastor_options)
select_event = st.selectbox("Select Event", event_options)


def calculate_attendance(campus, service_time, coefficients, numerical_date, week_num, pastor, event):
    service_options = coefficients

    weeknum_effect = service_options.get('week_number', 0) * week_num
    sundaydate_effect = service_options.get('sunday_date', 0) * numerical_date

    pastor_effect = 0
    event_effect = 0

    if event != 'None':
        event_keys = [event, event.replace(' ', ''), event.replace(' ', 'to'), event.replace(' ', '_')]
        for key in event_keys:
            if key in service_options:
                event_effect = service_options[key]
                break
    else:
        pastor_effect = service_options.get(pastor, 0)

    new_building_effect = 0
    if campus == 'St. Johns':
        new_building_effect = service_options.get('New Building', 0)

    intercept = service_options.get('intercept', 0)
    prediction = intercept + sundaydate_effect + weeknum_effect + pastor_effect + event_effect + new_building_effect

    if campus in ['St. Johns', 'North Jax']:
        adult_attendance = prediction
    else:
        adult_attendance = prediction ** 2

    if event == 'Inclement Weather':
        weather_reduction = service_options.get('Inclement Weather', 0.15)
        if weather_reduction < 1:
            adult_attendance = adult_attendance * (1 - weather_reduction)
        else:
            adult_attendance = adult_attendance + weather_reduction

    kids_coefficient = 'kids_easter' if event == 'Easter' else 'kids_projection'
    kids_keys = [kids_coefficient, kids_coefficient.replace('_', ' ').title(),
                 'Kids Projection', 'Kids Easter']

    kids_multiplier = 0.2
    for key in kids_keys:
        if key in service_options:
            kids_multiplier = service_options[key]
            break

    kids_attendance = adult_attendance * kids_multiplier

    return max(0, adult_attendance), max(0, kids_attendance)


def calculate_total_based_attendance(campus, service_time, coefficients, other_services_adult, other_services_kids):
    multiplier = coefficients.get('Total Attendance', 0)
    adult_attendance = other_services_adult * multiplier
    kids_attendance = other_services_kids * multiplier
    return max(0, adult_attendance), max(0, kids_attendance)


st.divider()

if st.button("Generate All Campus Projections"):
    numerical_date = date_mapping[selected_date_str]
    all_campus_data = []

    for campus_name, campus_services in campus_coefficients.items():
        campus_total_adults = 0
        campus_total_kids = 0

        standard_services_adult = 0
        standard_services_kids = 0

        for service_time, service_coefficients in campus_services.items():
            if 'Total Attendance' in service_coefficients:
                continue
            if 'intercept' not in service_coefficients:
                continue

            adult_attendance, kids_attendance = calculate_attendance(
                campus_name, service_time, service_coefficients,
                numerical_date, select_week, select_pastor, select_event
            )

            capacity_info = campus_capacities.get(campus_name, {'adult': 1000, 'kids': 250})
            adult_capacity_pct = (adult_attendance / capacity_info['adult']) * 100
            kids_capacity_pct = (kids_attendance / capacity_info['kids']) * 100

            standard_services_adult += adult_attendance
            standard_services_kids += kids_attendance

            all_campus_data.append({
                'Campus': campus_name,
                'Service_Time': service_time,
                'Date': selected_date_str,
                'Week': select_week,
                'Pastor': select_pastor,
                'Event': select_event,
                'Adult_Attendance': round(adult_attendance, 0),
                'Kids_Attendance': round(kids_attendance, 0),
                'Adult_Capacity_Percent': round(adult_capacity_pct, 1),
                'Kids_Capacity_Percent': round(kids_capacity_pct, 1),
                'Adult_Capacity_Limit': capacity_info['adult'],
                'Kids_Capacity_Limit': capacity_info['kids']
            })

        for service_time, service_coefficients in campus_services.items():
            if 'Total Attendance' not in service_coefficients:
                continue

            adult_attendance, kids_attendance = calculate_total_based_attendance(
                campus_name, service_time, service_coefficients,
                standard_services_adult, standard_services_kids
            )

            capacity_info = campus_capacities.get(campus_name, {'adult': 1000, 'kids': 250})
            adult_capacity_pct = (adult_attendance / capacity_info['adult']) * 100
            kids_capacity_pct = (kids_attendance / capacity_info['kids']) * 100

            all_campus_data.append({
                'Campus': campus_name,
                'Service_Time': service_time,
                'Date': selected_date_str,
                'Week': select_week,
                'Pastor': select_pastor,
                'Event': select_event,
                'Adult_Attendance': round(adult_attendance, 0),
                'Kids_Attendance': round(kids_attendance, 0),
                'Adult_Capacity_Percent': round(adult_capacity_pct, 1),
                'Kids_Capacity_Percent': round(kids_capacity_pct, 1),
                'Adult_Capacity_Limit': capacity_info['adult'],
                'Kids_Capacity_Limit': capacity_info['kids']
            })

        campus_total_adults = standard_services_adult + sum(
            row['Adult_Attendance'] for row in all_campus_data
            if row['Campus'] == campus_name and 'Total Attendance' in campus_services.get(row['Service_Time'], {})
        )
        campus_total_kids = standard_services_kids + sum(
            row['Kids_Attendance'] for row in all_campus_data
            if row['Campus'] == campus_name and 'Total Attendance' in campus_services.get(row['Service_Time'], {})
        )

        all_campus_data.append({
            'Campus': f"{campus_name} - TOTAL",
            'Service_Time': 'ALL',
            'Date': selected_date_str,
            'Week': select_week,
            'Pastor': select_pastor,
            'Event': select_event,
            'Adult_Attendance': round(campus_total_adults, 0),
            'Kids_Attendance': round(campus_total_kids, 0),
            'Adult_Capacity_Percent': 'N/A',
            'Kids_Capacity_Percent': 'N/A',
            'Adult_Capacity_Limit': 'N/A',
            'Kids_Capacity_Limit': 'N/A'
        })

    df_all_campuses = pd.DataFrame(all_campus_data)

    st.subheader("Preview of Projections")
    st.dataframe(df_all_campuses.head(40))

    csv_data = f"# All Campus Attendance Projections\n"
    csv_data += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    csv_data += f"# Parameters: Date={selected_date_str}, Week={select_week}, Pastor={select_pastor}, Event={select_event}\n\n"
    csv_data += df_all_campuses.to_csv(index=False)

    st.download_button(
        label="Download All Campus Projections (CSV)",
        data=csv_data,
        file_name=f"All_Campus_Projections_{selected_date_str.replace('-', '_')}.csv",
        mime="text/csv"
    )
