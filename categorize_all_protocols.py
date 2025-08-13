import os
import re
from collections import defaultdict
from tabulate import tabulate

README_FILE = "README.md"

# تنظیمات پایه
RAW_BASE_URL = "https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main"

def make_raw_link(path):
    """ساخت لینک مستقیم raw برای فایل داخل مخزن"""
    return f"{RAW_BASE_URL}/{path}"

def update_readme_section(section_name, new_content):
    start_marker = f"<!-- START-{section_name.upper()} -->"
    end_marker = f"<!-- END-{section_name.upper()} -->"

    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = f"{start_marker}.*?{end_marker}"
    replacement = f"{start_marker}\n{new_content}\n{end_marker}"

    if re.search(pattern, content, flags=re.S):
        content = re.sub(pattern, replacement, content, flags=re.S)
    else:
        content += f"\n\n{replacement}"

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def generate_stats_table(configs_by_protocol_and_port):
    protocols = sorted(configs_by_protocol_and_port.keys())
    ports = sorted({port for protocol_data in configs_by_protocol_and_port.values() for port in protocol_data})

    table = []
    for proto in protocols:
        row = [proto]
        total_proto = 0
        for port in ports:
            count = len(configs_by_protocol_and_port[proto].get(port, []))
            row.append(count)
            total_proto += count
        row.append(total_proto)
        table.append(row)

    totals_row = ["Total"]
    for port in ports:
        totals_row.append(sum(len(configs_by_protocol_and_port[proto].get(port, [])) for proto in protocols))
    totals_row.append(sum(totals_row[1:]))
    table.append(totals_row)

    headers = ["Protocol"] + [str(p) for p in ports] + ["Total"]
    return tabulate(table, headers=headers, tablefmt="github")

def generate_links_section(configs_by_protocol_and_port, known_ports):
    lines = []
    lines.append("## Subscription Links\n")

    # بر اساس پورت (شامل همه پروتکل‌ها)
    lines.append("### By Port (All Protocols)")
    for port in known_ports:
        lines.append(f"- **Port {port}** → [Subscribe]({make_raw_link(f'sub/port_{port}.txt')})")
    lines.append("")

    # بر اساس پروتکل (بدون جدا کردن پورت‌ها)
    lines.append("### By Protocol (All Ports)")
    for proto in configs_by_protocol_and_port:
        lines.append(f"- **{proto.upper()}** → [Subscribe]({make_raw_link(f'sub/{proto}.txt')})")
    lines.append("")

    # بر اساس پروتکل و پورت
    lines.append("### By Protocol & Port")
    proto_list = list(configs_by_protocol_and_port.keys())
    for i in range(0, len(proto_list), 2):
        row_links = []
        for proto in proto_list[i:i + 2]:
            sub_links = [f"[{p}]({make_raw_link(f'sub/{proto}_{p}.txt')})"
                         for p in sorted(configs_by_protocol_and_port[proto].keys()) if p in known_ports]
            if sub_links:
                row_links.append(f"**{proto.upper()}** → " + ", ".join(sub_links))
        if row_links:
            lines.append(" | ".join(row_links))

    return "\n".join(lines)

def generate_sources_section(source_stats, total, unique, duplicates):
    lines = []
    lines.append("## Sources & Summary\n")
    for src, (repo_url, count) in source_stats.items():
        lines.append(f"- [{src}]({repo_url}) → {count}")
    lines.append("\n---\n")
    lines.append(f"- **Total fetched:** {total}")
    lines.append(f"- **Unique configs:** {unique}")
    lines.append(f"- **Duplicates removed:** {duplicates}")
    return "\n".join(lines)

def replace_between(text, start_tag, end_tag, new_content):
    start_marker = f"<!-- {start_tag} -->"
    end_marker = f"<!-- {end_tag} -->"
    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker)
    if start_idx == -1 or end_idx == -1:
        raise ValueError(f"Markers {start_tag}/{end_tag} not found in README.md")
    return text[:start_idx + len(start_marker)] + new_content + text[end_idx:]

def update_readme(stats_table, links_section, sources_section):
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_between(content, "START-STATS", "END-STATS", f"\n{stats_table}\n")
    content = replace_between(content, "START-LINKS", "END-LINKS", f"\n{links_section}\n")
    content = replace_between(content, "START-SOURCES", "END-SOURCES", f"\n{sources_section}\n")

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

# اجرای اصلی
if __name__ == "__main__":
    KNOWN_PORTS = [80, 443, 2052, 2082, 2086, 2095]
    SOURCES = {
        "barry-far": ("https://github.com/barry-far/v2ray-worker", 15942),
        "kobabi": ("https://github.com/kobabi/v2ray-configs", 313),
        "mahdibland": ("https://github.com/mahdibland/ShadowsocksAggregator", 4906),
        "Epodonios": ("https://github.com/Epodonios/v2ray-configs", 15947),
        "Rayan-Config": ("https://github.com/Rayan-Config/Free-V2ray-Configs", 77)
    }
    total, unique, duplicates = 37185, 21012, 16173

    # داده نمونه
    configs_by_protocol_and_port = {
        "vless": {443: ["a", "b"], 80: ["c"]},
        "vmess": {443: ["d"], 80: ["e", "f"]},
        "trojan": {443: ["g"]},
        "ss": {80: ["h"]}
    }

    stats_table = generate_stats_table(configs_by_protocol_and_port)
    links_section = generate_links_section(configs_by_protocol_and_port, KNOWN_PORTS)
    sources_section = generate_sources_section(SOURCES, total, unique, duplicates)

    update_readme(stats_table, links_section, sources_section)
