📁 Project Structure
├── power_cleaning.ipynb        # Data cleaning and preprocessing steps
├── power_eda.ipynb                 # Exploratory data analysis (EDA)
├── main.py                   # Main Dash layout and app
├── callback.py               # All interactivity logic (filters, dropdowns, toggles)
├── styles.py                 # Custom styling and layout components
├── assets/                   
└── README.md                 # You’re reading it!

📊 Dataset Overview
The dataset contains information about major power outage events in the U.S., with the following columns:
date-event-began,date_event_restored,nerc-region,area-affected (State-level),loss-(megawatts),number-of-customers-affected,year,cause

🔧 Data Cleaning Highlights
Notebook: power_cleaning.ipynb 

📈 EDA Highlights
Notebook: power_eda.ipynb 
🖥️ Dash App Features
Code in main.py, callback.py, styles.py

💡 Key Insight Panel
A collapsible sidebar just under the header that summarizes:
Trends in outage frequency
State-level highlights
Leading causes of outages
% increase in states affected (e.g., “+20% since 2010”)

🎯 KPI Cards
Total outage events
Number of unique areas affected
Average power loss
number of people affected in a typical event

📅 Temporal Analysis
Yearly trend of unique areas affected
Line plots of:
Outage frequency
Avg. power loss
Avg. customers affected
(All filtered by state)

🌍 State-Level Insights
Choropleth map showing areas most affected
Top 10 states by:
Average power loss
Average number of customers affected
(Filtered by cause)

⚠️ Cause-Specific Analysis
Choropleth map of outages by cause
Line chart showing which causes contributed most to:
Power loss
People affected

What to improve on
- improve data cleaning skills
- add trendlines on the line plots
- pct_change calculations to cater for the different state sizes and population



