---
tags: zhihu-article
zhihu-link: https://zhuanlan.zhihu.com/p/1949603330578953873
---
![](https://pic2.zhimg.com/v2-0dee9824ab0579527a569ed5db162467_1440w.jpg)

  

**`broom`包用于将统计模型输出转换为整洁的数据框格式（`data.frame`），让原本仅用于查看的文本信息（例如`summary()`）变成可直接用于后续分析处理的、结构化的数据框。**

* * *

## 一、核心函数

`broom`以整洁的`tibble()`汇总模型的关键信息。`broom`提供三个动词，方便与模型对象交互：

-   [tidy()](https://link.zhihu.com/?target=https%3A//generics.r-lib.org/reference/tidy.html) 汇总有关模型组件的信息
-   [glance()](https://link.zhihu.com/?target=https%3A//generics.r-lib.org/reference/glance.html) 报告有关整个模型的信息
-   [augment()](https://link.zhihu.com/?target=https%3A//generics.r-lib.org/reference/augment.html) 向数据集添加有关观测的信息

> 摘自：[Convert Statistical Objects into Tidy Tibbles • broom](https://link.zhihu.com/?target=https%3A//broom.tidymodels.org/)

## 二、使用示例

先加载包

```ada
library(tidyverse)
library(broom)
```

### 1\. 上手快速总结模型

```ada
model <- lm(mpg ~ wt + cyl, data = mtcars)

tidy(model)
glance(model)
augment(model)
```

全都是整洁的`tibble`（是一种`data.frame`）

![](https://pic3.zhimg.com/v2-acd28e008c1bc59598b92bdf10cf1fac_1440w.jpg)

### 2\. 模型的批量比较

**先建立四个模型，存入列表：**

```ada
models <- list(
  model1 = lm(mpg ~ wt, data = mtcars),
  model2 = lm(mpg ~ wt + cyl, data = mtcars),
  model3 = lm(mpg ~ wt + cyl + hp, data = mtcars),
  model4 = lm(mpg ~ wt + cyl + hp + gear, data = mtcars)
)
```

-   **直接`unnest()`法**

```ada
tibble(Model = names(models)) |>
  mutate(
    Glance = map(models, glance)
  ) |>
  unnest(Glance)
```

![](https://pica.zhimg.com/v2-39cf0fa72d7a10cb2a086ef9fb6470e6_1440w.jpg)

-   **嵌套数据框法**

嵌套数据框法具有独特的工作流

> 详情见我之前写的文章：[【R 语言】一种基于嵌套数据框的工作流](https://zhuanlan.zhihu.com/p/1944921736941384138)

```ada
models_results <- tibble(Model = names(models)) |>
  mutate(
    Tidy = map(models, tidy),
    Glance = map(models, glance),
    Augment = map(models, augment)
  )
```

嵌套数据框的形式

![](https://pic4.zhimg.com/v2-8a6b8dffb8628e9ab5fb1a78a77c94cb_1440w.jpg)

**嵌套数据框的批量格式化导出：**

> 详情见我之前写的文章：[【R 语言】一种基于嵌套数据框的工作流](https://zhuanlan.zhihu.com/p/1944921736941384138)

```ada
setwd("D:/ObsidianDirectory/R/【R 语言】broom 包进行整洁建模")
# 此处用到上述那篇文章封装的函数
models_results |> export_all_nested_to_xlsx(output_dir = "./output")
models_results |> export_all_nested_to_xlsx(output_dir = "./output", rev = T)
```

![](https://pic4.zhimg.com/v2-9749f8797bacc056995bd91ff5f6b79f_1440w.jpg)

格式化导出为.xlsx

![](https://picx.zhimg.com/v2-2c8311218c6af5aa50f504c7be419613_1440w.jpg)

并且整理至各表各sheet中

两种导出方式的效果：

![3*4=12 sheets](https://pic2.zhimg.com/v2-c48a8bdc7b6a8f26cb7c18931368c76d_1440w.jpg)![4*3=12 sheets](https://pic1.zhimg.com/v2-843c0ad3c41009f69ee809e05f10ded8_1440w.jpg)

* * *

声明：

本文章仅介绍`broom`包的几个初级函数用法，及其可结合方法，不涉及后续分析与优化。

参考：

-   在此感谢**张敬信**老师推广整洁风格的`broom`包：

[【Tidyverse优雅编程】tidy 风格解决线性回归问题](https://zhuanlan.zhihu.com/p/1949234140554724995)

-   /：

[R语言机器学习框架tidymodels-broom包](https://zhuanlan.zhihu.com/p/613765212)

-   官网：

[Convert Statistical Objects into Tidy Tibbles • broom](https://link.zhihu.com/?target=https%3A//broom.tidymodels.org/)

-   我之前写的文章：

[【R 语言】一种基于嵌套数据框的工作流](https://zhuanlan.zhihu.com/p/1944921736941384138)