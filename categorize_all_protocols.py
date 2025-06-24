import requests
import base64
import json
import os
import re
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta, timezone

# === منابع نهایی کانفیگ ===
SOURCES = {
    "barry-far": "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "mahdibland": "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "Epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "soroushmirzaei": "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/mixed"
}

# === پارامترهای دسته‌بندی ===
FAMOUS_PORTS = {'80', '443', '8080', '8088', '2052', '2053', '2082', '2083', '2086', '2087', '2095', '2096'}

def fetch_all_configs(sources_dict):
    """
    کانفیگ‌ها را از تمام منابع تعریف شده دریافت کرده و یک لیست واحد برمی‌گرداند.
    """
    all_configs = []
    source_stats = defaultdict(int)
    print("شروع دریافت کانفیگ از منابع...")
    for name, url in sources_dict.items():
        try:
            print(f"--> در حال دریافت از منبع: {name}...")
            response = requests.get(url, timeout=120)
            if response.status_code == 200 and response.text:
                content = response.text.strip()
                try:
                    if len(content) > 1000 and "://" not in content:
                        decoded_content = base64.b64decode(content).decode('utf-8')
                        configs = decoded_content.strip().split('\n')
                    else:
                        configs = content.split('\n')
                    
                    valid_configs = [line.strip() for line in configs if line.strip() and '://' in line]
                    if valid_configs:
                        all_configs.extend(valid_configs)
                        source_stats[name] = len(valid_configs)
                        print(f"  ✅ {len(valid_configs)} کانفیگ معتبر از {name} اضافه شد.")
                except Exception as e:
                    print(f"  ⚠️ خطا در پردازش محتوای منبع {name}: {e}")
        except requests.RequestException as e:
            print(f"❌ خطا در اتصال به منبع {name}: {e}")
    
    unique_configs = list(set(all_configs))
    print(f"\nتعداد کل کانفیگ‌های منحصر به فرد: {len(unique_configs)}")
    return unique_configs, source_stats

def get_config_info(link):
    """
    یک لینک کانفیگ دریافت کرده و پروتکل و پورت آن را استخراج می‌کند.
    """
    try:
        protocol = link.split("://")[0].lower()
        port = None
        
        if protocol == "vless":
            parsed_url = urlparse(link)
            port = str(parsed_url.port)
        elif protocol in ["trojan", "tuic", "hysteria2", "hy2"]:
            protocol = "hysteria2" if protocol in ["hy2", "hysteria2"] else protocol
            parsed_url = urlparse(link)
            port = str(parsed_url.port)
        elif protocol == "vmess":
            b64_part = link.replace("vmess://", "")
            b64_part += '=' * (-len(b64_part) % 4)
            decoded_json_str = base64.b64decode(b64_part).decode('utf-8')
            config_json = json.loads(decoded_json_str)
            port = str(config_json.get('port'))
        elif protocol == "ss":
            protocol = "shadowsocks"
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
            return None, None

        return (protocol, port if (port and port.isdigit()) else None)
    except Exception:
        return None, None

def get_tehran_time():
    """
    زمان فعلی به وقت تهران را برمی‌گرداند.
    """
    tehran_tz = timezone(timedelta(hours=3, minutes=30))
    now_tehran = datetime.now(timezone.utc).astimezone(tehran_tz)
    return now_tehran.strftime("%Y-%m-%d %H:%M:%S Tehran Time")

def update_readme(stats):
    """
    فایل README.md را با استفاده از آمار جدید و یک جدول Markdown به‌روزرسانی می‌کند.
    """
    try:
        print("\nشروع به‌روزرسانی فایل README.md...")
        with open('README.template.md', 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # --- Start: Generate Markdown Table ---
        detailed_stats = stats.get('detailed_stats', {})
        all_protocols = sorted(detailed_stats.keys())
        # Sort famous ports numerically for a clean look
        famous_ports_sorted = sorted(list(FAMOUS_PORTS), key=int)

        header = "| Protocol | " + " | ".join(famous_ports_sorted) + " | Total |"
        separator = "|:---| " + " | ".join([":---:" for _ in famous_ports_sorted]) + " |:---:|"
        
        table_rows = [header, separator]
        port_totals = {port: 0 for port in famous_ports_sorted}
        
        for proto in all_protocols:
            row_total = 0
            # Start row with capitalized protocol name
            row = [f"| {proto.capitalize()}"]
            for port in famous_ports_sorted:
                count = len(detailed_stats.get(proto, {}).get(port, []))
                row.append(str(count))
                row_total += count
                port_totals[port] += count
            
            # Add total for the protocol row
            row.append(f"**{sum(len(c) for c in detailed_stats.get(proto, {}).values())}**")
            table_rows.append(" | ".join(row) + " |")

        # Footer Row (Totals for each port)
        footer = ["| **Total**"]
        for port in famous_ports_sorted:
            footer.append(f"**{port_totals[port]}**")
        
        # Grand total for the footer
        grand_total = sum(port_totals.values())
        footer.append(f"**{grand_total}**")
        table_rows.append(" | ".join(footer) + " |")

        table_string = "\n".join(table_rows)
        # --- End: Generate Markdown Table ---

        # Replace placeholders in the template
        new_readme_content = template_content.replace('<!-- UPDATE_TIME -->', stats['update_time'])
        new_readme_content = new_readme_content.replace('<!-- TOTAL_CONFIGS -->', str(stats['total_configs']))
        new_readme_content = re.sub(r'(<!-- STATS_TABLE_START -->)(.|\n)*?(<!-- STATS_TABLE_END -->)', f'\\1\n{table_string}\n\\3', new_readme_content)

        # Replace source stats (as before)
        source_stats_lines = []
        for name, count in stats['source_stats'].items():
            source_stats_lines.append(f"- **{name}:** {count} کانفیگ")
        source_stats_block = "\n".join(source_stats_lines)
        new_readme_content = re.sub(r'(<!-- SOURCE_STATS_START -->)(.|\n)*?(<!-- SOURCE_STATS_END -->)', f'\\1\n{source_stats_block}\n\\3', new_readme_content)
        
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(new_readme_content)
        print("✅ فایل README.md با جدول آمار جدید با موفقیت بازنویسی شد.")

    except FileNotFoundError:
        print("\n❌ خطا: فایل README.template.md پیدا نشد! لطفاً از وجود این فایل در پروژه اطمینان حاصل کنید.")
    except Exception as e:
        print(f"\n❌ خطا در به‌روزرسانی README.md: {e}")


def main():
    # مرحله ۱: دریافت تمام کانفیگ‌ها
    raw_configs, source_stats = fetch_all_configs(SOURCES)
    if not raw_configs:
        print("\nهیچ کانفیگی برای پردازش یافت نشد. پایان کار.")
        return

    # مرحله ۲: دسته‌بندی کانفیگ‌ها
    print("\nشروع دسته‌بندی کانفیگ‌ها...")
    categorized_by_protocol_and_port = defaultdict(lambda: defaultdict(list))

    for config_link in raw_configs:
        protocol, port = get_config_info(config_link)
        if protocol and port:
            categorized_by_protocol_and_port[protocol][port].append(config_link)

    print("✅ دسته‌بندی با موفقیت انجام شد.")
    
    # مرحله ۳: نوشتن فایل‌های دسته‌بندی شده
    print("\nشروع نوشتن فایل‌های دسته‌بندی شده...")
    # ساخت تمام پوشه‌ها و فایل‌های لازم...
    # (این بخش بدون تغییر باقی می‌ماند)
    os.makedirs('sub/protocols', exist_ok=True)
    with open('sub/all.txt', 'w', encoding='utf-8') as f: f.write('\n'.join(raw_configs))
    for protocol, ports_data in categorized_by_protocol_and_port.items():
        with open(f'sub/protocols/{protocol}.txt', 'w', encoding='utf-8') as f:
            all_protocol_configs = [cfg for cfgs in ports_data.values() for cfg in cfgs]
            f.write('\n'.join(all_protocol_configs))
    for port in FAMOUS_PORTS:
        port_configs = [cfg for proto_data in categorized_by_protocol_and_port.values() for p, cfgs in proto_data.items() if p == port for cfg in cfgs]
        if port_configs:
            with open(f'sub/{port}.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(port_configs))

    # مرحله ۴: نوشتن فایل‌های دسته‌بندی شده با جزئیات
    detailed_folder = 'detailed'
    os.makedirs(detailed_folder, exist_ok=True)
    for protocol, ports_data in categorized_by_protocol_and_port.items():
        protocol_folder = os.path.join(detailed_folder, protocol)
        os.makedirs(protocol_folder, exist_ok=True)
        other_ports_folder = os.path.join(protocol_folder, 'other_ports')
        has_other_ports = False
        for port, configs in ports_data.items():
            if port in FAMOUS_PORTS:
                file_path = os.path.join(protocol_folder, f'{port}.txt')
            else:
                if not has_other_ports:
                    os.makedirs(other_ports_folder, exist_ok=True)
                    has_other_ports = True
                file_path = os.path.join(other_ports_folder, f'{port}.txt')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(configs))
    print("✅ تمام فایل‌های دسته‌بندی شده با موفقیت ایجاد شدند.")

    # مرحله ۵: جمع‌آوری آمار و به‌روزرسانی README
    stats = {
        "total_configs": len(raw_configs),
        "update_time": get_tehran_time(),
        "source_stats": source_stats,
        "detailed_stats": categorized_by_protocol_and_port # << مهم: ارسال داده‌های دقیق به تابع آپدیت
    }
    update_readme(stats)
    
    print("\n🎉 پروژه با موفقیت به پایان رسید.")

if __name__ == "__main__":
    main()
