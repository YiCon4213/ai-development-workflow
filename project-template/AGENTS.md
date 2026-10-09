# 项目协作入口

用户当前明确指示 > 适用仓库规则 > 批准的架构、任务卡与验证规格 > 技能 > 本地实现选择。规则不得扩大授权；冲突需要最小必要决策。

- 规划、验证设计、任务执行、状态和验收工作：先读 `.tasks/WORKFLOW.md`。
- 指定 Task ID：工具可用时运行 `python -X utf8 .tasks/tools/taskctl.py context TASK-ID --role ROLE`；否则按路径只读对应 card、直接 hard 前置及角色所需 spec / evidence，遵循 WORKFLOW 的无 Python 约定。
- 修改模块：读取受影响模块的适用说明、公开契约、调用链与相邻测试。
- 架构规划读取 `.workflow/skills/architect/SKILL.md`；编码前验证设计读取 `.workflow/skills/verification-owner/SKILL.md`；领取、执行与用户验收读取 `.workflow/skills/coding-owner/SKILL.md`。若技能保存在其它位置，更新为实际路径；快捷调用仅在已配置可用时使用。
- 任务卡、验证规格、证据各有唯一真源；index 是由 card 生成的派生摘要，不独立维护。
- 保持项目批准的权限、数据与安全边界，不隐藏失败，不将未验证报告为通过。
- 自动化通过后进入 awaiting_acceptance；用户明确整体验收后才能 done。
- Git commit、push、merge、PR 和外部发布必须有明确授权。
- 任务领取与工作包选择不代表可以自动启动多个 Agent。

接入项目时补充：项目目标、可修改范围、禁止目录、各模块规则路由、运行/测试命令及敏感配置约束。不得直接继承来源项目的技术栈假设。
