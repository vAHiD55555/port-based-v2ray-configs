import os
import base64
from collections import defaultdict

README_FILE = "README.md"
SUB_DIR = "sub"
DETAILED_DIR = "detailed"

# Create folders if not exist
os.makedirs(SUB_DIR, exist_ok=True)
os.makedirs(DETAILED_DIR, exist_ok=True)

# Example data loading (Replace with your real config parsing)
configs = [
    ("vless", "80", "vless://example1"),
    ("vless", "443", "vless://example2"),
    ("vless", "8080", "vless://example3"),
    ("vmess", "80", "vmess://example4"),
    ("vmess", "443", "vmess://example5"),
    ("trojan", "443", "trojan://example6"),
]

# Save subscription files
proto_port_links = defaultdict(lambda: defaultdict(list))
for proto, port, link in configs:
    proto_port_links[proto][port].append(link)

    # Save in sub/ folder
    sub_file_path = os.path.join(SUB_DIR, f"{proto}_{port}.txt")
    with open(sub_file_path, "w") as f:
        f.write("\n".join(proto_port_links[proto][port]))

    # Save in detailed/ folder
    proto_dir = os.path.join(DETAILED_DIR, proto)
    os.makedirs(proto_dir, exist_ok=True)
    detailed_file_path = os.path.join(proto_dir, f"{port}.txt")
    with open(detailed_file_path, "w") as f:
        f.write("\n".join(proto_port_links[proto][port]))

# Build Subscription Links table
sub_table = "| Protocol | Port | Link |\n|----------|------|------|\n"
for idx, proto in enumerate(sorted(proto_port_links.keys())):
    for port in sorted(proto_port_links[proto].keys(), key=int):
        sub_table += f"| **{proto}** | {port} | [📎 Link](./{SUB_DIR}/{proto}_{port}.txt) |\n"
    if idx < len(proto_port_links) - 1:
        sub_table += "| **---** | **---** | **---** |\n"

sub_table += "\n> ℹ️ More ports and protocols are available in the `sub/` and `detailed/` folders.\n"

# Dummy sources data (replace with your real stats)
sources_data = [
    ("https://example1.com", 120, 20),
    ("https://example2.com", 90, 5),
]

sources_table = "| Source URL | Collected | Removed Duplicates |\n|------------|-----------|--------------------|\n"
for url, collected, removed in sources_data:
    sources_table += f"| `{url}` | {collected} | {removed} |\n"

sources_table += "| --- | --- | --- |\n"
sources_table += f"| **Total** | **{sum(s[1] for s in sources_data)}** | **{sum(s[2] for s in sources_data)}** |\n"

# Update README.md while keeping previous content
with open(README_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Replace between markers or append if not found
if "<!-- SUB_LINKS_START -->" in content and "<!-- SUB_LINKS_END -->" in content:
    content = content.split("<!-- SUB_LINKS_START -->")[0] + \
              "<!-- SUB_LINKS_START -->\n" + sub_table + "\n<!-- SUB_LINKS_END -->" + \
              content.split("<!-- SUB_LINKS_END -->")[1]
else:
    content += "\n## Subscription Links\n<!-- SUB_LINKS_START -->\n" + sub_table + "\n<!-- SUB_LINKS_END -->\n"

if "<!-- SOURCES_START -->" in content and "<!-- SOURCES_END -->" in content:
    content = content.split("<!-- SOURCES_START -->")[0] + \
              "<!-- SOURCES_START -->\n" + sources_table + "\n<!-- SOURCES_END -->" + \
              content.split("<!-- SOURCES_END -->")[1]
else:
    content += "\n## Sources\n<!-- SOURCES_START -->\n" + sources_table + "\n<!-- SOURCES_END -->\n"

with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("README.md updated successfully.")
