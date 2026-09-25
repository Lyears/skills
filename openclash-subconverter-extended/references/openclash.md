# OpenClash configuration and Provider diagnosis

## One combined subscription configuration

In **OpenClash → 配置订阅**, create or edit one subscription item. Put each service provider's **original subscription URL** in its `订阅 URL` field, one per line; `|` is an alternative delimiter. Adding separate OpenClash items creates separate generated configurations, not one combined configuration. Do not put the local converter URL among the source subscriptions.

For the tested router, enable **高级选项 → 在线订阅转换**, select **自定义** for the service address, and set `http://127.0.0.1:25500/sub`. Select **Aethersailor 规则 标准版 Custom_Clash** as the template. Leave optional switches at their defaults unless the subscription or traffic needs them: Emoji changes names; UDP support depends on nodes and use; do not skip certificate validation to paper over a fetch error. Save, update this subscription item, and select the generated YAML as the active OpenClash configuration. Keep the previously working configuration for rollback.

The [Aethersailor setup guide](https://github.com/Aethersailor/Custom_OpenClash_Rules/wiki/OpenClash-%E8%AE%BE%E7%BD%AE%E6%96%B9%E6%A1%88) documents the multiline field and template choices. Confirm actual labels against the installed OpenClash version.

## What `Provider_...` means

In the normal `target=clash` remote-subscription mode, SubConverter-Extended generates `proxy-providers` entries, one for each remote source. A generated name such as `Provider_XXXXXX` is a **collection of nodes from one source**, not a node or converter endpoint. Mihomo then downloads each Provider URL and updates it independently. The default generated Provider may specify `proxy: DIRECT`; the converter's own reachability does not determine that later fetch path. [Upstream behavior](https://github.com/Aethersailor/SubConverter-Extended/wiki/Remote-Subscriptions)

After updating, check the generated YAML for every expected `proxy-providers` entry and check the running Mihomo/OpenClash Provider view for nonzero node counts. Verify the strategy groups reference the Providers. A previously successful node count is only a historical observation, not a guarantee that the next fetch will work.

If a Provider is empty, test **that Provider's original source URL from the router** using the same User-Agent configured in OpenClash. Check HTTP status, response type, proxy route, and whether the body actually contains proxies; redact the URL/token in saved logs. A successful configuration download can coexist with an empty Provider. In the documented case, direct TLS timeouts to the source and a separate public backend's 502 did not prove that the public SubConverter-Extended instance generated empty nodes. Compare the generated Provider URL and its fetch result before assigning cause.

Use `list=true` only when its documented server-side parsing behavior is wanted and verified for the source format. It changes the normal Provider flow and failed with HTTP 400 during this router's earlier test. Multiple subscription URLs alone do not require it.

## Version check failure in the tested OpenClash build

OpenClash `0.47.156-r8` on this router once showed “无法检测后端版本” although `/healthz` worked. Its LuCI version-check handler returned HTTP 500 because six calls used undefined `util.shellquote` while the imported module was `UTIL`. The local fix backed up `/usr/lib/lua/luci/controller/openclash.lua`, changed only those six calls to `UTIL.shellquote`, verified Lua syntax, and retested the API. Apply such a fix **only after** confirming the same source-level fault in the installed build; upgrades may replace it or upstream may fix it. A green version label proves only that detection works, not that subscription or Provider downloads succeed.
