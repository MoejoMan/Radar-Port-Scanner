import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Callable, Optional

class PortScanner:
    """Multi-threaded port scanner with progress callbacks"""
    
    # Port categories as class constants
    PORT_CATEGORIES = {
        "web": {80: "HTTP", 443: "HTTPS", 8080: "HTTP-alt"},
        "database": {3306: "MySQL", 5432: "PostgreSQL", 1433: "MSSQL"},
        "email": {25: "SMTP", 110: "POP3", 143: "IMAP"},
        "admin": {22: "SSH", 3389: "RDP", 5900: "VNC"}
    }
    
    def __init__(self, timeout: float = 0.6, threads: int = 200):
        """
        Initialize scanner
        
        Args:
            timeout: Socket timeout in seconds
            threads: Number of concurrent threads
        """
        self.timeout = timeout
        self.threads = threads
        self.progress_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        """
        Set callback for progress updates
        
        Args:
            callback: Function that takes (scanned_count, total_count)
        """
        self.progress_callback = callback


    
    def scan(self, target: str, ports: List[int]) -> Dict:
        """
        Scan target for open ports
        
        Args:
            target: IP address or hostname
            ports: List of port numbers to scan
            
        Returns:
            Dict with keys:
                - success: bool
                - error: str or None
                - results: Dict with scan data or None
        """
        # Resolve hostname to IP
        ip = self._resolve_host(target)
        if not ip:
            return {
                "success": False,
                "error": f"Could not resolve {target}",
                "results": None
            }
        
        # Run scan
        start_time = datetime.utcnow()
        open_ports, closed_ports, filtered_ports = [], [], []
        total_ports = len(ports)
        scanned_count = 0
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self._scan_port, ip, p): p for p in ports}
            
            for future in as_completed(futures):
                scanned_count += 1
                
                # Emit progress
                if self.progress_callback:
                    self.progress_callback(scanned_count, total_ports)
                
                try:
                    result = future.result()
                except Exception:
                    result = None
                
                if result:
                    status = result["status"]
                    if status == "open":
                        port_num = result["port"]
                        banner = self._grab_banner(ip, port_num)
                        open_ports.append({
                            "port": port_num,
                            "status": status,
                            "banner": banner
                        })
                    elif status == "closed":
                        closed_ports.append(result)
                    else:
                        filtered_ports.append(result)
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Return clean data
        return {
            "success": True,
            "error": None,
            "results": {
                "target": target,
                "ip": ip,
                "timestamp_utc": start_time.strftime("%Y%m%dT%H%M%SZ"),
                "duration_s": duration,
                "open_ports": sorted(open_ports, key=lambda x: x["port"]),
                "closed_ports": sorted(closed_ports, key=lambda x: x["port"]),
                "filtered_ports": sorted(filtered_ports, key=lambda x: x["port"]),
                "summary": {
                    "total_open": len(open_ports),
                    "total_closed": len(closed_ports),
                    "total_filtered": len(filtered_ports)
                }
            }
        }
    
    def _scan_port(self, host: str, port: int) -> Dict:
        """Scan a single port"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        try:
            res = s.connect_ex((host, port))
            s.close()
            if res == 0:
                return {"port": port, "status": "open"}
            else:
                return {"port": port, "status": "closed"}
        except Exception:
            return {"port": port, "status": "filtered"}
    
    def _grab_banner(self, host: str, port: int) -> Optional[str]:
        """Try to grab service banner from open port"""
        try:
            s = socket.socket()
            s.settimeout(2)
            s.connect((host, port))
            banner = s.recv(1024).decode().strip()
            s.close()
            return banner if banner else None
        except Exception:
            return None
    
    def _resolve_host(self, host: str) -> Optional[str]:
        """Resolve hostname to IP address"""
        try:
            return socket.gethostbyname(host)
        except Exception:
            return None
    
    @staticmethod
    def compress_port_ranges(ports_list: List[Dict]) -> List[str]:
        """Compress consecutive ports into ranges for display"""
        if not ports_list:
            return []
        
        ports_list = sorted(ports_list, key=lambda x: x["port"])
        compressed = []
        start = prev = ports_list[0]["port"]
        
        for p in ports_list[1:]:
            if p["port"] == prev + 1:
                prev = p["port"]
            else:
                if start != prev:
                    compressed.append(f"{start}-{prev}")
                else:
                    compressed.append(str(start))
                start = prev = p["port"]
        
        if start != prev:
            compressed.append(f"{start}-{prev}")
        else:
            compressed.append(str(start))
        
        return compressed