##########San Pablo PROJECTIONS 9:00 and 11:22

import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta


    

coefficients = {

 '7:22': {
        'intercept' : -122.0,
        'sunday_date' : .008280,
        'week_number' : -.04381,
        'Guest Pastor' : -1.467,
        'Executive Pastor' : -.07055,
        'Pastor Joby' : -.5863,
        'Easter' : 6.387,
        'BacktoSchool' : 1.134,
        'Saturated Sunday' : 10.66,
        'kids_projection' : .08
    },
    
    
    
  '09:00:00': {
        'intercept' : -214.9,
        'sunday_date' : .01332, 
        'week_number' : -.002192,
        'Guest Pastor' : -1.699,
        'Executive Pastor' :  -1.307,
        'Pastor Joby' : 1.058,
        'Easter' : 16.03,
       	'BacktoSchool' : .2396,
        'Saturated Sunday' : 6.562,
        'kids_projection' : 0.21

    },
    
  '11:22:00': {

       	'intercept' : -155.5,
       	'sunday_date' : .01015,
        'week_number' : -.04676,
       	'Guest Pastor' : -1.526,
      	'Executive Pastor' : -1.526,
       	'Pastor Joby' : .4522,
        'Easter' : 14.72,
        'BacktoSchool' : 3.505,
        'Saturated Sunday' : 4.462,
        'kids_projection' : 0.16
    },
    
}



        


title = st.title("San Pablo Attendance Projection")

#dates = pd.read_csv(r"C:\Users\aaron\OneDrive\Desktop\python\RegressionDates1.csv")
#dates.info()
#dates.head()
#sunday_dates = dates['date'].tolist()
#num_date = dates['num_date'].tolist()
num_week = list(range(1, 53))
#momentum = ['Easter', 'Back to School-August', 'Christmas', 'Back to School-January', 'Easter 2025']


##listing service times based on coefficients
service_times = list(coefficients.keys())


##create dates for 2 year projection
start_date = datetime(2024, 1, 7)  # Start date
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

event_options = ['None', 'Easter', 'BacktoSchool', 'Saturated Sunday']


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

service_options = coefficients[select_service]

weeknum_effect = service_options['week_number'] * (select_week)
sundaydate_effect = service_options['sunday_date'] * (numerical_date)

pastor = service_options[select_pastor]

### No Event coefficient needs to be 0
no_event = 0

if select_event != 'None':
    no_event = service_options[select_event]

#event = service_options[select_event]


    




if st.button("Make Projection"):
    prediction = ((service_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + (pastor) + no_event)
    prediction1 =  (prediction) ** (2)
    
    kids_1122 = prediction1 * service_options['kids_projection']
    capacity = prediction1 / 3001 * (100)
    


    
    #divider before projected attendance
    st.divider()
    
    st.write(f"Projected Adult Attendance: {prediction1:.0f}")
    st.write(f"Adult Capacity: {capacity: .0f}%")
    
    st.divider()
    
    st.write(f"Projected Kids Attendance: {kids_1122: .0f}")
    

    