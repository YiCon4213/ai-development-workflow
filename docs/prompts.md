# 角色提示词

以下在目标项目中使用，将 Task ID、目标和工作包名换成真实内容。按 README 搭建后，通用入口是显式读取 `.workflow/skills/技能名/SKILL.md`；若项目原有技能位于其它目录，改用实际路径。`$技能名` 只在当前工具已发现或注册技能时使用。

以下 taskctl 命令均在 Python 与依赖可用时执行；否则按 WORKFLOW 的等价维护约定直接读写文件，用现有运行能力计算规范指纹并复核结构，明确记录工具未运行，不省略交接闸门。搭建提示词见 README 的“方式二”。

## 需求对齐与规划

```text
读取 .workflow/skills/architect/SKILL.md，为本次需求规划工作包：
目标：填写用户问题与可观察成功结果。
约束：填写真实限制和已批准决策。
方案倾向：填写偏好；未经证明的判断应标为假设。
遵守仓库入口与 .tasks/WORKFLOW.md；只读取相关上下文。
审计假设、比较最小可行方案，更新 architecture.md 的当前边界。
输出最少成果型任务，每张使用稳定 AC ID，明确范围、关系类型、风险和并行性。
写入 cards/active 并创建空 evidence，运行 reindex 与 validate。
代码任务 verification pending；不要实现或直接交给 Coding Owner。
给我可评审的架构和任务图，待批准后进入独立验证设计。
```

## 独立测试设计（使用独立上下文）

```text
架构与 TASK-001 已批准。读取 .workflow/skills/verification-owner/SKILL.md，设计编码前独立规格。
工具可用时运行 taskctl context TASK-001 --role verification-owner；否则按角色直接读对应文件。
先依据用户目标、架构、任务 AC 与公开契约建立 oracle，再读取最少测试约定。
明确正常、边界、失败和相关风险场景，按最低充分层级选择证据。
写入 verification/TASK-001.yaml，把 fingerprint 命令结果绑定到规格和任务元数据。
更新验证 ready；仅 hard 前置 done 时设主状态 ready。reindex 并 validate。
不领取 result.owner、不实现、不执行实现后测试。交接后停止。
```

## 领取与执行

```text
读取 .workflow/skills/coding-owner/SKILL.md，执行 TASK-001。
工具可用时运行 taskctl context TASK-001 --role coding-owner，否则直接读取当前 card、hard 前置、spec 和 evidence；检查交接与规范指纹。
符合领取条件后先持久化 Owner 与 in_progress，再实现。
完成开发者测试、独立规格执行、自修复、回归及 evidence 记录。
普通失败不退回 Verification Owner；冻结 oracle 或架构冲突升级决策。
全部必需自动化通过后设 awaiting_acceptance，提供真实前置条件、数据、逐步操作、预期、证据与清理清单。
不提前标 done、不领取下一张、不自行提交或发布。
```

## 拒绝后修复

```text
TASK-001 的 UAT-001 未通过：操作、预期、实际、证据如下……
原 Coding Owner 保持所有权，恢复 in_progress，诊断并修复，重跑受影响与必需回归，更新证据和验收清单。
```

## 用户通过后收口

```text
我已完成 TASK-001 所有必需人工验收并明确整体验收通过。
记录本次确认和 accepted_at，设 done，刷新 hard 前置已满足的后继 readiness，归档到指定工作包。
运行 reindex / validate，报告归档路径与后继状态，不自动领取下一张任务。
```

“看起来可以”“继续”或自动化全绿不应自动解释为用户整体通过；保留用户明确确认的来源。
