# COTA tire degradation model

**Build question:** How much within-stint pace loss remains after a chosen fuel correction, and how sensitive is that estimate?

An independently runnable Python + Streamlit + Plotly project. This standalone repository imports no sibling project. Interactive controls, hoverable charts and downloadable results are included. The supplied reference styling uses black, silver, gray and turquoise with a Segoe UI-style font stack and restrained Microsoft color accents. Each app includes a pauseable replay of its own computed data.

## Run

Use Python 3.12. From this folder:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows, activate with `.venv\Scripts\activate` instead. `requirements.txt` pins the tested full environment; `requirements.in` lists direct dependencies. A first install needs internet. The delivered normalized observations run offline afterward.

## Build with me

1. Start with the question above and run the app's default case.
2. Read the small numerical model (`model.py`) separately from the interface (`app.py`).
3. Inspect the data source and quality notes, then change one assumption at a time.
4. Select a long Leclerc stint and vary fuel gain from 0.02 to 0.08 seconds/lap. Inspect residuals and tail MAE. Explain why the wear slope changes almost one-for-one with fuel gain.
5. Run `python -m pytest -q` after changing numerical logic. Tests use analytic cases or labeled synthetic fixtures, not fabricated observed data.

## Model and interpretation

`model.py` fits one driver's one compound stint using ordinary least squares: corrected time = intercept + wear × (tire age − 1). Corrected time adds fuel_gain × (race lap − 1) to remove the assumed benefit of fuel burn. Tire age and race lap are collinear within a stint, so estimating both slopes from that stint would be unidentifiable. We expose the fuel assumption instead.

The 95% t interval is conditional on that assumption and independent residual errors. It can be too narrow with serially correlated laps. A chronological tail holdout re-fits on earlier observations and reports MAE. This is predictive validation, not causal identification. No cross-era pooling, automatic tire-life limit, or 2026 transfer claim. Negative slopes are retained and interpreted as a warning about confounding.

## Data and refresh

```sh
python fetch_openf1.py --year 2024 --session R
```

For supported lap projects, `python fetch_data.py --year 2024 --session R` uses FastF1; for qualifying use `--session Q`. Optional `--telemetry` downloads actual telemetry if upstream access permits it. During this build the FastF1 timing endpoint returned HTTP 401, so OpenF1 was explicitly used for historical lap/sector/stint observations. Jolpica provided the championship data. A failed fetch raises an error rather than silently generating demo results.

Local CSV lap times and sector times are seconds; tire age is one-based in source tables; model stint age is zero-based. Project metadata JSON files record retrieval time, source and filtering. OpenF1 `Eligible` is a derived quality heuristic, not a native FastF1 flag. Read [CONTEXT.md](CONTEXT.md) for verified COTA changes, tire eras, 2026 rules, primary-source links and data limits.

## Files and verification

- `app.py`, `ui.py`, `.streamlit/config.toml`: controls, chart rendering and adaptable style.
- `model.py` and `test_model.py`: numerical logic and meaningful invariants.
- `data/`: observed normalized tables and provenance; never mislabeled simulations.
- Fetch scripts: explicit provider adapters, no required credentials for the delivered public sources.
- `smoke_ui.py`: offline interface checks. Run `python smoke_ui.py` after the numerical tests. GitHub Actions workflows are not included.

Validation details are in [VALIDATION.md](VALIDATION.md). Downloaded data remains subject to provider terms. No code license has been assigned; publication does not grant a license to reuse the code or third-party data.

## Animation and API keys

The embedded replay starts paused and uses the app's computed arrays. Play/Pause, Reset, speed and a keyboard-accessible timeline are available. Reduced motion defaults to the operating-system preference and can be enabled manually; manual stepping remains available. Motion is labeled as observed-sector, fitted, estimated or simulated playback and is never presented as live telemetry. `motion.py` validates lengths and finite numbers; `motion.html` renders without external libraries or network access.

No API keys are needed for the public historical Jolpica/OpenF1 data or the local strategist. A provider authorization error is a data-access issue, not a requirement to invent an API key. FastF1 telemetry access remains dependent on its upstream service.

## Current grid and historical laps

The default driver selector includes the latest completed Grand Prix roster from a dated Jolpica snapshot. Kimi Antonelli is selectable even when he has no laps in the bundled 2024 Austin race. A driver without a sufficiently long clean stint gets an explicit no-data message and no fitted chart. This is not a claim about availability at other events.

Use **Refresh current grid** (internet required), or run `python roster.py`, to update the roster. Failed refreshes preserve the saved snapshot. The latest-race roster may lag substitutions; its race and retrieval date are displayed. **Historical session** lists drivers present in the bundled laps. Updating the roster never changes the lap dataset, infers 2026 tire behavior, or substitutes another driver's measurements.
