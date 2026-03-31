"""Slack integration for Network Monitor alerts"""
import requests
import json
from config import SLACK_WEBHOOK_URL, SLACK_ENABLED
from advanced_alerts import AlertSeverity, AlertType


def send_slack_alert(device_ip, alert_type, severity, message, details=None):
    """Send alert to Slack channel"""
    if not SLACK_ENABLED or not SLACK_WEBHOOK_URL:
        return False
    
    severity_colors = {
        AlertSeverity.CRITICAL: "#cc0000",
        AlertSeverity.HIGH: "#ff6600",
        AlertSeverity.MEDIUM: "#ffcc00",
        AlertSeverity.LOW: "#0066cc",
        AlertSeverity.INFO: "#00aa00"
    }
    
    severity_names = {
        AlertSeverity.CRITICAL: "🚨 CRITICAL",
        AlertSeverity.HIGH: "⚠️ HIGH",
        AlertSeverity.MEDIUM: "⚡ MEDIUM",
        AlertSeverity.LOW: "ℹ️ LOW",
        AlertSeverity.INFO: "✅ INFO"
    }
    
    color = severity_colors.get(severity, "#0066cc")
    severity_label = severity_names.get(severity, "UNKNOWN")
    
    alert_type_name = alert_type.value if hasattr(alert_type, 'value') else str(alert_type)
    
    payload = {
        "attachments": [
            {
                "color": color,
                "title": f"{severity_label} - {alert_type_name}",
                "text": message,
                "fields": [
                    {"title": "Device", "value": device_ip, "short": True},
                    {"title": "Alert Type", "value": alert_type_name, "short": True},
                    {"title": "Severity", "value": severity_label, "short": True},
                ]
            }
        ]
    }
    
    if details:
        payload["attachments"][0]["fields"].append(
            {"title": "Details", "value": details, "short": False}
        )
    
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Slack notification failed: {e}")
        return False
