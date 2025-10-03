![](https://pic2.zhimg.com/v2-0dee9824ab0579527a569ed5db162467_1440w.jpg)

Unlike **stepwise regression**, **all-subsets regression** does not explore partial combinations according to the "stepwise variable addition and subtraction" rule. Instead, it directly traverses all possible combinations of independent variables and selects the globally optimal model through indicators such as AIC and BIC. All-subsets regression has extremely high computational costs and is only suitable for scenarios with few independent variables; stepwise regression, on the other hand, has a small computational load and is more suitable for situations with many variables. However, stepwise regression may fall into local optima due to path limitations.

Therefore, this article is not actually a true all-subsets regression, otherwise the computational power requirements would be enormous, and the model would be overly complex with no interpretability, making it not worth the cost.

**Therefore, we should manually set the parameter `main_terms_spec` (the function used in this article) to control the number of main effects.**

* * *

## Selecting Response Variable

Preliminary observation (omitted) to make the response variable conform to model assumptions. Here, a logarithmic transformation is applied:

```R
dataset <- mtcars |>
  mutate(log_mpg = log(mpg), .keep = "unused")
```

Set the response variable (dependent variable) as `log_mpg`:

```R
target <- "log_mpg"
```

## Generating All-Subsets Formulas for the Model

Here, I use a function I wrote (placed at the end) to generate all-subsets formulas for the model (in data frame form):

```R
formulas <- generate_model_formulas(data = dataset,
                                    target = target,
                                    main_terms_spec = 2) # Number of main effects
                                    # Can also write 1:3, 2:4, etc.
# Note that "number of models" grows explosively with "number of main effects" and "number of independent variables"
```

![](https://pic1.zhimg.com/v2-f3aef93d138b1ed1a13adb8ebca280f8_1440w.jpg)

## Batch Modeling

Batch modeling with `map()` and slightly processing with `broom`:

```R
model_results <- formulas |>
  mutate(
    # Batch modeling
    model = map(formula, \(f) possibly(lm, tibble())(as.formula(f), dataset)),
    # Batch summarization
    Glance = map(model, glance),
    Tidy = map(model, tidy),
    Augment = map(model, augment)
  ) |>
  unnest(Glance, keep_empty = TRUE) |>
  # Sort by ascending AIC, descending r-squared
  arrange(AIC, desc(r.squared)) |>
  # Adjust column positions
  relocate(formula,
           has_interaction,
           interaction_count,
           r.squared,
           AIC,
           Tidy,
           Augment)
```

![](https://picx.zhimg.com/v2-98b4cf943184a9a58f4a6e2bc9fe4a07_1440w.jpg)

**AIC (Akaike Information Criterion)** is an important indicator for measuring model complexity and goodness of fit. The core idea of AIC is to find a model that can fit the data well without being overly complex. The calculation formula for $AIC$ is: $$AIC = 2k - 2ln(L)$$ where $k$ is the number of parameters in the model and $L$ is the likelihood function of the model.

**The smaller the AIC value, the better the model.**

* * *

Function for generating all-subsets formulas for the model:

```R
generate_model_formulas <- function(data, target, main_terms_spec) {
  # Validate target variable existence
  if (!target %in% colnames(data))
    stop("Target variable 'target' not in dataset")
  
  # Validate main_terms_spec type legality
  if (!is.numeric(main_terms_spec) &&
      !is.character(main_terms_spec)) {
    stop("'main_terms_spec' must be a numeric (vector) or character vector")
  }
  
  # Extract independent variables (excluding target variable)
  all_predictors <- data |> select(-all_of(target)) |> colnames()
  
  # Generate main effect combinations
  if (is.numeric(main_terms_spec)) {
    # Handle numeric vectors (such as 1:3)
    if (length(main_terms_spec) > 1) {
      return(map_dfr(
        main_terms_spec,
        \(n) generate_model_formulas(data, target, n)
      ))
    }
    # Validate main effect count range (allowing 1)
    if (main_terms_spec < 1 ||
        main_terms_spec > length(all_predictors)) {
      stop("Number of main effects must be between 1 and ", length(all_predictors))
    }
    main_combinations <- combn(all_predictors, main_terms_spec, simplify = FALSE)
  } else {
    # Handle character vectors (specified variables, compatible with single variable)
    if (!all(main_terms_spec %in% all_predictors)) {
      stop("Specified main effects contain invalid variables")
    }
    main_combinations <- list(main_terms_spec)
  }
  
  # Generate model formulas (compatible with main effect count = 1)
  map_dfr(main_combinations, \(one_main) {
    main_str <- paste(one_main, collapse = " + ")
    main_count <- length(one_main)  # New: Get current number of main effects
    
    # Only generate interaction terms when main effect count ≥ 2 (avoid 1 choose 2 error)
    if (main_count >= 2) {
      int_pairs <- combn(one_main, 2, \(p) paste(p, collapse = " : "), simplify = TRUE)
      n_pairs <- length(int_pairs)
      # Generate combinations with 0 to n_pairs interaction terms
      # Only generate double interactions to control model complexity and interpretability
      all_ints <- c(list("none"), map(
        1:n_pairs,
        \(k) combn(
          int_pairs,
          k,
          paste,
          collapse = " + ",
          simplify = TRUE
        )
      )) |> unlist()
    } else {
      # When main effect count = 1, no interaction terms, only keep "none"
      all_ints <- "none"
    }
    
    # Uniformly generate formula data frame
    tibble(
      formula = ifelse(
        all_ints == "none",
        paste(target, "~", main_str),
        paste(target, "~", main_str, "+", all_ints)
      ),
      has_interaction = all_ints != "none",
      interaction_count = ifelse(all_ints == "none", 0, str_count(all_ints, "\\+") + 1),
      main_terms = main_str,
      interaction_terms = all_ints
    )
  }) |> distinct(formula, .keep_all = TRUE)
}
```

Reference:

[【R Language】Tidy Modeling with broom Package](https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91broom%20Package%20for%20Tidy%20Modeling.md)
