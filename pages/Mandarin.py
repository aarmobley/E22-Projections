import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta




##coefficients for Mandarin
coefficients = {
    
 
'9:00'  :   {

    'intercept' : -74.6171,
    'sunday_date' : 0.0048,
    'week_number' : -0.0207,
    'Guest Pastor' : -0.3774,
    'Executive Pastor' : -0.2371,
    'Pastor Joby' : 0.4148,
    'Easter' : 5.4126,
    'BacktoSchool' : 0.4991,
    'Promotion Weekend' : 0.4991,
    'Saturated Sunday' : 0.9016,
    'Christmas' : 2.0198,
    'Kids Projection' : .33,
    'Kids Easter' : .27

},

'11:22' : {

    'intercept' : -37.0324,
    'sunday_date' : 0.0028,
    'week_number' : -0.0342,
    'Guest Pastor' : -0.7625,
    'Executive Pastor' : -0.628,
    'Pastor Joby' : -0.0359,
    'Easter' : 5.7258,
    'BacktoSchool' : 1.0997,
    'Promotion Weekend' : 1.0997,
    'Saturated Sunday' : 2.4291,
    'Christmas' : 2.9245,
    'Kids Projection' : .23,
    'Kids Easter' : .20

},
}


### logo
logo_file = "https://raw.githubusercontent.com/aarmobley/CoE22/main/E22%20Logo.png"
st.image(logo_file, width=150)


with st.sidebar:
    st.markdown("""
                Important Dates: 
                - 08-10-2025 (Promotion Week)  
                - 09-14-2025 (Saturated Sunday)
                - 12-24-2025 (Christmas)
                - 01-04-2026 (Back to School)
                - 04-05-2026 (Easter) 
                
                """)


title = st.title("Mandarin Attendance Projection")

#dates = pd.read_csv(r"C:\Users\aaron\OneDrive\Desktop\python\RegressionDates1.csv")
#dates.info()
#dates.head()
#sunday_dates = dates['date'].tolist()
#num_date = dates['num_date'].tolist()
num_week = [week for _ in range(2) for week in range(1, 53)]
if len(num_week) < 104:
    num_week.append(53)
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


# Function to calculate projection for a given service, pastor, and event
def calculate_projection(service_time, pastor, event, numerical_date, week_number):
    service_options = coefficients[service_time]
    
    weeknum_effect = service_options['week_number'] * week_number
    sundaydate_effect = service_options['sunday_date'] * numerical_date
    
    # Handle pastor and event coefficients
    pastor_coeff = 0
    event_coeff = 0
    
    if event != 'None':
        event_coeff = service_options[event]
    else:
        pastor_coeff = service_options[pastor]
    
    prediction = ((service_options['intercept']) + (sundaydate_effect) + (weeknum_effect) + (pastor_coeff) + event_coeff)
    prediction_squared = prediction ** 2
    
    # Calculate kids attendance
    kids_attendance = prediction_squared * service_options['Kids Projection']
    if event == 'Easter':
        kids_attendance = prediction_squared * service_options['Kids Easter']
    
    # Calculate capacities
    adult_capacity = prediction_squared / 840 * 100
    kids_capacity = kids_attendance / 330 * 100
    
    return {
        'adult_attendance': prediction_squared,
        'kids_attendance': kids_attendance,
        'adult_capacity': adult_capacity,
        'kids_capacity': kids_capacity
    }


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
        
    color = "red" if capacity > 70 else "blue"
    st.markdown(f"<p style='color:{color}; font-size:18px;'>Worship Center Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)
    
    st.divider()
    
    
    #kids projections with Easter
    if select_event == 'Easter':
        st.write(f"Projected Kids Attendance: {kids_easter: .0f}")
        color = "red" if kids_easter_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_easter_capacity:.0f}%</p>", unsafe_allow_html=True)
    else:
        st.write(f"Projected Kids Attendance: {kids: .0f}")
        
        color = "red" if kids_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_capacity:.0f}%</p>", unsafe_allow_html=True)


# Generate All Services to CSV button
st.divider()
st.subheader("Generate All Services Report")
st.write(f"Current settings: {selected_date_str}, {select_pastor}, {select_event}")

if st.button("Generate All Services to CSV"):
    # Create data for current date and settings, all service times
    all_data = []
    
    # Use only the currently selected date and settings
    for service in service_times:
        projection_data = calculate_projection(service, select_pastor, select_event, numerical_date, select_week)
        
        all_data.append({
            'Date': selected_date_str,
            'Week_Number': select_week,
            'Service_Time': service,
            'Pastor': select_pastor,
            'Event': select_event,
            'Adult_Attendance': round(projection_data['adult_attendance'], 0),
            'Kids_Attendance': round(projection_data['kids_attendance'], 0),
            'Adult_Capacity_Percent': round(projection_data['adult_capacity'], 1),
            'Kids_Capacity_Percent': round(projection_data['kids_capacity'], 1),
            'Total_Attendance': round(projection_data['adult_attendance'] + projection_data['kids_attendance'], 0)
        })
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Convert to CSV
    csv = df.to_csv(index=False)
    
    # Create download button
    st.download_button(
        label="Download CSV Report",
        data=csv,
        file_name=f"mandarin_projections_{selected_date_str.replace('-', '')}_{select_pastor.replace(' ', '_')}_{select_event}_{datetime.now().strftime('%H%M%S')}.csv",
        mime="text/csv"
    )
    
    st.success(f"Generated {len(df)} projection records for {selected_date_str} using current settings!")
    
    # Show preview of the data
    st.subheader("Preview of Generated Data")
    st.dataframe(df)
