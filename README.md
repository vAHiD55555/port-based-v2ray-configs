
<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/{GITHUB_USER}/{GITHUB_REPO}/{WORKFLOW_FILE_NAME}?style=for-the-badge&logo=githubactions&logoColor=white" alt="Actions Status">
  <img src="https://img.shields.io/github/last-commit/{GITHUB_USER}/{GITHUB_REPO}?style=for-the-badge&logo=git&logoColor=white" alt="Last Commit">
  <img src="https://img.shields.io/github/repo-size/{GITHUB_USER}/{GITHUB_REPO}?style=for-the-badge&logo=github" alt="Repo Size">
  <img src="https://img.shields.io/github/license/{GITHUB_USER}/{GITHUB_REPO}?style=for-the-badge" alt="License">
  <br>
  <img src="https://img.shields.io/github/stars/{GITHUB_USER}/{GITHUB_REPO}?style=social" alt="GitHub Stars">
  <img src="https://img.shields.io/github/forks/{GITHUB_USER}/{GITHUB_REPO}?style=social" alt="GitHub Forks">
</p>
"""

    # The main template for the README.md file.
    readme_template = f"""
{badges_section.strip()}

# Port-Based V2Ray Configs

This repository contains a collection of V2Ray configurations, aggregated from various public sources. The configs are automatically categorized by protocol and port using a Python script.

---

## 📊 Config Stats

<!-- START-STATS -->
_Last update: 2025-08-14 11:12:57 UTC_

| Protocol | 80 | 443 | 2053 | 8880 | 2087 | 2096 | 8443 | Total |
|---|---|---|---|---|---|---|---|---|
| VLESS | 2302 | 3436 | 142 | 1569 | 195 | 448 | 605 | 12965 |
| VMESS | 406 | 1191 | 34 | 96 | 10 | 11 | 196 | 3300 |
| TROJAN | 32 | 594 | 46 | 10 | 31 | 26 | 94 | 1453 |
| SS | 13 | 567 | 0 | 0 | 1 | 0 | 22 | 3511 |
| OTHER | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
<!-- END-STATS -->

---

## 🔗 Subscription Links

<!-- START-LINKS -->
### By Port
| Port | Count | Subscription Link |
|---|---|---|
| 80 | 2753 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_80.txt) |
| 443 | 5788 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_443.txt) |
| 2053 | 222 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_2053.txt) |
| 8880 | 1675 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_8880.txt) |
| 2087 | 237 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_2087.txt) |
| 2096 | 485 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_2096.txt) |
| 8443 | 917 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_8443.txt) |

### By Protocol
| Protocol | Count | Subscription Link |
|---|---|---|
| VLESS | 12965 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/vless.txt) |
| VMESS | 3300 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/vmess.txt) |
| TROJAN | 1453 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/trojan.txt) |
| SS | 3511 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/ss.txt) |
| OTHER | 5 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/other.txt) |

### By Protocol & Port (Common Ports)

<table width="100%" style="border: none; border-collapse: collapse;">
  <tr style="background-color: transparent;">
    <td width="50%" valign="top" style="border: none; padding-right: 10px;">
      <table><thead><tr><th>Protocol</th><th>Port</th><th>Count</th><th>Link</th></tr></thead><tbody><tr><td>VLESS</td><td>80</td><td>2302</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/80.txt">Sub</a></td></tr><tr><td>VLESS</td><td>443</td><td>3436</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/443.txt">Sub</a></td></tr><tr><td>VLESS</td><td>2053</td><td>142</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/2053.txt">Sub</a></td></tr><tr><td>VLESS</td><td>8880</td><td>1569</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/8880.txt">Sub</a></td></tr><tr><td>VLESS</td><td>2087</td><td>195</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/2087.txt">Sub</a></td></tr><tr><td>VLESS</td><td>2096</td><td>448</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/2096.txt">Sub</a></td></tr><tr><td>VLESS</td><td>8443</td><td>605</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/8443.txt">Sub</a></td></tr><tr style="border-top: 2px solid #d0d7de;"><td>VMESS</td><td>80</td><td>406</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/80.txt">Sub</a></td></tr><tr><td>VMESS</td><td>443</td><td>1191</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/443.txt">Sub</a></td></tr><tr><td>VMESS</td><td>2053</td><td>34</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/2053.txt">Sub</a></td></tr><tr><td>VMESS</td><td>8880</td><td>96</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/8880.txt">Sub</a></td></tr><tr><td>VMESS</td><td>2087</td><td>10</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/2087.txt">Sub</a></td></tr><tr><td>VMESS</td><td>2096</td><td>11</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/2096.txt">Sub</a></td></tr></tbody></table>
    </td>
    <td width="50%" valign="top" style="border: none; padding-left: 10px;">
      <table><thead><tr><th>Protocol</th><th>Port</th><th>Count</th><th>Link</th></tr></thead><tbody><tr><td>VMESS</td><td>8443</td><td>196</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/8443.txt">Sub</a></td></tr><tr style="border-top: 2px solid #d0d7de;"><td>TROJAN</td><td>80</td><td>32</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/80.txt">Sub</a></td></tr><tr><td>TROJAN</td><td>443</td><td>594</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/443.txt">Sub</a></td></tr><tr><td>TROJAN</td><td>2053</td><td>46</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/2053.txt">Sub</a></td></tr><tr><td>TROJAN</td><td>8880</td><td>10</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/8880.txt">Sub</a></td></tr><tr><td>TROJAN</td><td>2087</td><td>31</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/2087.txt">Sub</a></td></tr><tr><td>TROJAN</td><td>2096</td><td>26</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/2096.txt">Sub</a></td></tr><tr><td>TROJAN</td><td>8443</td><td>94</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/8443.txt">Sub</a></td></tr><tr style="border-top: 2px solid #d0d7de;"><td>SS</td><td>80</td><td>13</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/ss/80.txt">Sub</a></td></tr><tr><td>SS</td><td>443</td><td>567</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/ss/443.txt">Sub</a></td></tr><tr><td>SS</td><td>2087</td><td>1</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/ss/2087.txt">Sub</a></td></tr><tr><td>SS</td><td>8443</td><td>22</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/ss/8443.txt">Sub</a></td></tr></tbody></table>
    </td>
  </tr>
</table>

<!-- END-LINKS -->

---

## 📚 Sources & Summary

<!-- START-SOURCES -->

<table width="100%" style="border: none; border-collapse: collapse;">
  <tr style="background-color: transparent;">
    <td width="50%" valign="top" style="border: none; padding-right: 10px;">
      <h4>Sources</h4>
      <table><thead><tr><th>Source</th><th>Fetched Lines</th></tr></thead><tbody><tr><td>Epodonios</td><td>16175</td></tr><tr><td>Rayan-Config</td><td>98</td></tr><tr><td>barry-far</td><td>16150</td></tr><tr><td>kobabi</td><td>313</td></tr><tr><td>mahdibland</td><td>4943</td></tr></tbody></table>
    </td>
    <td width="50%" valign="top" style="border: none; padding-left: 10px;">
      <h4>Summary</h4>
      <table><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody><tr><td>Total Fetched</td><td>37679</td></tr><tr><td>Unique Configs</td><td>21234</td></tr><tr><td>Duplicates Removed</td><td>16445</td></tr></tbody></table>
    </td>
  </tr>
</table>

<!-- END-SOURCES -->
