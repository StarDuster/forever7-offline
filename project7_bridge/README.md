# Project7 bridge / patch / compatibility layer

This tree contains project-written adapters around the fixed Project7 backend:

- `runtime/`: DEX/seam patch payloads, manager RPC projection, BSON/script
  compatibility data, official-baseline reconstruction, and protocol adapters.
- `android/`: startup/repair injection hosts for the fixed component.
- `tools/`: DEX/script patchers, component fetch/materialization, compile, and
  assembly adapters.

Current offline features are under `offline/current/`; Java package names and
embedded Python2 module identities are unchanged. `runtime/project7_startup_hook.py`
is the startup hook path consumed by the bridge.
