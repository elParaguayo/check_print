# check_print

An extremely basic (and stupid) pre-commit hook for checking for rogue print statements
in your code.

For pre-commit: see https://github.com/pre-commit/pre-commit

### Using check_print with pre-commit:

Add this to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/elParaguayo/check_print
    rev: v0.1.0
    hooks:
    -   id: check-print-statements
```
