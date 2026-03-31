"""Webhook support for custom integrations"""
import requests
import json
from datetime import datetime
from config import WEBHOOKS_ENABLED, WEBHOOK_URLS


def send_webhook_alert(device_ip, alert_type, severity, message, details=None):
    """Send alert to configured webhooks"""
    if not WEBHOOKS_ENABLED or not WEBHOOK_URLS:
        return False
    
    payload = {
        "timestamp": datetime.now().isoformat(),
        "device": device_ip,
        "alert_type": alert_type,
        "severity": severity,
        "message": message,
        "details": details or {}
    }
    
    results = []
    for webhook_url in WEBHOOK_URLS:
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=5,
                headers={"Content-Type": "application/json"}
            )
            results.append(response.status_code == 200)
        except Exception as e:
            print(f"Webhook notification failed for {webhook_url}: {e}")
            results.append(False)
    
    return all(results) if results else False
