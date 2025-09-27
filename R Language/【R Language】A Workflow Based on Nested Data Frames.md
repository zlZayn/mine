-   **Flat data frame**: Traditional table structure, where 1 row = 1 observation record and 1 column = 1 variable, making it difficult to directly carry multi-level data relationships
-   **Nested data frame**: Breaking through the limitations of flat structures, it "packages" data from the same group through **list-columns**, with 1 row = 1 group + complete subgroup data, suitable for multi-dimensional, hierarchical analysis scenarios, typically implemented using `map`

![map Function Schematic](https://pic2.zhimg.com/v2-f095b1ba1f3c06f0cb3c2c575b51f093_1440w.jpg)

* * *

We have a flat data frame `demo_df` containing pharmaceutical sales records

```R
demo_df |> summary(maxsum = 10)
```

![](https://pic3.zhimg.com/v2-238417c0938c182c9b8e817e7e004d9c_1440w.jpg)![demo_df](https://picx.zhimg.com/v2-8e3d5b8473eb6ac2848800a07fa63ca1_1440w.jpg)

## From Flat Data Frame to Nested Data Frame

```R
library(tidyverse)
```

Group by `品名` (Product Name), nested data frame:

```R
warehouse_nested_df <- demo_df |>
  group_by(销售仓库) |>
  nest() |>
  # Or combine the two lines as nest(.by = 销售仓库)
  arrange(销售仓库)
```

![warehouse_nested_df](https://picx.zhimg.com/v2-f16376a6d25fc8392f38f7e6fe9874c1_1440w.jpg)

The `data` column contains sub-data frames for each warehouse

## Hierarchical Calculation

Define a function:

-   - Group by `品名` to summarize `总数平均` (Total Average), `毛利` (Gross Profit), and `总毛利` (Total Gross Profit)
-   - Classify `等级` (Grade) based on `平均毛利` (Average Gross Profit)

```R
# Define function
summarize_fun <- function(df) {
  df |>
    group_by(品名) |>
    summarize(
      总数 = n(),
      平均毛利 = mean(毛利, na.rm = TRUE),
      总毛利 = sum(毛利, na.rm = TRUE)
      ) |>
    mutate(
      等级 = case_when(
        平均毛利 >= 100 ~ "S",
        平均毛利 >= 50 ~ "A",
        平均毛利 >= 10 ~ "B",
        TRUE ~ "C"
        ),
      等级 = factor(等级, levels = c("S", "A", "B", "C"))
      ) |>
    arrange(desc(总毛利))
  }
```

Use `mutate()` with `map()` to apply the previously defined `summarize_fun()` to each df in the `data` column:

```R
warehouse_nested_df2 <- warehouse_nested_df |>
  mutate(drugname_result = map(data, summarize_fun))
```

![warehouse_nested_df2](https://picx.zhimg.com/v2-d891398046db8d5073432f812e7c4a7b_1440w.jpg)

Define another function:

-   - Group by `等级` to summarize `等级总数` (Grade Total), `等级平均毛利` (Grade Average Gross Profit), and `等级总毛利` (Grade Total Gross Profit)

```R
# Define function 2
summarize_fun2 <- function(df) {
  df |>
    group_by(等级) |>
    summarize(
      等级总数 = n(),
      等级平均毛利 = mean(平均毛利, na.rm = TRUE),
      等级总毛利 = sum(总毛利, na.rm = TRUE)
      ) |>
    arrange(等级)
  }
```

Use `mutate()` with `map()` to apply the previously defined `summarize_fun2()` to each df in the `drugname_result` column:

```R
warehouse_nested_df3 <- warehouse_nested_df2 |>
  mutate(grade_result = map(drugname_result, summarize_fun2))
```

![warehouse_nested_df3](https://pic2.zhimg.com/v2-37d5a7c8ff117ef9eb760386c837d077_1440w.jpg)

## Result Export

Subsequently, we can use the `walk` function to export to .xlsx

```R
# This uses a function I encapsulated (included at the end)
> warehouse_nested_df3 |> export_all_nested_to_xlsx(output_dir = "./otpt")
已导出：./otpt/data.xlsx
已导出：./otpt/drugname_result.xlsx
已导出：./otpt/grade_result.xlsx

所有导出完成！目录：D:\RDirectory\pct\otpt
```

The results are as follows:

![Exported Tables](https://pic3.zhimg.com/v2-e6a11eec0fb703f213f85fedd20a7f24_1440w.jpg)![drugname_result.xlsx](https://pic3.zhimg.com/v2-523efe30ca91ae2d0a2f23af20a9086c_1440w.jpg)

* * *

Appendix:

```R
export_all_nested_to_xlsx <- function(nested_df, output_dir = ".") {
  # Check required packages
  required_pkgs <- c("openxlsx", "tidyverse")
  lapply(required_pkgs, function(pkg) {
    if (!requireNamespace(pkg, quietly = TRUE)) {
      stop(paste("Please install package: install.packages('", pkg, "')", sep = ""))
    }
  })
  library(openxlsx)
  library(tidyverse)

  # Create output directory
  if (!dir.exists(output_dir)) {
    dir.create(output_dir,
               recursive = TRUE,
               showWarnings = FALSE)
    message("Output directory created: ", output_dir)
  }

  # Identify nested columns
  nested_cols <- names(nested_df)[map_lgl(nested_df, ~ is.list(.) &&
                                            all(map_lgl(., is.data.frame)))]
  if (length(nested_cols) == 0)
    stop("No nested data frame columns")

  # Identify grouping column
  group_col <- setdiff(names(nested_df), nested_cols)[1]
  if (is.na(group_col))
    stop("Missing grouping column")

  # Export each nested column to Excel
  walk(nested_cols, function(col) {
    wb <- createWorkbook()
    walk(seq_len(nrow(nested_df)), function(i) {
      # Process worksheet name
      sheet_name <- gsub("[\\/:*?\"<>|", "_", nested_df[[group_col]][i])
      sheet_name <- substr(sheet_name, 1, 31)

      # Write data
      addWorksheet(wb, sheet_name)
      writeData(wb, sheet_name, nested_df[[col]][[i]])
      setColWidths(wb, sheet_name, 1:ncol(nested_df[[col]][[i]]), "auto")
    })
    # Save file (without date)
    saveWorkbook(wb, file.path(output_dir, paste0(col, ".xlsx")), overwrite = TRUE)
    message("Exported: ", file.path(output_dir, paste0(col, ".xlsx")))
    rm(wb)
  })

  message("\nAll exports completed! Directory: ", normalizePath(output_dir))
}```

![purrr::cheatsheet](https://pic3.zhimg.com/v2-5a3d578a0218f691f72020fcf6398330_1440w.jpg)