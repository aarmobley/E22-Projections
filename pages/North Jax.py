##########North Jax PROJECTIONS 9:00 and 11:22

import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta


    

coefficients = {

 '9:00': {
        'intercept' : -1432.1719,
        'sunday_date' : 0.0913,
        'Saturated Sunday' : 111.6333,
        'Easter' : 106.0362,
        'Promotion Week' : 116.0079,
        'kids_projection' : .28,
        'kids_easter' : .08,
        'Christmas' : 52.3704

    },
    
    
}


### logo
logo_file = "https://raw.githubusercontent.com/aarmobley/CoE22/main/E22%20Logo.png"
st.image(logo_file, width=150)



##### sidebar

with st.sidebar:
    st.markdown("""
                Important Dates: 
                - 08-11-2024 (Promotion Week)  
                - 09-15-2024 (Saturated)
                - 12-22-2024 (Christmas)
                - 01-05-2025 (Back to School)
                - 04-20-2025 (Easter) """)

title = st.title("North Jax Attendance Projection")

#dates = pd.read_csv(r"C:\Users\aaron\OneDrive\Desktop\python\RegressionDates1.csv")
#dates.info()
#dates.head()
#sunday_dates = dates['date'].tolist()
#num_date = dates['num_date'].tolist()
num_week = [week for _ in range(2) for week in range(1, 53)]
if len(num_week) < 104:
    num_week.apend(53)
#momentum = ['Easter', 'Back to School-August', 'Christmas', 'Back to School-January', 'Easter 2025']


##listing service times based on coefficients
service_times = list(coefficients.keys())


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

#weeknum_effect = service_options['week_number'] * (select_week)
sundaydate_effect = service_options['sunday_date'] * (numerical_date)

#pastor = service_options[select_pastor]



### No Event coefficient needs to be 0 and pastor needs to be zero if any event is selected so it's not calcualted
no_event = 0
pastor = 0
if select_event != 'None':
    no_event = service_options[select_event]




#### updating attendance if prediciton is not accurate
#if select_service == "11:22:00":
    #number = st.number_input("Previous Service Attendance", value=0.0, placeholder= "Enter Attendance")

    #updated = number - (number * .22) 
    #st.write("Updated Attendance is", updated)

    

st.write("***This Campus Projection is Still In Development")
####predict button

if st.button("Make Projection"):
    prediction = ((service_options['intercept']) + (sundaydate_effect)  + no_event)
    #prediction1 =  (prediction) ** (2)
    
    # breaking down total into separate 9:00 and 11:22 services
    #prediction900 = prediction / 2.25
    
    #prediction1122 = prediction900 * 1.25
    
    kids_900 = prediction * service_options['kids_projection']
    #kids_1122 = prediction1122 * service_options['kids_projection']
    
    #kids easter percentage
    kids_easter = prediction * service_options['kids_easter']
    
    
    
    
    capacity = prediction / 700 * (100)
    
    kids_capacity = kids_1122 / 350 * (100)
    
    kids_easter_capacity = kids_easter / 350 *(100)
    
        
    

    
    #divider before projected attendance
    st.divider()
    
    ###needs 9:00 and 11:22
    st.markdown(f"9:00 Projected Adult Attendance  - {prediction:.0f}")
    
    #st.markdown(f"11:22 Projected Adult Attendance - {prediction1122:.0f}")
    
    ### HTML and MArkdown for adult capacity
    color = "red" if capacity > 80 else "blue"
    
    #st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)                                       #st.write(f"Adult Capacity: {capacity: .0f}%")
    
    
    ###st.write(f"Weekly Total: {select_service: .0f} ")
    #####
    st.divider()
    
    
    if select_event == 'Easter':
        st.write(f"Projected Kids Attendance: {kids_easter: .0f}")
        color = "red" if kids_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_easter_capacity:.0f}%</p>", unsafe_allow_html=True)
    
    else: 
        st.write(f"9:00 Projected Kids Attendance  -  {kids_900: .0f}")
        st.write(f"11:22 Projected Kids Attendnace -  {kids_1122: .0f}")
         ## HTML and markdown for kids capacity
        #color = "red" if kids_capacity > 80 else "blue"
        #st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_capacity:.0f}%</p>", unsafe_allow_html=True)
        
