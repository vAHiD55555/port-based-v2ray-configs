import os
import re

README_FILE = "README.md"
SUB_DIR = "subs"
DETAILED_DIR = "detailed"

COMMON_PORTS = [80, 443, 8443, 2083, 2053]  # پورت‌های معروف
PROTOCOLS = ["vless", "vmess", "trojan", "ss"]


def generate_subscription_links():
    md = "## Subscription Links\n\n"

    # Table 1: By Port
    md += "### By Port\n"
    md += "| Port | Link |\n|------|------|\n"
    for port in COMMON_PORTS:
        md += f"| {port} | [Link]({SUB_DIR}/port_{port}.txt) |\n"
    md += "\n---\n\n"

    # Table 2: By Protocol
    md += "### By Protocol\n"
    md += "| Protocol | Link |\n|----------|------|\n"
    for proto in PROTOCOLS:
        md += f"| {proto.upper()} | [Link]({SUB_DIR}/{proto}.txt) |\n"
    md += "\n---\n\n"

    # Table 3: By Protocol & Port
    md += "### By Protocol & Port\n"
    md += "| Protocol | Port | Link | Protocol | Port | Link |\n"
    md += "|----------|------|------|----------|------|------|\n"

    # دو ستونه برای صرفه‌جویی در فضا
    half = (len(COMMON_PORTS) + 1) // 2
    for i in range(half):
        left = f"{PROTOCOLS[0].upper()} | {COMMON_PORTS[i]} | [Link]({SUB_DIR}/{PROTOCOLS[0]}_{COMMON_PORTS[i]}.txt)" if i < len(COMMON_PORTS) else " |  | "
        right = f"{PROTOCOLS[1].upper()} | {COMMON_PORTS[i]} | [Link]({SUB_DIR}/{PROTOCOLS[1]}_{COMMON_PORTS[i]}.txt)" if i < len(COMMON_PORTS) else " |  | "
        md += f"| {left} | {right} |\n"

    for proto in PROTOCOLS[2:]:
        for port in COMMON_PORTS:
            md += f"| {proto.upper()} | {port} | [Link]({SUB_DIR}/{proto}_{port}.txt) |    |    |    |\n"

    return md


def update_readme():
    if not os.path.exists(README_FILE):
        print(f"{README_FILE} not found.")
        return

    with open(README_FILE, "r", encoding="utf-8") as f:
        readme_content = f.read()

    # جایگزینی بخش Subscription Links با نسخه جدید
    new_links_section = generate_subscription_links()
    updated_content = re.sub(
        r"## Subscription Links.*?(?=\n##|\Z)",
        new_links_section,
        readme_content,
        flags=re.S
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print("README.md updated successfully.")


if __name__ == "__main__":
    update_readme()
