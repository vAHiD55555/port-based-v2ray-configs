import os
import datetime
from collections import defaultdict

# Simulated function to get configs — Replace this with your actual logic
def get_all_configs():
    # Example: Each config is (protocol, port, content)
    return [
        ("vless", 80, "vless://example1"),
        ("vless", 443, "vless://example2"),
        ("vmess", 80, "vmess://example3"),
        ("trojan", 443, "trojan://example4"),
    ]

# Create directories
os.makedirs("sub", exist_ok=True)
os.makedirs("detailed", exist_ok=True)

# Data structures
protocol_links = defaultdict(list)
port_links = defaultdict(list)
proto_port_links = defaultdict(lambda: defaultdict(list))

# Collect configs
for proto, port, content in get_all_configs():
    # Add to protocol group
    protocol_links[proto].append(content)
    # Add to port group
    port_links[port].append(content)
    # Add to protocol+port group
    proto_port_links[proto][port].append(content)

# Write protocol files in sub/
for proto, configs in protocol_links.items():
    with open(f"sub/{proto}.txt", "w") as f:
        f.write("\n".join(configs))

# Write port files in sub/
for port, configs in port_links.items():
    with open(f"sub/port_{port}.txt", "w") as f:
        f.write("\n".join(configs))

# Write detailed files
for proto, ports in proto_port_links.items():
    proto_dir = f"detailed/{proto}"
    os.makedirs(proto_dir, exist_ok=True)
    for port, configs in ports.items():
        with open(f"{proto_dir}/{port}.txt", "w") as f:
            f.write("\n".join(configs))

# Build README dynamic content
def build_table_by_protocol():
    table = "| Protocol | Count | Link |\n|----------|-------|------|\n"
    for proto, configs in sorted(protocol_links.items()):
        table += f"| {proto.upper()} | {len(configs)} | [📎 Link](sub/{proto}.txt) |\n"
    return table

def build_table_by_port():
    table = "| Port | Count | Link |\n|------|-------|------|\n"
    for port, configs in sorted(port_links.items()):
        table += f"| {port} | {len(configs)} | [📎 Link](sub/port_{port}.txt) |\n"
    return table

def build_detailed_table():
    table = "| Protocol | Port | Count | Link |\n|----------|------|-------|------|\n"
    for proto, ports in sorted(proto_port_links.items()):
        for port, configs in sorted(ports.items()):
            table += f"| {proto.upper()} | {port} | {len(configs)} | [📎 Link](detailed/{proto}/{port}.txt) |\n"
    return table

# Read current README
readme_path = "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    readme_content = f.read()

# Generate new dynamic section
new_section = f"""<!-- START -->
_Last update: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC_

## 1️⃣ Table by Protocols
{build_table_by_protocol()}

## 2️⃣ Table by Ports
{build_table_by_port()}

## 3️⃣ Detailed Table (Protocol + Port)
{build_detailed_table()}
<!-- END -->"""

# Replace old section
import re
if "<!-- START -->" in readme_content and "<!-- END -->" in readme_content:
    readme_content = re.sub(r"<!-- START -->.*<!-- END -->", new_section, readme_content, flags=re.S)
else:
    readme_content += "\n\n" + new_section

# Write updated README
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme_content)

print("README updated successfully!")
