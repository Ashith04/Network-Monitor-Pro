# advanced_alerts.py
# Professional-grade alert system with multiple severity levels

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from enum import Enum
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER
from database import get_db_connection

# Alert Severity Levels
class AlertSeverity(Enum):
    CRITICAL = 1    # Immediate action required
    HIGH = 2        # Urgent attention needed
    MEDIUM = 3      # Should be addressed soon
    LOW = 4         # Monitor and plan
    INFO = 5        # Informational only

# Alert Types
class AlertType(Enum):
    DEVICE_DOWN = "Device Offline"
    HIGH_LATENCY = "High Latency"
    HIGH_CPU = "High CPU Usage"
    HIGH_MEMORY = "High Memory Usage"
    BANDWIDTH_SPIKE = "Bandwidth Spike"
    ANOMALY = "Anomaly Detected"
    CONFIG_CHANGE = "Configuration Change"
    AUTH_FAILED = "Authentication Failed"

# Track sent alerts to prevent storms
alert_history = {}
suppressed_alerts = set()

def create_alert_record(device_ip, alert_type, severity, message, details=None):
    """Create alert record in database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (timestamp, device_ip, alert_type, severity, message, details, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            device_ip,
            alert_type.value,
            severity.value,
            message,
            details,
            'OPEN'
        ))

def get_severity_color(severity):
    """Get color for severity level"""
    colors = {
        AlertSeverity.CRITICAL: "#dc2626",  # Red
        AlertSeverity.HIGH: "#ea580c",      # Orange
        AlertSeverity.MEDIUM: "#f59e0b",    # Amber
        AlertSeverity.LOW: "#3b82f6",       # Blue
        AlertSeverity.INFO: "#10b981"       # Green
    }
    return colors.get(severity, "#6b7280")

def get_severity_emoji(severity):
    """Get emoji for severity level"""
    emojis = {
        AlertSeverity.CRITICAL: "🚨",
        AlertSeverity.HIGH: "⚠️",
        AlertSeverity.MEDIUM: "⚡",
        AlertSeverity.LOW: "ℹ️",
        AlertSeverity.INFO: "✅"
    }
    return emojis.get(severity, "📢")

def create_html_email(device_ip, alert_type, severity, message, details=None, latency=None, status=None):
    """Create beautiful HTML email"""
    
    color = get_severity_color(severity)
    emoji = get_severity_emoji(severity)
    severity_name = severity.name
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f3f4f6;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: bold;
            }}
            .header p {{
                margin: 10px 0 0 0;
                font-size: 14px;
                opacity: 0.9;
            }}
            .content {{
                padding: 30px;
            }}
            .alert-box {{
                background-color: #f9fafb;
                border-left: 4px solid {color};
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .alert-box h2 {{
                margin: 0 0 10px 0;
                color: {color};
                font-size: 18px;
            }}
            .alert-box p {{
                margin: 8px 0;
                color: #374151;
                line-height: 1.6;
            }}
            .details {{
                background-color: #f3f4f6;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                font-family: 'Courier New', monospace;
                font-size: 13px;
            }}
            .details-row {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #e5e7eb;
            }}
            .details-row:last-child {{
                border-bottom: none;
            }}
            .details-label {{
                font-weight: bold;
                color: #6b7280;
                min-width: 150px;
            }}
            .details-value {{
                color: #111827;
                text-align: right;
            }}
            .severity-badge {{
                display: inline-block;
                background-color: {color};
                color: white;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .actions {{
                background-color: #f0f9ff;
                border: 1px solid #bfdbfe;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .actions h3 {{
                margin: 0 0 10px 0;
                color: #1e40af;
                font-size: 14px;
            }}
            .actions ul {{
                margin: 0;
                padding-left: 20px;
                color: #374151;
            }}
            .actions li {{
                margin: 5px 0;
                line-height: 1.6;
            }}
            .button {{
                display: inline-block;
                background-color: {color};
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                margin: 10px 5px 10px 0;
                font-weight: bold;
                font-size: 14px;
            }}
            .button:hover {{
                opacity: 0.9;
            }}
            .footer {{
                background-color: #f9fafb;
                padding: 20px;
                text-align: center;
                color: #6b7280;
                font-size: 12px;
                border-top: 1px solid #e5e7eb;
            }}
            .timestamp {{
                color: #9ca3af;
                font-size: 12px;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{emoji} {severity_name} Alert</h1>
                <p>Network Monitor Pro - Alert Notification</p>
            </div>
            
            <div class="content">
                <div class="alert-box">
                    <h2>{alert_type.value}</h2>
                    <p><strong>{message}</strong></p>
                    <div class="severity-badge">{severity_name}</div>
                </div>
                
                <div class="details">
                    <div class="details-row">
                        <span class="details-label">Device IP:</span>
                        <span class="details-value">{device_ip}</span>
                    </div>
                    <div class="details-row">
                        <span class="details-label">Alert Type:</span>
                        <span class="details-value">{alert_type.value}</span>
                    </div>
                    <div class="details-row">
                        <span class="details-label">Severity:</span>
                        <span class="details-value">{severity_name}</span>
                    </div>
                    <div class="details-row">
                        <span class="details-label">Timestamp:</span>
                        <span class="details-value">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span>
                    </div>
    """
    
    if status:
        html += f"""
                    <div class="details-row">
                        <span class="details-label">Status:</span>
                        <span class="details-value">{status}</span>
                    </div>
        """
    
    if latency:
        html += f"""
                    <div class="details-row">
                        <span class="details-label">Latency:</span>
                        <span class="details-value">{latency}ms</span>
                    </div>
        """
    
    if details:
        html += f"""
                    <div class="details-row">
                        <span class="details-label">Details:</span>
                        <span class="details-value">{details}</span>
                    </div>
        """
    
    html += """
                </div>
                
                <div class="actions">
                    <h3>Recommended Actions:</h3>
                    <ul>
    """
    
    # Add recommendations based on alert type
    if alert_type == AlertType.DEVICE_DOWN:
        html += """
                        <li>Check device power and network connectivity</li>
                        <li>Verify firewall rules allow ICMP</li>
                        <li>Check device configuration</li>
                        <li>Contact device administrator if issue persists</li>
        """
    elif alert_type == AlertType.HIGH_LATENCY:
        html += """
                        <li>Check network congestion</li>
                        <li>Verify device CPU and memory usage</li>
                        <li>Check for packet loss</li>
                        <li>Review network path and routing</li>
        """
    elif alert_type == AlertType.HIGH_CPU:
        html += """
                        <li>Check running processes</li>
                        <li>Review system logs</li>
                        <li>Consider load balancing</li>
                        <li>Upgrade hardware if needed</li>
        """
    elif alert_type == AlertType.HIGH_MEMORY:
        html += """
                        <li>Check memory usage by process</li>
                        <li>Review application logs</li>
                        <li>Consider memory optimization</li>
                        <li>Plan for hardware upgrade</li>
        """
    elif alert_type == AlertType.BANDWIDTH_SPIKE:
        html += """
                        <li>Identify traffic source</li>
                        <li>Check for DDoS attack</li>
                        <li>Review top talkers</li>
                        <li>Implement QoS if needed</li>
        """
    elif alert_type == AlertType.ANOMALY:
        html += """
                        <li>Review historical baseline</li>
                        <li>Check for unusual activity</li>
                        <li>Investigate root cause</li>
                        <li>Update alert thresholds if needed</li>
        """
    
    html += """
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="http://localhost:8501" class="button">View Dashboard</a>
                    <a href="http://localhost:8501" class="button" style="background-color: #6b7280;">View Alerts</a>
                </div>
            </div>
            
            <div class="footer">
                <p>Network Monitor Pro - Professional Network Monitoring</p>
                <p class="timestamp">Alert sent at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p>© 2024 Network Monitor. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_alert_email(device_ip, alert_type, severity, message, details=None, latency=None, status=None):
    """Send professional alert email"""
    
    # Check if alert should be suppressed
    alert_key = f"{device_ip}_{alert_type.value}"
    
    if alert_key in suppressed_alerts:
        return False
        
    # Prevent email overload (1-hour cooldown per alert type per device)
    last_sent = alert_history.get(alert_key)
    if last_sent:
        time_since = (datetime.now() - last_sent).total_seconds()
        if time_since < 3600:  # 3600 seconds = 1 hour
            return False
    
    try:
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[{severity.name}] {alert_type.value} - {device_ip}"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        
        # Create HTML content
        html_content = create_html_email(
            device_ip, alert_type, severity, message, 
            details, latency, status
        )
        
        # Attach HTML
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email (Real or Simulated)
        if EMAIL_SENDER != "youremail@gmail.com":
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        
        # Record alert
        create_alert_record(device_ip, alert_type, severity, message, details)
        
        # Mark as sent
        alert_history[alert_key] = datetime.now()
        
        print(f"[{severity.name}] Alert sent for {device_ip}: {alert_type.value}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to send alert: {e}")
        return False

def check_device_alerts(ip, status, latency, cpu=None, memory=None):
    """Check device and trigger appropriate alerts"""
    
    # Device Down Alert
    if status == "Offline":
        send_alert_email(
            ip,
            AlertType.DEVICE_DOWN,
            AlertSeverity.CRITICAL,
            f"Device {ip} is offline and not responding to ping",
            details="Device is unreachable"
        )
    
    # High Latency Alert
    elif latency and latency > 200:
        severity = AlertSeverity.HIGH if latency > 500 else AlertSeverity.MEDIUM
        send_alert_email(
            ip,
            AlertType.HIGH_LATENCY,
            severity,
            f"Latency to {ip} is {latency}ms (threshold: 200ms)",
            latency=latency,
            status=status
        )
    
    # High CPU Alert
    if cpu and cpu > 80:
        severity = AlertSeverity.CRITICAL if cpu > 95 else AlertSeverity.HIGH
        send_alert_email(
            ip,
            AlertType.HIGH_CPU,
            severity,
            f"CPU usage on {ip} is {cpu}% (threshold: 80%)",
            details=f"CPU: {cpu}%"
        )
    
    # High Memory Alert
    if memory and memory > 90:
        severity = AlertSeverity.CRITICAL if memory > 95 else AlertSeverity.HIGH
        send_alert_email(
            ip,
            AlertType.HIGH_MEMORY,
            severity,
            f"Memory usage on {ip} is {memory}% (threshold: 90%)",
            details=f"Memory: {memory}%"
        )

def suppress_alert(device_ip, alert_type_value, duration_minutes=30):
    """Suppress alert for specified duration"""
    alert_key = f"{device_ip}_{alert_type_value}"
    suppressed_alerts.add(alert_key)
    print(f"[INFO] Alert suppressed for {alert_key} for {duration_minutes} minutes")

def clear_suppression(device_ip, alert_type_value):
    """Clear alert suppression"""
    alert_key = f"{device_ip}_{alert_type_value}"
    suppressed_alerts.discard(alert_key)
    print(f"[INFO] Alert suppression cleared for {alert_key}")

def get_alert_history(device_ip=None, hours=24):
    """Get alert history from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if device_ip:
            cursor.execute("""
                SELECT * FROM alerts
                WHERE device_ip = ? AND timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
            """, (device_ip, hours))
        else:
            cursor.execute("""
                SELECT * FROM alerts
                WHERE timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
            """, (hours,))
        
        return cursor.fetchall()

def acknowledge_alert(alert_id, acknowledged_by=None):
    """Acknowledge an alert"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alerts
            SET status = 'ACKNOWLEDGED', acknowledged_by = ?, acknowledged_at = ?
            WHERE id = ?
        """, (acknowledged_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), alert_id))
