# Fixed upstream Project7 dependency and official resources

This directory contains pin/provenance metadata for the fixed Project7 component
and the official NetEase game 640 resource manifest. The component ZIP is an
external dependency, not source in this repository.

- Component: 57,258,978 bytes, SHA-256
  `ccbde188251c68eb23a4af1d0b6aef1946236d527d2a70f30058277e5a7b7a0d`
- Descriptor: `component.json`
- Official NetEase game 640 resource manifest:
  `provenance/patch2.android.640.version`. This is the original game resource
  manifest published by NetEase, used for official640 reconstruction and by the
  legacy `prepare_scripts` path. It is not Project7 component provenance.
- Ordinary builds consume the official original APK plus this fixed component.
- The original Project7 game/manager APK is needed only when generating or
  updating the fixed component; builds consume its compiled component.

The manifest is classified as official game 640 provenance; the fixed Project7
component pin is classified separately. No project-written `project7_*` /
`Project7_*` implementation is classified here.
