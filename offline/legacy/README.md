# Legacy runtime

The legacy backend is supported by `offline/tools/patch_bootstrap.py`. Its flat
runtime contains 43 files in `offline/runtime/`; the legacy concatenation and bare
module imports use those file names directly.

- `offline_tutorials.py` is shared by the legacy runtime and the Project7 startup
  loader.
- The remaining legacy runtime modules and `local_gateway.py` stay in the flat
  directory so the legacy backend and host checks remain usable.
- `legacy-runtime-manifest.json` lists the files and the shared module.

The legacy implementation is retained as a supported comparison backend. It is
not part of the default `project7` build route.
