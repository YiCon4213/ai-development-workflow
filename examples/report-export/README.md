# 虚构示例：个人报告导出

本示例没有真实产品代码、用户账号或实际验收，所有通过记录均标明 synthetic，只演示文件与状态关系。

- TASK-001：导出字段契约，纯文档，已有虚构用户通过记录，位于归档。
- TASK-002：受权限保护的导出，依赖 TASK-001 的字段契约；独立规格 ready，所以主状态 ready。
- TASK-003：下载提示与错误显示，无 hard 前置，但 verification pending，因此主状态 pending。通过 integration_order 描述稍后需要与 TASK-002 联调，不将集成顺序伪装成领取前置。

从本工作流项目根运行 README 中的示例 validate / context 命令。这里的 tools 使示例目录本身也可以独立运行；升级工具时一并同步。本示例可在副本中练习修改状态和归档，不能作为任何真实项目的通过证据。

规格中的 `tests.test_report_export` 是虚构目标仓库的示例命令，本包不提供该业务测试；只有 taskctl 和包测试是可运行的。迁入真实项目时 Verification Owner 必须替换为已确认可执行的项目原生命令。
