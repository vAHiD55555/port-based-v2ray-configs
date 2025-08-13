import os
import re
from collections import defaultdict
from tabulate import tabulate

# Paths
SUB_DIR = "sub"
README_FILE = "README.md"

# GitHub repo info (for raw links)
GITHUB_USER = "hamedcode"
GITHUB_REPO = "port-based-v2ray-configs"
RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/refs/heads/main/{SUB_DIR}"

# Popular ports
POPULAR_PORTS = [80, 443, 2083, 2087, 2096, 8443]

# Gather stats
protocol_port_counts = defaultdict(lambda: defaultdict(int))
protocol_totals = defaultdict(int)
port_totals = defaultdict(int)

for filename in os.listdir(SUB_DIR):
    if not filename.endswith(".txt"):
        continue
    match = re.match(r"([a-zA-Z0-9]+)_(\d+)\.txt", filename)
    if not match:
        continue
    proto, port = match.group(1).upper(), int(match.group(2))
    with open(os.path.join(SUB_DIR, filename), "r", encoding="utf-8") as f:
        count = sum(1 for line in f if line.strip())
    protocol_port_counts[proto][port] = count
    protocol_totals[proto] += count
    port_totals[port] += count

# Table: stats
all_ports_sorted = sorted({p for counts in protocol_port_counts.values() for p in counts})
stats_table = []
for proto in sorted(protocol_port_counts.keys()):
    row = [proto] + [protocol_port_counts[proto].get(p, 0) for p in all_ports_sorted] + [protocol_totals[proto]]
    stats_table.append(row)
total_row = ["Total"] + [port_totals.get(p, 0) for p in all_ports_sorted] + [sum(port_totals.values())]
stats_table.append(total_row)
stats_md = tabulate(stats_table, headers=["Protocol"] + [str(p) for p in all_ports_sorted] + ["Total"], tablefmt="github")

# Subscription Links: only popular ports
by_port_md = []
for port in POPULAR_PORTS:
    filename = f"port_{port}.txt"
    link = f"{RAW_BASE}/{filename}"
    by_port_md.append([port, port_totals.get(port, 0), f"[Link]({link})"])
by_port_md = tabulate(by_port_md, headers=["Port", "Count", "Subscription Link"], tablefmt="github")

# Update README.md between markers
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
readme_content = replace_between_tags(readme_content, "links", f"### Subscription Links (popular ports only)\n\n{by_port_md}")

with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(readme_content)

print("README.md updated successfully.")
