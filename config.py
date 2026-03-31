# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


DEVICES = [
    "8.8.8.8",        # Google DNS
    "1.1.1.1",        # Cloudflare DNS
    "192.168.1.1"     # Your WiFi Router
]

# SNMP-enabled devices (IP: community_string)
# Add your routers/switches here with their SNMP community strings
SNMP_DEVICES = {
    # "192.168.1.1": "public",  # Example: Your router
    # "192.168.1.10": "public", # Example: Your switch
}

SNMP_PORT = 161
SNMP_TIMEOUT = 2  # seconds

LATENCY_THRESHOLD = 200      # ms — alert if latency crosses this
PACKET_LOSS_THRESHOLD = 20   # % — alert if loss crosses this
CHECK_INTERVAL = 10          # seconds between each check

EMAIL_SENDER = os.getenv("EMAIL_SENDER", "youremail@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_app_password")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "receiver@gmail.com")

LOG_FILE = "logs/network_log.csv"

# Database settings
USE_DATABASE = True  # Set to False to use CSV only
DATA_RETENTION_DAYS = 30  # Auto-cleanup data older than this

# Slack Integration
SLACK_ENABLED = os.getenv("SLACK_ENABLED", "False").lower() in ("true", "1", "t")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/YOUR/WEBHOOK/URL")

# Webhook Support
WEBHOOKS_ENABLED = False
WEBHOOK_URLS = [
    # "https://your-webhook-endpoint.com/alerts",
]

# REST API
API_ENABLED = True
API_PORT = 5000

# Predictive Alerts
PREDICTIVE_ALERTS_ENABLED = True
