<!-- AUTO-GENERATED FILE: Do not edit README.md directly. Run `python scripts/generate-readme.py` -->
# AV-Scrub-Index

An automated, machine-readable dataset of official uninstallation and scrub utilities for Antivirus and Endpoint Security (AV/EDR/XDR) products.

> **Direct Data Endpoint:** [`dist/index.json`](dist/index.json) | [`dist/index.min.json`](dist/index.min.json) | **Schema:** [`data/schema/uninstaller.schema.json`](data/schema/uninstaller.schema.json)

## Removal Tools Directory (Public Direct-Download)

Official removal utilities served directly from unauthenticated vendor CDNs (`distribution: "public"`):

| Vendor | Tool Name | Tier | Download URL | Safe Mode? | Silent / Force Args | Notes |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **Avast** | [Avast Clear (avastclear)](https://www.avast.com/uninstall-utility) | `consumer` | [Download](https://files.avast.com/iavs9x/avastclear.exe) | Yes | `/silent` | Prompts to reboot into Windows Safe Mode when launched interactively; run from Safe Mode with /silent for unattended cleanup. |
| **AVG** | [AVG Clear](https://www.avg.com/en-us/avg-remover) | `consumer` | [Download](https://honzik.avcdn.net/setup/avg-av/release/avg_av_clear.exe) | Yes | `/silent` | Official AVG removal utility served from Gen Digital CDN. Recommended to execute in Windows Safe Mode; supports /silent flag. |
| **Avira** | [Avira RegistryCleaner](https://support.avira.com/hc/en-us/articles/360002858514-How-do-I-perform-a-manual-reinstallation-of-my-Avira-product) | `consumer` | [Download](https://install.avira-update.com/package/regcleaner/win32/en/avira_registry_cleaner_en.exe) | Yes | `None` | Execute in Windows Safe Mode after removing C:\Program Files\Avira and C:\ProgramData\Avira to purge residual Avira registry keys. |
| **Bitdefender** | [GravityZone BEST Uninstall Tool (BEST_uninstallTool)](https://www.bitdefender.com/business/support/en/77209-80124-using-the-uninstall-tool-to-remove-bitdefender-endpoint-security-tools.html) | `enterprise` | [Download](https://download.bitdefender.com/SMB/Hydra/release/bst_win/uninstallTool/BEST_uninstallTool.exe) | No | `/bdparams /noWait` / `/bdparams /bruteForce /noWait` | Enterprise GravityZone scrubber; pass /password="<pwd>" after /bdparams if uninstall password protection is enabled, or run /bruteForce from Safe Mode. |
| **Bitdefender** | [Bitdefender Consumer Uninstall Tool](https://www.bitdefender.com/uninstall/) | `consumer` | [Download](https://www.bitdefender.com/links/uninstall_consumer_paid.html) | No | `None` | Evergreen redirect to the latest consumer Bitdefender Uninstall Tool binary. For GravityZone enterprise endpoints, use BEST_uninstallTool.exe. |
| **Comodo / Xcitium** | [Comodo CIS Cleanup Tool (ciscleanuptool_x64)](https://forums.comodo.com/t/forced-uninstaller-tools/289908) | `both` | [Download](https://download.comodo.com/cis/download/installs/ciscleanuptool/ciscleanuptool_x64.exe) | No | `None` | Official 64-bit forced uninstaller removing cmdagent, inspect.sys firewall drivers, and containment artifacts (32-bit build at ciscleanuptool_x86.exe); typically prompts for two reboots. |
| **ESET** | [ESET Uninstaller](https://support.eset.com/en/kb2289-uninstall-eset-manually-using-the-eset-uninstaller-tool) | `both` | [Download](https://download.eset.com/com/eset/tools/installers/eset_apps_remover/latest/uninstaller.exe) | Yes | `/force` | Console-based utility that must be executed from Windows Safe Mode. Pass /force for unprompted removal; /reinst also resets network interfaces. |
| **F-Secure / WithSecure** | [F-Secure Uninstallation Tool (FsUninstallationTool)](https://www.f-secure.com/en/support/tools) | `both` | [Download](https://download.sp.f-secure.com/uninstallationtool/FsUninstallationTool.exe) | No | `None` | Official last-resort removal utility for F-Secure consumer suites and legacy WithSecure endpoint agents. |
| **G DATA** | [G DATA Product Cleaner (AVCleaner)](https://www.gdata.de/help-en/tools/ProductCleaner/) | `both` | [Download](https://gdata-a.akamaihd.net/Q/WEB/TOOL/GDATA_Product_Cleaner.exe) | No | `--cleanall --nomessage --noreboot` / `--cleanall -q` | Successor to G DATA AVCleaner (also linked via https://secure.gd/dl-product-cleaner) supporting GUI and CLI automation (--client:u, --cleanall, -q, --noreboot). |
| **Kaspersky** | [Kaspersky Removal Tool (kavremover)](https://support.kaspersky.com/common/uninstall/1464) | `both` | [Download](https://media.kaspersky.com/utilities/ConsumerUtilities/kavremvr.exe) | No | `-nodetect` | Displays an interactive CAPTCHA challenge to prevent unauthorized removal; pass -nodetect to manually select unlisted product profiles. |
| **Malwarebytes** | [Malwarebytes Support Tool CLI (mbstcmd)](https://support.threatdown.com/hc/en-us/articles/16660990749331-Business-Support-Tool-for-Nebula-and-OneView) | `both` | [Download](https://downloads.malwarebytes.com/file/mbstcmd) | No | `/y /cleanup /noreboot` / `/y /cleanup` | Dedicated headless command-line remover ideal for RMM scripts; disable Tamper Protection first if managed by Nebula/OneView. |
| **Malwarebytes** | [Malwarebytes Support Tool (MBST)](https://support.malwarebytes.com/hc/en-us/articles/360039023473-Uninstall-and-reinstall-Malwarebytes-using-the-Malwarebytes-Support-Tool) | `both` | [Download](https://downloads.malwarebytes.com/file/mbst) | No | `/y /cleanup /noreboot` / `/y /cleanup` | Use the Clean option under Advanced in GUI mode; for headless RMM automation see malwarebytes-mbst-cmd (https://downloads.malwarebytes.com/file/mbstcmd). |
| **McAfee** | [McAfee Consumer Product Removal Tool (MCPR)](https://www.mcafee.com/support/?articleId=TS101331&page=shell&shell=article-view) | `consumer` | [Download](https://download.mcafee.com/molbin/iss-loc/SupportTools/MCPR/MCPR.exe) | No | `None` | Interactive GUI requires security CAPTCHA validation; extracted mccleanup.exe inside %TEMP% supports unattended -p/-v/-s flags. |
| **Norton** | [Norton 360 Remover (NRnR)](https://support.norton.com/sp/en/us/home/current/solutions/v20240301142500636) | `consumer` | [Download](https://honzik.avcdn.net/setup/norton-suite/release/norton_360_remover.exe) | No | `/silent` / `/RemoveOnly` | Current Norton 360 Remover binary (also reachable via https://www.norton.com/nortonremover). Choose Remove in UI to skip reinstallation. |
| **Panda Security** | [Panda Generic Uninstaller](https://www.pandasecurity.com/en/support/) | `both` | [Download](https://www.pandasecurity.com/resources/tools/uninstaller.exe) | No | `None` | Purges residual Panda Dome and legacy Panda Antivirus services, filter drivers, and registry keys prior to system reboot. |
| **Sophos** | [SophosZap](https://support.sophos.com/support/s/article/KB-000038989) | `enterprise` | [Download](https://download.sophos.com/tools/SophosZap.exe) | No | `--confirm` | Last-resort CLI cleanup tool. Disable Tamper Protection first, run SophosZap --confirm from an elevated prompt, reboot, and re-run if prompted. |
| **Trend Micro** | [Trend Micro Remnant File Remover Tool](https://helpcenter.trendlife.com/en-us/article/tmka-11879) | `consumer` | [Download](https://powerbox-na-file.trend.org/SFDC/DownloadFile_iv.php?jsonInfo=%7B%22Query%22%3A%22nXHR467Mr%2BMAdpqcxpZE533QzOnQ1s3nYrVSB3z8qxVtNWTomxmDnfj87mwb6LI3GTBySeJHoJpmqhe%2BF2XlxRD8KnKaLE%2Fn1NDLJZ%2BPoeLSKyr7GggMBKWNIyxs23zpkNe7Wk3c74lxO%2F053Rz54i%2F%2BMzJV%2FlE9OHouMhBddkna54xIouV8xDlqvAqKyHXYKF9UMytuA%2BGJPVU0VclqbBMwDU1QSZHfuL0tR0%2BgdvLezTUzDzZOKfjaYScwSMi3vVPmhAj8FpruTOz8kkIMjBw1M7PlosdPLYVqg6P37UoexsqAz0ZZDwg5h84iKpgLrqE8TXJMb%2BvptL%2Fs18x%2BeQ%3D%3D%22%2C%22iv%22%3A%22ef213a00e1ffa98eccd3badd864f2f32%22%7D) | No | `None` | Official consumer cleanup utility when Trend Micro Diagnostic Toolkit (supporttool.exe) is missing or fails to remove leftover drivers. |
| **VIPRE** | [VIPRE Removal Tool](https://documentation.remote.management/remote-management/troubleshooting/Content/kb/Where-do-I-obtain-the-Vipre-Removal-Tool.htm) | `both` | [Download](https://go.vipre.com/?linkid=1914) | No | `-spquiet` / `-spquiet --nolog` | Removes broken VIPRE Consumer, Endpoint Security, and N-able Managed AV (SBAMSvc) installations; pass -spquiet for unattended RMM execution. |
| **Webroot** | [Webroot SecureAnywhere Uninstaller (wsainstall)](https://answers.webroot.com/Webroot/ukp.aspx?pid=12&app=vw&vw=1&solutionid=1025) | `both` | [Download](https://anywhere.webrootcloudav.com/zerol/wsainstall.exe) | No | `/uninstall /silent` / `/uninstall` | Webroot's official evergreen installer doubles as its forcible uninstaller when invoked with /uninstall; interactive runs display a CAPTCHA challenge. |
| **ZoneAlarm (Check Point)** | [ZoneAlarm Clean Utility (CLEAN.exe)](https://support.zonealarm.com/hc/en-us/articles/115001848332-How-to-Upgrade-your-ZoneAlarm-software) | `consumer` | [Download](https://download.zonealarm.com/bin/free/support/download/CLEAN.exe) | Yes | `None` | Disable 'Load ZoneAlarm at startup' or boot into Windows Safe Mode before running CLEAN.exe to remove Check Point TrueVector (vsmon) drivers. |

## Portal-Gated & Support-Issued Scrubbers

Official enterprise EDR/XDR and support-issued removal utilities that require a customer portal login, active entitlement, or support request (`distribution: "portal_gated"`):

| Vendor | Tool Name | Tier | Portal / KB | Safe Mode? | Silent / Force Args | Notes |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **Broadcom (Symantec)** | [Symantec CleanWipe](https://knowledge.broadcom.com/external/article/178870/download-the-cleanwipe-removal-tool-to-u.html) | `enterprise` | [Portal / KB](https://knowledge.broadcom.com/external/article/178870/download-the-cleanwipe-removal-tool-to-u.html) | Yes | `-silent` | Available to entitled customers via Broadcom Support Portal (Article 178870) or inside full SEP installation media under Tools\CleanWipe. |
| **CrowdStrike** | [Falcon Windows Sensor Uninstall Tool (CsUninstallTool)](https://falcon.crowdstrike.com/support/tool-downloads) | `enterprise` | [Portal / KB](https://falcon.crowdstrike.com/support/tool-downloads) | No | `/quiet` / `MAINTENANCE_TOKEN=<token> /quiet` | Download CsUninstallTool.exe from Falcon Console > Support and resources > Tool downloads. Supply MAINTENANCE_TOKEN=<token> when sensor uninstall protection is enabled. |
| **Dr.Web** | [Dr.Web Remover (drw_remover)](https://support.drweb.com/) | `both` | [Portal / KB](https://support.drweb.com/) | No | `None` | Emergency uninstallation utility issued via Dr.Web Support / customer portal; requires interactive CAPTCHA entry to disengage dwprot.sys self-protection. |
| **K7 Computing** | [K7 Security Product Removal Tool (K7RT)](https://support.k7computing.com/) | `both` | [Portal / KB](https://support.k7computing.com/) | No | `None` | Standalone cleanup utility obtained via K7 Support when standard uninstallation fails or the settings protection password is lost. |
| **SentinelOne** | [SentinelCleaner](https://support.sentinelone.com/) | `enterprise` | [Portal / KB](https://support.sentinelone.com/) | Yes | `uninstall.exe /k "<passphrase>" /q` | Obtained via SentinelOne Management Console or Support; SentinelCleaner must be executed from Windows Safe Mode when standard passphrase uninstall fails. |
| **Trellix (McAfee Enterprise)** | [Endpoint Product Removal Tool (EPR)](https://kcm.trellix.com/corporate/index?page=content&id=KB90895&locale=en_US) | `enterprise` | [Portal / KB](https://kcm.trellix.com/corporate/index?page=content&id=KB90895&locale=en_US) | No | `--accepteula --ALL` / `--accepteula --ALL --BRUTEFORCE=MFEDEEPREM_FOLDER_ATP_STOP` | Requires active Trellix Grant Number (KB90895). EPR binaries have a built-in ~90-day security expiration window and must be refreshed periodically. |
| **Trend Micro** | [Common Uninstall Tool (CUT / SCUT)](https://success.trendmicro.com/en-US/solution/KA-0013399) | `enterprise` | [Portal / KB](https://success.trendmicro.com/en-US/solution/KA-0013399) | No | `-c` / `ForceUninstall -c` | Downloaded via Trend Micro Business Success Portal (Diagnostic Tool > CUT); binaries carry a rolling ~30-day validity window. |
| **WatchGuard / Cytomic** | [Protection Generic Uninstaller (PSInfo)](https://www.watchguard.com/help/docs/help-center/en-US/Content/en-US/Endpoint-Security/troubleshooting/psinfotool/psinfo.html) | `enterprise` | [Portal / KB](https://www.watchguard.com/help/docs/help-center/en-US/Content/en-US/Endpoint-Security/troubleshooting/psinfotool/psinfo.html) | No | `-local -nogui` | Bundled inside WatchGuard PSInfo (archive password 'panda' -> Tools tab -> Protection Generic Uninstaller); prompts for tamper password if configured. |

## Automation & Consumption

```powershell
# PowerShell Quick-Fetch Example
$tools = Invoke-RestMethod -Uri "https://raw.githubusercontent.com/SeanShaffer88/av-scrub-index/main/dist/index.json"

# Filter to direct public-CDN downloads (exclude portal-gated enterprise tools)
$publicTools = $tools | Where-Object { $_.distribution -ne "portal_gated" -and $_.download_url }

# Fetch a specific vendor scrubber
$avast = $publicTools | Where-Object { $_.id -eq "avast-clear" }
Start-BitsTransfer -Source $avast.download_url -Destination "$env:TEMP\avastclear.exe"
```

## Contributing & Local Validation

Vendor records live in [`data/vendors/`](data/vendors/) (one JSON file per tool) and are validated against [`data/schema/uninstaller.schema.json`](data/schema/uninstaller.schema.json).

```bash
# Validate all vendor entries against the JSON Schema
python scripts/validate-schema.py

# Probe vendor download & portal endpoints
python scripts/check-links.py --all --output report.json

# Rebuild dist/index.json, dist/index.min.json, and README.md
python scripts/compile-dist.py
python scripts/generate-readme.py
```
