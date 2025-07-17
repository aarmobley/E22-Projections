##########North Jax PROJECTIONS 9:00 and 11:22

import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta


    

coefficients = {

 '9:00': {
        'intercept' : -5996.548,
        'sunday_date' :  0.323,
        'WeekNumber' : -0.672,
        'Saturated Sunday' : 105.441,
        'Easter' : 125.539,
        'Promotion Week' : 11.408,
        'kids_projection' : .28,
        'kids_easter' : .08,
        'Christmas' : -158.638,
        'Wildlight' : -130.274
    },
 '11:22': {
        'intercept' : -1798.8597,
        'sunday_date' :  0.1082,
        'WeekNumber' : -0.5227,
        'Saturated Sunday' : 164.4344,
        'Easter' : 181.8301,
        'Promotion Week' : 59.5298,
        'kids_projection' : .28,
        'kids_easter' : .08,
        'Christmas' : 41.9161,
        'Wildlight' : -76.7777
    },

'7:22' :  {
       'New' : .23
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
                - 09-14-2025 (Saturated)
                - 12-24-2024 (Christmas)
                - 01-05-2026 (Back to School)
                - 04-05-2026 (Easter) """)

title = st.title("North Jax Attendance Projection")

#dates = pd.read_csv(r"C:\Users\aaron\OneDrive\Desktop\python\RegressionDates1.csv")
#dates.info()
#dates.head()
#sunday_dates = dates['date'].tolist()
#num_date = dates['num_date'].tolist()
num_week = [week for _ in range(3) for week in range(1, 53)]
if len(num_week) < 156:
    num_week.append(53)
#momentum = ['Easter', 'Back to School-August', 'Christmas', 'Back to School-January', 'Easter 2025']


##listing service times based on coefficients
service_times = list(coefficients.keys())


##create dates for 2 year projection
start_date = datetime(2025, 1, 7)  # Start date
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
#pastor_options = ['Pastor Joby', 'Guest Pastor', 'Executive Pastor']

event_options = ['None', 'Easter', 'Promotion Week', 'Saturated Sunday', 'Christmas']


####creating selectbox options
#select_date = st.selectbox("Select a Sunday Date", date_options)

#select_week = st.selectbox("Select Week Number", num_week)

select_service = st.selectbox("Select a Service", service_times)

#select_pastor = st.selectbox("Select a Pastor", pastor_options)

select_event = st.selectbox("Select Event", event_options)
#select_date1 = st.selectbox("Select a Sunday Date", sunday_dates)
#select_event = st.selectbox("Select a Momentum Event", momentum)



#### ATTENDANCE PREDICTION

#### predict button formula
numerical_date = date_mapping[selected_date_str]                                                         #numerical_date = date_mapping[select_date]

service_options = coefficients[select_service]

# Variables will be set inside the conditional blocks below




#### updating attendance if prediciton is not accurate
#if select_service == "11:22:00":
    #number = st.number_input("Previous Service Attendance", value=0.0, placeholder= "Enter Attendance")

    #updated = number - (number * .22) 
    #st.write("Updated Attendance is", updated)

    

st.write("***This Campus Projection is Still In Development")
####predict button

if st.button("Make Projection"):
    
    # Handle 7:22 service differently - it's calculated as 23% of 9:00 + 11:22
    if select_service == '7:22':
        # Calculate 9:00 service projection
        service_900 = coefficients['9:00']
        weeknum_effect_900 = service_900['WeekNumber'] * (select_week)
        sundaydate_effect_900 = service_900['sunday_date'] * (numerical_date)
        wildlight_effect_900 = service_900['Wildlight']
        no_event_900 = 0
        if select_event != 'None':
            no_event_900 = service_900[select_event]
        prediction_900 = ((service_900['intercept']) + (sundaydate_effect_900) + (weeknum_effect_900) + wildlight_effect_900 + no_event_900)
        
        # Calculate 11:22 service projection
        service_1122 = coefficients['11:22']
        weeknum_effect_1122 = service_1122['WeekNumber'] * (select_week)
        sundaydate_effect_1122 = service_1122['sunday_date'] * (numerical_date)
        wildlight_effect_1122 = service_1122['Wildlight']
        no_event_1122 = 0
        if select_event != 'None':
            no_event_1122 = service_1122[select_event]
        prediction_1122 = ((service_1122['intercept']) + (sundaydate_effect_1122) + (weeknum_effect_1122) + wildlight_effect_1122 + no_event_1122)
        
        # 7:22 is 23% of the total of 9:00 and 11:22
        prediction = (prediction_900 + prediction_1122) * 0.23
        
        # Use 9:00 service coefficients for kids projections for 7:22
        kids_projection = prediction * service_900['kids_projection']
        kids_easter = prediction * service_900['kids_easter']
        
    else:
        # For 9:00 and 11:22 services, use original calculation
        weeknum_effect = service_options['WeekNumber'] * (select_week)
        sundaydate_effect = service_options['sunday_date'] * (numerical_date)
        wildlight_effect = service_options['Wildlight']
        no_event = 0
        if select_event != 'None':
            no_event = service_options[select_event]
        prediction = ((service_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + wildlight_effect + no_event)
        
        # Kids projection for the selected service
        kids_projection = prediction * service_options['kids_projection']
        kids_easter = prediction * service_options['kids_easter']
    
    
    
    
    capacity = prediction / 700 * (100)
    
    kids_capacity = kids_projection / 350 * (100)
    
    kids_easter_capacity = kids_easter / 350 *(100)
    
        
    

    
    #divider before projected attendance
    st.divider()
    
    ###Display projection for selected service
    st.markdown(f"{select_service} Projected Adult Attendance  - {prediction:.0f}")
    
    st.markdown(f"Projected Kids Attendance: {kids_projection:.0f}")
    
    ### HTML and MArkdown for adult capacity
    color = "red" if capacity > 80 else "blue"
    
    #st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)                                       #st.write(f"Adult Capacity: {capacity: .0f}%")
    
    
    ###st.write(f"Weekly Total: {select_service: .0f} ")
    #####
    st.divider()
    
    
    if select_event == 'Easter':
        st.write(f"Easter Kids Attendance: {kids_easter: .0f}")
        color = "red" if kids_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_easter_capacity:.0f}%</p>", unsafe_allow_html=True)
        
