import uasyncio as asyncio
import gc

async def send_chunk(writer, data):
    """Helper to write data to the socket safely."""
    writer.write(data)
    await writer.drain()

async def stream_table(writer, csv_data):
    """
    Parses CSV and streams HTML table rows directly to the writer
    to avoid creating a massive HTML string in memory.
    """
    if not csv_data:
        return

    # Split lines lazily if possible, or just standard split
    # processing row by row to keep memory low
    lines = csv_data.split("\n")
    
    # Start Table
    await send_chunk(writer, b"<table border='1' cellpadding='6'>\n")
    
    is_header = True
    for line in lines:
        if not line.strip():
            continue
            
        cols = line.strip().split(",")
        
        if is_header:
            await send_chunk(writer, b"<thead><tr>")
            for col in cols:
                # varied encoding to handle potential special chars
                await send_chunk(writer, f"<th>{col}</th>".encode('utf-8'))
            await send_chunk(writer, b"</tr></thead><tbody>\n")
            is_header = False
        else:
            await send_chunk(writer, b"<tr>")
            for col in cols:
                await send_chunk(writer, f"<td>{col}</td>".encode('utf-8'))
            await send_chunk(writer, b"</tr>\n")
            
    await send_chunk(writer, b"</tbody></table>")

async def stream_file(writer, filename):
    """Reads a file in small chunks and sends them to the writer."""
    try:
        with open(filename, "r") as f:
            while True:
                # Read 512 bytes at a time
                chunk = f.read(512)
                if not chunk:
                    break
                await send_chunk(writer, chunk.encode('utf-8'))
    except OSError:
        print(f"Error: Could not read {filename}")

async def handle_client(reader, writer, csv_interface):
    try:
        # Read the request line (we just need to consume it)
        request_line = await reader.readline()
        if not request_line:
            return

        # Consume headers until the empty line
        while True:
            header = await reader.readline()
            if header == b'\r\n' or header == b'\n' or not header:
                break
        
        # 1. Send HTTP Headers
        await send_chunk(writer, b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")

        # 2. Stream the Template line by line
        try:
            with open("webserver/index.html", "r") as f:
                for line in f:
                    # Check for placeholders
                    if "{{CSS_PLACEHOLDER}}" in line:
                        await stream_file(writer, "webserver/style.css")
                    elif "{{TABLE_PLACEHOLDER}}" in line:
                        csv_data = csv_interface.get_content()
                        await stream_table(writer, csv_data)
                        # Free up CSV memory immediately
                        del csv_data
                        gc.collect() 
                    else:
                        # Send standard HTML line
                        await send_chunk(writer, line.encode('utf-8'))
        except OSError:
            await send_chunk(writer, b"<h1>Error: index.html not found</h1>")

    except Exception as e:
        print("Server Handler Error:", e)
    finally:
        # Ensure connection is closed properly
        try:
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

async def run_server(csv_interface):
    print("Starting Web Server on port 80...")
    
    # Wrapper to pass csv_interface to the handler
    async def serve_wrapper(reader, writer):
        await handle_client(reader, writer, csv_interface)

    # Start the server
    server = await asyncio.start_server(serve_wrapper, "0.0.0.0", 80)
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)