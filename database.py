# database.py
# SQLite database management for Network Monitor

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_FILE = "logs/network_monitor.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize database with required tables"""
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Ping monitoring table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ping_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                ip TEXT NOT NULL,
                status TEXT NOT NULL,
                latency REAL,
                health_score REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ping_timestamp 
            ON ping_logs(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ping_ip 
            ON ping_logs(ip)
        """)
        
        # SNMP monitoring table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snmp_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                ip TEXT NOT NULL,
                status TEXT NOT NULL,
                cpu_load REAL,
                memory_used_pct REAL,
                system_desc TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snmp_timestamp 
            ON snmp_logs(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snmp_ip 
            ON snmp_logs(ip)
        """)
        
        # Flow data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flow_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                exporter TEXT NOT NULL,
                src_ip TEXT NOT NULL,
                dst_ip TEXT NOT NULL,
                src_port INTEGER,
                dst_port INTEGER,
                protocol TEXT,
                packets INTEGER,
                bytes INTEGER,
                duration REAL,
                flow_type TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_timestamp 
            ON flow_logs(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_src_ip 
            ON flow_logs(src_ip)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_dst_ip 
            ON flow_logs(dst_ip)
        """)
        
        # Alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                device_ip TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity INTEGER NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                status TEXT DEFAULT 'OPEN',
                acknowledged_by TEXT,
                acknowledged_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alert_timestamp 
            ON alerts(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alert_device 
            ON alerts(device_ip)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alert_severity 
            ON alerts(severity)
        """)
        
        # Devices table (for device metadata)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT UNIQUE NOT NULL,
                name TEXT,
                device_type TEXT,
                location TEXT,
                snmp_enabled BOOLEAN DEFAULT 0,
                snmp_community TEXT,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME
            )
        """)
        
        conn.commit()
        print("[*] Database initialized successfully")

def log_ping_result(ip, status, latency, health_score, timestamp=None):
    """Log ping monitoring result to database"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ping_logs (timestamp, ip, status, latency, health_score)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, ip, status, latency, health_score))
        
        # Update last_seen in devices table
        cursor.execute("""
            INSERT INTO devices (ip, last_seen) 
            VALUES (?, ?)
            ON CONFLICT(ip) DO UPDATE SET last_seen = ?
        """, (ip, timestamp, timestamp))

def log_snmp_result(ip, status, cpu_load, memory_pct, sys_desc, timestamp=None):
    """Log SNMP monitoring result to database"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO snmp_logs (timestamp, ip, status, cpu_load, memory_used_pct, system_desc)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, ip, status, cpu_load, memory_pct, sys_desc))

def log_flow_data(flow):
    """Log flow data to database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO flow_logs (timestamp, exporter, src_ip, dst_ip, src_port, dst_port,
                                  protocol, packets, bytes, duration, flow_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (flow['timestamp'], flow['exporter'], flow['src_ip'], flow['dst_ip'],
               flow['src_port'], flow['dst_port'], flow['protocol'],
               flow['packets'], flow['bytes'], flow['duration'], flow['type']))

def get_latest_ping_status():
    """Get latest ping status for all devices"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ip, timestamp, status, latency, health_score
            FROM ping_logs
            WHERE (ip, timestamp) IN (
                SELECT ip, MAX(timestamp)
                FROM ping_logs
                GROUP BY ip
            )
            ORDER BY ip
        """)
        return cursor.fetchall()

def get_ping_history(ip=None, hours=24):
    """Get ping history for specific IP or all IPs"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if ip:
            cursor.execute("""
                SELECT timestamp, ip, status, latency, health_score
                FROM ping_logs
                WHERE ip = ? AND timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
            """, (ip, hours))
        else:
            cursor.execute("""
                SELECT timestamp, ip, status, latency, health_score
                FROM ping_logs
                WHERE timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
            """, (hours,))
        
        return cursor.fetchall()

def get_latest_snmp_status():
    """Get latest SNMP status for all devices"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ip, timestamp, status, cpu_load, memory_used_pct, system_desc
            FROM snmp_logs
            WHERE (ip, timestamp) IN (
                SELECT ip, MAX(timestamp)
                FROM snmp_logs
                GROUP BY ip
            )
            ORDER BY ip
        """)
        return cursor.fetchall()

def get_snmp_history(ip=None, hours=24):
    """Get SNMP history for specific IP or all IPs"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if ip:
            cursor.execute("""
                SELECT timestamp, ip, status, cpu_load, memory_used_pct, system_desc
                FROM snmp_logs
                WHERE ip = ? AND timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
            """, (ip, hours))
        else:
            cursor.execute("""
                SELECT timestamp, ip, status, cpu_load, memory_used_pct, system_desc
                FROM snmp_logs
                WHERE timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
            """, (hours,))
        
        return cursor.fetchall()

def cleanup_old_data(days=30):
    """Remove data older than specified days"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM ping_logs 
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        """, (days,))
        
        cursor.execute("""
            DELETE FROM snmp_logs 
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        """, (days,))
        
        deleted = cursor.rowcount
        conn.commit()
        return deleted

def get_database_stats():
    """Get database statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM ping_logs")
        ping_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM snmp_logs")
        snmp_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM devices")
        device_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM flow_logs")
        flow_count = cursor.fetchone()[0]
        
        # Get database file size
        db_size = os.path.getsize(DB_FILE) if os.path.exists(DB_FILE) else 0
        
        return {
            'ping_records': ping_count,
            'snmp_records': snmp_count,
            'devices': device_count,
            'flow_records': flow_count,
            'db_size_mb': round(db_size / (1024 * 1024), 2)
        }

def get_top_talkers(hours=1, limit=10):
    """Get top bandwidth consumers"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT src_ip, SUM(bytes) as total_bytes, COUNT(*) as flow_count
            FROM flow_logs
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            GROUP BY src_ip
            ORDER BY total_bytes DESC
            LIMIT ?
        """, (hours, limit))
        return cursor.fetchall()

def get_protocol_distribution(hours=1):
    """Get traffic distribution by protocol"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT protocol, SUM(bytes) as total_bytes, COUNT(*) as flow_count
            FROM flow_logs
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            GROUP BY protocol
            ORDER BY total_bytes DESC
        """, (hours,))
        return cursor.fetchall()

def get_flow_summary(hours=1):
    """Get flow data summary"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_flows,
                SUM(bytes) as total_bytes,
                SUM(packets) as total_packets,
                AVG(duration) as avg_duration
            FROM flow_logs
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
        """, (hours,))
        return cursor.fetchone()
