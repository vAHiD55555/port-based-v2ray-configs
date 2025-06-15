# port-based-v2ray-configs

<div dir="rtl">

# کانفیگ‌های V2Ray بر اساس پورت

[![وضعیت آپدیت خودکار](https://github.com/hamed1124/port-based-v2ray-configs/actions/workflows/main.yml/badge.svg)](https://github.com/hamed1124/port-based-v2ray-configs/actions/workflows/main.yml)

یک مخزن خودکار که کانفیگ‌های رایگان را جمع‌آوری کرده و بر اساس شماره پورت و نوع پروتکل دسته‌بندی می‌کند.

---

### 🔧 ویژگی‌ها

**به‌روزرسانی خودکار**
<br>
مخزن به صورت خودکار هر **۴ ساعت** یک بار به‌روز شده و جدیدترین کانفیگ‌ها را دریافت می‌کند.

**پشتیبانی از پروتکل‌های مختلف**
<br>
کانفیگ‌های پروتکل‌های `Vmess`، `Vless`، `Trojan`، `ShadowSocks` و پروتکل‌های جدیدتر جمع‌آوری می‌شوند.

**دسته‌بندی هوشمند و چندگانه**
<br>
کانفیگ‌ها به سه روش دسته‌بندی می‌شوند: بر اساس **شماره پورت**، بر اساس **نوع پروتکل**، و یک دسته ویژه برای **VLESS روی پورت‌های خاص**.

**حذف موارد تکراری**
<br>
اسکریپت به طور هوشمند کانفیگ‌های تکراری را که از منابع مختلف دریافت شده‌اند، حذف می‌کند.

---

### 🚀 نحوه استفاده (لینک‌های اشتراک)

از لینک‌های اشتراک زیر در نرم‌افزار کلاینت خود (مانند v2rayNG یا Nekoray) استفاده کنید.

---

#### ⭐ لینک ویژه (VLESS روی پورت‌های پرسرعت)
این لینک فقط حاوی کانفیگ‌های **VLESS** است که روی پورت‌های مقاوم و پرسرعت `80`, `443`, `8080` و `8088` قرار دارند. (پیشنهاد ویژه)
  ```
  [https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/VLESS_Special_Ports.txt](https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/VLESS_Special_Ports.txt)
  ```

---

#### دسته‌بندی بر اساس نوع پروتکل
برای دریافت تمام کانفیگ‌های یک پروتکل خاص، از لینک‌های زیر استفاده کنید:

- **فقط VLESS:**
  ```
  [https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/protocols/vless.txt](https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/protocols/vless.txt)
  ```
- **فقط VMess:**
  ```
  [https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/protocols/vmess.txt](https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/protocols/vmess.txt)
  ```
- **(سایر پروتکل‌ها در پوشه `sub/protocols` قرار دارند)**

---

#### دسته‌بندی بر اساس شماره پورت

- **تمام کانفیگ‌ها (ادغام شده):**
  ```
  [https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/all.txt](https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/all.txt)
  ```

- **پورت‌های معروف (شامل تمام پروتکل‌ها):**
  ```
  # پورت 443
  [https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/443.txt](https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/443.txt)

  # پورت 80
  [https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/80.txt](https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/80.txt)
  ```

- **سایر پورت‌ها (مثال برای پورت ۲۰۵۲):**
  ```
  [https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/other/2052.txt](https://raw.githubusercontent.com/hamed1124/port-based-v2ray-configs/main/sub/other/2052.txt)
  ```
---

### 📚 منابع جمع‌آوری

این پروژه کانفیگ‌ها را از مخازن تجمعی زیر دریافت می‌کند. با تشکر فراوان از صاحبان این مخازن برای کار ارزشمندشان:

- **V2ray-Configs** by [barry-far](https://github.com/barry-far/V2ray-Config)
- **V2RayAggregator** by [mahdibland](https://github.com/mahdibland/V2RayAggregator)
- **v2ray-configs** by [Epodonios](https://github.com/Epodonios/v2ray-configs)
- **telegram-configs-collector** by [soroushmirzaei](https://github.com/soroushmirzaei/telegram-configs-collector)

---


### 📄 سلب مسئولیت

این مخزن تنها برای اهداف آموزشی و تحقیقاتی ایجاد شده است. کانفیگ‌ها به صورت خودکار از منابع عمومی در اینترنت جمع‌آوری می‌شوند و هیچ تضمینی برای پایداری یا امنیت آن‌ها وجود ندارد. مسئولیت استفاده از این کانفیگ‌ها بر عهده کاربر است.

</div>
