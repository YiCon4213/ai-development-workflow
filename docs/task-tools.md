# 任务工具使用

`taskctl` 用于按角色读取任务、检查关联与验证指纹、生成索引和归档。运行环境：Python 3.10+、PyYAML。

## 准备

将来源项目的 requirements.txt 复制到目标项目 `.workflow/requirements.txt`，在目标项目根目录运行：

```sh
python -m pip install -r .workflow/requirements.txt
```

## 常用操作

Task ID 和工作包名按实际替换：

```sh
python -X utf8 .tasks/tools/taskctl.py list
python -X utf8 .tasks/tools/taskctl.py show TASK-001
python -X utf8 .tasks/tools/taskctl.py context TASK-001 --role coding-owner
python -X utf8 .tasks/tools/taskctl.py fingerprint TASK-001
python -X utf8 .tasks/tools/taskctl.py reindex
python -X utf8 .tasks/tools/taskctl.py validate
python -X utf8 .tasks/tools/taskctl.py archive TASK-001 --work-package report-export
```

`--root` 可在子命令前指定项目根目录。空库校验结果为 `PASS: 0 task cards validated`。

工具不自动领取或刷新主状态，不执行产品测试，也不代替用户验收。检查范围见 [数据契约](data-contracts.md)；等价维护方式见 [接入指南](adoption.md#无-python-时怎样维护)。

## 运行本包检查

在本工作流项目根目录运行：

```sh
python -m pip install -r requirements.txt
python -X utf8 project-template/.tasks/tools/taskctl.py --root project-template validate
python -X utf8 project-template/.tasks/tools/taskctl.py --root examples/report-export validate
python -m unittest discover -s tests -v
```
