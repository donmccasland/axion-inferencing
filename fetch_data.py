import pandas as pd
import requests
import google.auth
import google.auth.transport.requests
import logging

# --- Configuration ---
PROJECT_ID = "aiinfrasummit-demo"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Google Cloud Authentication ---
def get_credentials():
    """Gets Google Cloud credentials."""
    logging.info("Attempting to get Google Cloud credentials...")
    try:
        credentials, project = google.auth.default(scopes=['https://www.googleapis.com/auth/monitoring.read'])
        logging.info("Successfully got Google Cloud credentials.")
        return credentials
    except Exception as e:
        logging.error(f"Error getting Google Cloud credentials: {e}")
        return None

# --- Monitoring API Query ---
def get_accelerator_data(credentials):
    """Fetches accelerator duty cycle data from the Google Cloud Monitoring API."""
    if not credentials:
        logging.error("No credentials provided to get_accelerator_data.")
        return None

    logging.info("Refreshing credentials...")
    try:
        credentials.refresh(google.auth.transport.requests.Request())
    except Exception as e:
        logging.error(f"Error refreshing credentials: {e}")
        return None

    logging.info("Fetching accelerator data from Monitoring API...")
    query = "fetch k8s_container::kubernetes.io/container/accelerator/duty_cycle | within 5m"

    url = f"https://monitoring.googleapis.com/v3/projects/{PROJECT_ID}/timeSeries:query"
    
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
    }
    
    data = {"query": query}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logging.info("Successfully fetched data from Monitoring API.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making request to Monitoring API: {e}")
        return None

# --- Data Processing ---
def process_data(time_series_data):
    """Processes the time series data into a Pandas DataFrame."""
    if not time_series_data:
        return pd.DataFrame(columns=["accelerator_id", "duty_cycle"])

    logging.info("Processing time series data...")
    data = []
    for series in time_series_data.get("timeSeriesData", []):
        accelerator_id = "Unknown"
        # Find the accelerator_id from the labelValues
        for i, descriptor in enumerate(time_series_data.get("timeSeriesDescriptor", {}).get("labelDescriptors", [])):
            if descriptor.get("key") == "metric.accelerator_id":
                if i < len(series.get("labelValues", [])):
                    accelerator_id = series["labelValues"][i].get("stringValue", "Unknown")
                break

        if series.get("pointData"):
            latest_point = series["pointData"][0]
            duty_cycle = int(latest_point["values"][0]["int64Value"])
            data.append({"accelerator_id": accelerator_id, "duty_cycle": duty_cycle})

    if not data:
        logging.info("No data points found in the time series data.")
        return pd.DataFrame(columns=["accelerator_id", "duty_cycle"])

    logging.info(f"Processed {len(data)} data points.")
    return pd.DataFrame(data)

# --- HTML Generation ---
def generate_html(df):
    """Generates an HTML file with the data in a table."""
    html = f"""
    <html>
    <head>
        <title>Accelerator Duty Cycle</title>
        <style>
            table {{
                width: 50%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>
        <h1>Accelerator Duty Cycle</h1>
        {df.to_html(index=False)}
    </body>
    </html>
    """
    with open("index.html", "w") as f:
        f.write(html)

# --- Main ---
def main():
    """Main function."""
    credentials = get_credentials()
    if credentials:
        raw_data = get_accelerator_data(credentials)
        df = process_data(raw_data)
        if not df.empty:
            generate_html(df)
            print("Successfully generated index.html")
        else:
            print("No accelerator data found.")

if __name__ == "__main__":
    main()