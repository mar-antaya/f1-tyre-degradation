# COTA context and source ledger

Verified 23 October 2026. These projects are educational, unofficial, and independent of F1 teams.

## Circuit and changes

COTA's Grand Prix layout is 5.513 km, 20 turns and 56 race laps, with its first F1 race in 2012. Its rapid esses, slow corners and long straight demand different tire/energy compromises. [FIA 2022 US GP preview](https://www.fia.com/sites/default/files/2022_us_gp_preview.pdf) and [F1 circuit page](https://www.formula1.com/en/racing/2026/united-states).

Do not assume a single “2019 resurfacing” explains later lap times. [Pirelli's 2021 preview](https://press.pirelli.com/2021-united-states-grand-prix---preview/) documents resurfacing since the previous 2019 visit at the start/finish–T1, T9–10, T11–12 and T15–19 sections. It does not establish a precise 2019 work date. The FIA 2022 preview documents further resurfacing that year. [F1's 2024 tire preview](https://www.formula1.com/en/latest/article/what-tyres-will-the-teams-and-drivers-have-for-the-2024-united-states-grand.8QfDCtgqiePxAvvNol577) reports a broad resurfacing program begun two years earlier, with C2/C3/C4 nominated in 2024. These changes motivate separate season analyses, not an invented numerical grip multiplier.

## Tire and regulation eras

[Pirelli's 2022 announcement](https://press.pirelli.com/a-look-into-the-future-of-formula-1-with-new-18-inch-tyres-for-2022-cars/) establishes the switch from 13-inch to 18-inch wheels. [F1's 2026 terminology update](https://corp.formula1.com/f1-2026-regulations-terminology-update/) confirms 18-inch rims remain but tread widths shrink 25 mm front / 30 mm rear, alongside major chassis, power-unit and active-aero changes. Consequently, a 2024 fitted wear coefficient is not a measured 2026 coefficient. Compound names are relative event labels, not stable cross-year materials. No unverified 2026 COTA compound nomination is embedded.

The models assume full-distance dry races and fresh sets, with at least two dry specifications and a medium/hard mandatory-race-specification assumption. [FIA Section B, Issue 09, 1 October 2026, B6.3.6](https://api.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_b_sporting_-_iss_09_-_2026-10-01.pdf) governs the dry-compound requirement, with wet-weather and suspension exceptions. Inventory, actual event mandates, exceptional race rules and 2026 energy deployment are outside these small models.

## Championship rules and current facts

[FIA Section A, Issue 03, A2.1–A2.2](https://api.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_a_general_provisions_-_iss_03_-_2026-06-25.pdf) specifies points and race-result countbacks, followed by qualifying results if race countbacks fail. Our full-points race scale is 25/18/15/12/10/8/6/4/2/1; Sprint 8 through 1; no fastest-lap bonus. Unresolved race countbacks are explicitly unresolved; qualifying countbacks are not simulated.

On 23 October, [official standings](https://www.formula1.com/en/results/2026/drivers) and Jolpica agreed on Antonelli 340, Russell 238, Hamilton 229, Verstappen 221, Leclerc 215 and Norris 201. [The current calendar](https://www.formula1.com/en/racing/2026) has six GPs remaining: Austin, Mexico, São Paulo, Las Vegas, Qatar, Abu Dhabi. [FIA's Sprint calendar](https://api.fia.com/news/fia-and-formula-1-announce-2026-sprint-calendar) has no remaining Sprint after Singapore. Hence 150 points remain before Austin and 125 afterward. These are dated facts; refresh and cross-check before reuse. Event dates in APIs use UTC, which may be the following local day (Las Vegas).

## Data sources and provenance

- [Jolpica API documentation](https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md): standings, calendar and paginated race results. API pages are capped; the fetcher follows offsets.
- [FastF1 API/source](https://github.com/theOehrly/Fast-F1): supported adapter uses `get_session`, `load`, lap/sector fields and optional telemetry. Its upstream historical timing server returned HTTP 401 during this build. No authentication bypass or fabricated fallback is used.
- [OpenF1 public historical API](https://openf1.org/docs/): the available alternate provider for 2024 laps/sectors/stints and 2023–2025 race-control messages. Its historical coverage starts in 2023. This is observed public timing, not synthetic data and not official classification.

Each `data/cota_*.json` records provider, session key, retrieval date and quality method. OpenF1 eligibility is a local conservative heuristic (sector consistency, non-pit, deletion messages, neutral/yellow intervals and blue flags), **not FastF1's IsAccurate flag**. Missing fields and unknown events are not imputed as valid laps or zero incidents. Timing can still have provider errors, unmatched deletion messages, traffic and weather confounding. No telemetry is fabricated. Any simulated scenario is labeled separately.

Downloaded third-party data retains its providers' rights and terms; the local analysis files do not grant redistribution rights. No data, code or apps have been published. The supplied reference images inform layout and colors only; their tire allocations and activation-zone annotations are not treated as verified 2026 sporting facts. The second circuit image is a style reference, not COTA geometry.
