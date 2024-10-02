import json
from datetime import datetime
import os
import streamlit as st
import pandas as pd

def initialize_save_file(save_file_path: str):
  """
  Initializes the save JSON file if it doesn't exist.
  
  Args:
      save_file_path (str): Path to the save file.
  """
  if not os.path.exists(save_file_path):
      try:
          with open(save_file_path, "w") as f:
              json.dump({}, f)  # Create an empty JSON object
      except Exception as e:
          st.error(f"Error initializing save file: {e}")

def append_to_save_file(save_file_path: str, gate_name: str, data_record: dict):
  """
  Appends a JSON record to the save file under the specified gate name.
  
  Args:
      save_file_path (str): Path to the save file.
      gate_name (str): The name of the gate to append data to.
      data_record (dict): The data record to append.
  """
  try:
      # Read the existing data
      with open(save_file_path, "r") as f:
          data = json.load(f)

      # Append the new record to the appropriate gate
      if gate_name not in data:
          data[gate_name] = []  # Create a new list for this gate if it doesn't exist
      data[gate_name].append(data_record)

      # Write the updated data back to the file
      with open(save_file_path, "w") as f:
          json.dump(data, f, indent=4)  # Use indent for pretty printing
  except Exception as e:
      st.error(f"Error saving data: {e}")

def create_data_record(track_id, plate_text, confidence):
  """
  Creates a data record dictionary with the required fields.
  
  Args:
      track_id: The tracking ID of the vehicle.
      plate_text: The detected license plate text.
      confidence: The confidence score of detection.
  
  Returns:
      dict: A dictionary containing the track_id, plate_text, timestamp, and confidence.
  """
  return {
      "track_id": track_id,
      "plate_text": plate_text,
      "timestamp": datetime.now().isoformat(),
      "confidence": confidence,
  }

import pandas as pd
import streamlit as st

# Function to update the cars data
def update_cars_data(plate_number, action, cars_data_path):
  print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",plate_number)
  # Load the existing cars data
  cars_df = pd.read_excel(cars_data_path)

  # Check if the plate number already exists in the DataFrame
  existing_record = cars_df[cars_df['Plate Number'] == plate_number]

  if not existing_record.empty:
      # If the record exists, update the corresponding row
      index = existing_record.index[0]
      if action == "whitelist":
          cars_df.at[index, 'Permit'] = 1
          cars_df.at[index, 'BlackList'] = 0
      elif action == "blacklist":
          cars_df.at[index, 'Permit'] = 0
          cars_df.at[index, 'BlackList'] = 1
      st.session_state.message = f"Updated {plate_number} to {'whitelist' if action == 'whitelist' else 'blacklist'}."
  else:
      # If the record does not exist, append a new row
      new_record = pd.DataFrame([{
          'category': 'Cars',
          'Plate Number': plate_number,
          'Sticker Number': 0,  # Assuming default value
          'Model': 'Unknown',  # Assuming default value
          'BlackList': 0 if action == "whitelist" else 1,
          'Unit #': 'Unknown',  # Assuming default value
          'Permit': 1 if action == "whitelist" else 0,
          'From': '',  # Assuming default value
          'To': '',  # Assuming default value
          'Expired': 0  # Assuming default value
      }])
      cars_df = pd.concat([cars_df, new_record], ignore_index=True)
      st.session_state.message = f"Added {plate_number} to {'whitelist' if action == 'whitelist' else 'blacklist'}."

  # Save the updated DataFrame back to the Excel file
  print("ZZZZZZZZZZZZZZZZZZZZZZZZZ",plate_number)
  cars_df.to_excel(cars_data_path, index=False)


def search_car_history(plate_text,saved_json):
      # Load the JSON data from the file
  with open(saved_json, 'r', encoding='utf-8') as file:
      data = json.load(file)

  # Initialize a list to hold matching records
  matching_records = []

  # Iterate through each gate in the data
  for gate, records in data.items():
      # Check each record for a matching plate text
      for record in records:
          if record['plate_text'] == plate_text:
              matching_records.append({
                  'gate': gate,
                  'track_id': record['track_id'],
                  'plate_text': record['plate_text'],
                  'timestamp': record['timestamp'],
                  'confidence': record['confidence']
              })
  @st.dialog("car history")
  def show_car_history():  
    st.write(matching_records)
  show_car_history()
  return matching_records
# # Function to update the cars data
# def update_cars_data(plate_number, action, cars_data_path):
#   # Load the existing cars data
#   cars_df = pd.read_excel(cars_data_path)

#   # Check if the plate number already exists in the DataFrame
#   existing_record = cars_df[cars_df['Plate Number'] == plate_number]

#   if not existing_record.empty:
#       # If the record exists, update the corresponding row
#       index = existing_record.index[0]
#       if action == "whitelist":
#           cars_df.at[index, 'Permit'] = 1
#           cars_df.at[index, 'BlackList'] = 0
#       elif action == "blacklist":
#           cars_df.at[index, 'Permit'] = 0
#           cars_df.at[index, 'BlackList'] = 1
#       st.session_state.message = f"Updated {plate_number} to {'whitelist' if action == 'whitelist' else 'blacklist'}."
#   else:
#       # If the record does not exist, append a new row
#       new_record = {
#           'category': 'Cars',
#           'Plate Number': plate_number,
#           'Sticker Number': 0,  # Assuming default value
#           'Model': 'Unknown',  # Assuming default value
#           'BlackList': 0 if action == "whitelist" else 1,
#           'Unit #': 'Unknown',  # Assuming default value
#           'Permit': 1 if action == "whitelist" else 0,
#           'From': 'Unknown',  # Assuming default value
#           'To': 'Unknown',  # Assuming default value
#           'Expired': 0  # Assuming default value
#       }
#       cars_df = cars_df.append(new_record, ignore_index=True)
#       st.session_state.message = f"Added {plate_number} to {'whitelist' if action == 'whitelist' else 'blacklist'}."

#   # Save the updated DataFrame back to the Excel file
#   cars_df.to_excel(cars_data_path, index=False)