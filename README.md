# Fysio-Project
This application offers an efficient overview for researchers, analysts, and professionals in the Dutch healthcare industry. 
The primary purpose of this tool is to enable users to analyze the
data by leveraging advanced algorithms and natural language processing techniques.
This application allows users to upload the Dutch PDF Health Magazine and dive into the
content of these magazines and uncover clusters of complexity-related terms. Additionally,
users can explore the relationships between these terms and observe any changes that may have
occurred over the years.

# System Requirements
Before you begin, please ensure that your system meets the following requirements:
● Operating System: Windows, macOs, or Linux
● Docker: Recent version
● Internet connection: for downloading Docker application, Docker images and updates
● Available storage: 1GB

# Installation
To install and set up the Fysio Project Application, follow these steps:

## Step 1: Download Docker
● Visit the official Docker website at https://www.docker.com/
● Download the appropriate Docker version for your operating system.
● Install Docker by following the provided instructions.

## Step 2: Download the Project Image:
● Open a terminal or command prompt.
● Run the following command to download the project image:
docker pull wattbreak/physio:clean

## Step 3: Launch the Image
Run the following command to launch the application:
docker run -p 8050:8050 wattbreak/physio:clean

The application will start running. After a few seconds, open a browser and access the following website
http://localhost:8050.

# --> Read the manual PDF to see how to use the application. 
