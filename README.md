# Skills

这里收集可复用的 Codex skills。每个 skill 直接放在仓库根目录，包含自己的 `SKILL.md`；后续会继续添加。

| Skill | 用途 |
| --- | --- |
| [openclash-subconverter-extended](openclash-subconverter-extended/SKILL.md) | 在 OpenWrt/Kwrt 上安装和排查 SubConverter-Extended，并配置 OpenClash 的本地订阅转换与 Mihomo Proxy Provider。 |

## 在 Codex 中使用

```sh
git clone https://github.com/Lyears/skills.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$(pwd)/skills/openclash-subconverter-extended" \
  "${CODEX_HOME:-$HOME/.codex}/skills/openclash-subconverter-extended"
```

重启或新开 Codex 任务后，即可按名称使用 `openclash-subconverter-extended`。仓库中的参考案例包含特定版本和架构的操作记录；在其他设备上执行前，应先按 skill 检查固件、包管理器和上游发布版本。

本仓库不包含上游 APK/IPK 安装包或私人订阅链接。SubConverter-Extended、OpenClash 和 luci-app-run 属于各自维护者，遵循各自的许可证。本仓库原创的 skill 文档与辅助脚本采用 [MIT License](LICENSE)。
