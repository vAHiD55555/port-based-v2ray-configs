import requests
import base64
import json
import os
from collections import defaultdict

# لیستی از بهترین منابع برای جمع‌آوری کانفیگ
SOURCES = [
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vmess",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_base64.txt",
    # در صورت تمایل می‌توانید منابع بیشتری اضافه کنید
]

def fetch_all_configs(sources):
    """تمام کانفیگ‌ها را از منابع مختلف دریافت و در یک لیست ادغام می‌کند."""
    all_configs = []
    print("شروع دریافت کانفیگ از منابع...")
    for url in sources:
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                configs = response.text.strip().split('\n')
                all_configs.extend(configs)
                print(f"✅ {len(configs)} کانفیگ از {url} دریافت شد.")
        except requests.RequestException as e:
            print(f"❌ خطا در دریافت از {url}: {e}")
    return list(set(all_configs)) # حذف موارد تکراری

def decode_vmess(vmess_link):
    """لینک vmess را دیکود کرده و به آبجکت JSON تبدیل می‌کند."""
    if not vmess_link.startswith("vmess://"):
        return None
    try:
        b64_part = vmess_link.replace("vmess://", "")
        # رفع خطای پدینگ Base64
        b64_part += '=' * (-len(b64_part) % 4)
        decoded_json = base64.b64decode(b64_part).decode('utf-8')
        return json.loads(decoded_json)
    except Exception:
        return None

def main():
    """تابع اصلی برای اجرای کامل فرآیند."""
    raw_configs = fetch_all_configs(SOURCES)
    if not raw_configs:
        print("هیچ کانفیگی برای پردازش یافت نشد. خروج.")
        return

    print(f"\nتعداد کل کانفیگ‌های منحصر به فرد: {len(raw_configs)}")
    print("شروع پردازش و دسته‌بندی بر اساس پورت...")

    # استفاده از defaultdict برای سادگی در گروه‌بندی
    categorized_by_port = defaultdict(list)

    for config_link in raw_configs:
        details = decode_vmess(config_link)
        if details and 'port' in details:
            # پورت را به عنوان کلید برای دسته‌بندی استفاده می‌کنیم
            port = str(details['port'])
            categorized_by_port[port].append(config_link)

    print("دسته‌بندی انجام شد. شروع به نوشتن فایل‌ها...")

    # ایجاد پوشه‌ها در صورت عدم وجود
    os.makedirs('ports', exist_ok=True)
    os.makedirs('sub', exist_ok=True)

    # ذخیره تمام کانفیگ‌ها در یک فایل کلی
    all_configs_content = "\n".join(raw_configs)
    with open('All-Configs.txt', 'w') as f:
        f.write(all_configs_content)
    with open('sub/all.txt', 'w') as f:
        f.write(base64.b64encode(all_configs_content.encode('utf-8')).decode('utf-8'))
    print("✅ فایل کلی 'All-Configs.txt' و لینک اشتراک آن ساخته شد.")


    # نوشتن فایل برای هر پورت
    for port, configs in categorized_by_port.items():
        if not configs:
            continue

        # ۱. فایل متنی خام
        file_path = f"ports/{port}.txt"
        content = "\n".join(configs)
        with open(file_path, 'w') as f:
            f.write(content)

        # ۲. فایل لینک اشتراک (Base64)
        sub_path = f"sub/{port}.txt"
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        with open(sub_path, 'w') as f:
            f.write(encoded_content)

        print(f"✅ فایل برای پورت {port} با {len(configs)} کانفیگ ساخته شد.")

    print("\n🎉 پردازش با موفقیت به پایان رسید.")

if __name__ == "__main__":
    main()
