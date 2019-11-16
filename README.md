# LewinTools

一些常用功能的封装，Python实现。

找示例用法的最好方式，是去单元测试程序中找。

## 1. Logger

仿照Python标准库`logging`写的日志类。

支持上下文管理器`with`，能够保证将日志输出到指定位置。可以选择发到`钉钉`机器人，或者Mongo数据库中。

### 示例

```python
from lewintools.base.logging import Logger
DINGTALK_API = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxx"

if __name__ == "__main__":
    with Logger() as lg:
        # 注册一个输出端，输出到Dingtalk中
        lg.add_op_dingrobot(DINGTALK_API, "Cron-job 01")
        # 运行业务函数
        run()
```

运行正常，你会在钉钉上看到：

```text
<ok> [Cron-job 01]
Start at: 2019-11-16 10:08:01
End at: 2019-11-16 10:08:05
```

异常退出，你会在钉钉上看到：

```text
<err> [Cron-job 01]
Start at: 2019-11-16 10:50:02
End at: 2019-11-16 10:50:03
Status: Failed!!
Traceback (most recent call last):
  File "xxx", line 112, in have_a_try
    xxxxx
Exception: xxxxxxxx
```

### 主要特性

1. 支持劫持`sys.stdout`和`sys.stderr`，因此可以截取系统`print`输出。
2. 支持多个输出，可以同时输出；目前支持系统输出、文件、Email、Mongo、钉钉机器人。
3. 支持自定义输出格式，类似`logging`标准库的语法：`[%(levelname)s] %(message)s`。
4. 支持钉钉的`@`功能，平时可以屏蔽钉钉机器人，如果异常它会`@`你。
4. 未做字符串性能优化，最好只把最关键的日志用它输出。
5. 与`logging`库不兼容，因为它好像也劫持了系统输出对象。

## 2. Findfiles

用于从一系列（日期不同，名字格式相同）的文件中找到最新的那个，或者是全部符合条件的。支持正则表达式。

### 示例

假设你有一系列报表文件，长这样：

```text
FX_report_20191101.csv
FX_report_20191102.csv
FX_report_20191105.csv
```

你可以用它来找到最新的那个文件：

```python
from lewintools import Findfiles

wsp = Findfiles("some dir path")
filename = wsp.find_lastone(prefix="FX_report_", fmt="%Y%m%d", postfix="\.csv")
```

### 主要特性

1. 支持`before`参数，比如找到某一天之前的最新的文件，常用于过了当天之后重新运行任务的情况。
2. 支持返回所有符合正则表达式规则的文件名。
3. 支持返回文件名中包含的时间，以`datetime`对象形式。
