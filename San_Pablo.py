##########San Pablo PROJECTIONS 9:00 and 11:22

import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta


    

coefficients = {

 '7:22': {
        'intercept' : -135.82447,
        'sunday_date' : 0.00905,
        'week_number' : -0.06895,
        'Guest Pastor' : -1.64363,
        'Executive Pastor' : -2.90210,
        'Pastor Joby' : -1.17237,
        'Easter' :  6.32402,
        'Promotion Week' : 1.52663,
        'Back to School' : 1.52663,
        'Saturated Sunday' :  13.94077,
        'kids_projection' : .08,
        'kids_easter' : .08,
        'Christmas' : 6.52290
    },
    
    
    
  '09:00:00': {
        'intercept' : -211.279175,
        'sunday_date' : 0.013135, 
        'week_number' : -0.003892,
        'Guest Pastor' : -1.708413,
        'Executive Pastor' :  -1.202008,
        'Pastor Joby' : 0.983648,
        'Easter' : 16.092007,
       	'Promotion Week' : 0.332188,
        'Back to School' : 0.332188,
        'Saturated Sunday' : 6.668219,
        'kids_projection' : 0.22,
        'kids_easter' : .12,
        'Christmas' : 3.349966
        

    },
    
  '11:22:00': {

       	'intercept' : -151.7846,
       	'sunday_date' : 0.01,
        'week_number' : -0.0726,
       	'Guest Pastor' :  -1.6713,
      	'Executive Pastor' : -1.4246,
       	'Pastor Joby' : 0.2733,
        'Easter' : 14.6459,
        'Promotion Week' : 3.4931,
        'Back to School' : 3.4931,
        'Saturated Sunday' : 6.2969,
        'kids_projection' : .15,
        'kids_easter' : .12,
        'kids_labor' : 17.64,
        'Christmas' : 9.5353
    },
    
}


### logo
logo_file = "https://raw.githubusercontent.com/aarmobley/CoE22/main/E22%20Logo.png"
st.image(logo_file, width=150)

st.link_button("Go to Campus Dashboard", "https://app.powerbi.com/reportEmbed?reportId=fa1a49cb-9b22-4086-a694-39b61e180281&autoAuth=true&ctid=c441cd00-b4c3-41ab-9fc5-d891c8b7fc28")

##### sidebar

with st.sidebar:
    st.markdown("""
                Important Dates: 
                - 08-11-2024 (Promotion Week)  
                - 09-15-2024 (Saturated)
                - 12-22-2024 (Christmas)
                - 01-05-2025 (Back to School)
                - 04-20-2025 (Easter) """)

title = st.title("San Pablo Attendance Projection")

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
service_times = list(coefficients.keys()) + ["All Services"]   #### LEFT OFF HERE


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

event_options = ['None', 'Easter', 'Promotion Week', 'Saturated Sunday', 'Christmas', 'Back to School', 'Inclement Weather']


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




#### updating attendance if prediciton is not accurate
#if select_service == "11:22:00":
    #number = st.number_input("Previous Service Attendance", value=0.0, placeholder= "Enter Attendance")

    #updated = number - (number * .22) 
    #st.write("Updated Attendance is", updated)

    


####predict button for all services selected

if st.button("Make Projection"):
    if select_service == "All Services":
        total_prediction = 0  #
        for service in coefficients:
            service_options = coefficients[service]
            weeknum_effect = service_options['week_number'] * (select_week)
            sundaydate_effect = service_options['sunday_date'] * (numerical_date)
            no_event = 0
            pastor = 0

        
            if select_event != 'None':
                no_event = service_options[select_event]
            else:
                pastor = service_options[select_pastor ]



            prediction = ((service_options['intercept']) + sundaydate_effect + weeknum_effect + pastor + no_event)
            total_prediction += prediction ** 2


        # Display the total for all services
        st.divider()
        st.write(f"Projected Total Attendance - Adults (All Services): {total_prediction:.0f}")
    else:
        # Regular calculation for a single service
        service_options = coefficients[select_service]
        weeknum_effect = service_options['week_number'] * select_week
        sundaydate_effect = service_options['sunday_date'] * numerical_date
        no_event = 0
        pastor = 0
        
        if select_event != 'None':
            no_event = service_options.get(select_event, 0)
        else:
            pastor = service_options.get(select_pastor, 0)

        # Calculate prediction for the selected service
        prediction = ((service_options['intercept']) + sundaydate_effect + weeknum_effect + pastor + no_event)
        prediction1 = prediction ** 2

    

    
        kids_1122 = prediction1 * service_options['kids_projection']
    
        kids_easter = prediction1 * service_options['kids_easter']

        inclement_weather1 = prediction1 * .15
        inclement_weather = prediction1 - inclement_weather1
    #kids_labor = prediction1 * service_options['kids_labor']
    
    
        capacity = prediction1 / 3001 * (100)
    
        kids_capacity = kids_1122 / 750 * (100)
    
        kids_easter_capacity = kids_easter / 750 *(100)
    
        
    

    
    #divider before projected attendance
        st.divider()
    if select_event != 'Inclement Weather':
        st.write(f"Projected Adult Attendance: {prediction1:.0f}")
        color = "red" if capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True) 
    else:    
        st.write(f"Projected Adult Attendance: {inclement_weather:.0f}")
        color = "red" if capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)
    
    ### HTML and MArkdown for adult capacity
        #color = "red" if capacity > 80 else "blue"
    
        #st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)                                       #st.write(f"Adult Capacity: {capacity: .0f}%")
    
    
    ###st.write(f"Weekly Total: {select_service: .0f} ")
    #####
    st.divider()
    
    
    if select_event == 'Easter':
        st.write(f"Projected Kids Attendance: {kids_easter: .0f}")
        color = "red" if kids_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_easter_capacity:.0f}%</p>", unsafe_allow_html=True)
    
    else: 
        st.write(f"Projected Kids Attendance: {kids_1122: .0f}")
             ## HTML and markdown for kids capacity
        color = "red" if kids_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_capacity:.0f}%</p>", unsafe_allow_html=True)
        
        
        
    ## HTML and markdown for kids capacity
   # color = "red" if kids_capacity > 80 else "blue"
    #st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_capacity:.0f}%</p>", unsafe_allow_html=True)
    

    ### side bar button to list important dates like easter, christmas, promotion weekend
    
    ### Have a Week total - and each service have a percent of the total
    
    ###Disciple Group projection based off of the weekly total
    
    ###Disciple Group Total vs. goal based on projection
    
    
