# Offline implementation

This tree contains the offline product and its legacy compatibility runtime.

- `current/`: current business/UI/resource/single-package implementation.
  - `java/`: Java modules; `com.project7.localmanager` package names are preserved.
  - `runtime/`: embedded Python2 UI/business modules; module names and compile
    identity are preserved.
  - `data/`: feature catalogs, policies, and contracts.
  - `tools/`: feature producers and checkers.
- `runtime/`: flat legacy runtime used by the legacy backend. It contains 43
  files. `offline_tutorials.py` is shared with the Project7 startup loader.
- `tools/`: build/export/package/resource and legacy tools.
- `legacy/`: legacy runtime manifest.

`--offline` does not force component acquisition offline. Use the dependency-ready
bundle or an explicit `--component-offline-input` for a fully offline build.
