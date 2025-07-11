##########North Jax PROJECTIONS 9:00 and 11:22

import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta


    

coefficients = {

 '9:00:00': {
        'intercept' : -1489.2378,
        'sunday_date' : 0.0961,
        'week_number' : -1.3899,
        'Saturated Sunday' : 125.3024,
        'Easter' : 86.2632,
        'Promotion Week' : 61.8972,
        'kids_projection' : .32,
        'kids_easter' : .27,
        'Christmas' : 85.7072

    },
 '11:22:00': {
        'intercept' : 1066.1896,
        'sunday_date' : -0.0362,
        'week_number' : -1.0235,
        'Saturated Sunday' : 280.5179,
        'Easter' : 80.8687,
        'Promotion Week' : 92.1327,
        'Back to School' : 92.1327,
        'kids_projection' : .23,
        'kids_easter' : .29,
        'Christmas' : 38.8151

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

weeknum_effect = service_options['week_number'] * (select_week)

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
    prediction = ((service_options['intercept']) + (sundaydate_effect) + (weeknum_effect)  + no_event)
    #prediction1 =  (prediction) ** (2)
    
    # breaking down total into separate 9:00 and 11:22 services
    #prediction900 = prediction / 2.25
    
    #prediction1122 = prediction900 * 1.25
    
    kids_nj = prediction * service_options['kids_projection']
 
    
    #kids easter percentage
    kids_easter = prediction * service_options['kids_easter']
    
    
    #capacity for worship center
    capacity = prediction / 700 * (100)
    
    #formula for capacity for kids
    kids_capacity = kids_nj / 350 * 100
    kids_easter_capacity = kids_easter / 350 *(100)
    
        
    

    
    #divider before projected attendance
    st.divider()
    
    ###needs 9:00 and 11:22
    st.markdown(f"Projected Adult Attendance: {prediction:.0f}")
    
    #st.markdown(f"11:22 Projected Adult Attendance - {prediction1122:.0f}")
    
    ### HTML and MArkdown for adult capacity
    color = "red" if kids_capacity > 70 else "blue"
    st.markdown(f"<p style='color:{color}; font-size:18px;'>Worship Center Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)
    
    #st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)                                       #st.write(f"Adult Capacity: {capacity: .0f}%")
    
    #####
    st.divider()
    
    
    if select_event == 'Easter':
        st.write(f"Projected Kids Attendance: {kids_easter: .0f}")
        color = "red" if kids_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_easter_capacity:.0f}%</p>", unsafe_allow_html=True)
    
    else: 
        st.write(f"Projected Kids Attendance: {kids_nj: .0f}")
        color = "red" if kids_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_capacity:.0f}%</p>", unsafe_allow_html=True)
        
         ## HTML and markdown for kids capacity
        #color = "red" if kids_capacity > 80 else "blue"
        #st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_capacity:.0f}%</p>", unsafe_allow_html=True)
        
