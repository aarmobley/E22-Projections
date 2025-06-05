##########San Pablo PROJECTIONS 9:00 and 11:22

import pandas as pd
import numpy as np
import streamlit as st
import openpyxl
from datetime import datetime, timedelta


    

coefficients = {

 '7:22': {
        'intercept' : -128.6394,
        'sunday_date' : 0.0087,
        'week_number' : -0.067,
        'Guest Pastor' : -1.856,
        'Executive Pastor' : -1.1375,
        'Pastor Joby' : -1.1643,
        'Easter' :  8.5637,
        'Promotion Week' : 1.52663,
        'Back to School' : 1.8641,
        'Saturated Sunday' :  13.8692,
        'kids_projection' : .08,
        'kids_easter' : .08,
        'Christmas' : 6.2412
    },
    
    
    
  '09:00:00': {
        'intercept' : -179.262118,
        'sunday_date' : 0.011448, 
        'week_number' : -0.006540,
        'Guest Pastor' : -1.275874,
        'Executive Pastor' :  -0.510051,
        'Pastor Joby' : 1.122999,
        'Easter' : 14.028790,
       	'Promotion Week' : 0.332188,
        'Back to School' : 1.276608,
        'Saturated Sunday' : 7.142149,
        'kids_projection' : 0.20,
        'kids_easter' : .12,
        'Christmas' : 4.326568
        

    },
    
   '11:22:00': {                     ##### updated 02/24/25

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
        'Christmas' : 9.5353,
        'Inclement Weather' : .15
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
                - 04-20-2025 (Easter) 
                
                *Choose Inclement Weather if the weather will effect attendance""")

title = st.title("San Pablo Attendance Projection")

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
service_times = list(coefficients.keys()) + ["Elder Led Prayer", "All Services"]   #### LEFT OFF HERE


##create dates for 2 year projection
start_date = datetime(2025, 1, 5)  # Start date
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

#### predict button formula - moved here so both buttons can access it
numerical_date = date_mapping[selected_date_str]

# Add button for generating all services CSV without running projections
st.divider()
if st.button("Generate All Services CSV (7:22, 9:00, 11:22)"):
    all_services_data = []
    
    # Loop through the three main services
    for service_time in ['7:22', '09:00:00', '11:22:00']:
        service_options = coefficients[service_time]
        weeknum_effect = service_options['week_number'] * select_week
        sundaydate_effect = service_options['sunday_date'] * numerical_date
        no_event = 0
        pastor = 0
        
        if select_event != 'None':
            no_event = service_options.get(select_event, 0)
        else:
            pastor = service_options.get(select_pastor, 0)

        # Calculate prediction for the service
        prediction = ((service_options['intercept']) + sundaydate_effect + weeknum_effect + pastor + no_event)
        prediction1 = prediction ** 2
        
        # Handle inclement weather adjustment
        if select_event == 'Inclement Weather':
            final_adult_attendance = prediction1 - (prediction1 * 0.15)
        else:
            final_adult_attendance = prediction1
            
        # Calculate kids attendance (Easter vs regular)
        if select_event == 'Easter':
            kids_attendance = prediction1 * service_options['kids_easter']
        else:
            kids_attendance = prediction1 * service_options['kids_projection']
        
        # Calculate capacities
        adult_capacity = (final_adult_attendance / 3001) * 100
        kids_capacity = (kids_attendance / 750) * 100
        
        # Store the data
        all_services_data.append({
            'Service': service_time,
            'Date': selected_date_str,
            'Week': select_week,
            'Pastor': select_pastor,
            'Event': select_event,
            'Adult_Attendance': round(final_adult_attendance, 0),
            'Kids_Attendance': round(kids_attendance, 0),
            'Adult_Capacity_Percent': round(adult_capacity, 1),
            'Kids_Capacity_Percent': round(kids_capacity, 1)
        })
    
    # Create DataFrame and CSV
    df_all_three = pd.DataFrame(all_services_data)
    
    # Add totals row
    total_adults = sum(row['Adult_Attendance'] for row in all_services_data)
    total_kids = sum(row['Kids_Attendance'] for row in all_services_data)
    
    totals_row = pd.DataFrame({
        'Service': ['TOTAL'],
        'Date': [selected_date_str],
        'Week': [select_week],
        'Pastor': [select_pastor],
        'Event': [select_event],
        'Adult_Attendance': [total_adults],
        'Kids_Attendance': [total_kids],
        'Adult_Capacity_Percent': ['N/A'],
        'Kids_Capacity_Percent': ['N/A']
    })
    
    df_final = pd.concat([df_all_three, totals_row], ignore_index=True)
    
    # Create CSV with header
    csv_data = f"# San Pablo Attendance Projections - All Three Services\n"
    csv_data += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    csv_data += f"# Parameters: Date={selected_date_str}, Week={select_week}, Pastor={select_pastor}, Event={select_event}\n\n"
    csv_data += df_final.to_csv(index=False)
    
    st.success(f"CSV generated for all three services! Total projected attendance: {total_adults} adults, {total_kids} kids")
    
    st.download_button(
        label="📥 Download All Three Services CSV",
        data=csv_data,
        file_name=f"San_Pablo_All_Three_Services_{selected_date_str.replace('-', '_')}.csv",
        mime="text/csv"
    )



#### ATTENDANCE PREDICTION

#### predict button formula - moved here so both buttons can access it
numerical_date = date_mapping[selected_date_str]




#### updating attendance if prediciton is not accurate
#if select_service == "11:22:00":
    #number = st.number_input("Previous Service Attendance", value=0.0, placeholder= "Enter Attendance")

    #updated = number - (number * .22) 
    #st.write("Updated Attendance is", updated)

    


####predict button for all services selected

if st.button("Make Projection"):
    if select_service == "All Services":
        total_prediction = 0  #
        service_details = []  # Store individual service data for CSV
        
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
            service_prediction = prediction ** 2
            total_prediction += service_prediction
            
            # Store service details for CSV
            service_details.append({
                'Service': service,
                'Adult_Attendance': round(service_prediction, 0),
                'Kids_Attendance': round(service_prediction * service_options['kids_projection'], 0),
                'Adult_Capacity_Percent': round((service_prediction / 3001) * 100, 0),
                'Kids_Capacity_Percent': round((service_prediction * service_options['kids_projection'] / 750) * 100, 0)
            })

        # Display the total for all services
        st.divider()
        st.write(f"Projected Total Attendance - Adults (All Services): {total_prediction:.0f}")
        
        # Add CSV export for All Services
        st.divider()
        df_all_services = pd.DataFrame(service_details)
        # Add summary row
        summary_row = pd.DataFrame({
            'Service': ['TOTAL'],
            'Adult_Attendance': [round(total_prediction, 0)],
            'Kids_Attendance': [round(sum(row['Kids_Attendance'] for row in service_details), 0)],
            'Adult_Capacity_Percent': ['N/A'],
            'Kids_Capacity_Percent': ['N/A']
        })
        df_all_services = pd.concat([df_all_services, summary_row], ignore_index=True)
        
        # Add metadata
        metadata_df = pd.DataFrame({
            'Parameter': ['Date', 'Week', 'Pastor', 'Event'],
            'Value': [selected_date_str, select_week, select_pastor, select_event]
        })
        
        csv_data = f"# San Pablo Attendance Projections - All Services\n# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        csv_data += "## Projection Parameters\n"
        csv_data += metadata_df.to_csv(index=False)
        csv_data += "\n## Service Projections\n"
        csv_data += df_all_services.to_csv(index=False)
        
        st.download_button(
            label="📥 Download All Services Projections (CSV)",
            data=csv_data,
            file_name=f"San_Pablo_All_Services_{selected_date_str.replace('-', '_')}.csv",
            mime="text/csv"
        )
        
    elif select_service == "Elder Led Prayer":
        # Using 9:00 service calculation and reducing by 80%
        service_options = coefficients['09:00:00']
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

        ####start of edited code
        elder_prayer_prediction = prediction1 * 0.2  # 20% of the 9:00 service (80% reduction)
        
        st.divider()
        st.write(f"Projected Adult Attendance: {elder_prayer_prediction:.0f}")
        
        # Calculate capacity (using same capacity as 9:00)
        capacity = elder_prayer_prediction / 3001 * (100)
        color = "red" if capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Worship Center Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)
        
        # Kid's calculation for Elder Prayer service
        kids_attendance = elder_prayer_prediction * service_options['kids_projection']
        kids_capacity = kids_attendance / 750 * (100)
        
        st.divider()
        st.write(f"Projected Kids Attendance: {kids_attendance:.0f}")
        color = "red" if kids_capacity > 80 else "blue"
        st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_capacity:.0f}%</p>", unsafe_allow_html=True)
        
        # Add CSV export for Elder Prayer
        st.divider()
        elder_data = {
            'Parameter': ['Date', 'Week', 'Pastor', 'Event', 'Service', 'Adult_Attendance', 'Kids_Attendance', 'Adult_Capacity_Percent', 'Kids_Capacity_Percent'],
            'Value': [selected_date_str, select_week, select_pastor, select_event, 'Elder Led Prayer', 
                     round(elder_prayer_prediction, 0), round(kids_attendance, 0), 
                     round(capacity, 0), round(kids_capacity, 0)]
        }
        df_elder = pd.DataFrame(elder_data)
        
        csv_data = f"# San Pablo Attendance Projections - Elder Led Prayer\n# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        csv_data += df_elder.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Elder Prayer Projection (CSV)",
            data=csv_data,
            file_name=f"San_Pablo_Elder_Prayer_{selected_date_str.replace('-', '_')}.csv",
            mime="text/csv"
        )
        
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
        ###end of edited code
    
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
            st.markdown(f"<p style='color:{color}; font-size:18px;'>Worship Center Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True) 
        else:    
            st.write(f"Projected Adult Attendance: {inclement_weather:.0f}")
            
            color = "red" if capacity > 70 else "blue"
            st.markdown(f"<p style='color:{color}; font-size:18px;'>Worship Center Capacity: {capacity:.0f}%</p>", unsafe_allow_html=True)
    
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
        
        # Add CSV export for individual service
        st.divider()
        
        # Determine which attendance values to use based on event and weather
        final_adult_attendance = inclement_weather if select_event == 'Inclement Weather' else prediction1
        final_kids_attendance = kids_easter if select_event == 'Easter' else kids_1122
        final_kids_capacity = kids_easter_capacity if select_event == 'Easter' else kids_capacity
        
        service_data = {
            'Parameter': ['Date', 'Week', 'Pastor', 'Event', 'Service', 'Adult_Attendance', 'Kids_Attendance', 'Adult_Capacity_Percent', 'Kids_Capacity_Percent'],
            'Value': [selected_date_str, select_week, select_pastor, select_event, select_service,
                     round(final_adult_attendance, 0), round(final_kids_attendance, 0),
                     round(capacity, 0), round(final_kids_capacity, 0)]
        }
        df_service = pd.DataFrame(service_data)
        
        csv_data = f"# San Pablo Attendance Projections - {select_service}\n# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        csv_data += df_service.to_csv(index=False)
        
        st.download_button(
            label=f"📥 Download {select_service} Projection (CSV)",
            data=csv_data,
            file_name=f"San_Pablo_{select_service.replace(':', '_')}_{selected_date_str.replace('-', '_')}.csv",
            mime="text/csv"
        )
        
        
        
    ## HTML and markdown for kids capacity
   # color = "red" if kids_capacity > 80 else "blue"
    #st.markdown(f"<p style='color:{color}; font-size:18px;'>Capacity: {kids_capacity:.0f}%</p>", unsafe_allow_html=True)
    

    ### side bar button to list important dates like easter, christmas, promotion weekend
    
    ### Have a Week total - and each service have a percent of the total
    
    ###Disciple Group projection based off of the weekly total
    
    ###Disciple Group Total vs. goal based on projection
    
    
