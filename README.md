# Academic Homepage — 个人学术主页

单页式个人学术主页，风格参考 [littlefatshiba.github.io](https://littlefatshiba.github.io)：
左侧 sticky 个人资料栏 + 右侧单栏正文，米白底 + 深绿点缀 + Georgia 衬线标题。

Quarto 只负责构建与部署，页面正文是手写 HTML，所以排版完全可控、不受主题约束。

## 项目结构

```
├── _quarto.yml            # Quarto 构建配置（theme: none，无导航栏 / TOC / 页脚）
├── index.qmd              # 极简骨架，正文由 page.html 注入
├── page.html              # 英文版页面 HTML（About / News / Selected / All Publications）
├── zh.html                # 中文版页面（独立 HTML，与英文版同构，顶栏可互相跳转）
├── refs.bib               # BibTeX 文献库（中英两页共用）
├── bib2qmd.py             # refs.bib → page.html + zh.html 的论文区块
├── cv.qmd                 # 简历页（当前未构建，需要时加回 _quarto.yml 的 render）
├── assets/
│   ├── css/academic.css   # 全站样式
│   ├── js/academic.js     # 滚动时高亮导航项
│   └── img/avatar.png     # 头像
├── files/cv.pdf           # 简历 PDF
└── .github/workflows/publish.yml  # GitHub Actions 自动部署
```

## 双语结构

- 英文版：`page.html`，由 Quarto 渲染 `index.qmd` 时注入 → 站点根路径 `/`
- 中文版：`zh.html`，不经过 Quarto（避免 `include-after-body` 重复注入），由 `_quarto.yml` 的 `project.resources` 原样复制到 `_site/zh.html` → `/zh.html`
- 两页顶部导航各有一个语言切换按钮（英文页「中文」/ 中文页「EN」）
- 论文标题、作者、期刊与会议名保持英文原文，不翻译；正文与界面文案为中文

## 日常维护流程

### 更新论文

1. 把新论文的 BibTeX 条目追加到 `refs.bib`
2. 运行 `python bib2qmd.py`，自动重写 `page.html`（英文）与 `zh.html`（中文）里的论文区块与篇数徽章
3. 提交推送：`git add -A && git commit -m "add paper" && git push`

`refs.bib` 支持以下可选展示字段（缺省时自动降级）：

| 字段 | 作用 |
|------|------|
| `shortvenue` | 卡片上显示的会议/期刊简称，缺省用 `journal` / `booktitle` |
| `role` | 作者角色标签，如 `First author`（中文页自动译为「第一作者」） |
| `summary` | 一句话摘要，仅在 Selected Publications 显示 |
| `summary_zh` | 中文一句话摘要，中文页使用；缺省回退 `summary` |
| `selected` | `true` 表示进入 Selected Publications |
| `url` | 额外链接（GitHub 链接会标注为 `Code` / `代码`） |

只想更新其中一页时：`python bib2qmd.py --pages zh.html:zh`

### 修改个人信息

- **英文版布局、简介、News、教育经历** → 编辑 `page.html`
- **中文版对应内容** → 编辑 `zh.html`（两页是各自独立的 HTML，改动需分别同步）
- **论文列表** → 编辑 `refs.bib` 后运行 `python bib2qmd.py`（两页一起更新）
- **配色、字体、间距** → 编辑 `assets/css/academic.css`（配色集中在文件顶部的 CSS 变量）
- **站点标题与 meta** → 编辑 `_quarto.yml`

### 本地预览

```powershell
quarto render
python -m http.server 4200 -d _site
```

打开 http://127.0.0.1:4200 即可。

## 部署

推送到 `main` 分支后，GitHub Actions 会自动安装 Quarto、运行 `bib2qmd.py`、渲染并发布到 GitHub Pages。

- 英文版：https://huzimun.github.io
- 中文版：https://huzimun.github.io/zh.html
