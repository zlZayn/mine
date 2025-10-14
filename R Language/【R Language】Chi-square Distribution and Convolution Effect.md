Many people have heard: **The higher the degrees of freedom of a chi-square distribution, the closer it approximates a normal distribution (central limit theorem)**.
But why exactly? And what is a chi-square distribution anyway?

## Basic Definition

Chi-square distribution,

- **Definition**: If there are $k$ **independent, standard normal random variables** ($Z_1, Z_2, ..., Z_k$), then the **sum of their squares** follows a chi-square distribution with $k$ degrees of freedom ($df=k$). Mathematically:

$$X = {Z_1}^2 + {Z_2}^2 + ... + {Z_k}^2$$

Here, $X$ follows a chi-square distribution ($X \sim \chi^2(k)$), and $k$ is its degrees of freedom.

Since every term in a chi-square distribution is a square, all values are greater than 0.

## Initial Observations

This graph is quite familiar:
(Simulated with one million data points)

![](https://pic1.zhimg.com/v2-322524d83c27b059bcc71db0afb81eee_1440w.jpg)

For $df=1$, it's easy to understand—it's simply the square of a standard normal distribution $N(0,1)$, so the density is highest near 0.

For $df=2$, $X = {Z_1}^2 + {Z_2}^2$ is the sum of squares of two standard normal distributions. **Note that these two are independent!** The highest density is still near 0.

For $df=3$, $X = {Z_1}^2 + {Z_2}^2 + {Z_3}^2$ is the sum of squares of three standard normal distributions. For $X^2$ to be 0, all three terms must be 0. Due to the **smoothing effect of convolution**, this probability becomes smaller, and this is already noticeable.

And so on. **As $df$ increases, there are more terms, and the smoothing effect of convolution becomes more pronounced.**

We can understand the smoothing effect of convolution this way: When degrees of freedom exceed 2, for the sum of squares to be close to 0, all standard normal variables must be close to 0 **simultaneously**. While the probability of each individual variable being close to 0 is not low, the probability of multiple variables being close to 0 simultaneously decreases as the number of variables increases. Moreover, as degrees of freedom increase, the probability of the sum of squares taking small values becomes increasingly smaller, because as long as one variable is not close to 0, the sum of squares will become larger.

A simple example that helps understand the smoothing effect of convolution is:

## Rolling Dice (Insert)

Convolution is a mathematical operation that calculates "all possible combinations" and is used in probability theory to compute the distribution of the sum of two independent random variables.

For easier understanding, rolling dice is an example of **discrete convolution**.

- Single roll: Uniform distribution (1-6 points, each with probability $\frac{1}{6}$)
- Sum of two rolls: Triangular distribution (7 points have the highest probability):

  - Sum of two rolls being 2 (extreme value): Requires both rolls to be 1, with probability $\left(\frac{1}{6}\right)^2$
  - Sum of two rolls being 12 (extreme value): Requires both rolls to be 6, also with probability $\left(\frac{1}{6}\right)^2$
  - Sum of two rolls being 7 (middle value): Can be achieved in many ways—(1,6), (2,5), (3,4), (4,3), (5,2), (6,1)—six different combinations

![](https://pica.zhimg.com/v2-ec2c9755590e7db249cd54d8b104894c_1440w.jpg)

- Sum of three rolls: Begins to show a bell shape

![](https://pic3.zhimg.com/v2-23959f2b1f33a0c0ceee1b0ff213d94c_1440w.jpg)

- Sum of many rolls: Approaches a normal distribution

![](https://pica.zhimg.com/v2-f0f60c2d8b9318cca3fe2c8325a55636_1440w.jpg)

**This is the smoothing effect of convolution: Middle values have more combinations, so they have higher probabilities!**

## Direct Visualization

The chi-square distribution involves continuous convolution.

Let's continue with the intuitive observation.

**As $df$ increases, there are more terms, and the smoothing effect of convolution becomes more pronounced.**

![](https://pic2.zhimg.com/v2-c0b6b6f079e0748d91f968e84c013a77_1440w.jpg)

When $df$ is small, the distribution is right-skewed. As $df$ increases, it becomes more and more like a normal distribution. Notice the peak's position on the x-axis—it gradually approaches $df$ (at the red line) from left to right.

## Mathematical Derivation

What is the value on the x-axis corresponding to the peak? What is its relationship with $df$? Why does it happen when $df > 2$?

### 1. Probability Density Function of Chi-square Distribution

**The probability density function (PDF) of a chi-square distribution with $k$ degrees of freedom is:**

$$f(x;k) = \frac{1}{2^{\frac{k}{2}} \Gamma\left(\frac{k}{2}\right)}\cdot x^{\frac{k}{2}-1}\cdot e^{-\frac{x}{2}}, \quad x > 0$$

### 2. Taking Logarithm to Simplify Differentiation

$$\ln f(x;k) = \ln\left[\frac{1}{2^{\frac{k}{2}} \Gamma\left( \frac{k}{2} \right)} \right] + \ln x^{\frac{k}{2} - 1}  + \ln e^{-\frac{x}{2}} $$

$$\ln f(x;k) = C + \left(\frac{k}{2} - 1\right) \ln x - \frac{x}{2}$$

Where $C = \ln\left[\frac{1}{2^{\frac{k}{2}} \Gamma\left( \frac{k}{2} \right)} \right]$ is a constant.

### 3. Differentiating with respect to $x$ and Setting Derivative to Zero

$$\frac{d}{dx} [\ln f(x;k)] = \frac{\frac{k}{2} - 1}{x} - \frac{1}{2}$$

Setting the derivative to zero:

$$\frac{\frac{k}{2} - 1}{x} - \frac{1}{2} = 0$$

$$x = k - 2$$

To verify it's a maximum point, compute the second derivative:

$$\frac{d^2}{dx^2} [\ln f(x;k)] = -\frac{\frac{k}{2} - 1}{x^2}$$

When $k > 2$, the second derivative is negative, confirming $x = k - 2$ is a maximum point.

### 4. Function Behavior Decomposition Method

Returning to the original PDF, we can derive the **proportional form of the PDF**:

$$f(x;k) \propto x^{\frac{k}{2}-1} \cdot e^{-\frac{x}{2}}, \quad x > 0$$

| Degrees of Freedom | Key Feature | Mode |
| ----------------- | ----------- | ---- |
| df=1 | Singularity at x=0 (approaching infinity) | 0 |
| df=2 | Maximum at x=0, degenerates to pure exponential function | 0 |
| df=3 | Exponent becomes positive for the first time! Polynomial term dominates (grows) when x is small | 1 |
| df=4 | Polynomial term dominates (grows) when x is small | 2 |

Due to the exponential nature of $e^{-\frac{x}{2}}$, it will always dominate when x is sufficiently large (ensuring the right side always decays), and together with the polynomial term, they produce the mode.

### 5. Conclusion

For $k > 2$, the mode of the chi-square distribution (the x-value corresponding to the peak of its density plot) is $k - 2$; for $0 < k \leq 2$, the mode is 0. Expressed piecewise:

$$\text{Mode}(k) =  \begin{cases}  0, & 0 < k \leq 2 \\ k - 2, & k > 2  \end{cases}$$

**As $df$ (i.e., $k$) increases, the mode gets closer to $df$:**

![](https://pic1.zhimg.com/v2-51bb23fe499edb6253c2569b63cbd24c_1440w.jpg)![](https://pic4.zhimg.com/v2-c7ec2ec9344dce86abccd7556b0107fd_1440w.jpg)![](https://pic4.zhimg.com/v2-8f28429d70c9767a511a011ce84223dd_1440w.jpg)

The larger $df$ (i.e., $k$ in the formula), the closer they get, because when $k$ is large enough, we can consider $k-2=k$, and the gap is always 2!

Don't forget! $k-2$ is the x-value corresponding to the peak, and $k$ is the $df$.

## Final Points

- **A chi-square distribution is formed by the sum (convolution) of squares of independent standard normal random variables. Its morphological evolution perfectly demonstrates the smoothing effect of convolution.**
- **The smoothing effect of convolution: Middle values have more combinations, so they have higher probabilities!**

* * *

## CODE

### Plotting Chi-square Distributions with Different Degrees of Freedom on the Same Graph

```R
library(tidyverse)

# Set parameters
n <- 10000000  # Number of simulations
df_values <- c(1, 2, 3, 5, 10)  # Degrees of freedom to display

# Step 1: Generate squared values of standard normal distributions (intermediate data)
intermediate_data <- map_dfr(df_values, \(k) {
  # Generate k columns of standard normal random numbers
  norm_matrix <- matrix(rnorm(n * k), ncol = k)
  # Calculate the square of each value
  square_matrix <- norm_matrix^2
  # Convert to data frame and add degrees of freedom identifier
  as_tibble(square_matrix) |> 
    set_names(paste0("z", 1:k, "_square")) |> 
    mutate(df = k) |> 
    relocate(df)
})


# Step 2: Calculate chi-square values (sum of squares) based on intermediate data
data <- intermediate_data |> 
  # Group by degrees of freedom and sum the squared value columns for each group (ignore NA since different degrees of freedom have different numbers of columns)
  group_by(df) |> 
  mutate(
    value = rowSums(across(starts_with("z")), na.rm = TRUE)  # Sum all z*_square columns
  ) |> 
  ungroup() |> 
  # Keep only chi-square values and degrees of freedom columns
  select(value, df) |> 
  mutate(df = factor(df))


# Plot density chart
ggplot(data, aes(x = value)) +
  geom_density(aes(color = df, fill = df),
               linewidth = 0.1,
               alpha = 0.1) +
  # Add vertical lines for each degree of freedom (x = degrees of freedom value)
  geom_vline(
    xintercept = df_values,
    # All degrees of freedom values as vertical line positions
    color = "black",
    # Vertical line color
    linewidth = 0.1,
    # Line width
  ) +
  theme_classic() +
  scale_x_continuous(
    limits = c(0, 18),
    expand = c(0, 0),
    breaks = df_values  # Only show ticks corresponding to degrees of freedom
  ) +
  scale_y_continuous(limits = c(0, 1.7), expand = c(0, 0)) +
  labs(
    title = paste(
      "Chi-square Distribution (df =",
      paste(df_values, collapse = ", "),
      ")"
    ),
    x = "Value",
    y = "Density"
  ) +
  theme(
    plot.title = element_text(size = 18, face = "bold"),
    # Increase and bold title
    axis.title.x = element_text(size = 14, face = "bold"),
    # Increase and bold x-axis label
    axis.title.y = element_text(size = 14, face = "bold"),
    # Increase and bold y-axis label
    axis.text.x = element_text(size = 12, face = "bold"),
    # Increase and bold x-axis ticks
    axis.text.y = element_text(size = 12, face = "bold")
    # Increase and bold y-axis ticks
  )
```

### Batch Visualization of Approaching Normal Distribution

```R
library(tidyverse)

# Set parameters
n <- 1000000  # Number of simulations
df_values <- seq(20, 300, by = 20)  # Sequence of degrees of freedom (20 to 300, step 20)
save_dir <- "D:\\ObsidianDirectory\\R\\新建文件夹\\plots"  # Save path

# Create save directory if it doesn't exist
if (!dir.exists(save_dir)) {
  dir.create(save_dir, recursive = TRUE)
}

set.seed(42)  # Fix random seed to ensure reproducibility

# Batch generate and save images
walk(df_values, function(k) {
  k <- as.numeric(k)  # Ensure k is numeric
  
  # Directly generate chi-square distribution data
  chi2_data <- tibble(
    value = rchisq(n, df = k),
    # Directly use rchisq function to generate data
    df = factor(k)
  )
  
  # Plot density chart (fixed y-axis range)
  p <- ggplot(chi2_data, aes(x = value)) +
    geom_density(fill = 'black',
                 linewidth = 0.5,
                 alpha = 0.1) +
    theme_classic() +
    scale_x_continuous(
      limits = c(0, 2 * k),
      # x-axis range from 0 to 2df
      expand = c(0, 0),
      breaks = c(0, k, 2 * k)
      # Show ticks
    ) +
    scale_y_continuous(
      limits = c(0, 0.1),
      # Fixed y-axis range
      expand = c(0, 0)
    ) +
    # Add vertical line corresponding to degrees of freedom (at x = k)
    geom_vline(
      xintercept = k,
      # Vertical line position is current degrees of freedom
      color = "red",
      # Vertical line color
      linewidth = 0.1   # Line width
    ) +
    labs(
      title = paste("Chi-square Distribution (df =", k, ")"),
      x = "Value",
      y = "Density"
    ) +
    theme(
      plot.title = element_text(size = 18, face = "bold"),
      # Increase and bold title
      axis.title.x = element_text(size = 14, face = "bold"),
      # Increase and bold x-axis label
      axis.title.y = element_text(size = 14, face = "bold"),
      # Increase and bold y-axis label
      axis.text.x = element_text(
        size = 12,
        face = "bold",
        angle = 15,
        hjust = 1
      ),
      # Increase and bold x-axis ticks
      axis.text.y = element_text(size = 12, face = "bold")   # Increase and bold y-axis ticks
    )
  
  # Save image
  ggsave(
    filename = paste0("chi2_df_", k, ".png"),
    plot = p,
    path = save_dir,
    width = 10,
    height = 6,
    dpi = 300
  )
  
  cat("Image with degrees of freedom", k, "saved\n")
})

cat("All images saved to:", save_dir, "\n")
```

### Rolling Dice

```R
library(tidyverse)

# Calculate distribution of sum of two dice rolls
two_dice <- expand.grid(die1 = 1:6, die2 = 1:6) %>%
  mutate(sum = die1 + die2) %>%
  count(sum) %>%
  mutate(prob = n / 36)

ggplot(two_dice, aes(x = sum, y = prob)) +
  geom_col(fill = "lightgreen", width = 0.7) +
  scale_x_continuous(breaks = 2:12) +
  labs(title = "Sum of Two Dice: Triangular Distribution", 
       x = "Sum of Points", y = "Probability") +
  theme_bw()

# Calculate distribution of sum of three dice rolls
three_dice <- expand.grid(die1 = 1:6, die2 = 1:6, die3 = 1:6) %>%
  mutate(sum = die1 + die2 + die3) %>%
  count(sum) %>%
  mutate(prob = n / 216)  # 6^3 = 216

ggplot(three_dice, aes(x = sum, y = prob)) +
  geom_col(fill = "orange", width = 0.7) +
  labs(title = "Sum of Three Dice: Beginning to Show Bell Shape", 
       x = "Sum of Points", y = "Probability") +
  theme_bw()

# Simulate sum of 10 dice rolls (calculated via convolution)
convolution_pmf <- function(pmf, n) {
  result <- pmf
  for(i in 2:n) {
    result <- convolve(result, rev(pmf), type = "open")
  }
  result[1:(length(pmf) + (n-1)*(length(pmf)-1))]
}

pmf <- rep(1/6, 6)  # PMF of single die roll
n_rolls <- 10
ten_dice <- convolution_pmf(pmf, n_rolls)

ten_dice_df <- tibble(
  sum = n_rolls:(n_rolls + length(ten_dice) - 1),
  prob = ten_dice
)

ggplot(ten_dice_df, aes(x = sum, y = prob)) +
  geom_col(fill = "purple", alpha = 0.7) +
  labs(title = "Sum of 10 Dice: Approaching Normal Distribution", 
       x = "Sum of Points", y = "Probability") +
  theme_bw()
)
```

* * *

References:

[【人话统计学概念】一次搞懂卡方检验三大类型：独立性检验、同质性检验、拟合优度检验！_哔哩哔哩_bilibili](https://link.zhihu.com/?target=https%3A//www.bilibili.com/video/BV15tHQzrECH/%3Fspm_id_from%3D333.1391.0.0%26vd_source%3D44a0954fac8bbe48022f43ab92c0ddba)
[深入浅出详解卡方分布：直观理解、案例求解及可视化分析](https://zhuanlan.zhihu.com/p/682218728)
[卡方分布的概率密度函数和它的一些衍生问题](https://zhuanlan.zhihu.com/p/268756365)