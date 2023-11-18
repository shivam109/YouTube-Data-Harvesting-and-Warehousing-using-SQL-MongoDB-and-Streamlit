# Import necessary Python packages
import pandas as pd
from googleapiclient.discovery import build
import datetime
import pymongo
import mysql.connector
import streamlit as st

st.set_page_config(
    page_title="YouTube-App",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
   
)


# Set Streamlit page configuration
#st.set_page_config(page_title="YouTube-App", layout="wide")

# Define your YouTube API key for authentication
api_key = "AIzaSyBSj30rdwS2yna3qIK1d11INlh7zqVKAwY"

# Initialize the YouTube API client with the chosen API key
youtube = build('youtube', 'v3', developerKey=api_key)

# Function to retrieve channel data using the YouTube Data API
def retrieve_channel_data(channel_id):
    # Initialize an empty list to store channel data
    channel_data = []
    # Create a request to fetch channel details
    request = youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=channel_id)
    # Execute the request and obtain the response
    response = request.execute()
    # Extract and format channel information
    for item in response.get('items', []):
        data = {'Channel_ID': item['id'],
                'Channel_Name': item['snippet']['title'],
                'Subscriber_Count': item['statistics']['subscriberCount'],
                'Channel_Views': item['statistics']['viewCount'],
                'Channel_Description': item['snippet']['description'],
                'Upload_ID': item['contentDetails']['relatedPlaylists']['uploads']}
        channel_data.append(data)
    return channel_data

# Function to retrieve playlist data from a YouTube channel
def retrieve_playlist_data(channel_id):
    # Initialize an empty list to store playlists data
    playlists_data = []
    # Initialize request to fetch playlist details
    request = youtube.playlists().list(
        part="snippet,contentDetails",
        channelId=channel_id,
        maxResults=50)
    # Execute the request and obtain the response
    response = request.execute()
    # Get the total number of playlists
    total_playlists = response.get('pageInfo', {}).get('totalResults', 0)
    print(f"Total Playlists: {total_playlists}")
    # Check if there are no playlists in this channel
    if total_playlists == 0:
        print("There are no playlists in this channel.")
    else:
        # Continue fetching playlists until there are no more pages
        while response['items']:
            # Iterate through items in the response and extract playlist data
            for item in response['items']:
                data = {'Playlist_ID': item['id'],
                        'Playlist_Title': item['snippet']['title'],
                        'Playlist_Description': item['snippet']['description'],
                        'Playlist_Item_Count': item['contentDetails']['itemCount'],
                        'Channel_ID': channel_id}
                playlists_data.append(data)
            # Get the next page token for the next iteration
            next_page_token = response.get('nextPageToken')
            # Fetch the next page of results if available
            if next_page_token:
                request = youtube.playlists().list(
                    part="snippet,contentDetails",
                    channelId=channel_id,
                    maxResults=50,
                    pageToken=next_page_token)
                response = request.execute()
            else:
                # Break the loop if there are no more pages
                break
    return playlists_data

# Function to retrieve video IDs from a YouTube channel
def retrieve_video_ids(channel_id):
    # Initialize an empty list to store video IDs
    video_ids = []
    # Initialize a variable to store the next page token
    next_page_token = None
    # Continue fetching video IDs until there are no more pages
    while True:
        # Create a request to fetch video IDs
        request = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=50,
            type="video",
            pageToken=next_page_token)
        response = request.execute()
        # Iterate through items in the response and extract video IDs
        for item in response.get("items", []):
            # Check if "videoId" key exists before accessing it
            if "videoId" in item.get("id", {}):
                video_ids.append(item["id"]["videoId"])
        # Update the next page token for the next iteration
        next_page_token = response.get("nextPageToken")
        # Break the loop if there are no more pages
        if not next_page_token:
            break
    return video_ids

# Function to retrieve video data from YouTube for a list of video IDs
def retrieve_video_data(video_ids, upload_id):
    # Initialize an empty list to store videos data
    videos_data = []
    # Iterate through video IDs in batches of 50
    for i in range(0, len(video_ids), 50):
        batch_video_ids = video_ids[i:i + 50]
        # Create a request to fetch video data for the batch of video IDs
        request = youtube.videos().list(
            part='contentDetails, snippet, statistics',
            id=','.join(batch_video_ids))
        response = request.execute()
        # Function to format video duration
        def time_duration(t):
            a = pd.Timedelta(t)
            b = str(a).split()[-1]
            return b
        # Iterate through each video item in the response
        for item in response['items']:
            # Extract relevant video information and create a dictionary
            data = {'Video_ID': item['id'],
                    'Video_Name': item['snippet']['title'],
                    'Video_Description': item['snippet']['description'],
                    'Tags': item['snippet'].get('tags', []),  # Check if tags exist
                    'Published_Date': item['snippet']['publishedAt'][0:10],
                    'Published_Time': item['snippet']['publishedAt'][11:19],
                    'View_Count': item['statistics'].get('viewCount', 0),
                    'Like_Count': item['statistics'].get('likeCount', 0), 
                    'Favorite_Count': item['statistics']['favoriteCount'],
                    'Comment_Count': item['statistics'].get('commentCount', 0),  
                    'Duration': time_duration(item['contentDetails']['duration']),
                    'Thumbnail': item['snippet']['thumbnails']['default']['url'],
                    'Caption_Status': item['contentDetails']['caption'],
                    'Upload_ID': upload_id}
            # Append the video data to the videos_data list
            videos_data.append(data)
    return videos_data

# Function to retrieve comments data for a list of video IDs
def retrieve_comments_data(video_ids):
    # Initialize an empty list to store comments data
    comments_data = [] 
    try:
        # Iterate through each video ID in the provided list
        for video_id in video_ids:
            # Create a request to fetch comment threads for the video
            request = youtube.commentThreads().list(
                part='id, snippet',
                videoId=video_id,
                maxResults=85)
            response = request.execute()
            # Check if there are items (comments) in the response
            if 'items' in response:
                # Iterate through each comment in the response
                for item in response['items']:
                    # Extract relevant comment information and create a dictionary
                    data = {'Comment_ID': item['id'],
                            'Comment_Text': item['snippet']['topLevelComment']['snippet']['textDisplay'],
                            'Comment_Author': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            'Comment_Published_Date': item['snippet']['topLevelComment']['snippet']['publishedAt'][0:10],
                            'Comment_Published_Time': item['snippet']['topLevelComment']['snippet']['publishedAt'][11:19],
                            'Video_ID': video_id}
                    # Append the comment data to the comments_data list
                    comments_data.append(data)
    except:
        pass
    return comments_data

# Function to combine data for a YouTube channel
def combine_data(channel_id):
    # Retrieve channel data
    channel_data = retrieve_channel_data(channel_id)
    # Retrieve playlist data
    playlist_data = retrieve_playlist_data(channel_id)
    # Retrieve video IDs for the channel
    video_ids = retrieve_video_ids(channel_id)
    # Retrieve video data for the video IDs and upload ID from channel data
    video_data = retrieve_video_data(video_ids, channel_data[0]['Upload_ID'])
    # Retrieve comments data for the video IDs and insert it inside the video data
    comments_data = retrieve_comments_data(video_ids)
    # Create a dictionary to store combined data
    combined_data = {'Channel_Details': channel_data,
                     'Playlists': playlist_data,
                     'Video_Details': video_data,
                     'Comments': comments_data}
    # Store all extracted data in a variable
    all_data_extracted = combined_data
    return combined_data

# MongoDB connection configuration
mongo_url = "mongodb://localhost:27017/"
database_name = "youtube_db"

# Function to get a MongoDB collection
def get_mongodb_collection(collection_name):
    client = pymongo.MongoClient(mongo_url)
    db = client[database_name]
    return db[collection_name] 
    
# Function to save data to a MongoDB collection
def save_data_to_mongodb(collection_name, combined_data):
    collection = get_mongodb_collection(collection_name)
    collection.insert_one(combined_data)
    
# Function to check if a collection exists
def collection_exists(collection_name):
    client = pymongo.MongoClient(mongo_url)
    db = client[database_name]
    existing_collections = db.list_collection_names()
    return collection_name in existing_collections
    
# Function to store data in MongoDB
def store_data_in_mongodb(channel_name, combined_data):
    if collection_exists(channel_name):
        collection = get_mongodb_collection(channel_name)
        collection.drop()
        save_data_to_mongodb(channel_name, combined_data)
        st.success(f"Collection '{channel_name}' already exists, and the existing data has been overwritten.")
    else:
        save_data_to_mongodb(channel_name, combined_data)
        st.success(f"Data has been successfully stored in the MongoDB collection '{channel_name}'.")
        
# Function to fetch data from MongoDB
def fetch_data_from_mongodb(collection_name):
    collection = get_mongodb_collection(collection_name)
    # Fetch data from the collection
    fetched_data = collection.find_one() 
    return fetched_data
    
# Function to list existing MongoDB collections
def list_mongo_collections(mongo_url, database_name):
    client = pymongo.MongoClient(mongo_url)
    db = client[database_name]
    existing_collections = db.list_collection_names()
    existing_collections = sorted(existing_collections)
    for i, collection_name in enumerate(existing_collections, 1):
        st.write(f"{i}. {collection_name}")
    return existing_collections

# Establish a connection to the MySQL database
mysqldb = mysql.connector.connect(
    host="localhost",      		# Specify the MySQL server host (usually the local machine)
    user="root",           		# MySQL username for authentication
    password="Shivam@2000",        		# Password for the MySQL user           		
    database="shivam"    # Name of the MySQL database 
    )

# Create a cursor object for MySQL operations
mycursor = mysqldb.cursor(buffered=True)

# Function to create tables in the MySQL database
def create_tables(mycursor):
    # Create the 'Channels' table
    mycursor.execute("""CREATE TABLE IF NOT EXISTS Channels (
        Channel_ID VARCHAR(255),
        Channel_Name VARCHAR(255),
        Subscriber_Count INT,
        Channel_Views BIGINT,
        Channel_Description TEXT,
        Upload_ID VARCHAR(255)
    )""")
    # Create the 'Playlists' table
    mycursor.execute("""CREATE TABLE IF NOT EXISTS Playlists (
        Playlist_ID VARCHAR(255),
        Playlist_Title VARCHAR(255),
        Playlist_Description TEXT,
        Playlist_Item_Count INT,
        Channel_ID VARCHAR(255)
    )""")
    # Create the 'Videos' table
    mycursor.execute("""CREATE TABLE IF NOT EXISTS Videos (
        Video_ID VARCHAR(255),
        Video_Name VARCHAR(255),
        Video_Description TEXT,
        Tags TEXT, 
        Published_Date DATE,
        Published_Time TIME,
        View_Count INT,
        Like_Count INT,
        Favorite_Count INT,
        Comment_Count INT,
        Duration TIME,
        Thumbnail VARCHAR(255),
        Caption_Status BOOLEAN,
        Upload_ID VARCHAR(255)
    )""")
    # Create the 'Comments' table
    mycursor.execute("""CREATE TABLE IF NOT EXISTS Comments (
        Comment_ID VARCHAR(255),
        Comment_Text TEXT,
        Comment_Author VARCHAR(255),
        Comment_Published_Date DATE,
        Comment_Published_Time TIME,
        Video_ID VARCHAR(255) 
    )""")
    
# Function to insert values into MySQL tables based on the provided combined data
def insert_values_into_mysql(mycursor, collect_data,selected_channel):
    # Check if any channel in the collect_data already exists
    for channel in collect_data.get('Channel_Details', []):
        channel_id = channel.get('Channel_ID')
        mycursor.execute("SELECT * FROM Channels WHERE Channel_ID = %s", (channel_id,))
        existing_ch_sql = mycursor.fetchone()
        if not existing_ch_sql:
            # Insert Channel Details
            for channel in collect_data.get('Channel_Details', []):
                mycursor.execute("INSERT INTO Channels (Channel_ID, Channel_Name, Subscriber_Count, Channel_Views, Channel_Description, Upload_ID) VALUES (%s, %s, %s, %s, %s, %s)",
                                (channel.get('Channel_ID', 'N/A'), channel.get('Channel_Name', 'N/A'), channel.get('Subscriber_Count', 0),
                                 channel.get('Channel_Views', 0), channel.get('Channel_Description', 'N/A'), channel.get('Upload_ID', 'N/A')))
            # Insert Playlist Details
            for playlist in collect_data.get('Playlists', []):
                mycursor.execute("INSERT INTO Playlists (Playlist_ID, Playlist_Title, Playlist_Description, Playlist_Item_Count, Channel_ID) VALUES (%s, %s, %s, %s, %s)",
                                (playlist.get('Playlist_ID', 'N/A'), playlist.get('Playlist_Title', 'N/A'), playlist.get('Playlist_Description', 'N/A'),
                                 playlist.get('Playlist_Item_Count', 0), playlist.get('Channel_ID', 'N/A')))
            # Insert Video Details
            for video in collect_data.get('Video_Details', []):
                tags = ', '.join(video.get('Tags', [])) if 'Tags' in video else ''
                mycursor.execute("INSERT INTO Videos (Video_ID, Video_Name, Video_Description, Tags, Published_Date, Published_Time, View_Count, Like_Count, Favorite_Count, Comment_Count, Duration, Thumbnail, Caption_Status, Upload_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (video.get('Video_ID', 'N/A'), video.get('Video_Name', 'N/A'), video.get('Video_Description', 'N/A'), tags,
                                 video.get('Published_Date', 'N/A'), video.get('Published_Time', 'N/A'), video.get('View_Count', 0),
                                 video.get('Like_Count', 0), video.get('Favorite_Count', 0), video.get('Comment_Count', 0),
                                 video.get('Duration', '0'), video.get('Thumbnail', 'N/A'), bool(video.get('Caption_Status', False)),
                                 video.get('Upload_ID', 'N/A')))
            # Insert Comments
            for comment in collect_data.get('Comments', []):
                mycursor.execute("INSERT INTO Comments (Comment_ID, Comment_Text, Comment_Author, Comment_Published_Date, Comment_Published_Time, Video_ID) VALUES (%s, %s, %s, %s, %s, %s)",
                                (comment.get('Comment_ID', 'N/A'), comment.get('Comment_Text', 'N/A'), comment.get('Comment_Author', 'N/A'),
                                 comment.get('Comment_Published_Date', 'N/A'), comment.get('Comment_Published_Time', 'N/A'), comment.get('Video_ID', 'N/A')))
            st.success('Data migration to SQL database is completed successfully.')
        else:
            st.info(f"Channel {selected_channel} already exists in the database. Not inserting again.")
            
# Define a function for data migration
def migrate_data_to_sql(mycursor,collect_data,selected_channel):
    create_tables(mycursor)
    insert_values_into_mysql(mycursor, collect_data,selected_channel)
    mysqldb.commit()  

def perform_data_analysis():
    st.subheader("YouTube Data Analysis")
    client = pymongo.MongoClient(mongo_url)
    db = client[database_name]
    existing_collections = db.list_collection_names()
    selected_channel = st.selectbox("Select a Channel Name", options=existing_collections)
    # Fetch data from MongoDB based on the selected channel
    collect_data = fetch_data_from_mongodb(selected_channel)
    if collect_data:
        st.write(f"Channel: {selected_channel}")
        # Access the relevant data based on the structure of the fetched data
        channel_details = collect_data.get('Channel_Details', [{}])[0]
        playlists = collect_data.get('Playlists', [])
        video_details = collect_data.get('Video_Details', [])
        st.subheader("Channel Metrics")
        # Display metrics in three columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Subscribers", int(channel_details.get("Subscriber_Count", 0)))
        with col2:
            st.metric("Channel Views", int(channel_details.get("Channel_Views", 0)))
        with col3:
            st.metric("Playlists Count", len(playlists))
        
        # Display Top 5 Playlists
        st.subheader("Top 5 Playlists")
        try:
            top_playlists = sorted(playlists, key=lambda x: x.get("Playlist_Item_Count", 0), reverse=True)[:5]
            top_playlists_df = pd.DataFrame(top_playlists)[['Playlist_Title', 'Playlist_Item_Count']]
            top_playlists_df.index = range(1, len(top_playlists_df) + 1)
            st.dataframe(top_playlists_df)
        except:
            # Handle the case when 'playlists' is not defined
            st.write("No playlists exist in the channel")
        
        if video_details:
            # Calculate statistics for video_details
            total_videos = len(video_details)
            total_likes = sum(int(video.get("Like_Count", 0)) for video in video_details)
            total_comments = sum(int(video.get("Comment_Count", 0)) for video in video_details)
            average_likes = total_likes / len(video_details)
            average_comments = total_comments / len(video_details)
            st.subheader("Video Statistics")
            col3, col4, col5 = st.columns(3)
            with col3:
                st.metric("Total Videos", total_videos)
            with col4:
                st.metric("Average Likes", int(average_likes))
            with col5:
                st.metric("Average Comments", int(average_comments))
                
            col6, col7 = st.columns(2)
            with col6:
                # Example: Display the top 5 most liked videos in a DataFrame with video name and like count
                top_liked_videos = sorted(video_details, key=lambda x: int(x.get("Like_Count", 0)), reverse=True)[:5]
                top_liked_videos_df = pd.DataFrame(top_liked_videos)[['Video_Name', 'Like_Count']]
                top_liked_videos_df.index = range(1, len(top_liked_videos_df) + 1)
                st.subheader("Top 5 Most Liked Videos")
                st.dataframe(top_liked_videos_df)
            with col7:
                # Example: Display the top 5 most viewed videos in a DataFrame with only video name and views
                top_viewed_videos = sorted(video_details, key=lambda x: int(x.get("View_Count", 0)), reverse=True)[:5]
                top_viewed_videos_df = pd.DataFrame(top_viewed_videos)[['Video_Name', 'View_Count']]
                top_viewed_videos_df.index = range(1, len(top_viewed_videos_df) + 1)
                st.subheader("Top 5 Most Viewed Videos")
                st.dataframe(top_viewed_videos_df)
        else:
            st.warning("No video data available for this channel.")

# Function to execute SQL queries and display results in a DataFrame
def execute_query(query):
    df = pd.read_sql_query(query, mysqldb)
    return df
    
# List of queries
queries = {
    "Query 1: What are the names of all the videos and their corresponding channels?":
        """
        SELECT Videos.Video_Name,Channels.Channel_Name
        FROM Videos
        INNER JOIN Channels ON Videos.Upload_ID = Channels.Upload_ID
        """,
    "Query 2: Which channels have the most no.of Videos and their count?":
        """
        SELECT Channels.Channel_Name, COUNT(Videos.Video_ID) AS Video_Count
        FROM Channels
        INNER JOIN Videos ON Channels.Upload_ID = Videos.Upload_ID
        GROUP BY Channels.Channel_Name
        ORDER BY Video_Count DESC
        """,
    "Query 3: What are the top 10 most viewed videos and their corresponding channels?":
        """
        SELECT Channels.Channel_Name,Videos.Video_Name,Videos.View_Count
        FROM Videos
        INNER JOIN Channels ON Videos.Upload_ID = Channels.Upload_ID
        ORDER BY Videos.View_Count DESC
        LIMIT 10
        """,
    "Query 4: How many no.of comments on each video and their corresponding video names?":
        """
        SELECT Videos.Video_Name,  COUNT(*) AS CommentCount
        FROM Videos
        INNER JOIN Comments ON Videos.Video_ID = Comments.Video_ID
        GROUP BY Videos.Video_Name
        """,
    "Query 5: Which videos have the highest no.of likes and their corresponding channel names?":
        """
        SELECT Channels.Channel_Name,Videos.Video_Name,Videos.Like_Count
        FROM Videos
        INNER JOIN Channels ON Videos.Upload_ID = Channels.Upload_ID
        ORDER BY Videos.Like_Count DESC
        LIMIT 10
        """,
    "Query 6: What is the total no.of likes for each video and their corresponding video names?":
        """
        SELECT Videos.Video_Name, MAX(Videos.Like_Count) AS Total_Likes
        FROM Videos
        GROUP BY Videos.Video_Name
        """,
    "Query 7: What is the total no.of views for each channel and their corresponding channel names?":
        """
        SELECT Channels.Channel_Name, SUM(Videos.View_Count) AS Total_Views
        FROM Channels
        INNER JOIN Videos ON Channels.Upload_ID = Videos.Upload_ID
        GROUP BY Channels.Channel_Name
        """,
    "Query 8: What are the names of all the channels that published videos in the year 2022?":
        """
        SELECT Channels.Channel_Name,Videos.Video_Name
        FROM Channels
        INNER JOIN Videos ON Channels.Upload_ID = Videos.Upload_ID
        WHERE YEAR(Videos.Published_Date) = 2022
        """,
    "Query 9: What is the average duration of all videos in each channel?":
        """
        SELECT Channels.Channel_Name, AVG(TIME_TO_SEC(Videos.Duration)) AS AvgDuration_sec
        FROM Channels
        INNER JOIN Videos ON Channels.Upload_ID = Videos.Upload_ID
        GROUP BY Channels.Channel_Name
        """,
    "Query 10: Which videos have the highest no.of comments and their corresponding channel names?":
        """
        SELECT Channels.Channel_Name,Videos.Video_Name,Videos.Comment_Count
        FROM Videos
        INNER JOIN Channels ON Videos.Upload_ID = Channels.Upload_ID
        ORDER BY Videos.Comment_Count DESC
        """}    

# Function to display information about the project
def display_about_session():
    st.subheader("Project Title:")
    st.subheader("YouTube Data Harvesting and Warehousing using SQL, MongoDB, and Streamlit")
    
    st.subheader("What I've Learned")
    st.markdown("Throughout this project, I've gained valuable skills and knowledge in the following areas:")
    st.markdown("o>>> Python scripting for data extraction and analysis.")
    st.markdown("o>>> Integrating external APIs into the application, such as the YouTube API.")
    st.markdown("o>>> Data collection from the YouTube API.")
    st.markdown("o>>> Storing and managing data using MongoDB, including data lakes.")
    st.markdown("o>>> Data management using MongoDB Atlas for secure and scalable storage.")
    st.markdown("o>>> Setting up SQL databases and data warehousing.")
    st.markdown("o>>> Building interactive and user-friendly web applications with Streamlit.")
    
    st.subheader("What I've Created")
    st.markdown("In this project, I've developed a comprehensive solution that includes the following features:")
    st.markdown("1. A Streamlit application that allows users to input a YouTube channel ID and an API key to retrieve required YouTube data using the YouTube API.")
    st.markdown("2. An option to store the collected data in a MongoDB database as a data lake for flexible storage and retrieval.")
    st.markdown("3. The ability to collect data from different YouTube channels and store them in the data lake.")
    st.markdown("4. A feature to select a channel and migrate its data from the data lake to a SQL database, creating structured tables for efficient data analysis.")
    st.markdown("5. Advanced data retrieval and search capabilities from the SQL database, including the ability to join tables to get detailed channel information.")
    st.markdown("6. A streamlined process that covers data Collection, Storage, Transformation, and Answering 10 specific SQL Queries creating a user-friendly and efficient data warehousing solution.")
    
    st.markdown("Throughout this project, I've acquired some of the basic practical skills and experience that can be applied to real-world scenarios, making it a valuable learning and development experience.")
    st.subheader("Reference Links:")
    st.markdown("- [How to create API Key for YouTube Data API v3](https://youtu.be/F5yQ1BgDIDQ?feature=shared)")
    st.markdown("- [How to Find YouTube Channel ID](https://youtu.be/0oDy2sWPF38?feature=shared)")

# Function to display the options for YouTube Data Harvesting and Warehousing processes
def display_select_process():
    st.subheader("YouTube Data Harvesting and Warehousing Application")
    processes = ['1-Retrieve & Store data in MongoDB', '2-Migrate data to SQL Database', '3-Data Analysis', '4-SQL Queries']
    selected_process = st.selectbox('Please select the option below:', processes)
    st.write(f'You have selected the option {selected_process}')
    
    selected_channel = None  # Initialize with a default value
    
    if selected_process == '1-Retrieve & Store data in MongoDB':
        st.info("If you don't have a YouTube Channel ID or API Key, refer to the 'About Session' section for helpful video guides.")
        channel_id = st.text_input("Enter Channel ID: ", help="Hint: This is the unique identifier for the YouTube channel.")
        api_key ="AIzaSyBSj30rdwS2yna3qIK1d11INlh7zqVKAwY" 
        if api_key: 
            youtube = build('youtube', 'v3', developerKey=api_key)
        else:
            st.warning("API Key is not provided. Please enter your API Key.")
        if st.button('Retrieve & Store data'):
            all_data_extracted = combine_data(channel_id)
            st.success('YouTube data is retrieved successfully')
            st.caption("All the extracted data (JSON):")
            st.json(all_data_extracted)
            collection_name = all_data_extracted["Channel_Details"][0]["Channel_Name"]
            store_data_in_mongodb(collection_name, all_data_extracted)
            
    if selected_process == '2-Migrate data to SQL Database':
        existing_collections = list_mongo_collections(mongo_url, database_name)
        if not existing_collections:
            st.warning("No MongoDB collections found. Please retrieve and store data in MongoDB first.")
        else:
            selected_channel = st.selectbox("Select a Channel Name", options=existing_collections)
            st.write(f"You have selected the channel '{selected_channel}'")
            if collection_exists(selected_channel):
                collect_data = fetch_data_from_mongodb(selected_channel)
                migrate_data_to_sql(mycursor, collect_data, selected_channel)
            else:
                st.error("The MongoDB collection for the selected channel does not exist")
                
    if selected_process == '3-Data Analysis':
        perform_data_analysis()
        
    if selected_process == '4-SQL Queries':
        selected_query = st.selectbox("Select a query", list(queries.keys()))
        query = queries[selected_query]
        result = execute_query(query)
        st.dataframe(result)

# Get user input for page selection
page = st.sidebar.selectbox("Select Page", ["About Session", "Select Process", "Exit"])

# Main section to display different pages
def main():
    if page == "About Session":
        display_about_session()
    elif page == "Select Process":
        display_select_process()
    elif page == "Exit":
        st.subheader("Exit Application")
        st.markdown("Thank you for using the YouTube Data Harvesting and Warehousing application.")
        st.markdown("If you wish to exit, simply close the browser tab or window.")
        st.markdown("Have a great day!")

# Call the main function to display the appropriate content based on the selected page
main()
