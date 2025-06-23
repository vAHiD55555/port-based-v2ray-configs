import requests
import base64
import json
import os
import subprocess
import time
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
import threading

# ==========================================================
#                      تنظیمات تست
# ==========================================================
# فایل ورودی که حاوی تمام کانفیگ‌ها است
INPUT_FILE = "All-Configs.txt"
# فایل خروجی برای کانفیگ‌های تست شده
OUTPUT_FILE_TESTED = "sub/tested_configs.txt"
# آدرس فایل اجرایی Xray-core
XRAY_PATH = "./xray"
# آدرس URL برای تست سرعت (یک فایل ۱۰ مگابایتی)
SPEEDTEST_URL = "http://cachefly.cachefly.net/10mb.test"
# حداقل سرعت قابل قبول (به مگابیت بر ثانیه)
MIN_SPEED_MBPS = 1.0
# تعداد کانفیگ‌هایی که به صورت همزمان تست می‌شوند
CONCURRENT_TESTS = 10
# پورت محلی برای هر تست
BASE_SOCKS_PORT = 11000
# ==========================================================

def get_config_info(link):
    """لینک کانفیگ را تحلیل کرده و مشخصات آن را برمی‌گرداند."""
    try:
        protocol = link.split("://")[0].lower()
        if protocol == "vless":
            parsed_url = urlparse(link)
            query_params = parse_qs(parsed_url.query)
            return {
                "protocol": "vless",
                "address": parsed_url.hostname,
                "port": parsed_url.port,
                "id": parsed_url.username,
                "flow": query_params.get("flow", [None])[0],
                "security": query_params.get("security", ["none"])[0],
                "sni": query_params.get("sni", [None])[0],
                "fp": query_params.get("fp", [None])[0],
                "type": query_params.get("type", ["tcp"])[0],
                "host": query_params.get("host", [None])[0],
                "path": query_params.get("path", ["/"])[0],
                "pbk": query_params.get("pbk", [None])[0],
                "sid": query_params.get("sid", [None])[0]
            }
        # می‌توان تحلیل سایر پروتکل‌ها را نیز اضافه کرد
    except Exception:
        return None
    return None

def create_xray_config(details, port):
    """یک فایل کانفیگ JSON موقت برای Xray می‌سازد."""
    config = {
        "log": {"loglevel": "warning"},
        "inbounds": [{
            "port": port,
            "listen": "127.0.0.1",
            "protocol": "socks",
            "settings": {"auth": "noauth", "udp": True}
        }],
        "outbounds": [{
            "protocol": details["protocol"],
            "settings": {
                "vnext": [{
                    "address": details["address"],
                    "port": details["port"],
                    "users": [{"id": details["id"], "flow": details.get("flow", "xtls-rprx-vision")}]
                }]
            },
            "streamSettings": {
                "network": details.get("type", "tcp"),
                "security": details.get("security", "none"),
                "realitySettings": {
                    "serverName": details.get("sni"),
                    "fingerprint": details.get("fp"),
                    "publicKey": details.get("pbk"),
                    "shortId": details.get("sid"),
                } if details.get("security") == "reality" else None,
                "wsSettings": {
                    "path": details.get("path"),
                    "headers": {"Host": details.get("host")}
                } if details.get("type") == "ws" else None,
                "grpcSettings": {
                    "serviceName": details.get("path")
                } if details.get("type") == "grpc" else None
            }
        }]
    }
    # حذف کلیدهای خالی برای جلوگیری از خطا
    if config["outbounds"][0]["streamSettings"]["security"] != "reality":
        del config["outbounds"][0]["streamSettings"]["realitySettings"]

    filename = f"temp_config_{port}.json"
    with open(filename, 'w') as f:
        json.dump(config, f)
    return filename

def test_config_speed(config_link, port, results_list):
    """یک کانفیگ را تست کرده و سرعت آن را محاسبه می‌کند."""
    details = get_config_info(config_link)
    if not details or details['protocol'] != 'vless':
        return

    config_file = create_xray_config(details, port)
    process = None
    try:
        cmd = [XRAY_PATH, "run", "-c", config_file]
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2) # زمان برای شروع کامل Xray

        proxies = {
            "http": f"socks5://127.0.0.1:{port}",
            "https": f"socks5://127.0.0.1:{port}",
        }
        start_time = time.time()
        response = requests.get(SPEEDTEST_URL, proxies=proxies, timeout=15, stream=True)
        
        if response.status_code == 200:
            size_bytes = 0
            for chunk in response.iter_content(chunk_size=1024):
                size_bytes += len(chunk)
            
            end_time = time.time()
            duration = end_time - start_time
            if duration > 0:
                speed_mbps = (size_bytes * 8) / (duration * 1024 * 1024)
                if speed_mbps >= MIN_SPEED_MBPS:
                    print(f"✅  سرعت: {speed_mbps:.2f} Mbps | {config_link[:30]}...")
                    results_list.append({"speed": speed_mbps, "config": config_link})
                else:
                    print(f"❌  کند: {speed_mbps:.2f} Mbps | {config_link[:30]}...")
            else:
                print(f"❌  خطای زمان‌سنجی | {config_link[:30]}...")
        else:
            print(f"❌  اتصال ناموفق | {config_link[:30]}...")
    
    except Exception as e:
        print(f"❌  خطای کلی: {e} | {config_link[:30]}...")
    
    finally:
        if process:
            process.terminate()
            process.wait()
        if os.path.exists(config_file):
            os.remove(config_file)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"فایل ورودی '{INPUT_FILE}' پیدا نشد.")
        return
        
    with open(INPUT_FILE, 'r') as f:
        all_configs = f.read().strip().split('\n')
    
    vless_configs = [c for c in all_configs if c.startswith("vless://")]
    print(f"تعداد {len(vless_configs)} کانفیگ VLESS برای تست پیدا شد.")

    threads = []
    working_configs = []
    
    for i in range(0, len(vless_configs), CONCURRENT_TESTS):
        batch = vless_configs[i:i + CONCURRENT_TESTS]
        for j, config in enumerate(batch):
            port = BASE_SOCKS_PORT + j
            thread = threading.Thread(target=test_config_speed, args=(config, port, working_configs))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        threads = [] # پاک کردن لیست برای دسته بعدی
    
    if working_configs:
        # مرتب‌سازی بر اساس سرعت (از بیشترین به کمترین)
        working_configs.sort(key=lambda x: x["speed"], reverse=True)
        
        # ذخیره در فایل خروجی
        final_links = [item["config"] for item in working_configs]
        
        os.makedirs('sub', exist_ok=True)
        with open(OUTPUT_FILE_TESTED, 'w') as f:
            f.write("\n".join(final_links))
            
        print(f"\n✅  تعداد {len(final_links)} کانفیگ سالم و پرسرعت در فایل '{OUTPUT_FILE_TESTED}' ذخیره شد.")
    else:
        print("\nℹ️  هیچ کانفیگ سالمی با حداقل سرعت مورد نظر پیدا نشد.")

if __name__ == "__main__":
    main()
