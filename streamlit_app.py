import streamlit as st
import altair as alt
import pandas as pd
from wordcloud import WordCloud

# Function to load and return the datasets
def load_data():
    # Load the datasets here. Update the file paths as needed.
    data = pd.read_csv('2022_Motor_Vehicle_Collisions_-_Crashes.csv')
   
    return data

# Function for Hourly Trend Chart
def create_hour_chart(data):
    # Convert 'CRASH TIME' to datetime and extract hour
    data['CRASH TIME'] = pd.to_datetime(data['CRASH TIME'], format='%H:%M').dt.hour
    

    hour_chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('CRASH TIME:O', axis=alt.Axis(title='Time of Day')),
        y=alt.Y('count():Q', axis=alt.Axis(title='Number of Incidents')),
        tooltip=['CRASH TIME', 'count()']
    ).properties(
        title='Incidents by Hour of the Day'
    )

    return hour_chart

# Function for Hourly Trend Chart
def create_day_chart(data):
    # Convert 'CRASH DATE' to datetime specifying the format
    data['CRASH DATE'] = pd.to_datetime(data['CRASH DATE'])
    data['DayOfWeek'] = data['CRASH DATE'].dt.day_name()
    data['Month'] = data['CRASH DATE'].dt.month_name()
    

    day_chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('DayOfWeek:O', axis=alt.Axis(title='Day of the Week')),
        y=alt.Y('count():Q', axis=alt.Axis(title='Total Incidents')),
        tooltip=['DayOfWeek', 'count()']
    ).properties(
        title='Incidents by Day of the Week'
    )

    return day_chart

# Function for Injury Chart
def create_injury_chart(data):
    
    injury_chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('sum(NUMBER OF PERSONS INJURED):Q', axis=alt.Axis(title='Total Number of Injuries')),
        y=alt.Y('BOROUGH:N', axis=alt.Axis(title='Borough')),
        color='BOROUGH:N',
        tooltip=['BOROUGH', 'sum(NUMBER OF PERSONS INJURED)']
    ).properties(
        title='Injury Counts by Borough'
    )

    return injury_chart

# Function for Injury Chart
def create_borough_chart(data):
    
    # Borough Counts
    borough_chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('count():Q', axis=alt.Axis(title='Incident Count')),
        y=alt.Y('BOROUGH:N', axis=alt.Axis(title='Borough')),
        color='BOROUGH:N',
        tooltip=['BOROUGH', 'count()']
    ).properties(
        title='Incident Counts by Borough'
    )

    return borough_chart

# Function for Heatmap
def create_heatmap(data):
    
    # Filter the data 
    data = data.dropna(subset=['VEHICLE TYPE CODE 1'])
    data = data[data['NUMBER OF PERSONS INJURED'] > 0]

    # Aggregate data by vehicle type and borough
    heatmap_data = data.groupby(['VEHICLE TYPE CODE 1', 'BOROUGH']).size().reset_index(name='Incidents')

    # Filter out rows with incident counts less than or equal to 5
    heatmap_data = heatmap_data[heatmap_data['Incidents'] > 5]

    # Create the heatmap
    heatmap = alt.Chart(heatmap_data).mark_rect().encode(
        x=alt.X('BOROUGH:N', axis=alt.Axis(title='Borough')),
        y=alt.Y('VEHICLE TYPE CODE 1:N', axis=alt.Axis(title='Vehicle Type')),
        color=alt.Color('Incidents:Q', scale=alt.Scale(scheme='greenblue'), legend=alt.Legend(title="Number of Incidents")),
        tooltip=['BOROUGH', 'VEHICLE TYPE CODE 1', 'Incidents']
    ).properties(
        title='Heatmap of Incidents by Vehicle Type and Borough'
    )
    
    return heatmap

# Function for Word Cloud
def create_word_cloud(data):
    # Combine all contributing factor columns into a single string
    contributing_factors = data[['CONTRIBUTING FACTOR VEHICLE 1', 'CONTRIBUTING FACTOR VEHICLE 2']].fillna('').agg(' '.join, axis=1)

    # Generate the word cloud
    wordcloud = WordCloud(width = 800, height = 800, 
                    background_color ='white', 
                    stopwords = set(), 
                    min_font_size = 10).generate(' '.join(contributing_factors))

    # Save the word cloud to a file
    wordcloud_file_path = 'word_cloud.png'
    wordcloud.to_file(wordcloud_file_path)

    return wordcloud_file_path

def main():
    st.title("NYC Motor Vehicle Collisions Visualizations")

    # Load the data
    data = load_data()

    # Create a multi-select widget for borough selection
    selected_boroughs = st.multiselect('Select Boroughs', options=data['BOROUGH'].unique())

    # Filter data based on selected boroughs
    if selected_boroughs:
        filtered_data = data[data['BOROUGH'].isin(selected_boroughs)]
    else:
        filtered_data = data

    # Create and display charts using filtered data
    hour_chart = create_hour_chart(filtered_data)
    st.altair_chart(hour_chart, use_container_width=True)

    day_chart = create_day_chart(filtered_data)
    st.altair_chart(day_chart, use_container_width=True)

    injury_chart = create_injury_chart(filtered_data)
    st.altair_chart(injury_chart, use_container_width=True)

    borough_chart = create_borough_chart(filtered_data)
    st.altair_chart(borough_chart, use_container_width=True)

    heatmap = create_heatmap(filtered_data)
    st.altair_chart(heatmap, use_container_width=True)

    # Word Cloud
    wordcloud_file_path = create_word_cloud(filtered_data)
    st.image(wordcloud_file_path, caption='Word Cloud', use_column_width=True)

if __name__ == "__main__":
    main()

