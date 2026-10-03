---
tags: zhihu-article
zhihu-link: https://zhuanlan.zhihu.com/p/1944921736941384138
---
-   **扁平数据框（flat data frame）**：传统表格结构，1 行 = 1 条观测记录，1 列 = 1 个变量，难以直接承载多层级数据关系
-   **嵌套数据框（nested data frame）**：突破扁平结构限制，通过**列表列（list-column）**将同一分组的数据 “打包” 存储，1 行 = 1 个分组 + 该分组的完整子数据，适配多维度、分层级分析场景，通常使用 `map` 实现

![map 函数示意图](https://pic2.zhimg.com/v2-f095b1ba1f3c06f0cb3c2c575b51f093_1440w.jpg)

* * *

现有一扁平数据框 `demo_df`，包含药品销售记录

```ada
demo_df |> summary(maxsum = 10)
```

![](https://pic3.zhimg.com/v2-238417c0938c182c9b8e817e7e004d9c_1440w.jpg)![demo_df](https://picx.zhimg.com/v2-8e3d5b8473eb6ac2848800a07fa63ca1_1440w.jpg)

## 从扁平数据框到嵌套数据框

```ada
library(tidyverse)
```

根据`品名`分组，嵌套数据框：

```ada
warehouse_nested_df <- demo_df |>
  group_by(销售仓库) |>
  nest() |> 
  # 或者两句合并写为 nest(.by = 销售仓库)
  arrange(销售仓库)
```

![warehouse_nested_df](https://picx.zhimg.com/v2-f16376a6d25fc8392f38f7e6fe9874c1_1440w.jpg)

`data`这一列里是每个仓库的子数据框

## 分层计算

定义一个函数：

-   \- 根据`品名`分组汇总`总数平均`、`毛利`和`总毛利`
-   \- 根据`平均毛利`划分`等级`

```ada
# 定义函数
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

运用 `mutate()` 配合 `map()`，对 `data` 列的每个 df，逐一应用前面定义的 `summarize_fun()`：

```ada
warehouse_nested_df2 <- warehouse_nested_df |>
  mutate(drugname_result = map(data, summarize_fun))
```

![warehouse_nested_df2](https://picx.zhimg.com/v2-d891398046db8d5073432f812e7c4a7b_1440w.jpg)

再定义一个函数：

-   \- 根据`等级`分组汇总`等级总数`、`等级平均毛利`和`等级总毛利`

```ada
# 定义函数2
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

运用 `mutate()` 配合 `map()` ，对 `drugname_result` 列的每个 df，逐一应用前面定义的 `summarize_fun2()`：

```ada
warehouse_nested_df3 <- warehouse_nested_df2 |>
  mutate(grade_result = map(drugname_result, summarize_fun2))
```

![warehouse_nested_df3](https://pic2.zhimg.com/v2-37d5a7c8ff117ef9eb760386c837d077_1440w.jpg)

## 结果导出

后续可以用 `walk` 函数遍历导出为.xlsx

```ada
setwd("D:/RDirectory/pct")
# 此处用到我封装的函数（附于文末）
warehouse_nested_df3 |> export_all_nested_to_xlsx(output_dir = "./otpt")
# 或者，转置后输出（rev = TRUE）
warehouse_nested_df3 |> export_all_nested_to_xlsx(output_dir = "./otpt", rev = TRUE)
```

![](https://pic4.zhimg.com/v2-fda2c6a08e305b1fd0423a4a6dd2d2b5_1440w.jpg)

效果如下（不全打开展示了）：

![otpt](https://pic3.zhimg.com/v2-29fdde6672064f60309ccfb457bcbe0a_1440w.jpg)![drugname_result.xlsx](https://pic3.zhimg.com/v2-523efe30ca91ae2d0a2f23af20a9086c_1440w.jpg)

* * *

附：

```ada
export_all_nested_to_xlsx <- function(nested_df,
                                      output_dir = ".",
                                      rev = FALSE) {
  # 检查必要包
  required_pkgs <- c("openxlsx", "tidyverse", "fs")
  map(required_pkgs, function(pkg) {
    if (!requireNamespace(pkg, quietly = TRUE)) {
      stop(str_c("请安装包：install.packages('", pkg, "')"))
    }
  })
  library(openxlsx)
  library(tidyverse)
  library(fs)
  
  # 强制转换为绝对路径（关键步骤）
  output_dir_abs <- path(output_dir) |>  # 解析路径
    path_expand() |>                     # 展开~等符号
    path_abs()                           # 强制转为绝对路径（无视输入格式）
  
  # 创建目录
  if (!dir_exists(output_dir_abs)) {
    dir_create(output_dir_abs, recurse = TRUE)
    message(str_c("已创建输出目录：", output_dir_abs))
  }
  
  # 根据rev参数决定是否转置
  if (rev) {
    first_col <- names(nested_df)[1]
    # 按第一列转置
    nested_df <- nested_df |>
      column_to_rownames(first_col) |>
      t() |>
      as_tibble(rownames = "ResultType")
  }
  
  # 识别嵌套列和分组列
  nested_cols <- names(nested_df)[map_lgl(nested_df, ~ is.list(.) &&
                                            all(map_lgl(., is.data.frame)))]
  if (length(nested_cols) == 0)
    stop("无嵌套数据框列")
  group_col <- setdiff(names(nested_df), nested_cols)[1]
  if (is.na(group_col))
    stop("缺少分组列")
  
  # 获取所有工作表名
  sheet_names <- map_chr(seq_len(nrow(nested_df)), function(i) {
    nested_df[[group_col]][i] |>
      str_replace_all('[\\\\/:*?\"<>|]', "_") |>
      str_sub(1, 31)
  })
  n_sheets <- length(sheet_names)
  sheets_desc <- str_c("各文件均包含 ",
                       n_sheets,
                       " 个工作表：",
                       str_c(sheet_names, collapse = "、"))
  
  # 导出文件（使用绝对路径）
  walk(nested_cols, function(col) {
    wb <- createWorkbook()
    walk(seq_len(nrow(nested_df)), function(i) {
      sheet_name <- sheet_names[i]
      addWorksheet(wb, sheet_name)
      writeData(wb, sheet_name, nested_df[[col]][[i]])
      setColWidths(wb, sheet_name, 1:ncol(nested_df[[col]][[i]]), "auto")
    })
    file_path <- path(output_dir_abs, str_c(col, ".xlsx"))
    saveWorkbook(wb, file_path, overwrite = TRUE)
    message(str_c("已导出：", file_path))  # 这里也是绝对路径
    rm(wb)
  })
  
  # 最终目录提示（确保是绝对路径）
  message(sheets_desc)
  message(str_c("\n所有导出完成！目录：", output_dir_abs))
}
```

![purrr::cheatsheet](https://pic3.zhimg.com/v2-5a3d578a0218f691f72020fcf6398330_1440w.jpg)