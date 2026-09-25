# Installation and the tested Kwrt case

## Decide from the actual package manager

On the router, inspect `uname -m`, `/etc/openwrt_release`, `opkg list-installed`, `apk info`, the installed-package database, and `df -h /overlay`. Also check whether OpenClash already runs and whether `127.0.0.1:25500` is occupied. Presence of `/usr/bin/apk` alone is insufficient: the tested Kwrt firmware still marked `opkg` as Essential and had no initialized APK database.

- **APK-managed firmware:** fetch the official OpenWrt APK matching the architecture, verify the release checksum, and follow the [upstream native deployment guide](https://github.com/Aethersailor/SubConverter-Extended/wiki/Native-Deployment). Check current release names and dependencies first.
- **opkg-managed firmware:** use a compatible IPK. Do not run `apk add --initdb` against the live root just to make the upstream APK install: that creates a second package database unaware of opkg ownership. `luci-app-run` is an upload/install interface, not a remedy for this mismatch.

## Verified case: Kwrt x86_64, 2026-09-25

This router used `opkg`, despite a Kwrt 25.12 label. The installed version was SubConverter-Extended **v1.9.7-75d118d**, packaged as a local `1.9.7-r0kwrt1` IPK. The upstream `SubConverter-Extended-v1.9.7-openwrt-x86_64.apk` SHA-256 was `bc009fbd1a94b75a35b8f9693a05ebe5378de6ab5e0fa4a516c2c64bf2af970d`. This hash applies only to that exact release asset. A previously built IPK must not be assumed compatible with other firmware or architectures.

The successful sequence was:

1. Back up router configuration and the existing OpenClash YAML. Download the exact official APK and checksum file from its [release](https://github.com/Aethersailor/SubConverter-Extended/releases/tag/v1.9.7); verify SHA-256 before extraction.
2. Use `apk --allow-untrusted extract --destination /tmp/sc-apk-test <verified.apk>` on the router. This extracts into a temporary tree **without** initializing or mutating the live APK package database. Confirm the bundled binary and libraries run in isolation.
3. Archive that extracted tree and build an opkg IPK from only the files listed in `lib/apk/packages/subconverter-extended.list`. [The case-specific builder](../scripts/repack_kwrt_v1_9_7.py) verifies the original APK checksum, excludes APK database files and the upstream APK self-updater, sets the default listener to `127.0.0.1`, and assembles the IPK. Inspect its output and opkg metadata before installation. Re-evaluate its assumptions for a new upstream version.
4. Install the resulting IPK with `opkg install <file.ipk>` or the IPK upload path in [luci-app-run](https://github.com/wukongdaily/luci-app-run). The tested router used luci-app-run. Do not feed this IPK to `apk`.
5. Enable/start `/etc/init.d/subconverter-extended` and verify `wget -qO- http://127.0.0.1:25500/healthz` prints `ok`. Check that OpenClash still runs. The LuCI service page is under **Services → SubConverter-Extended**.

The repack omitted the upstream APK updater because it would try to manage an opkg-installed service through APK. Upgrade this installation with a newly reviewed IPK, not the omitted updater. The IPK carries an upstream-derived payload plus local packaging changes; it is not an official upstream IPK.

## Local default template used in this case

The converter initially failed to load its default remote template when `/sub` lacked an explicit `config` parameter. After backing up `/etc/subconverter/pref.toml`, the Aethersailor `Custom_Clash.ini` template was stored at `/etc/subconverter/Custom_Clash.ini`, and `default_external_config` in `pref.toml` was changed to that local path. Restart the service and retest `/healthz` and a conversion request. This fallback matters for requests without `config`; OpenClash may pass the selected template explicitly. Keep a backup so a failed template change can be rolled back.
