#!/usr/bin/env python
from __future__ import print_function
import sys


twentyeighteena = ["2018a", "GCCcore-6", "GCC-6"]

# keep these around
univ_curr_toolchains = ["2018b", "2020b", "GCCcore-7", "GCC-7"]

# deprecate these
univ_depr_toolchains = [
    "foss-2016b",
    "foss/2016b",
    "gompi/2016b",
    "gompi-2016b",
    "intel/2016b",
    "intel-2016b",
    "iimpi/2016b",
    "iimpi-2016b",
    "2016.3.210", #iccifort
    "foss-2017",
    "foss/2017",
    "GCC-4",
    "GCCcore-4",
    "GCC-5",
    "GCCcore-5",
    "gcccuda-2016",
    "gcccuda-2017",
    "intel-2017",
    "intel/2017",
    "iompi-2017",
    "iompi/2017",
    "iomkl-2017",
    "iomkl/2017",
    "iimpi-2017",
    "iimpi/2017",
]

# these should already be gone
# I say we just delete/move the Singularity modules
prev_depr_toolchains = ["foss-2016a", "foss/2016a", "Singularity"]

# what to say about this round of deprecation
depr_str = "{}: This module is being deprecated and will be removed from the module list in May 2021. If you need an updated or rebuilt version, please search for a newer version with module avail or email us at hpc@yale.edu with any questions you have.\n"

# modules with loads under load_thresh get hidden
load_thresh = 10
# except if they match unused_exceptions
unused_exceptions = [
    "Autoconf/",
    "Automake/",
    "Autotools/",
    "CUDA/",
    "cuDNN/",
    "dSQ/",
    "EasyBuild/",
    "GCCcore/",
    "GCC/",
    "MATLAB/",
    "ycga-public/",
    "mpifileutils/",
    "TotalView/",
]

build_deps = [
    "Bison/",
    "binutils/",
    "M4/",
    "zlib/",
    "libtool/",
    "bzip2/",
    "ncurses/",
    "pkg-config/",
    "flex/",
    "gettext/",
    "help2man/",
    "CMake/",
]

# deprecated modules with loads over lots_of_loads get added to pre_builds and saved to popular_modules.txt
lots_of_loads = 300

in_tsvs = sys.argv[1:]
for in_tsv in in_tsvs:
    prefix, _ = in_tsv.split("_", 1)

    if prefix in ["Grace", "Milgram"]:
        curr_toolchains = univ_curr_toolchains+twentyeighteena
        depr_toolchains = univ_depr_toolchains
    else:
        curr_toolchains = univ_curr_toolchains
        depr_toolchains = univ_depr_toolchains+twentyeighteena

    prev_depr_mods = []
    depr_unused_mods = []
    other_unused_mods = []
    recent_unused_mods = []
    build_deps_mods = []
    pre_builds = set()

    with open(in_tsv, "r") as module_tsv, open(
        "{}_admin.list".format(prefix), "w"
    ) as admin_list, open("{}_modulerc.lua".format(prefix), "w") as mod_rc:
        header = module_tsv.readline()
        for modinfo in module_tsv:
            mod_str, loads, rest = modinfo.split("\t", 2)
            loads = int(loads)

            # hide previously deprecated
            if any(toolchain in mod_str for toolchain in prev_depr_toolchains):
                prev_depr_mods.append(mod_str)  

            # deprecate with load message
            elif any(toolchain in mod_str for toolchain in depr_toolchains):
                if loads > lots_of_loads:
                    pre_builds.add("{}, {}".format(mod_str,loads))
                if loads < load_thresh and not any(
                    excepted in mod_str for excepted in unused_exceptions
                ):
                    depr_unused_mods.append(mod_str)
                print(depr_str.format(mod_str), file=admin_list)

            # hide recent but unused
            elif any(toolchain in mod_str for toolchain in curr_toolchains):
                if loads < load_thresh and not any(
                    excepted in mod_str for excepted in unused_exceptions
                ):
                    if any(excepted in mod_str for excepted in build_deps):
                        build_deps_mods.append(mod_str)
                    else:
                        recent_unused_mods.append(mod_str)                    

            # hide modules no one uses :-(
            elif loads < load_thresh and not any(
                excepted in mod_str for excepted in unused_exceptions
            ):
                if any(excepted in mod_str for excepted in build_deps):
                    build_deps_mods.append(mod_str)
                else:
                    other_unused_mods.append(mod_str) 

        for mod_str in prev_depr_mods:
            print('hide_version("{}") -- past_deprecated'.format(mod_str), file=mod_rc)

        for mod_str in depr_unused_mods:
            print('hide_version("{}") -- deprecating_and_unused'.format(mod_str), file=mod_rc)

        for mod_str in other_unused_mods:
            print('hide_version("{}") -- system_unused'.format(mod_str), file=mod_rc)

        for mod_str in recent_unused_mods:
            print(
                'hide_version("{}") -- current_unused'.format(mod_str),
                file=mod_rc,
            )

        for mod_str in build_deps_mods:
            print('hide_version("{}") -- build_dependency'.format(mod_str), file=mod_rc)

    with open("{}_popular_modules.txt".format(prefix), "w") as pop_mods:
        print(
            "Consider pre-building the modules in {} for new toolchain.".format(
                pop_mods.name
            )
        )
        for mod in sorted(pre_builds):
            print(mod, file=pop_mods)
