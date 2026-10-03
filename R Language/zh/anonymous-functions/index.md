---
zhihu-title: 【R 语言】匿名函数
zhihu-topics: R
zhihu-link: https://zhuanlan.zhihu.com/p/1944083434071917665
zhihu-created-at: 2025-09-01 00:00
---
匿名函数（Anonymous Function）

1. 精简代码：省去命名，直接嵌入逻辑，减少冗余
2. 即用即弃：适合一次性简单处理，无需单独维护函数
3. 上下文清晰：逻辑就近呈现，避免跳转查看定义

# 匿名函数的三种基本语法

## 1. 标准匿名函数

```r
function(参数) { ... }
```

## 2. 简化匿名函数

```r
\(参数) { ... }
```

R 4.1.0+ 引入的简洁语法，用 `\()` 替代 `function()`

## 3. `purrr` 匿名函数

```r
~ { ... }
```

`purrr` 包支持的特殊语法，公式风格，用 `~` 开头，**无需显式声明参数**：

- 单参数用 `.` 指代
- 双参数用 `.x`/`.y` 或 `..1`/`..2` 指代

# 单参数

```r
library(tidyverse)
# 示例数据：含数字的混合字符串
demo1 <- c(
  "张三_88分", "李四_95", "王五：72",
  "赵六_59", "89.孙七", "周八-81"
)
```

*任务：计算平均分：*

## 1. 标准匿名函数

```r
result1_1 <- map_dbl(
  .x = demo1,
  .f = function(x) {  # 标准匿名函数定义
    str_extract(x, "\\d+") |> as.numeric()
  }
)
```

```r
> result1_1
[1] 80.66667
```

## 2. 简化匿名函数

```r
result1_2 <- map_dbl(
  .x = demo1,
  .f = \(x) {  # 简化匿名函数定义
    str_extract(x, "\\d+") |> as.numeric()
  }
)
```

```r
> result1_2
[1] 80.66667
```

## 3. `purrr` 匿名函数

```r
result1_3 <- map_dbl(
  .x = demo1,
  .f = ~ {
    str_extract(., "\\d+") |> as.numeric()
  }
)
```

```r
> result1_3
[1] 80.66667
```

**结果一致性**：三种写法返回完全相同的数值向量。


# 双参数

基于两列数据计算相对分并判断合格状态，展示双参数匿名函数的应用。

```r
library(tidyverse)
# 示例数据：分数与满分数据框
demo2_df <- tibble(
  scores = c(89, 85, 80, 60),
  full_scores = c(150, 120, 140, 100)
)
```

- scores（科目分数）  
- full_scores（科目满分）  

*任务：计算科目是否及格：*

## 1. 标准匿名函数

```r
result2_1 <- map2_chr(
  .x = demo2_df$scores,
  .y = demo2_df$full_scores,
  .f = function(x, y) {
    relative_score <- x / y
    if (relative_score >= 0.6) "合格" else "不合格"
  }
)
```

```r
> result2_1
[1] "不合格" "合格"   "不合格" "合格"  
```

## 2. 简化匿名函数

```r
result2_2 <- map2_chr(
  .x = demo2_df$scores,
  .y = demo2_df$full_scores,
  .f = \(x, y) {
    relative_score <- x / y
    if (relative_score >= 0.6) "合格" else "不合格"
  }
)
```

```r
> result2_3.2
[1] "不合格" "合格"   "不合格" "合格"
```

## 3. `purrr` 匿名函数

```r
# 方式A：用 .x/.y 指代双参数
result2_3.1 <- map2_chr(
  .x = demo2_df$scores,
  .y = demo2_df$full_scores,
  .f = ~ {
    relative_score <- .x / .y  # .x 对应第一个参数，.y 对应第二个参数
    if (relative_score >= 0.6) "合格" else "不合格"
  }
)

# 方式B：用 ..1/..2 指代 第一位参数/第二位参数
result2_3.2 <- map2_chr(
  .x = demo2_df$scores,
  .y = demo2_df$full_scores,
  .f = ~ {
    relative_score <- ..1 / ..2  # ..1 对应第一个参数，..2 对应第二个参数
    if (relative_score >= 0.6) "合格" else "不合格"
  }
)
```

```r
> result2_1
[1] "不合格" "合格"   "不合格" "合格"  
> result2_2
[1] "不合格" "合格"   "不合格" "合格"    
```

**结果一致性**：四种写法返回完全相同的判断结果

# 多参数

同理。

```r
library(tidyverse)

products <- tibble(
  id = c("#2025_178", "#2025_179", "#2025_180", "#2025_181", "#2025_182", "#2025_183"),
  cost = c(50, 80, 120, 30, 15, 90),
  base_price = c(80, 130, 180, 60, 40, 150)
  )

discount_rates <- c(0.9, 0.85, 0.7, 0.95, 0.8, 0.75)
tax_rates <- c(0.1, 0.1, 0.13, 0.1, 0.08, 0.13)
min_profit <- c(10, 20, 35, 8, 5, 22)
```

- id（编号）  
- cost（成本）  
- base_price（基础售价）
- discount_rates（折扣率）
- tax_rates（税率）
- min_profit（最低利润要求）

任务：
1. `最终售价 = 基础售价 × 折扣率 × (1 + 税率)`
2. `利润 = 最终售价 - 成本`
3. 若`利润 ≥ 最低利润要求`，则为 "符合要求"，否则为 "利润不足"

```r
result3_1 <- pmap_chr(
  .l = list(products$base_price, products$cost, discount_rates, tax_rates, min_profit),
  .f = function(price, cost, disc, tax, min_prof) { # 5 个参数
    final_price <- price * disc * (1 + tax)
    profit <- final_price - cost
    if (profit >= min_prof) "符合要求" else "利润不足"
    }
  )

result3_2 <- pmap_chr(
  .l = list(products$base_price, products$cost, discount_rates, tax_rates, min_profit),
  .f = \(price, cost, disc, tax, min_prof) { # 5 个参数
    final_price <- price * disc * (1 + tax)
    profit <- final_price - cost
    if (profit >= min_prof) "符合要求" else "利润不足"
    }
  )

result3_3 <- pmap_chr(
  .l = list(products$base_price, products$cost, discount_rates, tax_rates, min_profit),
  .f = ~ { # 5 个参数
    final_price <- ..1 * ..3 * (1 + ..4)
    profit <- final_price - ..2
    if (profit >= ..5) "符合要求" else "利润不足"
    }
  )    
# 值得一提的是：多参数场景下
# 由于不支持 `.z` 等占位符
# `purrr` 匿名函数不适合用 `.x` `.y` 的表示方法
```

```r
> result3_1
[1] "符合要求" "符合要求" "利润不足" "符合要求" "符合要求" "符合要求"
> result3_2
[1] "符合要求" "符合要求" "利润不足" "符合要求" "符合要求" "符合要求"
> result3_3
[1] "符合要求" "符合要求" "利润不足" "符合要求" "符合要求" "符合要求"
```

# 支持 R 4.1.0 管道符 `|>` 参数传递

完全可以代替 `%>%` 和 `.` 了，拥抱管道符和匿名函数吧。

*生成 5 个在 100 的 90% - 110% 之间（即 90 到 110）的随机数：*

无需加载任何包。

```r
> 100 |> {function(x) runif(n = 5, min = x * 0.9, max = x * 1.1)}()
[1]  90.66307  98.13106  94.21186  97.03786 107.08260
> 100 %>% {function(x) runif(n = 5, min = x * 0.9, max = x * 1.1)}()
[1]  92.61766 102.39945 106.84165  90.16113 106.17477
```

```r
> 100 |> {\(x) runif(n = 5, min = x * 0.9, max = x * 1.1)}()
[1]  90.45097 108.74709 101.62091  95.89730 107.91112
> 100 %>% {\(x) runif(n = 5, min = x * 0.9, max = x * 1.1)}()
[1]  96.02148  90.71566 103.00370 106.33754  93.41225
```

目前不支持`purrr`语法：
```r
> 100 |> {~ runif(n = 5, min = .x * 0.9, max = .x * 1.1)}()
Error: attempt to apply non-function
> 100 %>% {~ runif(n = 5, min = .x * 0.9, max = .x * 1.1)}()
Error in 100 %>% { : attempt to apply non-function
```

# 总结

| 函数形式              | 语法特点         | 适用场景                                             |
| --------------------- | ---------------- | ---------------------------------------------------- |
| `function(x) { ... }` | **显式声明参数** | 兼容性最强，无需加载包                               |
| `\(x) { ... }`        | **显式声明参数** | 兼容性较强，简洁，R 4.1.0 及以上版本支持，无需加载包 |
| `~ { ... }`           | **非显式参数名** | 兼容性较弱，简洁，`purrr` 包内置，                     |

三种形式功能基本一致，选择主要取决于需求、代码可读性和个人习惯。

在团队协作中，保持风格统一更为重要。

声明：本文示例仅作对比用途，实际场景中采用直接向量运算更优。