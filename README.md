# -*- coding: utf-8 -*-
# create_readme.py
# This script creates a clean README.md file with the correct template and badges.
# Run it simply as: python create_readme.py

# --- CONFIGURATION ---
# Please verify these values carefully.

# 1. Your GitHub username and repository name.
GITHUB_USER = "hamedcode"
GITHUB_REPO = "port-based-v2ray-configs"

# 2. The EXACT filename of your workflow file located in the .github/workflows/ directory.
#    This is crucial for the "Actions Status" badge.
#    Example: 'main.yml', 'update.yml', etc.
WORKFLOW_FILE_NAME = "main.yml" 

# --- END OF CONFIGURATION ---


# Building the badges section with the configuration above.
badges_section = f"""
<p align="center">
  <!-- Workflow Status Badge -->
  <a href="https://github.com/{GITHUB_USER}/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE_NAME}">
    <img src="https://img.shields.io/github/actions/workflow/status/{GITHUB_USER}/{GITHUB_REPO}/{WORKFLOW_FILE_NAME}?style=for-the-badge&logo=githubactions&logoColor=white" alt="Actions Status">
  </a>
  <!-- Last Commit Badge -->
  <a href="https://github.com/{GITHUB_USER}/{GITHUB_REPO}/commits">
    <img src="https://img.shields.io/github/last-commit/{GITHUB_USER}/{GITHUB_REPO}?style=for-the-badge&logo=git&logoColor=white" alt="Last Commit">
  </a>
  <!-- Repo Size Badge -->
  <img src="https://img.shields.io/github/repo-size/{GITHUB_USER}/{GITHUB_REPO}?style=for-the-badge&logo=github" alt="Repo Size">
  <!-- License Badge (will be red if you don't have a LICENSE file) -->
  <a href="https://github.com/{GITHUB_USER}/{GITHUB_REPO}/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/{GITHUB_USER}/{GITHUB_REPO}?style=for-the-badge" alt="License">
  </a>
  <br>
  <!-- Social Badges -->
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
_Last update: 2025-08-14 10:52:52 UTC_

| Protocol | 80 | 443 | 2053 | 8880 | 2087 | 2096 | 8443 | Total |
|---|---|---|---|---|---|---|---|---|
| VLESS | 2311 | 3502 | 144 | 1584 | 197 | 467 | 609 | 13125 |
| VMESS | 407 | 1193 | 34 | 96 | 10 | 11 | 196 | 3314 |
| TROJAN | 32 | 594 | 46 | 10 | 31 | 26 | 94 | 1447 |
| SS | 13 | 570 | 0 | 0 | 1 | 0 | 22 | 3519 |
| OTHER | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 |
<!-- END-STATS -->

---

## 🔗 Subscription Links

<!-- START-LINKS -->
### By Port
| Port | Count | Subscription Link |
|---|---|---|
| 80 | 2763 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_80.txt) |
| 443 | 5859 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_443.txt) |
| 2053 | 224 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_2053.txt) |
| 8880 | 1690 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_8880.txt) |
| 2087 | 239 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_2087.txt) |
| 2096 | 504 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_2096.txt) |
| 8443 | 921 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/port_8443.txt) |

### By Protocol
| Protocol | Count | Subscription Link |
|---|---|---|
| VLESS | 13125 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/vless.txt) |
| VMESS | 3314 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/vmess.txt) |
| TROJAN | 1447 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/trojan.txt) |
| SS | 3519 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/ss.txt) |
| OTHER | 6 | [Sub Link](https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/sub/other.txt) |

### By Protocol & Port (Common Ports)

<table width="100%" style="border: none; border-collapse: collapse;">
  <tr style="background-color: transparent;">
    <td width="50%" valign="top" style="border: none; padding-right: 10px;">
      <table><thead><tr><th>Protocol</th><th>Port</th><th>Count</th><th>Link</th></tr></thead><tbody><tr><td>VLESS</td><td>80</td><td>2311</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/80.txt">Sub</a></td></tr><tr><td>VLESS</td><td>443</td><td>3502</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/443.txt">Sub</a></td></tr><tr><td>VLESS</td><td>2053</td><td>144</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/2053.txt">Sub</a></td></tr><tr><td>VLESS</td><td>8880</td><td>1584</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/8880.txt">Sub</a></td></tr><tr><td>VLESS</td><td>2087</td><td>197</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/2087.txt">Sub</a></td></tr><tr><td>VLESS</td><td>2096</td><td>467</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/2096.txt">Sub</a></td></tr><tr><td>VLESS</td><td>8443</td><td>609</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vless/8443.txt">Sub</a></td></tr><tr style="border-top: 2px solid #d0d7de;"><td>VMESS</td><td>80</td><td>407</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/80.txt">Sub</a></td></tr><tr><td>VMESS</td><td>443</td><td>1193</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/443.txt">Sub</a></td></tr><tr><td>VMESS</td><td>2053</td><td>34</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/2053.txt">Sub</a></td></tr><tr><td>VMESS</td><td>8880</td><td>96</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/8880.txt">Sub</a></td></tr><tr><td>VMESS</td><td>2087</td><td>10</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/2087.txt">Sub</a></td></tr><tr><td>VMESS</td><td>2096</td><td>11</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/2096.txt">Sub</a></td></tr></tbody></table>
    </td>
    <td width="50%" valign="top" style="border: none; padding-left: 10px;">
      <table><thead><tr><th>Protocol</th><th>Port</th><th>Count</th><th>Link</th></tr></thead><tbody><tr><td>VMESS</td><td>8443</td><td>196</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/vmess/8443.txt">Sub</a></td></tr><tr style="border-top: 2px solid #d0d7de;"><td>TROJAN</td><td>80</td><td>32</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/80.txt">Sub</a></td></tr><tr><td>TROJAN</td><td>443</td><td>594</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/443.txt">Sub</a></td></tr><tr><td>TROJAN</td><td>2053</td><td>46</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/2053.txt">Sub</a></td></tr><tr><td>TROJAN</td><td>8880</td><td>10</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/8880.txt">Sub</a></td></tr><tr><td>TROJAN</td><td>2087</td><td>31</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/2087.txt">Sub</a></td></tr><tr><td>TROJAN</td><td>2096</td><td>26</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/2096.txt">Sub</a></td></tr><tr><td>TROJAN</td><td>8443</td><td>94</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/trojan/8443.txt">Sub</a></td></tr><tr style="border-top: 2px solid #d0d7de;"><td>SS</td><td>80</td><td>13</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/ss/80.txt">Sub</a></td></tr><tr><td>SS</td><td>443</td><td>570</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/ss/443.txt">Sub</a></td></tr><tr><td>SS</td><td>2087</td><td>1</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/ss/2087.txt">Sub</a></td></tr><tr><td>SS</td><td>8443</td><td>22</td><td><a href="https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/main/detailed/ss/8443.txt">Sub</a></td></tr></tbody></table>
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
      <table><thead><tr><th>Source</th><th>Fetched Lines</th></tr></thead><tbody><tr><td>Epodonios</td><td>16352</td></tr><tr><td>Rayan-Config</td><td>98</td></tr><tr><td>barry-far</td><td>16327</td></tr><tr><td>kobabi</td><td>313</td></tr><tr><td>mahdibland</td><td>4943</td></tr></tbody></table>
    </td>
    <td width="50%" valign="top" style="border: none; padding-left: 10px;">
      <h4>Summary</h4>
      <table><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody><tr><td>Total Fetched</td><td>38033</td></tr><tr><td>Unique Configs</td><td>21411</td></tr><tr><td>Duplicates Removed</td><td>16622</td></tr></tbody></table>
    </td>
  </tr>
</table>

<!-- END-SOURCES -->
""".strip()

# The name of the file to be created.
file_name = "README.md"

# Writing the content to the file.
try:
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(readme_template)
    # A clean success message that won't be written to the file.
    print(f"✅ Successfully created '{file_name}'.")
    print("➡️  You can now run your main script to populate it.")
except IOError as e:
    print(f"❌ Error creating file '{file_name}': {e}")
