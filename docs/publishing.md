# 发布到 GitHub

本目录已经按独立仓库组织。本次提炼不创建远程仓库，不修改原项目 Git 配置，也不执行提交和推送。

1. 将整个 `ai-development-workflow/` 目录复制到原业务仓库之外，作为新仓库根。不要上传外层业务仓库或其历史。
2. 检查 README、MIT 版权署名、来源发布权属、敏感内容与示例标记；运行 CONTRIBUTING 中的所有检查。
3. 在 GitHub 创建一个空仓库，可使用 `ai-development-workflow` 名称，不要预先生成另一套 README 或许可证。
4. 在复制后的独立目录执行下面命令。最后一条 URL 必须换为实际新仓库地址。

```sh
git init -b main
git add .
git commit -m "Initial reusable AI development workflow"
git remote add origin https://github.com/YOUR_ACCOUNT/ai-development-workflow.git
git push -u origin main
```

这些是发布者手动执行的说明，不授予 Agent 外部操作权限。新仓库的 MIT 许可来自本包 LICENSE；来源权属仍由发布者确认。

CI 将安装 Python / PyYAML，在 Windows 与 Ubuntu 验证工具、空模板和虚构示例。首次推送后检查实际运行结果；本地通过不能称远程 CI 已通过。建议启用私密漏洞报告，发布首个版本时使用 CHANGELOG 作为说明。

发布后向使用者说明：本包是角色规则、文档骨架与任务辅助工具，尚无自动调度、锁、完整 schema 验证或验收审批服务。后续发布改变冻结字段、状态语义或存储结构时必须说明迁移步骤。
