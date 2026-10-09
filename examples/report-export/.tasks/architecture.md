# 个人报告导出工作包（虚构）

## Goal
已授权用户下载自己的报告；未经授权不得读取他人数据。
## Assumption Decisions
稳定字段契约允许导出服务与提示组件独立实现；最终集成验证需同时可用。
## Context
虚构契约：CSV 只含 report_id、title；UTF-8，包含标题行。
## Global Constraints
身份由服务端建立；导出只限当前用户可访问报告。
## Forbidden
不得信任客户端 user_id；不得在错误时返回其他用户数据。
## Global Acceptance Intent
本人数据下载正确，越权失败关闭，错误可见。
## Key Risks
权限遗漏、CSV 字段漂移、失败被当成功。
## Architecture Escalation Conditions
新增公开字段、共享数据范围或更换授权边界需要决策。
