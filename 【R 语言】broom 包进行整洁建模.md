---
zhihu-title: 【R 语言】broom包进行整洁建模
zhihu-topics: R
zhihu-link: https://zhuanlan.zhihu.com/p/1949603330578953873
zhihu-created-at: 2025-09-11 22:51
---

**`broom`包用于将统计模型输出转换为整洁的数据框格式（`data.frame`），让原本仅用于查看的文本信息（例如`summary()`）变成可直接用于后续分析处理的、结构化的数据框。**

本文章仅介绍`broom`包的几个初级函数用法。

# 一、核心函数

`broom`以整洁的`tibble()`汇总模型的关键信息。`broom`提供三个动词，方便与模型对象交互：

- [tidy()](https://generics.r-lib.org/reference/tidy.html) 汇总有关模型组件的信息
- [glance()](https://generics.r-lib.org/reference/glance.html) 报告有关整个模型的信息
- [augment()](https://generics.r-lib.org/reference/augment.html) 向数据集添加有关观测的信息

> 摘自：[Convert Statistical Objects into Tidy Tibbles • broom](https://broom.tidymodels.org/)

# 二、使用示例

先加载包
```r
library(tidyverse)
library(broom)
```

## 1. 上手快速总结模型

```r
model <- lm(mpg ~ wt + cyl, data = mtcars)

tidy(model)
glance(model)
augment(model)
```

全都是整洁的`tibble`（是一种`data.frame`）

![[3fun.png]]

## 2. 模型的批量比较

### 直接`unnest()`法

```r
tibble(Model = names(models)) |>
  mutate(
    Glance = map(models, glance)
  ) |>
  unnest(Glance)
```

![[unnest().png]]

### 嵌套数据框法

具有独特的工作流

```r
models <- list(
  model1 = lm(mpg ~ wt, data = mtcars),
  model2 = lm(mpg ~ wt + cyl, data = mtcars),
  model3 = lm(mpg ~ wt + cyl + hp, data = mtcars),
  model4 = lm(mpg ~ wt + cyl + hp + gear, data = mtcars)
)

models_results <- tibble(Model = names(models)) |>
  mutate(
    Tidy = map(models, tidy),
    Glance = map(models, glance),
    Augment = map(models, augment)
  )
```

嵌套数据框的形式

![[models_results.png]]

**嵌套数据框的批量格式化导出：**

```r
# 此处用到我封装的函数
models_results |> export_all_nested_to_xlsx(output_dir = "./output")
```

![[export.png]]

格式化导出为.xlsx

![[output.png]]

并且整理至各表各sheet中

![[3xlsx.png]]
