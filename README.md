\# ⚡ EV Charging Intelligence \& Demand Analytics Platform



An interactive data analytics platform designed to analyze electric vehicle (EV) charging sessions, understand charging demand, evaluate station performance, and identify unusual charging patterns.



Built using \*\*Python, Pandas, Streamlit, Plotly, and SQL\*\*, this project transforms raw charging session data into actionable business insights through an interactive dashboard.



\## 📌 Project Overview



As electric vehicle adoption grows, charging station operators need to understand when charging demand peaks, which stations deliver the most energy, and how vehicles use charging infrastructure.



This project analyzes EV charging session data to help answer these questions through data cleaning, exploratory data analysis (EDA), demand analysis, station performance comparisons, and charging behavior investigation.



\### 🎯 Business Objectives



\* Understand hourly, daily, and monthly charging demand.

\* Identify busy charging periods and usage patterns.

\* Compare charging stations by session volume and energy delivered.

\* Analyze energy consumption per charging session.

\* Investigate unusually long vehicle connections and high-energy sessions.

\* Identify data quality issues, including missing charging completion timestamps.

\* Present analytical findings through an interactive dashboard.



\## 🖥️ Dashboard Features



\### 1. Executive Overview



Provides a high-level view of charging activity through key performance indicators, charts, station comparisons, and data filters.



\### 2. Demand Analysis



Explores charging demand across different time periods.



Features include:



\* Hourly charging demand

\* Daily demand patterns

\* Weekday versus weekend comparisons

\* Monthly charging trends

\* Energy delivered by hour

\* Charging station filters

\* Downloadable analysis results



\### 3. Station Performance



Compares charging stations using operational and energy metrics.



Features include:



\* Total charging sessions per station

\* Total energy delivered

\* Average energy per session

\* Station energy contribution

\* Connection duration versus charging duration

\* Station performance summary

\* CSV export



\### 4. Charging Behavior \& Anomaly Analysis



Investigates unusual charging patterns and sessions that may require further review.



Features include:



\* Connection duration distribution

\* Energy consumption distribution

\* Configurable long-connection threshold

\* Potential high-energy outlier detection using the Interquartile Range (IQR) method

\* Long connections with relatively low energy delivery

\* Station-level behavior summaries

\* Downloadable analysis results



\*\*Important:\*\* These anomaly indicators identify sessions for investigation. They do not independently establish equipment faults, fraud, or other causes.



\## 📊 Dataset Description



The project uses an EV charging session dataset stored in `ev\_charging\_cleaned.csv`.



| Dataset characteristic | Description                   |

| ---------------------- | ----------------------------- |

| Total records          | 3,034 charging sessions       |

| Total original columns | 13                            |

| Data type              | Structured session-level data |

| Time coverage          | January–September 2021        |

| September coverage     | Partial month                 |

| Duplicate session IDs  | 0 identified                  |

| Duplicate record IDs   | 0 identified                  |



\### Key Columns



| Column             | Description                          |

| ------------------ | ------------------------------------ |

| `sessionID`        | Unique charging session identifier   |

| `connectionTime`   | Time the vehicle connected           |

| `disconnectTime`   | Time the vehicle disconnected        |

| `doneChargingTime` | Recorded charging completion time    |

| `kWhDelivered`     | Energy delivered during the session  |

| `stationID`        | Charging station identifier          |

| `siteID`           | Charging site identifier             |

| `spaceID`          | Charging space identifier            |

| `userID`           | User identifier, when available      |

| `timezone`         | Timezone associated with the session |



The analysis distinguishes between \*\*connection duration\*\* and \*\*charging duration\*\*. A vehicle may remain connected after charging has finished, so these measurements should not be treated as equivalent.



\## 🔍 Data Analysis Workflow



The project follows a practical analytics workflow:



1\. \*\*Data loading\*\* — Read the charging session dataset into Python.

2\. \*\*Data inspection\*\* — Examine columns, data types, missing values, and duplicate records.

3\. \*\*Data preparation\*\* — Standardize column names, parse timestamps, and convert energy values to numeric data.

4\. \*\*Feature engineering\*\* — Calculate connection duration, charging duration, hour, weekday, and month.

5\. \*\*Exploratory data analysis\*\* — Examine charging demand, energy consumption, and station activity.

6\. \*\*Outlier analysis\*\* — Apply the IQR method to identify potentially unusual energy values.

7\. \*\*Business analysis\*\* — Compare charging stations and investigate charging behavior.

8\. \*\*Dashboard development\*\* — Build interactive visualizations and filters using Streamlit and Plotly.

9\. \*\*Deployment\*\* — Publish the dashboard using Streamlit Community Cloud.



\## 💡 Key Findings



The analysis identified several useful patterns in the dataset.



\* \*\*Peak charging hour:\*\* 8 AM local time was the busiest hour for session starts in the analyzed dataset.

\* \*\*Busiest weekday by session count:\*\* Wednesday recorded the highest number of sessions in the original analysis.

\* \*\*Monthly demand:\*\* August 2021 recorded the highest monthly session count in the original analysis. September contains only partial-month data.

\* \*\*Station concentration:\*\* Station `2-39-81-4550` recorded 997 sessions and delivered approximately 22,796.65 kWh, accounting for about 60.83% of total energy delivered.

\* \*\*High-energy sessions:\*\* The IQR method identified 222 potential high-energy outliers. These are investigation candidates, not automatically data errors.

\* \*\*Missing completion timestamps:\*\* Approximately 37.51% of sessions lacked a recorded charging completion timestamp.

\* \*\*Long connections:\*\* Some vehicles remained connected for extended periods. Long connection duration does not necessarily indicate that charging continued for the entire period.



These findings can help charging operators investigate demand patterns, station utilization, energy delivery, and potential opportunities for operational improvement.



\## 🛠️ Technologies Used



| Technology                | Purpose                                                            |

| ------------------------- | ------------------------------------------------------------------ |

| Python                    | Data processing and analytics                                      |

| Pandas                    | Data cleaning, transformation, and aggregation                     |

| SQL / MySQL               | Relational database design and querying during project development |

| Streamlit                 | Interactive dashboard development                                  |

| Plotly                    | Interactive charts and visualizations                              |

| CSV / JSON                | Data storage and input formats                                     |

| Git and GitHub            | Version control and source code hosting                            |

| Streamlit Community Cloud | Dashboard deployment                                               |



\## 📁 Project Structure



```text

EV\_Charging\_Intelligence/

│

├── app.py

├── ev\_charging\_cleaned.csv

├── requirements.txt

├── README.md

│

└── pages/

&#x20;   ├── 1\_Demand\_Analysis.py

&#x20;   ├── 2\_Station\_Performance.py

&#x20;   └── 3\_Charging\_Behavior.py

```



The main application provides the Executive Overview. The `pages` directory contains the three additional analytical pages.



\## 🚀 Run the Project Locally



\### Prerequisites



\* Python 3.11 or a compatible Python version

\* Git

\* The project dataset, `ev\_charging\_cleaned.csv`



\### Step 1: Clone the repository



```bash

git clone https://github.com/akashkprasanth/EV\_Charging\_Intelligence.git

```



\### Step 2: Enter the project directory



```bash

cd EV\_Charging\_Intelligence

```



\### Step 3: Create a virtual environment



```bash

python -m venv .venv

```



Activate it on Windows PowerShell:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



\### Step 4: Install dependencies



```bash

python -m pip install -r requirements.txt

```



\### Step 5: Start the dashboard



```bash

python -m streamlit run app.py

```



Streamlit will display a local address in the terminal. Open that address in your browser to explore the dashboard.



\## 🌐 Deployment



The dashboard is deployed using Streamlit Community Cloud.



\*\*Live Dashboard:\*\* Add your public Streamlit application URL here.



\*\*GitHub Repository:\*\*

https://github.com/akashkprasanth/EV\_Charging\_Intelligence



\## 🔐 Security and Data Handling



\* Do not commit database passwords, API keys, or other credentials.

\* Keep local environment files and `.streamlit/secrets.toml` out of version control.

\* The deployed dashboard reads the included CSV dataset, so the current cloud deployment does not require a live MySQL connection.

\* Review dataset permissions and licensing before redistributing the underlying data.



\## 📈 Future Improvements



Potential extensions include:



\* Forecasting future charging demand.

\* Predicting energy consumption per session.

\* Estimating station utilization and capacity requirements.

\* Adding geographic and site-level comparisons.

\* Connecting the dashboard to a managed database.

\* Adding automated data validation and scheduled dataset updates.

\* Comparing demand forecasts with actual charging activity.



\## 👨‍💻 Project Purpose



This project demonstrates practical skills in data analysis, Python programming, data visualization, SQL, dashboard development, and deployment.



It is designed to turn raw operational data into understandable metrics and business insights that can support data-driven decisions.



