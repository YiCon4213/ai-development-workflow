# 贡献指南

修改前明确解决的可观察问题。保留三个角色的单向交接、编码前独立 oracle、单任务执行所有权、人工验收闸门及授权边界。

结构或状态规则变更应同步技能、WORKFLOW、数据契约、模板、示例及工具测试。不要给每个业务栈加入默认必读规范；专项说明按条件加载。示例必须为虚构并显式标记，禁止复制客户任务、账号、日志或内部地址。

本地验证：

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -X utf8 project-template/.tasks/tools/taskctl.py --root project-template validate
python -X utf8 project-template/.tasks/tools/taskctl.py --root examples/report-export validate
```

PR 说明问题、修改后的行为、实际验证结果及兼容影响。文档和静态测试不能证明 Agent 行为；更改角色决策逻辑时，另提供独立上下文的真实场景评估及偏差记录。不要以通过结构校验代替行为验证。
