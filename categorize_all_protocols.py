import requests
import base64
import json
import os
import re
from collections import defaultdict
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta

# === Config Sources ===
SOURCES = {
    "barry-far": "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "mahdibland": "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "Epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "soroushmirzaei": "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/mixed"
}

# === Classification Parameters ===
FAMOUS_PORTS = {'80', '443', '8080', '8088', '2052', '2053', '2082', '2083', '2086', '2087', '2095', '2096'}
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY', 'hamed1124/port-based-v2ray-configs')


def fetch_all_configs(sources_dict):
    raw_configs_list, source_stats = [], defaultdict(int)
    print("Fetching configs from sources...")
    for name, url in sources_dict.items():
        try:
            print(f"--> Fetching from: {name}...")
            response = requests.get(url, timeout=120)
            if response.status_code == 200 and response.text:
                content = response.text.strip()
                try:
                    configs = base64.b64decode(content).decode('utf-8').strip().split('\n') if len(content) > 1000 and "://" not in content else content.split('\n')
                    valid_configs = [line.strip() for line in configs if line.strip() and '://' in line]
                    if valid_configs:
                        raw_configs_list.extend(valid_configs)
                        source_stats[name] = len(valid_configs)
                        print(f"  ✅ Added {len(valid_configs)} valid configs from {name}.")
                except Exception as e:
                    print(f"  ⚠️ Error processing content from {name}: {e}")
        except requests.RequestException as e:
            print(f"❌ Connection error for {name}: {e}")
            
    raw_total = len(raw_configs_list)
    unique_configs = list(set(raw_configs_list))
    print(f"\nFetched {raw_total} configs in total. Found {len(unique_configs)} unique configs.")
    return unique_configs, source_stats, raw_total

def get_config_info(link):
    try:
        protocol = link.split("://")[0].lower()
        port = None
        if protocol == "vless":
            port = str(urlparse(link).port)
        elif protocol in ["trojan", "tuic", "hysteria2", "hy2"]:
            protocol = "hysteria2" if protocol in ["hy2", "hysteria2"] else protocol
            port = str(urlparse(link).port)
        elif protocol == "vmess":
            b64_part = link.replace("vmess://", "") + '=' * (-len(link.replace("vmess://", "")) % 4)
            config_json = json.loads(base64.b64decode(b64_part).decode('utf-8'))
            port = str(config_json.get('port'))
        elif protocol == "ss":
            protocol = "shadowsocks"
            if '@' in (main_part := link.split('#')[0]):
                port = str(urlparse(main_part).port)
            else:
                b64_part = main_part.replace("ss://", "") + '=' * (-len(main_part.replace("ss://", "")) % 4)
                port = str(base64.b64decode(b64_part).decode('utf-8').split('@')[1].split(':')[-1])
        else:
            return None, None
        return (protocol, port) if (port and port.isdigit()) else (None, None)
    except Exception:
        return None, None

def get_tehran_time():
    tehran_tz = timezone(timedelta(hours=3, minutes=30))
    now_tehran = datetime.now(timezone.utc).astimezone(tehran_tz)
    return now_tehran.strftime("%Y-%m-%d %H:%M:%S Tehran Time")

def update_readme(stats):
    try:
        print("\nUpdating README.md...")
        with open('README.template.md', 'r', encoding='utf-8') as f:
            template_content = f.read()

        detailed_stats = stats.get('detailed_stats', {})
        protocol_totals = {p: sum(len(cfgs) for cfgs in data.values()) for p, data in detailed_stats.items()}
        sorted_protocols = sorted(protocol_totals.keys(), key=lambda p: protocol_totals[p], reverse=True)
        port_totals = {port: sum(len(detailed_stats.get(p, {}).get(port, [])) for p in sorted_protocols) for port in FAMOUS_PORTS}
        sorted_ports = sorted(port_totals.keys(), key=lambda p: port_totals[p], reverse=True)

        header = "| Protocol | " + " | ".join(sorted_ports) + " | Total |"
        separator = "|:---| " + " | ".join([":---:" for _ in sorted_ports]) + " |:---:|"
        table_rows = [header, separator]
        for proto in sorted_protocols:
            row = [f"| {proto.capitalize()}"]
            for port in sorted_ports:
                row.append(str(len(detailed_stats.get(proto, {}).get(port, []))))
            row.append(f"**{protocol_totals[proto]}**")
            table_rows.append(" | ".join(row) + " |")
        footer = ["| **Total**", *[f"**{port_totals[port]}**" for port in sorted_ports], f"**{sum(port_totals.values())}**"]
        table_rows.append(" | ".join(footer) + " |")
        stats_table_string = "\n".join(table_rows)

        protocol_links_string = "\n".join([f"- **{proto.capitalize()}:**\n  ```\n  [https://raw.githubusercontent.com/](https://raw.githubusercontent.com/){GITHUB_REPO}/main/sub/protocols/{proto}.txt\n  ```" for proto in sorted_protocols])
        port_links_string = "\n".join([f"- **Port {port}:**\n  ```\n  [https://raw.githubusercontent.com/](https://raw.githubusercontent.com/){GITHUB_REPO}/main/sub/{port}.txt\n  ```" for port in sorted_ports])

        # --- Generate Two-Column Source Statistics Table ---
        summary_lines = [
            f"**Total Fetched (Raw):** {stats['raw_total']}",
            f"**Duplicates Removed:** {stats['duplicates_removed']}"
        ]
        details_lines = [f"**{name}:** {count}" for name, count in stats['source_stats'].items()]
        
        source_table_rows = ["| Summary | Source Details |", "|:---|:---|"]
        max_len = max(len(summary_lines), len(details_lines))
        for i in range(max_len):
            left_col = summary_lines[i] if i < len(summary_lines) else ""
            right_col = details_lines[i] if i < len(details_lines) else ""
            source_table_rows.append(f"| {left_col} | {right_col} |")
        source_stats_string = "\n".join(source_table_rows)
        # --- End of New Table Logic ---

        new_readme_content = template_content.replace('<!-- UPDATE_TIME -->', stats['update_time'])
        new_readme_content = new_readme_content.replace('<!-- TOTAL_CONFIGS -->', str(stats['total_configs']))
        new_readme_content = re.sub(r'(<!-- STATS_TABLE_START -->)(.|\n)*?(<!-- STATS_TABLE_END -->)', f'\\1\n{stats_table_string}\n\\3', new_readme_content)
        new_readme_content = re.sub(r'(<!-- PROTOCOL_LINKS_START -->)(.|\n)*?(<!-- PROTOCOL_LINKS_END -->)', f'\\1\n{protocol_links_string}\n\\3', new_readme_content)
        new_readme_content = re.sub(r'(<!-- PORT_LINKS_START -->)(.|\n)*?(<!-- PORT_LINKS_END -->)', f'\\1\n{port_links_string}\n\\3', new_readme_content)
        new_readme_content = re.sub(r'(<!-- SOURCE_STATS_START -->)(.|\n)*?(<!-- SOURCE_STATS_END -->)', f'\\1\n{source_stats_string}\n\\3', new_readme_content)
        
        with open('README.md', 'w', encoding='utf-8') as f: f.write(new_readme_content)
        print("✅ README.md updated successfully with two-column source stats.")

    except FileNotFoundError:
        print("\n❌ Error: README.template.md not found!")
    except Exception as e:
        print(f"\n❌ An error occurred while updating README.md: {e}")

def main():
    unique_configs, source_stats, raw_total = fetch_all_configs(SOURCES)
    if not unique_configs:
        print("\nNo configs found. Exiting.")
        return

    categorized_by_protocol_and_port = defaultdict(lambda: defaultdict(list))
    for config_link in unique_configs:
        protocol, port = get_config_info(config_link)
        if protocol and port:
            categorized_by_protocol_and_port[protocol][port].append(config_link)

    # ... (Writing files part remains unchanged) ...
    print("\nWriting all subscription files...")
    os.makedirs('sub/protocols', exist_ok=True)
    with open('sub/all.txt', 'w', encoding='utf-8') as f: f.write('\n'.join(unique_configs))
    for protocol, ports_data in categorized_by_protocol_and_port.items():
        all_protocol_configs = [cfg for cfgs in ports_data.values() for cfg in cfgs]
        with open(f'sub/protocols/{protocol}.txt', 'w', encoding='utf-8') as f: f.write('\n'.join(all_protocol_configs))
    for port in FAMOUS_PORTS:
        port_configs = [cfg for p_data in categorized_by_protocol_and_port.values() for p, cfgs in p_data.items() if p == port for cfg in cfgs]
        if port_configs:
            with open(f'sub/{port}.txt', 'w', encoding='utf-8') as f: f.write('\n'.join(port_configs))
    detailed_folder = 'detailed'
    os.makedirs(detailed_folder, exist_ok=True)
    for protocol, ports_data in categorized_by_protocol_and_port.items():
        protocol_folder = os.path.join(detailed_folder, protocol)
        os.makedirs(protocol_folder, exist_ok=True)
        other_ports_folder = os.path.join(protocol_folder, 'other_ports')
        has_other_ports = False
        for port, configs in ports_data.items():
            file_path = os.path.join(protocol_folder, f'{port}.txt') if port in FAMOUS_PORTS else os.path.join(other_ports_folder, f'{port}.txt')
            if port not in FAMOUS_PORTS and not has_other_ports:
                os.makedirs(other_ports_folder, exist_ok=True)
                has_other_ports = True
            with open(file_path, 'w', encoding='utf-8') as f: f.write('\n'.join(configs))
    print("✅ All subscription files written successfully.")

    stats = {
        "total_configs": len(unique_configs),
        "raw_total": raw_total,
        "duplicates_removed": raw_total - len(unique_configs),
        "update_time": get_tehran_time(),
        "source_stats": source_stats,
        "detailed_stats": categorized_by_protocol_and_port
    }
    update_readme(stats)
    
    print("\n🎉 Project update finished successfully.")

if __name__ == "__main__":
    main()
