#!/usr/bin/env node
// 用途：本机 DNS 把 github.com 解析到 20.205.243.166（连接被丢包），
// 但 140.82.112.3 是通的。这个本地极小代理把 github.com 的 TLS 连接改指到可用 IP，
// 让 git 在没有 VPN 的情况下也能 clone / push。
//
// 用法：
//   node deploy/github-proxy.mjs           # 另开一个窗口保持运行
//   git -c http.proxy=http://127.0.0.1:17890 push
//
// 不需要时可把本文件删掉，不影响站点。

import net from 'node:net'

const PORT = Number(process.env.PROXY_PORT || 17890)

const MAP = {
  'github.com': ['140.82.112.3', '20.27.177.113'],
  'codeload.github.com': ['140.82.112.3'],
  'gist.github.com': ['140.82.112.3'],
  'raw.githubusercontent.com': ['185.199.108.133']
}

function pick(host) {
  const list = MAP[host]
  if (!list) return host
  return list[Math.floor(Math.random() * list.length)]
}

const server = net.createServer((sock) => {
  sock.on('error', () => {})
  sock.once('data', (chunk) => {
    const end = chunk.indexOf('\r\n\r\n')
    if (end === -1) return sock.destroy()

    const head = chunk.subarray(0, end).toString('latin1')
    const rest = chunk.subarray(end + 4)
    const m = /^CONNECT\s+([^\s:]+):(\d+)/i.exec(head)
    if (!m) {
      sock.end('HTTP/1.1 405 Method Not Allowed\r\n\r\n')
      return
    }

    const host = m[1].toLowerCase()
    const port = Number(m[2])
    const target = pick(host)

    const up = net.connect({ host: target, port, family: 4 }, () => {
      sock.write('HTTP/1.1 200 Connection Established\r\n\r\n')
      if (rest.length) up.write(rest)
      sock.pipe(up)
      up.pipe(sock)
    })
    up.on('error', () => sock.destroy())
    sock.on('close', () => up.destroy())
    up.on('close', () => sock.destroy())
  })
})

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[github-proxy] 监听 127.0.0.1:${PORT}，github.com -> ${MAP['github.com'].join(' / ')}`)
})
