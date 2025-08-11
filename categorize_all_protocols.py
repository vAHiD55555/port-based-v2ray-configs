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
COMMON_PORTS = [80, 443, 2053, 2083, 2087, 2096, 8443]  # popular ports shown in README
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
    """Return (PROTO, PORT) as (str, str) or (None, None) on failure."""
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
            # port detection
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
                    # ss://<base64> fallback
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
                                    # often like "method:pass@host:port"
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

# build markdown table helpers
def md_table_from_rows(header_cells, rows):
    """header_cells: list of header strings
       rows: list of list of cell strings
       returns markdown table string"""
    header = "| " + " | ".join(header_cells) + " |"
    sep = "|" + "|".join(["---"] * len(header_cells)) + "|"
    body = "\n".join("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join([header, sep, body])

# ---------------- Fetch sources ----------------
print("Fetching sources...")
all_items = []   # (cfg_line, source_name)
source_counts = defaultdict(int)
for name, url in SOURCES.items():
    try:
        r = requests.get(url, timeout=25)
        if r.status_code == 200 and r.text:
            cfgs = parse_configs(r.text)
            for c in cfgs:
                all_items.append((c.strip(), name))
            source_counts[name] = len(cfgs)
            print(f"  fetched {len(cfgs)} from {name}")
        else:
            print(f"  warning: {name} returned status {getattr(r,'status_code','ERR')}")
    except Exception as e:
        print(f"  error fetching {name}: {e}")

total_fetched = len(all_items)
print("Total fetched:", total_fetched)

# ---------------- Dedupe & categorize ----------------
seen = set()
duplicates = 0
protocol_links = defaultdict(list)            # proto -> [cfg...]
port_links = defaultdict(list)                # port_str -> [cfg...]
proto_port_links = defaultdict(lambda: defaultdict(list))  # proto -> port_str -> [cfg...]

for cfg, src in all_items:
    key = cfg
    if key in seen:
        duplicates += 1
        continue
    seen.add(key)
    proto, port = extract_info(cfg)
    if proto and port:
        port_s = str(port)
        protocol_links[proto].append(cfg)
        port_links[port_s].append(cfg)
        proto_port_links[proto][port_s].append(cfg)
    else:
        protocol_links["OTHER"].append(cfg)
        port_links["unknown"].append(cfg)
        proto_port_links["OTHER"]["unknown"].append(cfg)

unique_count = len(seen)
print("Unique configs:", unique_count, "duplicates removed:", duplicates)

# ---------------- Write files ----------------
os.makedirs(SUB_DIR, exist_ok=True)
os.makedirs(DETAILED_DIR, exist_ok=True)

for proto, cfgs in protocol_links.items():
    fname = os.path.join(SUB_DIR, f"{safe_filename(proto.lower())}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(cfgs))
    # print(f"Wrote {len(cfgs)} to {fname}")

for port_s, cfgs in port_links.items():
    fname = os.path.join(SUB_DIR, f"port_{safe_filename(port_s)}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(cfgs))
    # print(f"Wrote {len(cfgs)} to {fname}")

for proto, ports in proto_port_links.items():
    dirpath = os.path.join(DETAILED_DIR, safe_filename(proto.lower()))
    os.makedirs(dirpath, exist_ok=True)
    for port_s, cfgs in ports.items():
        fname = os.path.join(dirpath, f"{safe_filename(port_s)}.txt")
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(cfgs))
        # no print per-file to keep logs small

# ---------------- Build Stats table ----------------
# protocol ordering
protocols_all = sorted(set(protocol_links.keys()), key=lambda p: (0 if p in PREFERRED else 1, PREFERRED.index(p) if p in PREFERRED else p))

ports_header = COMMON_PORTS
header_cells = ["Protocol"] + [str(p) for p in ports_header] + ["Total"]
rows = []
for proto in protocols_all:
    total = 0
    row = [proto]
    for p in ports_header:
        cnt = len(proto_port_links.get(proto, {}).get(str(p), []))
        row.append(str(cnt))
        total += cnt
    row.append(str(total))
    rows.append(row)

# totals row
totals = ["Total"]
grand = 0
for p in ports_header:
    s = 0
    for proto in protocols_all:
        s += len(proto_port_links.get(proto, {}).get(str(p), []))
    totals.append(str(s))
    grand += s
totals.append(str(grand))
rows.append(totals)

stats_table_md = md_table_from_rows(header_cells, rows)

# ---------------- Build Subscription Links section ----------------
# 1) By Port
port_rows = []
for p in ports_header:
    path = f"./{SUB_DIR}/port_{safe_filename(p)}.txt"
    count = len(port_links.get(str(p), [])) if str(p) in port_links else len(port_links.get(p, []))
    port_rows.append([str(p), f"{count}", f"[📎 Link]({path})"])
port_table_md = md_table_from_rows(["Port", "Config Count", "Subscription Link"], port_rows)

# 2) By Protocol
proto_rows = []
for proto in protocols_all:
    path = f"./{SUB_DIR}/{safe_filename(proto.lower())}.txt"
    count = len(protocol_links.get(proto, []))
    proto_rows.append([proto, str(count), f"[📎 Link]({path})"])
proto_table_md = md_table_from_rows(["Protocol", "Config Count", "Subscription Link"], proto_rows)

# 3) By Protocol + Port (grouped by protocol, two entries per row)
pp_rows = []
pp_md_lines = []
for proto in protocols_all:
    entries = []
    for p in ports_header:
        cnt = len(proto_port_links.get(proto, {}).get(str(p), []))
        if cnt == 0:
            continue
        path = f"./{DETAILED_DIR}/{safe_filename(proto.lower())}/{safe_filename(str(p))}.txt"
        entries.append((proto, str(p), cnt, path))
    if not entries:
        continue
    # produce two-per-row lines for this protocol group
    for i in range(0, len(entries), 2):
        left = entries[i]
        right = entries[i+1] if i+1 < len(entries) else None
        if right:
            pp_md_lines.append(f"| {left[0]} | {left[1]} | [📎 Link]({left[3]}) | {right[0]} | {right[1]} | [📎 Link]({right[3]}) |")
        else:
            pp_md_lines.append(f"| {left[0]} | {left[1]} | [📎 Link]({left[3]}) |  |  |  |")
    # separator row between protocols
    pp_md_lines.append("| **---** | **---** | **---** | **---** | **---** | **---** |")

# remove last separator if exists
if pp_md_lines and pp_md_lines[-1].startswith("| **---**"):
    pp_md_lines = pp_md_lines[:-1]

pp_header = "| Protocol | Port | Link | Protocol | Port | Link |"
pp_sep = "|----------|------|------|----------|------|------|"
pp_section_md = pp_header + "\n" + pp_sep + "\n" + "\n".join(pp_md_lines) if pp_md_lines else "_No protocol+port combos found for common ports._"

# ---------------- Build Sources & Summary ----------------
sources_rows = []
for src, cnt in source_counts.items():
    sources_rows.append([src, str(cnt)])
sources_table_md = md_table_from_rows(["Source", "Fetched Lines"], sources_rows)

summary_rows = [
    ["Total fetched", str(total_fetched)],
    ["Duplicates removed", str(duplicates)],
    ["Unique configs", str(unique_count)]
]
summary_table_md = md_table_from_rows(["Metric", "Value"], summary_rows)

# ---------------- Compose dynamic blocks ----------------
now_ts = datetime.utcnow().replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

stats_block = MARKERS["stats"][0] + "\n" + f"_Last update: {now_ts}_\n\n" + stats_table_md + "\n" + MARKERS["stats"][1]
links_block = MARKERS["links"][0] + "\n" + "## Subscription Links (popular ports only)\n\n" + "**By Port**\n\n" + port_table_md + "\n\n" + "**By Protocol**\n\n" + proto_table_md + "\n\n" + "**By Protocol & Port**\n\n" + (pp_section_md if pp_md_lines else "_No entries found_") + "\n\nFor full list and other ports see the `detailed/` folder.\n" + MARKERS["links"][1]
sources_block = MARKERS["sources"][0] + "\n" + "## Sources & Summary\n\n" + sources_table_md + "\n\n" + "---\n\n" + summary_table_md + "\n" + MARKERS["sources"][1]

# ---------------- Update README (require markers present) ----------------
if not os.path.exists(README_PATH):
    print("ERROR: README.md not found. Please create README.md and add the markers.")
    raise SystemExit(1)

with open(README_PATH, "r", encoding="utf-8") as f:
    readme_text = f.read()

missing = [k for k, (s, e) in MARKERS.items() if s not in readme_text or e not in readme_text]
if missing:
    print("ERROR: The following markers are missing in README.md:", missing)
    print("Please add these markers to README.md before running the script:")
    for k in missing:
        s, e = MARKERS[k]
        print(f"  {k}: {s} ... {e}")
    raise SystemExit(1)

def replace_between_markers(text, start_marker, end_marker, block):
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.S)
    return pattern.sub(block, text, count=1)

readme_text = replace_between_markers(readme_text, MARKERS["stats"][0], MARKERS["stats"][1], stats_block)
readme_text = replace_between_markers(readme_text, MARKERS["links"][0], MARKERS["links"][1], links_block)
readme_text = replace_between_markers(readme_text, MARKERS["sources"][0], MARKERS["sources"][1], sources_block)

with open(README_PATH, "w", encoding="utf-8") as f:
    f.write(readme_text)

print("README updated successfully.")
print(f"Wrote subscription files to '{SUB_DIR}/' and detailed files to '{DETAILED_DIR}/'.")
print(f"Summary: fetched={total_fetched}, unique={unique_count}, duplicates={duplicates}")
