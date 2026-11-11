# Verification evidence

## 6.7.0 integrated native driver workflows

[v6.7.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.7.0) is stable/latest. Application/tag source `84c2977b3c85b417c5b3f70a98bde1f66ab6f623`, PR #18, merge `c3241f9a698c28d0479eed5f1bb5f9889506d4d5`, signed metadata `f1c511620fdaec809e1c5bc12ccb1fc98eaa5ebb`, release `441086918`.

The existing driver center now separates updates, installed inventory, backup/recovery, offline preparation and ignored offers. Inventory search/problem-code filtering, dated local libraries, eligible recovery selection (1–20 per action), source-bound inspection state and atomic bulk ignore/unignore use the existing backend. Update all remains independent of filters and that recovery limit. Workshop controls are categorized within the same application. Unknown/null Windows device codes remain unknown, including a real PowerShell 5.1 fixture covering null, missing, zero and 28.

96 Qt and 58 Node tests passed locally and on Windows. Initial packaged smoke testing caught a test-helper local Qt import shadowing its global; the helper was corrected before final packaging. Final source, PR and main checks passed. Installed, portable, reopened portable and upgraded packages exercised the real inventory and five sections. A uniquely generated unsigned INF was imported for inspection only, verified ineligible/noncheckable with apply disabled, then only that fixture's returned local UUID was removed. No driver was installed by this test. Actual VM inventory contained 58 rows; hardware is the test VM's. Existing scans, hardware categories, cleanup/restore, recovery, personalization, maintenance milestones, portable isolation and locked-EXE replacement still passed.

[Source Windows](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42929726018), [PR](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42929733618), [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42930935244), [publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42931018862), [motion enabled](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42931022893) and [actual installed 6.6.0 → 6.7.0 update](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42931252345) succeeded. The update used real Settings controls and verified payload hash, registry/runtime version, prior preferences, cleanup/restore history and milestones. The animation run checked all ten page clocks using the same package and restored its test-only Windows motion setting; normal app code does not change it.

| Artifact | ID | SHA-256 |
| --- | --- | --- |
| Source Windows | 13815553211 | `707edfa41c3f9f28cdbbcb49126595dee61ac205b50e7941a01202692241e6cf` |
| Motion enabled | 13816312293 | `164644701b020521b794c6fbba30be6950fde57df3a6910a1b0cbc0b89b42cae` |
| Installed update | 13814919812 | `4d3e38b487db8febcd3dd6ccf1458e219fcc451c0a728b04fc835c4444307bd5` |

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| Setup | 96,904,339 | `11f0449f4ee187a316c8300cee3bec9a28e2915f879eac8f0acf81907c832737` |
| Portable | 96,755,094 | `736847bd7e5cf72d77d856fd26e5f3a8f16183f74d277ba2aedb088fbb2c8e58` |

Original ZIP CRC/hashes, five public asset digests, Ed25519 manifest and seven PE icon sizes matched. Actual Windows screenshots: [inventory](screenshots/WinOptimizer-6.7.0-Surucu-Envanteri.png), [blocked unsigned package](screenshots/WinOptimizer-6.7.0-Paket-Inceleme.png). [Private Drive backup](https://drive.google.com/drive/folders/15Xqf4wiTvqzkMCMsc-_aK_negXLIln1N): every source push, merge, metadata and closing docs, full reachable Git history/tags, whole Setup/Portable files and source/evidence archives; raw readback hashes, ZIP CRC and bundles checked. Signing keys excluded. [Request coverage](REQUEST-COVERAGE.md) explicitly records remaining proprietary catalog, OEM/game-component and legacy differences; full Driver Booster parity is not claimed.

## 6.6.0 font, color and contextual Aion animation

[v6.6.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.6.0) was the previous verified stable release. Application/tag source `525229f452b535bce01dac5f07877d0a236f58f0`, PR #17, merge `3878fe1b8b2cef055358cccf650126fa2ade50e8`, signed metadata/test-only animation workflow `23e7cf4051efb9f22e156ba99c2f8ceeb8c40966`. The metadata commit skips the redundant application push build; the unchanged app is validated by source, PR and merge builds, and the new animation workflow is dispatched separately against that exact source artifact.

Settings opens on Appearance. Every page offers a Font and theme shortcut. Font choices, actual preview and bundled Turkish OpenDyslexic glyphs are visible; application/content fonts now update together. Native color picker, five presets, validated hex input, independent reset and black/white primary-button text are included. Theme, accent, UI/text scales and other preferences remain independent. Percentage controls fit narrow screens. [User instructions](PERSONALIZATION.md).

A new transparent 1024×1536 atlas has 24 distinct frames for cleanup, drivers, hardware, startup, tools and history. Existing approved Aion art supplies the other four page loops. Shared pixmaps, a fixed foot anchor, 360 ms frames, short pointer gaze, petting, pause across navigation, one-shot success and hidden-timer suspension are tested. Child-widget construction preserves keyboard focus. Overview keeps its existing care guide first. No separate donor process or browser engine is added; normal application code only reads the Windows reduced-motion preference.

86 Qt and 55 Node tests passed locally and on Windows. Initial Windows checks caught the new header pushing the care action below the viewport and a clock test assuming host foreground/motion policy. Guide priority was restored and the unit clock is controlled independently; actual Windows policy is tested in packaged runs. One final PR runner could not read CIM services; the same source passed the source run and unchanged assertions passed on a fresh second PR attempt.

[Source Windows](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42862554953), [PR, attempt 2](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42862566359), [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42864509713), [publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42864650951), [motion enabled](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42864657457) and [actual installed 6.5.0 → 6.6.0 update](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42865115572) succeeded. Regular runners requested reduced motion and all ten pages used static frames. A separate test-only runner enabled Windows client-area animation, read it back, ran the same source Portable and verified actual clock advance on all ten pages, then restored the original setting in finally. This setter exists only in the opt-in CI workflow. Actual UI controls changed font/accent, verified bundled Turkish glyphs, exercised all page companions and motion/visibility off, then restored saved preferences with milestones unchanged. Existing scans, hardware, cleanup/restore, recovery, journey navigation, portable isolation, locked-EXE replacement, signature and seven icon sizes passed. Upgrade payload hash/registry/runtime, settings, cleanup/restore history and health/scan progress matched.

| Artifact | ID | SHA-256 |
| --- | --- | --- |
| Source Windows | 13786795837 | `1c6c57221acd24fc168418db297dd0f36c8fe94e64b4a66763a2c5c808dfce9e` |
| Motion enabled | 13787151038 | `89773f5e01b21c899ec0c3805975ecdd67009df171167721bfbd0c76ee1d57fc` |
| Installed update | 13785863874 | `2c9926bdaf0941ea6bb220ba4fde2b10006531de968b39ebd78a2320f57e7f00` |

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| Setup | 96,894,439 | `6aa4f697a89b07cd31046c1ff06f47637ed05a80766549f7f2838276eb7a019c` |
| Portable | 96,743,942 | `28081b7cddb2a41418ed8c8a8185f0333f384afb1b57845d0da3a88de87f1961` |

Original archive hashes/ZIP CRC, all five public asset digests and the Ed25519 manifest signature matched. Actual Windows test-runner screenshots: [font/theme](screenshots/WinOptimizer-6.6.0-Yazi-Tema.png), [color presets/picker](screenshots/WinOptimizer-6.6.0-Renkler.png), [Aion with hardware](screenshots/WinOptimizer-6.6.0-Aion-Donanim.png). Hardware shown belongs to the test VM. [Private Drive backup](https://drive.google.com/drive/folders/1i11oPGJtgpqmLSzB0bqCHGn3cX2YTSCQ): every code push, full reachable Git history/tags, whole Setup/Portable files, notes and source/evidence; raw readback hashes, ZIP CRC and bundles checked. Signing keys excluded; old public releases/assets/tags preserved.

## 6.5.0 operation recovery and clear next steps

[v6.5.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.5.0) was the previous verified stable release. Application/tag source `484f317286681816c3e939a481400827bf028500`, PR #16, merge `0a2da16a769292fb313f91b67b81c07b0af47f9f`, signed metadata `bad8e8194f90a09a32056c802429c2ff971e4716`.

Unexpected backend exit, failed startup and malformed response envelopes settle pending requests once. Later requests fail immediately and status polling stops; navigation can display cached results. A readable TR/EN panel identifies the relevant screen/action, explains cancellation, stale selection, administrator cancellation or engine loss, and offers operation details, local diagnostic copy and navigation. Only an explicit allowlist of read operations can be retried with captured options and original screen/section. Mutations are never automatically replayed. An interrupted Windows operation may still be running; its outcome is not asserted. Cached reports are not promised to survive reopening the app. Existing maintenance milestones remain intact. See [recovery behavior](RECOVERY.md).

69 Qt and 55 Node tests passed locally and on Windows. Coverage includes real QProcess startup/exit, missing executable, malformed IDs/status/error fields, callback-versus-protocol exceptions, exactly-once completion, no pending growth, original retry options, no mutation replay, disconnected navigation, startup failure shell, local copy without payloads, TR/EN and 200% UI + 125% text/OpenDyslexic. Initial source/PR tests expected a missing-process signal after subscription; Windows can emit it synchronously. The test now covers both timings and opens the real failure shell. The first final PR attempt reported an unavailable CIM services provider on its runner; the same source passed the full source run and unchanged PR tests passed on a fresh second attempt. Assertions were not weakened.

[Source Windows](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42849224849), [PR, successful attempt 2](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42849238917), [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42851312163), [publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42851360524) and [actual installed 6.4.0 → 6.5.0 update](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42851646661) succeeded. Source artifact `13779049952`, SHA-256 `32afbd62c3076771efe300d24fd5bee6e7482c5ebe624949380cf10a1c68e227`; upgrade artifact `13781885063`, SHA-256 `d49d51fd4a8c5d81b42c6fcb2efa5898e11f1aaf50cb3530f50085fa1873d8e3`. Original archive hashes and ZIP CRC verified.

Installed, portable, reopened portable and upgraded packages deliberately terminated only their own idle bundled Node after ordinary Windows work. Receipts verify immediate error, zero pending requests, stopped polling, no automatic replay, preserved reports/progress and a real recovery screenshot. No in-flight Windows installation was terminated in this test. Existing shared scan, hardware, cleanup/restore, reduced exports, journey navigation, portable data isolation and exact locked-EXE replacement passed. The real update used the app's UI controls, verified the installed payload hash against Portable, registry/runtime version, preferences, cleanup/restore history and existing `health`/`scan` milestones. Seven original icon sizes matched both EXEs; all five public asset digests and the Ed25519 manifest signature matched local verified files.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| Setup | 94,215,580 | `5468a32565f1a6a2202ae5d3131a8bb2a5a28c3d5c37e3b4537cc15fe52fe7ef` |
| Portable | 94,090,849 | `7676454849d0d26dd4351c8b4e8f61edaf315bde4d183ae0a853c17a978cd547` |

Private backup target: [6.5.0 folder](https://drive.google.com/drive/folders/1G5Rb5K8imWeNcem9fEDzdaL6lpxEesh1). Every pushed source/merge/metadata/closing commit gets a tracked-source ZIP, full reachable Git-history bundle and receipt; both EXEs and source/evidence are backed up whole. Raw downloads are compared by SHA-256/length, ZIP CRC and Git bundle verification. Signing keys are excluded. Older public assets/tags are unchanged.

## 6.4.0 explained care steps and guided actions

[v6.4.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.4.0) was the previous verified stable release. Final application/tag source `807c252a0eac0d4e8f1ccf41fa26a0f12cb3fa2c`, PR #15, merge `a6855cb4bc499bbea630bb21577af7c329e3ec31`, signed metadata `c27a82718f5bb2158933aa89ebde53ad21526c0b`.

The old bare 2/3 bar did not identify its tasks. Overview now starts with the three existing milestone names, explanations, prior-completion states and a prominent first-missing-step action. The meanings are unchanged: `health` is system information, `scan` is cleanup candidate scanning (not Scan & Fix), and `drivers` is a nonempty third-party driver backup. Opening a step only navigates, reveals/focuses its real button and explains what to press. A return action takes the user back to the guide; navigation grants no progress. All-done, historical-versus-health meaning, gamification-off and zero-package backup outcomes are explicit. Saved milestones are preserved.

47 Qt and 55 Node tests passed locally and on Windows. Coverage includes TR/EN, 0/1/2/3 completion, different missing tasks, 200% UI + independent 125% text/OpenDyslexic, visible keyboard focus, late text/layout changes, manual scrolling, disposed-page cancellation, return flow and the actual service predicates. Initial Windows source/PR runs failed because a late Windows layout could move the target out of view and a test compared benign status polling as a side effect. A target-owned Qt observer now follows layout/range changes only while the action is focused on the current page; the test excludes only status polling. These failures were resolved before publication.

[Final source Windows](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42836539870), [PR](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42836550684), [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42837793956), [publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42838264089) and [actual installed 6.3.3 → 6.4.0 update](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42838763716) succeeded. First source/PR attempts `42835302935` / `42835323900` are retained as failure evidence; old published assets/tags are unchanged.

Source artifact `13774496808`: SHA-256 `dbc7215d72157c44f26b6ef298a317078ebe8003e222699a4927f9324718e54e`. Upgrade artifact `13775410366`: SHA-256 `210cfd3c81ab9b77cedebe1f1fb8c7ff4bf0c370ff2de785c006a4959ddc506a`. Original hashes and ZIP CRC verified. Actual installed/portable/reopened apps read Service history, showed the guide, followed its suggestion, verified the real button was focused/visible and returned with milestones unchanged. Existing scan/provider receipts, hardware, reduced export, cleanup/restore, portable isolation, locked EXE replacement and seven icon sizes passed.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| Setup | 94,206,450 | `123faed04869e5cf5f89375eab6c13e3e602b50b63d278046ea7e331f023505b` |
| Portable | 94,081,082 | `29a80519578215418701fd17ac51e4c54a5c1ccda4e943ca527dd3f16830b7ff` |

Native UI Automation invoked the old app's signed update. Installed payload hash, registry and real running Qt version matched 6.4.0. English/dark/135% UI/125% text/OpenDyslexic, original cleanup/restore events and milestones survived; the upgraded guide's milestone array matches the verified retained history. [Guide screenshot](screenshots/WinOptimizer-6.4.0-Bakim-Rehberi.png) and [revealed next action](screenshots/WinOptimizer-6.4.0-Siradaki-Adim.png) come from the actual upgraded Windows runner, not the user's PC. [Private 6.4.0 backups](https://drive.google.com/drive/folders/1t6Npt3xJDciBsdA8j4_ULPs5nx7zGREz) include source/reachable Git, both complete EXEs and evidence; EXE readbacks match the original files. Final source/history/evidence closure also uses byte/hash, ZIP and bundle checks. Signing keys are excluded.

## 6.3.3 UI lifetime, scale input and result feedback

[v6.3.3](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.3.3) is a preserved stable release. Final application/tag source `ca63f1ae1c07da7d8a7c03e6f235e38e666acd62`, PR #14, merge `1db8f3942b714b6cda3175ba81bbc24fa80e06ad`, signed metadata `c20c95e31d47e8227fa118819f388ad3980197cb`.

A stability audit reproduced `Internal C++ object (Paragraph) already deleted` while navigating and changing appearance with pending layout work. Paragraph fitting now uses a widget-owned, coalesced timer and Qt slots; resize/document signals schedule work rather than recursively fitting immediately. Initial option-group callbacks are bound to their group lifetime and read its current checked state. Disposed pages cannot receive this work, and immediately expanded options remain visible. Keyboard scale changes now save; rounded input updates both controls to the recorded value with blocked intermediate signals. Scan issues/unknown findings trigger review/help feedback even if the envelope omits an attention flag; healthy results retain celebration.

35 Qt and 54 Node tests passed locally and on Windows. Seven new regression cases fail on an isolated 6.3.2 tree; the healthy-result control passes there. Positive coverage includes delayed startup, rapid disposal and resizing, TR/EN, 80/135/200% scale, independent 125% text, OpenDyslexic, dark/high contrast, keyboard scale changes and expansion before the initial callback. A separate source audit covered 24 language/theme/scale combinations with narrow/wide navigation and reported zero callback errors after the lifecycle change.

[Final source Windows](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42827961742), [PR](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42827972758), [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42829231941), [publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42829259677) and [actual 6.3.2 → 6.3.3 installed update](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42829583076) succeeded. Earlier source/PR runs were cancelled after the final expansion-state correction superseded them; published versions were not changed.

Source artifact `13769753543`: SHA-256 `49b07ee6d0733f4069301478888768792358ab3485f6b0bf126ab7a57fe11ad1`. Upgrade artifact `13770946314`: SHA-256 `8e8846df56ec1999baafd5cc1e823159b0e6624bc4d07c6c712199e554dbda13`. Original hashes and ZIP CRC verified. Actual installed/portable/reopened Qt apps completed scan/provider receipts, hardware inventory, reduced exports and data-isolation checks. Locked executable replacement and all seven original icon payload sizes passed. [Actual Portable screenshot](screenshots/WinOptimizer-6.3.3-Portable.png) shows the test machine.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| Setup | 94,197,038 | `2ee7a3f167c294ac76b30e73f67b3731e4c7db54dfc37a4b59089eb3586a9ec0` |
| Portable | 94,072,751 | `28baa49b80ca59cfc84057bd7a07850fde5cb5171714350a634072652e40a98b` |

Native UI Automation invoked the baseline app's signed update. Installed payload hash, registry and real running Qt version matched 6.3.3. English/dark/135% UI/125% text/OpenDyslexic, original cleanup/restore history and milestones survived. The [private 6.3.3 backup folder](https://drive.google.com/drive/folders/1oIneRNnkJqnFECjrVwBeuWj3yObJvCSz) holds source/history, both complete EXEs and evidence; EXE readbacks matched exact bytes/hashes. Final source/history and evidence closure uses the same ZIP/Git bundle/readback checks, excluding signing keys. These checks establish the exercised scenarios, not universal fault-free operation on every Windows PC.

## 6.3.2 startup resize crash fix

[v6.3.2](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.3.2) is a preserved stable release. Application/tag source `322ab8e59089e6c89b9e4b1ee082ecfdc0d2c319`, PR #13, merge `578d6b2ffbb253175b3b19e779f39d45243ffba6`, signed metadata `3b9c7c745b3aa3c70997aaaee8bfb883fe6ea092`.

The user reported a packaged 6.3.1 Portable crash in `QMainWindow.resizeEvent`: `Window object has no attribute details_expanded`. Qt can resize on first show before the real asynchronous Node bootstrap responds. The expansion flag previously existed only after bootstrap/appearance; synchronous test fixtures hid the ordering. The flag now exists before the first resize, and resize layout work waits until bootstrap is ready. The saved expansion preference is still applied afterwards. No reset or data migration is required.

A delayed-bootstrap regression drives the actual Qt Window through resize, show, narrow/wide sizes and settings delivery. All four TR/EN and expanded/collapsed cases fail with the exact reported AttributeError on the old source and pass after the fix; collapsed cases also use 200% UI scale. 27 Qt and 54 Node tests passed locally and on Windows. [Source Windows](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42822010321), [PR](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42822106630), [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42823081581), [publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42823181236) and [real 6.3.1 → 6.3.2 update](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42823397571) succeeded.

Source artifact `13767473371`, SHA-256 `e74d271a4c92610820a830f21ed4acce45da0d89c204fbe24a0cfc4c448490ef`; upgrade artifact `13768271194`, SHA-256 `69c255975d148e8bc313fb8a5168ee76e90b1afbe9805e9a7b4fe256c2840092`. Original hashes and ZIP CRC verified. Real installed/portable/reopened apps completed local scans, shared Windows provider receipts, hardware inventory, reduced exports and data-isolation checks. Locked installer replacement and all seven original icon payload sizes passed. [Portable Windows screenshot](screenshots/WinOptimizer-6.3.2-Portable.png) shows the test runner, not the user's PC.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| Setup | 94,195,586 | `8aab33cdaced2ee26c167b0b8f4f2d3a2d0341c624cb03e2dd8ebea6889a986e` |
| Portable | 94,071,833 | `5cddddc2149de8719fd629ed8662fc9f85fefeb0330fee52691cc33e6f294d6d` |

Actual baseline UI Automation invoked the signed update. Installed payload hash, registry version and running Qt version matched 6.3.2; English/dark/135% UI/125% text/OpenDyslexic, original cleanup/restore events and milestones were retained. Both full EXEs were backed up and read back by hash in the [private 6.3.2 Drive folder](https://drive.google.com/drive/folders/1belBteQsII4QY7VxrBccOpHmAAcfr0Tn); final source/reachable history, evidence and receipts use the same backup closure. Old releases are preserved and signing keys are excluded.

## 6.3.1 unified Windows scan and existing pages

[v6.3.1](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.3.1) is a preserved stable release. Final application/tag source `01715e9ca2d8f86011bee0949a3a15dc4f745329`; integration PR #11 merge `6219ad3b5e2e5dbb4ef98cc2a2e91c9137c769f7`, final label PR #12 merge `b4c71a406872b182ea2a76899ca923f00a15c484`, signed metadata `8de2c00f163c4b7887aee9d32663df63fa969d27`.

The separate Windows Health tab is removed. One `diagnostics.scan` reads the device checks, nine Windows evidence providers and optional WUA offers with a shared cancellation signal and operation log. Events/crashes appear in Scan & Fix, protection/services and confirmed CheckHealth in System tools, restart signals in Overview, and WUA history/support export in History & backups. Navigation reuses the completed snapshot and its timestamp. No donor executable or child application is shipped. Unknown providers do not become healthy, valid driver offers survive an evidence-provider failure, and cancellation retains the last completed snapshot. Global exports reduce nested evidence too, excluding event message bodies.

54 Node and 23 native Qt tests passed locally and on Windows. [Final source Windows build/install/portable](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42817615406), [final PR](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42817650396), [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42818514168), [publication attempt 2](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42818597131) and [actual native 6.3.0 → 6.3.1 upgrade](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42819311009) succeeded. Initial publication stopped before uploading assets when a draft-source update cleared its version tag; restoring `v6.3.1` resolved it. A prematurely dispatched upgrade run was cancelled before the successful final run. Published 6.3.0 bytes/tag remain unchanged.

Source artifact `13765422660`: SHA-256 `9abe7cef4d0db0577c23692874d9a75820aa9484ad29cd1259cdc59b36f515f1`. Original digest and ZIP CRC verified. Installed/portable/reopened Qt apps provided nine actual terminal provider receipts in the same diagnostics trace and reused that snapshot across four existing pages. Reduced exports omitted event-message fields. CPU/hardware checks, real cleanup/restore, portable data isolation and locked executable replacement also passed. Both EXEs contain all seven original icon sizes.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| Setup | 94,196,263 | `82b02c07f00500f3b97279ab86839a56e567fb3f5b348761a3cd80b7c6aba755` |
| Portable | 94,072,699 | `37789dd3ef7631e90bac7f518d78785d0257e958e639db66ea84c5a0505ab638` |

Upgrade artifact `13766203321`: SHA-256 `d7a7245c076e7e37db46857baef2e8f4ba04450eb267c4bebd32e5e328a355c1`; ZIP CRC and receipts verified. Native UI Automation invoked Check for updates, Update and restart and Continue in the actual 6.3.0 app. Installed payload hash, registry version and running Qt version matched 6.3.1. English/dark/135% UI/125% text/OpenDyslexic, original cleanup/restore history and milestones survived. The upgraded app ran the unified scan and all four integrated pages.

Real runner screenshots: [Scan & Fix](screenshots/WinOptimizer-6.3.1-Tarama.png), [System tools](screenshots/WinOptimizer-6.3.1-Sistem-Araclari.png), [Overview](screenshots/WinOptimizer-6.3.1-Genel-Bakis.png), [History](screenshots/WinOptimizer-6.3.1-Gecmis.png). These show the test machine, not the user's PC. [Private Drive release backup](https://drive.google.com/drive/folders/1qNgH2ZW8lLDOLNbdxSttkmlXC8u8xYM_) includes source, reachable Git history, both complete EXEs and evidence; actual readbacks are checked by size/hash, ZIP CRC and Git bundle verification. Signing keys are excluded.

## 6.3.0 SysMender donor adaptation

Application/tag source `e102bcac9bd50932c07d6e8c1981fa041338c830`, PR #10, merge `c4f5e5e1f9b9dca07ebea4b3518864ce21534cb1`. [v6.3.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.3.0) is a preserved stable release. [Source Windows](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42811034065), [PR](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42811230024), [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42812621830), [publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42812646149) and [actual native 6.2.0 → 6.3.0 upgrade](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42812826451) passed.

50 Node and 22 native Qt checks passed, including unelevated/local evidence requests, ignored injected flags, separate confirmed read-only elevation, support-export allowlists, retained filters, unknown/empty states, actual category-receipt progress and confirmation cancellation. Windows PowerShell 5.1 parsed the new backend and read actual readiness/service evidence; the administrator recorded-component check returned a recognized DISM state. It does not certify a full DISM/SFC scan or repair.

Both installed and portable native apps read all nine care categories and exported reduced evidence with no event-message fields. The runner provided readiness, Defender, all three firewall profiles, System/Application events, local update history and selected services; crash and dump lists correctly returned no matching records. Actual clipboard summaries and installed/portable data isolation/reopening passed. The existing real locked-executable replacement check also passed. [Turkish Windows Health view](screenshots/WinOptimizer-6.3.0-Windows-Sagligi.png) shows the runner, not the user's PC.

Source artifact `13762945439`: SHA-256 `c3193b12bcaf6612f537777eba11dbd12ab2ebe63ad61a49527f85b742c9b962`; original digest and ZIP CRC verified. The embedded-key Ed25519 manifest, all five published sizes/digests and seven original icon payloads in both EXEs were verified. SysMender/WinUtil full MIT notices are bundled; [donor provenance and exact scope](SYSMENDER-DONOR.md) identifies the pinned source and distinguishes transferred functionality from candidates not implemented.

| Package | Bytes | SHA-256 |
| --- | --- | --- |
| Setup | 94,189,573 | `e09ace7bbc7fdd18a5b1bbdc37be3c3eb3ccf0ba1553f86dc6009a369e47ae74` |
| Portable | 94,065,931 | `bd610799a6b5b9d5b3e503c6bce4fd25de6beea9517472e1ef15316c9b72f952` |

Upgrade artifact `13764056243`: SHA-256 `76ceb8d5e2065c9d2a90102e6ca516f867153ea88656ed4fa28a861ba3b2b2eb`; ZIP CRC and receipts checked. Native UI Automation invoked the baseline app's update flow. Installed payload SHA-256, registration 6.3.0 and actual running version 6.3.0 matched; English/dark/135% UI/125% text/OpenDyslexic, original cleanup/restore history and milestones were preserved. The updated app then ran the new care scan and reduced export.

Limits: hosted Windows VM/provider coverage, not every physical machine or policy. Read success and historical events are not proof of overall health or root cause. Primary care scanning does not change Windows protection/services or request elevation; only the separate recorded-state read requests administrator approval and may write Windows' diagnostic log. No full repair, donor binary/Linux port, global OEM driver database or all-66-tool parity is claimed. Portable updates remain manual replacement beside Data; installer Authenticode remains unavailable. In-app installer authentication remains Ed25519 metadata plus SHA-256.

Private Drive source/history and whole Setup/Portable readbacks passed size/hash, ZIP CRC and Git-bundle checks; final documentation/evidence and the cumulative private receipt preserve earlier records. No private signing key was uploaded.


## 6.2.0 Native update replacement and readable results

Application/tag source `fc60edaed7aa75ae78b3deaac8ddccb20179248c`, PR #9, merge `9dba27a974fc8926b09de27db0a0348a80032048`. [Release v6.2.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.2.0) is stable/latest. [Source Windows](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42777535853), [PR](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42777542808), [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42778260279), [immutable publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42778350270) and [actual native 6.1.0 → 6.2.0 upgrade](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42778713731) passed.

47 Node and 18 native Qt checks passed, covering preserved hardware search, clipboard/UTF-8 report output, unknown data, real-receipt category progress, collapsed log visibility/counts, saved preferences, clean installer handoff and launch failure recovery. Real installed and portable packages read fourteen categories, copied the actual Windows inventory summary and formatted the full text report. Portable reopening and data isolation passed. The package scan rejects browser-engine payloads; the GUI remains Python/Qt Widgets with headless Node/PowerShell. [Turkish compact Windows view](screenshots/WinOptimizer-6.2.0-Windows-Donanim.png) shows the test VM's hardware.

The old native update negative control [6.0.0 → 6.1.0](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42776288899) reached the real confirmation through Windows UI Automation, then exposed registration 6.1.0 with the unchanged 6.0.0 executable hash. It is a failing historical pair, not a certified upgrade. The new installer stages the complete new payload and retries atomic MoveFileEx replacement while the old executable remains locked. Registration and restart follow successful replacement; failures leave the old executable. Installer/client handoffs request a fresh onefile environment. A real Windows test holds the installed EXE open without delete sharing, verifies the installer waits, releases the lock, and verifies the exact new payload with no leftover staging file.

The successful 6.1.0 → 6.2.0 run invokes Settings, Updates, Check for updates, Update and restart, and Continue on the installed native app. It checks the installed EXE against the published portable SHA-256, registration 6.2.0, and actual running application 6.2.0. English, dark theme, 135% UI, 125% text, OpenDyslexic, cleanup/restore history and milestones were preserved. Upgrade artifact `13744404860`: SHA-256 `57d0dd43d8015d5a815c0c2ec098748eda40ac70aba02eea063e4b2a31a483c9`; ZIP CRC and actual receipts verified.

Source artifact `13745030924`: SHA-256 `27848a4251b47a54feaa0f70e76a414895b671efe824262ee7b0b764ed991b32`; original digest and ZIP CRC verified. Embedded-key Ed25519 metadata, all five published asset sizes/digests, and all seven original icon payloads at 16/24/32/48/64/128/256 pixels in both EXEs were checked.

| Package | Bytes | SHA-256 |
| --- | --- | --- |
| Setup | 94,171,235 | `e24f9ab650e54a46acbe8bf688ddb4cf642773015625ce9a186ee768d1f5b2e4` |
| Portable | 94,046,497 | `c57f9356d28ca451c4b277574e79c92a3175b8708c893ff679d9f0db105c407f` |

Hardware percentage is processed category work, not a health score. Missing values/providers and unknown operation totals remain explicit. Physical GPU/provider combinations and all disk/filesystem failures are not exhaustively certified; [hardware scope](HARDWARE.md) applies. Portable updates remain manual replacement beside Data; installer Authenticode signing remains unavailable. In-app installer updates authenticate Ed25519 metadata plus SHA-256.

Source/history and whole Setup/Portable private Drive readbacks passed size/hash, ZIP CRC and Git-bundle checks. Final evidence and the cumulative private receipt retain previous records. Private signing keys are excluded.


## 6.1.0 Hardware and front-facing Aion

Application/tag source `350a93c4751d283a57cca72fe95077d5028e7786`, merged through PR #8. 46 Node checks and 12 native Qt checks passed. [Source Windows build](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42745105796), [PR](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42745111433), [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42745759295), [immutable publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42745776245) and [installed 5.3.0 → 6.1.0 upgrade](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42745955196) succeeded. Release [v6.1.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.1.0) is stable/latest; prior 6.0.1 angled-icon preview remains a historical prerelease.

Actual Windows PowerShell 5.1 parsed the inventory and compiled the DXGI C# helper. Both installed and portable packages scanned fourteen categories through their native Qt Hardware tab and recorded actual category completion events. The runner reported system, CPU, GPU, memory/arrays, motherboard, BIOS, storage/volumes, display, network and PnP devices; audio and battery correctly reported no devices. Reopening, installed/portable data isolation, real cleanup/restore and official Microsoft runtime checks passed. [Turkish 100% view](screenshots/WinOptimizer-6.1.0-Windows-Donanim.png) shows the Windows runner's hardware, not the user's computer.

UI/service fixtures check a 12 GiB dedicated GPU value, unknown fallback VRAM, DDR5, category/search behavior, missing providers versus absent devices, read-only unelevated invocation, retained session results and export without rescanning. DXGI fields are uint64; the Windows VM supplied values above 4 GiB for shared memory. A physical GPU with more than 4 GiB dedicated VRAM was not separately exercised. [Hardware sources and limitations](HARDWARE.md) describe unsupported sensors/PSU information and firmware-provided values.

Final source artifact `13731436656`: SHA-256 `a0a1f33c2d06737d9bef3b4ebae3fbfa1ff76fc950b9edb6f4818691232b53a4`. Original artifact SHA-256/ZIP CRC and embedded-key Ed25519 metadata were verified. All five published asset sizes/digests match the source build. Both PE files contain all seven original front-facing icon payloads at 16/24/32/48/64/128/256 pixels.

| Package | Bytes | SHA-256 |
| --- | --- | --- |
| Setup | 94,160,972 | `fdf23af1e99e1f618a49b4e8d0aa2b67c5003c18c2971d49309b822365c8c9a9` |
| Portable | 94,037,141 | `79227d0401dcd571ce6e9b27dca0c0e6be439e0dbe3a7a157173358bad2387bc` |

Downloaded upgrade evidence `13731322441` passed SHA-256 `aed80b06c4ba1e73b2ac1681f32039acfa302c4689817f7b12f48ce46b7f779e` and ZIP CRC. It verifies version 6.1.0, English/dark/135% UI/125% text/OpenDyslexic, original cleanup/restore events and milestones. This is the tested 5.3.0 migration pair; no separate 6.0.0 → 6.1.0 in-app pair was certified. Installer Authenticode signing remains unavailable; authenticated in-app updates use Ed25519 metadata and SHA-256. Portable updates remain manual EXE replacement beside Data.

Private Drive backup readbacks for source ZIPs, all-history Git bundles and whole Setup/Portable files passed size/SHA-256, ZIP CRC and Git-bundle checks. No private signing key was uploaded. The canonical private receipt retains previous verification records and records the new source/package evidence.


Production release: [6.0.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.0.0). Production application source/tag: `d5090af906b313eb8e63160c354bda54f7edda6b`. Earlier evidence is retained below.

## 6.0.0 native Windows GUI

45 Node/backend tests and 10 native PySide6/Qt UI tests passed. The interface is Qt Widgets/QPainter, not a browser surface. The packaged application includes CPython and a SHA-pinned official Node24.22.1 runtime; no separately installed Python/Node/browser is required. PyInstaller archive entries were checked for Electron, Chromium and Qt WebEngine payloads and none were present. Previous Chromium UI tests describe earlier versions, not the 6.x native UI.

[Source build/install](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42736382969), [PR validation](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42736390974), [merge](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42737067232) and [publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42737192913) succeeded. The opt-in packaged Qt UI self-test used the real native entry, clicked its controls, ran actual Windows health and local diagnostic inventory, moved/restored a real aged Temp file and reopened the portable executable. Portable settings were beside its EXE and installed settings remained byte-identical. These are hosted Windows VM/internal UI self-test results; they are not a claim of exhaustive physical hardware or external UI Automation certification.

[Installed 5.3.0 → 6.0.0 migration](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42737857096) passed: the old app's update button downloaded/authenticated/ran the new Setup; the native app reopened; English/dark/135% UI/125% text/OpenDyslexic remained. The original cleanup and restore events and health/scan milestones remained. Exported receipts were downloaded with artifact SHA-256 and ZIP CRC checks, and their exact version/settings/history assertions were reread. A previous successful migration run was extended with a test-only history check; published binaries were not changed.

Native UI fixtures verify bilingual Update all without individual checkboxes, confirmation/cancel, 24 offers, partial failures, native navigation, independent large appearance settings, explicit local scan/skip reasons, retained chronological export and latest-state display, per-driver outcomes with identical titles, portable update separation and primary-action visibility. Backend tests cover 32-item hash-pinned plans, ignored/firmware exclusion, cleanup protections and native progress line delivery. The PowerShell5.1 integration tests read actual progress events and reject tampered plans before Windows Update mutation. Driver installation failures and large offer lists use controlled fixtures; no device was deliberately damaged.

Setup: 93,478,533 bytes, SHA-256 `532a90c7932b4ad1a3b654aa5e7cea28d3a41c5328e2e1c23e262488ed98f1be`. Portable: 93,426,145 bytes, SHA-256 `4ed4e7e047e0096fb0f6f71dff08ea51c1b4be24558f46014ae616a27b4c0bf7`. Both signed-manifest descriptors and all five GitHub release asset digests matched before/after publication. Whole Setup/Portable files, source ZIPs and Git bundles were downloaded from private Drive and compared byte-for-byte; ZIP CRC and Git bundle verification passed. Private signing keys were excluded.

Authenticode remains unavailable. Portable updates currently use manual browser download/file replacement and are not an automatically verified self-update. The installed migration test crosses from 5.3 to native6; a future native6-to-native6 update pair does not yet exist. Full original CLI/Driver Booster parity is not claimed; see [legacy coverage](LEGACY-COVERAGE.md) and [driver coverage](DRIVER-COVERAGE.md). Actual native Windows screenshots are in [screenshots](screenshots/).

## 5.3.0 interactive companion and 5.2 workshop

36 Node tests and 17 Chromium scenarios passed. Coverage includes pointer directions/dead zone, four petting zones, keyboard activation, persisted independent settings, reduced motion, disabled/offscreen behavior, scan-result pointer following, 150% mascot with 200% narrow UI, and firmware exclusion. Workshop tests cover signed local package inspection, one-use plans and changed files, selected updates and exact ignores, bounded imports, Microsoft runtime publisher/hash verification, absent-device rechecks and conflict-aware focus restoration. Production dependency audit reported zero vulnerabilities at validation time.

[Source Windows build/install](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42725411279), [PR validation](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42725419940), [main merge](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42726497251) and [immutable publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42726582946) succeeded. Artifact SHA-256 and ZIP CRC, embedded-key Ed25519 signature, source commit and all four published asset digests were checked. Installer: 134,466,232 bytes; SHA-256 `c2635bf1980b0def3a612b40ecf25597213366138c30580dc922f815a28f185b`.

[Real installed 5.2.0 → 5.3.0 update](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42726691878) passed using the app's update button. English, dark theme, 135% UI, 125% text, OpenDyslexic and existing activity remained. The installed app passed scan and pointer/petting checks; its Turkish light/dark/scan/workshop/pointer/petting screenshots are in [screenshots](screenshots/). VM values in screenshots describe that runner.

5.2 source [42721023776](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42721023776) passed real official Microsoft DirectX download, publisher validation, installation and installed-indicator postcheck. [5.1.0 → 5.2.0 update](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42722973347) preserved settings/history. An earlier screenshot helper expected a stale button label; the test-only fix was rerun successfully without changing published binaries.

Private Drive source/history/release readbacks passed byte/hash, ZIP CRC and Git-bundle verification. The downloaded helper reconstructed the original 5.3.0 installer from downloaded parts with the exact SHA-256 above. No private signing key was included. Physical hardware permutations, all driver classes and OEM catalogs are not exhaustively certified. The application has no independent global/OEM catalog or Authenticode certificate; see [coverage](DRIVER-COVERAGE.md) and [catalog](DRIVER-CATALOG.md).

## Earlier 5.0.1 evidence

| Evidence | Result |
| --- | --- |
| Node security/data checks | 11 passed: scoped cleanup, personal/recent-file protection, link/traversal rejection, changed files, one-use plans, restore conflicts, actual purge bytes, settings persistence/independence, milestone deduplication, non-executable imports, shell payload isolation, signature/platform/channel/URL/hash checks, corrupt/interrupted downloads, partial-result classification. |
| Real Chromium UI | 6 passed: bilingual state, invalid scale/reset, narrow 200% with 125% text/OpenDyslexic/high contrast, keyboard, reduced motion, disable journey/companion, source-frame animation, and partial-driver failure feedback/history. Partial driver results are explicit UI fixtures, not deliberate hardware damage. |
| TypeScript/Vite | Production build passed. Production dependency audit: zero vulnerabilities at validation time. |
| Fonts | Regular and bold cmap include Ç Ğ İ Ö Ş Ü ç ğ ı ö ş ü; actual bundled font loaded in Chromium. Original OTF/OFL files retained, no runtime font download. |
| [Windows build/install](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42687275191) | PS 5.1 parse and real system inventory, driver export/hash verification, reversible HKCU fixture, real Setup.exe install, actual installed cleanup/restore, driver inventory and persisted appearance passed. |
| [Windows final UI coverage](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42688246954) | All checks passed, including all 6 browser scenarios. Application code unchanged from the production source; metadata and UI regression coverage were added. |
| [5.0.0 → 5.0.1 installed update](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42688518853) | Real old package installed, real sample data created, Settings → Updates used, signed metadata/hash verified, app restarted, version 5.0.1 and language/dark theme/135% scale/125% text/OpenDyslexic/activity preserved. |
| [Earlier baseline → 5.0.0](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42684849845) | Earlier pair independently passed. |
| [Publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42688251498) | Original artifact SHA-256/ZIP CRC, manifest Ed25519 signature, source commit, architecture, size and installer hash verified before immutable upload. |
| Drive readback | Source ZIP CRC and Git bundle verification passed after downloading actual stored bytes. All installer backup parts were downloaded, hashed and recombined to the exact original package SHA-256. Private project ownership/sharing re-read. |

Installer bytes: 128250297. SHA-256: `9e687a2a8776de50c29350483c01b708c962ea2da8b758998d0c6a08e9b83d65`.

Limits: hosted Windows VM coverage, not every physical Windows 10/11 device. No BIOS/firmware updater or complete system-image backup. No Windows Authenticode certificate. Update authentication is Ed25519-authenticated metadata plus SHA-256. Browser preview is explicitly labelled and cannot execute Windows operations or fabricate device data. Offline local flows do not make update availability claims; physical network-disconnection scenarios were not separately certified.


## 5.1.0 Scan & Fix

19 Node tests and 8 Chromium scenarios passed, including expired/forged repair plans, changed/disabled targets, partial/unverified outcomes, explicit confirmation, manual-guidance labeling, retained scan results and 200% narrow layouts. Production npm audit: zero findings. Local PowerShell parsing and real Windows PowerShell 5.1 inventory passed.

Source [42707694779](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42707694779), PR [42707734459](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42707734459), main [42708567170](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42708567170) and publication [42708918343](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42708918343) succeeded. The installed app read real devices/services/network/display/runtime data with no unavailable providers on the Windows runner. This is VM evidence, not universal hardware coverage. Repairs were not tested by deliberately damaging devices; before/after failure paths use controlled fixtures.

[Installed 5.0.1 → 5.1.0 upgrade](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42709194171) verified version 5.1.0, dark theme, English, 135% interface, 125% text, OpenDyslexic and existing history. The updated installed application ran Scan & Fix again. Downloaded artifact digests and ZIP CRCs were checked; Drive parts were downloaded, hashed and reconstructed using the supplied PowerShell helper to the original installer SHA-256.

Tagged source: `5d696ccbdbd7d4eaee8dfa0041fcf744507c05ed`; installer 128,258,942 bytes, SHA-256 `b4898218d8203460abc8e5585659508503a367cd030fb693be404e06ce5d40aa`. Authenticode remains unsigned; in-app updates verify Ed25519 metadata and the package hash. Exact scan/repair limits are in [SCAN-FIX.md](SCAN-FIX.md).
