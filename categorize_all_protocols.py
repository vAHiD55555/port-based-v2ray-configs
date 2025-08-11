import os
import datetime
from collections import defaultdict
from tabulate import tabulate

# تنظیمات
KNOWN_PORTS = [80, 443, 2053, 2083, 2087, 2096, 8443]
PROTOCOLS = ["VLESS", "VMESS", "TROJAN"]
DATA_DIR = "data"
RAW_FILE = os.path.join(DATA_DIR, "raw.txt")
SUBS_FILE = os.path.join(DATA_DIR, "subs.txt")
DETAIL_FILE = os.path.join(DATA_DIR, "detailed.txt")
README_FILE = "README.md"

# کمک کننده برای خواندن دیتا
def read_lines(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

# آمار بر اساس پروتکل و پورت
def build_statistics(configs):
    stats = defaultdict(lambda: defaultdict(int))
    for conf in configs:
        proto = conf.split("://")[0].upper()
        port = int(conf.split(":")[-1].split("?")[0].split("/")[0])
        stats[proto][port] += 1
        stats[proto]["total"] += 1
        stats["TOTAL"][port] += 1
        stats["TOTAL"]["total"] += 1
    ports_sorted = sorted({p for proto in stats for p in stats[proto] if p != "total"})
    headers = ["Protocol"] + [str(p) for p in ports_sorted] + ["Total"]
    table = []
    for proto in PROTOCOLS + ["TOTAL"]:
        row = [proto] + [stats[proto].get(p, 0) for p in ports_sorted] + [stats[proto]["total"]]
        table.append(row)
    return "### Statistics (Protocol × Common Ports)\n\n" + \
           f"Last update: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n" + \
           tabulate(table, headers=headers, tablefmt="github")

# لینک‌های اشتراک
def build_subscription_links(configs):
    base_url = "https://example.com/sub"
    links = []

    # بر اساس پورت (همه پروتکل‌ها)
    links.append("#### By Port (all protocols)\n")
    for p in KNOWN_PORTS:
        links.append(f"- **Port {p}** → [Link]({base_url}?port={p})")

    # بر اساس پروتکل
    links.append("\n#### By Protocol\n")
    for proto in PROTOCOLS:
        links.append(f"- **{proto}** → [Link]({base_url}?proto={proto.lower()})")

    # بر اساس پروتکل + پورت (دو ستونه)
    links.append("\n#### By Protocol × Port\n")
    rows = []
    for proto in PROTOCOLS:
        row = [f"**{proto} {p}** → [Link]({base_url}?proto={proto.lower()}&port={p})"
               for p in KNOWN_PORTS]
        for i in range(0, len(row), 2):
            rows.append(row[i:i+2])
    links.append(tabulate(rows, tablefmt="github"))

    return "### Subscription Links\n\n" + "\n".join(links)

# منابع و خلاصه
def build_sources_summary(configs):
    total = len(configs)
    unique = len(set(configs))
    duplicates = total - unique
    table = [
        ["Total Retrieved", total],
        ["Duplicates Removed", duplicates],
        ["Unique Configs", unique]
    ]
    return "### Sources & Summary\n\n" + tabulate(table, headers=["Metric", "Value"], tablefmt="github")

# تولید README
def generate_readme():
    configs = read_lines(RAW_FILE)
    stats_section = build_statistics(configs)
    subs_section = build_subscription_links(configs)
    summary_section = build_sources_summary(configs)
    notes = "### Notes\n\n- Script auto-generates subscription links and statistics.\n- Includes only popular ports in main table."

    content = [
        "# Port-based V2Ray Configs",
        stats_section,
        subs_section,
        summary_section,
        notes
    ]
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write("\n\n".join(content))
    print(f"README.md updated with {len(configs)} configs.")

if __name__ == "__main__":
    generate_readme()
