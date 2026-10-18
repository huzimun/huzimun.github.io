# Academic Homepage — 个人学术主页

单页式个人学术主页，风格参考 [littlefatshiba.github.io](https://littlefatshiba.github.io)：
左侧 sticky 个人资料栏 + 右侧单栏正文，米白底 + 深绿点缀 + Georgia 衬线标题。

Quarto 只负责构建与部署，页面正文是手写 HTML，所以排版完全可控、不受主题约束。

## 项目结构

```
├── _quarto.yml            # Quarto 构建配置（theme: none，无导航栏 / TOC / 页脚）
├── index.qmd              # 极简骨架，正文由 page.html 注入
├── page.html              # 页面全部 HTML（About / News / Selected / All Publications）
├── refs.bib               # BibTeX 文献库
├── bib2qmd.py             # refs.bib → page.html 的论文区块
├── cv.qmd                 # 简历页（当前未构建，需要时加回 _quarto.yml 的 render）
├── assets/
│   ├── css/academic.css   # 全站样式
│   ├── js/academic.js     # 滚动时高亮导航项
│   └── img/avatar.png     # 头像
├── files/cv.pdf           # 简历 PDF
└── .github/workflows/publish.yml  # GitHub Actions 自动部署
```

## 日常维护流程

### 更新论文

1. 把新论文的 BibTeX 条目追加到 `refs.bib`
2. 运行 `python bib2qmd.py`，自动重写 `page.html` 里的论文区块与篇数徽章
3. 提交推送：`git add -A && git commit -m "add paper" && git push`

`refs.bib` 支持以下可选展示字段（缺省时自动降级）：

| 字段 | 作用 |
|------|------|
| `shortvenue` | 卡片上显示的会议/期刊简称，缺省用 `journal` / `booktitle` |
| `role` | 作者角色标签，如 `First author` |
| `summary` | 一句话摘要，仅在 Selected Publications 显示 |
| `selected` | `true` 表示进入 Selected Publications |
| `url` | 额外链接（GitHub 链接会标注为 `Code`） |

### 修改个人信息

- **布局、简介、News、教育经历** → 编辑 `page.html`
- **论文列表** → 编辑 `refs.bib` 后运行 `python bib2qmd.py`
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
站点地址：https://huzimun.github.io
