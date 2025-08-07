


import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta

coefficients = {
    

'9:00'  :   {

    'intercept' : -7376.0256,
    'sunday_date' : 0.4081,
    'week_number' : -0.7781,
    'Guest Pastor' : -25.0405,
    'Executive Pastor' : -10.8755,
    'Pastor Joby' : -12.5410,
    'Easter' : 368.6713,
    'Promotion Week' : 99.6941,
    'Saturated Sunday' : 144.4888,
    'Christmas' : 267.1487,
    'Kids Projection' : .35,
    'Kids Easter' : .24,
    'New Building' : 674.2372

},

'11:22' : {

    'intercept' : -5681.6164,
    'sunday_date' : 0.3158,
    'week_number' : -1.4148,
    'Guest Pastor' : -13.0240,
    'Executive Pastor' : 0.1442,
    'Pastor Joby' :2.1450,
    'Easter' : 373.0117,
    'Promotion Week' : 129.6823,
    'Saturated Sunday' : 156.1531,
    'Christmas' : 285.94632,
    'Kids Projection' : .25,
    'Kids Easter' : .15,
    'New Building' : 492.5563

},

'7:22' : {
    'PercentofTotal' : .20
}
}

students = {
    'Middle School' : {
        'intercept' : -134.127525,   #-150.3
        'sunday_date' : 0.007249,
        'week_number' : 0.018061,
        'In_Out' : 1.966009,
        'New Building': 4.383636
    },
    'High School': {
        'intercept' : -114.203912,
        'sunday_date' : 0.006256,
        'week_number' : 0.038843,
        'In_Out' : 1.730
    }
}

### logo
logo_file = "https://raw.githubusercontent.com/aarmobley/CoE22/main/E22%20Logo.png"
st.image(logo_file, width=150)


##### sidebar

with st.sidebar:
    st.markdown("""
                Important Dates: 
                - 08-10-2025 (Promotion Week)  
                - 09-14-2025 (Saturated Sunday)
                - 12-24-2025 (Christmas)
                - 01-04-2026 (Back to School)
                - 04-05-2026 (Easter) 
                
                """)


title = st.header("St. Johns Adults and Kids Projection")


num_week = [week for _ in range(2) for week in range(1, 53)]
if len(num_week) < 104:
    num_week.append(53)
#momentum = ['Easter', 'Back to School-August', 'Christmas', 'Back to School-January', 'Easter 2025']


##listing service times based on coefficients
service_times = list(coefficients.keys())

##listing students option - Fixed this part
student_options_list = list(students.keys())

school_year = ("In-School", "Summer")



##create dates for 2 year projection
start_date = datetime(2025, 1, 5)  # Start date
date_range = [start_date + timedelta(weeks=i) for i in range(104)]  # 104 weeks range

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



#### ATTENDANCE PREDICTION

#### predict button formula
numerical_date = date_mapping[selected_date_str]                                                         #numerical_date = date_mapping[select_date]

# Function to calculate prediction for a given service
def calculate_prediction(service_name, numerical_date, select_week, select_pastor, select_event):
    service_options = coefficients[service_name]
    weeknum_effect = service_options['week_number'] * (select_week)
    sundaydate_effect = service_options['sunday_date'] * (numerical_date)
    pastor = service_options[select_pastor]
    new_building = service_options['New Building']

    ### No Event coefficient needs to be 0
    no_event = 0
    if select_event != 'None':
        no_event = service_options[select_event]
    
    prediction = ((service_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + (pastor) + no_event + new_building)
    return prediction

if st.button("Make Projection"):
    if select_service == '7:22':
        # Calculate predictions for 9:00 and 11:22 services
        prediction_9 = calculate_prediction('9:00', numerical_date, select_week, select_pastor, select_event)
        prediction_11 = calculate_prediction('11:22', numerical_date, select_week, select_pastor, select_event)
        
        # Calculate 7:22 as 20% of the combined total
        combined_total = prediction_9 + prediction_11
        prediction = combined_total * coefficients['7:22']['PercentofTotal']
        
        # For 7:22, we'll use the kids projection from 9:00 service as a default
        kids_1122 = prediction * coefficients['9:00']['Kids Projection']
        kids_easter = prediction * coefficients['9:00']['Kids Easter']
        
    else:
        # Original calculation for 9:00 and 11:22
        service_options = coefficients[select_service]
        weeknum_effect = service_options['week_number'] * (select_week)
        sundaydate_effect = service_options['sunday_date'] * (numerical_date)
        pastor = service_options[select_pastor]
        new_building = service_options['New Building']
        
        ### No Event coefficient needs to be 0
        no_event = 0
        if select_event != 'None':
            no_event = service_options[select_event]
        
        prediction = ((service_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + (pastor) + no_event + new_building)   ###need to figure out where new building fits in
        kids_1122 = prediction * service_options['Kids Projection']
        kids_easter = prediction * service_options['Kids Easter']
    
    capacity = prediction / 1948 * (100)
    kids_capacity = kids_1122 / 470 * (100)
    
    #divider before projected attendance
    st.divider()
    
    st.write(f"Projected Adult Attendance: {prediction:.0f}")
    
    color = "red" if capacity > 70 else "blue"
    
    st.markdown(f"<p style='color:{color}; font-size:18px;'>Worship Center Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)
    
    st.divider()
    
    
    #kids projections with Easter
    if select_event == 'Easter':
        st.write(f"Projected Kids Attendance: {kids_easter: .0f}")
        kids_capacity_easter = kids_easter / 470 * (100)  # Fixed capacity calculation for Easter
        color = "red" if kids_capacity_easter > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_capacity_easter:.0f}%</p>", unsafe_allow_html=True)
    
    else: 
        st.write(f"Projected Kids Attendance: {kids_1122: .0f}")
         ## HTML and markdown for kids capacity
        color = "red" if kids_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_capacity:.0f}%</p>", unsafe_allow_html=True)


st.divider()

title = st.header("St. Johns Students Projection")

# Second set of selectboxes for students
date_options_students = st.selectbox("Select SundayDate", date_week_options, key="students_date")
select_students = st.selectbox("Select Students", student_options_list)  # Fixed variable name
select_in_out = st.selectbox("Select Time of Year", school_year )

# Parse the selected date for students (same logic as above)
selected_date_str_students = date_options_students.split(' ')[0]
select_week_students = int(date_options_students.split('Week ')[-1].strip(')'))
numerical_date_students = date_mapping[selected_date_str_students]

if st.button("Make Projection", key="students_projection"):
    # Use students coefficients instead of service_options
    student_options = students[select_students]
    
    # Calculate prediction using students coefficients INCLUDING week number
    sundaydate_effect_students = student_options['sunday_date'] * numerical_date_students
    weeknum_effect_students = student_options['week_number'] * select_week_students
    
    # Apply In_Out coefficient based on selection
    # If "In-School" is selected, use the coefficient value
    # If "Summer" is selected, use 0 (no effect)
    in_out_effect = student_options['In_Out'] if select_in_out == "In-School" else 0
    
    # Handle New Building coefficient - only apply if it exists for the selected student group
    if select_students == "Middle School" and 'New Building' in student_options:
        new_building_effect = student_options['New Building']
    else:
        new_building_effect = 0

    prediction_students = (student_options['intercept'] + 
                          sundaydate_effect_students + 
                          weeknum_effect_students + 
                          in_out_effect +
                          new_building_effect)
    
    # Apply the square transformation as shown in your code
    prediction_students_final = prediction_students ** 2
    
    # Show total attendance for both groups
    st.write(f"Projected {select_students} Total: {prediction_students_final:.0f}")
    
    # Only show Wednesday attendance for Middle School
    if select_students == "Middle School":
        wednesday = prediction_students_final * .45
        sunday = prediction_students_final * .55
        st.write(f"Projected {select_students} Wednesday Attendance: {wednesday:.0f}")
        st.write(f"Projected {select_students} Sunday Attendance: {sunday:.0f}")





