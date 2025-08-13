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

# --- Sources Block ---
sources_rows = sorted(source_counts.items())
summary_rows = [
    ["Total Fetched", total_fetched],
    ["Unique Configs", unique_count],
    ["Duplicates Removed", total_fetched - unique_count],
]
sources_table_md = md_table_from_rows(["Source", "Fetched Lines"], sources_rows)
summary_table_md = md_table_from_rows(["Metric", "Value"], summary_rows)

# --- Compose Blocks ---
now_ts = datetime.utcnow().replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
stats_block = f"{MARKERS['stats'][0]}\n_Last update: {now_ts}_\n\n{stats_table_md}\n{MARKERS['stats'][1]}"
links_block = f"{MARKERS['links'][0]}\n### By Port\n{port_table_md}\n\n### By Protocol\n{proto_table_md}\n{MARKERS['links'][1]}"
sources_block = f"{MARKERS['sources'][0]}\n{sources_table_md}\n\n{summary_table_md}\n{MARKERS['sources'][1]}"

print("Updating README.md...")
try:
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme_text = f.read()

    # --- Replace in correct order ---
    # The order of these replacements matters if markers are nested, but for safety we do it sequentially.
    # The final order in the file depends on the order of markers in the template.
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

