---
name: openclash-subconverter-extended
description: Install or troubleshoot SubConverter-Extended on OpenWrt/Kwrt and connect it to OpenClash, including opkg/APK package mismatches and empty Mihomo Proxy Providers. Use for router subscription conversion work, not for unrelated Clash routing changes.
---

# OpenClash + SubConverter-Extended

Use this skill to make a router's subscription conversion reproducible and to distinguish conversion failures from Provider download failures. Preserve the user's chosen OpenClash configuration and subscription sources.

## Route the work

1. Inspect the router's architecture, firmware, **actual package database**, free storage, existing OpenClash configuration, and any running converter. An `apk` executable alone does not mean the firmware is APK-managed.
2. For installation or upgrades, read [installation.md](references/installation.md). Use the upstream package on a genuinely APK-managed system. The documented Kwrt x86_64 case uses an opkg-compatible repack of a verified upstream APK; never initialize a second APK database merely to install this service.
3. For OpenClash setup, multiple subscriptions, or empty nodes, read [openclash.md](references/openclash.md). Configure the backend and verify both the generated YAML and each Mihomo Provider separately.
4. Before changing a live router, capture the relevant configuration and a rollback path. After a change, verify service health, YAML validity, the active OpenClash configuration, and nonempty Provider node counts. Stop once those checks pass.

## Operational boundaries

- Treat subscription URLs and tokens as credentials. Do not print them in logs, commit them, or paste them into external conversion services unless the user chose that destination.
- A green backend version check or HTTP 200 from `/sub` does not prove the remote Provider fetched nodes. Each Provider may fetch its source directly using `proxy: DIRECT`.
- Keep a local backend bound to `127.0.0.1` unless the user explicitly needs another access path. For a remote browser, prefer an SSH tunnel over changing its listener.
- The 2026-09-25 Kwrt package and OpenClash Lua fix are **case records**, not universal instructions. Recheck upstream releases and local source before replaying either.

## Primary sources

- [SubConverter-Extended releases](https://github.com/Aethersailor/SubConverter-Extended/releases) and [native deployment](https://github.com/Aethersailor/SubConverter-Extended/wiki/Native-Deployment)
- [Mihomo remote subscription / Proxy Provider behavior](https://github.com/Aethersailor/SubConverter-Extended/wiki/Remote-Subscriptions)
- [Aethersailor OpenClash setup](https://github.com/Aethersailor/Custom_OpenClash_Rules/wiki/OpenClash-%E8%AE%BE%E7%BD%AE%E6%96%B9%E6%A1%88)
