# Data Generator for Auto-Edge

## Brief Introduction


## Quick Start
```python

```

## Docker Start
```shell

```

## Related Interface
```python
# 向调度器请求超参数 包括{分辨率、帧率、编码方式、一片多少帧、优先级、发往微服务的ip}
# (请求可以每隔若干片执行一次)
requests.get()

# 一片数据的数据结构
# {数据流id, 数据片id, 数据形式（原视频or结果）,数据内容....}
# {data flow id, task id, work dag, current step, frame resolution, frame rate, frame number, 
# encoding, worker(ip:port)，priority, data form, data content}
```
