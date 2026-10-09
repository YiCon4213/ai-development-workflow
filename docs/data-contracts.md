# 数据契约与工具边界

## 唯一真源

任务卡包含 `schema_version: 2` 与 `task` 映射；任务定义、AC、关系、状态与 Owner 放在 task 内。证据与规格是单独 YAML，不嵌入 card。模板见 [templates](../templates/)。项目初始没有任务，不建立伪任务来通过校验。

- Task ID：`TASK-` 后接大写字母、数字及中划线，如 TASK-001；活动文件名必须匹配。
- Work package：小写字母、数字和中划线，例如 report-export。
- hard：task / type / reason / required_artifact。
- integration_order：task / type / reason / verification_gate。
- coordination：task / type / reason / shared_surfaces。
- parallelism：mode 为 parallel / isolated / serial，加 reason。
- verification：required、status、spec、designed_by、designed_at、basis_fingerprint、waiver_reason。
- result：owner、attempts、completed_at、accepted_at、evidence_ref。completed_at 表示实现与自动化交付完成时刻；done 仍以 accepted_at 和用户通过为必要条件。

## Fingerprint

`fingerprint TASK-ID` 计算 canonical-json-v1 的 SHA-256。稳定字段：id、goal、scope、constraints、forbidden、acceptance、relations、dependencies、parallelism、risk_level、escalation_conditions。字符串换行统一 LF；映射按键排序、列表保序；紧凑 UTF-8 JSON 无 BOM / 尾随换行。排除 status、verification、Owner、时间、执行结果。

同一值同时填写 card.verification.basis_fingerprint 和 spec.basis.task_card_fingerprint。需求依据变更后旧规格失效；不能只改 hash 来掩盖语义变更，需要先由有权限的角色确认新 oracle，再重新设计必要规格。

工具当前指纹不覆盖 architecture.md 内容。架构应有明确版本或章节依据；架构语义改变但 card 没变时仍需人工复核规格，不应声称哈希已检测全部需求漂移。

## 证据与验收

证据 `schema_version: 1`，包含 task_id、records、verification_deviations、follow_up_candidates。执行快照包含 git_head、worktree_state、task_card_fingerprint 与可追溯 snapshot_id。records 逐条 covers AC/VER/UAT，记录结果、检查和必要工件。

合法结果：pass / fail / skipped / no_tests / flaky_retry / baseline_failure / environment_blocked / unverified。只有 pass 满足必需项。验证 case 声明 evidence_gate 为 automated / user_acceptance / both；awaiting_acceptance 仅表示必需自动化已过，人工部分仍待用户。

## 工具实际检查范围

现有 taskctl 检查 ID 唯一与文件位置、关系目标、hard 环、指定执行状态的依赖和验证准备、引用文件、规格指纹、派生索引、归档哈希；归档只接受 done 且有 pass 的 user_acceptance 记录。

它不是完整 schema 验证器：不验证所有状态枚举、关系字段、全部 AC/VER/UAT 覆盖、完整用户清单、accepted_at、审批来源、证据真实性、未知 YAML 字段或真实测试结果。角色必须遵守 WORKFLOW.md，不能把 validate 通过等同于可以交付。CLI 不提供锁、自动状态迁移、任务领取或测试执行。

工具会读取任务引用的本地文件，只用于可信仓库。来源不明的 YAML 先审查路径和内容，不作为沙箱或对抗性输入安全边界。

## 变更维护

调整字段或规则时同步技能 references、模板、虚构示例、测试、工具和文档；派生文件重建后验证。不修改已归档任务来迁就新格式。本包不提供旧格式迁移器，也不提供来源项目的流程切换例外。
