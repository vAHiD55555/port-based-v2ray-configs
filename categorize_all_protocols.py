import os
import re
from collections import defaultdict
from datetime import datetime
from tabulate import tabulate

# Paths
SUB_DIR = "sub"
README_FILE = "README.md"

# GitHub repo info (for raw links)
GITHUB_USER = "hamedcode"
GITHUB_REPO = "port-based-v2ray-configs"
RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{SUB_DIR}"

# Ports to display in the "popular ports" section
POPULAR_PORTS = [80, 443, 2083, 2087, 2096, 8443]

# Gather stats
protocol_port_counts = defaultdict(lambda: defaultdict(int))
protocol_totals = defaultdict(int)
port_totals = defaultdict(int)

# Gather subscription links data
ports_data = defaultdict(int)
protocols_data = defaultdict(int)
protocol_port_data = defaultdict(lambda: defaultdict(int))

for filename in os.listdir(SUB_DIR):
    if not filename.endswith(".txt"):
        continue
    path = os.path.join(SUB_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        continue

    # Extract protocol and port from filename
    match = re.match(r"([a-zA-Z0-9]+)_(\d+)\.txt", filename)
    if match:
        proto, port = match.group(1).upper(), int(match.group(2))
        count = len(lines)
        protocol_port_counts[proto][port] = count
        protocol_totals[proto] += count
        port_totals[port] += count
        ports_data[port] += count
        protocols_data[proto] += count
        protocol_port_data[proto][port] += count

# Table: Statistics (Protocol × Common Ports)
all_ports_sorted = sorted({p for counts in protocol_port_counts.values() for p in counts})
stats_table = []
for proto in sorted(protocol_port_counts.keys()):
    row = [proto] + [protocol_port_counts[proto].get(p, 0) for p in all_ports_sorted] + [protocol_totals[proto]]
    stats_table.append(row)
total_row = ["Total"] + [port_totals.get(p, 0) for p in all_ports_sorted] + [sum(port_totals.values())]
stats_table.append(total_row)
stats_md = tabulate(stats_table, headers=["Protocol"] + [str(p) for p in all_ports_sorted] + ["Total"], tablefmt="github")

# Subscription Links: By Port
by_port_md = []
for port in POPULAR_PORTS:
    link = f"{RAW_BASE}/port_{port}.txt"
    by_port_md.append([port, ports_data.get(port, 0), f"[Link]({link})"])
by_port_md = tabulate(by_port_md, headers=["Port", "Config Count", "Subscription Link"], tablefmt="github")

# Subscription Links: By Protocol
by_protocol_md = []
for proto in sorted(protocols_data.keys()):
    link = f"{RAW_BASE}/{proto.lower()}.txt"
    by_protocol_md.append([proto, protocols_data[proto], f"[Link]({link})"])
by_protocol_md = tabulate(by_protocol_md, headers=["Protocol", "Config Count", "Subscription Link"], tablefmt="github")

# Subscription Links: By Protocol & Port
by_protocol_port_md = []
proto_list = sorted(protocol_port_data.keys())
max_rows = max(len(protocol_port_data[proto]) for proto in proto_list)
ports_sorted_per_proto = {proto: sorted(protocol_port_data[proto].keys()) for proto in proto_list}

for i in range(max_rows):
    row = []
    for proto in proto_list:
        if i < len(ports_sorted_per_proto[proto]):
            port = ports_sorted_per_proto[proto][i]
            link = f"{RAW_BASE}/{proto.lower()}_{port}.txt"
            row += [proto, port, f"[Link]({link})"]
        else:
            row += ["---", "---", "---"]
    by_protocol_port_md.append(row)

headers = []
for proto in proto_list:
    headers += [proto, "Port", "Link"]
by_protocol_port_md = tabulate(by_protocol_port_md, headers=headers, tablefmt="github")

# Sources & Summary
sources_list = [
    ("barry-far", "https://github.com/barry-far", 15942),
    ("kobabi", "https://github.com/kobabi", 313),
    ("mahdibland", "https://github.com/mahdibland", 4906),
    ("Epodonios", "https://github.com/Epodonios", 15947),
    ("Rayan Config", "https://github.com/Rayan-Config", 77),
]
sources_md = tabulate([[f"[{name}]({url})", count] for name, url, count in sources_list],
                      headers=["Source", "Fetched Lines"], tablefmt="github")

summary_md = tabulate([
    ["Total fetched", 37185],
    ["Duplicates removed", 16173],
    ["Unique configs", 21012]
], headers=["Metric", "Value"], tablefmt="github")

# Update README.md
with open(README_FILE, "r", encoding="utf-8") as f:
    readme_content = f.read()

def replace_between_tags(content, tag, new_text):
    return re.sub(
        fr"(<!-- START-{tag.upper()} -->)(.*?)(<!-- END-{tag.upper()} -->)",
        fr"\1\n\n{new_text}\n\n\3",
        content,
        flags=re.S
    )

readme_content = replace_between_tags(readme_content, "stats", stats_md)
readme_content = replace_between_tags(readme_content, "links",
    f"### Subscription Links (popular ports only)\n\n"
    f"**By Port**\n\n{by_port_md}\n\n"
    f"**By Protocol**\n\n{by_protocol_md}\n\n"
    f"**By Protocol & Port**\n\n{by_protocol_port_md}"
)
readme_content = replace_between_tags(readme_content, "sources",
    f"### Sources & Summary\n\n{sources_md}\n\n{summary_md}"
)

with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(readme_content)

print("README.md updated successfully.")
