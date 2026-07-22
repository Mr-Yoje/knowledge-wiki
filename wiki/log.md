# 操作日志

## 2026-07-22｜初始化 + 首次资料导入

### 知识库初始化

- 创建 Knowledge Wiki 目录结构（source/、wiki/、schema/）
- 创建 wiki/index.md、wiki/README.md、wiki/log.md
- 创建 wiki/ 子目录：资料/、实体/、概念/、综合/、对比/、查询/
- 安装 schema 文件（SKILL.md、verify_wiki.py）
- 初始化 git 仓库，创建 GitHub 远程仓库 `Mr-Yoje/knowledge-wiki` 并推送
- 保存 GitHub PAT 到 secrets.json

### 首次资料导入

- 调研 Mem0 架构、Graph Memory 创建/去重/更新机制
- **新增概念页**：[[Knowledge/wiki/概念/Mem0架构与知识图谱技术细节|Mem0 架构与知识图谱技术细节]]
- **新增资料页**：[[Knowledge/wiki/资料/原始资料层说明]]
- 更新 wiki/index.md 添加概念页入口
- 修复断链：README.md 中的示例链接、概念页中的待创建页面引用
- 运行体检脚本 verify_wiki.py：问题已全部修复（0 broken links, 0 missing index）

---

## 当前待办 / 后续方向

- [ ] 在 Obsidian 中打开此 vault
- [ ] 继续完善 Mem0 相关页面（LLM记忆层对比、知识图谱构建方法）
- [ ] 添加更多资料
