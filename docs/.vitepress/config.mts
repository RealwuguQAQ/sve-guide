import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'zh-CN',
  title: '实体卡新手指南',
  description: '实体卡玩法、牌店、收卡、组卡、福利与社群指南',
  cleanUrls: false,
  appearance: false,
  outDir: '../dist',
  lastUpdated: false,
  themeConfig: {
    siteTitle: '实体卡新手教程',
    nav: [
      { text: '基本玩法', link: '/basics' },
      { text: '牌店在哪', link: '/stores' },
      { text: '怎么收卡', link: '/collecting' },
      { text: '怎么组卡', link: '/deck-building' },
      { text: '更多', items: [
        { text: '名词解释', link: '/glossary' },
        { text: '实体卡福利', link: '/benefits' },
        { text: '组织与社群', link: '/communities' }
      ] }
    ],
    sidebar: [
      {
        text: '实体卡新手教程',
        items: [
          { text: '首页', link: '/' },
          { text: '基本玩法', link: '/basics' },
          { text: '牌店在哪', link: '/stores' },
          { text: '怎么收卡', link: '/collecting' },
          { text: '怎么组卡', link: '/deck-building' },
          { text: '名词解释', link: '/glossary' },
          { text: '实体卡福利', link: '/benefits' },
          { text: '组织与社群', link: '/communities' }
        ]
      }
    ],
    search: { provider: 'local' },
    outline: { label: '本页目录', level: [2, 3] },
    docFooter: { prev: '上一页', next: '下一页' },
    returnToTopLabel: '返回顶部',
    sidebarMenuLabel: '目录',
    darkModeSwitchLabel: '主题'
  },
  head: [
    ['meta', { name: 'theme-color', content: '#101827' }],
    ['meta', { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' }]
  ]
})
