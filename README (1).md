# **Data Analytics Report Generator**

This command-line tool analyzes user session and order data from CSV files to generate a comprehensive analytics report. It performs a funnel conversion analysis, calculates the distribution of user intents, and checks for violations of the order cancellation policy.

The final output includes a detailed JSON file and two data visualizations.

## **Features**

* **Funnel Analysis:** Builds a Loaded → Interact → Clicks → Purchase conversion funnel, segmented by device (mobile vs. desktop).  
* **Intent Analysis:** Calculates the percentage share of all detected user intents from messages.  
* **SLA Compliance:** Checks order data for compliance with a 60-minute cancellation window and calculates the violation rate.  
* **Automated Reporting:** Generates a report.json file summarizing all analytical findings.  
* **Data Visualization:** Creates and saves two PNG charts:  
  * funnel.png: A bar chart visualizing the conversion funnel by device.  
  * intents.png: A bar chart showing the distribution of the top 10 user intents.

## **Setup and Installation**

Before running the script, you need to have Python 3 installed and the required libraries.

1. **Prerequisites**:  
   * Python 3.7 or newer  
2. Install Libraries:  
   Open your terminal and run the following command to install the necessary Python packages:  
   pip install pandas matplotlib seaborn

## **How to Run**

Execute the script from your terminal, providing paths to the input data files and specifying an output directory. The script name is assumed to be evo.py.

**Command Structure:**

python evo.py \--events \<path\_to\_events.csv\> \--messages \<path\_to\_messages.csv\> \--orders \<path\_to\_orders.csv\> \--out \<output\_directory\_path\>

Example:  
If your CSV files are in the same directory as the script, you can run:  
python evo.py \\  
  \--events ./events.csv \\  
  \--messages ./messages.csv \\  
  \--orders ./orders.csv \\  
  \--out ./output/

The script will create the output directory if it doesn't already exist and place the generated files inside it.

## **Output Files**

The script will generate the following files in the specified output directory:

1. report.json  
   A JSON file containing the complete analysis.  
   * funnel: A list of objects, detailing each step of the conversion funnel for each device.  
   * intents: A list of objects, showing the count and percentage share for each detected intent.  
   * cancellation\_sla: An object summarizing total orders, cancellations, and SLA violations.  
2. funnel.png  
   A grouped bar chart that visually compares the user conversion journey on mobile versus desktop devices.  
3. intents.png  
   A horizontal bar chart displaying the percentage share of the top 10 most common user intents.