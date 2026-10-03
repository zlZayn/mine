---
tags: zhihu-article
zhihu-link: https://zhuanlan.zhihu.com/p/1954307887825414074
---
**最小二乘法是实现线性拟合的主要数学手段。**

## 基础

R 中两个函数：

-   `nls()`（Nonlinear Least Squares，非线性最小二乘法）：

```ada
nls(y ~ 数学式子, data = 数据集, start = list(参数1 = 初始值1, 参数2 = 初始值2,...))
# 支持非线性函数（由 f(x,β) 组成），参数必须显式定义！并提供初始值！
# 纯数学式子，更灵活，不支持交互项的语法糖
```

$$\hat{y}=\beta_{0}+f(x_{1},\beta_{1})+f(x_{2},\beta_{2})+\dots+f(x_{n},\beta_{n})$$

-   `lm()`（Linear Models，线性模型；线性最小二乘法）：

```ada
lm(y ~ 数学式子, data = 数据集)
# 线性形式（仅 βx 组合），参数不可显式书写！由模型自动生成！
# 支持交互项的语法糖（'*'、':'）
```

$$\hat{y}=\beta_{0}+\beta_{1}x_{1}+\beta_{2}x_{2}+\dots+\beta_{n}x_{n}$$

矩阵形式：

$$\beta^T=\begin{bmatrix}  \beta_0 \\ \beta_1 \\ \vdots \\ \beta_n  \end{bmatrix}, X= \begin{bmatrix} 1\\ x_{1}\\ \vdots\\ x_{n}\\ \end{bmatrix}; \hat{y}=\beta X$$

* * *

## `nls()` 与 `lm()` 可以互相转化

当一个非线性模型可以**对变量进行数学变换**转化为线性形式时，使用 `nls()` 求解的非线性回归问题与使用 `lm()` 求解的线性回归问题等价，**它们本质上都是在求解相同的最小二乘优化问题**，通过\*\*最小化残差平方和（$SS_{R}$）\*\*来估计参数，即最小化：

$$SS_{R} = \sum_{i=1}^n (y_i - \hat{y}_i)^2$$

其中 $y$ 为观测值，$\hat{y}$ 为模型预测值

## 实例说明

以汽车油耗数据（`mtcars`）为例：

### 非线性模型

拟合模型：$\hat{mpg} = k\times\dfrac{1}{wt} + b$  
  
其中 $mpg$ 是每加仑行驶英里数， $wt$ 是车重。

```ada
nlsfit <- nls(mpg ~ k / wt + b, mtcars, start = list(k = 1, b = 0))

summary(nlsfit)
```

  

![](https://pic1.zhimg.com/v2-30400738a70be104fefaf655cc935802_1440w.jpg)

$$\hat{mpg}=\frac{45.829}{wt}+4.386$$

```ada
ggplot(mtcars, aes(wt, mpg)) +
	geom_point() +
	geom_line(aes(y = predict(nlsfit))) +
        geom_segment(aes(xend = wt, yend = predict(nlsfit)), color = "red")
```

![](https://pic2.zhimg.com/v2-7c001bc58147551ad16e125befe9dae3_1440w.jpg)

### 线性模型

通过定义新变量 $wt_{2} = \dfrac{1}{wt}$，原非线性模型转化为：$\hat{mpg} = k\times wt_{2} + b$  
  
这样就是一个符合 `lm()` 语法的线性结构。

> 线性模型核心定义是**对模型参数（系数）呈线性关系**

```ada
mtcars2 <- mtcars |>
	mutate(wt2 = 1 / wt)
lmfit <- lm(mpg ~ wt2, mtcars2)

summary(lmfit)
```

![](https://pica.zhimg.com/v2-30887033a8ee445acc560cd831f61c30_1440w.jpg)

$$\hat{mpg}=45.829\times wt_{2}+4.386$$

估计出的参数（方框）完全相等

```ada
ggplot(mtcars2, aes(wt2, mpg)) +
	geom_point() +
	geom_line(aes(y = predict(lmfit))) +
        geom_segment(aes(xend = wt2, yend = predict(lmfit)), color = "red")
```

![](https://pic3.zhimg.com/v2-608fe87f1e5f6b355c919db9fdd92e64_1440w.jpg)

  
  
相当于对 x 轴进行了数学变换，完全等价

* * *

## 总结

`nls()` 与 `lm()` 可以互相转化，`nls()` 更灵活，`lm()` 简洁。  
  
`lm()` 本质就是通过**线性最小二乘法**求解狭义线性模型的系数。  
  
**它们本质上都是在求解相同的最小二乘优化问题**。