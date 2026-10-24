# Validation — 23 October 2026

Tested with Python 3.12.13 and the pinned environment in requirements.txt. This folder was tested in a separate process, without imports from sibling projects.

- Numerical/data/replay checks: **4 passed** (`python -m pytest -q`).
- Streamlit interface check: **passed** (`python smoke_ui.py`), including chart presence, embedded replay presence and an adjustable control where applicable.
- Normalized observed data is bundled for offline operation; public refresh adapters were exercised. OpenF1 race and qualifying downloads succeeded, as did paginated Jolpica standings/results. FastF1 upstream timing returned HTTP 401; telemetry was not downloaded.
- The reference-inspired shared interface was visually inspected in the local browser. Playback completion, reset and reduced-motion behavior were verified on the shared replay component. No motion autoplays; simulation/estimate labels remain visible.

The full suite contains 37 automated checks across seven independently runnable folders, plus seven interface smoke runs. The shared ingestion/replay invariants intentionally repeat in standalone folders so each future repository has its own checks. A dependency emits a pandas/NumPy timedelta deprecation warning; the pinned tested environment passes. It is not suppressed.

## Data integrity

The observed 2024 race table has 1,059 records; 816 pass the explicitly documented OpenF1 eligibility heuristic. Qualifying has 282 records; 85 pass. Completed-lap maxima match Jolpica for all 20 race drivers. Hamilton's feed includes an incomplete attempted lap 2 after one completed lap; it has no lap duration, is ineligible, and is not counted as a completed lap. “IsAccurate” is never fabricated for OpenF1 data.

The championship regression snapshot remains fixed after round 17, separate from the refreshable working snapshot. It records 23 drivers, 22 latest-race entrants, six remaining GPs and no remaining Sprints. Real Austin clinch tests exercise the Russell ninth/eighth boundary, Hamilton fifth/fourth boundary, maximum remaining points and countback rather than treating an Austin win as sufficient.

## Model limits

Read README.md and CONTEXT.md before interpreting outputs. The pit models are small full-distance dry-race simulations. The tire fit is conditional on fuel assumptions. The ideal lap is a theoretical sector sum, not a drivable telemetry trace. The SC sample has only three observed years and cannot establish empirical calibration.

The strategist's frozen experiment selected an update on validation. Held-out gain is **0.105 s/race**, with paired 95% interval **−0.189 to 0.399 s**. That is inconclusive. No tuning was performed to turn that test result into a success claim. It is synthetic offline evaluation, not real-world learning or a live team strategist.

## Branding and motion

Both supplied reference images were inspected. Black/silver/turquoise dominate, with a gray left panel, white outside margin, asymmetric lower corners, compact legend and restrained Microsoft accent colors. Segoe UI is preferred if available, with Arial/sans-serif fallback; the screenshot's exact font was not identified. No tire allocation or activation-zone facts were copied from the references. The second circuit is used for style only.

No API keys are required for the included public historical-data workflows or the local strategist. A provider access failure is reported explicitly; no fake data is substituted.
