import requests
import base64
import json
import os
from collections import defaultdict
from urllib.parse import urlparse, unquote

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
                else:
                    print(f"⚠️ منبع {url} محتوای معتبری نداشت.")
            else:
                 print(f"❌ منبع {url} در دسترس نبود یا خالی بود. Status Code: {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ خطا در اتصال به {url}: {e}")
    return list(set(all_configs))

def get_port_from_link(link):
    """
    لینک کانفیگ را تحلیل کرده و پورت آن را برمی‌گرداند.
    از پروتکل‌های Vmess, Vless, Trojan, SS, Hysteria2, TUIC پشتیبانی می‌کند.
    """
    try:
        # پروتکل‌های مبتنی بر ساختار URL
        if link.startswith(("vless://", "trojan://", "tuic://", "hysteria2://", "hy2://")):
            parsed_url = urlparse(link)
            return str(parsed_url.port) if parsed_url.port else None

        # پروتکل Vmess با ساختار Base64
        elif link.startswith("vmess://"):
            b64_part = link.replace("vmess://", "")
            b64_part += '=' * (-len(b64_part) % 4)
            decoded_json = base64.b64decode(b64_part).decode('utf-8')
            port = json.loads(decoded_json).get('port')
            return str(port) if port else None
        
        # پروتکل ShadowSocks با دو ساختار ممکن
        elif link.startswith("ss://"):
            link_main_part = link.split('#')[0]
            if '@' in link_main_part: # ساختار URL-like
                parsed_url = urlparse(link_main_part)
                return str(parsed_url.port)
            else: # ساختار Base64
                b64_part = link_main_part.replace("ss://", "")
                b64_part += '=' * (-len(b64_part) % 4)
                decoded_str = base64.b64decode(b64_part).decode('utf-8')
                host_port_part = decoded_str.split('@')[1]
                port = host_port_part.split(':')[-1]
                return str(port)
                
    except Exception:
        # اگر تحلیل هر لینکی با خطا مواجه شد، آن را نادیده می‌گیریم
        return None
    return None

def main():
    raw_configs = fetch_all_configs(SOURCES)
    if not raw_configs:
        print("هیچ کانفیگی برای پردازش یافت نشد. کار متوقف شد.")
        return

    print(f"\nتعداد کل کانفیگ‌های منحصر به فرد: {len(raw_configs)}")
    print("شروع پردازش و دسته‌بندی برای تمام پروتکل‌های پشتیبانی شده...")

    categorized_by_port = defaultdict(list)
    for config_link in raw_configs:
        port = get_port_from_link(config_link)
        if port:
            categorized_by_port[port].append(config_link)

    if not categorized_by_port:
        print("\n❌ با وجود دانلود کانفیگ‌ها، هیچکدام قابل تحلیل نبودند.")
        return

    print(f"\n✅ پردازش موفق بود. {len(categorized_by_port)} پورت منحصر به فرد پیدا شد.")
    
    os.makedirs('ports/other', exist_ok=True)
    os.makedirs('sub/other', exist_ok=True)
    
    # ذخیره فایل کلی
    with open('All-Configs.txt', 'w', encoding='utf-8') as f: f.write("\n".join(raw_configs))
    with open('sub/all.txt', 'w', encoding='utf-8') as f: f.write(base64.b64encode("\n".join(raw_configs).encode('utf-8')).decode('utf-8'))
    print("✅ فایل کلی 'All-Configs.txt' و لینک اشتراک آن ساخته شد.")

    # منطق دسته‌بندی فایل‌ها
    famous_ports_count = 0
    other_ports_count = 0
    for port, configs in categorized_by_port.items():
        content = "\n".join(configs)
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        if port in FAMOUS_PORTS:
            raw_path = f"ports/{port}.txt"
            sub_path = f"sub/{port}.txt"
            famous_ports_count += 1
        else:
            raw_path = f"ports/other/{port}.txt"
            sub_path = f"sub/other/{port}.txt"
            other_ports_count += 1
            
        with open(raw_path, 'w', encoding='utf-8') as f: f.write(content)
        with open(sub_path, 'w', encoding='utf-8') as f: f.write(encoded_content)
    
    print(f"✅ {famous_ports_count} فایل برای پورت‌های معروف ساخته شد.")
    print(f"✅ {other_ports_count} فایل برای سایر پورت‌ها در پوشه 'other' ساخته شد.")
    print("\n🎉 پروژه با موفقیت به پایان رسید.")

if __name__ == "__main__":
    main()
