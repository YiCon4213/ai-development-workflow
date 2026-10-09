# 通用任务卡工作流

仅在用户指定 Task ID、调用 `architect` / `verification-owner` / `coding-owner`，或明确要求更新任务状态与验收证据时读取本文件。

## 权威来源

- `.tasks/architecture.md`：当前工作包的目标、边界、全局约束、禁止事项、验收意图和架构升级条件。
- `.tasks/cards/active/<TASK-ID>.yaml`：活动任务定义、关系、主状态和 Owner 的唯一真源。
- `.tasks/verification/<TASK-ID>.yaml`：该任务编码前的验证意图、oracle、用例与证据要求。
- `.tasks/evidence/<TASK-ID>.yaml`：活动任务的执行证据、验证偏差、后续候选和用户验收真源。
- `.tasks/archive/<WORK-PACKAGE>/<TASK-ID>/`：已结束任务的完整历史包。
- `.tasks/index.yaml`：自动生成的活动任务摘要，不是权威来源，不手工编辑。
- `docs/TASK.md`：人类导航入口，不复制任务内容。
- `docs/PROGRESS.md`：功能包级阶段历史，只在整个功能包完成后更新。

Python 3.10+ 与 PyYAML 已可用时，指定任务后优先运行：

```text
python -X utf8 .tasks/tools/taskctl.py context TASK-ID --role architect
python -X utf8 .tasks/tools/taskctl.py context TASK-ID --role verification-owner
python -X utf8 .tasks/tools/taskctl.py context TASK-ID --role coding-owner
```

只读取相应角色上下文、相关架构章节和必要公开契约。不要为了执行一张任务读取完整活动索引或历史归档。`taskctl validate` 可自动检查唯一 ID、关系、readiness、fingerprint、引用、索引和归档哈希。没有 Python 时按以下等价方式读取和维护，不因复制或搭建要求安装 Python。

## 无 Python 的等价维护约定

- 直接读取 `.tasks/cards/active/<TASK-ID>.yaml`；只补充直接 hard 前置摘要及必要架构章节。验证角色读取对应 spec，实现角色再读取 evidence，不加载整个历史。
- 本文中的 context、reindex、fingerprint、validate、archive 命令表示相应操作。工具不可用时由 AI 使用现有文件与运行能力完成等价维护；不要求新增运行环境，不把未运行的工具报告为 PASS。
- index 只能从 card 派生生成；manifest 必须对应真实归档文件及 SHA-256。不得独立改摘要来掩盖事实。
- 指纹仍须满足 canonical-json-v1。可使用已有 Node.js 或其它等价能力；缺少计算能力时仅形成规划/规格草稿，报告缺口，不伪造指纹或把未满足交接条件的代码任务设 ready。
- 手工归档须先保留备份，维护移动后的引用、索引和哈希，确认完整性后再移出活动区；不能声称获得了 taskctl 的自动回滚保证。
- 任务、规格、证据、自动化测试与用户验收闸门保持相同要求。入口复制完成不代表已完成工具校验或业务验收。

## 单向角色流

```text
用户与 AI 对齐需求
  -> Architect
  -> Verification Owner
  -> Coding Owner
  -> 用户验收
```

### Architect

- 审计事实、目标、约束、方案和假设。
- 定义架构边界、稳定 AC、任务关系和并行性。
- 代码任务的 `verification.status` 初始为 `pending`。
- 不实现代码，也不设计完整测试步骤。

### Verification Owner

- 在编码前依据批准目标、架构、任务卡和公开契约建立独立 oracle。
- 写入 `.tasks/verification/<TASK-ID>.yaml`，更新对应活动 task card 的验证元数据为 `ready`，并刷新主状态：全部 hard 关系已完成则从 `pending` 转为 `ready`，否则保持 `pending`。
- 不领取 `result.owner`，不实现代码，不执行实现后的测试或验收。
- 完成交接后停止，不参与后续往返。

### Coding Owner

- 只领取验证交接已就绪的任务；继续执行时核对既有 Owner 和批准验证依据。
- 负责实现、开发者测试、执行验证规格、自修复、证据和详细用户验收清单。
- 普通测试失败、环境适配和实现修复不返回 Verification Owner。
- 只有冻结 oracle、架构边界或授权必须改变时，才升级给 Architect 或用户。

## 任务关系

新建或修改的任务使用带类型的 `relations`。新任务不使用无类型依赖列表。

| 类型 | 是否阻塞 Coding Owner 启动 | 必填说明 |
| --- | --- | --- |
| `hard` | 是 | `reason`、前置任务交付的 `required_artifact` |
| `integration_order` | 否 | `reason`、必须等待的 `verification_gate` |
| `coordination` | 否 | `reason`、共享的 `shared_surfaces` |

每张新任务还要声明：

```yaml
parallelism:
  mode: parallel  # parallel | isolated | serial
  reason: "为什么能并行、需要隔离或必须串行"
```

用户可以选择串行调度，但调度偏好不得伪造成技术 hard 依赖。

## 验证元数据与 readiness

新代码或用户可见行为任务默认包含：

```yaml
verification:
  required: true
  status: pending        # pending | ready | waived
  spec: ".tasks/verification/TASK-XXX.yaml"
  designed_by: null
  designed_at: null
  basis_fingerprint: null
  waiver_reason: null
```

纯文档、纯记录或可由确定性结构校验完全覆盖的机械任务可以 `waived`，但必须记录具体理由。

在分片任务库中，新任务还必须：

- 把 card 写入 `.tasks/cards/active/<TASK-ID>.yaml`；
- 在 `result.evidence_ref` 指向 `.tasks/evidence/<TASK-ID>.yaml`；
- 创建包含空 `records`、`verification_deviations` 和 `follow_up_candidates` 的 evidence 文件；
- 运行 `python -X utf8 .tasks/tools/taskctl.py reindex` 和 `validate`。

任何会改变活动摘要的 task card 更新（标题、状态、风险、关系、verification 路径）后都要重建索引；不要手工编辑 `index.yaml`。

任务成为 `ready` 的条件：

```text
所有 hard 关系对应任务为 done
AND verification.status 为 ready 或有有效理由的 waived
```

验证未就绪时任务保持 `pending`。如果旧任务错误地显示为 `ready` 但没有验证交接，Coding Owner 仍不得领取。

主状态刷新责任：Verification Owner 完成规格时刷新当前任务；某个前置任务被用户验收为 `done` 后，Coding Owner 只刷新因此满足 readiness 的后续任务，但不领取它们。

## 主状态

```text
pending -> ready -> in_progress -> awaiting_acceptance -> done
                     |                    |
                     |                    `-> 用户拒绝后回到 in_progress
                     |-> blocked
                     `-> needs_arch_review
```

- `blocked` 只用于真实外部依赖、权限、凭据、环境或必需工件不可用。
- `needs_arch_review` 用于必须改变冻结 oracle、公开契约、架构、安全/数据边界或实质范围。
- `failed` 只用于已有证据表明有效路径耗尽的终止情形。
- 部分实现、聚焦测试通过、成功编译或自动化全绿均不能越过用户验收直接进入 `done`。

## 验证规格的冻结与适配

Coding Owner 不得静默修改：

- 业务期望和禁止结果；
- 权限、安全、隐私和数据完整性边界；
- 必须覆盖的风险场景；
- AC/VER 与证据类别的映射。

可以在不降低证据的情况下调整：

- 命令、测试文件、夹具和选择器；
- 因仓库结构变化而调整的执行路径；
- 等价或更强的测试层级。

每次适配都要记录原机制、替代机制、原因、等价性和仓库证据。不可适配的冲突直接升级给 Architect 或用户，不回到 Verification Owner。

## 证据

每个 required AC/VER 必须声明 `evidence_gate: automated | user_acceptance | both`，并有与当前阶段对应的明确结果。只允许：

```text
pass | fail | skipped | no_tests | flaky_retry |
baseline_failure | environment_blocked | unverified
```

进入 `awaiting_acceptance` 前，`automated` 和 `both` 的自动化部分必须为 `pass`；纯 `user_acceptance` 以及 `both` 的人工部分保持待验收，不能提前标记通过。进入 `done` 前，必需人工项和用户总体结论都必须通过。把命令或检查、覆盖 ID、结果、简短摘要、执行快照和必要报告路径写入 `.tasks/evidence/<TASK-ID>.yaml`；不要把大段原始日志写入 YAML。

验证与结果必须绑定任务卡 fingerprint、Git HEAD（可用时）和 dirty/clean 状态，避免旧证据被错误复用。fingerprint 只覆盖目标、范围、约束、禁止项、验收、关系、并行策略、风险和升级条件等稳定验证依据；排除主状态、验证元数据、Owner、时间戳和结果证据。默认使用 `canonical-json-v1`：字符串换行归一为 LF，映射键按 Unicode 码点递归排序，数组保序，输出无 BOM、无尾随换行的紧凑 UTF-8 JSON，再计算 SHA-256。

## 用户验收闸门

全部 required 自动化证据通过后：

1. 将任务设为 `awaiting_acceptance`。
2. 持久化 AC/VER 证据、执行快照和验证机制偏差。
3. 向用户提供当前任务可直接执行的 E2E 清单：验收对象、环境/账号/权限、配置与数据、逐步操作、逐步预期、证据、清理和判定。
4. AI/Agent 功能额外列出固定提示词、页面/会话上下文、预期工具、必须事实、禁止内容、重复次数、模型/提示词/参数和一致性阈值。实际调用非确定性模型时至少运行两次、通常三次；确定性模拟不能代替模型表现评估。
5. 停止等待用户决定。

用户拒绝后返回 `in_progress`，由同一 Coding Owner 修复并重跑相关自动化。用户明确整体验收通过后，记录一次 `user_acceptance`、`accepted_at`，再标记 `done`。

刷新 hard 关系已满足的后续任务，但不得自动领取下一张任务。

## 任务归档

只有用户已经明确验收且状态为 `done` 的任务可以归档。归档前必须：

1. 用户验收证据已写入 evidence；
2. 因该任务完成而满足 readiness 的后续任务已经刷新；
3. 其他任务引用、fingerprint 和索引在归档命令的预检中通过。

随后运行 `python -X utf8 .tasks/tools/taskctl.py archive TASK-ID --work-package WORK-PACKAGE`。命令会做迁移前后校验，把 task、verification（如有）和 evidence 移入同一历史包，并重建活动索引与归档 manifest。`pending`、`ready`、`in_progress`、`awaiting_acceptance`、`blocked` 和 `needs_arch_review` 不得归档。归档任务仍可作为 hard 关系解析，但不会进入普通角色上下文。

## 文档和 Git

- 任务领取和状态只更新 task card；验证设计只更新 verification；执行、修复和用户验收证据只更新 evidence。
- 单张任务完成时不更新 `docs/PROGRESS.md`；整个功能包完成并通过全局验收后更新一次。
- 任务经用户验收通过并收口后，可为涉及的各仓库生成简短提交说明供用户使用；实际 Git 操作仍取决于明确授权。
- 不创建任务介绍、独立实现设计、下一任务提示词或重复总结文档。
- 仅在出现值得长期保留的问题时创建问题记录，并从任务证据引用。
- Agent 不执行 Git commit、push、merge 或 PR；除非用户对该操作另行明确授权。

## 工具能力边界

`taskctl` 校验结构性关联、hard 环、就绪前提、引用、指纹、索引及归档哈希；不自动领取任务、不自动刷新主状态、不执行测试，也不证明 AC/VER/UAT 的完整覆盖、证据真实性或人工验收有效性。调用者仍须履行本文验收闸门。并发领取不是原子操作：共享工作区须由单一协调者先持久化 Owner；隔离副本合并前复核唯一 Owner。

`done` 是归档前的短暂活动状态：写入用户验收与 accepted_at、刷新后继后，直接运行 archive；普通 validate 拒绝留在活动区的 done，archive 内部预检允许当前待归档任务。
