---
en-title: 【R Language】Writing R Extensions in Rust: A Complete Practical Guide
slug: rust-extensions-for-r
zhihu-link: https://zhuanlan.zhihu.com/p/2087557727866320879
zhihu-created-at: 
---

### I. The Core Mental Model

R does not know Rust. What R knows is a C dynamic library (`.dll` / `.so` / `.dylib`).

Loading an extension package in R is, at bottom, `dyn.load()` on a dynamic library, followed by `.Call()` to invoke functions in it that follow the C ABI. Rcpp works because C++ can compile a dynamic library that exposes the C ABI. extendr works because **Rust can compile a C-ABI dynamic library too**.

What `{extendr}` does is generate two layers of glue automatically:

| Layer | Job |
| ----- | ----- |
| Rust side | Uses the #[extendr] macro to wrap functions as extern "C", and handles conversion between R objects and Rust types |
| R side | Generates .Call() wrapper functions and NAMESPACE exports |

You write Rust functions and call them from R like ordinary functions. What R sees is still a C dynamic library.

`{extendr}` is the collective name for a group of crates (`extendr-api`, `extendr-engine`, `extendr-macros`). It occupies the same niche as Rcpp/cpp11, but underneath it is Rust. `{rextendr}` is the companion package on the R side, handling scaffold generation and toolchain management. extendr's design goal is to offer an opinionated API, drawing heavily on the ergonomics of Rcpp and cpp11.

### II. Environment Setup and Health Check

![](https://pic3.zhimg.com/v2-6f28b147f6d999a41bfedbc428ce19ec_1440w.jpg)

rextendr

Before you start, make sure three things are in place:

1. **Rust toolchain**: install `rustup` from [Rust Programming Language](https://link.zhihu.com/?target=http%3A//rust-lang.org). extendr's current minimum supported Rust version (MSRV) is 1.65.0, which keeps it CRAN-compliant. Windows users need to add the GNU toolchain as well: `rustup target add x86_64-pc-windows-gnu`
2. **R version**: R >= 4.2.0 is recommended
3. **R packages**: install `install.packages(c("rextendr", "usethis", "devtools"))` in R
4. **One-shot health check**: run the command below — all green checkmarks and you can begin:

```r
rextendr::rust_sitrep()
```

`rust_sitrep()` produces a detailed report on your current Rust infrastructure, along with suggestions for fixing whatever is not in order.

### III. Experiment First, Build the Package Later

Do not start by creating a package. First verify your core logic in the R console with `rust_function()`:

```r
rextendr::rust_function("
fn add_one(x: f64) -> f64 {
    x + 1.0
}
")
```

Then call it directly:

```r
add_one(5)
# [1] 6
```

The purpose of this step is to turn "Rust code running inside R" from an abstraction into something concrete. Once you have confirmed that the function logic is correct and the performance gain meets expectations, build the package for real.

As a compiled language, Rust converts code to machine language before running it, so it executes far faster than an interpreted language like R. The standard way to pair a compiled language with R is: use `Rprof()` to find the bottlenecks, rewrite the very slow parts in a compiled language, then write an R function to call it. Compared with C++, Rust has stricter code validation and memory-safety mechanisms, and its error messages are friendlier to beginners.

### IV. The Complete Package Structure: What Each File Is and Which Ones You Should Touch

Run the following commands to create the package and inject the scaffold:

```r
usethis::create_package("mypkg")
rextendr::use_extendr()
```

`use_extendr()` generates the following files in your package directory:

```text
mypkg/
├── R/
│   └── extendr-wrappers.R          ← auto-generated, do not touch
├── src/
│   ├── .gitignore                   ← usually no need to touch
│   ├── Makevars.in                  ← do not touch
│   ├── Makevars.win.in              ← do not touch
│   ├── entrypoint.c                 ← do not touch
│   ├── mypkg-win.def                ← do not touch
│   └── rust/
│       ├── Cargo.toml               ← editable (add dependencies here)
│       ├── document.rs              ← do not touch
│       └── src/
│           └── lib.rs               ← this is where you write Rust
├── tools/
│   ├── config.R                     ← do not touch
│   └── msrv.R                       ← do not touch
├── cleanup / cleanup.win            ← do not touch
└── configure / configure.win        ← do not touch
```

**You only need to edit three files**:

| File | What you do |
| ----- | ----- |
| src/rust/src/lib.rs | Write Rust functions — this is the core |
| src/rust/Cargo.toml | Add Rust dependencies |
| src/.gitignore | Occasionally needed, usually you can ignore it |

**Every other file is build-system plumbing.** Do not edit them by hand. If `use_extendr()` is run again, it will overwrite these files.

**What the key files do**:

- **`R/extendr-wrappers.R`** —— the interface layer on the R side. It is regenerated automatically every time you run `devtools::document()`, and it holds the R wrappers for your Rust functions. **Never edit it by hand**.
- **`src/entrypoint.c`** —— the C entry point R uses when it loads the dynamic library. R does not know Rust, but it knows C.
- **`src/Makevars.in`** —— tells R's build system: when compiling this package, first invoke cargo to compile the Rust, then link the result in.
- **`src/rust/Cargo.toml`** —— the Rust-side "DESCRIPTION". The crate is built in two forms at once: `rlib` (so the document binary can introspect the exports) and `staticlib` (linked into the R package). The `[[bin]]` entry registers `document.rs`, which generates the R wrapper functions at build time.
- **`src/rust/document.rs`** —— a build-time tool that scans functions marked with `#[extendr]` and generates `R/extendr-wrappers.R`.
- **`src/rust/src/lib.rs`** —— your main Rust source file. The `extendr_module!` macro controls which functions, impl blocks, and submodules are exposed to R. **Every function you want available from R must be listed in `extendr_module!`**.

### V. The Development Loop: Write, Compile, Load

5.1 Writing a Rust function

Open `src/rust/src/lib.rs` and write your logic:

```rust
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

5.2 Compiling and generating the wrapper functions

```r
devtools::document()
```

As of rextendr 0.4.0, packages created by `use_extendr()` ship with the `document` binary, which generates `R/extendr-wrappers.R` automatically during the normal cargo build step. `devtools::document()` therefore works as-is, with no rextendr-specific preprocessing required.

5.3 Loading the package

```r
devtools::load_all()
```

Now you can call it just like an ordinary R function:

```r
add_one(5)
# [1] 6
```

5.4 Convenience commands while developing

| Task | Command |
| ----- | ----- |
| Check Rust compilation only | cargo check --manifest-path src/rust/Cargo.toml |
| Format Rust code | cargo fmt --manifest-path src/rust/Cargo.toml |
| Update the scaffold | rextendr::update_scaffold() |

### VI. Type Mapping Between R and Rust

This is the key to understanding how extendr works. extendr builds a type bridge on top of R's C API (which is based on `SEXP` pointers), and every R object type has a corresponding wrapper struct in extendr.

Scalar types

R has no notion of scalars (everything is a vector), and Rust has no notion of NA. extendr provides dedicated scalar types for exactly this reason:

| R type | Rust native type | extendr wrapper type |
| ----- | ----- | ----- |
| integer(1) | i32 | Rint |
| logical(1) | bool | Rbool |
| double(1) | f64 | Rfloat |
| character(1) | String | Rstr |
| complex(1) | Complex<f64> | Rcplx |

Vector types

In R everything is a vector. extendr provides matching vector wrapper types:

| R type | extendr type | C API type |
| ----- | ----- | ----- |
| integer() | Integers | INTSXP |
| double() | Doubles | REALSXP |
| logical() | Logicals | LGLSXP |
| character() | Strings | STRSXP |
| raw() | Raw / &[u8] | RAWSXP |
| list() | List | VECSXP |

**Performance tip**: use extendr wrapper types rather than Rust's native `Vec<T>` wherever you can. Accepting or returning a `Vec<T>` requires an extra memory allocation, which adds overhead. That is fine when you can tolerate the cost, but if an extendr type will do the job, prefer it.

Type conversion

extendr converts between R and Rust values through the `From`, `Into`, and `TryFrom` traits. `Robj` is the wrapper around all R SEXP pointers: it can create R objects from Rust types and iterators, and it can convert in both directions to and from Rust vectors.

### VII. An Example With Real Practical Value

R's `for` loops are slow because every iteration carries interpreter overhead. Compiled to machine code, the same logic in Rust is orders of magnitude faster.

**Pure R version**:

```r
ma_r <- function(x, w) {
  sapply(seq_along(x), function(i) {
    start <- max(1, i - w + 1)
    mean(x[start:i])
  })
}
```

**Rust version**:

```rust
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

Calling it from R works exactly like calling an ordinary R function:

```r
ma_rust(c(1, 2, 3, 4, 5), 3)
```

The larger the data, the more obvious the gap.

### VIII. Adding Rust Dependencies

The crate names, edition, `rlib`/`staticlib` settings, and `[[bin]]` entry in `Cargo.toml` are all essential parts of the build process — do not modify them by hand. To add a dependency, use `use_crate()`:

```r
rextendr::use_crate("rand")
rextendr::use_crate("rayon")
```

`use_crate()` calls `cargo add` for you and writes the dependency into `[dependencies]` in `Cargo.toml`, much like `usethis::use_package()`. You can also edit it by hand, or just run `cargo add` in a terminal.

### IX. Testing and Debugging

9.1 Testing strategy

extendr officially recommends a two-track testing approach: **use `testthat` + `R CMD CHECK` on the R side, and standard unit and integration tests on the Rust side**. Following Rust convention, integration tests live in the `crate/src` folder and unit tests go at the end of each module file.

The core strategy is to compare the results of the Rust implementation against a pure R implementation:

```r
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

rextendr itself uses testthat 3rd edition with parallel testing enabled.

9.2 VS Code / Positron configuration

**Installing rust-analyzer is strongly recommended**. If you use VS Code or Positron, it provides type hints and autocompletion suggestions.

Run the following command to configure it automatically:

```r
rextendr::use_vscode()
```

By default rust-analyzer looks for `Cargo.toml` in the workspace root. This function creates `.vscode/settings.json` and points the workspace root at `src/rust/`, so the extension works properly. As of rextendr 0.4, if you use VS Code or Positron, running `use_extendr()` calls `use_vscode()` for you.

### X. Publishing to CRAN

extendr packages are CRAN-compatible out of the box. There is just one extra step you need to take — **vendor your Rust dependencies**:

```r
rextendr::vendor_crates()
```

10.1 Why vendoring is necessary

CRAN cares a great deal about portability. An R package must contain everything needed to build it, which means Rust dependencies cannot be downloaded from the internet at install time. Vendoring means embedding the source code of your dependencies into your R package. `vendor_crates()` creates a `vendor.tar.xz` file containing the compressed source of all dependencies.

10.2 Things to watch out for

- `vendor_pkgs()` is deprecated, use `vendor_crates()` instead
- Depending on the number of dependencies, `vendor.tar.xz` can reach several MB
- Note the package size in `cran-comments.md`, for example: "Tarball is 4.7mb due to vendored rust dependencies"
- The current CRAN MSRV is 1.81, and your package must satisfy it
- CRAN does not support nightly features

### XI. Advanced Features

11.1 Async Rust (Tokio)

extendr does not offer an async function interface, because R has no real async runtime. But that does not mean you cannot take advantage of Rust's vast async ecosystem. Many crates (such as `reqwest`, `axum`, `DataFusion`, `sqlx`) are built on the Tokio runtime.

How to enable it:

```r
rextendr::use_msrv("1.70")
rextendr::use_crate("tokio", features = "rt-multi-thread")
```

Define a shared Tokio runtime in `lib.rs`, using `OnceLock` for thread-safe lazy initialization. Then, whenever you need to call an async function, execute the future with `.block_on()`.

11.2 WebR support

As of rextendr 0.4, every extendr-powered R package is WebR-compatible out of the box, which means your package can run in the browser with no R installation. WebR support requires no extra work from you.

**Note**: WebR support requires `lto = true` in the release profile of `Cargo.toml`. New packages handle this automatically, but existing packages need to add it manually. Not every Rust crate is wasm-compatible.

### XII. Who Is Already Using It

extendr already has a set of production R packages spanning several domains:

- **dialrs**: an R package for parsing phone numbers
- **arcgisgeocode**: geocoding tools
- **rsgeo**: geospatial geometry operations
- **arcgisplaces**: place search
- **salso**, **caviarpd**, **fangs**: Rust-powered R packages already published on CRAN

A study modeling African swine fever (ASF) in wild boar demonstrates extendr's practical value: the researchers used Rust to build a custom sparse, cache-friendly data structure for tracking infection pressure — a data structure that is not achievable in R. extendr let this complex data structure coexist seamlessly with native R code and data structures, delivering a significant boost in computational performance.

### XIII. What You Don't Need to Worry About Right Now

`configure`, `cleanup`, `Makevars.in`, `entrypoint.c`, `document.rs` — these are build-system plumbing. They exist so that `devtools::document()` can handle compilation and linking automatically. You do not need to change them, and you do not need to understand their internals.

### One-Sentence Summary

**`lib.rs` is where you write your code, `Cargo.toml` is where you add dependencies, and every other file is generated plumbing.** Validate in the console with `rust_function()` first, then build the package; write Rust functions, compile with `devtools::document()`, load with `devtools::load_all()`, and call them from R like ordinary functions.

[Rust Programming Language](https://link.zhihu.com/?target=http%3A//rust-lang.org)[https://extendr.rs/rextendr/](https://link.zhihu.com/?target=https%3A//extendr.rs/rextendr/)
