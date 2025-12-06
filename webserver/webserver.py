import uasyncio as asyncio

def csv_to_html_table(csv_data):
    rows = [line.strip().split(",") for line in csv_data.split("\n") if line.strip()]
    # Build HTML table
    html = "<table border='1' cellpadding='6'><thead><tr>"
    html += "".join(f"<th>{h}</th>" for h in rows[0])
    html += "</tr></thead><tbody>"
    for row in rows[1:]:
        html += "<tr>" + "".join(f"<td>{col}</td>" for col in row) + "</tr>"
    html += "</tbody></table>"
    return html

def build_page(csv_interface):
    csv_data = csv_interface.get_content()
    table = csv_to_html_table(csv_data)
    
    with open("webserver/index.html", "r") as f:
        html_template = f.read()
    with open("webserver/style.css", "r") as f:
        css_content = f.read()
    html_page = html_template.replace("{{TABLE_PLACEHOLDER}}", table)
    html_page = html_page.replace("{{CSS_PLACEHOLDER}}", css_content)
    
    return f"""HTTP/1.1 200 OK
Content-Type: text/html

{html_page}"""



async def run_server(csv_interface):
    print("Starting Web Server...")
    
    async def serve(reader, writer):
        try:
            request = await reader.readline()
            if not request:
                await writer.aclose()
                return
            response = build_page(csv_interface)
            await writer.awrite(response)
            await writer.aclose()
        except Exception as e:
            print("Error:", e)

    server = await asyncio.start_server(serve, "0.0.0.0", 80)
    await server.wait_closed()
