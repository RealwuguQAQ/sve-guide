#!/usr/bin/env node
// 通过 GitHub REST API 把当前仓库（git 已跟踪的文件）推到一个新建的 GitHub 仓库，
// 并开启 GitHub Pages（走 Actions 构建）。
//
// 为什么不用 git push：本机到 github.com:443 不通（DNS 被解析到黑洞 IP），
// 但 api.github.com 是通的，所以走 API 上传。
//
// 用法：
//   $env:GITHUB_TOKEN = 'ghp_xxx'
//   node deploy/push-github-api.mjs [仓库名]
//
// 需要 token 具备 repo + workflow 权限（classic PAT）。

import { readFileSync } from 'node:fs'
import { execSync } from 'node:child_process'

const TOKEN = process.env.GITHUB_TOKEN
const REPO_NAME = process.argv[2] || 'sve-guide'

if (!TOKEN) {
  console.error('缺少环境变量 GITHUB_TOKEN')
  process.exit(1)
}

const API = 'https://api.github.com'

async function api(path, { method = 'GET', body, raw = false } = {}) {
  const res = await fetch(API + path, {
    method,
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'sve-guide-deploy',
      ...(body ? { 'Content-Type': 'application/json' } : {})
    },
    body: body ? JSON.stringify(body) : undefined
  })

  const text = await res.text()
  if (!res.ok) {
    if (raw) return { ok: false, status: res.status, text }
    throw new Error(`${method} ${path} -> ${res.status} ${text.slice(0, 400)}`)
  }
  return raw ? { ok: true, status: res.status, text } : text ? JSON.parse(text) : null
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms))
}

const me = await api('/user')
const owner = me.login
console.log(`账号：${owner}`)

// 1. 建仓库（已存在则复用）
let repo = (await api(`/repos/${owner}/${REPO_NAME}`, { raw: true })).ok
  ? await api(`/repos/${owner}/${REPO_NAME}`)
  : null

if (!repo) {
  console.log(`创建仓库 ${owner}/${REPO_NAME} ...`)
  repo = await api('/user/repos', {
    method: 'POST',
    body: {
      name: REPO_NAME,
      description: '实体卡新手指南（VitePress）',
      private: false,
      has_issues: true,
      has_wiki: false,
      auto_init: false
    }
  })
} else {
  console.log('仓库已存在，复用')
}

const branch = repo.default_branch || 'main'

// 2. 逐个文件上传（Contents API）
const files = execSync('git ls-files', { encoding: 'utf8' })
  .split('\n')
  .map((s) => s.trim())
  .filter(Boolean)

console.log(`准备上传 ${files.length} 个文件 ...`)

let done = 0
for (const file of files) {
  const content = readFileSync(file).toString('base64')
  const put = (extra) =>
    api(`/repos/${owner}/${REPO_NAME}/contents/${encodeURI(file)}`, {
      method: 'PUT',
      body: { message: `add ${file}`, content, ...(done === 0 ? {} : { branch }), ...extra },
      raw: true
    })

  let res = await put()
  if (res.status === 422) {
    // 文件已存在（或仓库非空）：取 sha 后覆盖
    const cur = await api(`/repos/${owner}/${REPO_NAME}/contents/${encodeURI(file)}?ref=${branch}`, {
      raw: true
    })
    if (cur.ok) {
      const sha = JSON.parse(cur.text).sha
      res = await put({ sha })
    }
  }
  if (!res.ok) {
    throw new Error(`上传 ${file} 失败：${res.status} ${res.text.slice(0, 200)}`)
  }
  done++
  if (done % 10 === 0) console.log(`  已上传 ${done}/${files.length}`)
}
console.log(`上传完成：${done}/${files.length}`)

// 3. 开启 Pages（构建方式 = GitHub Actions）
const pagesExisting = await api(`/repos/${owner}/${REPO_NAME}/pages`, { raw: true })
if (pagesExisting.ok) {
  console.log('Pages 已开启')
} else {
  await api(`/repos/${owner}/${REPO_NAME}/pages`, {
    method: 'POST',
    body: { build_type: 'workflow' },
    raw: true
  })
  console.log('Pages 已开启（Actions 构建）')
}

// 4. 触发工作流
await api(`/repos/${owner}/${REPO_NAME}/actions/workflows/deploy-pages.yml/dispatches`, {
  method: 'POST',
  body: { ref: branch },
  raw: true
})
console.log('已触发 GitHub Actions 构建 ...')

// 5. 等待首次部署完成
const url = `https://${owner}.github.io/${REPO_NAME}/`
for (let i = 0; i < 40; i++) {
  await sleep(15000)
  const runs = await api(`/repos/${owner}/${REPO_NAME}/actions/runs?per_page=1`, { raw: true })
  if (!runs.ok) continue
  const json = JSON.parse(runs.text)
  const run = json.workflow_runs?.[0]
  if (!run) continue
  if (run.status === 'completed' && run.conclusion === 'success') {
    console.log(`\n✅ 部署成功：${url}`)
    process.exit(0)
  }
  if (run.status === 'completed' && run.conclusion !== 'success') {
    console.error(`\n❌ 工作流失败：${run.html_url}`)
    process.exit(1)
  }
  console.log(`  [${i + 1}] 构建中：${run.status} ${run.conclusion || ''}`)
}
console.log(`\n构建仍在进行，稍后访问：${url}`)
