#!/usr/bin/env python3
# categorize_all_protocols.py
# Safe updater: writes files into sub/ and detailed/, updates README between markers.
# No external formatting library required.

import os
import re
import requests
import base64
import json
from urllib.parse import urlparse
from collections import defaultdict
from datetime import datetime, timezone

# ---------------- Config ----------------
SOURCES = {
    "barry-far": "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "kobabi": "https://raw.githubusercontent.com/liketolivefree/kobabi/main/sub.txt",
    "mahdibland": "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "Epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "Rayan-Config": "https://raw.githubusercontent.com/Rayan-Config/C-Sub/refs/heads/main/configs/proxy.txt",
}

# GitHub repository details for raw links
GITHUB_USER = "hamedcode"
GITHUB_REPO = "port-based-v2ray-configs"
GITHUB_BRANCH = "main"
RAW_URL_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"

COMMON_PORTS = [80, 443, 2053, 2083, 2087, 2096, 8443]
README_PATH = "README.md"
SUB_DIR = "sub"
DETAILED_DIR = "detailed"
PREFERRED = ["VLESS", "VMESS", "TROJAN", "SS", "OTHER"]

MARKERS = {
    "stats": ("<!-- START-STATS -->", "<!-- END-STATS -->"),
    "links": ("<!-- START-LINKS -->", "<!-- END-LINKS -->"),
    "sources": ("<!-- START-SOURCES -->", "<!-- END-SOURCES -->"),
}

# ---------------- Helpers ----------------
def safe_filename(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(s))

def parse_configs(text):
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(("vmess://", "vless://", "trojan://", "ss://")):
            out.append(line)
    return out

def extract_info(cfg):
    proto, port = None, None
    try:
        if cfg.startswith("vmess://"):
            proto = "VMESS"
            b64 = cfg[8:]
            dec = base64.b64decode(b64 + "=" * (-len(b64) % 4)).decode("utf-8", errors="ignore")
            data = json.loads(dec)
            port = str(data.get("port") or data.get("Port") or "")
        else:
            parsed = urlparse(cfg)
            scheme = (parsed.scheme or "").lower()
            if scheme in ["vless", "trojan", "ss"]:
                proto = scheme.upper()
            if parsed.port:
                port = str(parsed.port)
            elif "@" in parsed.netloc:
                host_part = parsed.netloc.rsplit("@", 1)[-1]
                if ":" in host_part:
                    p = host_part.rsplit(":", 1)[-1]
                    if p.isdigit():
                        port = p
    except Exception:
        return None, None
    return proto, port if port else None

def md_table_from_rows(header_cells, rows):
    header = "| " + " | ".join(header_cells) + " |"
    sep = "|" + "|".join(["---"] * len(header_cells)) + "|"
    body = "\n".join("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return f"{header}\n{sep}\n{body}"

# ---------------- Main Logic ----------------
print("Fetching sources...")
all_items = []
source_counts = defaultdict(int)
for name, url in SOURCES.items():
    try:
        r = requests.get(url, timeout=25)
        r.raise_for_status()
        cfgs = parse_configs(r.text)
        for c in cfgs:
            all_items.append((c.strip(), name))
        source_counts[name] = len(cfgs)
        print(f"  Fetched {len(cfgs)} from {name}")
    except requests.RequestException as e:
        print(f"  Error fetching {name}: {e}")

total_fetched = len(all_items)
print(f"Total fetched: {total_fetched}")

print("Deduplicating and categorizing...")
seen = set()
protocol_links = defaultdict(list)
port_links = defaultdict(list)
proto_port_links = defaultdict(lambda: defaultdict(list))

for cfg, src in all_items:
    if cfg in seen:
        continue
    seen.add(cfg)
    proto, port = extract_info(cfg)
    key_proto = proto or "OTHER"
    key_port = port or "unknown"
    
    protocol_links[key_proto].append(cfg)
    port_links[key_port].append(cfg)
    proto_port_links[key_proto][key_port].append(cfg)

unique_count = len(seen)
print(f"Unique configs: {unique_count}, duplicates removed: {total_fetched - unique_count}")

print("Writing subscription files...")
os.makedirs(SUB_DIR, exist_ok=True)
os.makedirs(DETAILED_DIR, exist_ok=True)

for group, links in protocol_links.items():
    with open(os.path.join(SUB_DIR, f"{safe_filename(group.lower())}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(links))

for group, links in port_links.items():
    with open(os.path.join(SUB_DIR, f"port_{safe_filename(group)}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(links))

for proto, ports in proto_port_links.items():
    dirpath = os.path.join(DETAILED_DIR, safe_filename(proto.lower()))
    os.makedirs(dirpath, exist_ok=True)
    for port, links in ports.items():
        with open(os.path.join(dirpath, f"{safe_filename(port)}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(links))

print("Generating README content...")
# --- Stats Block ---
protocols_all = sorted(protocol_links.keys(), key=lambda p: (PREFERRED.index(p) if p in PREFERRED else len(PREFERRED), p))
header_cells = ["Protocol"] + [str(p) for p in COMMON_PORTS] + ["Total"]
rows = []
for proto in protocols_all:
    row = [proto] + [len(proto_port_links.get(proto, {}).get(str(p), [])) for p in COMMON_PORTS]
    row.append(len(protocol_links.get(proto, [])))
    rows.append(row)
stats_table_md = md_table_from_rows(header_cells, rows)

# --- Links Block ---
port_rows = [[p, len(port_links.get(str(p), [])), f"[Sub Link]({RAW_URL_BASE}/{SUB_DIR}/port_{p}.txt)"] for p in COMMON_PORTS]
port_table_md = md_table_from_rows(["Port", "Count", "Subscription Link"], port_rows)

proto_rows = [[p, len(protocol_links.get(p, [])), f"[Sub Link]({RAW_URL_BASE}/{SUB_DIR}/{safe_filename(p.lower())}.txt)"] for p in protocols_all]
proto_table_md = md_table_from_rows(["Protocol", "Count", "Subscription Link"], proto_rows)

pp_md_lines = []
for proto in protocols_all:
    entries = []
    for p in COMMON_PORTS:
        count = len(proto_port_links.get(proto, {}).get(str(p), []))
        if count > 0:
            relative_path = f"{DETAILED_DIR}/{safe_filename(proto.lower())}/{safe_filename(str(p))}.txt"
            raw_url = f"{RAW_URL_BASE}/{relative_path}"
            entries.append((proto, str(p), count, raw_url))
    
    if not entries:
        continue

    for i in range(0, len(entries), 2):
        left = entries[i]
        right = entries[i+1] if i+1 < len(entries) else None
        
        left_md = f"| {left[0]} | {left[1]} | {left[2]} | [Sub Link]({left[3]})"
        if right:
            right_md = f"| {right[0]} | {right[1]} | {right[2]} | [Sub Link]({right[3]}) |"
            pp_md_lines.append(f"{left_md} {right_md}")
        else:
            pp_md_lines.append(f"{left_md} | | | | |")

pp_header = "| Protocol | Port | Count | Link | Protocol | Port | Count | Link |"
pp_sep = "|:---|:---|:---|:---|:---|:---|:---|:---|"
pp_table_md = f"{pp_header}\n{pp_sep}\n" + "\n".join(pp_md_lines) if pp_md_lines else "_No specific protocol-port combinations found for common ports._"

# --- Sources Block (Side-by-side HTML) ---
sources_rows = sorted(source_counts.items())
summary_rows = [
    ["Total Fetched", total_fetched],
    ["Unique Configs", unique_count],
    ["Duplicates Removed", total_fetched - unique_count],
]
sources_table_md = md_table_from_rows(["Source", "Fetched Lines"], sources_rows)
summary_table_md = md_table_from_rows(["Metric", "Value"], summary_rows)

# Create HTML structure for side-by-side tables
side_by_side_html = f"""
<table width="100%">
  <tr>
    <td width="50%" valign="top">
      <h4>Sources</h4>
      {sources_table_md}
    </td>
    <td width="50%" valign="top">
      <h4>Summary</h4>
      {summary_table_md}
    </td>
  </tr>
</table>
"""

# --- Compose Blocks ---
now_ts = datetime.utcnow().replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
stats_block = f"{MARKERS['stats'][0]}\n_Last update: {now_ts}_\n\n{stats_table_md}\n{MARKERS['stats'][1]}"
links_block = f"{MARKERS['links'][0]}\n### By Port\n{port_table_md}\n\n### By Protocol\n{proto_table_md}\n\n### By Protocol & Port (Common Ports)\n{pp_table_md}\n{MARKERS['links'][1]}"
sources_block = f"{MARKERS['sources'][0]}\n{side_by_side_html}\n{MARKERS['sources'][1]}"

print("Updating README.md...")
try:
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme_text = f.read()

    readme_text = re.sub(f"{re.escape(MARKERS['stats'][0])}.*?{re.escape(MARKERS['stats'][1])}", stats_block, readme_text, flags=re.S)
    readme_text = re.sub(f"{re.escape(MARKERS['links'][0])}.*?{re.escape(MARKERS['links'][1])}", links_block, readme_text, flags=re.S)
    readme_text = re.sub(f"{re.escape(MARKERS['sources'][0])}.*?{re.escape(MARKERS['sources'][1])}", sources_block, readme_text, flags=re.S)
    
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme_text)
    
    print("README updated successfully.")

except FileNotFoundError:
    print(f"ERROR: {README_PATH} not found. Please create it using the provided template.")
except Exception as e:
    print(f"An error occurred while updating README: {e}")

