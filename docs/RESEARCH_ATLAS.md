# Research atlas

The public [world atlas](https://metivity.github.io/talk2nature/research/atlas/) connects the literature library to approximate places and a source-year timeline. It is the first geographic layer, not a map of all published research or a live observation service.

## Current coverage — October 4, 2026

The atlas now includes **35 notes**, **14 with mapped locations**, across **14 approximate regions**. Twenty-one notes remain without a pin: eleven awaiting location verification and ten without a single applicable site. The complete catalog contains 111 source records, 35 notes and 13 acquisition resources (159 records / 73 citation links).

New locations are the Bahamas, Tepic and Puebla (Mexico), Barcelona (Spain), Tel Aviv (Israel), Lizard Island (Australia), and Niassa (Mozambique). Four existing notes gained supported geography; two new notes cover reef-fish recruitment and honeyguide–human cooperation. The dog study has two locations but remains one research note. Region and note counts measure editorial coverage, not independent evidence or animal abundance.

The [next-goals page](https://metivity.github.io/talk2nature/research/atlas/goals/) tracks 20 mapped notes (currently 14), three historical source notes (currently one), a scientifically reviewed passive parrot pilot, and a protected first observation release. The last two are future milestones with explicit dependencies. See [ATLAS_NEXT_GOALS.md](ATLAS_NEXT_GOALS.md).

| New geography | Basis actually reviewed | Date handling |
| --- | --- | --- |
| Bahamas | Research-team DolphinGemma announcement, field-program paragraph | Program start is mentioned; no complete recording interval inferred |
| Tepic and Puebla, Mexico | Dog-bark paper, section 3 Dataset, printed page 16481 | Recording dates remain unknown |
| Barcelona, Spain | Monk-parakeet paper, Methods 2.1–2.2, via open full-text mirror | Separate recording windows in October–November 2020 and 2021 |
| Tel Aviv, Israel | Plant-sounds paper, STAR Methods recording protocol; PDF page 12 / e2 visually checked | Recording dates remain unknown; ultrasound hardware limits retained |
| Lizard Island, Australia | Reef-fish paper, selected results/discussion and Methods study-site/control passages | Study October–December 2017; paper 2019 |
| Niassa Reserve, Mozambique | Primary Science abstract plus indexed institutional research-team account naming Niassa | Observation dates and full paper methods remain unreviewed |

Selected-passage review is not full scientific validation. The remaining cat, budgerigar, parrot-video, owner-survey, pig, moth and fungal geography was not inferred from author affiliations or approval bodies. Available cat methods and the previously saved parrot-video text were inspected but did not establish a clear collection geography for this pass. Some full-text retrievals failed; no access restrictions were bypassed. The honeyguide entry explicitly identifies the university account as its location source and the primary abstract as its scientific source.

Public `sources` in the atlas export may now include a checked `review_url` so location citations can link directly to the full-text version actually inspected. Original source URLs remain available. Downloaded article text/PDFs and rendered review images remain ignored, and no new animal recordings or model weights were acquired.

## October 3 baseline

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


## October 4 continuation: two coverage targets reached

The public collection now has **41 notes, 20 mapped notes, 20 approximate regions, 21 notes without pins and 119 sources**. Thirteen collection resources remain unchanged. The public/private metadata catalog has 173 records with 81 citation links. No article files, audio, videos or model weights are distributed.

| Added note | Location evidence actually reviewed | Date boundary |
| --- | --- | --- |
| Vervet development (1980) | Publisher abstract and German summary identify Amboseli, Kenya | Fourteen months reported without verified calendar dates; no date interval entered |
| Humpback song change (1985) | Indexed primary abstract locates recordings near Bermuda | April–May of 13 sampled years within 1957–1975; not continuous coverage |
| Raven gestures (2011) | Primary abstract places observations in the Northern Alps, Austria | Three field seasons without verified calendar years |
| Wolf howling (2013) | Main results name the Wolf Science Center, Austria; selected text reviewed via Europe PMC XML | Country locator; no exact enclosure or observation date inferred |
| Grouper–moray coordination (2006) | Methods name Mersa Bareika, Ras Mohammed National Park, Egypt | September 2002–December 2004 explicitly reported |
| Dolphin addressing (2013) | Indexed primary methods passage identifies eastern Scottish waters including Moray Firth | No calendar interval entered because complete methods were not obtained |

Original historical study years remain visible separately from observation periods and later reassessment citations. Fischer (2020) supplies a caution about production versus comprehension; Herman (2017) supplies a later review of disputed song functions. Review depth is stated per note: neither older paper is claimed to have received a complete methods review.

Access limits: the 1971 humpback PDF led to an institutional login, so it was not used as a full-text source. Several publisher opens failed. Primary indexed passages were retained only with explicit attribution and limited review labels. The wolf XML mirror was retrieved successfully; the dolphin XML mirror returned HTTP 500, so no complete-method review is claimed. Python's local TLS trust store failed on one retrieval; verified-TLS curl was used successfully for the wolf mirror, with no certificate checks disabled. No paywall or browser challenge was bypassed.

The goal board computes 20/20 and 3/3. It explicitly directs subsequent work toward methods depth and unresolved records; these counts do not close scientific-review, consent, hosting or physical-device requirements.
