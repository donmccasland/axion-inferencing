
import google.auth
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    logging.info("Attempting to get Google Cloud credentials...")
    try:
        credentials, project = google.auth.default()
        logging.info("Successfully got Google Cloud credentials.")
        if credentials:
            logging.info(f"Credentials token: {credentials.token}")
        if project:
            logging.info(f"Project ID: {project}")
    except Exception as e:
        logging.error(f"Error getting Google Cloud credentials: {e}")

if __name__ == "__main__":
    main()
