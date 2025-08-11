# Port-based V2Ray Configs

This repository provides categorized V2Ray/Trojan/Shadowsocks configurations aggregated from public sources.
The README is partially dynamic: three sections are auto-updated by `categorize_all_protocols.py`.

---

## Statistics (Protocol × Common Ports)
<!-- START-STATS -->
_Last update: 2025-08-11 12:22:58 UTC_

| Protocol | 80 | 443 | 8080 | 2053 | 2083 | 2087 | 2096 | Total |
|---|---|---|---|---|---|---|---|---|
| VLESS | 2284 | 3599 | 682 | 165 | 78 | 212 | 577 | 7597 |
| VMESS | 429 | 1169 | 84 | 31 | 18 | 10 | 19 | 1760 |
| TROJAN | 27 | 423 | 0 | 24 | 6 | 2 | 1 | 483 |
| SS | 14 | 577 | 366 | 0 | 1 | 2 | 0 | 960 |
| OTHER | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Total** | 2754 | 5768 | 1132 | 220 | 103 | 226 | 597 | 10800 |
<!-- END-STATS -->

> (The above table shows protocols as rows and common ports as columns. Totals are shown in last row/column.)

---

## Subscription Links (popular ports only)
<!-- START-LINKS -->
| Protocol | Port | Link |
|----------|------|------|
| **VLESS** | 80 | [📎 Link](./sub/vless_80.txt) |
|  | 443 | [📎 Link](./sub/vless_443.txt) |
|  | 8080 | [📎 Link](./sub/vless_8080.txt) |
|  | 2053 | [📎 Link](./sub/vless_2053.txt) |
|  | 2083 | [📎 Link](./sub/vless_2083.txt) |
|  | 2087 | [📎 Link](./sub/vless_2087.txt) |
|  | 2096 | [📎 Link](./sub/vless_2096.txt) |
| **---** | **---** | **---** |
| **VMESS** | 80 | [📎 Link](./sub/vmess_80.txt) |
|  | 443 | [📎 Link](./sub/vmess_443.txt) |
|  | 8080 | [📎 Link](./sub/vmess_8080.txt) |
|  | 2053 | [📎 Link](./sub/vmess_2053.txt) |
|  | 2083 | [📎 Link](./sub/vmess_2083.txt) |
|  | 2087 | [📎 Link](./sub/vmess_2087.txt) |
|  | 2096 | [📎 Link](./sub/vmess_2096.txt) |
| **---** | **---** | **---** |
| **TROJAN** | 80 | [📎 Link](./sub/trojan_80.txt) |
|  | 443 | [📎 Link](./sub/trojan_443.txt) |
|  | 2053 | [📎 Link](./sub/trojan_2053.txt) |
|  | 2083 | [📎 Link](./sub/trojan_2083.txt) |
|  | 2087 | [📎 Link](./sub/trojan_2087.txt) |
|  | 2096 | [📎 Link](./sub/trojan_2096.txt) |
| **---** | **---** | **---** |
| **SS** | 80 | [📎 Link](./sub/ss_80.txt) |
|  | 443 | [📎 Link](./sub/ss_443.txt) |
|  | 8080 | [📎 Link](./sub/ss_8080.txt) |
|  | 2083 | [📎 Link](./sub/ss_2083.txt) |
|  | 2087 | [📎 Link](./sub/ss_2087.txt) |
| **---** | **---** | **---** |

> ℹ️ More ports and protocols are available in the `sub/` and `detailed/` folders.
<!-- END-LINKS -->

For the full list of ports / files see the `detailed/` folder.

---

## Sources & Summary
<!-- START-SOURCES -->
| Source | Collected |
|--------|-----------|
| barry-far | 16037 |
| kobabi | 313 |
| mahdibland | 4906 |
| Epodonios | 16037 |
| Rayan-Config | 83 |

---

| Metric | Value |
|--------|-------|
| Total fetched | 37376 |
| Duplicates removed | 16318 |
| Unique configs | 21058 |
<!-- END-SOURCES -->

---

## Notes
- The script writes subscription files to `sub/` and detailed per-protocol files to `detailed/`.
- README will contain only links to files (not inline config content) to keep size small.
- If you want additional ports to appear in the README, add them to `COMMON_PORTS` in the script.

## Subscription Links
<!-- SUB_LINKS_START -->
| Protocol | Port | Link |
|----------|------|------|
| **trojan** | 443 | [📎 Link](./sub/trojan_443.txt) |
| **---** | **---** | **---** |
| **vless** | 80 | [📎 Link](./sub/vless_80.txt) |
| **vless** | 443 | [📎 Link](./sub/vless_443.txt) |
| **vless** | 8080 | [📎 Link](./sub/vless_8080.txt) |
| **---** | **---** | **---** |
| **vmess** | 80 | [📎 Link](./sub/vmess_80.txt) |
| **vmess** | 443 | [📎 Link](./sub/vmess_443.txt) |

> ℹ️ More ports and protocols are available in the `sub/` and `detailed/` folders.

<!-- SUB_LINKS_END -->

## Sources
<!-- SOURCES_START -->
| Source URL | Collected | Removed Duplicates |
|------------|-----------|--------------------|
| `https://example1.com` | 120 | 20 |
| `https://example2.com` | 90 | 5 |
| --- | --- | --- |
| **Total** | **210** | **25** |

<!-- SOURCES_END -->
