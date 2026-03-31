"""Alert testing module to verify all alert channels"""
from advanced_alerts import send_alert_email, AlertSeverity, AlertType
from slack_integration import send_slack_alert
from slack_integration import send_slack_alert
from webhook_alerts import send_webhook_alert
from config import (
    SLACK_ENABLED, WEBHOOKS_ENABLED,
    EMAIL_SENDER, EMAIL_RECEIVER
)
import time


def test_email_alert():
    """Test email alert"""
    print("\n[EMAIL] Testing Email Alert...")
    
    if EMAIL_SENDER == "youremail@gmail.com" or EMAIL_RECEIVER == "receiver@gmail.com":
        print("[WARN] Using simulated email dispatcher since .env is missing.")
    
    try:
        result = send_alert_email(
            device_ip=f"TEST_{int(time.time())}",
            alert_type=AlertType.DEVICE_DOWN,
            severity=AlertSeverity.CRITICAL,
            message="This is a test email alert from Network Monitor Pro",
            details="Test Details"
        )
        if result:
            print("[OK] Email alert sent successfully!")
            return True
        else:
            print("[FAIL] Email alert failed to send")
            return False
    except Exception as e:
        print(f"[FAIL] Email alert error: {e}")
        return False


def test_slack_alert():
    """Test Slack alert"""
    print("\n[SLACK] Testing Slack Alert...")
    if not SLACK_ENABLED:
        print("[WARN] Slack is disabled in config.py")
        return False
    
    try:
        result = send_slack_alert(
            device_ip="TEST_DEVICE",
            alert_type="Test Alert",
            severity=AlertSeverity.CRITICAL,
            message="This is a test Slack alert from Network Monitor Pro"
        )
        if result:
            print("[OK] Slack alert sent successfully!")
            return True
        else:
            print("[FAIL] Slack alert failed to send")
            return False
    except Exception as e:
        print(f"[FAIL] Slack alert error: {e}")
        return False


def test_webhook_alert():
    """Test webhook alert"""
    print("\n[WEBHOOK] Testing Webhook Alert...")
    if not WEBHOOKS_ENABLED:
        print("[WARN] Webhooks are disabled in config.py")
        return False
    
    try:
        result = send_webhook_alert(
            device_ip="TEST_DEVICE",
            alert_type="Test Alert",
            severity="CRITICAL",
            message="This is a test webhook alert from Network Monitor Pro",
            details={"test": True, "timestamp": time.time()}
        )
        if result:
            print("[OK] Webhook alert sent successfully!")
            return True
        else:
            print("[FAIL] Webhook alert failed to send")
            return False
    except Exception as e:
        print(f"[FAIL] Webhook alert error: {e}")
        return False


def test_database_alert():
    """Test database alert storage"""
    print("\n[DATABASE] Testing Database Alert Storage...")
    try:
        from advanced_alerts import create_alert_record
        create_alert_record(
            device_ip="TEST_DEVICE",
            alert_type=AlertType.DEVICE_DOWN,
            severity=AlertSeverity.CRITICAL,
            message="This is a test database alert"
        )
        print("[OK] Database alert stored successfully!")
        return True
    except Exception as e:
        print(f"[FAIL] Database alert error: {e}")
        return False


def run_all_tests():
    """Run all alert tests"""
    print("\n" + "="*60)
    print("NETWORK MONITOR PRO - ALERT TESTING")
    print("="*60)
    
    results = {
        "Email": test_email_alert(),
        "Slack": test_slack_alert(),
        "Webhook": test_webhook_alert(),
        "Database": test_database_alert()
    }
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for channel, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{channel:15} : {status}")
    
    print("="*60)
    print(f"Total: {passed}/{total} tests passed")
    print("="*60 + "\n")
    
    return passed == total


def test_specific_alert(alert_type):
    """Test specific alert type"""
    alert_type = alert_type.lower()
    
    if alert_type == "email":
        return test_email_alert()
    elif alert_type == "slack":
        return test_slack_alert()
    elif alert_type == "webhook":
        return test_webhook_alert()
    elif alert_type == "database":
        return test_database_alert()
    else:
        print(f"Unknown alert type: {alert_type}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        alert_type = sys.argv[1]
        print(f"\nTesting {alert_type} alert...")
        test_specific_alert(alert_type)
    else:
        run_all_tests()
