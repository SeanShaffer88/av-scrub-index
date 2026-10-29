<!-- AUTO-GENERATED FILE: Do not edit README.md directly. Run `python scripts/generate-readme.py` -->
# AV-Scrub-Index

An automated, machine-readable dataset of official uninstallation and scrub utilities for Antivirus and Endpoint Security products.

> **Direct Data Endpoint:** [`dist/index.json`](dist/index.json) | [`dist/index.min.json`](dist/index.min.json) | **Schema:** [`data/schema/uninstaller.schema.json`](data/schema/uninstaller.schema.json)

## Removal Tools Directory

| Vendor | Tool Name | Tier | Download URL | Safe Mode? | Silent / Force Args | Notes |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **Avast** | [Avast Clear (avastclear)](https://www.avast.com/uninstall-utility) | `consumer` | [Download](https://files.avast.com/iavs9x/avastclear.exe) | Yes | `/silent` | Prompts to reboot into Windows Safe Mode when launched interactively; run from Safe Mode with /silent for unattended cleanup. |
| **AVG** | [AVG Clear](https://www.avg.com/en-us/avg-remover) | `consumer` | [Download](https://honzik.avcdn.net/setup/avg-av/release/avg_av_clear.exe) | Yes | `/silent` | Official AVG removal utility served from Gen Digital CDN. Recommended to execute in Windows Safe Mode; supports /silent flag. |
| **Bitdefender** | [Bitdefender Consumer Uninstall Tool](https://www.bitdefender.com/uninstall/) | `consumer` | [Download](https://www.bitdefender.com/links/uninstall_consumer_paid.html) | No | `None` | Evergreen redirect to the latest consumer Bitdefender Uninstall Tool binary. For GravityZone enterprise endpoints, use BEST_uninstallTool.exe. |
| **ESET** | [ESET Uninstaller](https://support.eset.com/en/kb2289-uninstall-eset-manually-using-the-eset-uninstaller-tool) | `both` | [Download](https://download.eset.com/com/eset/tools/installers/eset_apps_remover/latest/uninstaller.exe) | Yes | `/force` | Console-based utility that must be executed from Windows Safe Mode. Pass /force for unprompted removal; /reinst also resets network interfaces. |
| **Kaspersky** | [Kaspersky Removal Tool (kavremover)](https://support.kaspersky.com/common/uninstall/1464) | `both` | [Download](https://media.kaspersky.com/utilities/ConsumerUtilities/kavremvr.exe) | No | `-nodetect` | Displays an interactive CAPTCHA challenge to prevent unauthorized removal; pass -nodetect to manually select unlisted product profiles. |
| **Malwarebytes** | [Malwarebytes Support Tool (MBST)](https://support.malwarebytes.com/hc/en-us/articles/360039023473-Uninstall-and-reinstall-Malwarebytes-using-the-Malwarebytes-Support-Tool) | `both` | [Download](https://downloads.malwarebytes.com/file/mbst) | No | `/y /cleanup /noreboot` / `/y /cleanup` | Use the Clean option under Advanced in GUI mode; for headless automation fetch mbstcmd.exe via https://downloads.malwarebytes.com/file/mbst-cmd with /y /cleanup /noreboot. |
| **McAfee** | [McAfee Consumer Product Removal Tool (MCPR)](https://www.mcafee.com/support/?articleId=TS101331&page=shell&shell=article-view) | `consumer` | [Download](https://download.mcafee.com/molbin/iss-loc/SupportTools/MCPR/MCPR.exe) | No | `None` | Interactive GUI requires security CAPTCHA validation; extracted mccleanup.exe inside %TEMP% supports unattended -p/-v/-s flags. |
| **Norton** | [Norton 360 Remover (NRnR)](https://support.norton.com/sp/en/us/home/current/solutions/v20240301142500636) | `consumer` | [Download](https://honzik.avcdn.net/setup/norton-suite/release/norton_360_remover.exe) | No | `/silent` / `/RemoveOnly` | Current Norton 360 Remover binary (also reachable via https://www.norton.com/nortonremover). Choose Remove in UI to skip reinstallation. |
| **Sophos** | [SophosZap](https://support.sophos.com/support/s/article/KB-000038989) | `enterprise` | [Download](https://download.sophos.com/tools/SophosZap.exe) | No | `--confirm` | Last-resort CLI cleanup tool. Disable Tamper Protection first, run SophosZap --confirm from an elevated prompt, reboot, and re-run if prompted. |

## Automation & Consumption

```powershell
# PowerShell Quick-Fetch Example
$tools = Invoke-RestMethod -Uri "https://raw.githubusercontent.com/SeanShaffer88/av-scrub-index/main/dist/index.json"
$avast = $tools | Where-Object { $_.id -eq "avast-clear" }
Start-BitsTransfer -Source $avast.download_url -Destination "$env:TEMP\avastclear.exe"
```

## Contributing & Local Validation

Vendor records live in [`data/vendors/`](data/vendors/) (one JSON file per vendor) and are validated against [`data/schema/uninstaller.schema.json`](data/schema/uninstaller.schema.json).

```bash
# Validate all vendor entries against the JSON Schema
python scripts/validate-schema.py

# Probe vendor download endpoints
python scripts/check-links.py --all --output report.json

# Rebuild dist/index.json, dist/index.min.json, and README.md
python scripts/compile-dist.py
python scripts/generate-readme.py
```
