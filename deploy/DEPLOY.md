# 把本站发布到「国内能打开、且不用开自己电脑」的免费站点

方案：**腾讯云 EdgeOne Pages（海外加速区）+ 自己的域名**。
0 元月费、不用备案、不用服务器，部署完就一直在线，关掉电脑也能访问。

---

## 0. 这次已经替你修好的问题

| 问题 | 处理 |
|---|---|
| `npm run build` 直接报错（`benefits.md` 里图片写成了 `docs/public/images/...`） | 改成站点根路径 `/images/...`，构建通过 |
| 图片文件名是中文，部分 CDN / 上传工具会出问题 | 全部改成英文名（`guide-entry.png` 等） |
| `cleanUrls: true` 生成 `/basics` 这类无后缀地址，纯静态托管上会 404 | 改为 `false`，链接变成 `/basics.html`，任何静态托管都能用 |
| 手工打包容易出错 | 新增 `deploy\publish.ps1`，一条命令完成「构建 + 打包 + 校验」 |
| 根目录旧 zip 是坏构建 | 已删除，改用 `deploy\card-guide-site.zip` |

现在 `deploy\card-guide-site.zip` 是可直接部署的成品（53 个文件，6.03 MB）。

---

## 1. 先搞清楚一件事：为什么必须有一个域名

EdgeOne Pages 会免费送你一个项目域名（形如 `xxx.edgeone.app`）。但按官方规则：

- 加速区域选「含中国大陆」→ 项目域名只能用 **3 小时有效**的预览链接，过期返回 401；
- 加速区域选「不含中国大陆」→ **中国大陆网络访问项目域名直接返回 401**。

所以：**默认域名在国内不能用，必须绑一个自己的域名**。绑域名时加速区域选「全球可用区（不含中国大陆）」，官方明确这种组合**不需要工信部备案**（见 [域名管理概览](https://edgeone.cloud.tencent.com/pages/document/175191784523485184)）。

> 域名「实名认证」和「ICP 备案」是两件事。买域名要做实名（1 个工作日内），但只要不解析到中国大陆节点，就不需要备案。

---

## 2. 购物清单（一次性，约 ¥10~¥90/年）

| 项目 | 在哪买 | 费用 | 备注 |
|---|---|---|---|
| 域名 1 个 | 腾讯云 / 阿里云「域名注册」 | `.top`/`.xyz` 首年约 ¥9~30；`.com` 约 ¥60~90/年 | 需身份证实名，1 个工作日内通过 |
| 腾讯云账号 | 微信/QQ 扫码注册 | 免费 | 需完成实名认证 |
| EdgeOne Pages | 控制台直接开通 | 免费 | 个人小站额度够用 |

不需要买服务器，不需要买证书（自动签发免费 HTTPS）。

---

## 3. 部署步骤（约 15 分钟，一次性）

### 3.1 上传站点

1. 打开 <https://console.cloud.tencent.com/edgeone/makers>
2. **创建项目** → 选 **直接上传**
3. 项目名称随便填，例如 `sve-guide`
4. **加速区域**：选 **全球可用区（不含中国大陆）** ← 选错要备案，且创建后不好改，务必选对
5. 把 `deploy\card-guide-site.zip` 拖进上传区（也可以直接拖 `dist` 文件夹）
6. 点 **开始部署**，等状态变成「部署成功」

上传限制：文件数 ≤ 1000、单文件 ≤ 25 MB。本站 53 个文件、最大 2.2 MB，远低于限制。
（参考：[直接上传](https://edgeone.ai/document/173731777484574720)）

### 3.2 绑定自己的域名

1. 进入项目 → **域名管理** → **添加自定义域名**
2. 填 `www.你的域名.com`（先只加这一个，跑通再说）
3. 按控制台提示，到域名解析处加一条 **CNAME**：
   - 主机记录：`www`
   - 记录类型：`CNAME`
   - 记录值：控制台给出的目标地址（形如 `xxx.edgeone.app`，照抄即可）
4. 回控制台点验证 / 等待
5. 证书自动签发，一般 5~15 分钟；状态变「已生效」后访问 `https://www.你的域名.com`

### 3.3 验收（重要）

用**手机流量**（关掉 Wi-Fi）逐项确认：

- [ ] 首页
- [ ] 基本玩法 / 牌店在哪 / 怎么收卡 / 怎么组卡
- [ ] 名词解释 / 实体卡福利 / 组织与社群
- [ ] 福利页 4 张图片能加载
- [ ] 输一个不存在的地址，出现 404 页面
- [ ] 右上角搜索能搜到内容

---

## 4. 以后怎么改内容

现在线上是 **GitHub Pages**（Actions 自动构建），改完内容一条命令就发布：

```powershell
# 1. 改 docs/ 里的 Markdown（本地想看效果：npm run dev）
# 2. 发布
$env:GITHUB_TOKEN = 'ghp_xxx'      # 或者把 token 写进 deploy\.token（已 gitignore）
powershell -ExecutionPolicy Bypass -File deploy\update.ps1 -Message "补充牌店信息"
```

脚本做三件事：

1. `npm run build` 先校验——**构建失败就不推送**，线上保持原样；
2. `git add -A` + `git commit`；
3. 自动拉起本地代理，把提交推到 GitHub（因为本机 `github.com` 的 DNS 指向坏 IP），Actions 构建发布，约 1 分钟生效。

看进度：<https://github.com/RealwuguQAQ/sve-guide/actions>

### 改图片的注意点

图片放 `docs/public/images/`，引用时写 **`/images/xxx.jpg`**（站点根路径），
**不要**写 `docs/public/images/xxx.jpg`——之前就是这样导致构建直接失败的。

### 不用脚本的手动方式

```powershell
git add -A
git commit -m "更新内容"
git push origin main        # 需要能连上 github.com 的网络
```

### 如果以后改用 EdgeOne 托管

```powershell
powershell -ExecutionPolicy Bypass -File deploy\publish.ps1
```

产物是 `deploy\card-guide-site.zip`，到 EdgeOne 控制台 → 项目 → **新建部署** → 拖进去即可。

---

## 5. 备选方案

### 备选 A：Cloudflare Pages（同样免费、无需备案）

1. 注册 <https://dash.cloudflare.com>（邮箱即可）
2. 把域名 **添加到 Cloudflare**，按提示到域名注册商处把 NS 改成 Cloudflare 给的两个地址（生效 0~24 小时）
3. 左侧 **Workers & Pages** → **Create** → **Pages** → **Upload assets** → 拖入 `deploy\card-guide-site.zip`
4. 先访问 `xxx.pages.dev` 自测
5. 项目 → **Custom domains** → 添加 `www.你的域名.com` → 自动配 DNS 和证书

比 EdgeOne 多一步「改 NS」，但 Cloudflare 的国内可达性比较有口碑。

### 不要用

- `*.vercel.app`、`*.netlify.app` 默认域名 —— 国内经常直接打不开，必须绑自有域名。
- Gitee Pages —— 已停止服务。

---

## 6. GitHub Pages（已上线）

**线上地址：<https://realwuguqaq.github.io/sve-guide/>**

| 项 | 值 |
|---|---|
| 仓库 | <https://github.com/RealwuguQAQ/sve-guide>（public） |
| 部署方式 | GitHub Actions（`build_type: workflow`），每次 push 到 `main` 自动构建发布 |
| 本地 remote | `origin` 已指向该仓库，分支 `main` |
| 首次部署 | 2026-11-08 通过 `deploy/push-github-api.mjs` 走 REST API 上传（本机连不上 github.com，但 api.github.com 通） |

第一次上传时脚本是逐个文件 PUT 的，所以远端有 27 个「add xxx」提交，历史看起来比较碎——不影响使用，以后正常 `git push` 就是干净的提交了。

GitHub Pages 需要的东西都已经配好了：

| 已配置 | 作用 |
|---|---|
| `docs/.vitepress/config.mts` 里的 `SITE_BASE` 支持 | 项目仓库的站点地址是 `https://<用户名>.github.io/<仓库名>/`，必须把子路径加进资源 URL，否则所有 CSS/JS/图片 404 |
| `.github/workflows/deploy-pages.yml` | push 到 `main` 自动 `npm ci` + `npm run build` + 发布；仓库里不用放 `dist` |
| 本地 git 仓库 | 分支 `main`，27 个文件，已完成 3 次提交 |

上线地址会是：`https://<你的用户名>.github.io/<仓库名>/`

⚠️ 两个现实问题必须先说清：

1. **本机连不上 github.com**：DNS 把 github.com 解析到 `20.205.243.166`（该 IP 丢包），`140.82.112.3` 反而通。所以在这台机器上 `git push` 会失败，但 `api.github.com` 是通的。
2. **`github.io` 在国内时通时不通**：部署成功 ≠ 国内稳定访问。

### 办法 A：给我一个 Token，我走 API 上传（不用连 github.com）

1. 打开 <https://github.com/settings/tokens/new>（classic token）
2. Note 随便填，Expiration 选 7 天，勾选 **`repo`** 和 **`workflow`**
3. 生成后把 `ghp_...` 这一串发我
4. 我执行：

```powershell
$env:GITHUB_TOKEN = 'ghp_xxx'
node deploy/push-github-api.mjs sve-guide
```

脚本会：建仓库 → 逐个文件走 Contents API 上传 → 开启 Pages（Actions 构建）→ 触发工作流 → 轮询到部署成功，最后打印网址。

用完请**立刻**到 <https://github.com/settings/tokens> 把这个 Token 删掉。

### 办法 B：你自己推（需要能上 GitHub 的网络）

先在能连 GitHub 的网络下（或开着代理）：

```powershell
git remote add origin https://github.com/<你的用户名>/sve-guide.git
git push -u origin main
```

然后仓库 → **Settings → Pages → Source** 选 **GitHub Actions**，等 Actions 跑完即可。

> 本机如果只是 DNS 问题，可以先跑 `node deploy/github-proxy.mjs` 起本地代理，再用
> `git -c http.proxy=http://127.0.0.1:17890 push`。实测浏览器类请求能通，但 git 传输在这条线路上仍不稳定，优先用办法 A。

---

## 7. 代码放哪：GitHub 还是国内托管？

**结论：代码可以放 GitHub，但别指望 GitHub Pages 当国内访问入口；而且你这台机器现在根本连不上 GitHub。**

实测（本机，2026-11-08）：

| 地址 | 结果 |
|---|---|
| `github.com:443` | ❌ 超时，21 秒连不上 |
| `raw.githubusercontent.com` | ❌ 超时 |
| `codeload.github.com` | ❌ 超时 |
| `api.github.com` | ✅ 通 |
| `gitee.com` | ✅ 通，0.1 秒 |
| `cnb.cool` | ✅ 通，0.2 秒 |

由此有三个结论：

1. 现在 `git push` 到 GitHub 会直接失败，除非你挂代理或改 hosts。
2. 就算推上去了，`github.io` 在国内也是时通时不通、时快时慢，不能当正式入口。
3. GitHub Pages 免费版要求仓库公开（私有仓库用 Pages 要付费），源码和那张「影之诗ID 145454」截图会一并公开。

### 路线 1（推荐）：CNB / Gitee 存代码 + EdgeOne Git 导入

- CNB（<https://cnb.cool>，腾讯自家，国内直连）或 Gitee 存仓库，国内 push 秒传。
- EdgeOne Pages 支持从 Git 仓库导入（官方有 CNB 插件、GitLab CI/CD 集成），构建命令填 `npm run build`，输出目录填 `dist`。
- 好处：以后改完 Markdown，`git push` 一下自动上线，不用手动传 zip。

### 路线 2：GitHub 只当备份

等你有能连 GitHub 的网络（代理/加速器）再 push，对外访问仍走 EdgeOne + 自有域名。

### 路线 3（最省事，现在就能做）

不上 Git，每次 `deploy\publish.ps1` 重新打包，控制台「新建部署」把 zip 拖进去。

> ⚠️ EdgeOne 项目建的时候要选「直接上传」还是「导入 Git 仓库」，**选定后不能改**，只能新建项目。想走自动部署就一开始选 Git 导入。

### 本地仓库已经准备好了

`git init` 和首次提交都已完成（分支 `main`，29 个文件），要推到哪家执行：

```powershell
git remote add origin https://cnb.cool/你的用户名/sve-guide.git   # 或 gitee 地址
git push -u origin main
```

---

## 8. 常见问题

**Q：国内访问速度怎么样？**
走境外（香港等）节点，一般首屏 1~3 秒，福利页图片多会慢一点。日常看文档够用。
要「秒开」只能走国内节点，那就必须备案 + 国内云（腾讯云 COS / 阿里云 OSS）。

**Q：绑定域名后国内还是打不开？**
先确认三件事：① 加速区域是「不含中国大陆」；② CNAME 已生效（`nslookup www.你的域名.com` 能看到目标）；③ 证书状态「已生效」。
如果都正常仍打不开，说明这条跨境线路不通，按备选 A 换 Cloudflare Pages 试，或改用香港轻量服务器（约 ¥25/月）。

**Q：会不会哪天突然打不开？**
两种风险：① 域名忘了续费；② 内容违规被投诉。记得开自动续费，内容保持现在这种正常资料就行。

**Q：想要不带 www 的地址？**
再加一条自定义域名 `你的域名.com`，主机记录填 `@`，同样做 CNAME。

**Q：电脑关机了还能访问吗？**
能。文件在腾讯云上，跟你的电脑无关。电脑只在「改内容 + 重新上传」时需要开机。

**Q：网站有外部依赖吗？**
没有。字体、样式、脚本、图片都在包内，不依赖任何境外 CDN（这点对国内访问很关键）。
