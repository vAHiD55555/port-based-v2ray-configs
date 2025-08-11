#!/usr/bin/env python3
# categorize_all_protocols.py
# Safe updater: writes sub/ and detailed/ files, updates only subscription section in README (with backup).

import os
import re
import requests
import base64
import json
from urllib.parse import urlparse, unquote
from collections import defaultdict
from datetime import datetime, timezone

# === Sources (edit or extend if needed) ===
SOURCES = {
    "barry-far": "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "kobabi": "https://raw.githubusercontent.com/liketolivefree/kobabi/main/sub.txt",
    "mahdibland": "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "Epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "Rayan-Config": "https://raw.githubusercontent.com/Rayan-Config/C-Sub/refs/heads/main/configs/proxy.txt",
}

# === Helpers ===
def parse_configs(text):
    """Return list of raw config lines (vmess://, vless://, trojan://, ss://) from a text blob."""
    configs = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(("vmess://", "vless://", "trojan://", "ss://")):
            configs.append(line)
    return configs

def extract_info(config):
    """
    Best-effort: return (PROTOCOL, PORT) for a single config line.
    PROTOCOL is normalized uppercase string ("VMESS","VLESS","TROJAN","SS") or None.
    PORT is string or None.
    """
    protocol = None
    port = None
    try:
        if config.startswith("vmess://"):
            protocol = "VMESS"
            # vmess payload after scheme is base64 (sometimes missing padding)
            b64 = config[8:]
            # Add padding if necessary
            padding = len(b64) % 4
            if padding:
                b64 += "=" * (4 - padding)
            decoded = base64.b64decode(b64).decode("utf-8", errors="ignore")
            data = json.loads(decoded)
            port = str(data.get("port") or data.get("Port") or "")
            if port == "": port = None
        elif config.startswith("vless://") or config.startswith("trojan://") or config.startswith("ss://"):
            # Use urlparse for these; ss sometimes has special forms but urlparse handles many.
            parsed = urlparse(config)
            scheme = parsed.scheme.lower()
            if scheme == "vless":
                protocol = "VLESS"
            elif scheme == "trojan":
                protocol = "TROJAN"
            elif scheme == "ss":
                protocol = "SS"
            # parsed.port may be None if url form is non-standard; try to extract from netloc
            if parsed.port:
                port = str(parsed.port)
            else:
                # try to parse netloc like user:pass@host:port
                netloc = parsed.netloc
                if ":" in netloc.rsplit("@", 1)[-1]:
                    # split host:port
                    p = netloc.rsplit(":", 1)[-1]
                    if p.isdigit():
                        port = p
                else:
                    # For ss://<base64> form, try decode to find port (best-effort)
                    if scheme == "ss":
                        # ss://<base64> or ss://method:pass@host:port
                        m = re.match(r"^ss://(.+)$", config)
                        if m:
                            rest = m.group(1)
                            # strip possible fragment/comment
                            rest = rest.split("#",1)[0]
                            # if rest contains "@", it's method:pass@host:port -> try urlparse again
                            if "@" in rest:
                                try:
                                    fake = "ss://" + rest
                                    p2 = urlparse(fake)
                                    if p2.port:
                                        port = str(p2.port)
                                except Exception:
                                    pass
                            else:
                                # try base64 decode
                                try:
                                    b = rest
                                    padding = len(b) % 4
                                    if padding:
                                        b += "=" * (4 - padding)
                                    dec = base64.b64decode(b).decode("utf-8", errors="ignore")
                                    # dec often like "method:password@host:port"
                                    if "@" in dec and ":" in dec.rsplit(":",1)[-1]:
                                        p = dec.rsplit(":",1)[-1]
                                        if p.isdigit():
                                            port = p
                                except Exception:
                                    pass
        # normalize protocol string
        if protocol:
            protocol = protocol.upper()
    except Exception:
        # fail silently, return (None, None)
        return None, None
    return protocol, port

def safe_filename(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(s))

# === Fetch & parse ===
print("Fetching sources...")
all_raw = []  # list of tuples (config_line, source_name)
for name, url in SOURCES.items():
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200 and r.text:
            cfgs = parse_configs(r.text)
            for c in cfgs:
                all_raw.append((c.strip(), name))
            print(f"  fetched {len(cfgs)} configs from {name}")
        else:
            print(f"  warning: {name} returned status {r.status_code}")
    except Exception as e:
        print(f"  error fetching {name}: {e}")

total_fetched = len(all_raw)
print(f"Total fetched lines: {total_fetched}")

# === Deduplicate, extract info and categorize ===
seen = set()
duplicates = 0
protocol_links = defaultdict(list)      # proto -> list of configs
port_links = defaultdict(list)          # port -> list of configs
proto_port_links = defaultdict(lambda: defaultdict(list))  # proto -> port -> list
source_counts = defaultdict(int)        # source -> count collected
for cfg, src in all_raw:
    source_counts[src] += 1
    key = cfg.strip()
    if key in seen:
        duplicates += 1
        continue
    seen.add(key)
    proto, port = extract_info(cfg)
    if proto and port:
        protocol_links[proto].append(cfg)
        port_links[port].append(cfg)
        proto_port_links[proto][port].append(cfg)
    else:
        # Place uncategorized under OTHER
        protocol_links["OTHER"].append(cfg)
        port_links["unknown"].append(cfg)
        proto_port_links["OTHER"]["unknown"].append(cfg)

unique_count = len(seen)
print(f"Unique configs: {unique_count}, duplicates removed: {duplicates}")

# === Prepare directories and write files ===
os.makedirs("sub", exist_ok=True)
os.makedirs("detailed", exist_ok=True)

# write protocol files under sub/
for proto, configs in protocol_links.items():
    fname = os.path.join("sub", f"{safe_filename(proto.lower())}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(configs))
    # small log:
    print(f"Wrote {len(configs)} to {fname}")

# write port files under sub/
for port, configs in port_links.items():
    fname = os.path.join("sub", f"port_{safe_filename(port)}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(configs))
    print(f"Wrote {len(configs)} to {fname}")

# write detailed files: detailed/{protocol}/{port}.txt
for proto, ports in proto_port_links.items():
    dirpath = os.path.join("detailed", safe_filename(proto.lower()))
    os.makedirs(dirpath, exist_ok=True)
    for port, configs in ports.items():
        fname = os.path.join(dirpath, f"{safe_filename(port)}.txt")
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(configs))
        print(f"Wrote {len(configs)} to {fname}")

# === Build the dynamic subscription tables (links point to files we just wrote) ===
def build_table_by_protocol():
    lines = ["| Protocol | Config Count | Subscription Link |", "|----------|--------------|-------------------|"]
    for proto in sorted(protocol_links.keys()):
        path = f"sub/{safe_filename(proto.lower())}.txt"
        lines.append(f"| {proto} | {len(protocol_links[proto])} | [📎 Link]({path}) |")
    return "\n".join(lines)

def build_table_by_port():
    # numeric sort if possible
    def keyfn(x):
        try:
            return int(x)
        except Exception:
            return 10**9
    lines = ["| Port | Config Count | Subscription Link |", "|------|--------------|-------------------|"]
    for port in sorted(port_links.keys(), key=keyfn):
        path = f"sub/port_{safe_filename(port)}.txt"
        lines.append(f"| {port} | {len(port_links[port])} | [📎 Link]({path}) |")
    return "\n".join(lines)

def build_detailed_table():
    lines = ["| Protocol | Port | Config Count | Subscription Link |", "|----------|------|--------------|-------------------|"]
    for proto in sorted(proto_port_links.keys()):
        for port in sorted(proto_port_links[proto].keys(), key=lambda x: int(x) if str(x).isdigit() else 10**9):
            ppath = f"detailed/{safe_filename(proto.lower())}/{safe_filename(port)}.txt"
            lines.append(f"| {proto} | {port} | {len(proto_port_links[proto][port])} | [📎 Link]({ppath}) |")
    return "\n".join(lines)

now_ts = datetime.utcnow().replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
dynamic_section = f"""<!-- SUBSCRIPTION TABLES START -->
_Last update: {now_ts}_

## 1️⃣ Table by Protocols
{build_table_by_protocol()}

## 2️⃣ Table by Ports
{build_table_by_port()}

## 3️⃣ Detailed Table (Protocol + Port)
{build_detailed_table()}
<!-- SUBSCRIPTION TABLES END -->"""

# === README update: safe replace with backups and multiple fallback strategies ===
README = "README.md"
if os.path.exists(README):
    with open(README, "r", encoding="utf-8") as f:
        readme_text = f.read()
else:
    readme_text = ""

# backup first
bak_name = f"README.md.bak.{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
with open(bak_name, "w", encoding="utf-8") as bf:
    bf.write(readme_text)
print(f"Backup of README written to {bak_name}")

def replace_between_markers(text, start_marker, end_marker, new_block):
    if start_marker in text and end_marker in text:
        before = text.split(start_marker)[0]
        after = text.split(end_marker, 1)[1]
        return before + new_block + after, True
    return text, False

# try a few possible marker pairs (old scripts might have used different markers)
marker_pairs = [
    ("<!-- SUBSCRIPTION TABLES START -->", "<!-- SUBSCRIPTION TABLES END -->"),
    ("<!-- START -->", "<!-- END -->"),
    ("<!-- DYNAMIC SUBS START -->", "<!-- DYNAMIC SUBS END -->"),
]

replaced = False
for sm, em in marker_pairs:
    readme_text, replaced = replace_between_markers(readme_text, sm, em, dynamic_section)
    if replaced:
        print(f"Replaced section between markers {sm} .. {em}")
        break

if not replaced:
    # try to find a sensible header to replace: e.g. "## 📌 Dynamic Subscription Tables" or "## Subscription Links"
    header_regex = re.compile(r"(?m)^(##\s*(?:📌\s*)?Dynamic Subscription Tables|##\s*Subscription Links|##\s*Subscription Links Overview|##\s*📌\s*Dynamic Subscription Tables)", re.IGNORECASE)
    m = header_regex.search(readme_text)
    if m:
        start_idx = m.start()
        # find next top-level section (## ) or horizontal rule '---' after this point
        next_section = re.search(r"(?m)^\s*(##\s+|---\s*$)", readme_text[m.end():])
        if next_section:
            end_idx = m.end() + next_section.start()
        else:
            end_idx = len(readme_text)
        new_text = readme_text[:start_idx] + dynamic_section + readme_text[end_idx:]
        readme_text = new_text
        replaced = True
        print("Replaced section found by header regex.")
    else:
        # fallback: append dynamic section at end
        readme_text = readme_text.rstrip() + "\n\n" + dynamic_section + "\n"
        replaced = True
        print("Markers/header not found — appended dynamic section at end of README.")

# write updated README
with open(README, "w", encoding="utf-8") as f:
    f.write(readme_text)
print("README updated (see backup if you need to restore).")

# === Optionally write a small sources summary file (not required) ===
summary = {
    "total_fetched": total_fetched,
    "unique": unique_count,
    "duplicates_removed": duplicates,
    "sources": dict(source_counts)
}
# Also print summary to console for logs
print("Summary:", summary)
