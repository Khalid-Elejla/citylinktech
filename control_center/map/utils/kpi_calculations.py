import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

def calculate_emergency_kpis(df):
    # Strip trailing '*' from column names
    df_copy = df.copy()
    df_copy.columns = df_copy.columns.str.rstrip("*")

    # Check if required columns exist
    required_columns = ["Open Time", "Closure Time", "Status", "Satisfaction"]
    for col in required_columns:
        if col not in df_copy.columns:
            raise ValueError(f"Column '{col}' is missing from the DataFrame")

    today = datetime.today().date()

    # Function to parse time whether it valid format
    def parse_time(t):
        try:
            return pd.to_datetime(t, format="%H:%M:%S").time()
        except ValueError:
            try:
                return pd.to_datetime(t, format="%H:%M").time()
            except ValueError:
                raise ValueError(f"Time format for '{t}' is incorrect")

    # Ensure 'Open Time' and 'Closure Time' are in time format
    df_copy["Open Time"] = df_copy["Open Time"].apply(
        lambda x: parse_time(x.time() if isinstance(x, datetime) else x)
    )
    df_copy["Closure Time"] = df_copy["Closure Time"].apply(
        lambda x: parse_time(x.time() if isinstance(x, datetime) else x)
    )

    # Combine with today's date to create datetime objects
    df_copy["Open Time"] = df_copy["Open Time"].apply(
        lambda x: datetime.combine(today, x)
    )
    df_copy["Closure Time"] = df_copy["Closure Time"].apply(
        lambda x: datetime.combine(today, x)
    )

    # Calculate the mean emergency closure time
    emergency_closure_time = (df_copy["Closure Time"] - df_copy["Open Time"]).mean()
    
    # Calculate Closure Percentage
    closure_percentage = (df_copy["Status"] == "Closed").mean() * 100
    satisfaction_rate = (
        df_copy["Satisfaction"].str.lower().apply(lambda x: x == "satisfied").mean() * 100
    )

    # Calculate unique emergency number
    emergency_numbers = len(df_copy)
    
    # Calculate unique emergency number
    df_copy['Location'] = df_copy[['Latitude', 'Longitude']].apply(lambda x: f"{x['Latitude']},{x['Longitude']}", axis=1)
    unique_emergency_numbers = df_copy['Location'].nunique()


    expected_emergency_alarm = "To be calculated based on relationships"

    return {
        "Closure Percentage": closure_percentage,
        "Emergency Closure Time":f"{emergency_closure_time.days}d {emergency_closure_time.seconds // 3600}h {(emergency_closure_time.seconds % 3600) // 60}m",
        "Satisfaction Rate": satisfaction_rate,
        "Emergency Numbers": emergency_numbers,
        "Expected Emergency Alarm": expected_emergency_alarm,
    }



def calculate_workforce_kpis(df):
  # Copy the DataFrame and strip trailing '*' from column names
    df_copy = df.copy(deep=False)
    df_copy.columns = df_copy.columns.str.rstrip('*')

    # Define required columns and validate their presence
    required_columns = ["Open Time", "Closure Time", "Status", "Evaluation", "Complain Today"]
    missing_columns = [col for col in required_columns if col not in df_copy.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    today = datetime.today().date()

    # Helper function to parse time, handling various formats
    def parse_time(t):
        try:
            return pd.to_datetime(t, format="%H:%M:%S").time()
        except ValueError:
            try:
                return pd.to_datetime(t, format="%H:%M").time()
            except ValueError:
                raise ValueError(f"Invalid time format: '{t}'")

    # Ensure 'Open Time' and 'Closure Time' are parsed as time objects
    df_copy["Open Time"] = df_copy["Open Time"].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
    df_copy["Closure Time"] = df_copy["Closure Time"].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

    # Combine parsed time with today's date to create full datetime objects
    df_copy["Open Time"] = df_copy["Open Time"].apply(lambda x: datetime.combine(today, x))
    df_copy["Closure Time"] = df_copy["Closure Time"].apply(lambda x: datetime.combine(today, x))

    # Calculate average working hours
    working_hours = (df_copy["Closure Time"] - df_copy["Open Time"]).mean()
    print("working_hours",working_hours)
    working_hours_str = f"{working_hours.days}d {working_hours.seconds // 3600}h {(working_hours.seconds % 3600) // 60}m"


    # Calculate operation percentage (Active operations / Total operations)
    total_operations = len(df_copy)
    active_operations = (df_copy["Status"] == "Active").sum()
    operation_percentage = (active_operations / total_operations) * 100 if total_operations > 0 else 0

    # Calculate evaluation rate
    total_evaluations = df_copy["Evaluation"].sum()
    evaluation_rate = total_evaluations / total_operations if total_operations > 0 else 0

    # Calculate the total number of complaints today
    complain_numbers = len(df_copy)

    # Placeholder for expected complaints alarm
    expected_complains_alarm = "To be calculated based on relationships"

    # Create a pie chart for operation status distribution
    if "Operation" in df_copy.columns:
        status_counts = df_copy["Operation"].value_counts()
        fig, ax = plt.subplots(figsize=(1, 1))

        # Set transparent background
        fig.patch.set_facecolor("none")
        ax.set_facecolor("none")

        # Plot pie chart with white text
        ax.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%", startangle=90, textprops={"color": "white", "fontsize": 4})
        ax.axis("equal")  # Ensures the pie chart is a circle
        plt.title("Operations Status Distribution")
    else:
        fig = None  # No pie chart if 'Operation' column is missing

    # Return the calculated KPIs along with the pie chart figure
    return {
        "Operation Percentage": operation_percentage,
        "Working Hours": working_hours_str,
        "Evaluation Rate": evaluation_rate,
        "Complain Numbers": complain_numbers,
        "Expected Complains Alarm": expected_complains_alarm,
        "fig": fig,
    }