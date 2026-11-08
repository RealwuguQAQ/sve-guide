# 实体卡新手教程站

内容位于 `docs/`，使用 Markdown 编写；构建后的静态网页输出到 `dist/`。

## 本地运行

```powershell
npm install
npm run dev
```

## 构建发布文件

```powershell
npm run build
```

将 `dist/` 中的全部文件上传到静态网站托管服务。默认首页设置为 `index.html`，404 页面可设置为 `404.html`。

## 发布到线上（国内可访问、无需开着电脑）

一条命令构建并打包：

```powershell
powershell -ExecutionPolicy Bypass -File deploy\publish.ps1
```

产物：`deploy\card-guide-site.zip`，拖进托管平台即可。

推荐做法与购物清单见 **[deploy/DEPLOY.md](deploy/DEPLOY.md)**：腾讯云 EdgeOne Pages（海外加速区）+ 自有域名，免费、无需备案。

需要国内节点加速（更快）时才考虑腾讯云 COS / 阿里云 OSS，但必须绑定已备案域名。

正式上线前，请用移动、电信和联通网络分别测试首页、子页面、图片和二维码。
