import requests
import base64
import json
import os
import re
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta, timezone

# === منابع نهایی و تایید شده توسط شما ===
SOURCES = [
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/mixed"
]

# پارامترهای دسته‌بندی
SPECIAL_PROTOCOLS = {'vless', 'vmess', 'trojan'}
SPECIAL_PORTS = {'80', '443', '8080', '8088'}
RARE_PORT_THRESHOLD = 5

def fetch_all_configs(source_urls):
    all_configs = []
    print("شروع دریافت کانفیگ از لیست انتخابی شما...")
    for i, url in enumerate(source_urls):
        try:
            print(f"--> در حال دریافت از منبع شماره {i+1}...")
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
                except Exception as e:
                    print(f"  ⚠️ خطا در پردازش محتوای منبع شماره {i+1}: {e}")
        except requests.RequestException as e:
            print(f"❌ خطا در اتصال به منبع شماره {i+1}: {e}")
    return list(set(all_configs))

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

def main():
    raw_configs = fetch_all_configs(SOURCES)
    if not raw_configs:
        print("هیچ کانفیگی برای پردازش یافت نشد.")
        return

    categorized_by_protocol = defaultdict(list)
    special_categorization = defaultdict(lambda: defaultdict(list))

    for config_link in raw_configs:
        protocol, port, is_reality = get_config_info(config_link)
        if protocol: 
            categorized_by_protocol[protocol].append(config_link)
        if protocol in SPECIAL_PROTOCOLS and port in SPECIAL_PORTS:
            special_categorization[protocol][port].append(config_link)
        if is_reality:
            special_categorization['reality']['all'].append(config_link)

    # نوشتن فایل‌های دسته‌بندی شده بر اساس پروتکل
    print("\n✅ شروع ساخت فایل‌های دسته‌بندی شده...")
    os.makedirs('protocols', exist_ok=True); os.makedirs('sub/protocols', exist_ok=True)
    for protocol, configs in categorized_by_protocol.items():
        with open(f"protocols/{protocol}.txt", 'w', encoding='utf-8') as f: f.write("\n".join(configs))
        with open(f"sub/protocols/{protocol}.txt", 'w', encoding='utf-8') as f: f.write(base64.b64encode("\n".join(configs).encode('utf-8')).decode('utf-8'))
    
    # نوشتن فایل‌های دسته‌بندی ویژه
    for protocol, ports_dict in special_categorization.items():
        if protocol == 'reality':
            os.makedirs(f'protocols/special', exist_ok=True); os.makedirs(f'sub/special', exist_ok=True)
            with open(f"protocols/special/reality.txt", 'w', encoding='utf-8') as f: f.write("\n".join(ports_dict['all']))
            with open(f"sub/special/reality.txt", 'w', encoding='utf-8') as f: f.write(base64.b64encode("\n".join(ports_dict['all']).encode('utf-8')).decode('utf-8'))
            print(f"  -> فایل ویژه برای REALITY با {len(ports_dict['all'])} کانفیگ ساخته شد.")
        else:
            os.makedirs(f'protocols/{protocol}', exist_ok=True); os.makedirs(f'sub/protocols/{protocol}', exist_ok=True)
            for port, configs in ports_dict.items():
                with open(f"protocols/{protocol}/{port}.txt", 'w', encoding='utf-8') as f: f.write("\n".join(configs))
                with open(f"sub/protocols/{protocol}/{port}.txt", 'w', encoding='utf-8') as f: f.write(base64.b64encode("\n".join(configs).encode('utf-8')).decode('utf-8'))
                print(f"  -> فایل ویژه برای {protocol.upper()} روی پورت {port} با {len(configs)} کانفیگ ساخته شد.")

    # ذخیره فایل کلی
    with open('All-Configs.txt', 'w', encoding='utf-8') as f: f.write("\n".join(raw_configs))
    with open('sub/all.txt', 'w', encoding='utf-8') as f: f.write(base64.b64encode("\n".join(raw_configs).encode('utf-8')).decode('utf-8'))
    
    print("\n🎉 پروژه با موفقیت به پایان رسید.")

if __name__ == "__main__":
    main()
