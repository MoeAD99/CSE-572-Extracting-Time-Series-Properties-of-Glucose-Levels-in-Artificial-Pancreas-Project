from datetime import datetime as dt

import pandas as pd

# Load and preprocess CGM data
cgm_df = pd.read_csv("CGMData.csv")
cgm_date = cgm_df["Date"]
cgm_time = cgm_df["Time"]
cgm_datetime = [
    dt.strptime(cgm_date[i] + " " + cgm_time[i], "%m/%d/%Y %H:%M:%S")
    for i in range(len(cgm_date))
]
cgm_df["Datetime"] = cgm_datetime  # Add the datetime to the DataFrame
cgm_df["Sensor Glucose (mg/dL)"].interpolate(axis=0, inplace=True)
cgm_df["Sensor Glucose (mg/dL)"] = cgm_df["Sensor Glucose (mg/dL)"].round()

# Load and preprocess Insulin data
insulin_df = pd.read_csv("InsulinData.csv")
insulin_date = insulin_df["Date"]
insulin_time = insulin_df["Time"]
insulin_datetime = [
    dt.strptime(insulin_date[i] + " " + insulin_time[i], "%m/%d/%Y %H:%M:%S")
    for i in range(len(insulin_date))
]
alarm = insulin_df["Alarm"]

# Detect the start of Auto mode
auto = False
pump_auto_start_timestamp = None
for i in range(len(alarm)):
    if alarm[i] == "AUTO MODE ACTIVE PLGM OFF":
        auto = True
        pump_auto_start_timestamp = insulin_datetime[i]

# Find the corresponding timestamp in CGM data
cgm_auto_start_timestamp = None
for datetime in cgm_datetime:
    if pump_auto_start_timestamp <= datetime:
        cgm_auto_start_timestamp = datetime

cgm_auto_start_index = cgm_datetime.index(cgm_auto_start_timestamp)

# Separate data into manual and auto mode
manual_mode_cgm_df = cgm_df.iloc[cgm_auto_start_index + 1 :]
auto_mode_cgm_df = cgm_df.iloc[: cgm_auto_start_index + 1]

# Add a 'Date' and 'Time' column for easier grouping by day and segment
manual_mode_cgm_df["Date"] = manual_mode_cgm_df["Datetime"].dt.date
manual_mode_cgm_df["Time"] = manual_mode_cgm_df["Datetime"].dt.time
auto_mode_cgm_df["Date"] = auto_mode_cgm_df["Datetime"].dt.date
auto_mode_cgm_df["Time"] = auto_mode_cgm_df["Datetime"].dt.time


# Function to calculate metrics for each segment
def calculate_metrics_for_segment(df, start_time, end_time):
    segment_data = df[(df["Time"] >= start_time) & (df["Time"] < end_time)]
    days = segment_data["Date"].unique()
    metrics = {
        "Percentage time in hyperglycemia": [],
        "Percentage time in hyperglycemia critical": [],
        "Percentage time in range": [],
        "Percentage time in range secondary": [],
        "Percentage time in hypoglycemia Level 1": [],
        "Percentage time in hypoglycemia Level 2": [],
    }

    for day in days:
        day_data = segment_data[segment_data["Date"] == day]

        metrics["Percentage time in hyperglycemia"].append(
            (day_data["Sensor Glucose (mg/dL)"] > 180).sum() / 288 * 100
        )
        metrics["Percentage time in hyperglycemia critical"].append(
            (day_data["Sensor Glucose (mg/dL)"] > 250).sum() / 288 * 100
        )
        metrics["Percentage time in range"].append(
            (
                (day_data["Sensor Glucose (mg/dL)"] >= 70)
                & (day_data["Sensor Glucose (mg/dL)"] <= 180)
            ).sum()
            / 288
            * 100
        )
        metrics["Percentage time in range secondary"].append(
            (
                (day_data["Sensor Glucose (mg/dL)"] >= 70)
                & (day_data["Sensor Glucose (mg/dL)"] <= 150)
            ).sum()
            / 288
            * 100
        )
        metrics["Percentage time in hypoglycemia Level 1"].append(
            (day_data["Sensor Glucose (mg/dL)"] < 70).sum() / 288 * 100
        )
        metrics["Percentage time in hypoglycemia Level 2"].append(
            (day_data["Sensor Glucose (mg/dL)"] < 54).sum() / 288 * 100
        )

    return pd.DataFrame(metrics).mean()


# Calculate metrics for manual mode
manual_daytime_metrics = calculate_metrics_for_segment(
    manual_mode_cgm_df,
    dt.strptime("06:00:00", "%H:%M:%S").time(),
    dt.strptime("23:59:59", "%H:%M:%S").time(),
)
manual_overnight_metrics = calculate_metrics_for_segment(
    manual_mode_cgm_df,
    dt.strptime("00:00:00", "%H:%M:%S").time(),
    dt.strptime("06:00:00", "%H:%M:%S").time(),
)
manual_whole_day_metrics = calculate_metrics_for_segment(
    manual_mode_cgm_df,
    dt.strptime("00:00:00", "%H:%M:%S").time(),
    dt.strptime("23:59:59", "%H:%M:%S").time(),
)

# Calculate metrics for auto mode
auto_daytime_metrics = calculate_metrics_for_segment(
    auto_mode_cgm_df,
    dt.strptime("06:00:00", "%H:%M:%S").time(),
    dt.strptime("23:59:59", "%H:%M:%S").time(),
)
auto_overnight_metrics = calculate_metrics_for_segment(
    auto_mode_cgm_df,
    dt.strptime("00:00:00", "%H:%M:%S").time(),
    dt.strptime("06:00:00", "%H:%M:%S").time(),
)
auto_whole_day_metrics = calculate_metrics_for_segment(
    auto_mode_cgm_df,
    dt.strptime("00:00:00", "%H:%M:%S").time(),
    dt.strptime("23:59:59", "%H:%M:%S").time(),
)

# Combine results into 2x18 format
manual_results = pd.concat(
    [manual_overnight_metrics, manual_daytime_metrics, manual_whole_day_metrics]
).values.flatten()
auto_results = pd.concat(
    [auto_overnight_metrics, auto_daytime_metrics, auto_whole_day_metrics]
).values.flatten()

# Combine both rows into a final DataFrame
final_results = pd.DataFrame([manual_results, auto_results])

# Write CSV file
final_results.to_csv("Result.csv", header=False, index=False)

print("Result.csv saved successfully!")
