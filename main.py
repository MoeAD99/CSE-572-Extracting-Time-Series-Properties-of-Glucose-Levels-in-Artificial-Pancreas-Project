from datetime import datetime as dt

import pandas as pd

cgm_df = pd.read_csv("CGMData.csv")
cgm_df.ffill()
cgm_date = cgm_df["Date"]
cgm_time = cgm_df["Time"]
cgm_datetime = [
    dt.strptime(cgm_date[i] + " " + cgm_time[i], "%m/%d/%Y %H:%M:%S")
    for i in range(len(cgm_date))
]
cgm = cgm_df["Sensor Glucose (mg/dL)"]
cgm.interpolate(axis=0, inplace=True)
cgm = cgm.round()
# print(cgm[0:10])

# cgm_datetime1 = [
#     (
#         dt.strptime(cgm_date[i], "%m/%d/%Y"),
#         dt.strptime(cgm_time[i], "%H:%M:%S"),
#     )
#     for i in range(len(cgm_date))
# ]

# print(cgm_datetime1[0])
insulin_df = pd.read_csv("InsulinData.csv")
insulin_date = insulin_df["Date"]
insulin_time = insulin_df["Time"]
insulin_datetime = [
    dt.strptime(insulin_date[i] + " " + insulin_time[i], "%m/%d/%Y %H:%M:%S")
    for i in range(len(insulin_date))
]
alarm = insulin_df["Alarm"]

auto = False
pump_auto_start_timestamp = ()
for i in range(len(alarm)):
    if alarm[i] == "AUTO MODE ACTIVE PLGM OFF":
        auto = True
        pump_auto_start_timestamp = insulin_datetime[i]
        print(pump_auto_start_timestamp)
        print(i)
cgm_auto_start_timestamp = 0
for datetime in cgm_datetime:
    if datetime == pump_auto_start_timestamp:
        cgm_auto_start_timestamp = datetime
    else:
        if pump_auto_start_timestamp <= datetime:

            # index = insulin_datetime.index(datetime)
            cgm_auto_start_timestamp = datetime

# cgm_auto_start_timestamp = ()
# for datetime in cgm_datetime:
#     if datetime[0] == pump_auto_start_timestamp[0]:
#         if datetime[1] == pump_auto_start_timestamp[1]:
#             cgm_auto_start_timestamp = datetime
#         else:
#             if int(pump_auto_start_timestamp[1].split(":")[1]) <= int(
#                 datetime[1].split(":")[1]
#             ) and int(pump_auto_start_timestamp[1].split(":")[0]) <= int(
#                 datetime[1].split(":")[0]
#             ):

#                 # index = insulin_datetime.index(datetime)
#                 cgm_auto_start_timestamp = (datetime[0], datetime[1])
# print(type(int(pump_auto_start_timestamp[1].split(":")[0])))

# print(pump_auto_start_timestamp[1].split(":")[1])
print(cgm_datetime.index(cgm_auto_start_timestamp))
print(cgm_datetime[55342])
