![](https://pic2.zhimg.com/v2-0dee9824ab0579527a569ed5db162467_1440w.jpg)



**The `broom` package is used to convert statistical model outputs into tidy data frame formats (`data.frame`), transforming text information that was originally only for viewing (such as `summary()`) into structured data frames that can be directly used for subsequent analysis and processing.**

* * *

## I. Core Functions

`broom` summarizes key information about models in tidy `tibble()` format. `broom` provides three verbs to facilitate interaction with model objects:

-   [tidy()](https://link.zhihu.com/?target=https%3A//generics.r-lib.org/reference/tidy.html) summarizes information about model components
-   [glance()](https://link.zhihu.com/?target=https%3A//generics.r-lib.org/reference/glance.html) reports information about the entire model
-   [augment()](https://link.zhihu.com/?target=https%3A//generics.r-lib.org/reference/augment.html) adds informations about observations to a dataset

> Source: [Convert Statistical Objects into Tidy Tibbles • broom](https://link.zhihu.com/?target=https%3A//broom.tidymodels.org/)

## II. Usage Examples

First, load the packages

```R
library(tidyverse)
library(broom)
```

### 1. Quick Model Summary

```R
model <- lm(mpg ~ wt + cyl, data = mtcars)

tidy(model)
glance(model)
augment(model)
```

All are tidy `tibble`s (a type of `data.frame`)

![](https://pic3.zhimg.com/v2-acd28e008c1bc59598b92bdf10cf1fac_1440w.jpg)

### 2. Batch Comparison of Models

**First, create four models and store them in a list:**

```R
models <- list(
  model1 = lm(mpg ~ wt, data = mtcars),
  model2 = lm(mpg ~ wt + cyl, data = mtcars),
  model3 = lm(mpg ~ wt + cyl + hp, data = mtcars),
  model4 = lm(mpg ~ wt + cyl + hp + gear, data = mtcars)
)
```

-   **Direct `unnest()` Method**

```R
tibble(Model = names(models)) |>
  mutate(
    Glance = map(models, glance)
  ) |>
  unnest(Glance)
```

![](https://pica.zhimg.com/v2-39cf0fa72d7a10cb2a086ef9fb6470e6_1440w.jpg)

-   **Nested Data Frame Method**

The nested data frame method has a unique workflow

> For details, see my previous article:[【R Language】A Workflow Based on Nested Data Frames](https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91A%20Workflow%20Based%20on%20Nested%20Data%20Frames.md)

```R
models_results <- tibble(Model = names(models)) |>
  mutate(
    Tidy = map(models, tidy),
    Glance = map(models, glance),
    Augment = map(models, augment)
  )
```

Nested data frame format

![](https://pic4.zhimg.com/v2-8a6b8dffb8628e9ab5fb1a78a77c94cb_1440w.jpg)

**Batch Formatted Export of Nested Data Frames:**

> For details, see my previous article:[【R Language】A Workflow Based on Nested Data Frames](https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91A%20Workflow%20Based%20on%20Nested%20Data%20Frames.md)

```R
setwd("D:/ObsidianDirectory/R/【R 语言】broom 包进行整洁建模")
# This uses functions encapsulated in the article mentioned above
models_results |> export_all_nested_to_xlsx(output_dir = "./output")
models_results |> export_all_nested_to_xlsx(output_dir = "./output", rev = T)
```

![](https://pic4.zhimg.com/v2-9749f8797bacc056995bd91ff5f6b79f_1440w.jpg)

Formatted export to .xlsx

![](https://picx.zhimg.com/v2-2c8311218c6af5aa50f504c7be419613_1440w.jpg)

And organized into separate sheets
The effects of the two export methods:

![3*4=12 sheets](https://pic2.zhimg.com/v2-c48a8bdc7b6a8f26cb7c18931368c76d_1440w.jpg)![4*3=12 sheets](https://pic1.zhimg.com/v2-843c0ad3c41009f69ee809e05f10ded8_1440w.jpg)

* * *

Declaration:

This article only introduces the usage of several basic functions of the `broom` package and their combinable methods, and does not involve subsequent analysis and optimization.

References:

-   Thanks to teacher **张敬信** for promoting the tidy-style `broom` package:

[【Tidyverse优雅编程】tidy 风格解决线性回归问题](https://zhuanlan.zhihu.com/p/1949234140554724995)

-   /：

[R语言机器学习框架tidymodels-broom包](https://zhuanlan.zhihu.com/p/613765212)

-   Official website:

[Convert Statistical Objects into Tidy Tibbles • broom](https://link.zhihu.com/?target=https%3A//broom.tidymodels.org/)

-   My previous article:

[【R Language】A Workflow Based on Nested Data Frames](https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91A%20Workflow%20Based%20on%20Nested%20Data%20Frames.md)
