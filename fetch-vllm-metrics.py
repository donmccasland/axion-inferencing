import requests
import google.auth
import google.auth.transport.requests
import logging
import json

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
def get_vllm_generation_tokens_data(_credentials):
    """Fetches vllm:generation_tokens_total/counter data from the Google Cloud Monitoring API."""
    logging.info("Refreshing credentials...")
    try:
        _credentials.refresh(google.auth.transport.requests.Request())
    except Exception as e:
        logging.error(f"Error refreshing credentials: {e}")
        return None

    logging.info("Fetching vllm:generation_tokens_total/counter data from Monitoring API...")
    query = "vllm:generation_tokens_total"

    url = f"https://monitoring.googleapis.com/v1/projects/{PROJECT_ID}/location/global/prometheus/api/v1/query"
    
    headers = {
        "Authorization": f"Bearer {_credentials.token}",
    }
    
    params = {
        "query": query
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        logging.info("Successfully fetched vllm:generation_tokens_total/counter data from Monitoring API.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making request to Monitoring API: {e}")
        return None

# --- Main ---
def main():
    """Main function for the script."""
    logging.info("Starting script to fetch vLLM metrics.")

    credentials = get_credentials()
    
    if not credentials:
        logging.error("Could not get Google Cloud credentials. Exiting.")
        return

    vllm_data = get_vllm_generation_tokens_data(credentials)

    if vllm_data:
        print(json.dumps(vllm_data, indent=2))

if __name__ == "__main__":
    main()
