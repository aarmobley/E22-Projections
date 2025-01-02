import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta




##coefficients for Mandarin
coefficients = {
    
 
'09:00:00'  :   {

    'intercept' : -78.0882,
    'sunday_date' : 0.005,
    'week_number' : -0.0268,
    'Guest Pastor' : -0.3544,
    'Executive Pastor' : -0.2808,
    'Pastor Joby' : 0.383,
    'Easter' : 5.3472,
    'BacktoSchool' : 0.5319,
    'Promotion Weekend' : 0.5319,
    'Saturated Sunday' : 0.9357,
    'Christmas' : 2.0513,
    'Kids Projection' : .33,
    'Kids Easter' : .27

},

'11:22' : {

    'intercept' : -36.7261,
    'sunday_date' : 0.0028,
    'week_number' : -0.0366,
    'Guest Pastor' : -0.617,
    'Executive Pastor' : -0.5055,
    'Pastor Joby' : -0.0211,
    'Easter' : 5.7791,
    'BacktoSchool' : 1.2009,
    'Promotion Weekend' : 1.2009,
    'Saturated Sunday' : 2.4291,
    'Christmas' : 3.078,
    'Kids Projection' : .23,
    'Kids Easter' : .20

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


title = st.title("Mandarin Attendance Projection")

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

event_options = ['None', 'Easter', 'BacktoSchool', 'Promotion Weekend', 'Saturated Sunday', 'Christmas']


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


#### Predict button with formula, kids projection and capacity

if st.button("Make Projection"):
    prediction = ((service_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + (pastor) + no_event)
    prediction1 =  (prediction) ** (2) 
     
    kids = prediction1 * service_options['Kids Projection']
    
  
    
    kids_easter = prediction1  * service_options['Kids Easter']
    
   

    capacity = prediction1 / 840 * (100)

  
    
    kids_capacity = kids / 330 * (100)
    

    
    kids_easter_capacity = kids_easter / 330 * (100)
    
   
    
    
   
        
    
    
    ## projection displayed with capacity percentage
    st.divider()
    
    ### projecting for 9am with no squared formula
    st.write(f"Projected Adult Attendance: {prediction1:.0f}")
        
    st.write(f"Adult Capacity: {capacity: .0f}%")
    
    st.divider()
    
    
    #kids projections with Easter
    if select_event == 'Easter':
        st.write(f"Projected Kids Attendance: {kids_easter: .0f}")
        st.write(f"Kids Capacity: {kids_easter_capacity}")
    else:
        st.write(f"Projected Kids Attendance: {kids: .0f}")
        
        st.write(f"Kids Capacity: {kids_capacity: .0f}%")
