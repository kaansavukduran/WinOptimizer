# WinOptimizer Aion Forge

Authorized repository: https://github.com/kaansavukduran/WinOptimizer
Working branch: `forge/aion-desktop`. Target: `main`.
Platform: **Windows x64 only**, explicitly requested by Kaan.

The commit containing this file identifies the checkpoint. Upstream history is retained; the original tree was clean. No AGENTS.md or prior FORGE.md existed. Other repos were read only for Kaan’s assets and font provenance.

Implemented: isolated Electron desktop; reversible age-filtered cleanup; real PowerShell backend; driver inventory/third-party backup/selected Windows Update drivers; HKCU startup rollback; DNS/network/power; bilingual persistent settings; independent scale/text/font/motion; Aion sprite frames; real-check milestones; exports; pinned-key verified updates; NSIS installer/Windows workflows.

Acceptance: installed entry opens; TR/EN keeps the settings category; 135% and 200% persist independently of text/font/theme; cleanup protects personal files and new originals on restore; real checks deduplicate; invalid update signatures block installation. Two real packages must prove in-app updating and data retention.

## Verification status

- Local Node security/data tests: initial 9 passed.
- Local TypeScript/Vite production build: passed.
- Browser combined accessibility tests: 5 passed, including TR/EN persistence, invalid values, independent reset, 200% + 125% text + OpenDyslexic + high contrast + narrow viewport, reduced motion, optional Aion/journey, actual source-frame changes.
- Windows parser/backend, installed smoke, two-package updater: pending Actions.
- Publication and private Drive backup: pending.
- Authenticode certificate unavailable. Update authenticity uses Ed25519 + SHA-256, not an Authenticode claim.
- Connected GitHub identity cannot access Actions secrets (HTTP 403). Private update signing key stays outside repo/backups for this session. Future signing continuity needs a maintainer-managed secret; never silently replace the trusted key.

Next: fix concrete failures, install both Windows packages, publish signed update metadata/assets, test actual in-app upgrade, record exact commit/run/release links, back up source/history/packages.

Private Drive project folder: https://drive.google.com/drive/folders/1weoq7A_Y6jjhVgR8eb3QrnES9cxGurGE

Future: multi-profile caches, OEM integrations, device-specific recovery and deeper diagnostics. Do not claim universal acceleration, full-system backup, automatic driver rollback or firmware updating.
