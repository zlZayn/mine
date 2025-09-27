This article uses **case-based teaching** and recommends using **directory navigation**.

* * *

## I. Introduction

In R's `ggplot2` package, the `geom_*` series of functions form the core element family for visualization, responsible for rendering various geometric objects in coordinate systems. As a special member of this family, `geom_function()` works with `stat_function()` to provide a direct, efficient way to draw functions—without pre-calculating large numbers of data points, but instead by directly passing function expressions to achieve **visualization of function curves**.

**Compare the code of these two older methods:**

### Traditional Data Point Method

```R
x <- seq(-5, 5, length.out = 100)
y <- x^2 + 2*x + 1
data_df <- data.frame(x = x, y = y)

ggplot(data_df, aes(x, y)) +
  geom_line(color = "blue")
```

![Traditional Data Point Method](https://pic4.zhimg.com/v2-08a11c72d126098849736b7e677004fb_1440w.jpg)

### Direct Plotting Method

```R
ggplot() +
  geom_function(fun = function(x) x^2 + 2*x + 1, 
                color = "blue") +
  xlim(-5, 5)
```

![Direct Plotting Method](https://pic3.zhimg.com/v2-d7080e9d92c26ec4c71b055e285ce582_1440w.jpg)

The results are identical, but the code is much cleaner.

## II. Basic Preparation

```R
library(ggplot2)
```

## III. Plotting Basic Functions with geom_function

### 1. Linear Functions

$$y = 2x + 1$$

```R
ggplot() +
  geom_function(fun = function(x) 2 * x + 1,  # Linear function
                color = "blue",              # Line color
                linewidth = 1) +                   # Line thickness
  xlim(-5, 5)  # x-axis range
```

![Linear Function](https://pic3.zhimg.com/v2-c789d4ebe7e528bb4b9516468fc10dc6_1440w.jpg)

### 2. Quadratic Functions

$$y = 2x^2 - 3x + 1$$

```R
ggplot() +
  geom_function(fun = function(x) 2 * x^2 - 3*x + 1,  # Quadratic function
                color = "red",
                linewidth = 1) +
  xlim(-4, 4)
```

![Quadratic Function](https://pic4.zhimg.com/v2-bff8ec790f6b5f9477be9f12d21dd8d7_1440w.jpg)

### 3. Exponential Functions

$$y = 2^x$$

```R
ggplot() +
  geom_function(fun = function(x) 2^x,  # Exponential function
                color = "green",
                linewidth = 1) +
  xlim(-2, 2) +
  ylim(0, 5)  # y-axis range
```

![Exponential Function](https://pica.zhimg.com/v2-859e59a7aa88ff6151fd98e2f9f2bfc6_1440w.jpg)

### 4. Logarithmic Functions

$$y = \log(x)$$

```R
ggplot() +
  geom_function(fun = function(x) log(x),  # Logarithmic function
                color = "purple",
                linewidth = 1) +
  xlim(0.1, 5)  # x > 0
```

![Logarithmic Function](https://pica.zhimg.com/v2-fc5d4f7f46b0a335af29d3dabb9b17f0_1440w.jpg)

### 5. Power Functions

And multiple can be overlaid

$$y = x$$

$$y = x^2$$

$$y = x^3$$

```R
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

![Multiple Functions Overlaid](https://pic2.zhimg.com/v2-41fc0ae4986d7b671c341c8ac605cdaf_1440w.jpg)

### 6. Trigonometric Functions

$$y = \sin(x)$$

$$y = \cos(x)$$

```R
ggplot() +
  geom_function(fun = sin,  # sin function
                color = "blue",
                linewidth = 1, 
                linetype = "solid") +
  geom_function(fun = cos,  # cos function
                color = "red",
                linewidth = 1, 
                linetype = "dashed") +
  xlim(-pi, pi) +
  scale_x_continuous(breaks = c(-pi, -pi/2, 0, pi/2, pi),
                     labels = c("-π", "-π/2", "0", "π/2", "π"))
```

![Trigonometric Functions](https://pic3.zhimg.com/v2-86aea00d5681ff887001ef6a3729cbcc_1440w.jpg)

### 7. Derivatives

$$f(x) = x^3 - 2x$$

$$f'(x) = 3x^2 - 2$$

```R
# Define functions
f <- function(x) x^3 - 2*x  # Original function
f_prime <- function(x) 3*x^2 - 2  # Derivative function

# Plot original and derivative functions
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

![Derivative Visualization](https://pic3.zhimg.com/v2-ee03648502472bfe93399d74369cd24a_1440w.jpg)

## IV. Advanced Techniques for Using geom_function

### 1. Functions with Parameters

$$y = x^2$$

$$y = x^3$$

```R
# Define function
power_function <- function(x, exponent) {
  return(x^exponent)
}

# Plot functions with parameters
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

![Functions with Parameters](https://pic3.zhimg.com/v2-1baf4eb88aa5a3d289db609d6bcffa8e_1440w.jpg)

### 2. Built-in Functions

Probability density function

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}$$

```R
ggplot() +
  geom_function(fun = dnorm,  # Normal distribution
                geom = "line",
                color = "#FF5733",
                linewidth = 1.5,
                linetype = "solid") +
  xlim(-3, 3)
```

![Normal Distribution Probability Density Function](https://pica.zhimg.com/v2-60387fdaef66dd42cdfc022875a88ec4_1440w.jpg)

### 3. Plotting **Curves: Circles**

Unlike functions, a single x can correspond to multiple y values for curves, requiring segmentation $$x^2 + y^2 = 1$$

```R
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
  coord_fixed() + # Fix axis ratio to avoid circle deformation
  xlim(-1, 1) 
```

![Circle](https://pica.zhimg.com/v2-5f2ba3ff8d9dff63e13c481cca2a474c_1440w.jpg)

## V. Flexible Plotting with stat_function

Plotting images with different geometric aesthetics

$$y=e^{\frac{1}{x}}$$

$$y=e^{x}$$ $$y=e^{x^{0.2}}$$

```R
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

## VI. Selection Guide for geom_function and stat_function

| Function | Application Scenario | Features |
| -------- | -------------------- | -------- |
| geom_function() | Direct, simple plotting of function curves | Concise syntax |
| stat_function() | Supports various geometric mappings | More flexible and free |

* * *

**It's worth mentioning that `function()` can be abbreviated as `\()`. For details, see my previous article:**

[【R 语言】匿名函数](https://zhuanlan.zhihu.com/p/1944083434071917665)