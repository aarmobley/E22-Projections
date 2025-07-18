##########Baymeadows PROJECTIONS 9:00 and 11:22

import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta


    

coefficients = {
    
    '9:00': {
        'intercept' : -67.30,
        'sunday_date' :  .004270, 
        'week_number' : -.001089,
        'Guest Pastor' : -.3866,
        'Executive Pastor' :  -.2336,
        'Pastor Joby' : .4164,
        'Easter' : 4.030,
       	'Promotion Week' : 1.048,
        'Saturated Sunday' : 1.437,
        'kids_projection' : 0.24, 
        'kids_easter' : .19,
        'Christmas' : -1.303112
        

    },
    
  '11:22': {

       	
        'intercept' : -43.74,
        'sunday_date' :  .003019, 
        'week_number' : -.005647,
        'Guest Pastor' : -.6090,
        'Executive Pastor' :  -.2468,
        'Pastor Joby' : .2159,
        'Easter' : 2.782,
       	'Promotion Week' : .4619,
        'Saturated Sunday' : 2.013,
        'kids_projection' : 0.21,  
        'kids_easter' : .19,
        'Christmas' : -1.018843
    },
    

 '7:22': {
        'Total Attendance' : .16
 }
}


### logo
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
                
                """)

title = st.title("Baymeadows Attendance Projection")


num_week = [week for _ in range(2) for week in range(1, 53)]
if len(num_week) < 156:
    num_week.append(53)
#momentum = ['Easter', 'Back to School-August', 'Christmas', 'Back to School-January', 'Easter 2025']


##listing service times based on coefficients
service_times = list(coefficients.keys())


##create dates for 2 year projection
start_date = datetime(2025, 1, 5)  # Start date
date_range = [start_date + timedelta(weeks=i) for i in range(156)]  # 156 weeks range

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

event_options = ['None', 'Easter', 'Promotion Week', 'Saturated Sunday', 'Christmas']


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
    
    # Special handling for 7:22:00 service
    if service_time == '7:22:00':
        # Calculate total attendance from other services first
        total_attendance = 0
        for other_service in ['09:00:00', '11:22:00']:
            other_projection = calculate_projection_base(other_service, pastor, event, numerical_date, week_number)
            total_attendance += other_projection['adult_attendance'] + other_projection['kids_attendance']
        
        # 7:22:00 attendance is 16% of total weekly attendance
        attendance_722 = total_attendance * service_options['Total Attendance']
        
        # Assume 80% adults, 20% kids for 7:22 service (you can adjust these ratios)
        adult_attendance = attendance_722 * 0.8
        kids_attendance = attendance_722 * 0.2
        
        # Calculate capacities (assuming same capacity limits)
        adult_capacity = adult_attendance / 525 * 100
        kids_capacity = kids_attendance / 247 * 100
        
        return {
            'adult_attendance': adult_attendance,
            'kids_attendance': kids_attendance,
            'adult_capacity': adult_capacity,
            'kids_capacity': kids_capacity
        }
    else:
        return calculate_projection_base(service_time, pastor, event, numerical_date, week_number)

# Base calculation function for 9:00 and 11:22 services
def calculate_projection_base(service_time, pastor, event, numerical_date, week_number):
    service_options = coefficients[service_time]
    
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
    adult_capacity = prediction_squared / 525 * 100
    kids_capacity = kids_attendance / 247 * 100
    
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

# Handle different logic for 7:22:00 service
if select_service == '7:22:00':
    # For 7:22 service, we don't need individual coefficients
    pass
else:
    weeknum_effect = service_options['week_number'] * (select_week)
    sundaydate_effect = service_options['sunday_date'] * (numerical_date)
    
    pastor = service_options[select_pastor]
    
    ### No Event coefficient needs to be 0 and pastor needs to be zero if any event is selected so it's not calcualted
    no_event = 0
    pastor = 0
    if select_event != 'None':
        no_event = service_options[select_event]
    else:
        pastor = service_options[select_pastor ]




####predict button

if st.button("Make Projection"):
    if select_service == '7:22:00':
        # Special calculation for 7:22:00 service
        # Calculate total attendance from other services
        total_weekly_attendance = 0
        for other_service in ['09:00:00', '11:22:00']:
            other_projection = calculate_projection_base(other_service, select_pastor, select_event, numerical_date, select_week)
            total_weekly_attendance += other_projection['adult_attendance'] + other_projection['kids_attendance']
        
        # 7:22:00 attendance is 16% of total weekly attendance
        attendance_722 = total_weekly_attendance * coefficients['7:22:00']['Total Attendance']
        
        # Assume 80% adults, 20% kids for 7:22 service
        prediction1 = attendance_722 * 0.8
        kids_1122 = attendance_722 * 0.2
        
        capacity = prediction1 / 525 * 100
        kids_capacity = kids_1122 / 247 * 100
        
    else:
        # Original calculation for 9:00 and 11:22 services
        prediction = ((service_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + (pastor) + no_event)
        prediction1 =  (prediction) ** (2)
        
        kids_1122 = prediction1 * service_options['kids_projection']
        
        kids_easter = prediction1 * service_options['kids_easter']
        
        #kids_labor = prediction1 * service_options['kids_labor']
        
        
        capacity = prediction1 / 525 * (100)
        
        kids_capacity = kids_1122 / 247 * (100)
        
        kids_easter_capacity = kids_easter / 247 *(100)
    
    #divider before projected attendance
    st.divider()
    
    st.write(f"Projected Adult Attendance: {prediction1:.0f}")
    
    
    ### HTML and MArkdown for adult capacity
    color = "red" if capacity > 80 else "blue"
    
    st.markdown(f"<p style='color:{color}; font-size:18px;'>Worship Center Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)                                       #st.write(f"Adult Capacity: {capacity: .0f}%")
    
    
    ###st.write(f"Weekly Total: {select_service: .0f} ")
    #####
    st.divider()
    
    
    if select_service == '7:22:00':
        # For 7:22:00 service, just show kids attendance
        st.write(f"Projected Kids Attendance: {kids_1122: .0f}")
        color = "red" if kids_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_capacity:.0f}%</p>", unsafe_allow_html=True)
    elif select_event == 'Easter':
        st.write(f"Projected Kids Attendance: {kids_easter: .0f}")
        color = "red" if kids_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_easter_capacity:.0f}%</p>", unsafe_allow_html=True)
    else: 
        st.write(f"Projected Kids Attendance: {kids_1122: .0f}")
         ## HTML and markdown for kids capacity
        color = "red" if kids_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_capacity:.0f}%</p>", unsafe_allow_html=True)


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
        file_name=f"baymeadows_projections_{selected_date_str.replace('-', '')}_{select_pastor.replace(' ', '_')}_{select_event}_{datetime.now().strftime('%H%M%S')}.csv",
        mime="text/csv"
    )
    
    st.success(f"Generated {len(df)} projection records for {selected_date_str} using current settings!")
    
    # Show preview of the data
    st.subheader("Preview of Generated Data")
    st.dataframe(df)
        
