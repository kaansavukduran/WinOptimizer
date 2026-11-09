# Scan & Fix (5.1.0)

Driver Booster's [official manual](https://www.iobit.com/product-manuals/db-help/) describes scans for outdated, missing and faulty drivers and game components, plus tools for audio, device, network, resolution and game DLL issues. Its proprietary catalog and repair algorithms are not part of this project. WinOptimizer uses Windows inventory and Windows Update, with Microsoft sources for optional components.

| Check | Evidence | Available action |
| --- | --- | --- |
| Devices | Win32_PnPEntity error codes, presence, signed-driver version/provider | PnPUtil hardware rescan with UAC, then verify the same device's error code; Driver center; Windows troubleshooting |
| Driver updates (opt-in online) | Applicable Windows Update driver offers | Driver center for backup, selection, separate confirmation and installation |
| Audio | AudioEndpointBuilder and Audiosrv status/startup type | Start only a stopped, non-disabled service with UAC; verify Running; open Windows sound settings |
| Network | Adapter link status; opt-in DNS resolution of www.microsoft.com | Clear only DNS cache; repeat the same query and report unresolved failures accurately |
| Display | Reported resolution and basic display driver indicators | Windows display settings and Driver center; no guessed preferred resolution |
| Visual C++ | v14 x64/x86 Installed/Version in both registry views | Microsoft documentation/download source; user installation and rescan |
| Legacy DirectX | D3DX9_43 and XAudio2_7 file presence in System32 and SysWOW64 | Official Microsoft runtime page; user installation and rescan |

A missing optional runtime is not a Windows fault. Installed indicators are not a full runtime integrity test. Older Visual C++ generations and game-specific files are not checked. Disabled devices and services may be deliberate. Disconnected devices are counted separately and never marked broken or removed. A driver date alone never triggers a warning. Unknown providers and failed Windows Update queries are shown as unavailable, not healthy or no updates.

Repairs use server-side cached report/finding/action IDs, explicit confirmation, a 30-minute lifetime and a fresh precheck. The action and audio service target are taken from the trusted finding, not renderer-supplied commands. Each repair consumes its report. Native actions are fixed allowlists; the only elevation is starting an eligible audio service or hardware rescan. After the action, a fresh check yields `fixed`, `still-present` or `unverified`. Merely opening settings or running a command is never evidence of repair. Pending/failed/completed repair outcomes are saved in local history and JSON exports.

No individual DLL downloads, blanket registry cleaning, adapter/Winsock resets, security disabling, third-party driver catalog scraping, arbitrary shell execution or forced driver removal are added. Existing driver backup is third-party packages only, not a full Windows restore image.

## Validation

Node tests cover classification, failed providers, online/offline query separation, confirmation, forged actions, expiration, changed targets, consumed reports, failed actions and postcondition verification. Chromium fixtures verify UI confirmation, unresolved outcomes, manual guidance, state retention and 200% narrow layouts. Fixture data is never presented as real hardware evidence. Windows CI separately reads real inventory using PowerShell 5.1 and exercises Scan & Fix inside the installed application. Hardware is not deliberately broken to exercise repairs.

## Primary references

- [Win32_PnPEntity and ConfigManagerErrorCode](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-pnpentity)
- [PnPUtil syntax](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/pnputil-command-syntax)
- [Microsoft Visual C++ redistributables](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)
- [Microsoft DirectX End-User Runtime](https://www.microsoft.com/en-us/download/details.aspx?id=35)
