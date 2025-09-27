**Anonymous Functions**

1.  Concise code: No need for naming, directly embed logic, reduce redundancy
2.  Use and discard: Suitable for one-time simple processing, no need to maintain functions separately
3.  Clear context: Logic presented nearby, avoiding jumping to view definitions

* * *

## Three Basic Syntaxes of R Anonymous Functions

### 1. Standard Anonymous Function

```R
function(parameters) { ... }
```

### 2. Simplified Anonymous Function

```R
\(parameters) { ... }
```

A concise syntax introduced in R 4.1.0+, replacing `function()` with `\()`

### 3. `purrr` Anonymous Function

```R
~ { ... }
```

A special syntax supported by the `purrr` package, formula style, starting with `~`, **no need to explicitly declare parameters**:

-   Single parameter is referred to as `.`
-   Two parameters are referred to as `.x`/`.y` or `..1`/`..2`

## Single Parameter

```R
library(tidyverse)
# Example data: mixed strings containing numbers
demo1 <- c(
  "张三_88分", "李四_95", "王五：72",
  "赵六_59", "89.孙七", "周八-81"
)
```

*Task: Calculate the average score:*

### 1. Standard Anonymous Function

```R
result1_1 <- map_dbl(
  .x = demo1,
  .f = function(x) {  # Standard anonymous function definition
    str_extract(x, "\\d+") |> as.numeric()
  }
)
> result1_1
[1] 80.66667
```

### 2. Simplified Anonymous Function

```R
result1_2 <- map_dbl(
  .x = demo1,
  .f = \(x) {  # Simplified anonymous function definition
    str_extract(x, "\\d+") |> as.numeric()
  }
)
> result1_2
[1] 80.66667
```

### 3. `purrr` Anonymous Function

```R
result1_3 <- map_dbl(
  .x = demo1,
  .f = ~ {
    str_extract(., "\\d+") |> as.numeric()
  }
)
> result1_3
[1] 80.66667
```

**Result consistency**: All three writing methods return exactly the same numeric vector.

## Two Parameters

Calculate relative scores and determine pass status based on two columns of data, demonstrating the application of two-parameter anonymous functions.

```R
library(tidyverse)
# Example data: score and full score data frame
demo2_df <- tibble(
  scores = c(89, 85, 80, 60),
  full_scores = c(150, 120, 140, 100)
)
```

-   scores (subject scores)
-   full_scores (subject full marks)

*Task: Calculate whether the subject is passed:*

### 1. Standard Anonymous Function

```R
result2_1 <- map2_chr(
  .x = demo2_df$scores,
  .y = demo2_df$full_scores,
  .f = function(x, y) {
    relative_score <- x / y
    if (relative_score >= 0.6) "合格" else "不合格"
  }
)
> result2_1
[1] "不合格" "合格"   "不合格" "合格"
```

### 2. Simplified Anonymous Function

```R
result2_2 <- map2_chr(
  .x = demo2_df$scores,
  .y = demo2_df$full_scores,
  .f = \(x, y) {
    relative_score <- x / y
    if (relative_score >= 0.6) "合格" else "不合格"
  }
)
> result2_3.2
[1] "不合格" "合格"   "不合格" "合格"
```

### 3. `purrr` Anonymous Function

```R
# Method A: Using .x/.y to refer to two parameters
result2_3.1 <- map2_chr(
  .x = demo2_df$scores,
  .y = demo2_df$full_scores,
  .f = ~ {
    relative_score <- .x / .y  # .x corresponds to the first parameter, .y to the second
    if (relative_score >= 0.6) "合格" else "不合格"
  }
)

# Method B: Using ..1/..2 to refer to first parameter/second parameter
result2_3.2 <- map2_chr(
  .x = demo2_df$scores,
  .y = demo2_df$full_scores,
  .f = ~ {
    relative_score <- ..1 / ..2  # ..1 corresponds to the first parameter, ..2 to the second
    if (relative_score >= 0.6) "合格" else "不合格"
  }
)
> result2_1
[1] "不合格" "合格"   "不合格" "合格"  
> result2_2
[1] "不合格" "合格"   "不合格" "合格"
```

**Result consistency**: All four writing methods return exactly the same judgment results.

## Multiple Parameters

Similarly.

```R
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

-   id (product ID)
-   cost (cost)
-   base_price (base selling price)
-   discount_rates (discount rates)
-   tax_rates (tax rates)
-   min_profit (minimum profit requirement)

Tasks:

1.  `Final price = Base price × Discount rate × (1 + Tax rate)`
2.  `Profit = Final price - Cost`
3.  If `Profit ≥ Minimum profit requirement`, then "符合要求" (Meets requirements), otherwise "利润不足" (Insufficient profit)

```R
result3_1 <- pmap_chr(
  .l = list(products$base_price, products$cost, discount_rates, tax_rates, min_profit),
  .f = function(price, cost, disc, tax, min_prof) { # 5 parameters
    final_price <- price * disc * (1 + tax)
    profit <- final_price - cost
    if (profit >= min_prof) "符合要求" else "利润不足"
    }
  )

result3_2 <- pmap_chr(
  .l = list(products$base_price, products$cost, discount_rates, tax_rates, min_profit),
  .f = \(price, cost, disc, tax, min_prof) { # 5 parameters
    final_price <- price * disc * (1 + tax)
    profit <- final_price - cost
    if (profit >= min_prof) "符合要求" else "利润不足"
    }
  )

result3_3 <- pmap_chr(
  .l = list(products$base_price, products$cost, discount_rates, tax_rates, min_profit),
  .f = ~ { # 5 parameters
    final_price <- ..1 * ..3 * (1 + ..4)
    profit <- final_price - ..2
    if (profit >= ..5) "符合要求" else "利润不足"
    }
  )    
# It's worth mentioning: In multi-parameter scenarios
# Since .z and other placeholders are not supported
# `purrr` anonymous functions are not suitable for using .x/.y notation
> result3_1
[1] "符合要求" "符合要求" "利润不足" "符合要求" "符合要求" "符合要求"
> result3_2
[1] "符合要求" "符合要求" "利润不足" "符合要求" "符合要求" "符合要求"
> result3_3
[1] "符合要求" "符合要求" "利润不足" "符合要求" "符合要求" "符合要求"
```

## Supporting R 4.1.0 Pipe Operator `|>` Parameter Passing

Can completely replace `%>%` and `.`, embrace pipe operators and anonymous functions.

*Generate 5 random numbers between 90% and 110% of 100 (i.e., 90 to 110):*

No need to load any packages.

```R
> 100 |> {function(x) runif(n = 5, min = x * 0.9, max = x * 1.1)}()
[1]  90.66307  98.13106  94.21186  97.03786 107.08260
> 100 %>% {function(x) runif(n = 5, min = x * 0.9, max = x * 1.1)}()
[1]  92.61766 102.39945 106.84165  90.16113 106.17477
> 100 |> {\(x) runif(n = 5, min = x * 0.9, max = x * 1.1)}()
[1]  90.45097 108.74709 101.62091  95.89730 107.91112
> 100 %>% {\(x) runif(n = 5, min = x * 0.9, max = x * 1.1)}()
[1]  96.02148  90.71566 103.00370 106.33754  93.41225
```

Currently does not support `purrr` syntax:

```R
> 100 |> {~ runif(n = 5, min = .x * 0.9, max = .x * 1.1)}() # Not supported
Error: attempt to apply non-function
> 100 %>% {~ runif(n = 5, min = .x * 0.9, max = .x * 1.1)}() # Not supported
Error in 100 %>% { : attempt to apply non-function
```

## Summary

| Function Form | Syntax Features | Application Scenarios |
| ------------- | --------------- | --------------------- |
| function(x) { ... } | Explicitly declare parameters | Strongest compatibility, no need to load packages |
| \(x) { ... } | Explicitly declare parameters | Stronger compatibility, concise, supported in R 4.1.0 and above, no need to load packages |
| ~ { ... } | Non-explicit parameter names | Weaker compatibility, concise, built into purrr package, mainly used with its map functions |

In R 4.1.0 and above, \(x) can be said to be completely equivalent to function(x)

If the function body has only one line, the {} of anonymous functions can be omitted, for example:

```R
map_int(c(2, 3, 4), function(ele) ele^2)
#[1]  4  9 16
map_chr(c("apple", "banana", "cherry"), \(fr) paste0("fruit_", fr))
#[1] "fruit_apple"  "fruit_banana" "fruit_cherry"
map_dbl(c(1, 10, 10*sqrt(10)), ~ log10(.x))
#[1] 0.0 1.0 1.5
```

The three forms have basically the same functionality; the choice mainly depends on needs, code readability, and personal habits. In team collaboration, maintaining a unified style is more important.

* * *

Appendix:

![purrr::cheatsheet](https://pic3.zhimg.com/v2-5a3d578a0218f691f72020fcf6398330_1440w.jpg)

References:

[优雅的循环迭代和泛函数编程-purr packages 和 map 函数](https://link.zhihu.com/?target=https%3A//blog.csdn.net/nixiang_888/article/details/123826084)[【Tidyverse优雅编程】管道符：是时候用 |>替代 %>% 了吗？](https://zhuanlan.zhihu.com/p/1942366213322807149)

Declaration: The examples in this article are for comparison purposes only; direct vector operations are better in actual scenarios.