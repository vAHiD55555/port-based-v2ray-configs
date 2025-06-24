import requests
import base64
import json
import os
import re
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta, timezone

# === منابع نهایی کانفیگ ===
# شما می‌توانید این لیست را در آینده ویرایش کنید
SOURCES = {
    "barry-far": "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt",
    "mahdibland": "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "Epodonios": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "soroushmirzaei": "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/mixed"
}

# === پارامترهای دسته‌بندی ===
# فقط برای پورت‌های موجود در این لیست فایل جداگانه ساخته می‌شود
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
            # افزایش زمان تایم‌اوت برای جلوگیری از خطا در شبکه‌های کند
            response = requests.get(url, timeout=120)
            if response.status_code == 200 and response.text:
                content = response.text.strip()
                # برخی منابع محتوای خود را با Base64 کد می‌کنند
                try:
                    # یک بررسی ساده برای تشخیص محتوای Base64
                    if len(content) > 1000 and "://" not in content:
                        decoded_content = base64.b64decode(content).decode('utf-8')
                        configs = decoded_content.strip().split('\n')
                    else:
                        configs = content.split('\n')
                    
                    # پاک‌سازی لیست و حذف خطوط خالی یا نامعتبر
                    valid_configs = [line.strip() for line in configs if line.strip() and '://' in line]
                    if valid_configs:
                        all_configs.extend(valid_configs)
                        source_stats[name] = len(valid_configs)
                        print(f"  ✅ {len(valid_configs)} کانفیگ معتبر از {name} اضافه شد.")
                except Exception as e:
                    print(f"  ⚠️ خطا در پردازش محتوay منبع {name}: {e}")
        except requests.RequestException as e:
            print(f"❌ خطا در اتصال به منبع {name}: {e}")
    
    # حذف کانفیگ‌های تکراری با استفاده از set
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
            # تبدیل hy2 به hysteria2 برای یکپارچگی
            protocol = "hysteria2" if protocol in ["hy2", "hysteria2"] else protocol
            parsed_url = urlparse(link)
            port = str(parsed_url.port)
        elif protocol == "vmess":
            # دیکود کردن اطلاعات از Base64
            b64_part = link.replace("vmess://", "")
            b64_part += '=' * (-len(b64_part) % 4) # Padding
            decoded_json_str = base64.b64decode(b64_part).decode('utf-8')
            config_json = json.loads(decoded_json_str)
            port = str(config_json.get('port'))
        elif protocol == "ss":
            protocol = "shadowsocks" # استانداردسازی نام
            link_main_part = link.split('#')[0]
            if '@' in link_main_part:
                parsed_url = urlparse(link_main_part)
                port = str(parsed_url.port)
            else: # فرمت قدیمی‌تر ss
                b64_part = link_main_part.replace("ss://", "").split('#')[0]
                b64_part += '=' * (-len(b64_part) % 4)
                decoded_str = base64.b64decode(b64_part).decode('utf-8')
                port = str(decoded_str.split('@')[1].split(':')[-1])
        else:
            return None, None # پروتکل‌های ناشناخته

        return (protocol, port if (port and port.isdigit()) else None)
    except Exception:
        # در صورت بروز هرگونه خطا در پارس کردن، از این کانفیگ صرف نظر می‌شود
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
    فایل README.md را با استفاده از آمار جدید به‌روزرسانی می‌کند.
    """
    try:
        print("\nشروع به‌روزرسانی فایل README.md...")
        with open('README.template.md', 'r', encoding='utf-8') as f:
            template_content = f.read()

        # ساخت بلاک آمار اصلی
        stats_lines = [
            f"**آخرین به‌روزرسانی:** {stats['update_time']}",
            f"**تعداد کل کانفیگ‌های منحصر به فرد:** {stats['total_configs']}\n",
            "#### تفکیک بر اساس پروتکل:"
        ]
        for protocol, count in stats['protocols'].items():
            stats_lines.append(f"- **{protocol.capitalize()}:** {count} کانفیگ")
        
        stats_lines.append("\n#### تفکیک بر اساس پورت‌های معروف:")
        for port in sorted(FAMOUS_PORTS):
            if port in stats['ports']:
                 stats_lines.append(f"- **پورت {port}:** {stats['ports'].get(port, 0)} کانفیگ")

        stats_block = "\n".join(stats_lines)
        new_readme_content = re.sub(r'(<!-- STATS_START -->)(.|\n)*?(<!-- STATS_END -->)', f'\\1\n{stats_block}\n\\3', template_content)

        # ساخت بلاک آمار منابع
        source_stats_lines = []
        for name, count in stats['source_stats'].items():
            source_stats_lines.append(f"- **{name}:** {count} کانفیگ")
        
        source_stats_block = "\n".join(source_stats_lines)
        # جایگزینی بخش آمار منابع
        new_readme_content = re.sub(r'(<!-- SOURCE_STATS_START -->)(.|\n)*?(<!-- SOURCE_STATS_END -->)', f'\\1\n{source_stats_block}\n\\3', new_readme_content)
        
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(new_readme_content)
        print("✅ فایل README.md با آمار جدید با موفقیت بازنویسی شد.")
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
    print("\nشروع دسته‌بندی کانفیگ‌ها بر اساس پورت و پروتکل...")
    categorized_by_port = defaultdict(list)
    categorized_by_protocol = defaultdict(list)

    for config_link in raw_configs:
        protocol, port = get_config_info(config_link)
        if port:
            categorized_by_port[port].append(config_link)
        if protocol:
            categorized_by_protocol[protocol].append(config_link)
    print("✅ دسته‌بندی با موفقیت انجام شد.")
    
    # مرحله ۳: نوشتن فایل‌های دسته‌بندی شده
    print("\nشروع نوشتن فایل‌های دسته‌بندی شده...")
    
    # اطمینان از وجود پوشه‌های مورد نیاز
    os.makedirs('sub/protocols', exist_ok=True)

    # نوشتن فایل all.txt شامل تمام کانفیگ‌های منحصر به فرد
    with open('sub/all.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(raw_configs))
    print("- فایل 'sub/all.txt' با موفقیت ایجاد شد.")

    # نوشتن فایل‌ها بر اساس پورت‌های معروف
    for port, configs in categorized_by_port.items():
        if port in FAMOUS_PORTS:
            with open(f'sub/{port}.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(configs))
            print(f"- فایل پورت 'sub/{port}.txt' با موفقیت ایجاد شد.")

    # نوشتن فایل‌ها بر اساس پروتکل
    for protocol, configs in categorized_by_protocol.items():
        with open(f'sub/protocols/{protocol}.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(configs))
        print(f"- فایل پروتکل 'sub/protocols/{protocol}.txt' با موفقیت ایجاد شد.")
    
    # مرحله ۴: جمع‌آوری آمار و به‌روزرسانی README
    stats = {
        "total_configs": len(raw_configs),
        "update_time": get_tehran_time(),
        "protocols": {p: len(c) for p, c in sorted(categorized_by_protocol.items())},
        "ports": {p: len(c) for p, c in categorized_by_port.items()},
        "source_stats": source_stats
    }
    update_readme(stats)
    
    print("\n🎉 پروژه با موفقیت به پایان رسید.")

if __name__ == "__main__":
    main()
