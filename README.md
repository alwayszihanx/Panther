# Panther Browser for Android

[![GitHub](https://img.shields.io/github/downloads/jqssun/android-helium-browser/total?label=GitHub&logo=GitHub)](https://github.com/jqssun/android-helium-browser/releases)
[![license](https://img.shields.io/badge/License-GPLv2-blue.svg)](https://github.com/jqssun/android-helium-browser/blob/main/LICENSE)
[![build](https://img.shields.io/github/actions/workflow/status/jqssun/android-helium-browser/build.yml)](https://github.com/jqssun/android-helium-browser/actions/workflows/build.yml)
[![release](https://img.shields.io/github/v/release/jqssun/android-helium-browser)](https://github.com/jqssun/android-helium-browser/releases)

<img alt="Panther Browser logo" src="res/logo.svg" width="160" />

A fully open-source, experimental Chromium-based web browser for Android with full
extensions support, built on top of:

- [Vanadium](https://github.com/GrapheneOS/Vanadium) by [GrapheneOS](https://github.com/GrapheneOS)
- [Helium](https://github.com/imputnet/helium) by [imput](https://github.com/imputnet) (downstream patches pending GPLv2 compatibility)

Application id: `io.alwayszihan.panther`

## Branding

- **Main app logo** — `res/logo.svg`. It is rasterized into every launcher icon density
  during the build (`res/icon.sh`), replacing the previous Vanadium/Helium-style icon.
- **Alternative logos** — `res/logo-2.svg` … `res/logo-10.svg`. These are the selectable
  app icons offered in the in-app **customization settings** (change app icon).
- **Themed icon** — `res/drawable/themed_app_icon.xml` is the monochrome vector used when
  Android "themed icons" are enabled.
- **Store assets** — `fastlane/.../images/icon.png` and `featureGraphic.png` are regenerated
  from `res/logo.svg` on every build.

## Features & Settings

All of the following are applied automatically by `patch.sh` at build time.

### Branding & identity
- App name set to **Panther** (overrides Chrome / Helium / Vanadium strings).
- Package name `io.alwayszihan.panther`.
- Custom launcher icon + themed icon generated from `res/logo.svg`.

### Extensions
- **Manifest V2 (MV2)** extensions are supported and not deprecated (`kExtensionManifestV2Unsupported`
  and `kExtensionManifestV2Disabled` disabled, MV2 testing allowed, Web Store MV2 deprecation set to `kNone`).
- `browser_action` / `page_action` API sources re-added so legacy MV2 extensions load.
- **Extensions toolbar** — a dedicated toolbar container + menu button is injected
  (`toolbar_phone.xml` ViewStub, `ToolbarTablet` cast removed, popup drawing wired).
- **Pin to toolbar** — extension popups can be pinned; the extensions menu button is hidden
  unless pinned.
- **Incognito (OTR) support for extensions** — `process_manager` forced and
  `shouldOpenIncognitoAsWindow()` returns `true`.
- **Extension priority** — extension host processes are marked `IMPORTANT`.
- **Install prompt fix** — permission prompts anchor to the correct parent window.
- **Bundled uBlock Origin** — force-installed from `extensions/ublock-origin/src` when present
  (ad / tracker / cookie / script blocking).

### Privacy & security
- **Fingerprinting protection enabled by default** (`kFingerprintingProtection` and
  `kFingerprintingProtectionForFeatures`).
- **WebRTC IP handling policy** available under *Settings › Privacy and security › WebRTC IP handling policy*.
- All [Vanadium](https://github.com/GrapheneOS/Vanadium) hardening patches are applied by default.
- Google API keys are stripped (`google_api_key` / `google_default_client_id` / secret set to `x`).

### Media & playback
- **Background play** — media keeps playing when the app is backgrounded
  (`MediaSessionImpl::OnSuspend` returns early for `kSystem` suspend).
- Proprietary codecs enabled (`ffmpeg_branding = "Chrome"`, `proprietary_codecs = true`,
  AV1 decoder enabled).

### UI / UX
- **Bottom address bar** (crbug.com/40831291 fix).
- **Developer menu & tools enabled** — `kSubmenusInAppMenu`, `kTaskManagerClank`,
  `kAndroidDevToolsFrontend`; developer entry always shown in the context menu and the
  overflow menu.
- **Site search** in Omnibox enabled (`kOmniboxSiteSearch`).
- **Custom search engines** — 32 privacy-friendly search engines (DuckDuckGo Lite,
  Brave, Startpage, Kagi, SearXNG, Mojeek, Wikiless, etc.) are prepended to
  Chromium's prepopulated list (`res/add_search_engines.py`), and **DuckDuckGo
  Lite (no-AI)** is set as the default search provider for every country.
- **Default homepage** set to `https://www.google.com` (New Tab Page homepage disabled).
- **Downloads from other apps** — handles the `VIEW_DOWNLOADS` intent.
- **Extension popup / card viewport fixes** — minimum popup size raised to `256×25`,
  responsive card and toolbar widths for the extensions page.
- **Overscroll** fix (crbug.com/525294822) on older Chromium versions.
- **Incognito UAF fixes** (crbug.com/431004500, crbug.com/40274462) via
  `HasLiveWebContentsForBrowserContext`.
- **API 31 profile** — `MIXED` profile type supported.

### Graphics
- Vulkan / ANGLE passthrough disabled in favor of a stable software/GL fallback
  (`kSkipVulkanBlocklist`, `kDefaultANGLEVulkan`, `kVulkanFromANGLE`,
  `kDefaultPassthroughCommandDecoder` removed; `kFallbackToSWIfGLES3NotSupported` disabled).

## Build configuration (`args.gn`)

| Option | Value | Purpose |
| --- | --- | --- |
| `chrome_public_manifest_package` | `io.alwayszihan.panther` | Application id |
| `is_desktop_android` | `true` | Desktop-class Android build |
| `target_cpu` | `arm` / `arm64` | Both ABIs are produced |
| `is_official_build` | `true` | Optimized release build |
| `symbol_level` | `1` | Limited symbols for crash reports |
| `proprietary_codecs` | `true` | H.264 / AAC etc. |
| `ffmpeg_branding` | `Chrome` | Proprietary FFmpeg |
| `enable_av1_decoder` / `enable_dav1d_decoder` | `true` | AV1 playback |
| `use_login_database_as_backend` | `true` | Local login database |
| `disable_fieldtrial_testing_config` | `true` | No field-trial config |
| `google_api_key` / `client_id` / `secret` | `x` | Keys stripped |

## Building

All releases are produced with [GitHub Actions](https://github.com/features/actions) on a
self-hosted runner (default) or `ubuntu-latest`. Builds are attested with
[`actions/attest-build-provenance`](https://github.com/actions/attest-build-provenance).

```shell
gh attestation verify *.apk -R jqssun/android-helium-browser
```

This repository ships the build scripts to compile on the latest Ubuntu (and likely other
Linux distributions). The pipeline:

1. Checks out submodules (`vanadium`, `helium`).
2. Fetches the matching Chromium tag from `chromium.googlesource.com`.
3. Applies the (rebranded) Vanadium patches and runs `patch.sh`.
4. Builds `chrome_public_apk` for `arm` and `arm64`, plus an `arm64` App Bundle (`.aab`).
5. Signs the APKs/AAB with the repo keystore and publishes a GitHub release.

To build via CI, fork the repository and supply your `base64`-encoded `keystore.jks`
(`LOCAL_TEST_JKS`) and `local.properties` (`STORE_TEST_JKS`, containing `keyAlias`,
`keyPassword`, `storePassword`) as **Repository secrets** under
*Settings › Secrets and variables › Actions*. Then go to **Actions › Build › Run workflow**
and choose the runner.

Build artifacts:

- `*-armeabi-v7a.apk`
- `*-arm64-v8a.apk`
- `*-arm64-v8a.aab`

## Credits

This project would not have been possible without the huge community contributions from
[Vanadium](https://github.com/GrapheneOS/Vanadium), [Helium](https://github.com/imputnet/helium),
[ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium), and various
other upstream projects. All credit goes to the original authors and contributors.
