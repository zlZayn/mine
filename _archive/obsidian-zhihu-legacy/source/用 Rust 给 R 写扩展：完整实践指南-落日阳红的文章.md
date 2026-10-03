---
tags: zhihu-article
zhihu-link: https://zhuanlan.zhihu.com/p/2087557727866320879
---
## 用 Rust 给 R 写扩展：完整实践指南

### 一、核心心智模型

R 不认识 Rust。R 认识的是 C 动态库（`.dll` / `.so` / `.dylib`）。

R 加载扩展包的方式，本质上是 `dyn.load()` 加载一个动态库，然后通过 `.Call()` 调用其中符合 C ABI 的函数。Rcpp 能工作，是因为 C++ 能编译出 C ABI 的动态库。extendr 能工作，是因为 **Rust 也能编译出 C ABI 的动态库**。

`{extendr}` 做的事，就是自动生成两层胶水：

| 层 | 工作 |
| ----- | ----- |
| Rust 侧 | 用 #[extendr] 宏把函数包装成 extern "C"，处理 R 对象与 Rust 类型的转换 |
| R 侧 | 生成 .Call() 包装函数和 NAMESPACE 导出 |

你写 Rust 函数，在 R 里像普通函数一样调用。R 看到的仍然是一个 C 动态库。

`{extendr}` 是一组 crate 的统称（`extendr-api`、`extendr-engine`、`extendr-macros`），定位等同于 Rcpp/cpp11，但底层是 Rust。`{rextendr}` 是 R 端的配套包，负责脚手架生成和工具链管理。extendr 的设计目标是提供一个 opinionated API，重点参考了 Rcpp 和 cpp11 的人体工学设计。

### 二、环境准备与体检

![](https://pic3.zhimg.com/v2-6f28b147f6d999a41bfedbc428ce19ec_1440w.jpg)

rextendr

在开始之前，确保三样东西就位：

1.  **Rust 工具链**：从 [Rust Programming Language](https://link.zhihu.com/?target=http%3A//rust-lang.org) 安装 `rustup`。当前 extendr 的最低支持 Rust 版本（MSRV）是 1.65.0，这是为了确保 CRAN 合规。Windows 用户需要额外添加 GNU 工具链：`rustup target add x86_64-pc-windows-gnu`
2.  **R 版本**：推荐使用 R >= 4.2.0
3.  **R 包**：在 R 中安装 `install.packages(c("rextendr", "usethis", "devtools"))`
4.  **一键体检**：运行以下命令，全部绿色对勾即可开始：

```text
rextendr::rust_sitrep()
```

`rust_sitrep()` 会提供当前 Rust 基础设施的详细报告，并给出修复建议。

### 三、先做实验，再建包

不要一上来就建包。先在 R 控制台里用 `rust_function()` 验证核心逻辑：

```text
rextendr::rust_function("
fn add_one(x: f64) -> f64 {
    x + 1.0
}
")
```

然后直接调用：

```text
add_one(5)
# [1] 6
```

这一步的目的是让“Rust 代码在 R 里跑起来”从抽象变成具体。确认函数逻辑正确、性能提升符合预期后，再正式建包。

Rust 作为编译语言，将代码转换为机器语言后再运行，因此执行速度远快于 R 这样的解释型语言。用编译语言配合 R 的标准做法是：先用 `Rprof()` 找出代码瓶颈，对非常慢的部分用编译语言重写，再写一个 R 函数来调用它。Rust 相比 C++ 有更严格的代码验证和内存安全机制，而且错误信息对初学者更友好。

### 四、完整包结构：每个文件是什么、你该碰哪个

运行以下命令创建包并注入脚手架：

```text
usethis::create_package("mypkg")
rextendr::use_extendr()
```

`use_extendr()` 会在你的包目录中生成以下文件：

```text
mypkg/
├── R/
│   └── extendr-wrappers.R          ← 自动生成，不要碰
├── src/
│   ├── .gitignore                   ← 通常不用管
│   ├── Makevars.in                  ← 不要碰
│   ├── Makevars.win.in              ← 不要碰
│   ├── entrypoint.c                 ← 不要碰
│   ├── mypkg-win.def                ← 不要碰
│   └── rust/
│       ├── Cargo.toml               ← 可编辑（加依赖）
│       ├── document.rs              ← 不要碰
│       └── src/
│           └── lib.rs               ← 你写 Rust 的地方
├── tools/
│   ├── config.R                     ← 不要碰
│   └── msrv.R                       ← 不要碰
├── cleanup / cleanup.win            ← 不要碰
└── configure / configure.win        ← 不要碰
```

**你只需要编辑三个文件**：

| 文件 | 你做什么 |
| ----- | ----- |
| src/rust/src/lib.rs | 写 Rust 函数，这是核心 |
| src/rust/Cargo.toml | 加 Rust 依赖 |
| src/.gitignore | 偶尔需要，通常不用管 |

**其余所有文件都是构建系统的管道。** 不要手动编辑它们。`use_extendr()` 如果被重新运行，会覆盖这些文件。

**关键文件的作用**：

-   **`R/extendr-wrappers.R`** —— R 端的接口层。每次运行 `devtools::document()` 时自动重新生成，里面是你 Rust 函数的 R 包装版本。**永远不要手动编辑**。
-   **`src/entrypoint.c`** —— R 加载动态库时的 C 入口点。R 不认识 Rust，但认识 C。
-   **`src/Makevars.in`** —— 告诉 R 的构建系统：编译这个包时，先调用 cargo 编译 Rust，再把结果链接进来。
-   **`src/rust/Cargo.toml`** —— Rust 侧的“DESCRIPTION”。crate 同时以 `rlib`（供 document 二进制内省导出）和 `staticlib`（链接进 R 包）两种形态构建。`[[bin]]` 条目注册了 `document.rs`，用于在构建时生成 R 包装函数。
-   **`src/rust/document.rs`** —— 构建时运行的工具，扫描 `#[extendr]` 标记的函数，生成 `R/extendr-wrappers.R`。
-   **`src/rust/src/lib.rs`** —— 你的 Rust 代码主文件。`extendr_module!` 宏控制哪些函数、impl 块和子模块暴露给 R。**每个你希望 R 可用的函数都必须在 `extendr_module!` 中列出**。

### 五、开发循环：写代码、编译、加载

5.1 写 Rust 函数

打开 `src/rust/src/lib.rs`，写入你的逻辑：

```text
use extendr_api::prelude::*;

/// @export
#[extendr]
fn add_one(x: f64) -> f64 {
    x + 1.0
}

extendr_module! {
    mod mypkg;
    fn add_one;
}
```

5.2 编译并生成包装函数

```text
devtools::document()
```

从 rextendr 0.4.0 开始，`use_extendr()` 创建的包包含了 `document` 二进制文件，它会在正常的 cargo 构建步骤中自动生成 `R/extendr-wrappers.R`，因此 `devtools::document()` 可以直接使用，不需要 rextendr 特有的预处理。

5.3 加载包

```text
devtools::load_all()
```

现在就可以像普通 R 函数一样调用了：

```text
add_one(5)
# [1] 6
```

5.4 开发时的辅助命令

| 操作 | 命令 |
| ----- | ----- |
| 只检查 Rust 编译 | cargo check --manifest-path src/rust/Cargo.toml |
| 格式化 Rust 代码 | cargo fmt --manifest-path src/rust/Cargo.toml |
| 更新脚手架 | rextendr::update_scaffold() |

### 六、R 与 Rust 的类型映射

这是理解 extendr 如何工作的关键。extendr 在 R 的 C-API（基于 `SEXP` 指针）之上建立了类型桥接，R 的每种对象类型在 extendr 中都有对应的包装结构体。

标量类型

R 没有标量的概念（一切都是向量），Rust 也没有 NA 的概念。extendr 为此提供了专门的标量类型：

| R 类型 | Rust 原生类型 | extendr 包装类型 |
| ----- | ----- | ----- |
| integer(1) | i32 | Rint |
| logical(1) | bool | Rbool |
| double(1) | f64 | Rfloat |
| character(1) | String | Rstr |
| complex(1) | Complex<f64> | Rcplx |

向量类型

R 中一切皆向量。extendr 提供了对应的向量包装类型：

| R 类型 | extendr 类型 | C API 类型 |
| ----- | ----- | ----- |
| integer() | Integers | INTSXP |
| double() | Doubles | REALSXP |
| logical() | Logicals | LGLSXP |
| character() | Strings | STRSXP |
| raw() | Raw / &[u8] | RAWSXP |
| list() | List | VECSXP |

**性能提示**：尽可能使用 extendr 包装类型而非 Rust 原生 `Vec<T>`。接受或返回 `Vec<T>` 需要额外的内存分配，会带来开销。在可以容忍的开销场景下没问题，但如果能用 extendr 类型，优先使用它。

类型转换

extendr 通过 `From`、`Into` 和 `TryFrom` trait 在 R 和 Rust 值之间转换。`Robj` 是所有 R SEXP 指针的包装器，可以从 Rust 类型和迭代器创建 R 对象，也可以双向转换为 Rust 向量。

### 七、一个有实际价值的例子

R 的 `for` 循环慢，是因为每次迭代都有解释器开销。Rust 编译成机器码后，同样的逻辑快几个数量级。

**纯 R 版本**：

```text
ma_r <- function(x, w) {
  sapply(seq_along(x), function(i) {
    start <- max(1, i - w + 1)
    mean(x[start:i])
  })
}
```

**Rust 版本**：

```text
use extendr_api::prelude::*;

/// @export
#[extendr]
fn ma_rust(x: &[f64], w: i32) -> Vec<f64> {
    let w = w as usize;
    (0..x.len()).map(|i| {
        let start = if i + 1 >= w { i + 1 - w } else { 0 };
        x[start..=i].iter().sum::<f64>() / (i + 1 - start) as f64
    }).collect()
}

extendr_module! {
    mod mypkg;
    fn ma_rust;
}
```

R 端调用方式和普通 R 函数完全一样：

```text
ma_rust(c(1, 2, 3, 4, 5), 3)
```

数据量越大，差距越明显。

### 八、添加 Rust 依赖

`Cargo.toml` 中的 crate 名称、edition、`rlib`/`staticlib` 设置和 `[[bin]]` 条目都是构建过程的关键部分，不要手动修改。添加依赖时，用 `use_crate()`：

```text
rextendr::use_crate("rand")
rextendr::use_crate("rayon")
```

`use_crate()` 会自动调用 `cargo add`，把依赖写到 `Cargo.toml` 的 `[dependencies]` 中，类似于 `usethis::use_package()`。你也可以手动编辑或直接在终端用 `cargo add`。

### 九、测试与调试

9.1 测试策略

extendr 官方建议采用双轨测试：**R 侧用 `testthat` + `R CMD CHECK`，Rust 侧用标准的单元测试和集成测试**。按照 Rust 惯例，集成测试放在 `crate/src` 文件夹中，单元测试放在每个模块文件的末尾。

核心策略是将 Rust 实现与纯 R 实现的结果进行对比：

```text
# tests/testthat/test-moving_average.R
test_that("ma_rust matches R implementation", {
  r_ma <- function(x, w) {
    sapply(seq_along(x), function(i) {
      start <- max(1, i - w + 1)
      mean(x[start:i])
    })
  }
  set.seed(42)
  x <- rnorm(1000)
  expect_equal(ma_rust(x, 3), r_ma(x, 3))
})
```

rextendr 自身使用 testthat 第 3 版，并启用了并行测试。

9.2 VS Code / Positron 配置

**强烈推荐安装 rust-analyzer**。如果你使用 VS Code 或 Positron，它可以提供类型提示和自动补全建议。

运行以下命令自动配置：

```text
rextendr::use_vscode()
```

rust-analyzer 默认在工作区根目录查找 `Cargo.toml`。这个函数会创建 `.vscode/settings.json`，将工作区根目录指向 `src/rust/`，让扩展正常工作。从 rextendr 0.4 开始，如果你使用 VS Code 或 Positron，运行 `use_extendr()` 时会自动调用 `use_vscode()`。

### 十、发布到 CRAN

extendr 包开箱即与 CRAN 兼容。你只需要做额外的一步——**vendor（打包）你的 Rust 依赖**：

```text
rextendr::vendor_crates()
```

10.1 为什么需要 vendor

CRAN 非常重视可移植性。一个 R 包必须包含构建它所需的一切，这意味着 Rust 依赖不能在被安装时从网上下载。Vendoring 就是把依赖的源代码嵌入到你的 R 包中。`vendor_crates()` 会创建一个 `vendor.tar.xz` 文件，包含所有依赖的压缩源代码。

10.2 注意事项

-   `vendor_pkgs()` 已被弃用，请使用 `vendor_crates()`
-   根据依赖的数量，`vendor.tar.xz` 可能达到数 MB 级别
-   在 `cran-comments.md` 中注明包的大小，例如：“Tarball is 4.7mb due to vendored rust dependencies”
-   当前 CRAN 的 MSRV 为 1.81，你的包必须满足这个要求
-   CRAN 不支持 nightly 特性

### 十一、高级特性

11.1 异步 Rust（Tokio）

extendr 不提供异步函数接口，因为 R 没有真正的异步运行时。但这不意味着你不能利用 Rust 庞大的异步生态。许多 crate（如 `reqwest`、`axum`、`DataFusion`、`sqlx`）都基于 Tokio 运行时。

启用方式：

```text
rextendr::use_msrv("1.70")
rextendr::use_crate("tokio", features = "rt-multi-thread")
```

在 `lib.rs` 中定义一个共享的 Tokio 运行时，使用 `OnceLock` 实现线程安全的延迟初始化。然后在需要调用异步函数时，用 `.block_on()` 执行 future。

11.2 WebR 支持

从 rextendr 0.4 开始，所有 extendr 驱动的 R 包都开箱兼容 WebR，这意味着你的包可以在浏览器中运行，无需安装 R。WebR 支持不需要你做额外的工作。

**注意**：WebR 支持要求 `Cargo.toml` 的 release profile 中设置 `lto = true`。新包会自动处理，但已有包需要手动添加。并非所有 Rust crate 都兼容 wasm。

### 十二、谁已经在用

extendr 已经有一批生产落地的 R 包，覆盖多个领域：

-   **dialrs**：解析电话号码的 R 包
-   **arcgisgeocode**：地理编码工具
-   **rsgeo**：地理空间几何操作
-   **arcgisplaces**：地点搜索
-   **salso**、**caviarpd**、**fangs**：CRAN 上已发布的 Rust 驱动 R 包

一项针对野生猪非洲猪瘟（ASF）建模的研究展示了 extendr 的实际价值：研究者用 Rust 创建了一个自定义的稀疏缓存友好数据结构来追踪感染压力，这是 R 中无法实现的数据结构。extendr 让这个复杂数据结构能与原生 R 代码和数据结构无缝共存，在计算性能上带来了显著提升。

### 十三、现在不需要关心的东西

`configure`、`cleanup`、`Makevars.in`、`entrypoint.c`、`document.rs`——这些是构建系统的管道。它们的存在是为了让 `devtools::document()` 能自动完成编译和链接。你不需要改，也不需要理解它们的内部逻辑。

### 一句话总结

**`lib.rs` 是你写代码的地方，`Cargo.toml` 是你加依赖的地方，其他文件都是自动生成的管道。** 先用 `rust_function()` 在控制台验证，再建包；写 Rust 函数，`devtools::document()` 编译，`devtools::load_all()` 加载，在 R 里像普通函数一样调用。

[Rust Programming Language](https://link.zhihu.com/?target=http%3A//rust-lang.org)[https://extendr.rs/rextendr/](https://link.zhihu.com/?target=https%3A//extendr.rs/rextendr/)