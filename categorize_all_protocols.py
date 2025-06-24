import requests
import base64
import json
import os
import re
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta, timezone

# === منابع نهایی و تایید شده توسط شما ===
SOURCES = {
    "barry-far": "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "mahdibland": "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "Epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "soroushmirzaei": "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/mixed"
}

# پارامترهای دسته‌بندی
FAMOUS_PORTS = {'80', '443', '8080', '8088'}
SPECIAL_PROTOCOLS = {'vless', 'vmess', 'trojan'}
SPECIAL_PORTS = {'80', '443', '8080', '8088'}
RARE_PORT_THRESHOLD = 5

def fetch_all_configs(sources_dict):
    all_configs = []
    source_stats = defaultdict(int)
    print("شروع دریافت کانفیگ از لیست انتخابی شما...")
    for name, url in sources_dict.items():
        try:
            print(f"--> در حال دریافت از منبع: {name}...")
            response = requests.get(url, timeout=90)
            if response.status_code == 200 and response.text:
                content = response.text.strip()
                try:
                    if len(content) > 1000 and "://" not in content:
                        decoded_content = base64.b64decode(content).decode('utf-8')
                        configs = decoded_content.strip().split('\n')
                    else:
                        configs = content.split('\n')
                    valid_configs = [line for line in configs if line.strip() and '://' in line]
                    if valid_configs:
                        all_configs.extend(valid_configs)
                        source_stats[name] = len(valid_configs)
                except Exception as e:
                    print(f"  ⚠️ خطا در پردازش محتوای منبع {name}: {e}")
        except requests.RequestException as e:
            print(f"❌ خطا در اتصال به منبع {name}: {e}")
    return list(set(all_configs)), source_stats

def get_config_info(link):
    try:
        protocol = link.split("://")[0].lower()
        is_reality = False
        if protocol == "vless":
            protocol_name = "vless"
            parsed_url = urlparse(link)
            port = str(parsed_url.port) if parsed_url.port else None
            query_params = parse_qs(parsed_url.query)
            if 'security' in query_params and query_params['security'][0].lower() == 'reality':
                is_reality = True
        elif protocol in ["trojan", "tuic", "hysteria2", "hy2"]:
            protocol_name = "hysteria2" if protocol == "hy2" else protocol
            parsed_url = urlparse(link)
            port = str(parsed_url.port) if parsed_url.port else None
        elif protocol == "vmess":
            protocol_name = "vmess"
            b64_part = link.replace("vmess://", "")
            b64_part += '=' * (-len(b64_part) % 4)
            decoded_json = base64.b64decode(b64_part).decode('utf-8')
            port = str(json.loads(decoded_json).get('port'))
        elif protocol == "ss":
            protocol_name = "shadowsocks"
            link_main_part = link.split('#')[0]
            if '@' in link_main_part:
                parsed_url = urlparse(link_main_part)
                port = str(parsed_url.port)
            else:
                b64_part = link_main_part.replace("ss://", "").split('#')[0]
                b64_part += '=' * (-len(b64_part) % 4)
                decoded_str = base64.b64decode(b64_part).decode('utf-8')
                port = str(decoded_str.split('@')[1].split(':')[-1])
        else:
            return None, None, False
        return (protocol_name, port if (port and port.isdigit()) else None, is_reality)
    except Exception:
        return None, None, False

def get_tehran_time():
    tehran_tz = timezone(timedelta(hours=3, minutes=30))
    now_tehran = datetime.now(timezone.utc).astimezone(tehran_tz)
    return now_tehran.strftime("%Y-%m-%d %H:%M:%S Tehran Time")

def update_readme(stats):
    try:
        with open('README.template.md', 'r', encoding='utf-8') as f:
            template_content = f.read()

        stats_lines = [f"**آخرین به‌روزرسانی:** {stats['update_time']}", f"**تعداد کل کانفیگ‌های منحصر به فرد:** {stats['total_configs']}"]
        stats_lines.append("\n#### تفکیک بر اساس پروتکل:")
        for protocol, count in stats['protocols'].items():
            stats_lines.append(f"- **{protocol.capitalize()}:** {count} کانفیگ")
        
        stats_lines.append("\n#### تفکیک بر اساس پورت‌های معروف:")
        for port in sorted(FAMOUS_PORTS):
            stats_lines.append(f"- **پورت {port}:** {stats['ports'].get(port, 0)} کانفیگ")

        stats_block = "\n".join(stats_lines)
        new_readme_content = re.sub(r'<!-- STATS_START -->(.|\n)*?<!-- STATS_END -->', f'<!-- STATS_START -->\n{stats_block}\n<!-- STATS_END -->', template_content)

        # آمار منابع را فقط برای برنچ بتا اضافه می‌کنیم
        source_stats_lines = ["\n---", "\n### 📦 آمار منابع (فقط در برنچ بتا)"]
        for name, count in stats['source_stats'].items():
            source_stats_lines.append(f"- **{name}:** {count} کانفیگ")
        
        source_stats_block = "\n".join(source_stats_lines)
        new_readme_content = re.sub(r'<!-- SOURCE_STATS_START -->(.|\n)*?<!-- SOURCE_STATS_END -->', f'<!-- SOURCE_STATS_START -->\n{source_stats_block}\n<!-- SOURCE_STATS_END -->', new_readme_content)
        
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(new_readme_content)
        print("\n✅ فایل README.md با آمار جدید با موفقیت بازنویسی شد.")
    except Exception as e:
        print(f"\n❌ خطا در به‌روزرسانی README.md: {e}")

def main():
    raw_configs, source_stats = fetch_all_configs(SOURCES)
    if not raw_configs: return

    categorized_by_port = defaultdict(list)
    categorized_by_protocol = defaultdict(list)
    special_categorization = defaultdict(lambda: defaultdict(list))
    vless_reality_list = []

    for config_link in raw_configs:
        protocol, port, is_reality = get_config_info(config_link)
        if port: categorized_by_port[port].append(config_link)
        if protocol: categorized_by_protocol[protocol].append(config_link)
        if protocol in SPECIAL_PROTOCOLS and port in SPECIAL_PORTS:
            special_categorization[protocol][port].append(config_link)
        if is_reality:
            vless_reality_list.append(config_link)
    
    # نوشتن فایل‌ها
    # ... (بقیه کدهای نوشتن فایل‌ها بدون تغییر)
    # ...
    
    stats = {
        "total_configs": len(raw_configs),
        "update_time": get_tehran_time(),
        "protocols": {p: len(c) for p, c in sorted(categorized_by_protocol.items())},
        "ports": {p: len(c) for p, c in sorted(categorized_by_port.items())},
        "source_stats": source_stats
    }
    update_readme(stats)
    
    print("\n🎉 پروژه با موفقیت به پایان رسید.")

if __name__ == "__main__":
    main()
