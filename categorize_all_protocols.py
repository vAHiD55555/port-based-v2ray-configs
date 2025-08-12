import os
from collections import defaultdict
from tabulate import tabulate

# سورس‌ها با اسم و لینک ریپوی اصلی
SOURCES = {
    "barry-far": "https://github.com/barry-far/v2ray-worker",
    "kobabi": "https://github.com/kobabi/v2ray-configs",
    "mahdibland": "https://github.com/mahdibland/ShadowsocksAggregator",
    "Epodonios": "https://github.com/Epodonios/v2ray-configs",
    "Rayan-Config": "https://github.com/Rayan-Config/Free-V2ray-Configs"
}

# پورت‌های معروف برای نمایش در جدول و لینک‌ها
KNOWN_PORTS = [80, 443, 2052, 2082, 2086, 2095]

# تابع ساخت جدول آماری
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

# ساخت لینک‌های raw
def make_raw_link(path):
    return f"https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/refs/heads/main/{path}"

# ساخت بخش Subscription Links
def generate_links_section(configs_by_protocol_and_port):
    lines = []
    lines.append("## Subscription Links\n")
    
    # بر اساس پورت (شامل همه پروتکل‌ها)
    lines.append("### By Port (All Protocols)")
    for port in KNOWN_PORTS:
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
        for proto in proto_list[i:i+2]:
            sub_links = [f"[{p}]({make_raw_link(f'sub/{proto}_{p}.txt')})" 
                         for p in sorted(configs_by_protocol_and_port[proto].keys()) if p in KNOWN_PORTS]
            if sub_links:
                row_links.append(f"**{proto.upper()}** → " + ", ".join(sub_links))
        if row_links:
            lines.append(" | ".join(row_links))
    
    return "\n".join(lines)

# ساخت بخش سورس‌ها و خلاصه آمار
def generate_sources_section(source_stats, total, unique, duplicates):
    lines = []
    lines.append("## Sources & Summary\n")
    for src, count in source_stats.items():
        lines.append(f"- [{src}]({SOURCES[src]}) → {count}")
    lines.append("\n---\n")
    lines.append(f"- **Total fetched:** {total}")
    lines.append(f"- **Unique configs:** {unique}")
    lines.append(f"- **Duplicates removed:** {duplicates}")
    return "\n".join(lines)

# بروزرسانی README بین تگ‌ها
def update_readme(stats_table, links_section, sources_section):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    content = replace_between(content, "START-STATS", "END-STATS", f"\n{stats_table}\n")
    content = replace_between(content, "START-LINKS", "END-LINKS", f"\n{links_section}\n")
    content = replace_between(content, "START-SOURCES", "END-SOURCES", f"\n{sources_section}\n")
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

# تابع جایگزینی بین تگ‌ها
def replace_between(text, start_tag, end_tag, new_content):
    start_marker = f"<!-- {start_tag} -->"
    end_marker = f"<!-- {end_tag} -->"
    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker)
    if start_idx == -1 or end_idx == -1:
        raise ValueError(f"Markers {start_tag}/{end_tag} not found in README.md")
    return text[:start_idx+len(start_marker)] + new_content + text[end_idx:]

# --- اجرای اصلی ---
if __name__ == "__main__":
    # اینجا باید داده‌های واقعی از پردازش قبلی بیاد
    configs_by_protocol_and_port = {
        "vless": {443: ["a","b"], 80: ["c"]},
        "vmess": {443: ["d"], 80: ["e","f"]},
        "trojan": {443: ["g"]},
        "ss": {80: ["h"]}
    }
    source_stats = {
        "barry-far": 15942,
        "kobabi": 313,
        "mahdibland": 4906,
        "Epodonios": 15947,
        "Rayan-Config": 77
    }
    total, unique, duplicates = 37185, 21012, 16173
    
    stats_table = generate_stats_table(configs_by_protocol_and_port)
    links_section = generate_links_section(configs_by_protocol_and_port)
    sources_section = generate_sources_section(source_stats, total, unique, duplicates)
    
    update_readme(stats_table, links_section, sources_section)
