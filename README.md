📊 Mini Sales Analysis Tool (Automatic)

A fully automated Sales Data Analysis Desktop Application built using Python, Pandas, Matplotlib, and Tkinter.

This tool allows users to import sales data in CSV, Excel, or JSON format, automatically detect important columns, clean the data, perform analysis, generate visualizations, and export cleaned results.

🚀 Features

✅ Supports CSV, Excel (.xls/.xlsx), and JSON input files
✅ Automatic column detection (Date, Product, Quantity, Price)
✅ Data cleaning and preprocessing
✅ Removes duplicates and invalid rows
✅ Calculates total revenue
✅ Monthly sales trend analysis
✅ Revenue by product analysis
✅ Auto-generated visualizations (Bar & Line charts)
✅ Export cleaned data as CSV or Excel
✅ Unique output file name for every run
✅ Simple GUI interface using Tkinter

🛠 Technologies Used

Python

Pandas – Data processing

Matplotlib – Data visualization

Tkinter – GUI

Openpyxl – Excel export support

Regex (re module) – Data cleaning

📂 Supported Input Formats
Format	Extension
CSV	.csv
Excel	.xls, .xlsx
JSON	.json
📈 What the Program Does
1️⃣ Automatic Column Detection

The program intelligently detects:

Date column

Product column

Quantity column

Price column

Even if column names are different, the system tries to identify them based on data patterns.

2️⃣ Data Cleaning

Removes special characters from product names

Converts quantity and price to numeric

Parses date columns safely

Removes duplicates

Drops invalid rows

3️⃣ Sales Calculations

Creates Total = Quantity × Price

Extracts month from date

Calculates:

Total Revenue

Revenue by Product

Monthly Sales Trend

Best Month vs Average %

4️⃣ Visualization

📊 Bar Chart – Revenue by Product
📈 Line Chart – Monthly Sales Trend

Charts are displayed using Matplotlib (TkAgg backend).

5️⃣ Output File

The cleaned file is saved automatically as:

OriginalFileName_cleaned_YYYYMMDD_HHMMSS.csv

Example:

January_Sales_cleaned_20260220_104523.csv

This ensures:

Unique filename every time

No overwriting

Saved in the same folder as input file

You can choose:

CSV output

Excel output (.xlsx)

🖥 How to Run
Step 1: Install Required Libraries
pip install pandas matplotlib openpyxl

(Tkinter comes pre-installed with most Python installations)

Step 2: Run the Program
python your_file_name.py
Step 3: Use the GUI

Click "Select Data File and Run Analysis"

Choose your CSV / Excel / JSON file

Select output format (CSV or Excel)

Analysis will run automatically

Charts will appear

Cleaned file will be saved

Success message will be displayed

📌 Project Structure Example
mini-sales-analysis/
│
├── sales_analysis.py
├── README.md
└── sample_data.csv
🎯 Ideal For

Python beginners learning data analysis

Students building mini projects

Data cleaning automation practice

Portfolio project demonstration

Academic submission

🔮 Future Improvements (Optional Ideas)

Add PDF report export

Add filtering options (Date range, Product)

Add dashboard view

Add summary statistics panel

Add database integration (MySQL / SQLite)

👩‍💻 Author

Priya Dharshini
Python Developer | Data Analysis Enthusiast


🏷️ Professional project explanation for interviews

Just tell me 😊
