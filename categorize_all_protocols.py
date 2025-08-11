import os
import base64
from collections import defaultdict
import glob

# پورت‌های معروف
COMMON_PORTS = [80, 443, 8080, 2053, 2083, 2087, 2096]

README_FILE = "README.md"

def read_existing_readme():
    if os.path.exists(README_FILE):
        with open(README_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def write_updated_readme(content):
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def generate_stats_table(proto_port_counts):
    ports_sorted = sorted(COMMON_PORTS)
    protocols_sorted = sorted(proto_port_counts.keys())

    header = "| Protocol | " + " | ".join(map(str, ports_sorted)) + " | Total |\n"
    header += "|----------|" + "|".join(["---"] * (len(ports_sorted) + 1)) + "|\n"

    rows = ""
    for proto in protocols_sorted:
        total = 0
        row = f"| {proto} "
        for port in ports_sorted:
            count = proto_port_counts[proto].get(port, 0)
            total += count
            row += f"| {count} "
        row += f"| {total} |\n"
        rows += row

    totals_row = "| **Total** "
    for port in ports_sorted:
        totals_row += f"| {sum(proto_port_counts[p].get(port, 0) for p in protocols_sorted)} "
    totals_row += f"| {sum(sum(ports.values()) for ports in proto_port_counts.values())} |\n"

    return header + rows + totals_row

def generate_links_tables(proto_links, port_links, detailed_links):
    # جدول اول: بر اساس پروتکل
    proto_table = "| Protocol | Subscription Link |\n|----------|--------------------|\n"
    for proto, links in proto_links.items():
        b64 = base64.b64encode("\n".join(links).encode()).decode()
        proto_table += f"| {proto} | [📎 Link](data:text/plain;base64,{b64}) |\n"

    # جدول دوم: بر اساس پورت
    port_table = "| Port | Subscription Link |\n|------|--------------------|\n"
    for port, links in port_links.items():
        b64 = base64.b64encode("\n".join(links).encode()).decode()
        port_table += f"| {port} | [📎 Link](data:text/plain;base64,{b64}) |\n"

    # جدول سوم: بر اساس پروتکل+پورت
    detailed_table = "| Protocol+Port | Subscription Link |\n|---------------|--------------------|\n"
    for key, links in detailed_links.items():
        b64 = base64.b64encode("\n".join(links).encode()).decode()
        detailed_table += f"| {key} | [📎 Link](data:text/plain;base64,{b64}) |\n"

    return proto_table, port_table, detailed_table

def main():
    proto_port_counts = defaultdict(lambda: defaultdict(int))
    proto_links = defaultdict(list)
    port_links = defaultdict(list)
    detailed_links = defaultdict(list)

    # خواندن فایل‌های پوشه sub
    for file_path in glob.glob("sub/*.txt"):
        file_name = os.path.basename(file_path)
        try:
            proto, port = file_name.replace(".txt", "").split("_")
            port = int(port)
        except ValueError:
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]

        if port in COMMON_PORTS:
            proto_port_counts[proto][port] += len(lines)
            proto_links[proto].extend(lines)
            port_links[port].extend(lines)
            detailed_links[f"{proto} {port}"].extend(lines)

    # جدول آمار
    stats_table = generate_stats_table(proto_port_counts)

    # سه جدول لینک
    proto_table, port_table, detailed_table = generate_links_tables(proto_links, port_links, detailed_links)

    # خواندن README موجود
    readme_content = read_existing_readme()

    # جایگزینی تگ‌ها
    import re
    readme_content = re.sub(r"(<!-- START-STATS -->)(.*?)(<!-- END-STATS -->)", f"\\1\n{stats_table}\n\\3", readme_content, flags=re.S)
    links_section = f"{proto_table}\n\n{port_table}\n\n{detailed_table}\n\nFor a full list of ports and subscriptions, visit the [detailed folder](./detailed)."
    readme_content = re.sub(r"(<!-- START-LINKS -->)(.*?)(<!-- END-LINKS -->)", f"\\1\n{links_section}\n\\3", readme_content, flags=re.S)

    write_updated_readme(readme_content)

if __name__ == "__main__":
    main()
