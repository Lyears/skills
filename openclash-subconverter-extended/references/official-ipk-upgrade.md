# Official IPK upgrades with configuration preservation

## Tested upgrade and asset verification

On 2026-10-21, a Kwrt x86_64 router using opkg was upgraded from the local `1.9.7-r0kwrt1` repack to the official `1.10.4-r0` IPK. The installed converter, OpenClash configuration, local default template, and existing Provider collections were retained. This is a tested case; inspect package scripts and firmware dependencies again for a different release.

The [v1.10.4 release](https://github.com/Aethersailor/SubConverter-Extended/releases/tag/v1.10.4) supplies `SubConverter-Extended-v1.10.4-openwrt-x86_64.ipk` and `SHA256SUMS`. Its verified SHA-256 is `c0e481373ae0c4d1168846804ebb603f35f6beb998d79394e8c6fceb4c6af84d`, applicable only to that asset. Match `opkg print-architecture` before downloading. Verify the complete file against the upstream checksum; an interrupted download must not be installed. A resumed download or downloading directly on the router is sufficient when the original transfer fails and the final checksum matches.

## Capture configuration before installing

Create a private, uniquely named backup directory on the router. Archive the existing paths needed for this installation:

- `/etc/config/subconverter-extended` and `/etc/subconverter/`, including `pref.toml` and any local `Custom_Clash.ini`;
- `/etc/config/openclash`, the active subscription configuration, and existing Provider files;
- any relevant local OpenClash controller patch.

Save checksums of these configuration files, the installed package status, the converter's listener and autostart state, and the running Mihomo Provider names/counts. Keep real subscription URLs, API credentials, Provider snapshots, and backup archives out of the public skill repository. Record the archive's relative paths so restoration targets only the intended configuration.

## Check dependencies before using an exception

Inspect the official IPK's control metadata and maintainer scripts, then run `opkg --noaction install /tmp/<verified-package>.ipk`. Read the diagnostic output: on the tested firmware, this dry run returned exit code 0 while reporting an unsatisfied dependency. Check the resulting installed version and runtime separately after a real installation as well.

The v1.10.4 package declares `luci-base`, `luci-i18n-base-zh-cn`, `curl`, `jsonfilter`, and `ca-bundle`. In this Kwrt case, **only** `luci-i18n-base-zh-cn` was missing from opkg's package records. The Chinese translation was already installed as part of `luci-base`, confirmed by:

```sh
opkg search /usr/lib/lua/luci/i18n/base.zh-cn.lmo
```

The command reported `luci-base` as the owner, and the other dependencies were installed. With those facts established, the unchanged official IPK was installed using `opkg --force-depends install /tmp/<verified-package>.ipk`. This flag bypasses all dependency checks, so use it only when the sole missing dependency is this independently verified, already bundled translation. Install genuinely missing runtime dependencies normally; do not apply this workaround to missing libraries, utilities, or an unexamined set of dependencies. The original dependency declaration remains in opkg's database, so later package operations can still report the translation-package warning.

## Restore settings that package defaults replace

Do not assume that preserving `pref.toml` preserves the full service configuration. In the tested upgrade, opkg replaced the old UCI file with new package defaults because its previous contents had not been modified since installation. The converter then listened on `0.0.0.0:25500`, although `pref.toml` and the local template were unchanged. UCI listener values override preferences through the service environment.

After installation, immediately compare the saved configuration checksums and inspect `netstat -ltn` for port 25500. If the previous UCI settings were replaced, stop the converter, restore **only** `/etc/config/subconverter-extended` from the archive, and start it again. For an archive created relative to `/`, the tested restoration was:

```sh
/etc/init.d/subconverter-extended stop
tar -xzf "$backup_dir/configuration.tar.gz" -C / etc/config/subconverter-extended
/etc/init.d/subconverter-extended start
```

Restore the recorded autostart state as appropriate. The old UCI configuration worked unchanged with v1.10.4, including the `127.0.0.1` listener and disabled automatic updater. Recheck required migration fields for other versions. Restore configuration selectively rather than overwriting upgraded binaries or the entire installation.

## Verify conversion and the existing OpenClash runtime

Completion requires all of the following:

- opkg reports the expected installed version and the converter is running with its intended autostart state;
- `/healthz` returns `ok`, the listener is still `127.0.0.1:25500`, and saved configuration checksums match;
- a normal `target=clash&list=false` request returns HTTP 200 and valid YAML containing the expected Providers, groups, and rules;
- OpenClash is running with its original active configuration and each existing Provider remains nonempty.

For a conversion test, read source addresses from the matching OpenClash UCI `config_subscribe` section and write the result to a private temporary file. A file under `/etc/openclash/config/` can be encoded subscription text rather than a YAML mapping; the generated runtime file and UCI subscription settings are better sources when that occurs. Do not print URLs while extracting them. A test need not activate its output or restart OpenClash. The v1.10.4 case returned two Providers, 35 groups, and 46 rules, and both running Provider node counts remained unchanged; those counts are case observations, not template requirements.

`GET /version` returns an HTML page in v1.10.4. For a concise version check, inspect the `Server` header with `curl -fsSI http://127.0.0.1:25500/version` or read package/build metadata rather than dumping the page.

Keep the upgrade backup through these checks. When the user authorizes cleanup after a successful upgrade, delete only that upgrade's named backup directory and verify it is absent. Remove temporary subscription inputs, test output, downloaded packages, and temporary SSH helpers as applicable. Do not delete older or unrelated backups as part of this cleanup.
