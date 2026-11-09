# Maintainer-only regeneration

The production build consumes only the fixed `seams.xor-zlib`, `contract.json`
and `tools/project7_manager_rpc_projection_patch.py`. The generator is not a
normal build dependency.

Maintainer inputs (external, not checked into Git):

- v9 base manager DEX: `analysis/project7/v9-manager-target-7ea1.dex`
  (`7ea1e95f...`)
- disassembled v9 manager tree: `analysis/project7/v9-manager-smali`
- pinned toolchains: JDK17, Android build-tools 37.0.0, dex2jar v2.4
- isolated generator/verifier:
  `analysis/project7/manager-rpc-projection-fix-v1/generator/build.py` and `verify.py`

Run only in a maintainer workspace with those inputs:

```bash
python3 analysis/project7/manager-rpc-projection-fix-v1/generator/build.py
python3 analysis/project7/manager-rpc-projection-fix-v1/verify.py
```

The patched source is `LocalGatewayServer.smali`; its size and SHA-256 are pinned
in `contract.json.source_class`. The apply tool rejects a source smali/contract
drift before restoring the delta. Do not add the base DEX or full base smali tree
to Git/source export.
