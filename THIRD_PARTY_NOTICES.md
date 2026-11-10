# Notices

Original project: OguzhanDUYAR/WinOptimizer. Existing GNU GPL version 3 license is preserved in LICENSE. Original source and history remain available. The desktop implementation never executes legacy scripts.

## Aion

Kaan Savukduran’s user-provided/generated Aion assets, explicitly authorized for this app. The requested 4-column/8-row sprite sheet is from Kaan’s `reallife-rpg/assets/companions/aion_actions.png`; icon from `reallife-rpg/assets/branding/aion-icon.png`; ICO from `fire-axolotl/branding/aion.ico`. Other projects were read only. Character collection state was not changed. Origins and hashes are in docs/ASSETS.json. Aion is not a Windows/Microsoft mascot.

## OpenDyslexic

Copyright Abbie Gonzalez. SIL Open Font License 1.1, Reserved Font Name OpenDyslexic. Original unmodified OTF files and full license are under public/fonts/. Source: docs/FONT_SOURCE.json. Regular/bold include Ç Ğ İ Ö Ş Ü ç ğ ı ö ş ü. Fonts are bundled and work offline.

## Libraries

Electron: MIT, bundled Chromium/Node notices. React/React DOM: MIT. Lucide: ISC. Vite: MIT. Electron Builder: MIT. Playwright: Apache-2.0. Exact versions/integrity hashes: package-lock.json. Runtime dependencies’ license files are included by the packager; Electron’s LICENSE.electron.txt and LICENSES.chromium.html remain in the installed runtime.

WinOptimizer-specific Aion animation sheet (`public/assets/aion-optimizer.png`): generated for this application from Kaan’s approved main character, turnaround and tail-continuity references in Drive. 4 columns × 6 rows; 24 distinct poses. Original generated master retained in the session workspace. The earlier Aion assets and their provenance remain preserved. Runtime installers and driver packages are downloaded/imported by the user; Microsoft installers are not redistributed inside this application.

Interactive Aion atlas (`public/assets/aion-pet.png`): Kaan’s user-owned Aion Pet art reused from his `reallife-rpg` companion assets with his explicit request. Source SHA-256 and frame layout are recorded in `docs/ASSETS.json`. Pointer direction and body-part feedback follow the requested RealLife interaction behavior; that repository was read only. No pet collection or other application data was changed.


## Native Windows GUI (6.0.0)

Python/PySide6 6.8.3 and Qt Widgets replace the Electron renderer in released 6.x packages. Qt is dynamically loaded from the PyInstaller extraction directory. LGPL-3.0 and GPL-3.0 texts are bundled in `native/licenses`; Qt source and modification/relinking instructions are available from https://code.qt.io/cgit/qt/qtbase.git/tag/?h=v6.8.3 and https://doc.qt.io/qtforpython-6/licenses.html . Source for this application is published under the repository GPLv3. Users may replace the extracted compatible Qt shared libraries; no anti-tampering checks prevent replacement of Qt libraries. Python and PyInstaller retain their respective licenses/bootloader exception. The bundled Node.js v24.22.1 runtime includes its complete LICENSE with third-party notices in `vendor/NODE-LICENSE.txt`. Chromium, Electron and Qt WebEngine are not included in the new application packages. Existing React/Electron files are retained as historical source/reference, not imported by the native entry.
