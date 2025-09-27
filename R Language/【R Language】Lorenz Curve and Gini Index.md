**Lorenz Curve and Gini Index**

> Lorenz (Max Otto Lorenz, December 19, 1876 — July 1, 1959), an American statistician, proposed the Lorenz curve in 1905 to measure the degree of social income distribution inequality; this achievement was later developed by the Italian statistician Gini (Corrado Gini) into the Gini coefficient.

![Lorenz Curve Diagram](https://pica.zhimg.com/v2-063fe65ec9451ee54d336a066e2c4d98_1440w.jpg)

## Concepts

The Lorenz curve is used for **visualizing inequality**; the Gini index is used for **quantifying inequality**.

-   **Horizontal axis**: "Cumulative percentage of population" sorted from low to high resource possession
-   **Vertical axis**: "Cumulative percentage of resources" owned by the corresponding horizontal axis population

**The more curved downward the Lorenz curve, the more unequal it is**
Based on the Lorenz curve:

-   $S_{A}$: The area between the Lorenz curve and the "absolute equality line" (the hypotenuse of the lower triangle)
-   $S_{B}$: The area between the Lorenz curve and the "absolute inequality line" (the two right sides of the lower triangle)

$$Gini = \frac{S_{A}}{S_{A} + S_{B}}$$

The Gini index ranges from $[0, 1]$
**The larger the value, the more unequal**

1.  **How to read the Lorenz curve**: The closer it is to the "absolute equality line" in the middle of the graph, the fairer the distribution; the more it deviates downward from this line, the more uneven the distribution.
2.  **How to read the Gini index**: The smaller the proportion of $S_{A}$ to $(S_{A} + S_{B})$, the higher the degree of equality; the larger the proportion, the more serious the inequality.

![Diagram](https://picx.zhimg.com/v2-6cbca6aca2ed4c962def3ab0ab1a0b95_1440w.jpg)

According to the **Lagrange mean value theorem**, if the curve between two points is continuous, differentiable, and does not coincide with the line connecting the two points, then there must exist two points on the curve whose tangent slopes are respectively greater than and less than the **slope of the line connecting the two points**.

This exactly proves that some people have less resource allocation (slope less than 1), and some people have more resource allocation (slope greater than 1).

The essence of the **slope of the Lorenz curve** is: **the proportion of resources (vertical axis) that each unit proportion of the population (horizontal axis) can receive**.

$$\text{Slope of Lorenz curve} = \frac{\text{Change in cumulative proportion of resources}}{\text{Change in cumulative proportion of population}}$$

## Loading Packages and Data

The `Wage` dataset built into `ISLR`:

> Wage and other data for a group of 3000 male workers in the Mid-Atlantic region.

```R
library(tidyverse)
Wage_df <- ISLR::Wage
```

Next is an example of exploring whether the `wage` distribution of these 3000 people is equal.

## I. Lorenz Curve

### Data Preprocessing

Calculate cumulative population proportion and cumulative `wage` proportion, which are the basic data for drawing the Lorenz curve:

1.  `arrange(wage)`: **Sort from low-income to high-income groups (critical!!!!!)**
2.  `n`: **Number of people**
3.  `pop_accum`: **Cumulative proportion from low-income to high-income groups (because they were sorted by income earlier)**
4.  `val_accum`: **Cumulative proportion of income from low-income to high-income groups (because they were sorted by income earlier)**
5.  `add_row(pop_accum=0,val_accum=0,.before=1)`: **Add data for coordinate (0,0) (for drawing)**

```R
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

![First 8 rows after data preprocessing](https://pic2.zhimg.com/v2-d042709c80cefb7fd9ae32a1a930968b_1440w.jpg)![Last 8 rows after data preprocessing](https://pic4.zhimg.com/v2-6a5aa72451de130c6e6d765a4e1b99d9_1440w.jpg)

### Drawing the Lorenz Curve

```R
ggplot(data, aes(x = pop_accum, y = val_accum)) +
  geom_line() +
  geom_abline(intercept = 0, slope = 1, linetype = "dashed") +
  coord_cartesian(xlim = c(0, 1), ylim = c(0, 1), expand = FALSE) +
  theme_bw()
```

![Lorenz Curve](https://pic3.zhimg.com/v2-0922d0fa580ac390a013bd8cae1d04fc_1440w.jpg)

The Lorenz curve shows the `wage` distribution, where the dashed line represents absolutely equal distribution. The more the curve bends downward (away from the "absolute equality line"), the more unequal the distribution. (No need to look at the upper triangle)

It can be seen that the curve in the figure is relatively close to the dashed line (relatively equal).

## II. Gini Index

### Calculating the Area Under the Lorenz Curve

Calculate the area under the Lorenz curve `area_under_Lorenz` ($S_{B}$) using the **trapezoidal rule**.

```R
area_under_Lorenz <- data |> 
  mutate(
    x_diff = pop_accum - lag(pop_accum),
    y_mean = (val_accum + lag(val_accum)) / 2
  ) |> 
  summarise(area_under_Lorenz = sum(x_diff * y_mean, na.rm = TRUE)) |> 
  pull(area_under_Lorenz)
```

```R
> area_under_Lorenz # Result
[1] 0.4045936
```

### Calculating the Gini Index

According to the known conditions

$$S_{B} = 0.4045936$$

$$S_{A} + S_{B} = 0.5$$

$$Gini = \frac{S_{A}}{S_{A} + S_{B}}$$

Calculate the Gini index jointly

```R
Gini_Index = (0.5 - area_under_Lorenz) / 0.5
```

```R
> Gini_Index # Result
[1] 0.1908127
```

The Gini index `Gini_Index` is used to quantify the degree of `wage` inequality, with a value of 0 indicating complete equality and a value of 1 indicating complete inequality.

A Gini index of 0.191 indicates that wage distribution is relatively equal.

* * *

Appendix:

Randomly drew the distribution of `wage`

```R
ggplot(data, aes(wage)) +
  geom_density() +
  theme_bw()
```

![](https://pic1.zhimg.com/v2-10b75f4c20da0c66ed3394756236a662_1440w.jpg)

Reference:

[The Lorenz Curve](https://link.zhihu.com/?target=https%3A//www.economicsonline.co.uk/definitions/thelorenzcurve.html/)