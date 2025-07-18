#### streamlit python

##########FLEMING ISLAND PROJECTIONS 9:00 and 11:22

import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta


####coefficients for 11:22        11:22 = 3     9:00 = 4
coefficients = {
    
    '7:22': {
        'intercept' : -56.532818,
        'sunday_date' : 0.003535,
        'week_number' : -0.017519,
        'Guest Pastor' : -0.132035,
        'Executive Pastor' : -0.818452,
        'Pastor Joby' : -0.266790,
        'Easter' : 5.701672,
        'Promotion Week' : 1.144970,
        'Back To School' : 1.144970,
        'Saturated Sunday' : 8.582320,
        'kids_projection' : .15,
        'kids_easter' : .13,
        'Christmas' : 6.746094
    },
    
    
    
    '9:00': {
        'intercept' : -59.344,
        'sunday_date' : 0.0041, 
        'week_number' : -0.0079,
        'Guest Pastor' : -0.0018,
        'Executive Pastor' :  -0.4856,
        'Pastor Joby' : 0.4656,
        'Easter' : 7.6926,
        'Promotion Week' : 1.2294,
        'Back To School' : 1.2294,
        'Saturated Sunday' : 2.1657,
        'kids_projection' : 0.27,
        'kids_easter' : .20,
        'Christmas' : 2.5449
    },
    
    '11:22': {

        'intercept' : -52.0234 ,
        'sunday_date' : 0.0038,
        'week_number' : -0.0316,
        'Guest Pastor' : -0.5974,
        'Executive Pastor' : -0.5027,
        'Pastor Joby' : -0.0229,
        'Easter' : 6.1344,
        'Promotion Week' : 1.8042,
        'Back To School' : 1.8042,
        'Saturated Sunday' : 3.6719,
        'kids_projection' : 0.27,
        'kids_easter' : .21,
        'Christmas' : 4.6251
    },
    
    '4:22' : {
        'NewService' : .06
    }
}

### logo
logo_file = "https://raw.githubusercontent.com/aarmobley/CoE22/main/E22%20Logo.png"
st.image(logo_file, width=150)

##### sidebar

##### Sidebar
with st.sidebar:
    st.markdown("""
                Important Dates: 
                - 08-10-2025 (Promotion Week)  
                - 09-14-2025 (Saturated Sunday)
                - 12-24-2025 (Christmas)
                - 01-04-2026 (Back to School)
                - 04-05-2026 (Easter) 
                
                """)




title = st.title("Fleming Island Attendance Projection")

#dates = pd.read_csv(r"C:\Users\aaron\OneDrive\Desktop\python\RegressionDates1.csv")
#dates.info()
#dates.head()
#sunday_dates = dates['date'].tolist()
#num_date = dates['num_date'].tolist()
#num_week = list(range(1, 53))
num_week = [week for _ in range(3) for week in range(1, 53)]
if len(num_week) < 156:
    num_week.append(53)
#momentum = ['Easter', 'Back to School-August', 'Christmas', 'Back to School-January', 'Easter 2025']


##listing service times based on coefficients
service_times = list(coefficients.keys())


##create dates for 2 year projection
start_date = datetime(2025, 1, 5)  # Start date
date_range = [start_date + timedelta(weeks=i) for i in range(156)]  # 104 weeks range

# Create date mapping with numerical values as days since Unix epoch (1970-01-01)
epoch = datetime(1970, 1, 1)
date_mapping = {date.strftime('%m-%d-%Y'): (date - epoch).days for date in date_range}


#creating sunday date and week numbers for same drop down
date_week_options = [f"{date.strftime('%m-%d-%Y')} (Week {week})" for date, week in zip(date_range, num_week)]

#select box for sunday date and wekk number
date_options = st.selectbox("Select Sunday Date", date_week_options)                                                    #list(date_mapping.keys())


selected_date_str = date_options.split(' ')[0]
select_week = int(date_options.split('Week ')[-1].strip(')'))



#list pastors
pastor_options = ['Pastor Joby', 'Guest Pastor', 'Executive Pastor']

event_options = ['None', 'Easter', 'Promotion Week', 'Back To School', 'Saturated Sunday', 'Christmas']


####creating selectbox options
#select_date = st.selectbox("Select a Sunday Date", date_options)

#select_week = st.selectbox("Select Week Number", num_week)

select_service = st.selectbox("Select a Service", service_times)

select_pastor = st.selectbox("Select a Pastor", pastor_options)

select_event = st.selectbox("Select Event", event_options)
#select_date1 = st.selectbox("Select a Sunday Date", sunday_dates)
#select_event = st.selectbox("Select a Momentum Event", momentum)


# Function to calculate projection for a given service, pastor, and event
def calculate_projection(service_time, pastor, event, numerical_date, week_number):
    service_options = coefficients[service_time]
    
    # Special handling for 4:22 service
    if service_time == '4:22':
        # Calculate total attendance for all other services first
        total_other_services = 0
        for other_service in ['7:22', '09:00:00', '11:22:00']:
            other_options = coefficients[other_service]
            weeknum_effect = other_options['week_number'] * week_number
            sundaydate_effect = other_options['sunday_date'] * numerical_date
            
            # Handle pastor and event coefficients
            pastor_coeff = 0
            event_coeff = 0
            
            if event != 'None':
                event_coeff = other_options[event]
            else:
                pastor_coeff = other_options[pastor]
            
            prediction = ((other_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + (pastor_coeff) + event_coeff)
            prediction_squared = prediction ** 2
            total_other_services += prediction_squared
        
        # 4:22 attendance is 6% of total of other services
        adult_attendance = total_other_services * service_options['NewService']
        kids_attendance = adult_attendance * 0.15  # Using similar kids ratio as 7:22
        
        # Calculate capacities (assuming similar capacity constraints)
        adult_capacity = adult_attendance / 766 * 100
        kids_capacity = kids_attendance / 250 * 100
        
        return {
            'adult_attendance': adult_attendance,
            'kids_attendance': kids_attendance,
            'adult_capacity': adult_capacity,
            'kids_capacity': kids_capacity
        }
    
    # Original calculation for other services
    weeknum_effect = service_options['week_number'] * week_number
    sundaydate_effect = service_options['sunday_date'] * numerical_date
    
    # Handle pastor and event coefficients
    pastor_coeff = 0
    event_coeff = 0
    
    if event != 'None':
        event_coeff = service_options[event]
    else:
        pastor_coeff = service_options[pastor]
    
    prediction = ((service_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + (pastor_coeff) + event_coeff)
    prediction_squared = prediction ** 2
    
    # Calculate kids attendance
    kids_attendance = prediction_squared * service_options['kids_projection']
    if event == 'Easter':
        kids_attendance = prediction_squared * service_options['kids_easter']
    
    # Calculate capacities
    adult_capacity = prediction_squared / 766 * 100
    kids_capacity = kids_attendance / 250 * 100
    
    return {
        'adult_attendance': prediction_squared,
        'kids_attendance': kids_attendance,
        'adult_capacity': adult_capacity,
        'kids_capacity': kids_capacity
    }


#### ATTENDANCE PREDICTION

#### predict button formula
numerical_date = date_mapping[selected_date_str]                                                         #numerical_date = date_mapping[select_date]

service_options = coefficients[select_service]

# Special handling for 4:22 service in the main prediction
if select_service == '4:22':
    # Calculate total attendance for all other services first
    total_other_services = 0
    for other_service in ['7:22', '09:00:00', '11:22:00']:
        other_options = coefficients[other_service]
        weeknum_effect = other_options['week_number'] * select_week
        sundaydate_effect = other_options['sunday_date'] * numerical_date
        
        # Handle pastor and event coefficients
        pastor_coeff = 0
        event_coeff = 0
        
        if select_event != 'None':
            event_coeff = other_options[select_event]
        else:
            pastor_coeff = other_options[select_pastor]
        
        prediction = ((other_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + (pastor_coeff) + event_coeff)
        prediction_squared = prediction ** 2
        total_other_services += prediction_squared
    
    # Set variables for 4:22 service
    prediction1 = total_other_services * service_options['NewService']
    kids_1122 = prediction1 * 0.15  # Using similar kids ratio as 7:22
    kids_easter = prediction1 * 0.13  # Using similar Easter kids ratio as 7:22
    
else:
    # Original calculation for other services
    weeknum_effect = service_options['week_number'] * (select_week)
    sundaydate_effect = service_options['sunday_date'] * (numerical_date)

    pastor = service_options[select_pastor]

    ### No Event coefficient needs to be 0
    no_event = 0
    pastor = 0
    if select_event != 'None':
        no_event = service_options[select_event]
    else:
        pastor = service_options[select_pastor ]

    prediction = ((service_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + (pastor) + no_event)
    prediction1 = (prediction) ** (2)
    kids_1122 = prediction1 * service_options['kids_projection']
    kids_easter = prediction1 * service_options['kids_easter']

#event = service_options[select_event]

if st.button("Make Projection"):
    ###kids_capacity = prediction1 /
    capacity = prediction1 / 766 * (100)
    kids_capacity = kids_1122 / 250 * (100)
    kids_easter_capacity = kids_easter / 250 * (100)
    

    
    #divider before projected attendance
    st.divider()
    
    st.write(f"Projected Adult Attendance: {prediction1:.0f}")
    color = "red" if capacity >= 80 else "blue"
    st.markdown(f"<p style='color:{color}; font-size:18px;'>Worship Center Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)
    
    st.divider()
    
    if select_event == 'Easter':
        st.write(f"Projected Kids Attendance: {kids_easter: .0f}")
        color = "red" if kids_easter_capacity >= 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Kids Capacity: {kids_easter_capacity:.0f}%</p>", unsafe_allow_html=True)
    else: 
        st.write(f"Projected Kids Attendance: {kids_1122: .0f}")
        color = "red" if kids_capacity >= 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Kids Capacity: {kids_capacity:.0f}%</p>", unsafe_allow_html=True)
    
    
    
    
    
    
   
#### Kids projection
#kids1122 = prediction1 * (.26)
#if service_times == '11:22:00':
#st.write(f"Kids Projection: {kids1122: .2f}")


# Generate All Services to CSV button
st.divider()
st.subheader("Generate All Services Report")
st.write(f"Current settings: {selected_date_str}, {select_pastor}, {select_event}")

if st.button("Generate All Services to CSV"):
    # Create data for current date and settings, all service times
    all_data = []
    
    # Use only the currently selected date and settings
    for service in service_times:
        projection_data = calculate_projection(service, select_pastor, select_event, numerical_date, select_week)
        
        all_data.append({
            'Date': selected_date_str,
            'Week_Number': select_week,
            'Service_Time': service,
            'Pastor': select_pastor,
            'Event': select_event,
            'Adult_Attendance': round(projection_data['adult_attendance'], 0),
            'Kids_Attendance': round(projection_data['kids_attendance'], 0),
            'Adult_Capacity_Percent': round(projection_data['adult_capacity'], 1),
            'Kids_Capacity_Percent': round(projection_data['kids_capacity'], 1),
            'Total_Attendance': round(projection_data['adult_attendance'] + projection_data['kids_attendance'], 0)
        })
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Convert to CSV
    csv = df.to_csv(index=False)
    
    # Create download button
    st.download_button(
        label="Download CSV Report",
        data=csv,
        file_name=f"fleming_island_projections_{selected_date_str.replace('-', '')}_{select_pastor.replace(' ', '_')}_{select_event}_{datetime.now().strftime('%H%M%S')}.csv",
        mime="text/csv"
    )
    
    st.success(f"Generated {len(df)} projection records for {selected_date_str} using current settings!")
    
    # Show preview of the data
    st.subheader("Preview of Generated Data")
    st.dataframe(df)
    
    
    
    
    
   
#### Kids projection
#kids1122 = prediction1 * (.26)
#if service_times == '11:22:00':
#st.write(f"Kids Projection: {kids1122: .2f}")
    
    
