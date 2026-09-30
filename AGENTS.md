# AGENTS.md

## Local setup

See `Justfile` for common local development commands.

Note that the developer might have a `.env` file that overrides the default `RUN` command with a conda env.

## Style guide

- Prefer functional code over object-oriented code unless state management is required
- Avoid any side effects in methods and functions, unless made explicit in the docstring and name (use terminology such as `set_`, `update_`, `load_`, or `initialize_`). Methods that modify the database are often called `save_`, `update_`, or `process_`. If a method returns anything, we expect it doesn't have any side effects - either return everything or nothing, unless approved by developer.
- Prefer list comprehensions and other one-liners over tiny helper functions unless they ensure consistent behavior
- Place important end-to-end functions at the top of the file, helper functions below them
- Use imperative verbs for function and method names, e.g. `sanitize_name()` instead of `sanitized_name()` or `format_group_suffix()` instead of `group_suffix()`. But don't get too creative use `get` or other common verbs if possible: `prepare`, `validate`, `parse`, `format`, `visualize`, `select`, `process`, `show`, `create`, `save`, `submit`, `generate`, ...
- Before writing code that interacts with the database, read [apidocs/database.md](docs/source/apidocs/database.md) and [ovo/core/database/sql_db.py](ovo/core/database/sql_db.py)
- Avoid using `db.get` in for loops or in functions that get called in for loops, use `db.select` instead, possibly converting to dict using dict comprehension and then iterating through that in the for loop. Consider using `db.select_values` or `db.select_dict` when only one field is needed.
- When saving multiple DB entries, always use `db.save_all` to ensure atomic behavior.
- In `ovo.app`, use cached functions defined in [ovo/app/utils/cached_db.py](ovo/app/utils/cached_db.py). Introduce new cached functions if needed.
- The codebase has pre-existing ruff linting errors. Never run `ruff check --fix` or `ruff format` across it - check and fix only the files you touched.
- Prefer validating by refusing with a message that says what to do instead, rather than sanitizing or escaping silently
- Do not worry about revealing rare exceptions to the user, do not add unnecessary try/except blocks. Prefer checking your assumptions with assert or if + st.error / ValueError, and then let the exception propagate if it is unexpected. When processing multiple items, consider if everything should fail or if a list of warnings should be collected and returned downstream.
- Prefer exiting early rather than nesting code in if/else blocks

## Contributing

- Some feature requests might benefit from modifying core methods on DBEngine, Storage, Workflow, Structure, or adding new ones, rather than introducing complex logic on top of them. This is encouraged if backwards-compatible, but always consult it with the developer.
- If a developer's request involves more changes than it might appear, don't be afraid to push back, and confirm before proceeding, unless you found out too late - then it's better to finish the job but point out the cost in your summary.
- When planning a new feature, the most important aspect to agree on is how things should be called (new terminology) and how they should be stored. There should always be one "source of truth" and there should ideally only be a few channels for modifying it. It might be hard to figure out the shape of this from the beginning, so you can reiterate after you and the developer learn more from building the first iteration.
- This file is meant to be primarily edited by humans. Do not pollute this with random notes. But if you see any inconsistencies, or crucial missing information, suggest any line-by line changes to the developer and ask for approval to edit.

## Tests

- For the sake of readability, prefer not creating global variables or too many fixtures in tests, rather hardcode the specific values, unless too long
- At the top of a unit test file, prefer creating a single multi-step test that covers the end-to-end behavior, even with multiple subsections with leading comments, so that you can avoid creating many trivial small tests

## Common gotchas

- Anything that imports `ovo` requires an initialized "OVO home" directory (`~/ovo` by default), which includes the configuration, the database, the storage directory, the scheduler workdir, etc. This includes local development. The home directory contains *real data* - never delete from it, and never delete from the database unless you are sure you are working inside a temporary ovo home!
- The Storage class abstracts away how files are stored - this is not always the local filesystem! Storage can also return paths that live on S3. Any manipulation of workflow-adjacent files should most likely use the Storage class, rather than the local filesystem.
- If `uv run` or `uv sync` is slow, this is likely because the current directory contains symlinks to large directories, due to how setuptools build works. Notify the developer about this in case that happens.
- The `ovo.common` submodule is also packaged as a separate `ovo-common` pip package. Do not import the rest of ovo or ovo dependencies inside that module. 
- Do not import `ovo.app` globally inside `ovo.core` - only local imports are allowed, to avoid importing streamlit when not used.
