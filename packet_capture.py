"""Packet capturing and analysis module - Enhanced for Wireshark layout"""
import socket
import struct
import textwrap
import threading
import time
import random
from collections import defaultdict, deque
from datetime import datetime


class PacketCapture:
    def __init__(self, interface=None, packet_count=0):
        self.interface = interface
        self.packet_count = packet_count
        self.packets = deque(maxlen=2000)
        self.stats = defaultdict(int)
        self.running = False
        self.error = None
        self.is_simulated = False
        self._packet_index = 0
        
    def start_capture(self):
        """Start packet capture or fallback to simulation mode on PermissionError"""
        self.running = True
        try:
            if self.interface:
                sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
                sock.bind((self.interface, 0))
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
                sock.bind((socket.gethostbyname(socket.gethostname()), 0))
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
            
            count = 0
            while self.running and (self.packet_count == 0 or count < self.packet_count):
                raw_buffer = sock.recvfrom(65535)
                raw_data = raw_buffer[0]
                self._packet_index += 1
                packet_info = self.parse_packet(raw_data, self._packet_index)
                self.packets.append(packet_info)
                self.update_stats(packet_info)
                count += 1
                
        except Exception as e:
            err_str = str(e).lower()
            if "10013" in err_str or "forbidden" in err_str or "permission" in err_str:
                self.error = "[WinError 10013] Simulation Mode Active"
                self.is_simulated = True
                self.run_simulation_loop()
            else:
                self.error = str(e)
                print(f"Packet capture error: {e}")
        finally:
            self.running = False
            if 'sock' in locals():
                try:
                    sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
                except:
                    pass
                sock.close()

    def run_simulation_loop(self):
        """Generates realistic mock packet streams resembling Wireshark logs"""
        count = 0
        protocols = ["TCP"] * 60 + ["UDP"] * 25 + ["ICMP"] * 5 + ["DNS", "TLSv1.2"] * 5
        
        while self.running and (self.packet_count == 0 or count < self.packet_count):
            time.sleep(random.uniform(0.01, 0.2)) # Realistic rapid burst timing
            
            self._packet_index += 1
            proto = random.choice(protocols)
            size = random.randint(54, 1514)
            src_ip = f"192.168.1.{random.randint(2, 254)}"
            dst_ip = f"{random.randint(1, 254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}" # External
            
            # 80/20 rule: sometimes internal to internal
            if random.random() > 0.8:
                dst_ip = "192.168.1.1" # Gateway
                
            src_port = random.randint(1024, 65535)
            dst_port = 443 if proto in ("TCP", "TLSv1.2") else (53 if proto == "DNS" else random.randint(1024, 65535))
            
            info = "Unknown"
            if proto == "TCP":
                flags = random.choice(["[SYN]", "[PSH, ACK]", "[ACK]", "[FIN, ACK]"])
                info = f"{src_port} \u2192 {dst_port} {flags} Seq={random.randint(0, 1000)} Win={random.randint(1000, 65000)} Len={size}"
            elif proto == "UDP":
                info = f"{src_port} \u2192 {dst_port} Len={size}"
            elif proto == "ICMP":
                info = f"Echo (ping) {random.choice(['request', 'reply'])}  id={random.randint(1, 1000)} seq={count}/0 ttl=64"
                src_port, dst_port = 'N/A', 'N/A'
            elif proto == "DNS":
                info = f"Standard query 0x{random.randint(1000,9999):x} A google.com"
            elif proto == "TLSv1.2":
                info = "Application Data"
                
            # Generate dummy payload bytes to display a realistic Hex dump
            raw_hex = " ".join([f"{random.randint(0, 255):02x}" for _ in range(min(size, 80))])
            
            packet_info = {
                'no': self._packet_index,
                'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3], # Millisecond precision
                'protocol': proto,
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_port': src_port,
                'dst_port': dst_port,
                'size': size,
                'info': info,
                'hex_dump': raw_hex
            }
            
            self.packets.append(packet_info)
            self.update_stats(packet_info)
            count += 1

    def parse_packet(self, raw_data, pkt_index):
        """Parse packet data and extract Wireshark-like fields"""
        try:
            ipv4_packet = self.parse_ipv4(raw_data, pkt_index)
            if ipv4_packet:
                return ipv4_packet
        except:
            pass
            
        hex_dump = " ".join([f"{b:02x}" for b in raw_data[:80]])
        
        return {
            'no': pkt_index,
            'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3],
            'protocol': 'Unknown',
            'src_ip': 'N/A',
            'dst_ip': 'N/A',
            'src_port': 'N/A',
            'dst_port': 'N/A',
            'size': len(raw_data),
            'info': 'Raw Packet Data',
            'hex_dump': hex_dump
        }
    
    def parse_ipv4(self, data, pkt_index):
        """Parse IPv4 packet deeply enough for rich UI"""
        version_header_length = data[0]
        header_length = (version_header_length & 15) * 4
        ttl, proto, src, target = struct.unpack('! 8x B B 2x 4s 4s', data[:20])
        
        src_ip = self.format_ipv4(src)
        dst_ip = self.format_ipv4(target)
        
        protocol_str = 'IPv4'
        src_port = 'N/A'
        dst_port = 'N/A'
        info = f"IPv4 header, TTL={ttl}"
        
        if proto == 1:
            protocol_str = 'ICMP'
            info = f"Echo Ping Request/Reply TTL={ttl}"
        elif proto == 6:
            protocol_str = 'TCP'
            if len(data) >= header_length + 4:
                src_port, dst_port = struct.unpack('! H H', data[header_length:header_length+4])
                info = f"{src_port} \u2192 {dst_port} [TCP Segment] Len={len(data)}"
        elif proto == 17:
            protocol_str = 'UDP'
            if len(data) >= header_length + 4:
                src_port, dst_port = struct.unpack('! H H', data[header_length:header_length+4])
                info = f"{src_port} \u2192 {dst_port} Len={len(data)}"
        
        hex_dump = " ".join([f"{b:02x}" for b in data[:120]]) # Include up to 120 bytes of payload for inspect
        
        return {
            'no': pkt_index,
            'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3],
            'protocol': protocol_str,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'src_port': src_port,
            'dst_port': dst_port,
            'size': len(data),
            'info': info,
            'hex_dump': hex_dump
        }
    
    @staticmethod
    def format_ipv4(bytes_addr):
        return '.'.join(map(str, bytes_addr))
    
    def update_stats(self, packet_info):
        self.stats['total_packets'] += 1
        self.stats['total_bytes'] += packet_info['size']
        # Map common subprotocols back to TCP/UDP for overall statistics
        core_proto = "TCP" if packet_info['protocol'] in ("TCP", "TLSv1.2") else ("UDP" if packet_info['protocol'] == "DNS" else packet_info['protocol'])
        self.stats[f"protocol_{core_proto}"] += 1
    
    def get_stats(self):
        return dict(self.stats)
    
    def get_packets(self, limit=100):
        return list(self.packets)[-limit:]
    
    def stop_capture(self):
        self.running = False


def start_packet_capture_thread(interface=None, packet_count=0):
    capture = PacketCapture(interface, packet_count)
    thread = threading.Thread(target=capture.start_capture, daemon=True)
    thread.start()
    return capture
