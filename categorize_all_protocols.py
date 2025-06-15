import requests
import base64
import json
import os
from collections import defaultdict
from urllib.parse import urlparse

# === منابع نهایی و تایید شده توسط شما (با اصلاح لینک) ===
SOURCES = [
    # لینک اصلاح شده - باید از raw.githubusercontent.com استفاده شود
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/mixed"
]

# پورت‌های معروف برای دسته‌بندی جداگانه
FAMOUS_PORTS = {'80', '443', '8080'}

def fetch_all_configs(source_urls):
    """
    تمام کانفیگ‌ها را از منابع مختلف دریافت می‌کند.
    به طور هوشمند لینک اشتراک (Base64) و لیست خام را تشخیص می‌دهد.
    """
    all_configs = []
    print("شروع دریافت کانفیگ از لیست انتخابی شما...")
    for i, url in enumerate(source_urls):
        try:
            print(f"--> در حال دریافت از منبع شماره {i+1}...")
            response = requests.get(url, timeout=90)
            if response.status_code == 200 and response.text:
                content = response.text.strip()
                try:
                    # تلاش برای دیکود کردن به عنوان Base64
                    if len(content) > 1000 and "://" not in content:
                        decoded_content = base64.b64decode(content).decode('utf-8')
                        configs = decoded_content.strip().split('\n')
                        print(f"✅ منبع شماره {i+1} به عنوان لینک اشتراک (Base64) پردازش شد.")
                    else:
                        # در غیر این صورت، به عنوان لیست خام در نظر بگیر
                        configs = content.split('\n')
                        print(f"✅ منبع شماره {i+1} به عنوان لیست خام پردازش شد.")
                    
                    valid_configs = [line for line in configs if line.strip() and '://' in line]
                    if valid_configs:
                        all_configs.extend(valid_configs)
                        print(f"  -> {len(valid_configs)} کانفیگ معتبر اضافه شد.")
                except Exception as e:
                    print(f"  ⚠️ خطا در پردازش محتوای منبع شماره {i+1}: {e}")

        except requests.RequestException as e:
            print(f"❌ خطا در اتصال به منبع شماره {i+1}: {e}")
            
    # حذف موارد تکراری در انتهای کار
    return list(set(all_configs))


def get_config_info(link):
    """لینک کانفیگ را تحلیل کرده و یک تاپل (پروتکل، پورت) را برمی‌گرداند."""
    try:
        protocol = link.split("://")[0].lower()
        protocol_name = None

        if protocol in ["vless", "trojan", "tuic", "hysteria2", "hy2"]:
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
                b64_part = link_main_part.replace("ss://", "")
                b64_part += '=' * (-len(b64_part) % 4)
                decoded_str = base64.b64decode(b64_part).decode('utf-8')
                port = str(decoded_str.split('@')[1].split(':')[-1])
        
        else:
            return None, None

        return (protocol_name, port) if (port and port.isdigit()) else (protocol_name, None)

    except Exception:
        return None, None

def main():
    raw_configs = fetch_all_configs(SOURCES)
    if not raw_configs:
        print("هیچ کانفیگی برای پردازش یافت نشد.")
        return

    print(f"\nتعداد کل کانفیگ‌های منحصر به فرد: {len(raw_configs)}")
    print("شروع پردازش و دسته‌بندی نهایی...")

    categorized_by_port = defaultdict(list)
    categorized_by_protocol = defaultdict(list)

    for config_link in raw_configs:
        protocol, port = get_config_info(config_link)
        if port: categorized_by_port[port].append(config_link)
        if protocol: categorized_by_protocol[protocol].append(config_link)

    # نوشتن فایل‌ها بر اساس پورت
    if categorized_by_port:
        print(f"\n✅ پردازش بر اساس پورت: {len(categorized_by_port)} پورت منحصر به فرد پیدا شد.")
        os.makedirs('ports/other', exist_ok=True); os.makedirs('sub/other', exist_ok=True)
        for port, configs in categorized_by_port.items():
            path_prefix = "" if port in FAMOUS_PORTS else "other/"
            with open(f"ports/{path_prefix}{port}.txt", 'w', encoding='utf-8') as f: f.write("\n".join(configs))
            with open(f"sub/{path_prefix}{port}.txt", 'w', encoding='utf-8') as f: f.write(base64.b64encode("\n".join(configs).encode('utf-8')).decode('utf-8'))

    # نوشتن فایل‌ها بر اساس پروتکل
    if categorized_by_protocol:
        print(f"\n✅ پردازش بر اساس پروتکل: {len(categorized_by_protocol)} پروتکل منحصر به فرد پیدا شد.")
        os.makedirs('ports/protocols', exist_ok=True); os.makedirs('sub/protocols', exist_ok=True)
        for protocol, configs in categorized_by_protocol.items():
            with open(f"ports/protocols/{protocol}.txt", 'w', encoding='utf-8') as f: f.write("\n".join(configs))
            with open(f"sub/protocols/{protocol}.txt", 'w', encoding='utf-8') as f: f.write(base64.b64encode("\n".join(configs).encode('utf-8')).decode('utf-8'))
        
    # ذخیره فایل کلی
    with open('All-Configs.txt', 'w', encoding='utf-8') as f: f.write("\n".join(raw_configs))
    with open('sub/all.txt', 'w', encoding='utf-8') as f: f.write(base64.b64encode("\n".join(raw_configs).encode('utf-8')).decode('utf-8'))
    
    print("\n🎉 پروژه با موفقیت به پایان رسید.")

if __name__ == "__main__":
    main()
