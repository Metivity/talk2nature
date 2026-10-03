# Research atlas

The public [world atlas](https://metivity.github.io/talk2nature/research/atlas/) connects the literature library to approximate places and a source-year timeline. It is the first geographic layer, not a map of all published research or a live observation service.

## Current coverage

The October 3, 2026 release includes every one of the **33 research notes**: eight have cited geography, across seven display regions; 25 remain without a pin. Fifteen await location review, and ten cover tools, methods, benchmarks or a claim review without a single mapped site. All remain searchable. The source inventory contains 108 records, with 13 curated acquisition resources; the shared catalog has 154 records and 70 citation links.

| Display region | Literature represented | Observation time checked |
| --- | --- | --- |
| Wolfgangsee, Austria | Honeybee orientation experiment recounted in von Frisch’s Nobel lecture | 1949 trial; lecture published in 1973 |
| Karuizawa region, Japan | Japanese tit call-order experiments | Not established in this location review |
| Waters off Dominica | Sperm whale coda structure; observed birth | 2005–2018 recordings; birth on July 8, 2023 |
| Herzliya region, Israel | Capture origin of bats later observed in acoustic chambers | Not established; this is **animal origin**, not the recording location |
| Kenya, Samburu and Amboseli | Elephant individually directed calls | Not established in this location review |
| Northern Cape, South Africa | animal2vec / MeerKAT field recordings | August–September 2017 and July–August 2019 |
| Brazil, Cerrado and Atlantic Forest | AnuraSet frog recordings | 2019–2021 |

Locations are editorial regional/country locators, not exact samples, boundaries, densities or claims of comprehensive coverage. A count is the number of library notes; two notes may analyze related data. The bat-origin distinction is visible before opening advanced evidence details. Nearby buttons cluster on small screens to preserve 44-pixel hit targets; the Where filter also permits selecting a single region directly.

The historical addition is an original short summary of selected passages from the [1973 lecture](https://www.nobelprize.org/uploads/2018/06/frisch-lecture.pdf). PDF pages 9–10 were visually reviewed for the 1949 Wolfgangsee account. The referenced original experiments and subsequent literature have not all been reviewed. The downloaded PDF and review screenshots remain ignored local evidence, not website assets.

## Data and provenance

- `content/research.json`: each note may carry `atlas` metadata: review date, location status, explanation, locations with role/source/passage/basis, and a separately cited observation period.
- `content/atlas-places.json`: explicit public place registry. Precision is `region` or `country`; coordinates allow at most one decimal place. Do not infer a study site from an author affiliation. Public coordinates are editorial display choices, not quotations from papers.
- `talk2nature/atlas.py`: validates these assertions and projects the complete note inventory into an explicit public field allowlist. Missing geography stays missing, never `(0, 0)`. Unknown source IDs, inconsistent statuses, exact coordinates, unreviewed locations and unexpected location fields fail the build.
- `/research/atlas/catalog.json`: public `talk2nature.atlas.v1` projection. Each record retains the same `note:<slug>` key and immutable evidence-version ID as the existing evidence graph and private metadata catalog. Source-year ranges are sorted by their latest year; publication/documentation dates and observation dates are separate.
- `admin.catalog`: imports the complete public note payload, including these location assertions, into the existing versioned SQLite/PostgreSQL catalog. No backend schema change, upload endpoint, participant location field or admission change was made. Existing frozen study versions stay frozen.

The catalog is literature metadata, not raw observations or a training set. JavaScript filters public records already rendered as a complete static timeline. Search terms stay in page memory. There is no location permission, analytics, external tile service, account requirement, browser persistence or private API connection. The atlas is outside the app’s offline service-worker scope and is not advertised as an offline feature.

## Adding or correcting evidence

1. Add the primary source and an original short evidence note; state what was actually reviewed and retain scientific/reuse limitations.
2. Read the methods, data statement or original historical account for geography. Record the cited section/page and what the place describes: study region or animal origin. If the site cannot be established, leave it pending.
3. Choose a coarse regional/country display point. Never copy a household address, individual tracker trace or sensitive species location into public content. Coordinate rounding alone is not a privacy review.
4. Record observation dates only when the source supports them. Do not use the paper’s publication year as a substitute.
5. Run the checks below; inspect the note, citation and map behavior. Reimport public metadata when updating the private catalog. Changes create new evidence versions rather than rewriting frozen study evidence.

## Map asset rights

The land silhouette is derived from Natural Earth’s public-domain 1:110m land geometry, without political boundaries. Its [terms](https://www.naturalearthdata.com/about/terms-of-use/) and exact upstream commit, source URL, size and SHA-256 are recorded in `research/atlas-map-source.json`. The original remains in ignored `data/external/natural-earth/`; only the derived `web/assets/atlas-land.svg` is published. `python3 scripts/build_atlas_land.py` reproduces that SVG from the separately acquired, hash-verified source. It performs no network request. Scientific articles, audio and publisher figures are not redistributed.

## Next layer: participant observations

This release does not publish local app sessions or private synthetic records. Before adding a real observation layer, resolve the existing study-protocol, consent and hosted-storage gates. The next design should keep precise collection information private, link admitted observations to frozen study/evidence versions, and produce a separately reviewed public projection. Its release process must record contributor permission, location sensitivity/generalization decisions, reviewer status and withdrawal reconciliation. Open-map publication must be optional; absence of a public pin must never exclude a valid private observation. Do not open real-data admission just to populate a map.

## Validation

Required checks:

```sh
python3 -m unittest discover -s tests -v
node --test tests/*.test.mjs
python3 web/build.py
python3 scripts/check_site.py
python3 web/build.py --public --base-url https://metivity.github.io/talk2nature --repo-url https://github.com/Metivity/talk2nature
python3 scripts/check_site.py
```

New tests cover complete-note coverage, public field boundaries, source/location/date validation, stable catalog versions, observation/source-year distinctions, multi-filter intersection, multi-site counting and mobile cluster separation. The static build includes all notes and citations without JavaScript.

Browser acceptance covered 1440-, 390- and 320-pixel layouts; real pin and select/search/reset handlers; unmapped plant/fungi results; empty-state recovery; distinct 1949/1973 dates; keyboard disclosure and evidence-graph navigation; 44-pixel map controls; 16-pixel mobile inputs; no horizontal overflow; a blocked catalog request and JavaScript-disabled fallback. Temporary browser restrictions were restored. No physical-phone, microphone, participant or biological validation is implied. Publication receipts and final check counts are in `docs/STATUS.md`.
