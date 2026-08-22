# Academic Homepage — Quarto + GitHub Pages

基于 Quarto 构建的个人学术主页，托管于 GitHub Pages。

## 项目结构

```
├── _quarto.yml            # Quarto 站点主配置
├── index.qmd              # 首页（个人简介、研究方向、教育经历）
├── publications.qmd       # 论文列表页（由 refs.bib 自动生成）
├── cv.qmd                 # 在线简历页
├── refs.bib               # BibTeX 文献库
├── bib2qmd.py             # BibTeX → 论文页 转换脚本
├── assets/
│   ├── css/styles.css     # 自定义样式
│   └── img/avatar.png     # 头像（请替换为自己的照片）
├── files/                 # 存放 cv.pdf、论文 PDF
└── .github/workflows/publish.yml  # GitHub Actions 自动部署
```

## 日常维护流程

### 更新论文
1. 将新论文的 BibTeX 条目追加到 `refs.bib`
2. 运行 `python bib2qmd.py` 自动重新生成 `publications.qmd`
3. 提交推送：`git add . && git commit -m "add paper" && git push`

### 修改个人信息
- 编辑 `index.qmd`（简介、研究方向、教育经历）
- 编辑 `cv.qmd`（简历详情）
- 编辑 `_quarto.yml`（姓名、邮箱、链接）

### 本地预览
```powershell
quarto preview
# 或渲染后用任意静态服务器
quarto render
python -m http.server 4200 -d _site
```

## 首次部署（需完成）

1. 在 GitHub 创建公开仓库 `你的用户名.github.io`
2. 替换 `_quarto.yml` 和页面中所有 `YOUR USERNAME` / `YOUR_USERNAME` 占位符
3. 绑定远端并推送：
   ```powershell
   git remote add origin https://github.com/你的用户名/你的用户名.github.io.git
   git push -u origin main
   ```
4. 仓库 Settings → Pages → Source 选 **GitHub Actions**
5. 等待 Actions 运行完成，访问 `https://你的用户名.github.io`

## 注意事项

- 本机 Quarto 安装位置：`F:\quarto\bin\`（已加入 PATH）
- 文件名避免中文与空格
- 修改 `.qmd` 文件后需重新 render 或直接推送（Actions 云端构建）
