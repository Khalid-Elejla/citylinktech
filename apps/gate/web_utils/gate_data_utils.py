import json


def load_gate_data(Gate_id, GATE_DATA):
    """Load the parking spots and video source for the selected parking spot."""
    with open(GATE_DATA, 'r') as file:
        data = json.load(file)
    gate_data = data.get(Gate_id, {})
    video_type = gate_data.get('type')
    video_source = gate_data.get('video_source')
    coordinates = gate_data.get('coordinates', [])
    return video_type, video_source, [list(map(tuple, spots)) for spots in coordinates]

def get_gates_names(GATE_DATA):
    with open(GATE_DATA, 'r') as file:
        data = json.load(file)
    return list(data.keys())

import pandas as pd
from datetime import datetime

def check_vehicle_status(cars_df, license_plate_text):
    # Search for the license plate in the DataFrame
    vehicle_row = cars_df[cars_df['Plate Number'] == license_plate_text]

    # Check if the license plate exists in the data
    if vehicle_row.empty:
        return "License plate not found"

    # Check the BlackList column
    if vehicle_row['BlackList'].values[0] == 1:
        return "Blacklisted"
    
    # Check the Permit column
    if vehicle_row['Permit'].values[0] == 0:
        return "Not Permitted"
    
    # Check if current time is within the permitted range (From and To columns)
    current_time = datetime.now()

    # Convert 'From' and 'To' columns to datetime
    try:
        from_date = pd.to_datetime(vehicle_row['From'].iloc[0])
        to_date = pd.to_datetime(vehicle_row['To'].iloc[0])
    except (ValueError, KeyError, IndexError) as e:
        # return f"Error parsing date: {str(e)}"
        return f"Error parsing time"

    # try:
    #     from_date = pd.to_datetime(vehicle_row['From'].values[0])
    #     to_date = pd.to_datetime(vehicle_row['To'].values[0])
    # except ValueError:
    #     return "Time is not accurately formatted"


    if from_date <= current_time <= to_date:
        return "Permitted"
    else:
        return "Permission is not valid"
