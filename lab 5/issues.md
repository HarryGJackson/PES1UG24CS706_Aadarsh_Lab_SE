# Lab 5: Static Code Analysis – Issues Found and Fixed

**Name:** Aadarsh Reddy Yedhala | **SRN:** PES1UG24CS706
**File:** `student_grade_system.py`

## Results

| Tool | Before | After |
|---|---|---|
| Pylint | 5.51/10 | 10.00/10 |
| Bandit | 6 issues (2 High, 1 Medium, 3 Low) | 0 issues |
| Flake8 | 8 issues | 0 issues |

## Issue Table

Line numbers refer to the original file.

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Shell injection (`os.system`) | Bandit B605 – High | 60 | Filename concatenated into a shell command; could run arbitrary commands | Removed `os.system`, replaced with `print()` |
| Weak hash (MD5) | Bandit B324 – High | 49 | MD5 is cryptographically broken | Switched to `hashlib.sha256` |
| Use of `eval` | Bandit B307 – Medium | 44 | `eval(gpa_expr)` executes any Python string (code injection) | Removed `eval`; GPA computed as `avg_score / scale` |
| Insecure random PIN | Bandit B311 – Low | 53 | `random.randint` is predictable | Used `1000 + secrets.randbelow(9000)` |
| Hardcoded token | Bandit B105 – Low | 64, 72 | Secret token in source code and printed | Read from `PORTAL_TOKEN` env variable; print only whether it is set |
| Bare `except: pass` | Bandit B110, Flake8 E722, Pylint W0702 | 26–27 | Silently swallows all errors | Catch `KeyError`, print message, return `False` |
| Mutable default arg | Pylint W0102 – Bug | 15 | `grade_list=[]` shared across calls | Default to `None`, create list inside function |
| Unused import / variables | Flake8 F401, F841 | 6, 31, 43 | `json`, `grace_marks`, `avg_score` unused | Removed them / used `avg_score` directly |
| Comparison to None | Flake8 E711 | 32 | `== None` used | Changed to `is None` |
| Long lines / no final newline | Flake8 E501, W292 | 19, 34, 75 | Lines over 79 chars; missing newline at end | Split lines; added final newline |
| Naming + missing docstrings | Pylint C0103, C0116 | 15–63 | `addGrade` not snake_case; 8 functions without docstrings | Renamed to `add_grade`; added docstrings |
| Unsafe file handling | Pylint R1732, W1514 | 57–59 | `open()` without `with` or encoding | `with open(filename, "w", encoding="utf-8")` |
| Old formatting / redundant if-else | Pylint C0209, R1705 | 19, 35–38 | `%` formatting; `if…return True else return False` | f-string; `return avg >= pass_threshold` |

## Reflection

**1. Easiest and hardest fixes?**
The Flake8 style issues were easiest. Unused imports, `== None` and the missing newline are one-line changes that don't affect behaviour. Removing `eval` was hardest: the function took an expression string, so it had to be changed to take a numeric `scale` instead, while checking the GPA output stayed 4.35.

**2. Any false positives?**
Bandit's MD5 warning (B324, High) is arguably a false positive here. The hash only creates an ID from the student number and isn't used for passwords or security. It was still switched to SHA-256 since that cost nothing. Some Pylint messages, like preferring f-strings (C0209), are style preferences rather than real bugs.

**3. How would you use these tools in a real workflow?**
Run Flake8 and Pylint in the editor and as a pre-commit hook, so issues are caught before committing. In CI (e.g. GitHub Actions), run all three on every push and fail the build on any Bandit Medium/High issue or a Pylint score below 9.5.

**4. What improvements did you observe?**
Security: two code-injection risks (`eval`, `os.system`) and the hardcoded token are gone. Robustness: errors are no longer silently ignored, the file is always closed, and the shared default list bug is fixed. Readability: consistent naming and docstrings everywhere. The program's output stayed the same.
