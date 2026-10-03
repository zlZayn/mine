---
tags: zhihu-article
zhihu-link: https://zhuanlan.zhihu.com/p/1946672841723454894
---
![mice r package logo](https://pica.zhimg.com/v2-517d187895cdc2734f566b6918daa350_1440w.jpg)

```ada
> packageVersion("mice") # 本文章所使用 mice 包版本
[1] ‘3.18.0’
```

![MICE 方法示意图](https://pic2.zhimg.com/v2-6c24556374d7eae28580a9663eec1de9_1440w.jpg)

`mice`包（Multivariate Imputation by Chained Equations）是 R 语言中处理缺失值的工具包，核心作用是通过**链式方程多重插补法**生成多个完整数据集（而非单一填充结果），相比简单填充（如均值法），能更好保留数据分布和变量关系，尤其适合复杂缺失模式。

**特殊 R 对象（R objects）的类型：**

| 特殊 R 对象的类型名称 | 全称 | 来源 | 作用 |
| ----- | ----- | ----- | ----- |
| mids | Multiply Imputed Data Set | mice() 生成 | 存多重插补数据集 |
| mira | Multiply Imputed Repeated Analyses | with() 分析 mids | 存各数据集单独分析结果 |
| mipo | Multiply Imputed Pooled Results | pool() 合并 mira | 合并得最终统计量 |

`mice` 包主要具有下列功能：

1.  **为含缺失值的变量构建预测模型**
2.  **生成多个插补数据集**
3.  **后续批量建模并整合结果**

* * *

**多重插补缺失数据** → **多套数据批量建模 → 合并模型结果**

```ada
library(tidyverse)
library(mice)
```

## 1\. 数据与缺失值查看

```ada
data(airquality)
# 内置空气质量数据集

airquality |> glimpse()
# 预览 airquality 的数据结构

airquality |> map_int(\(c) sum(is.na(c)))
# 查看每列缺失值

md.pattern(airquality)
# 统计及可视化缺失值模式
```

![](https://pic4.zhimg.com/v2-d4c3a10c3f51c4b8d8b55eca660d5cf3_1440w.jpg)![](https://pic2.zhimg.com/v2-cd9463c43dd9608965d97f00d3b18af3_1440w.jpg)![md.pattern()](https://pic3.zhimg.com/v2-3010c7bab286c18304673298561bba60_1440w.jpg)| md.pattern() 结果描述 | 解读 |
| ----- | ----- |
| 每行最左侧数字 | 该模式（pattern）的总出现频数 |
| 中间的 1（蓝）和 0（红） | 表示该模式下每行（观测）各列（变量）是否有缺失值 |
| 每行最右侧数字 | 该模式下每行（观测）缺失值总数 |
| 每列底部数字 | 每列（变量）的总缺失值总数 |

## 2\. mice() 多重插补

```ada
set.seed(123)

mids <- airquality |> 
  mice(m = 5, method = "pmm")
# 预测均值匹配，5 重插补

stripplot(mids, chl)
# 绘制原数据与 5 个插补后数据的，含缺失值标记的带状图
```

![红色表示插补标记](https://pic1.zhimg.com/v2-813b746bb0dec29a591f74a791bb9892_1440w.jpg)

## 3\. complete() 提取插补后的 data.frame

```ada
imputed_data_3 <- mids |> 
  complete(3)
# 仅提取第三套 data.frame

imputed_data_3 |> map_int(\(c) sum(is.na(c)))
# 验证每列缺失值
```

![](https://pica.zhimg.com/v2-3bbc3caedc6742972d9cf6253ab105d6_1440w.jpg)![](https://pic1.zhimg.com/v2-dc404ea28cad69257a0b733383711244_1440w.jpg)

也可以一次性提取所有完整插补数据集，有下列五种方式：

```ada
walk2(
  c("ALL", "STACKED", "LONG", "BROAD", "REPEATED"),
  c("all", "stacked", "long", "broad", "repeated"),
  \(name, arg) assign(name, complete(mids, action = arg), envir = .GlobalEnv)
  )
# 会在全局环境生成这 5 个对应不同插补结果格式的对象
```

| action = 参数 | 对象类型 | 特征 |
| ----- | ----- | ----- |
| "all" | 列表 | 每个元素是一个完整插补数据集 |
| "stacked" | 长格式数据框 |  |
| "long" | 长格式数据框 | 附加 .imp（插补集）和 .id（行索引）标记 |
| "broad" | 宽格式数据框 |  |
| "repeated" | 宽格式数据框 | 重复宽格式 |

## 4\. with() 批量建模

```ada
mira <- mids |> 
  with(lm(Ozone ~ Solar.R + Wind + Temp + Month + Day))
# 批量拟合相同线性回归模型

mira_analysis <- mira |> summary()
# 可以得到 5 个模型的汇总结果
```

![](https://pica.zhimg.com/v2-b34a628e5603e647475011aae1874680_1440w.jpg)

## 5\. pool() 合并分析结果

```ada
mipo <- mira |>
  pool()
# 基于统计理论，一键合并分析得到最终结果

mipo_analysis <- mipo |> summary()
# 得到合并模型的最终汇总结果
```

![](https://pic3.zhimg.com/v2-30b7a61ab4fbabb96e079bd0ad82e9ca_1440w.jpg)

从表格中可以得到**最终的线性回归方程**

$$Ozone = -66.096 + 0.048 Solar.R - 3.012 Wind + 1.859 Temp - 2.875 Month + 0.304 Day$$

  

本文中 **R 对象（R objects）**的类型

![R objects&#39; types](https://pic3.zhimg.com/v2-8d0cf23c32bf2ddd654640f9723ff392_1440w.jpg)![MICE 方法示意图](https://pic2.zhimg.com/v2-6c24556374d7eae28580a9663eec1de9_1440w.jpg)

* * *

附：

`mice` 包中内置的单变量插补方法（univariate imputation methods）

| 插补方法名称 | 适用数据类型 | 方法全称 / 说明 |
| ----- | ----- | ----- |
| pmm | any | Predictive mean matching |
| midastouch | any | Weighted predictive mean matching |
| sample | any | Random sample from observed values |
| cart | any | Classification and regression trees |
| rf | any | Random forest imputations |
| mean | numeric | Unconditional mean imputation |
| norm | numeric | Bayesian linear regression |
| norm.nob | numeric | Linear regression ignoring model error |
| norm.boot | numeric | Linear regression using bootstrap |
| norm.predict | numeric | Linear regression, predicted values |
| lasso.norm | numeric | Lasso linear regression |
| lasso.select.norm | numeric | Lasso select + linear regression |
| quadratic | numeric | Imputation of quadratic terms |
| ri | numeric | Random indicator for nonignorable data |
| logreg | binary | Logistic regression |
| logreg.boot | binary | Logistic regression with bootstrap |
| lasso.logreg | binary | Lasso logistic regression |
| lasso.select.logreg | binary | Lasso select + logistic regression |
| polr | ordered | Proportional odds model |
| polyreg | unordered | Polytomous logistic regression |
| lda | unordered | Linear discriminant analysis |
| 2l.norm | numeric | Level - 1 normal heteroscedastic |
| 2l.lmer | numeric | Level - 1 normal homoscedastic, lmer |
| 2l.pan | numeric | Level - 1 normal homoscedastic, pan |
| 2l.bin | binary | Level - 1 logistic, glmer |
| 2lonly.mean | numeric | Level - 2 class mean |
| 2lonly.norm | numeric | Level - 2 class normal |
| 2lonly.pmm | any | Level - 2 class predictive mean matching |

* * *

参考：

[mice](https://link.zhihu.com/?target=https%3A//amices.org/mice/)[处理缺失值之多重插补（Multiple Imputation）](https://zhuanlan.zhihu.com/p/36436260)[缺失值的高级处理：用mice进行多重填补](https://link.zhihu.com/?target=https%3A//cloud.tencent.com/developer/article/1972392)[R语言缺失值判断与处理mice包-3_r mice-CSDN博客](https://link.zhihu.com/?target=https%3A//blog.csdn.net/LeaningR/article/details/120145073)