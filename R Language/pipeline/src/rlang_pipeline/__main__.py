"""让 `python -m rlang_pipeline` 可用。"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
