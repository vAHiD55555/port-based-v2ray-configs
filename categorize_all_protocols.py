import requests
import base64
import json
import os
from collections import defaultdict
from urllib.parse import urlparse

# === منابع تجمعی (حاوی تمام پروتکل‌ها) ===
SOURCES = [
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/yebekhe/V2Hub/main/merged",
    "https://raw.githubusercontent.com/ALIILAPRO/v2ray-configs/main/all.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/export/all"
]

# پورت‌های معروف برای دسته‌بندی جداگانه
FAMOUS_PORTS = {'80', '443', '8080'}

def fetch_all_configs(source_urls):
    """تمام کانفیگ‌ها را از لیست منابع دریافت می‌کند."""
    all_configs = []
    print("شروع دریافت کانفیگ از منابع تجمعی...")
    for i, url in enumerate(source_urls):
        try:
            print(f"--> در حال تلاش برای دریافت از منبع شماره {i+1}...")
            response = requests.get(url, timeout=45)
            if response.status_code == 200 and response.text:
                configs = response.text.strip().split('\n')
                valid_configs = [line for line in configs if line.strip() and '://' in line]
                if valid_configs:
                    all_configs.extend(valid_configs)
                    print(f"✅ {len(valid_configs)} کانفیگ معتبر از {url} دریافت شد.")
        except requests.RequestException as e:
            print(f"❌ خطا در اتصال به {url}: {e}")
    return list(set(all_configs))

def get_config_info(link):
    """
    لینک کانفیگ را تحلیل کرده و یک تاپل (پروتکل، پورت) را برمی‌گرداند.
    """
    try:
        protocol = link.split("://")[0]

        if protocol in ["vless", "trojan", "tuic", "hysteria2", "hy2"]:
            parsed_url = urlparse(link)
            port = str(parsed_url.port) if parsed_url.port else None
            return protocol, port

        elif protocol == "vmess":
            b64_part = link.replace("vmess://", "")
            b64_part += '=' * (-len(b64_part) % 4)
            decoded_json = base64.b64decode(b64_part).decode('utf-8')
            port = str(json.loads(decoded_json).get('port'))
            return "vmess", port
        
        elif protocol == "ss":
            link_main_part = link.split('#')[0]
            if '@' in link_main_part:
                parsed_url = urlparse(link_main_part)
                port = str(parsed_url.port)
            else:
                b64_part = link_main_part.replace("ss://", "")
                b64_part += '=' * (-len(b64_part) % 4)
                decoded_str = base64.b64decode(b64_part).decode('utf-8')
                port = str(decoded_str.split('@')[1].split(':')[-1])
            return "shadowsocks", port
                
    except Exception:
        return None, None
    return None, None

def main():
    raw_configs = fetch_all_configs(SOURCES)
    if not raw_configs:
        print("هیچ کانفیگی برای پردازش یافت نشد.")
        return

    print(f"\nتعداد کل کانفیگ‌های منحصر به فرد: {len(raw_configs)}")
    print("شروع پردازش و دسته‌بندی دوگانه (بر اساس پورت و پروتکل)...")

    # <<< تغییر جدید: ایجاد دو دیکشنری برای دسته‌بندی دوگانه >>>
    categorized_by_port = defaultdict(list)
    categorized_by_protocol = defaultdict(list)

    for config_link in raw_configs:
        protocol, port = get_config_info(config_link)
        if port: # فقط کانفیگ‌هایی که پورت معتبر دارند را پردازش می‌کنیم
            categorized_by_port[port].append(config_link)
        if protocol:
            categorized_by_protocol[protocol].append(config_link)

    # --- بخش ۱: نوشتن فایل‌ها بر اساس پورت (مانند قبل) ---
    if categorized_by_port:
        print(f"\n✅ پردازش بر اساس پورت موفق بود. {len(categorized_by_port)} پورت منحصر به فرد پیدا شد.")
        os.makedirs('ports/other', exist_ok=True)
        os.makedirs('sub/other', exist_ok=True)
        
        famous_ports_count = 0
        other_ports_count = 0
        for port, configs in categorized_by_port.items():
            content = "\n".join(configs)
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            if port in FAMOUS_PORTS:
                raw_path, sub_path = f"ports/{port}.txt", f"sub/{port}.txt"
                famous_ports_count += 1
            else:
                raw_path, sub_path = f"ports/other/{port}.txt", f"sub/other/{port}.txt"
                other_ports_count += 1
                
            with open(raw_path, 'w', encoding='utf-8') as f: f.write(content)
            with open(sub_path, 'w', encoding='utf-8') as f: f.write(encoded_content)
        
        print(f"✅ {famous_ports_count} فایل برای پورت‌های معروف ساخته شد.")
        print(f"✅ {other_ports_count} فایل برای سایر پورت‌ها ساخته شد.")
    else:
        print("\n❌ هیچ پورتی برای دسته‌بندی پیدا نشد.")

    # <<< تغییر جدید: بخش ۲: نوشتن فایل‌ها بر اساس پروتکل >>>
    if categorized_by_protocol:
        print(f"\n✅ پردازش بر اساس پروتکل موفق بود. {len(categorized_by_protocol)} پروتکل منحصر به فرد پیدا شد.")
        os.makedirs('ports/protocols', exist_ok=True)
        os.makedirs('sub/protocols', exist_ok=True)

        for protocol, configs in categorized_by_protocol.items():
            content = "\n".join(configs)
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

            with open(f"ports/protocols/{protocol}.txt", 'w', encoding='utf-8') as f: f.write(content)
            with open(f"sub/protocols/{protocol}.txt", 'w', encoding='utf-8') as f: f.write(encoded_content)

        print(f"✅ {len(categorized_by_protocol)} فایل دسته‌بندی شده بر اساس پروتکل ساخته شد.")
    else:
        print("\n❌ هیچ پروتکلی برای دسته‌بندی پیدا نشد.")
        
    # ذخیره فایل کلی در انتها
    with open('All-Configs.txt', 'w', encoding='utf-8') as f: f.write("\n".join(raw_configs))
    with open('sub/all.txt', 'w', encoding='utf-8') as f: f.write(base64.b64encode("\n".join(raw_configs).encode('utf-8')).decode('utf-8'))
    print("\n✅ فایل کلی 'All-Configs.txt' و لینک اشتراک آن ساخته شد.")
    
    print("\n🎉 پروژه با موفقیت به پایان رسید.")

if __name__ == "__main__":
    main()
