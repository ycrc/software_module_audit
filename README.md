# Software Module Audit

## Running

First, get a tsv with module names and load counts as the first two columns, store in FY directory for that year. Files for each cluster should start with cluster name. Then run

``` bash
# e.g. FY21
./mod_audit.py FY21/*.tsv
```

This will create three files for each cluster.

| Filename               | Function                                               | Notes                                                      |
|------------------------|--------------------------------------------------------|------------------------------------------------------------|
| `_admin.list`          | Sets module load messages notifying of deprecation     | Append to `apps/modules/admin.list`                        |
| `_modulerc.lua`        | Hides deprecated/unused modules from `module avail`    | Append to `apps/modulerc.lua`                              |
| `_popular_modules.txt` | List of newly deprecated modules that are often loaded | Consider updating/installing these in supported toolchains |
