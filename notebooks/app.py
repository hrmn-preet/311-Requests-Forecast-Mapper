import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
from textwrap import wrap

# Streamlit file uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load the data into a DataFrame
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        data = pd.read_excel(uploaded_file)
    
    st.write("Data Loaded:")
    st.dataframe(data.head())

    # Your data processing and visualization code here

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


# User selection
st.sidebar.title("Select Visualization")
option = st.sidebar.selectbox("Choose a plot", ["KDE Plot by Month", "KDE Plot by Day", "Source Type Distribution", "Top Neighbourhoods", "Requests by Business Unit", "Request Status Distribution"])

if option == "KDE Plot by Month":
    # Create KDE plot for requests by month
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(25, 7)) 

    # Define a color palette for the years
    palette = sns.color_palette("husl", len(data['Request Year'].unique()))

    # Plot KDE for each year
    for year in data['Request Year'].unique():
        subset = data[data['Request Year'] == year]
        sns.kdeplot(ax=axs[0], data=subset, x='Request Month', weights=subset['Count'], label=year, shade=True)

    # Title and labels
    axs[0].set_title('KDE Plot of Requests per Month')
    axs[0].set_xlabel('Request Month')
    axs[0].set_ylabel('Density')
    axs[0].grid(True)
    axs[0].set_xticks(range(1, 13)) 
    axs[0].legend(title='Request Year', bbox_to_anchor=(1, 1), loc='upper left')

    # Plot Barplot for each year
    sns.barplot(data=data, x='Request Year', y='Count', hue='Request Month', ax=axs[1])
    axs[1].set_title('Bar Plot of Requests per Month')
    axs[1].set_xlabel('Request Year')
    axs[1].set_ylabel('Count')
    axs[1].grid(True)
    axs[1].legend(title='Request Month', bbox_to_anchor=(1, 1), loc='upper left')

    plt.tight_layout()
    st.pyplot(fig)

elif option == "KDE Plot by Day":
    # Create KDE plot for requests by day
    plt.figure(figsize=(20, 4))
    for year in data['Request Year'].unique():
        subset = data[data['Request Year'] == year]
        sns.kdeplot(data=subset, x='Request Day', weights=subset['Count'], label=year, shade=True)

    plt.title('KDE of Requests per Day for Each Year')
    plt.xlabel('Request Day')
    plt.ylabel('Density')
    plt.legend(title='Request Year', bbox_to_anchor=(0.92, 1), loc='upper left')
    plt.xticks(range(1, 32))  # Days of the month (1-31)
    plt.grid(axis='y')

    plt.tight_layout()
    st.pyplot(plt)

elif option == "Source Type Distribution":
    # Source Type Distribution
    sns.countplot(data=data, x='Ticket Source', orient='h')
    plt.title('Distribution of Ticket Source')
    plt.xlabel('Count')
    plt.ylabel('Ticket Source')
    plt.grid(True)

    st.pyplot(plt)

elif option == "Top Neighbourhoods":
    # Top 20 Neighbourhoods
    top_neighbourhoods = data['Neighbourhood'].value_counts().head(20)

    plt.figure(figsize=(15, 6))
    sns.barplot(y=top_neighbourhoods.index, x=top_neighbourhoods.values, palette='plasma', orient='h')
    plt.xticks(rotation=40)
    plt.title('Top 20 Neighbourhoods by Number of Requests')
    plt.xlabel('Count')
    plt.ylabel('Neighbourhood')
    plt.grid(True)

    st.pyplot(plt)

elif option == "Requests by Business Unit":
    # Requests by Business Unit
    plt.figure(figsize=(20, 3))
    sns.countplot(data=data, x='Business Unit', order=data['Business Unit'].value_counts().index)
    plt.title('Count of Requests by Business Unit')
    plt.xlabel('Count')
    plt.ylabel('Business Unit')
    plt.xticks(rotation=75)
    plt.yticks()
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    st.pyplot(plt)

elif option == "Request Status Distribution":
    # Request Status Distribution
    status_counts = data['Request Status'].value_counts()

    plt.figure(figsize=(4, 4))
    plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title('Distribution of Request Status')

    st.pyplot(plt)
