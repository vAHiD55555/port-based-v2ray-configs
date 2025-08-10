import requests
import base64
import json
import os
import re
import socket
import time
import concurrent.futures
from collections import defaultdict
from urllib.parse import urlparse, unquote
from datetime import datetime, timezone, timedelta

# === Sources ===
SOURCES = {
    "barry-far": "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "kobabi": "https://raw.githubusercontent.com/liketolivefree/kobabi/main/sub.txt",
    "mahdibland": "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "Epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "Rayan-Config": "https://raw.githubusercontent.com/Rayan-Config/C-Sub/refs/heads/main/configs/proxy.txt",
}

# === Repo links for credits ===
SOURCE_REPOS = {
    "barry-far": "https://github.com/barry-far/V2ray-Config",
    "kobabi": "https://github.com/liketolivefree/kobabi",
    "mahdibland": "https://github.com/mahdibland/V2RayAggregator",
    "Epodonios": "https://github.com/Epodonios/v2ray-configs",
    "Rayan-Config": "https://github.com/Rayan-Config/C-Sub",
}

# === Known ports ===
FAMOUS_PORTS = {
    '80', '443', '8080', '8088', '2052', '2053', '2082', '2083', '2086', '2087',
    '2095', '2096', '8443'
}

# === Helpers ===
def parse_configs(data):
    configs = []
    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(("vmess://", "vless://", "trojan://", "ss://")):
            configs.append(line)
    return configs

def extract_info(config):
    protocol = None
    port = None
    try:
        if config.startswith("vmess://"):
            protocol = "VMESS"
            decoded = json.loads(base64.b64decode(config[8:] + '==').decode('utf-8', errors='ignore'))
            port = str(decoded.get('port'))
        elif config.startswith("vless://"):
            protocol = "VLESS"
            parsed = urlparse(config)
            port = str(parsed.port) if parsed.port else None
        elif config.startswith("trojan://"):
            protocol = "TROJAN"
            parsed = urlparse(config)
            port = str(parsed.port) if parsed.port else None
        elif config.startswith("ss://"):
            protocol = "SS"
            parsed = urlparse(config)
            port = str(parsed.port) if parsed.port else None
    except Exception:
        pass
    return protocol, port

# === Main process ===
all_configs = []
protocol_count = defaultdict(int)
port_count = defaultdict(int)
proto_port_count = defaultdict(int)
proto_links = defaultdict(list)
port_links = defaultdict(list)
proto_port_links = defaultdict(list)

for name, url in SOURCES.items():
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            configs = parse_configs(r.text)
            for cfg in configs:
                protocol, port = extract_info(cfg)
                if protocol and port:
                    all_configs.append(cfg)
                    protocol_count[protocol] += 1
                    port_count[port] += 1
                    proto_port_count[(protocol, port)] += 1
                    proto_links[protocol].append(cfg)
                    port_links[port].append(cfg)
                    proto_port_links[(protocol, port)].append(cfg)
    except Exception:
        continue

# === Table generators ===
def make_table_by_protocol():
    rows = ["| Protocol | Config Count | Subscription Link |", "|----------|--------------|-------------------|"]
    for proto in sorted(protocol_count.keys()):
        link = f"[📎 Link](data:text/plain;base64,{base64.b64encode('\n'.join(proto_links[proto]).encode()).decode()})"
        rows.append(f"| {proto} | {protocol_count[proto]} | {link} |")
    return "\n".join(rows)

def make_table_by_port():
    rows = ["| Port | Config Count | Subscription Link |", "|------|--------------|-------------------|"]
    for port in sorted(port_count.keys(), key=lambda x: int(x) if x.isdigit() else 99999):
        link = f"[📎 Link](data:text/plain;base64,{base64.b64encode('\n'.join(port_links[port]).encode()).decode()})"
        rows.append(f"| {port} | {port_count[port]} | {link} |")
    return "\n".join(rows)

def make_table_detailed():
    rows = ["| Protocol | Port | Config Count | Subscription Link |", "|----------|------|--------------|-------------------|"]
    for (proto, port) in sorted(proto_port_count.keys(), key=lambda x: (x[0], int(x[1]) if x[1].isdigit() else 99999)):
        link = f"[📎 Link](data:text/plain;base64,{base64.b64encode('\n'.join(proto_port_links[(proto, port)]).encode()).decode()})"
        rows.append(f"| {proto} | {port} | {proto_port_count[(proto, port)]} | {link} |")
    return "\n".join(rows)

# === Write to README.md ===
readme_content = f"""
# Subscription Links Overview

_Last update: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}_

## 1️⃣ Table by Protocols
{make_table_by_protocol()}

## 2️⃣ Table by Ports
{make_table_by_port()}

## 3️⃣ Detailed Table (Protocol + Port)
{make_table_detailed()}
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

print("README.md updated successfully!")
