---
tags: zhihu-article
zhihu-link: https://zhuanlan.zhihu.com/p/1948532373101713365
---
本文章使用**案例教学法，**推荐使用**目录**

* * *

## 一、引言

在 R 语言的 `ggplot2` 包中，`geom_*` 系列函数构成了可视化的核心元素家族，它们负责在坐标系中渲染各种几何对象。`geom_function()` 作为这个家族中的特殊成员，与 `stat_function()` 共同提供了一种直接、高效的函数绘制方式——无需预先计算大量数据点，而是通过直接传递函数表达式来实现**函数曲线的可视化**。

**对比下面两种老旧方法的代码：**

### 传统数据点法

```ada
x <- seq(-5, 5, length.out = 100)
y <- x^2 + 2*x + 1
data_df <- data.frame(x = x, y = y)

ggplot(data_df, aes(x, y)) +
  geom_line(color = "blue")
```

![传统数据点法](https://pic4.zhimg.com/v2-08a11c72d126098849736b7e677004fb_1440w.jpg)

### 直接绘制法

```ada
ggplot() +
  geom_function(fun = function(x) x^2 + 2*x + 1, 
                color = "blue") +
  xlim(-5, 5)
```

![直接绘制法](https://pic3.zhimg.com/v2-d7080e9d92c26ec4c71b055e285ce582_1440w.jpg)

效果一模一样，但代码简洁不少。

## 二、基础准备

```ada
library(ggplot2)
```

## 三、使用 geom\_function 绘制基本函数

### 1\. 线性函数

$$y = 2x + 1$$

```ada
ggplot() +
  geom_function(fun = function(x) 2 * x + 1,  # 线性函数
                color = "blue",              # 线条颜色
                linewidth = 1) +                   # 线条粗细
  xlim(-5, 5)  # x轴范围
```

![线性函数](https://pic3.zhimg.com/v2-c789d4ebe7e528bb4b9516468fc10dc6_1440w.jpg)

### 2\. 二次函数

$$y = 2x^2 - 3x + 1$$

```ada
ggplot() +
  geom_function(fun = function(x) 2 * x^2 - 3*x + 1,  # 二次函数
                color = "red",
                linewidth = 1) +
  xlim(-4, 4)
```

![二次函数](https://pic4.zhimg.com/v2-bff8ec790f6b5f9477be9f12d21dd8d7_1440w.jpg)

### 3\. 指数函数

$$y = 2^x$$

```ada
ggplot() +
  geom_function(fun = function(x) 2^x,  # 指数函数
                color = "green",
                linewidth = 1) +
  xlim(-2, 2) +
  ylim(0, 5)  # y轴范围
```

![指数函数](https://pica.zhimg.com/v2-859e59a7aa88ff6151fd98e2f9f2bfc6_1440w.jpg)

### 4\. 对数函数

$$y = \log(x)$$

```ada
ggplot() +
  geom_function(fun = function(x) log(x),  # 对数函数
                color = "purple",
                linewidth = 1) +
  xlim(0.1, 5)  # x > 0
```

![对数函数](https://pica.zhimg.com/v2-fc5d4f7f46b0a335af29d3dabb9b17f0_1440w.jpg)

### 5\. 幂函数

而且可多个叠加

$$y = x$$

$$y = x^2$$

$$y = x^3$$

```ada
ggplot() +
  geom_function(fun = function(x) x, 
                color = "blue", 
                linewidth = 1) +
  geom_function(fun = function(x) x^2, 
                color = "red", 
                linewidth = 1) +
  geom_function(fun = function(x) x^3, 
                color = "green", 
                linewidth = 1) +
  xlim(-2, 2) +
  ylim(-5, 5)
```

![多函数叠加](https://pic2.zhimg.com/v2-41fc0ae4986d7b671c341c8ac605cdaf_1440w.jpg)

### 6\. 三角函数

$$y = \sin(x)$$

$$y = \cos(x)$$

```ada
ggplot() +
  geom_function(fun = sin,  # sin函数
                color = "blue",
                linewidth = 1, 
                linetype = "solid") +
  geom_function(fun = cos,  # cos函数
                color = "red",
                linewidth = 1, 
                linetype = "dashed") +
  xlim(-pi, pi) +
  scale_x_continuous(breaks = c(-pi, -pi/2, 0, pi/2, pi),
                     labels = c("-π", "-π/2", "0", "π/2", "π"))
```

![三角函数](https://pic3.zhimg.com/v2-86aea00d5681ff887001ef6a3729cbcc_1440w.jpg)

### 7\. 导数

$$f(x) = x^3 - 2x$$

$$f'(x) = 3x^2 - 2$$

```ada
# 定义函数
f <- function(x) x^3 - 2*x  # 原函数
f_prime <- function(x) 3*x^2 - 2  # 导函数

# 绘制原函数和导函数
ggplot() +
  geom_function(fun = f, 
                color = "blue", 
                linewidth = 1.5) +
  geom_function(fun = f_prime, 
                color = "red", 
                linewidth = 1.5) +
  xlim(-3, 3) +
  ylim(-10, 10)
```

![导数可视化](https://pic3.zhimg.com/v2-ee03648502472bfe93399d74369cd24a_1440w.jpg)

## 四、使用 geom\_function 的高级技巧

### 1\. 带参数

$$y = x^2$$

$$y = x^3$$

```ada
# 定义函数
power_function <- function(x, exponent) {
  return(x^exponent)
}

# 绘制带参数的函数
ggplot() +
  geom_function(fun = power_function, args = list(exponent = 2),
                color = "blue",
                linewidth = 1) +
  geom_function(fun = power_function, args = list(exponent = 3),
                color = "red",
                linewidth = 1) +
  xlim(-2, 2) +
  ylim(-5, 5)
```

![带参数函数](https://pic3.zhimg.com/v2-1baf4eb88aa5a3d289db609d6bcffa8e_1440w.jpg)

### 2\. 内置函数

概率密度函数

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}$$

```ada
ggplot() +
  geom_function(fun = dnorm,  # 正态分布
                geom = "line",
                color = "#FF5733",
                linewidth = 1.5,
                linetype = "solid") +
  xlim(-3, 3)
```

![正态分布概率密度函数](https://pica.zhimg.com/v2-60387fdaef66dd42cdfc022875a88ec4_1440w.jpg)

### 3\. 绘制**曲线：圆**

不同于函数，曲线的一个x可以对应多个y，需要分段$$x^2 + y^2 = 1$$

```ada
ggplot() +
  geom_function(
    fun = function(x) sqrt(1 - x^2),
    color = "lightpink", 
    linewidth = 1
  ) +
  geom_function(
    fun = function(x) -sqrt(1 - x^2),
    color = "lightblue",
    linewidth = 1
  ) +
  coord_fixed() + # 固定轴比例，避免圆变形
  xlim(-1, 1) 
```

![圆](https://pica.zhimg.com/v2-5f2ba3ff8d9dff63e13c481cca2a474c_1440w.jpg)

## 五、使用 stat\_function 灵活绘图

绘制不同几何美学的图像

$$y=e^{\frac{1}{x}}$$

$$y=e^{x}$$ $$y=e^{x^{0.2}}$$

```ada
my_fun <- function(x, p) {
  return(exp(x^p))
}

ggplot() +
  stat_function(fun = my_fun, args = list(p = -1), 
                color = "blue", 
                geom = "line",
                linewidth = 1) +
  stat_function(fun = my_fun, args = list(p = 1), 
                color = "red", 
                geom = "point",
                size = 1) +
  stat_function(fun = my_fun, args = list(p = 0.2), 
                color = "green", 
                geom = "smooth",
                linewidth = 1) +
  xlim(-5, 5) +
  ylim(0, 10)
```

![my_fun](https://pic2.zhimg.com/v2-8f4e498bfca8b00ce291e2fc27840ef1_1440w.jpg)

## 六、geom\_function 与 stat\_function 的选择指南

| 函数 | 适用场景 | 特点 |
| ----- | ----- | ----- |
| geom_function() | 直接、简单地绘制函数曲线 | 语法简洁 |
| stat_function() | 支持各种几何映射 | 更灵活更自由 |

* * *

**值得一提的是，`function()`可以简写为`\()`，具体见我之前写的文章：**

[【R 语言】匿名函数](https://zhuanlan.zhihu.com/p/1944083434071917665)