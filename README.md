# safe-drive-datahub

The data analysis platform for the safe drive africa

## Overview

**safe-drive-datahub** is an analytics platform designed to help curate drivers driving data from the safe-drive-africa-api to anaylse and better understand drivers driving patterns, with the aim to improve overall driving safety. By collecting, processing, and visualizing key data points (like speed, braking, swerving and alcohol influenced driving), this platform aims to provide actionable insights to foster safer driving behaviours in Africa. This is part of a PhD Research work domiciled at the University of Aberdeen Scotland, United Kingdom and sponsored by the Tertiary Education Trust Fund (Tetfund) in Nigeria.

## Features

- **Real-Time Data Collection**  
  Seamlessly integrate with a backend api that recieves data from our safe-drive-africa mobile which collects data in realtime.

- **Analytics Dashboard**  
  Visualize driving data through charts, graphs, and heatmaps to quickly identify trends and patterns.


- **Historical Data Comparison**
  Compare current driving data with historical records to measure improvement or identify recurring issues.

- **Loading Feedback**
  A spinner overlay briefly appears while pages prepare data so you know the application is working.

## Getting Started

### Prerequisites

- A machine or server with Python 3.9+ installed (or the relevant environment for your chosen tech stack).
- Optionally, Docker installed (if you plan to containerize and deploy easily).

### Installation

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/iniakponode/safe-drive-africa-datahub.git
   cd safe-drive-datahub

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
3. **Usage**
   ```bash
   python app/main.py
  This command starts the server or the main analytics process, depending on your specific implementation.

4. **Access the Dashboard**
  Open your browser and navigate to the URL (e.g., http://localhost:8001) to view the dashboard.

### Table Navigation

Tables on the dashboard and the driver statistics page support client-side pagination and search.
Use the search boxes above each table to filter by Driver ID, Driver Email, or Trip ID.
Previous/Next buttons and page numbers below each table allow navigating between pages of up to 10 rows at a time.

