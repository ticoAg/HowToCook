# 基于原项目的处理及应用

## Tasks

-   [x] extract_data: 提取原始的菜谱数据, 数据检视, 数据处理
-   [ ] tag: 对菜谱进行分类/打标签

## Usage

> 使用 [[uv]](https://docs.astral.sh/uv/) [[uv-doc-zh]](https://hellowac.github.io/uv-zh-cn) 进行`python`环境的管理

### How to use uv?

1. 安装 uv(可以使用 pip 安装)

```shell
# 使用pip安装
pipx install uv
# For macOS & Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 创建虚拟环境

```shell
cd HowToCook
uv venv
```

3. 激活运行环境

```shell
# Windows
.venv\Scripts\activate.bat
# macOS & Linux
source .venv/bin/activate
```

4. 同步依赖

```shell
uv sync
```

## 启动服务

> 服务集成在`tasks\server.py`

```shell
# 此处假定已安好依赖
python tasks/server.py
```

## Problem

当前对于菜谱文档的解析存在一定无法处理之处,由于是共建,大家对于各部分的格式,表述形式无法严格统一,故此处主要关注的菜谱所需材料的提取(二级标题:`必备原料和工具`),无法做的很细

此处尽量的提取出关键元素,可以观察程序启动初始化时的`Warning`日志,即认为数据不是很干净的,后续大概率也不太会进行篇章级细致的处理

原始数据示例:

```markdown
## 必备原料和工具

-   125ml 淡奶油
-   250ml 椰树牌椰汁
-   35ml espresso 意式浓缩
-   50ml 椰子水
-   10g 吉利丁(gelatin)
-   过滤网（可选）
-   （那个...有摆盘需求的话，可以来点蓝莓 and/or 咖啡粉）

## 必备原料和工具

-   淡奶油
-   糖
-   原味酸奶
-   吉利丁片
-   筛网

## 必备原料和工具

-   原料:
    -   奇异果
    -   苹果
    -   菠菜叶（ 2-5 片）
    -   水
    -   白砂糖
-   工具
    -   榨汁机

## 必备原料和工具

-   饮用水
-   大米
-   糯米
-   花生
-   红豆
-   红枣
-   粥锅（普通锅容易糊底，有条件可选择高压锅）
-   中号玻璃碗（或其他中号不锈钢容器）
-   小碗若干

## 必备原料和工具

-   西红柿
-   鸡蛋
-   香油
-   味素
-   盐
-   葱、姜、蒜
```
