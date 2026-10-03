---
en-title: 【R Language】The tidymodels Worldview: A Rigorous Language Hidden in R
slug: tidymodels-worldview
zhihu-link: https://zhuanlan.zhihu.com/p/2088737447098303432
zhihu-created-at: 
---

![](https://pic2.zhimg.com/v2-26144a7b60f634c7e36759cd357adee7_1440w.jpg)

The tidymodels core workflow: resampling → preprocessing → modeling → postprocessing → measurement, with orchestration running through all of it.

![](https://pica.zhimg.com/v2-bdd050b9d03e9aa935134b9584c9d120_1440w.jpg)

The tidymodels surrounding ecosystem and hands-on examples: tuning, deployment, data, deep learning, and the list of core packages.

* * *

### 01 | What it believes: modeling is not "running a model", it is a pipeline

In the traditional view, modeling is "`lm(y ~ x, data)`, done."

tidymodels does not see it that way. It holds that modeling is a complete pipeline running from raw data to the final decision:

**Resampling → Preprocessing → Modeling → Postprocessing → Measurement**

Every one of these five stages affects the final result. You cannot care only about stage three and ignore the other four. In the traditional approach, preprocessing is written at the top of the script, evaluation is thrown together on the fly, and postprocessing does not exist at all — tidymodels says: no. These five stages must be treated as equals, and they must be managed explicitly.

That is why it turns each stage into its own package instead of stuffing everything into one big function.

![](https://pic4.zhimg.com/v2-24d00959b34d40506f5471b6df0dbf0f_1440w.jpg)

The tidymodels five-stage pipeline: resampling → preprocessing → modeling → postprocessing → measurement, with orchestration running through all of it.

* * *

### 02 | What it believes: data leakage is original sin

This is the most central conviction in the tidymodels worldview.

What is data leakage? Put simply: while training a model, you accidentally "peek" at information from the test data.

A classic example: you standardize the entire dataset first, and only then split it into a training set and a test set. At that point the standardization parameters in the training set already have information from the test set mixed into them. Your model evaluation will look too optimistic, because you cheated.

tidymodels calls data leakage "a pervasive failure mode". Its design goal is: **make sure you have no opportunity to make the mistake.**

How does it do that? By bundling everything into a single `workflow()` object. When you call `fit()`, it automatically learns the preprocessing parameters from the training data alone; when you call `predict()`, it automatically applies the parameters learned during training to the new data.

**You do not need to manage these steps by hand, because managing them by hand is exactly where things go wrong.**

The one and only reason `workflow` exists is not to make your code look nice — it is to stop you from cheating.

![](https://pic2.zhimg.com/v2-d250db7acbfcc6a9dbf0253e8e8378d3_1440w.jpg)

Splitting the dataset

* * *

### 03 | What it believes: models are interchangeable parts

![](https://picx.zhimg.com/v2-4c94a2a94a0894177123bd8bb7f1ad59_1440w.jpg)

In traditional R modeling, switching algorithms means switching to a completely different syntax. Every function has its own parameter names, its own data format, its own return structure. Change the algorithm and you have to learn everything again.

tidymodels says: that should not be the case.

It uses `parsnip` to unify all models under a single syntax. Unified parameter names, unified data interface, unified return structure. Models become interchangeable parts. You can swap models the way you swap a tire, without having to learn how to drive all over again.

The conviction behind this is: **the heart of modeling is "what you want to do", not "what tool you use to do it".**

* * *

### 04 | What it believes: preprocessing is not "cleaning data", it is "part of the model"

![](https://pic4.zhimg.com/v2-977f0ef0796236de3df71c5e9b6c4485_1440w.jpg)

In the traditional view, preprocessing means "getting the data clean" — preparatory work done before modeling, a separate matter from the model itself.

tidymodels says: wrong. Preprocessing is part of the model.

Why? Because the preprocessing parameters — means, standard deviations, encoding mappings, missing-value imputation rules — are learned from the data. Like a model's coefficients, they are "trained". Manage them separately from the model and you will run into trouble.

So `recipes` is not a "data cleaning tool" but a "preprocessing specification". What it defines is "how things should be handled", not "the result after handling". The actual handling happens at the moment of `fit()`, performed automatically by `workflow`.

**Preprocessing and the model are an inseparable whole. Pull them apart and you have a breeding ground for data leakage.**

* * *

### 05 | What it believes: evaluation must be honest

In the traditional approach, evaluation is often "compute the accuracy on the training set" or "just do some 70⁄30 split and run it".

tidymodels says: not good enough.

It puts `rsample` at the very first step of the whole process, not the last. This means: **before you do anything else, think clearly about how you will evaluate.**

Cross-validation, bootstrap, validation sets, spatial resampling… `rsample` provides a complete toolkit that lets you design your evaluation scheme before you start modeling. What is more, `workflow` guarantees that on every resample the preprocessing parameters are learned only from that fold's training data — every fold's evaluation is honest.

**A model's worth lies not in how good it is on the training set, but in how good it is on unseen data. Designing the evaluation scheme matters more than the model itself.**

* * *

### 06 | What it believes: everything can be tuned, everything can be compared, and models ultimately have to go to production

Tuning is not "try a few settings by hand and see which looks best". `tune` and `dials` turn hyperparameter optimization into a systematic search process. You can define the search space, choose a search strategy, run in parallel, and automatically select the best. And because every model uses a unified interface, you can compare multiple models at once, or even stack several of them.

And a finished model run is not the end either. `vetiver` handles versioning, deployment, and monitoring. `butcher` handles slimming down. `tidypredict` and `orbital` translate models into SQL or portable equations. `applicable` detects whether new samples have drifted away from the training distribution.

**The endpoint of modeling is not "obtaining a model" but "making the model create value in the real world".**

* * *

### 07 | Why are there so many packages? Because there are many scenarios, not because the thinking is muddled

The very first line of the official cheatsheet makes it clear: it is not a function manual, it is an ecosystem map.

The core meta-package `library(tidymodels)` loads only a dozen or so packages:

- `rsample`
- `recipes`
- `parsnip`
- `workflows`
- `yardstick`
- `tune`
- `dials`
- `broom`
- `tailor`
- `infer`
- `modeldata`
- `workflowsets`

Everything else is a plugin you load "only when you need it":

| Scenario | Plugin |
| ----- | ----- |
| Text | textrecipes |
| Class imbalance | themis |
| Spatial data | spatialsample |
| Survival analysis | censored |
| Deep learning | tabby / brulee |
| Deployment | vetiver |

**There are many packages because machine learning runs into many problems. Not because the thinking is muddled.**

The right way to read it: treat the cheatsheet as a dictionary, not as a textbook. Want to learn the flow? Look at the five-stage diagram. Want to look up a scenario? Consult the corresponding grouping. Writing code day to day? Use only the dozen or so core packages.

![](https://picx.zhimg.com/v2-bcc18b5525ec93a89a7d7c7319e989ed_1440w.jpg)

* * *

### 08 | An objective assessment: is it actually pleasant to use?

### Strengths

- Unified syntax, easy switching between algorithm engines
- Fundamentally prevents data leakage through `workflow`
- Modular and composable, deeply integrated with the Tidyverse
- Rigorous evaluation and systematic tuning, suited to production-grade pipelines

### Weaknesses

- Steep learning curve, with abstract and scattered concepts
- A huge number of packages and functions, easy to scare off newcomers
- Abstraction and deferred execution add to the cost of understanding
- Built on tibble underneath, so tuning on large data can be slow
- Some critics point out that its bootstrap methods are statistically inconsistent for inference, making it better suited to predictive modeling than to strict statistical inference

### Side-by-side comparison

| Framework | Design philosophy | Learning curve | Where it fits |
| ----- | ----- | ----- | ----- |
| tidymodels | Modular, rigorous, composable | High | Production-grade, reproducible, leakage-proof pipelines |
| caret | All-in-one, simple and direct | Low | Rapid prototyping |
| mlr3 | Object-oriented, highly extensible | Very high | Benchmarking, complex experiments |
| scikit-learn | Python ecosystem, unified API | Medium | Python users, deep learning integration |

**Conclusion:** If you are new to R, or you just want to run a model quickly, it may leave you frustrated. If you are an experienced data scientist with extremely high demands for reproducibility, leakage prevention, and automated tuning, it will be a tremendous advantage.

* * *

### 09 | Is it like any programming language?

tidymodels really is like certain programming languages.

### Most like Rust: compile-time error prevention and an ownership mindset

![](https://pica.zhimg.com/v2-710acbcb35baba22d2a3f4ec131d4de2_1440w.jpg)

Rust's Borrow Checker enforces memory borrowing rules at the compilation stage; if the code has a memory safety hazard, it fails to compile and simply will not let you run it. tidymodels' `workflow` forcibly binds preprocessing and model together at the modeling stage: if you try to use information from the test set to guide training, the process errors out immediately or blocks you automatically.

Rust uses Traits to define a unified interface; implement that Trait and you can plug in seamlessly. `parsnip` is exactly the same — it defines "what a model must look like", and as long as a package implements that interface, whether it is `ranger` or `xgboost`, it can be swapped in seamlessly.

Rust uses Cargo to manage extremely fragmented yet highly composable crates. `tidymodels` likewise uses a meta-package mechanism to chain dozens of independent small packages into one ecosystem.

**Both chose to trade "strict constraints early on" for "absolute safety later on".**

### Its soul is like Haskell: pure functional style and lazy evaluation

![](https://pica.zhimg.com/v2-dcd541b64aa7f32b9fab44302402d346_1440w.jpg)

Data in Haskell is immutable; you cannot modify a variable, only generate new data from old data. tidymodels follows this strictly. You use `recipe()` to define a recipe and `step_*()` to add steps, and every step returns a new recipe object, never modifying the original data.

Haskell chains functions with `>>=` or `$`. tidymodels chains workflows with `%>%` or `|>`. Philosophically they are entirely in agreement: write a complex computation as a series of clear, readable data transformation pipelines.

Haskell's famous trait is "compute nothing until the last possible moment". `recipes`' `prep()` and `bake()` embody this perfectly. When you write down a pile of `step_normalize()`, R does not immediately go and compute means and variances; only at the moment you call `fit()` does it truly begin to calculate. This design exists precisely to prevent "computing ahead of time and thereby leaking data".

### Its architecture is like Java/C#: object orientation and dependency injection

In Java you write `List list = new ArrayList()`; in `parsnip` you write `linear_reg() %>% set_engine("lm")`. The front-end code depends only on the abstract interface, while the concrete implementation can be replaced at any time.

Java's Spring framework assembles its components into Beans. `workflow()` is a container that injects a `recipe` and a `model` into itself, forming a complete executable unit.

### The ultimate conclusion

**tidymodels is essentially "a domain-specific language embedded in R, built specifically for machine learning". It borrows R's syntactic shell, but its worldview is Rust-grade rigor plus Haskell-grade pure-functional elegance.**

* * *

### 10 | Conclusion: not complicated, but rigorous

What makes tidymodels intimidating stems, in essence, from the fact that in pursuit of engineering rigor it sacrificed how intuitive it is to get started.

It is not a hammer; it is an entire factory. You cannot "just use it casually" — you have to understand its worldview before you can truly use it.

But once you understand it, you will find:

**It is not complicated, it is rigorous. It is not cumbersome, it is complete. It forces you to become a better modeler — not because you use it, but because it will not let you cut corners.**

If you remember only one sentence:

> **One workflow, five stages, one iron law against leakage. Many packages because there are many scenarios, not because the thinking is muddled. Its soul is the rigor of Rust plus the elegance of Haskell.**
