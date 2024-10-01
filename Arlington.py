



import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta

coefficients = {

	
	'09:00:00': {
        	'intercept' : -38.65,
        	'sunday_date' : .002963, 
        	'week_number' : .003602,
        	'Guest Pastor' : -.4529,
        	'Executive Pastor' :  -.8438,
        	'Pastor Joby' : -.1221,
        	'Easter' : 6.193,
       	 	'BacktoSchool' : .08546,
        	'Saturated Sunday' : .9908,
        	'kids_projection' : 0.29,
			'kids_easter' : .25
    },
    
    '11:22:00': {

       		'intercept' : -4.1528006,
       		'sunday_date' : 0.0011252,
        	'week_number' : -.0178361,
       		'Guest Pastor' : -.7539401,
      		'Executive Pastor' : -.3526798,
       		'Pastor Joby' : .1628141,
        	'Easter' : 5.4945168,
        	'BacktoSchool' : -.9172174,
        	'Saturated Sunday' : 1.6824265,
        	'kids_projection' : .30,
			'kids_easter' : .25
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
                - 01-05-2025 (Back to School)
                - 04-20-2025 (Easter) """)




title = st.title("Arlington Attendance Projection")

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


### If there is no event, select none
### No Event coefficient needs to be 0
no_event = 0
pastor = 0

if select_event != 'None':
    no_event = service_options[select_event]
else: pastor = service_options[select_pastor]

#event = service_options[select_event]


    


### Predict button fromula

if st.button("Make Projection"):
    prediction = ((service_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + (pastor) + no_event)
    prediction1 =  (prediction) ** (2)
    
    kids_1122 = prediction1 * service_options['kids_projection']
    kids_easter = prediction1 * service_options['kids_easter']
    
    
    ###capacity
    capacity = prediction1 / 850 * (100)
    kids_cap = kids_1122 / 225 * (100)
    


    
    #divider before projected attendance
    st.divider()
    
    
    
    ### projection and capacity
    st.write(f"Projected Adult Attendance: {prediction1:.0f}")
    
     ### HTML and MArkdown for adult capacity
    color = "red" if capacity > 80 else "blue"
    
    st.markdown(f"<p style='color:{color}; font-size:18px;'>Adult Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)                                       #st.write(f"Adult Capacity: {capacity: .0f}%")
    
    
    #st.write(f"Adult Capacity: {capacity: .0f}%")
    
    st.divider()
    
    #####kids projection and capacity
    if select_event == 'Easter':
        st.write(f"Projected Kids Attendance: {kids_easter: .0f}")
        color = "red" if kids_cap > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_cap:.0f}%</p>", unsafe_allow_html=True)
    
    else: 
        st.write(f"Projected Kids Attendance: {kids_1122: .0f}")
         ## HTML and markdown for kids capacity
        color = "red" if kids_cap > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_cap:.0f}%</p>", unsafe_allow_html=True)
    
    
    