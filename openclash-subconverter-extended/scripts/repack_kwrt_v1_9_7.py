#!/usr/bin/env python3
"""Repackage the verified v1.9.7 x86_64 APK payload for an opkg-based Kwrt."""

import argparse
import atexit
import hashlib
import io
import json
import pathlib
import shutil
import tarfile
import tempfile


APK_SHA256 = "bc009fbd1a94b75a35b8f9693a05ebe5378de6ab5e0fa4a516c2c64bf2af970d"

EXCLUDE = {
    "etc/init.d/subconverter-extended-updater",
    "usr/libexec/subconverter-extended-update",
    "www/luci-static/resources/view/subconverter_extended/update.js",
}


def write(path, content, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(mode)


def make_tar(root):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz", format=tarfile.USTAR_FORMAT) as archive:
        for path in sorted(root.rglob("*")):
            relative = path.relative_to(root)
            archive.add(path, arcname="./" + str(relative), recursive=False)
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=pathlib.Path, required=True,
                        help="Original upstream v1.9.7 OpenWrt x86_64 APK")
    parser.add_argument("--extracted-tar", type=pathlib.Path, required=True,
                        help="Tar.gz of the tree produced by apk extract")
    parser.add_argument("--output", type=pathlib.Path, required=True,
                        help="Destination IPK; must not already exist")
    args = parser.parse_args()

    hasher = hashlib.sha256()
    with args.apk.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hasher.update(chunk)
    digest = hasher.hexdigest()
    if digest != APK_SHA256:
        raise ValueError(f"Unexpected APK SHA-256: {digest}")
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")

    stage = pathlib.Path(tempfile.mkdtemp(prefix="subconverter-ipk-"))
    atexit.register(shutil.rmtree, stage, ignore_errors=True)
    data = stage / "data"
    control_dir = stage / "control"
    data.mkdir()
    control_dir.mkdir()

    with tarfile.open(args.extracted_tar, "r:gz") as source:
        package_files = source.extractfile(
            "./lib/apk/packages/subconverter-extended.list"
        ).read().decode().splitlines()
        members = {m.name.removeprefix("./"): m for m in source.getmembers()}
        for raw_name in package_files:
            name = raw_name.removeprefix("/")
            if not name or name in EXCLUDE or name.startswith("lib/apk/packages/"):
                continue
            if name.startswith("/") or ".." in pathlib.PurePosixPath(name).parts:
                raise ValueError(f"Unsafe package path: {name}")
            member = members.get(name)
            if not member or not member.isfile():
                raise ValueError(f"Missing regular package file: {name}")
            target = data / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.extractfile(member).read())
            target.chmod(member.mode)

    config = data / "etc/config/subconverter-extended"
    original = config.read_text()
    updated = original.replace("option listen_address ''", "option listen_address '127.0.0.1'")
    updated = updated.replace("option enabled '1'", "option enabled '0'")
    if updated == original:
        raise ValueError("Expected default UCI options were not found")
    write(config, updated)

    defaults = """#!/bin/sh
set -e
PACKAGE=subconverter-extended
uci -q get "$PACKAGE.service" >/dev/null || uci set "$PACKAGE.service=service"
uci -q get "$PACKAGE.service.config_file" >/dev/null || \\
    uci set "$PACKAGE.service.config_file=/etc/subconverter/pref.toml"
uci -q get "$PACKAGE.service.listen_address" >/dev/null || \\
    uci set "$PACKAGE.service.listen_address=127.0.0.1"
uci commit "$PACKAGE"
mkdir -p /etc/subconverter /tmp/subconverter-extended/cache
[ -e /etc/subconverter/base ] || [ -L /etc/subconverter/base ] || \\
    ln -s /opt/subconverter-extended/base/base /etc/subconverter/base
[ -e /etc/subconverter/snippets ] || [ -L /etc/subconverter/snippets ] || \\
    ln -s /opt/subconverter-extended/base/snippets /etc/subconverter/snippets
[ -e /etc/subconverter/cache ] || [ -L /etc/subconverter/cache ] || \\
    ln -s /tmp/subconverter-extended/cache /etc/subconverter/cache
"""
    write(data / "etc/uci-defaults/90_subconverter-extended", defaults, 0o755)

    menu_path = data / "usr/share/luci/menu.d/luci-app-subconverter-extended.json"
    menu = json.loads(menu_path.read_text())
    menu.pop("admin/services/subconverter-extended/update")
    write(menu_path, json.dumps(menu, ensure_ascii=False, indent=2) + "\n")

    acl_path = data / "usr/share/rpcd/acl.d/luci-app-subconverter-extended.json"
    acl = json.loads(acl_path.read_text())
    acl["luci-app-subconverter-extended"]["write"]["ubus"]["luci.subconverter_extended"] = [
        "service_action"
    ]
    write(acl_path, json.dumps(acl, ensure_ascii=False, indent=2) + "\n")

    readme = """SubConverter-Extended v1.9.7 for this opkg-based Kwrt router

Unofficial repack of the upstream x86_64 OpenWrt APK payload.
Upstream APK SHA-256: bc009fbd1a94b75a35b8f9693a05ebe5378de6ab5e0fa4a516c2c64bf2af970d
Source: https://github.com/Aethersailor/SubConverter-Extended/releases/tag/v1.9.7

The upstream APK updater is omitted because this firmware uses opkg, not an
initialized apk database. Update by installing a new opkg package. The service
listens on 127.0.0.1:25500 by default and is managed with:
  /etc/init.d/subconverter-extended {start|stop|restart|enable|disable}
"""
    write(data / "usr/share/doc/subconverter-extended/README.OpenWrt", readme)

    size = sum(p.stat().st_size for p in data.rglob("*") if p.is_file())
    control = f"""Package: subconverter-extended
Version: 1.9.7-r0kwrt1
Architecture: x86_64
Maintainer: Aethersailor (upstream); local opkg repack
Section: net
Priority: optional
Depends: ca-bundle, curl, jsonfilter, luci-base
Source: https://github.com/Aethersailor/SubConverter-Extended
License: GPL-3.0-only
Installed-Size: {size}
Description: SubConverter-Extended v1.9.7 with LuCI for this opkg-based Kwrt router.
 Repacked from the verified upstream OpenWrt APK; upstream APK updater omitted.
"""
    write(control_dir / "control", control)
    write(control_dir / "conffiles", "/etc/config/subconverter-extended\n")
    postinst = """#!/bin/sh
set -e
[ -n "$IPKG_INSTROOT" ] && exit 0
pkgname=subconverter-extended
. /lib/functions.sh
default_postinst
/etc/init.d/rpcd reload >/dev/null 2>&1 || true
"""
    write(control_dir / "postinst", postinst, 0o755)
    prerm = """#!/bin/sh
[ -n "$IPKG_INSTROOT" ] && exit 0
/etc/init.d/subconverter-extended stop >/dev/null 2>&1 || true
/etc/init.d/subconverter-extended disable >/dev/null 2>&1 || true
exit 0
"""
    write(control_dir / "prerm", prerm, 0o755)
    postrm = """#!/bin/sh
rm -f /tmp/luci-indexcache /tmp/luci-indexcache.*
[ -n "$IPKG_INSTROOT" ] || /etc/init.d/rpcd reload >/dev/null 2>&1 || true
exit 0
"""
    write(control_dir / "postrm", postrm, 0o755)

    data_archive = make_tar(data)
    control_archive = make_tar(control_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.output, "w:gz", format=tarfile.USTAR_FORMAT) as package:
        for name, content in (
            ("debian-binary", b"2.0\n"),
            ("data.tar.gz", data_archive),
            ("control.tar.gz", control_archive),
        ):
            info = tarfile.TarInfo("./" + name)
            info.mode = 0o644
            info.size = len(content)
            package.addfile(info, io.BytesIO(content))
    print(args.output)
    print(f"Package size: {args.output.stat().st_size} bytes; installed size: {size} bytes")


if __name__ == "__main__":
    main()
