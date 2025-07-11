


import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta

coefficients = {
    

'09:00'  :   {

    'intercept' : -7319.7344,
    'sunday_date' : 0.4052,
    'week_number' : -0.8006,
    'Guest Pastor' : -24.5846,
    'Executive Pastor' : -11.2854,
    'Pastor Joby' : -9.9740,
    'Easter' : 366.5613,
    'BacktoSchool' : 98.5655,
    'Saturated Sunday' : 142.8192,
    'Christmas' : 267.1385 ,
    'Kids Projection' : .37,
    'Kids Easter' : .24,
    'New Building' : 706.0721

},

'11:22' : {

    'intercept' : -5819.98219,
    'sunday_date' :  0.32295,
    'week_number' : -1.40040,
    'Guest Pastor' : -15.11825,
    'Executive Pastor' : -21.48908,
    'Pastor Joby' : 9.44896,
    'Easter' : 384.33688,
    'BacktoSchool' : 128.17882,
    'Saturated Sunday' : 147.10815,
    'Christmas' : 285.94632,
    'Kids Projection' : .29,
    'Kids Easter' : .15,
    'New Building' : 516.5903

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

event_options = ['None', 'Easter', 'BacktoSchool', 'Saturated Sunday', 'Christmas']


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
        prediction_9 = calculate_prediction('09:00', numerical_date, select_week, select_pastor, select_event)
        prediction_11 = calculate_prediction('11:22', numerical_date, select_week, select_pastor, select_event)
        
        # Calculate 7:22 as 20% of the combined total
        combined_total = prediction_9 + prediction_11
        prediction = combined_total * coefficients['7:22']['PercentofTotal']
        
        # For 7:22, we'll use the kids projection from 9:00 service as a default
        kids_1122 = prediction * coefficients['09:00']['Kids Projection']
        kids_easter = prediction * coefficients['09:00']['Kids Easter']
        
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


st.divider()

# CSV Generation Section
st.header("Generate CSV Report")

# Multi-select date range
csv_dates = st.multiselect("Select Dates for CSV Export", date_week_options, default=[])

# Service parameters for CSV
csv_service = st.selectbox("Service Time for CSV", service_times, key="csv_service")
csv_pastor = st.selectbox("Pastor for CSV", pastor_options, key="csv_pastor")
csv_event = st.selectbox("Event for CSV", event_options, key="csv_event")

# Student parameters for CSV
csv_students = st.selectbox("Student Group for CSV", student_options_list, key="csv_students")
csv_in_out = st.selectbox("Time of Year for CSV", school_year, key="csv_in_out")

if st.button("Generate CSV Report") and csv_dates:
    csv_data = []
    
    for date_option in csv_dates:
        # Parse date and week
        date_str = date_option.split(' ')[0]
        week_num = int(date_option.split('Week ')[-1].strip(')'))
        numerical_date_csv = date_mapping[date_str]
        
        # Calculate adult attendance
        if csv_service == '7:22':
            pred_9 = calculate_prediction('09:00', numerical_date_csv, week_num, csv_pastor, csv_event)
            pred_11 = calculate_prediction('11:22', numerical_date_csv, week_num, csv_pastor, csv_event)
            combined = pred_9 + pred_11
            adult_attendance = combined * coefficients['7:22']['PercentofTotal']
            kids_attendance = adult_attendance * coefficients['09:00']['Kids Projection']
            kids_easter_attendance = adult_attendance * coefficients['09:00']['Kids Easter']
        else:
            adult_attendance = calculate_prediction(csv_service, numerical_date_csv, week_num, csv_pastor, csv_event)
            service_opts = coefficients[csv_service]
            kids_attendance = adult_attendance * service_opts['Kids Projection']
            kids_easter_attendance = adult_attendance * service_opts['Kids Easter']
        
        # Use Easter kids projection if event is Easter
        final_kids_attendance = kids_easter_attendance if csv_event == 'Easter' else kids_attendance
        
        # Calculate capacities
        adult_capacity = adult_attendance / 1948 * 100
        kids_capacity = final_kids_attendance / 470 * 100
        
        # Calculate student attendance
        student_opts = students[csv_students]
        sunday_effect = student_opts['sunday_date'] * numerical_date_csv
        week_effect = student_opts['week_number'] * week_num
        in_out_effect = student_opts['In_Out'] if csv_in_out == "In-School" else 0
        new_building_effect = student_opts['New Building'] if csv_students == "Middle School" and 'New Building' in student_opts else 0
        
        student_prediction = (student_opts['intercept'] + sunday_effect + week_effect + in_out_effect + new_building_effect)
        student_final = student_prediction ** 2
        
        # Middle School breakdown
        if csv_students == "Middle School":
            student_wednesday = student_final * 0.45
            student_sunday = student_final * 0.55
        else:
            student_wednesday = None
            student_sunday = None
        
        # Add to CSV data
        csv_data.append({
            'Date': date_str,
            'Week': week_num,
            'Service_Time': csv_service,
            'Pastor': csv_pastor,
            'Event': csv_event,
            'Adult_Attendance': round(adult_attendance),
            'Adult_Capacity_Percent': round(adult_capacity, 1),
            'Kids_Attendance': round(final_kids_attendance),
            'Kids_Capacity_Percent': round(kids_capacity, 1),
            'Student_Group': csv_students,
            'Time_of_Year': csv_in_out,
            'Student_Total': round(student_final),
            'Student_Wednesday': round(student_wednesday) if student_wednesday else None,
            'Student_Sunday': round(student_sunday) if student_sunday else None
        })
    
    # Create DataFrame and CSV
    df = pd.DataFrame(csv_data)
    csv_string = df.to_csv(index=False)
    
    # Display preview
    st.subheader("CSV Preview")
    st.dataframe(df)
    
    # Download button
    st.download_button(
        label="Download CSV",
        data=csv_string,
        file_name=f"stjohns_projections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )



