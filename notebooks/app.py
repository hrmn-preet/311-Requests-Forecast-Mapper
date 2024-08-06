import streamlit as st

# Title for the app
st.title('311 Requests Dynamic Map')

# Path to the GIF file 
gif_path = 'notebooks/Dynamic_311_Requests.gif'

# Slider to select a date range (optional)
st.sidebar.header('Filters')
start_date = st.sidebar.date_input('Start Date', value=None)
end_date = st.sidebar.date_input('End Date', value=None)

# Display selected date range
if start_date and end_date:
    st.sidebar.write(f'Selected Date Range: {start_date} to {end_date}')
else:
    st.sidebar.write('No date range selected')

# Option to select a date
date = st.sidebar.selectbox('Select a Date', ['2019-01-01', '2019-01-02', '2019-01-03'])

# Button to refresh GIF (simulate refreshing behavior)
if st.sidebar.button('Refresh GIF'):
    st.sidebar.write('Refreshing GIF...')  # Optionally display a message or perform other actions

# Display the GIF file
st.image(gif_path, use_column_width=True)
