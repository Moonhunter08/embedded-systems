import uasyncio as asyncio
import gc
import utime

# ================= FIREWALL CONFIG =================
ALLOWED_PATHS = {"/", "/status", "/table_rows"}
ALLOWED_SUBNET = "192.168.4."
MAX_REQUESTS = 10        # max requests
WINDOW_MS = 5000         # per 5 seconds


def ip_allowed(peer):
    if not peer:
        return False
    ip = peer[0]
    return ip.startswith(ALLOWED_SUBNET)

CLIENT_HITS = {}
def rate_limited(ip):
    now = utime.ticks_ms()
    hits = CLIENT_HITS.get(ip, [])
    hits = [t for t in hits if utime.ticks_diff(now, t) < WINDOW_MS]
    hits.append(now)
    CLIENT_HITS[ip] = hits
    return len(hits) > MAX_REQUESTS

class BufferedWriter:
    """Buffers small writes into larger packets for speed."""
    def __init__(self, writer, size=2048):
        self.writer = writer
        self.buffer = bytearray()
        self.size = size
    
    async def write(self, data):
        if not isinstance(data, (bytes, bytearray)):
            data = str(data).encode('utf-8')
        self.buffer.extend(data)
        if len(self.buffer) >= self.size:
            await self.flush()

    async def flush(self):
        if self.buffer:
            self.writer.write(self.buffer)
            await self.writer.drain()
            self.buffer = bytearray()

# --- HELPER: Streams ONLY the table rows (for live updates) ---
async def stream_rows_only(buf_writer, csv_data):
    if not csv_data: return
    
    lines = csv_data.split("\n")
    rows = [line.strip() for line in lines if line.strip()]
    
    # Skip header (index 0) and stream the rest
    if len(rows) > 1:
        for line in rows[1:]:
            cols = line.split(",")
            await buf_writer.write(b"<tr>")
            for col in cols:
                await buf_writer.write(b"<td>" + col.encode('utf-8') + b"</td>")
            await buf_writer.write(b"</tr>\n")

# --- HELPER: Streams the FULL table (for first load) ---
async def stream_full_table(buf_writer, csv_data):
    if not csv_data: return
    
    lines = csv_data.split("\n")
    await buf_writer.write(b"<table border='1' cellpadding='6'>\n")
    
    is_header = True
    for line in lines:
        if not line.strip(): continue
        cols = line.strip().split(",")
        
        if is_header:
            await buf_writer.write(b"<thead><tr>")
            for col in cols:
                await buf_writer.write(b"<th>" + col.encode('utf-8') + b"</th>")
            await buf_writer.write(b"</tr></thead><tbody>\n")
            is_header = False
        else:
            await buf_writer.write(b"<tr>")
            for col in cols:
                await buf_writer.write(b"<td>" + col.encode('utf-8') + b"</td>")
            await buf_writer.write(b"</tr>\n")
            
    await buf_writer.write(b"</tbody></table>")

async def stream_file(buf_writer, filename):
    try:
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(1024)
                if not chunk: break
                await buf_writer.write(chunk)
    except OSError: pass

async def handle_client(reader, writer, csv_interface):
    buf_writer = BufferedWriter(writer)
    try:
        peer = writer.get_extra_info("peername")
        ip = peer[0] if peer else "unknown"

        # FIREWALL: IP FILTER
        if not ip_allowed(peer):
            await buf_writer.write(b"HTTP/1.1 403 Forbidden\r\n\r\n")
            await buf_writer.flush()
            return

        # FIREWALL: RATE LIMIT
        if rate_limited(ip):
            await buf_writer.write(b"HTTP/1.1 429 Too Many Requests\r\n\r\n")
            await buf_writer.flush()
            return

        request_line = await reader.readline()
        if not request_line: return
        
        request_str = request_line.decode('utf-8').strip()
        parts = request_str.split(" ")
        if len(parts) < 3:
            return

        method = parts[0]
        path = parts[1]

        # Consume headers
        while True:
            header = await reader.readline()
            if header == b'\r\n' or header == b'\n' or not header: break

        # FIREWALL: METHOD FILTER
        if method != "GET":
            await buf_writer.write(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            await buf_writer.flush()
            return

        # FIREWALL: PATH ALLOW-LIST
        if path not in ALLOWED_PATHS:
            await buf_writer.write(b"HTTP/1.1 403 Forbidden\r\n\r\n")
            await buf_writer.flush()
            return

        # --- ROUTE: /status ---
        if path == "/status":
            count = getattr(csv_interface, 'impact_count', 0)
            await buf_writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n")
            await buf_writer.write(str(count))
            await buf_writer.flush()

        # --- ROUTE 2: /table_rows (Get ONLY new HTML rows) ---
        elif path == '/table_rows':
            await buf_writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            csv_data = csv_interface.get_content()
            await stream_rows_only(buf_writer, csv_data)
            await buf_writer.flush()
            del csv_data
            gc.collect()

        # --- ROUTE 3: / (Full Page Load) ---
        else:
            await buf_writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            page_load_count = getattr(csv_interface, 'impact_count', 0)
            
            try:
                with open("webserver/index.html", "r") as f:
                    for line in f:
                        if "{{CSS_PLACEHOLDER}}" in line:
                            await stream_file(buf_writer, "webserver/style.css")
                        elif "{{TABLE_PLACEHOLDER}}" in line:
                            csv_data = csv_interface.get_content()
                            await stream_full_table(buf_writer, csv_data)
                            del csv_data
                            gc.collect()
                        else:
                            await buf_writer.write(line)
                
                # --- JAVASCRIPT FOR LIVE UPDATES ---
                # This script replaces the tbody content instead of reloading the page
                js_script = f"""
                <script>
                    let localCount = {page_load_count};
                    const tbody = document.querySelector("tbody");

                    setInterval(() => {{
                        fetch('/status')
                        .then(r => r.text())
                        .then(serverCount => {{
                            if (serverCount != localCount) {{
                                fetch('/table_rows')
                                .then(r => r.text())
                                .then(html => {{
                                    tbody.innerHTML = html;
                                    localCount = serverCount;
                                }});
                            }}
                        }});
                    }}, 2000); 
                </script>
                """
                await buf_writer.write(js_script)

            except OSError:
                await buf_writer.write(b"<h1>Error: index.html not found</h1>")
            
            await buf_writer.flush()

    except Exception as e:
        print("Handler Error:", e)
    finally:
        try:
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except: pass

async def run_server(csv_interface):
    print("Starting Live-Update Web Server...")
    async def serve_wrapper(reader, writer):
        await handle_client(reader, writer, csv_interface)
    
    server = await asyncio.start_server(serve_wrapper, "0.0.0.0", 80)
    while True:
        await asyncio.sleep(500)
