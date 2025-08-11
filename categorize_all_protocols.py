#!/usr/bin/env python3
# categorize_all_protocols_safe.py
# Updates README only between markers, writes sub/ and detailed/ files, no backups, no inline content.

import os
import re
import requests
import json
import base64
from urllib.parse import urlparse
from collections import defaultdict
from datetime import datetime, timezone

# ====== config ======
SOURCES = {
    "barry-far": "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "kobabi": "https://raw.githubusercontent.com/liketolivefree/kobabi/main/sub.txt",
    "mahdibland": "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "Epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "Rayan-Config": "https://raw.githubusercontent.com/Rayan-Config/C-Sub/refs/heads/main/configs/proxy.txt",
}
COMMON_PORTS = [80, 443, 8080, 2053, 2083, 2087, 2096]  # edit if you want different popular ports
README_PATH = "README.md"
MARKERS = {
    "stats": ("<!-- START-STATS -->", "<!-- END-STATS -->"),
    "links": ("<!-- START-LINKS -->", "<!-- END-LINKS -->"),
    "sources": ("<!-- START-SOURCES -->", "<!-- END-SOURCES -->"),
}
SUB_DIR = "sub"
DETAILED_DIR = "detailed"
PREFERRED_ORDER = ["VLESS", "VMESS", "TROJAN", "SS", "OTHER"]

# ====== helpers ======
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
    proto = None
    port = None
    try:
        if cfg.startswith("vmess://"):
            proto = "VMESS"
            b64 = cfg[8:]
            pad = len(b64) % 4
            if pad:
                b64 += "=" * (4 - pad)
            dec = base64.b64decode(b64).decode("utf-8", errors="ignore")
            data = json.loads(dec)
            port = str(data.get("port") or data.get("Port") or "") or None
        else:
            parsed = urlparse(cfg)
            scheme = (parsed.scheme or "").lower()
            if scheme == "vless":
                proto = "VLESS"
            elif scheme == "trojan":
                proto = "TROJAN"
            elif scheme == "ss":
                proto = "SS"
            # port from parsed
            if parsed.port:
                port = str(parsed.port)
            else:
                net = parsed.netloc or ""
                if "@" in net:
                    net = net.rsplit("@", 1)[-1]
                if ":" in net:
                    p = net.rsplit(":", 1)[-1]
                    if p.isdigit():
                        port = p
                else:
                    # try ss://<base64> fallback
                    if scheme == "ss":
                        m = re.match(r"^ss://([^#]+)", cfg)
                        if m:
                            rest = m.group(1)
                            if "@" not in rest:
                                pad = len(rest) % 4
                                if pad:
                                    rest += "=" * (4 - pad)
                                try:
                                    dec = base64.b64decode(rest).decode("utf-8", errors="ignore")
                                    if ":" in dec and "@" in dec:
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

# ====== fetch and parse sources ======
print("Fetching sources...")
all_items = []  # list of (cfg_line, source_name)
source_raw_counts = defaultdict(int)
for name, url in SOURCES.items():
    try:
        r = requests.get(url, timeout=25)
        if r.status_code == 200 and r.text:
            cfgs = parse_configs(r.text)
            for c in cfgs:
                all_items.append((c.strip(), name))
            source_raw_counts[name] = len(cfgs)
            print(f"  {name}: {len(cfgs)} lines")
        else:
            print(f"  warning: {name} returned {getattr(r,'status_code','ERR')}")
    except Exception as e:
        print(f"  error fetching {name}: {e}")

total_fetched = len(all_items)
print("Total fetched:", total_fetched)

# ====== deduplicate & categorize ======
seen = set()
duplicates = 0
protocol_links = defaultdict(list)           # proto -> [cfg...]
port_links = defaultdict(list)               # port_str -> [cfg...]
proto_port_links = defaultdict(lambda: defaultdict(list))  # proto -> port_str -> [cfg...]

for cfg, src in all_items:
    k = cfg
    if k in seen:
        duplicates += 1
        continue
    seen.add(k)
    proto, port = extract_info(cfg)
    if proto and port:
        port_s = str(port)
        proto_port_links[proto][port_s].append(cfg)
        protocol_links[proto].append(cfg)
        port_links[port_s].append(cfg)
    else:
        proto_port_links["OTHER"]["unknown"].append(cfg)
        protocol_links["OTHER"].append(cfg)
        port_links["unknown"].append(cfg)

unique_count = len(seen)
print("Unique:", unique_count, "Duplicates removed:", duplicates)

# ====== write files to sub/ and detailed/ ======
os.makedirs(SUB_DIR, exist_ok=True)
os.makedirs(DETAILED_DIR, exist_ok=True)

# write per-protocol files
for proto, cfgs in protocol_links.items():
    fname = os.path.join(SUB_DIR, f"{safe_filename(proto.lower())}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(cfgs))
    print("Wrote", len(cfgs), "to", fname)

# write per-port files
for port_s, cfgs in port_links.items():
    fname = os.path.join(SUB_DIR, f"port_{safe_filename(port_s)}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(cfgs))
    print("Wrote", len(cfgs), "to", fname)

# write detailed/{proto}/{port}.txt
for proto, ports in proto_port_links.items():
    proto_dir = os.path.join(DETAILED_DIR, safe_filename(proto.lower()))
    os.makedirs(proto_dir, exist_ok=True)
    for port_s, cfgs in ports.items():
        fname = os.path.join(proto_dir, f"{safe_filename(port_s)}.txt")
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(cfgs))
        # no verbose print for each to avoid too long logs

# ====== build stats table (protocol rows x common ports columns) ======
# protocols order: preferred then rest alpha
protocols_all = sorted(set(protocol_links.keys()), key=lambda p: (0 if p in PREFERRED_ORDER else 1, PREFERRED_ORDER.index(p) if p in PREFERRED_ORDER else p))

ports_header = COMMON_PORTS
# header
header_cells = ["Protocol"] + [str(p) for p in ports_header] + ["Total"]
stats_lines = []
stats_lines.append("| " + " | ".join(header_cells) + " |")
stats_lines.append("|" + "|".join(["---"] * len(header_cells)) + "|")

# rows
for proto in protocols_all:
    total = 0
    row_cells = [proto]
    for p in ports_header:
        cnt = len(proto_port_links.get(proto, {}).get(str(p), []))
        row_cells.append(str(cnt))
        total += cnt
    row_cells.append(str(total))
    stats_lines.append("| " + " | ".join(row_cells) + " |")

# totals row
totals = ["**Total**"]
grand_total = 0
for p in ports_header:
    s = 0
    for proto in protocols_all:
        s += len(proto_port_links.get(proto, {}).get(str(p), []))
    totals.append(str(s))
    grand_total += s
totals.append(str(grand_total))
stats_lines.append("| " + " | ".join(totals) + " |")

stats_table = "\n".join(stats_lines)

# ====== build subscription links table (grouped by protocol, separator between protocols) ======
subs_lines = ["| Protocol | Port | Link |", "|----------|------|------|"]
for idx, proto in enumerate(protocols_all):
    # find ports from common ports that exist for this proto
    ports_present = [p for p in ports_header if len(proto_port_links.get(proto, {}).get(str(p), [])) > 0]
    if not ports_present:
        continue
    for i, p in enumerate(ports_present):
        link_path = f"./{SUB_DIR}/{safe_filename(proto.lower())}_{safe_filename(str(p))}.txt"
        if i == 0:
            subs_lines.append(f"| **{proto}** | {p} | [📎 Link]({link_path}) |")
        else:
            subs_lines.append(f"|  | {p} | [📎 Link]({link_path}) |")
    # add bold separator row between protocols (visual gap), except after last one
    if idx < len(protocols_all) - 1:
        subs_lines.append("| **---** | **---** | **---** |")

subs_lines.append("\n> ℹ️ More ports and protocols are available in the `sub/` and `detailed/` folders.")
subs_section = "\n".join(subs_lines)

# ====== build sources table + summary ======
sources_table_lines = ["| Source | Collected |", "|--------|-----------|"]
for src, cnt in source_raw_counts.items():
    sources_table_lines.append(f"| {src} | {cnt} |")
sources_table = "\n".join(sources_table_lines)

# summary table (after a horizontal rule)
summary_lines = [
    "",
    "\n---\n",
    "| Metric | Value |",
    "|--------|-------|",
    f"| Total fetched | {total_fetched} |",
    f"| Duplicates removed | {duplicates} |",
    f"| Unique configs | {unique_count} |",
]
summary_table = "\n".join(summary_lines)

sources_section = sources_table + summary_table

# ====== replace only between markers; require markers exist ======
if not os.path.exists(README_PATH):
    print("ERROR: README.md not found in repo root. Please create README.md with markers and re-run.")
    raise SystemExit(1)

with open(README_PATH, "r", encoding="utf-8") as f:
    rd = f.read()

# check markers presence
missing = [k for k, (s, e) in MARKERS.items() if s not in rd or e not in rd]
if missing:
    print("ERROR: The following markers are missing in README.md:", missing)
    print("Please add these markers at appropriate places in README.md before running the script:")
    for k in missing:
        s, e = MARKERS[k]
        print(f"  {k}: {s} ... {e}")
    raise SystemExit(1)

# do replacements
def replace_block(text, start_marker, end_marker, new_block):
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.S)
    return pattern.sub(new_block, text, count=1)

rd = replace_block(rd, MARKERS["stats"][0], MARKERS["stats"][1], MARKERS["stats"][0] + "\n" + f"_Last update: {datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}_\n\n" + stats_table + "\n" + MARKERS["stats"][1])
rd = replace_block(rd, MARKERS["links"][0], MARKERS["links"][1], MARKERS["links"][0] + "\n" + subs_section + "\n" + MARKERS["links"][1])
rd = replace_block(rd, MARKERS["sources"][0], MARKERS["sources"][1], MARKERS["sources"][0] + "\n" + sources_section + "\n" + MARKERS["sources"][1])

with open(README_PATH, "w", encoding="utf-8") as f:
    f.write(rd)

print("README updated successfully (markers replaced). No backups were created.")
print(f"Files written to '{SUB_DIR}/' and '{DETAILED_DIR}/'.")
