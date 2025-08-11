# Port-based V2Ray Configs

This repository provides categorized V2Ray/Trojan/Shadowsocks configurations aggregated from public sources.
The README is partially dynamic: three sections are auto-updated by `categorize_all_protocols.py`.

---

## Statistics (Protocol × Common Ports)
<!-- START-STATS -->
_Last update: 2025-08-11 09:18:40 UTC_

| Protocol | 80 | 443 | 8080 | 2053 | 2083 | 2087 | 2096 | Total |
|---|---|---|---|---|---|---|---|---|
| VLESS | 2278 | 3504 | 650 | 169 | 80 | 210 | 557 | 7448 |
| VMESS | 428 | 1172 | 83 | 31 | 19 | 10 | 20 | 1763 |
| TROJAN | 27 | 425 | 0 | 24 | 6 | 2 | 1 | 485 |
| SS | 14 | 566 | 364 | 0 | 1 | 2 | 0 | 947 |
| OTHER | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Total** | 2747 | 5667 | 1097 | 224 | 106 | 224 | 578 | 10643 |
<!-- END-STATS -->

> (The above table shows protocols as rows and common ports as columns. Totals are shown in last row/column.)

---

## Subscription Links (popular ports only)
<!-- START-LINKS -->
| Protocol | Config Count | Subscription Link |
|----------|--------------|-------------------|
| VLESS | 13050 | [📎 Link](./sub/vless.txt) |
| VMESS | 3157 | [📎 Link](./sub/vmess.txt) |
| TROJAN | 1099 | [📎 Link](./sub/trojan.txt) |
| SS | 3525 | [📎 Link](./sub/ss.txt) |
| OTHER | 43 | [📎 Link](./sub/other.txt) |

| Port | Config Count | Subscription Link |
|------|--------------|-------------------|
| 80 | 2747 | [📎 Link](./sub/port_80.txt) |
| 443 | 5667 | [📎 Link](./sub/port_443.txt) |
| 8080 | 1097 | [📎 Link](./sub/port_8080.txt) |
| 2053 | 224 | [📎 Link](./sub/port_2053.txt) |
| 2083 | 106 | [📎 Link](./sub/port_2083.txt) |
| 2087 | 224 | [📎 Link](./sub/port_2087.txt) |
| 2096 | 578 | [📎 Link](./sub/port_2096.txt) |

| Protocol | Port | Config Count | Subscription Link |
|----------|------|--------------|-------------------|
| VLESS | 80 | 2278 | [📎 Link](./detailed/vless/80.txt) |
| VLESS | 443 | 3504 | [📎 Link](./detailed/vless/443.txt) |
| VLESS | 8080 | 650 | [📎 Link](./detailed/vless/8080.txt) |
| VLESS | 2053 | 169 | [📎 Link](./detailed/vless/2053.txt) |
| VLESS | 2083 | 80 | [📎 Link](./detailed/vless/2083.txt) |
| VLESS | 2087 | 210 | [📎 Link](./detailed/vless/2087.txt) |
| VLESS | 2096 | 557 | [📎 Link](./detailed/vless/2096.txt) |
| VMESS | 80 | 428 | [📎 Link](./detailed/vmess/80.txt) |
| VMESS | 443 | 1172 | [📎 Link](./detailed/vmess/443.txt) |
| VMESS | 8080 | 83 | [📎 Link](./detailed/vmess/8080.txt) |
| VMESS | 2053 | 31 | [📎 Link](./detailed/vmess/2053.txt) |
| VMESS | 2083 | 19 | [📎 Link](./detailed/vmess/2083.txt) |
| VMESS | 2087 | 10 | [📎 Link](./detailed/vmess/2087.txt) |
| VMESS | 2096 | 20 | [📎 Link](./detailed/vmess/2096.txt) |
| TROJAN | 80 | 27 | [📎 Link](./detailed/trojan/80.txt) |
| TROJAN | 443 | 425 | [📎 Link](./detailed/trojan/443.txt) |
| TROJAN | 2053 | 24 | [📎 Link](./detailed/trojan/2053.txt) |
| TROJAN | 2083 | 6 | [📎 Link](./detailed/trojan/2083.txt) |
| TROJAN | 2087 | 2 | [📎 Link](./detailed/trojan/2087.txt) |
| TROJAN | 2096 | 1 | [📎 Link](./detailed/trojan/2096.txt) |
| SS | 80 | 14 | [📎 Link](./detailed/ss/80.txt) |
| SS | 443 | 566 | [📎 Link](./detailed/ss/443.txt) |
| SS | 8080 | 364 | [📎 Link](./detailed/ss/8080.txt) |
| SS | 2083 | 1 | [📎 Link](./detailed/ss/2083.txt) |
| SS | 2087 | 2 | [📎 Link](./detailed/ss/2087.txt) |

For full list of all ports and detailed files, see the [detailed folder](./detailed).
<!-- END-LINKS -->

For the full list of ports / files see the `detailed/` folder.

---

## Sources & Summary
<!-- START-SOURCES -->
| Source | Fetched Lines |
|--------|---------------|
| barry-far | 15810 |
| kobabi | 313 |
| mahdibland | 4906 |
| Epodonios | 15814 |
| Rayan-Config | 83 |
| **Total fetched** | 36926 |
| **Unique configs** | 20874 |
| **Duplicates removed** | 16052 |
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
