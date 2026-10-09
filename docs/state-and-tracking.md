# 状态、推进与跟踪

## 三层状态

- 任务主状态：task card 是唯一真源。
- 验证准备状态：card.verification 表示 pending / ready / waived，规格正文在 verification。
- 工作包阶段历史：PROGRESS.md 仅在整个工作包与全局验收通过后记录，不充当实时看板。

| 主状态 | 含义 | 推进责任 |
| --- | --- | --- |
| pending | hard 未完成或独立验证尚未就绪 | Architect 创建；Verification Owner / 收尾 Coding Owner 刷新 |
| ready | hard 全 done，验证 ready 或合法豁免 | 等待指定 Coding Owner |
| in_progress | 一位 Owner 已领取 | Coding Owner 持续实现与修复 |
| awaiting_acceptance | 必需自动化通过，人工待验收 | 用户决定；原 Coding Owner 保持责任 |
| blocked | 必需外部工件、权限、环境不可用 | 记录阻塞条件、解除办法；恢复后复核领取条件 |
| needs_arch_review | 冻结 oracle 或批准边界必须改变 | Architect / 用户做最小决策 |
| done | 必需人工项与用户整体通过 | 原 Owner 写 accepted_at、刷新后继并归档 |
| failed | 有效路径有证据表明已耗尽 | 保留失败原因与证据，不冒充 done |

正常推进为 pending → ready → in_progress → awaiting_acceptance → done。拒绝返回 in_progress。blocked 与 needs_arch_review 恢复时仍需复核依赖、验证依据和 Owner，不自动跳到 done。failed 留在活动库，若用户重新批准继续，记录新决策并复核后转入适用状态。

## 一次推进记录什么

领取：card.status、result.owner。修复：evidence 中记录失败分类、修正假设、有效尝试及新证据，result.attempts 计有效修复尝试。验证：每条记录映射 AC/VER，保留命令、结果、摘要、快照及报告引用。机制适配：verification_deviations。范围外发现：follow_up_candidates，不自动扩大任务。

阻塞记录至少说明必需条件、证据、谁可以解除、解除后第一项验证；恢复和架构决策引用同样进入证据。只更新相应真源；任何影响活动摘要的 card 修改后运行 reindex。

## 会话恢复

读取项目入口，工具可用时使用 `context TASK-ID --role ROLE`，否则按 WORKFLOW 直接读取相应文件，确认当前 Owner、主状态、hard 前置、spec fingerprint、最新执行快照。in_progress 继续原任务；awaiting_acceptance 等待用户结论；不得把上次命令通过当作当前快照通过。

跨会话的证据应记录 HEAD、dirty 状态，并在脏工作区额外保存有关 diff、文件内容摘要或报告版本；单独一个 dirty 标签不能唯一标识代码版本。模板中 snapshot_id 应替换为可追溯的实际快照或制品标识。

## 收口与归档

用户全部必需人工项和整体通过 → 写人工证据及 accepted_at → done → 刷新后继 ready → archive。工具内部迁移前后校验；归档后可作为 hard 前置解析，普通上下文不加载完整历史。普通 validate 拒绝活动 done，因此不要在 done 与 archive 之间用普通 validate 作为步骤。

归档工件约定不可变。manifest 的内容哈希用于发现意外改动；`reindex` 也会重新生成 manifest，不是防篡改签名。审计须结合版本控制与保留制品，不能在发现历史被改后直接重建哈希冒充无变化。
