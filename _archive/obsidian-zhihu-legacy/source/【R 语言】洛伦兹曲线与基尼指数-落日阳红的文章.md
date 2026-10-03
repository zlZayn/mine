---
tags: zhihu-article
zhihu-link: https://zhuanlan.zhihu.com/p/1951089194756703939
---
**洛伦兹曲线（Lorenz Curve）** 和 **基尼指数（Gini Index）**是衡量不平等程度的重要工具。其广泛应用于宏观经济、医疗、教育等领域。

> 洛伦兹（Max Otto Lorenz，1876年12月19日—1959年7月1日），美国统计学家，于1905年提出衡量社会收入分配不公平程度的洛伦茨曲线；该成果后被意大利统计学家基尼（Corrado Gini）发展为基尼系数。

![洛伦兹曲线示意图](https://pica.zhimg.com/v2-063fe65ec9451ee54d336a066e2c4d98_1440w.jpg)

## 概念

洛伦兹曲线用于**可视化不平等**；基尼指数用于**量化不平等**。

-   **横轴**：资源占有量从低到高排序的 “人口累计百分比”
-   **纵轴**：对应横轴人口所拥有的 “资源累计百分比”

  
**洛伦兹曲线越下弯曲，越不平等**  
以洛伦兹曲线为基础：

-   $S_{A}$：洛伦兹曲线与 “绝对平等线” （下三角斜边）之间的面积
-   $S_{B}$：洛伦兹曲线与 “绝对不平等线”（下三角两条直角边）之间的面积

$$Gini = \frac{S_{A}}{S_{A} + S_{B}}$$

基尼指数取值范围：$[0, 1]$  
**值越大，越不平等**

1.  **怎么看洛伦兹曲线：它越贴近图中间的 “绝对平等线”，分配越公平；越往下偏离这条线，分配越不均。**
2.  **怎么看基尼指数：** $S_{A}$ **占** $(S_{A} + S_{B})$ **的比例越小，平等程度越高；比例越大，不平等越严重。**

![示意图](https://picx.zhimg.com/v2-6cbca6aca2ed4c962def3ab0ab1a0b95_1440w.jpg)

根据**拉格朗日中值定理**，若两点间的曲线连续可导且不与两点连线重合，则曲线上必存在两点，它们的切线斜率分别大于、小于**两点连线的斜率**。

这正是证明了有人资源分配少（斜率小于1），有人资源分配多（斜率大于1）

**洛伦兹曲线的斜率**本质就是：**每单位比例的人群（横轴），能分到的资源（纵轴）占比。**  
$$洛伦兹曲线的斜率 = \frac{资源累计占比的变化量}{人群累计占比的变化量}$$

## 加载包和数据

`ISLR`内置的`Wage`数据集：

> Wage and other data for a group of 3000 male workers in the Mid-Atlantic region.

```ada
library(tidyverse)
Wage_df <- ISLR::Wage
```

接下来是探究这3000人的`wage`分配是否平等的示例

## 一、洛伦兹曲线

### 数据预处理

计算累积人口比例和累积`wage`比例，这是绘制洛伦兹曲线的基础数据：

1.  `arrange(wage)`：**从低收入人群到高收入人群排序（关键!!!!!）**
2.  `n`：**人数**
3.  `pop_accum`：**从低收入人群到高收入人群的（因为前面按收入排序了）累计比例**
4.  `val_accum`：**从低收入人群到高收入人群的（因为前面按收入排序了）收入累计比例**
5.  `add_row(pop_accum=0,val_accum=0,.before=1)`：**加上坐标(0,0)的数据（用于画图）**

```ada
data <- Wage_df |> 
  select(wage) |> 
  arrange(wage) |> 
  mutate(
    n = n(),
    pop_accum = row_number() / n,
    val_accum = cumsum(wage) / sum(wage)
  ) |> 
  add_row(pop_accum = 0, val_accum = 0, .before = 1)
```

![数据预处理后，前8行](https://pic2.zhimg.com/v2-d042709c80cefb7fd9ae32a1a930968b_1440w.jpg)![数据预处理后，后8行](https://pic4.zhimg.com/v2-6a5aa72451de130c6e6d765a4e1b99d9_1440w.jpg)

### 绘制洛伦兹曲线

```ada
ggplot(data, aes(x = pop_accum, y = val_accum)) +
  geom_line() +
  geom_abline(intercept = 0, slope = 1, linetype = "dashed") +
  coord_cartesian(xlim = c(0, 1), ylim = c(0, 1), expand = FALSE) +
  theme_bw()
```

![洛伦兹曲线](https://pic3.zhimg.com/v2-0922d0fa580ac390a013bd8cae1d04fc_1440w.jpg)

  
洛伦兹曲线展示了`wage`分配情况，其中虚线表示绝对平等的分配，曲线越向下弯曲（远离“绝对平等线”）表示分配越不平等。（上三角不用看）

可以看出图中曲线还是比较靠近虚线的（较为平等）

## 二、基尼指数

### 计算洛伦兹曲线下面积

通过**梯形法则**计算洛伦兹曲线下的面积`area_under_Lorenz`（$S_{B}$）

```ada
area_under_Lorenz <- data |> 
  mutate(
    x_diff = pop_accum - lag(pop_accum),
    y_mean = (val_accum + lag(val_accum)) / 2
  ) |> 
  summarise(area_under_Lorenz = sum(x_diff * y_mean, na.rm = TRUE)) |> 
  pull(area_under_Lorenz)
```

  

```ada
> area_under_Lorenz # 结果
[1] 0.4045936
```

### 计算基尼指数

根据已知条件

$$S_{B} = 0.4045936$$

$$S_{A} + S_{B} = 0.5$$

$$Gini = \frac{S_{A}}{S_{A} + S_{B}}$$

联立计算基尼指数

```ada
Gini_Index = (0.5 - area_under_Lorenz) / 0.5
```

  

```ada
> Gini_Index # 结果
[1] 0.1908127
```

基尼指数`Gini_Index`用于量化`wage`的不平等程度，值为0表示完全平等，值为1表示完全不平等。  
  
0.191的基尼指数说明工资分配较为平等

* * *

附：  
  
随手画了`wage`的分布

```ada
ggplot(data, aes(wage)) +
  geom_density() +
  theme_bw()
```

![](https://pic1.zhimg.com/v2-10b75f4c20da0c66ed3394756236a662_1440w.jpg)

参考：

[The Lorenz Curve](https://link.zhihu.com/?target=https%3A//www.economicsonline.co.uk/definitions/thelorenzcurve.html/)