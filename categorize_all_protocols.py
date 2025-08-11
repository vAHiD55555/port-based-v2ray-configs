#!/usr/bin/env python3
# categorize_all_protocols.py
# Safe updater: writes files into sub/ and detailed/, updates only marked sections in README.
# IMPORTANT: This script does NOT embed config content into README (only links to files).

import os
import re
import requests
import json
import base64
from urllib.parse import urlparse
from collections import defaultdict
from datetime import datetime, timezone

# ------------- Configurable ----------------
SOURCES = {
    "barry-far": "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "kobabi": "https://raw.githubusercontent.com/liketolivefree/kobabi/main/sub.txt",
    "mahdibland": "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "Epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "Rayan-Config": "https://raw.githubusercontent.com/Rayan-Config/C-Sub/refs/heads/main/configs/proxy.txt",
}
# ports to show in README tables (popular/common)
COMMON_PORTS = [80, 443, 8080, 2053, 2083, 2087, 2096]  # customize if needed
README_PATH = "README.md"
# markers used in README
MARKERS = {
    "stats": ("<!-- START-STATS -->", "<!-- END-STATS -->"),
    "links": ("<!-- START-LINKS -->", "<!-- END-LINKS -->"),
    "sources": ("<!-- START-SOURCES -->", "<!-- END-SOURCES -->"),
}

# ------------- Helpers ----------------
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
    """Return (PROTO, PORT) or (None, None) on failure. PROTO normalized uppercase."""
    proto = None
    port = None
    try:
        if cfg.startswith("vmess://"):
            proto = "VMESS"
            b64 = cfg[8:]
            padding = len(b64) % 4
            if padding:
                b64 += "=" * (4 - padding)
            decoded = base64.b64decode(b64).decode("utf-8", errors="ignore")
            data = json.loads(decoded)
            port = str(data.get("port") or data.get("Port") or "")
            if port == "":
                port = None
        else:
            parsed = urlparse(cfg)
            scheme = (parsed.scheme or "").lower()
            if scheme == "vless":
                proto = "VLESS"
            elif scheme == "trojan":
                proto = "TROJAN"
            elif scheme == "ss":
                proto = "SS"
            # try parsed.port
            if parsed.port:
                port = str(parsed.port)
            else:
                # netloc fallback (host:port) after @ if present
                net = parsed.netloc
                if "@" in net:
                    after_at = net.rsplit("@", 1)[-1]
                else:
                    after_at = net
                if ":" in after_at:
                    p = after_at.rsplit(":", 1)[-1]
                    if p.isdigit():
                        port = p
                else:
                    # special attempt for ss://<base64> form
                    if scheme == "ss":
                        m = re.match(r"^ss://([^#]+)", cfg)
                        if m:
                            rest = m.group(1)
                            # if contains "@", let urlparse handle it
                            if "@" not in rest:
                                try:
                                    b = rest
                                    pad = len(b) % 4
                                    if pad:
                                        b += "=" * (4 - pad)
                                    dec = base64.b64decode(b).decode("utf-8", errors="ignore")
                                    if "@" in dec and ":" in dec.rsplit(":",1)[-1]:
                                        p = dec.rsplit(":",1)[-1]
                                        if p.isdigit():
                                            port = p
                                except Exception:
                                    pass
        if proto:
            proto = proto.upper()
    except Exception:
        return None, None
    return proto, port

# ------------- Fetch & parse -------------
print("Fetching sources...")
all_lines = []      # tuples of (line, source)
source_raw_counts = defaultdict(int)
for name, url in SOURCES.items():
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200 and r.text:
            cfgs = parse_configs(r.text)
            for c in cfgs:
                all_lines.append((c, name))
            source_raw_counts[name] = len(cfgs)
            print(f"  {name}: fetched {len(cfgs)} lines")
        else:
            print(f"  warning: {name} returned status {getattr(r, 'status_code', 'ERR')}")
    except Exception as e:
        print(f"  error fetching {name}: {e}")

total_fetched = len(all_lines)
print("Total fetched lines:", total_fetched)

# ------------- Deduplicate & categorize -------------
seen = set()
duplicates = 0
protocol_links = defaultdict(list)           # PROTO -> [configs...]
port_links = defaultdict(list)               # port -> [configs...]
proto_port_links = defaultdict(lambda: defaultdict(list))  # PROTO -> port -> [configs...]

for cfg, src in all_lines:
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
        # fallback bucket
        protocol_links["OTHER"].append(cfg)
        port_links["unknown"].append(cfg)
        proto_port_links["OTHER"]["unknown"].append(cfg)

unique_count = len(seen)
print("Unique configs:", unique_count, "duplicates removed:", duplicates)

# ------------- Write files (sub/ and detailed/) -------------
os.makedirs("sub", exist_ok=True)
os.makedirs("detailed", exist_ok=True)

# write per-protocol full lists
for proto, cfgs in protocol_links.items():
    fname = os.path.join("sub", f"{safe_filename(proto.lower())}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(cfgs))
    print("Wrote", len(cfgs), "to", fname)

# write per-port full lists
for port, cfgs in port_links.items():
    fname = os.path.join("sub", f"port_{safe_filename(port)}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(cfgs))
    print("Wrote", len(cfgs), "to", fname)

# write detailed/{proto}/{port}.txt
for proto, ports in proto_port_links.items():
    dirpath = os.path.join("detailed", safe_filename(proto.lower()))
    os.makedirs(dirpath, exist_ok=True)
    for port, cfgs in ports.items():
        fname = os.path.join(dirpath, f"{safe_filename(port)}.txt")
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(cfgs))
        print("Wrote", len(cfgs), "to", fname)

# ------------- Build tables (no inlining content) -------------
# Determine display protocol order (preferred first)
preferred = ["VLESS", "VMESS", "TROJAN", "SS", "OTHER"]
protocols_all = sorted(set(protocol_links.keys()), key=lambda p: (0 if p in preferred else 1, preferred.index(p) if p in preferred else p))
# Build stats table (protocol rows x COMMON_PORTS columns)
ports_header = COMMON_PORTS[:]
header_cells = ["Protocol"] + [str(p) for p in ports_header] + ["Total"]
stats_lines = []
stats_lines.append("| " + " | ".join(header_cells) + " |")
stats_lines.append("|" + "|".join(["---"] * len(header_cells)) + "|")

# per-protocol rows
for proto in protocols_all:
    row = [proto]
    total = 0
    for p in ports_header:
        cnt = len(proto_port_links.get(proto, {}).get(str(p), [])) if False else len(proto_port_links.get(proto, {}).get(p, []))
        # sometimes ports are strings, ensure both checks:
        if cnt == 0:
            cnt = len(proto_port_links.get(proto, {}).get(str(p), []))
        total += cnt
        row.append(str(cnt))
    row.append(str(total))
    stats_lines.append("| " + " | ".join(row) + " |")

# totals row
totals = ["**Total**"]
grand_total = 0
for p in ports_header:
    # sum across protocols (handle p as str or int)
    s = 0
    for proto in protocols_all:
        s += len(proto_port_links.get(proto, {}).get(p, [])) if p in proto_port_links.get(proto, {}) else 0
        s += len(proto_port_links.get(proto, {}).get(str(p), []))
    totals.append(str(s))
    grand_total += s
totals.append(str(grand_total))
stats_lines.append("| " + " | ".join(totals) + " |")

stats_table = "\n".join(stats_lines)

# ------------- Links tables (use file links, only common ports shown for port-based lists) -------------
# by protocol (link to ./sub/{proto}.txt)
proto_table_lines = ["| Protocol | Config Count | Subscription Link |", "|----------|--------------|-------------------|"]
for proto in protocols_all:
    path = f"./sub/{safe_filename(proto.lower())}.txt"
    count = len(protocol_links.get(proto, []))
    proto_table_lines.append(f"| {proto} | {count} | [📎 Link]({path}) |")
proto_table = "\n".join(proto_table_lines)

# by port (only COMMON_PORTS)
port_table_lines = ["| Port | Config Count | Subscription Link |", "|------|--------------|-------------------|"]
for p in ports_header:
    path = f"./sub/port_{safe_filename(p)}.txt"
    count = len(port_links.get(str(p), [])) if str(p) in port_links else len(port_links.get(p, []))
    port_table_lines.append(f"| {p} | {count} | [📎 Link]({path}) |")
port_table = "\n".join(port_table_lines)

# detailed (protocol+port) only for common ports and combinations that exist
detailed_table_lines = ["| Protocol | Port | Config Count | Subscription Link |", "|----------|------|--------------|-------------------|"]
for proto in protocols_all:
    for p in ports_header:
        cnt = len(proto_port_links.get(proto, {}).get(p, [])) if p in proto_port_links.get(proto, {}) else 0
        if cnt == 0:
            cnt = len(proto_port_links.get(proto, {}).get(str(p), []))
        if cnt == 0:
            continue
        path = f"./detailed/{safe_filename(proto.lower())}/{safe_filename(p)}.txt"
        detailed_table_lines.append(f"| {proto} | {p} | {cnt} | [📎 Link]({path}) |")
detailed_table = "\n".join(detailed_table_lines)

links_section_text = (
    proto_table + "\n\n" + port_table + "\n\n" + detailed_table +
    "\n\nFor full list of all ports and detailed files, see the [detailed folder](./detailed)."
)

# ------------- Sources summary table -------------
sources_lines = ["| Source | Fetched Lines |", "|--------|---------------|"]
for src, cnt in source_raw_counts.items():
    sources_lines.append(f"| {src} | {cnt} |")
sources_lines.append(f"| **Total fetched** | {total_fetched} |")
sources_lines.append(f"| **Unique configs** | {unique_count} |")
sources_lines.append(f"| **Duplicates removed** | {duplicates} |")
sources_table = "\n".join(sources_lines)

# ------------- README update (backup then replace) -------------
now = datetime.utcnow().replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

stats_block = MARKERS["stats"][0] + "\n" + f"_Last update: {now}_\n\n" + stats_table + "\n" + MARKERS["stats"][1]
links_block = MARKERS["links"][0] + "\n" + links_section_text + "\n" + MARKERS["links"][1]
sources_block = MARKERS["sources"][0] + "\n" + sources_table + "\n" + MARKERS["sources"][1]

if os.path.exists(README_PATH):
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme_text = f.read()
else:
    readme_text = ""

# backup
bak = f"README.md.bak.{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
with open(bak, "w", encoding="utf-8") as bf:
    bf.write(readme_text)
print("Backup written to", bak)

def replace_or_append(text, start_marker, end_marker, new_block):
    if start_marker in text and end_marker in text:
        pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.S)
        text = pattern.sub(new_block, text, count=1)
        return text, True
    else:
        # append at end
        text = text.rstrip() + "\n\n" + new_block + "\n"
        return text, False

# replace stats
readme_text, s_replaced = replace_or_append(readme_text, MARKERS["stats"][0], MARKERS["stats"][1], stats_block)
# replace links
readme_text, l_replaced = replace_or_append(readme_text, MARKERS["links"][0], MARKERS["links"][1], links_block)
# replace sources
readme_text, src_replaced = replace_or_append(readme_text, MARKERS["sources"][0], MARKERS["sources"][1], sources_block)

with open(README_PATH, "w", encoding="utf-8") as f:
    f.write(readme_text)
print("README updated (stats replaced:", s_replaced, "links replaced:", l_replaced, "sources replaced:", src_replaced, ")")

# ------------- Done summary -------------
print("Done.")
print("Total fetched:", total_fetched, "Unique:", unique_count, "Duplicates:", duplicates)
