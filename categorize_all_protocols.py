import requests
import base64
import json
import os
from collections import defaultdict
from urllib.parse import urlparse, unquote

# دیکشنری منابع
SOURCES = {
    "vmess": [
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vmess",
        "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_base64.txt"
    ],
    "vless": [
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vless"
    ],
    "trojan": [
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/trojan"
    ],
    "shadowsocks": [
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/ss"
    ]
}

def fetch_all_configs(sources_dict):
    """تمام کانفیگ‌ها را از منابع مختلف بر اساس پروتکل دریافت می‌کند."""
    all_configs = []
    print("شروع دریافت کانفیگ از منابع...")
    for protocol, urls in sources_dict.items():
        print(f"--- دریافت پروتکل: {protocol} ---")
        for url in urls:
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    configs = response.text.strip().split('\n')
                    configs = [line for line in configs if line.strip() and '://' in line]
                    all_configs.extend(configs)
                    print(f"✅ {len(configs)} کانفیگ از {url} دریافت شد.")
            except requests.RequestException as e:
                print(f"❌ خطا در دریافت از {url}: {e}")
    return list(set(all_configs))

def get_port_from_link(link):
    """
    لینک کانفیگ را تحلیل کرده و پورت آن را برمی‌گرداند.
    این نسخه شامل لاگ خطای دقیق است.
    """
    try:
        if link.startswith("vmess://"):
            b64_part = link.replace("vmess://", "")
            b64_part += '=' * (-len(b64_part) % 4)
            decoded_json = base64.b64decode(b64_part).decode('utf-8')
            port = json.loads(decoded_json).get('port')
            return str(port) if port else None

        elif link.startswith(("vless://", "trojan://")):
            parsed_url = urlparse(link)
            return str(parsed_url.port) if parsed_url.port else None

        elif link.startswith("ss://"):
            # بخش #fragment را جدا می‌کنیم چون می‌تواند حاوی کاراکترهای نامعتبر باشد
            link_main_part = link.split('#')[0]
            if '@' in link_main_part:
                # فرمت URL-like: ss://method:pass@host:port
                parsed_url = urlparse(link_main_part)
                return str(parsed_url.port)
            else:
                # فرمت Base64: ss://BASE64...
                b64_part = link_main_part.replace("ss://", "")
                b64_part += '=' * (-len(b64_part) % 4)
                decoded_str = base64.b64decode(b64_part).decode('utf-8')
                # فرمت دیکود شده: method:pass@host:port
                host_port_part = decoded_str.split('@')[1]
                port = host_port_part.split(':')[-1]
                return str(port)
    # <<< تغییر کلیدی: ثبت دقیق نوع خطا >>>
    except Exception as e:
        print(f"  [!] EXCEPTION while parsing link: {link[:70]}... | Error: {e}")
        return None
    return None

def main():
    raw_configs = fetch_all_configs(SOURCES)
    if not raw_configs:
        print("هیچ کانفیگی برای پردازش یافت نشد.")
        return

    print(f"\nتعداد کل کانفیگ‌های منحصر به فرد: {len(raw_configs)}")
    print("شروع پردازش و دسته‌بندی (نسخه عیب‌یابی دقیق)...")

    categorized_by_port = defaultdict(list)
    unparsed_configs = 0

    for config_link in raw_configs:
        port = get_port_from_link(config_link)
        if port:
            categorized_by_port[port].append(config_link)
        else:
            unparsed_configs += 1

    print("\n--- نتایج نهایی دیباگ ---")
    print(f"تعداد کل کانفیگ‌های موفق: {sum(len(v) for v in categorized_by_port.values())}")
    print(f"تعداد کانفیگ‌های ناموفق یا ناشناخته: {unparsed_configs}")
    print(f"تعداد کل پورت‌های منحصر به فرد پیدا شده: {len(categorized_by_port)}")

    if not categorized_by_port:
        print("\n❌ هشدار جدی: هیچ پورتی پیدا نشد! فایل‌های دسته‌بندی شده ساخته نمی‌شوند.")
        return

    # بقیه کد برای نوشتن فایل‌ها بدون تغییر باقی می‌ماند
    os.makedirs('ports', exist_ok=True)
    os.makedirs('sub', exist_ok=True)
    
    all_configs_content = "\n".join(raw_configs)
    with open('All-Configs.txt', 'w', encoding='utf-8') as f: f.write(all_configs_content)
    with open('sub/all.txt', 'w', encoding='utf-8') as f: f.write(base64.b64encode(all_configs_content.encode('utf-8')).decode('utf-8'))
    print("\n✅ فایل کلی 'All-Configs.txt' و لینک اشتراک آن ساخته شد.")

    for port, configs in categorized_by_port.items():
        content = "\n".join(configs)
        with open(f"ports/{port}.txt", 'w', encoding='utf-8') as f: f.write(content)
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        with open(f"sub/{port}.txt", 'w', encoding='utf-8') as f: f.write(encoded_content)
        print(f"✅ فایل برای پورت {port} با {len(configs)} کانفیگ ساخته شد.")

    print("\n🎉 پردازش با موفقیت به پایان رسید.")

if __name__ == "__main__":
    main()
