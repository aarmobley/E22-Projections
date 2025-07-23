import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Set page config FIRST - before any other Streamlit commands
st.set_page_config(
    page_title="CoE22 Projections",
    layout="wide",  # Optional: use 'wide' or 'centered'
    initial_sidebar_state="expanded")  # 👈 THIS forces sidebar to stay open

# Campus coefficients (your existing data structure)
campus_coefficients = {
    'San Pablo': {
        '7:22': {
            'intercept': -128.6394,
            'sunday_date': 0.0087,
            'week_number': -0.067,
            'Guest Pastor': -1.856,
            'Executive Pastor': -1.1375,
            'Pastor Joby': -1.1643,
            'Easter': 8.5637,
            'Promotion Week': 1.52663,
            'Back to School': 1.8641,
            'Saturated Sunday': 13.8692,
            'kids_projection': .08,
            'kids_easter': .08,
            'Christmas': 6.2412
        },
        '9:00': {
            'intercept': -179.262118,
            'sunday_date': 0.011448, 
            'week_number': -0.006540,
            'Guest Pastor': -1.275874,
            'Executive Pastor': -0.510051,
            'Pastor Joby': 1.122999,
            'Easter': 14.028790,
            'Promotion Week': 0.332188,
            'Back to School': 1.276608,
            'Saturated Sunday': 7.142149,
            'kids_projection': 0.20,
            'kids_easter': .12,
            'Christmas': 4.326568
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
            'intercept': -1489.2378,
            'sunday_date': 0.0961,
            'week_number': -1.3899,
            'Saturated Sunday': 125.3024,
            'Easter': 86.2632,
            'Promotion Week': 61.8972,
            'kids_projection': .32,
            'kids_easter': .27,
            'Christmas': 85.7072
        },
        '11:22': {
            'intercept': 1066.1896,
            'sunday_date': -0.0362,
            'week_number': -1.0235,
            'Saturated Sunday': 280.5179,
            'Easter': 80.8687,
            'Promotion Week': 92.1327,
            'Back to School': 92.1327,
            'kids_projection': .23,
            'kids_easter': .29,
            'Christmas': 38.8151
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
            'intercept' : -6.321507,
            'sunday_date' :0.001285, 
            'week_number' : -0.012768,
            'Easter' : 5.188487,
       	    'Promotion Week' : 1.4468,
            'Back to School' : 1.443064,
            'Saturated Sunday' : 1.851372,
            'kids_projection' : 0.22,
            'kids_easter' : .12,
            'Christmas' : 2.685164,
            'Inclement Weather' : .15
        },
        '11:22': {
            'intercept' : 36.036786,
       	    'sunday_date' : -0.001003,
            'week_number' : -0.013473,
            'Easter' : 6.922727,
            'Promotion Week' : 1.979547,
            'Back to School' : 1.952,
            'Saturated Sunday' : 3.556182,
            'kids_projection' : .15,
            'kids_easter' : .12,
            'kids_labor' : 17.64,
            'Christmas' : 4.411963,
            'Inclement Weather' : .15
        }
    },
    'St. Johns': {
        '09:00': {
            'intercept': -7313.2975,
            'sunday_date': 0.4043,
            'week_number': -0.4042,
            'Guest Pastor': -34.2460,
            'Executive Pastor': -17.9290,
            'Pastor Joby': 1.4485,
            'Easter': 384.6168,
            'BacktoSchool': 56.9989,
            'Saturated Sunday': 132.4245,
            'Christmas': 348.4167,
            'Kids Projection': .37,
            'Kids Easter': .24
        },
        '11:22': {
            'intercept': -5819.98219,
            'sunday_date': 0.32295,
            'week_number': -1.40040,
            'Guest Pastor': -15.11825,
            'Executive Pastor': -21.48908,
            'Pastor Joby': 9.44896,
            'Easter': 384.33688,
            'BacktoSchool': 128.17882,
            'Saturated Sunday': 147.10815,
            'Christmas': 285.94632,
            'Kids Projection': .29,
            'Kids Easter': .15
        },
    '7:22' : {
    'Total Attendance' : .20
}
    }
}

# Define campus capacities (you may need to adjust these based on your actual capacities)
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

### Logo and title
logo_file = "https://raw.githubusercontent.com/aarmobley/CoE22/main/E22%20Logo.png"
st.image(logo_file, width=150)

##### Sidebar
with st.sidebar:
    st.markdown("""
                Important Dates: 
                - 08-10-2025 (Promotion Week)  
                - 09-14-2025 (Saturated Sunday)
                - 12-24-2025 (Christmas)
                - 01-04-2026 (Back to School)
                - 04-05-2026 (Easter) 
                
                *Choose Inclement Weather if the weather will affect attendance""")


# Create week numbers
num_week = [week for _ in range(3) for week in range(1, 53)]
if len(num_week) < 156:
    num_week.append(53)

# Create dates for 2 year projection
start_date = datetime(2025, 1, 5)
date_range = [start_date + timedelta(weeks=i) for i in range(156)]

# Create date mapping with numerical values
epoch = datetime(1970, 1, 1)
date_mapping = {date.strftime('%m-%d-%Y'): (date - epoch).days for date in date_range}

# Create date and week options
date_week_options = [f"{date.strftime('%m-%d-%Y')} (Week {week})" for date, week in zip(date_range, num_week)]

# Select box for sunday date and week number
date_options = st.selectbox("Select Sunday Date", date_week_options)

selected_date_str = date_options.split(' ')[0]
select_week = int(date_options.split('Week ')[-1].strip(')'))

# List pastors and events
pastor_options = ['Pastor Joby', 'Guest Pastor', 'Executive Pastor']
event_options = ['None', 'Easter', 'Promotion Week', 'Saturated Sunday', 'Christmas', 'Back to School', 'Inclement Weather']

# Select boxes
select_pastor = st.selectbox("Select a Pastor", pastor_options)
select_event = st.selectbox("Select Event", event_options)

####adding drop down for Saturated
st.divider()
st.subheader("📊 Saturated 2025 Projections")
saturated_option = st.selectbox("Saturated", ['Wednesday', 'Thursday', 'Friday', 'Saturday'])





saturated_option = st.selectbox("Saturated", ['Wednesday', 'Thursday', 'Friday', 'Saturday'])

df_saturated = None

if saturated_option == 'Wednesday':
    github_excel_url = "https://github.com/aarmobley/E22-Projections/raw/main/SaturatedWednesday2025.xlsx"
    try:
        df_saturated = pd.read_excel(github_excel_url, engine="openpyxl")
        st.success("Successfully loaded Saturated Wednesday file.")
        st.dataframe(df_saturated)
    except Exception as e:
        st.error(f"Could not load Saturated Wednesday file: {e}")
        
if saturated_option == 'Thursday':
    github_excel_url = "https://github.com/aarmobley/E22-Projections/raw/main/SaturatedThursday2025.xlsx"
    try:
        df_saturated = pd.read_excel(github_excel_url, engine="openpyxl")
        st.success("Successfully loaded Saturated Wednesday file.")
        st.dataframe(df_saturated)
    except Exception as e:
        st.error(f"Could not load Saturated Wednesday file: {e}")

if saturated_option == 'Friday':
    github_excel_url = "https://github.com/aarmobley/E22-Projections/raw/main/SaturatedWednesday2025.xlsx"
    try:
        df_saturated = pd.read_excel(github_excel_url, engine="openpyxl")
        st.success("Successfully loaded Saturated Wednesday file.")
        st.dataframe(df_saturated)
    except Exception as e:
        st.error(f"Could not load Saturated Wednesday file: {e}")

# --------------------- SATURATED DOWNLOAD BUTTON --------------------- #
if df_saturated is not None:
    st.markdown("### 📥 Export Saturated Projections")
    saturated_csv = df_saturated.to_csv(index=False)

    st.download_button(
        label="📤 Download Saturated Projections as CSV",
        data=saturated_csv,
        file_name=f"Saturated_{saturated_option}_Projections.csv",
        mime="text/csv"



# Function to calculate attendance for a service
def calculate_attendance(campus, service_time, coefficients, numerical_date, week_num, pastor, event):
    """Calculate attendance for a specific campus and service time"""
    service_options = coefficients
    
    # Calculate effects
    weeknum_effect = service_options.get('week_number', 0) * week_num
    sundaydate_effect = service_options.get('sunday_date', 0) * numerical_date
    
    # Determine pastor or event effect
    pastor_effect = 0
    event_effect = 0
    
    if event != 'None':
        # Handle different event naming conventions
        event_keys = [event, event.replace(' ', ''), event.replace(' ', 'to'), event.replace(' ', '_')]
        for key in event_keys:
            if key in service_options:
                event_effect = service_options[key]
                break
    else:
        pastor_effect = service_options.get(pastor, 0)
    
       # Calculate base prediction
    intercept = service_options.get('intercept', 0)
    prediction = intercept + sundaydate_effect + weeknum_effect + pastor_effect + event_effect
    
    #Make correct transformation based on Campus --- St. Johns and North Jax do not need to be squared
    if campus in ['St. Johns', 'North Jax']:
        adult_attendance = prediction
    else:
        adult_attendance = prediction ** 2
    
    # Handle inclement weather
    if event == 'Inclement Weather':
        weather_reduction = service_options.get('Inclement Weather', 0.15)
        if weather_reduction < 1:  # If it's a percentage
            adult_attendance = adult_attendance * (1 - weather_reduction)
        else:  # If it's already calculated in the coefficient
            adult_attendance = adult_attendance + weather_reduction
    
    # Calculate kids attendance
    kids_coefficient = 'kids_easter' if event == 'Easter' else 'kids_projection'
    
    # Handle different naming conventions for kids coefficients
    kids_keys = [kids_coefficient, kids_coefficient.replace('_', ' ').title(), 
                 'Kids Projection', 'Kids Easter']
    
    kids_multiplier = 0.2  # Default fallback
    for key in kids_keys:
        if key in service_options:
            kids_multiplier = service_options[key]
            break
    
    kids_attendance = adult_attendance * kids_multiplier
    
    return max(0, adult_attendance), max(0, kids_attendance)

# Function to calculate attendance for services that are based on total attendance
def calculate_total_based_attendance(campus, service_time, coefficients, other_services_adult, other_services_kids):
    """Calculate attendance for services that are based on total attendance of other services"""
    multiplier = coefficients.get('Total Attendance', 0)
    
    # Calculate adult and kids attendance as percentage of other services
    adult_attendance = other_services_adult * multiplier
    kids_attendance = other_services_kids * multiplier
    
    return max(0, adult_attendance), max(0, kids_attendance)

# Generate projections for all campuses
st.divider()

if st.button("Generate All Campus Projections"):
    numerical_date = date_mapping[selected_date_str]
    all_campus_data = []
    
    for campus_name, campus_services in campus_coefficients.items():
        campus_total_adults = 0
        campus_total_kids = 0
        
        # First pass: calculate standard services
        standard_services_adult = 0
        standard_services_kids = 0
        
        for service_time, service_coefficients in campus_services.items():
            # Skip services that are based on total attendance
            if 'Total Attendance' in service_coefficients:
                continue
                
            # Skip services that don't have intercept
            if 'intercept' not in service_coefficients:
                continue
                
            adult_attendance, kids_attendance = calculate_attendance(
                campus_name, service_time, service_coefficients, 
                numerical_date, select_week, select_pastor, select_event
            )
            
            # Get capacity information
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
        
        # Second pass: calculate services based on total attendance
        for service_time, service_coefficients in campus_services.items():
            if 'Total Attendance' not in service_coefficients:
                continue
                
            adult_attendance, kids_attendance = calculate_total_based_attendance(
                campus_name, service_time, service_coefficients, 
                standard_services_adult, standard_services_kids
            )
            
            # Get capacity information
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
        
        # Calculate campus total (including all services)
        campus_total_adults = standard_services_adult + sum(
            row['Adult_Attendance'] for row in all_campus_data 
            if row['Campus'] == campus_name and 'Total Attendance' in campus_services.get(row['Service_Time'], {})
        )
        campus_total_kids = standard_services_kids + sum(
            row['Kids_Attendance'] for row in all_campus_data 
            if row['Campus'] == campus_name and 'Total Attendance' in campus_services.get(row['Service_Time'], {})
        )
        
        # Add campus total row
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
    
    # Calculate grand totals
    grand_total_adults = sum(row['Adult_Attendance'] for row in all_campus_data 
                           if row['Service_Time'] != 'ALL' and isinstance(row['Adult_Attendance'], (int, float)))
    grand_total_kids = sum(row['Kids_Attendance'] for row in all_campus_data 
                         if row['Service_Time'] != 'ALL' and isinstance(row['Kids_Attendance'], (int, float)))
    
    # Add grand total row
    all_campus_data.append({
        'Campus': 'GRAND TOTAL - ALL CAMPUSES',
        'Service_Time': 'ALL',
        'Date': selected_date_str,
        'Week': select_week,
        'Pastor': select_pastor,
        'Event': select_event,
        'Adult_Attendance': round(grand_total_adults, 0),
        'Kids_Attendance': round(grand_total_kids, 0),
        'Adult_Capacity_Percent': 'N/A',
        'Kids_Capacity_Percent': 'N/A',
        'Adult_Capacity_Limit': 'N/A',
        'Kids_Capacity_Limit': 'N/A'
    })
    
    # Create DataFrame
    df_all_campuses = pd.DataFrame(all_campus_data)
    
    # Display summary
    #st.success(f"Projections generated for all campuses!")
    #st.write(f"**Grand Total Projected Attendance:**")
    #st.write(f"- Adults: {grand_total_adults:,.0f}")
    #st.write(f"- Kids: {grand_total_kids:,.0f}")
    #st.write(f"- Total: {grand_total_adults + grand_total_kids:,.0f}")
    
    # Show preview of data
    st.subheader("Preview of Projections")
    st.dataframe(df_all_campuses.head(25))
    
    # Create CSV with metadata
    csv_data = f"# All Campus Attendance Projections\n"
    csv_data += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    csv_data += f"# Parameters: Date={selected_date_str}, Week={select_week}, Pastor={select_pastor}, Event={select_event}\n"
    csv_data += f"# Grand Total Adults: {grand_total_adults:,.0f}\n"
    csv_data += f"# Grand Total Kids: {grand_total_kids:,.0f}\n"
    csv_data += f"# Grand Total All: {grand_total_adults + grand_total_kids:,.0f}\n\n"
    csv_data += df_all_campuses.to_csv(index=False)
    
    # Download button
    st.download_button(
        label="📥 Download All Campus Projections (CSV)",
        data=csv_data,
        file_name=f"All_Campus_Projections_{selected_date_str.replace('-', '_')}.csv",
        mime="text/csv"
    )

# Optional: Show campus list
with st.expander("View All Campuses and Service Times"):
    for campus, services in campus_coefficients.items():
        st.write(f"**{campus}:**")
        service_times = []
        for service_time, coeffs in services.items():
            if 'intercept' in coeffs:
                service_times.append(f"{service_time} (standard)")
            elif 'Total Attendance' in coeffs:
                service_times.append(f"{service_time} ({coeffs['Total Attendance']:.0%} of other services)")
        
        if service_times:
            st.write(f"  - Service Times: {', '.join(service_times)}")
        else:
            st.write(f"  - No services configured")
        st.write("")
