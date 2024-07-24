#### streamlit python

##########FLEMING ISLAND PROJECTIONS 9:00 and 11:22

import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta


####coefficients for 11:22        11:22 = 3     9:00 = 4
coefficients = {
    
    '7:22': {
        'intercept' : -50.03,
        'sunday_date' : .003145,
        'week_number' : .009080,
        'Guest Pastor' : .002012,
        'Executive Pastor' : -.07055,
        'Pastor Joby' : .3431,
        'Easter' : 5.711,
        'BackToSchool' : .6696,
        'Saturated Sunday' : 6.773
    },
    
    
    
    '09:00:00': {
        'intercept' : -62.398,
        'sunday_date' : .004255, 
        'week_number' : -.0001747,
        'Guest Pastor' : -.010888,
        'Executive Pastor' :  -.591838,
        'Pastor Joby' : .576633,
        'Easter' : 7.645752,
        'BacktoSchool' : 1.031662,
        'Saturated Sunday' : 1.163100
    },
    
    '11:22:00': {

        'intercept' : -49.72,
        'sunday_date' : .003626,
        'week_number' : -.02766,
        'Guest Pastor' : -.6772,
        'Executive Pastor' : -.5607,
        'Pastor Joby' : .01990,
        'Easter' : 6.137,
        'BacktoSchool' : 1.884,
        'Saturated Sunday' : 2.988
    },
    
}





title = st.title("Fleming Island Attendance Projection")

dates = pd.read_excel(r"C:\Users\aaron\OneDrive\Desktop\python\RegressionDates.xlsx")
dates.info()
#dates.head()
sunday_dates = dates['date'].tolist()
num_date = dates['num_date'].tolist()
num_week = dates['num_week'].to_list()
#momentum = ['Easter', 'Back to School-August', 'Christmas', 'Back to School-January', 'Easter 2025']


##listing service times based on coefficients
service_times = list(coefficients.keys())


##create dates for 2 year projection
start_date = datetime(2024, 1, 7)  # Start date
date_range = [start_date + timedelta(weeks=i) for i in range(104)]  # 104 weeks range

# Create date mapping with numerical values as days since Unix epoch (1970-01-01)
epoch = datetime(1970, 1, 1)
date_mapping = {date.strftime('%m-%d-%Y'): (date - epoch).days for date in date_range}

#list dates numerically
date_options = list(date_mapping.keys())

#list pastors
pastor_options = ['Pastor Joby', 'Guest Pastor', 'Executive Pastor']

event_options = ['None', 'Easter', 'BacktoSchool', 'Saturated Sunday']


####creating selectbox options
select_date = st.selectbox("Select a Sunday Date", date_options)

select_week = st.selectbox("Select Week Number", num_week)

select_service = st.selectbox("Select a Service", service_times)

select_pastor = st.selectbox("Select a Pastor", pastor_options)

select_event = st.selectbox("Select Event", event_options)
#select_date1 = st.selectbox("Select a Sunday Date", sunday_dates)
#select_event = st.selectbox("Select a Momentum Event", momentum)



#### ATTENDANCE PREDICTION

#### predict button formula
numerical_date = date_mapping[select_date]

service_options = coefficients[select_service]

weeknum_effect = service_options['week_number'] * select_week
sundaydate_effect = service_options['sunday_date'] * numerical_date

pastor = service_options[select_pastor]

### No Event coefficient needs to be 0
no_event = 0

if select_event != 'None':
    no_event = service_options[select_event]

#event = service_options[select_event]



if st.button("Make Projection"):
    prediction = (service_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + (pastor) + no_event
    prediction1 = (prediction) ** 2
    capacity = prediction1 / 766 * (100)
    
    #divider before projected attendance
    st.divider()
    
    st.write(f"Projected Attendance: {prediction1:.2f}")
    
    st.write(f"Capacity: {capacity: .2f}%")
