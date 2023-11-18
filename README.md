# YouTube Data Harvesting and Warehousing using SQL, MongoDB, and Streamlit

## Introduction
  The YouTube Data Harvesting and Warehousing project is dedicated to creating an intuitive Streamlit application that harnesses the Google API's power to extract valuable information from YouTube channels. 
  This extracted data is then stored in a MongoDB database and seamlessly migrated to a MySQL data warehouse, all within the same user-friendly Streamlit application.

## Table of Contents
1. Key Technologies and Skills
2. Usage
3. Features
4. Data Retrieval from the YouTube API
5. Storing Data in MongoDB
6. Data Migration to a MySQL Data Warehouse
7. Contribution Guidelines

## Key Technologies and Skills
- Python Scripting
- Data Collection
- API Integration
- Streamlit
- Data Management using MongoDB and MySQL

## Usage
To use this project, follow these steps:

  1. Install the required packages: ```pip install -r requirements.txt```
  2. Run the Streamlit app: ```streamlit run app.py```
  3. Open the app in your web browser. You can access it by opening a new tab and entering the following URL: ```http://localhost:8501```

## Features
  - Retrieve data from the YouTube API, including channel information, playlists, videos, and comments.
  - Store the collected data in a MongoDB database.
  - Migrate the data to a MySQL data warehouse.
  - Analyze and visualize data using Streamlit and other Python libraries.
  - Perform queries on the MySQL data warehouse.
  - Gain insights into channel metrics, video metrics, and top 5 data of the respective channel.
  - Answer default 10 queries to provide immediate insights into the data.
  
## Data Retrieval from the YouTube API
  Our project harnesses the power of the Google API to retrieve comprehensive data from YouTube channels. This data encompasses detailed information on channels, playlists, videos, and comments.
  By interacting with the Google API, we gather and consolidate this information into a structured format, laying the foundation for further data processing and analysis.
  
## Storing Data in MongoDB
  The retrieved data is securely stored in a MongoDB database with proper user authorization. In cases where the data already exists in the database, any subsequent attempts to insert the same data will 
  automatically lead to data overwriting. This storage mechanism ensures efficient and updated data management and preservation, simplifying the process of handling the collected data.
  
## Data Migration to a MySQL Data Warehouse
  Our application empowers users to transfer data from MongoDB to a MySQL data warehouse seamlessly. Users can choose the specific channel they want to migrate from the displayed list, enabling a tailored 
  approach to data handling.The data migration process involves transforming and structuring the collected data, ensuring it aligns with the structured format of a MySQL database.Facilitating a seamless 
  transition of data from MongoDB to MySQL for further analysis and insights.
  
## Contribution Guidelines
  Contributions to this project are highly encouraged. If you come across any challenges or have ideas for enhancements, we invite you to submit a pull request. Your input is valuable to us, and we appreciate 
  your contributions.

## Contact Information
  Email: shivam109.kumar@gmail.com
  LinkedIn: https://www.linkedin.com/in/shivam-7094911b1/
  
