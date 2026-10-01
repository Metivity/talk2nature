# Website reliability and open-source audit

October 1, 2026. Scope: Talk2Nature public website and local audio tools; repository contribution foundations and primary-source connection research. No private-backend changes, new service purchases or partner messages.

## Reproduced findings and fixes

| Finding | Evidence | Change |
|---|---|---|
| Listen begins too far down on a phone | On the live release at 390 × 844, file input top was about 1,127 CSS pixels and example top 1,159 | Shortened intro; put example/file controls first; moved format detail into a disclosure |
| Unfinished observations can be lost | Entered synthetic notes, replaced the example; notes disappeared without a warning | Track unfinished drafts, guard replacement/edit/discard, and block exports that would omit them |
| Download request mistaken for successful saving | JSON export reset the dirty flag immediately in the old handler | Retain session-loss warning after requesting download; show adjacent feedback asking users to check downloads |
| New HTML can run with old assets | Preview browser loaded new HTML with old CSS/JS: old computed sizes and absent new load focus | Content-derived revision in HTML asset URLs, module/worklet imports and CSS dependencies; offline cache accepts exact revision URLs |
| Working tools hard to discover | Main navigation linked the planned Field Notes product and an installation landing page | Tools and videos in main navigation; Open app links directly to usable app; funding and planned workspace remain in footer |
| Mobile navigation depends on JavaScript | CSS hid navigation by default below 800 pixels | Collapse only after the menu script initializes; static links remain if scripts fail or are disabled |
| Open-source contribution foundations incomplete | No governance, conduct or security-report files; checks only in publishing workflows | Added those documents, a website-bug template, public PR/push checks, and a public community/network guide |

Asset revisioning does not force a service-worker update while an app window is open. Export and close existing app windows before reopening a waiting update. Query-bearing assets from another revision are not served from the current shell cache. No runtime response, recording or private route is added to offline storage.

## Verification

The regression suite executes the real Listen event handlers against a minimal DOM facade to test draft preservation, canceled replacement, blocked partial exports, alias-error focus and continued warnings after a requested download. Asset tests cover stable revisions, changed dependencies and missing-module failure; service-worker tests cover exact version matching and query isolation. Browser checks and deployment results are recorded below after execution.

## Limits and next work

A synthetic browser audit is not a first-time user study or physical-phone certification. M4A/MP3 support and direct Station-session-to-Listen interchange remain absent. Real microphone, iPhone/Android installation and interruption/endurance tests remain outstanding. Native unattended recording and hosted private research intake remain unreleased.

The open-source recommendations and dated connection routes are in [OPEN_SCIENCE_AND_CONNECTIONS.md](OPEN_SCIENCE_AND_CONNECTIONS.md). No institutional partnership or DPG recognition is claimed.


### Local acceptance receipt

34 Python tests and 40 Node tests pass (74 total). The local noindex build checks 44 HTML pages and 1,296 local links. At 390 × 844, the revised Listen file control begins at 390 pixels and example at 446, versus 1,127 and 1,159 before. The loaded recording heading receives focus. Draft export is blocked visibly with the draft intact; adding it then exporting produced an actual one-event JSON, successfully reopened in the offline app and checked with the Python annotation report.

The browser harness could not reliably expose the native confirmation dialog: its key call timed out and later returned no active dialog. Canceled replacement/discard preservation is therefore covered by the handler regression tests, not claimed as a successfully canceled native-browser prompt. Its download event hook also timed out; actual Downloads files were found, inspected and reused instead.

A fresh local app origin completed offline setup. With the network disabled, app navigation and Review loaded the versioned assets and reopened the labels. The synthetic Station worklet also ran offline and exported two retained WAVs in a ZIP; both checksums and archive CRCs matched. No microphone or speaker playback was used. Network emulation was restored afterward.

Mobile menu expansion and Escape close worked. With scripts disabled, all six navigation links remained visible and there was no horizontal overflow at 390 pixels; scripts were restored. The community page fit at 390 and 1,280 pixels. No physical-device or independent user-study claim is made. Public deployment verification follows in STATUS.md.

### Publication receipt


Released from `7da32b56b8c1722a076869b242bede1bbae3281e` through successful manual Pages run https://github.com/Metivity/talk2nature/actions/runs/36887134638. The new public-checks workflow also passed: https://github.com/Metivity/talk2nature/actions/runs/36887133330. Public build checked 44 HTML pages and 1,341 link references; all 76 deployed files matched the tested build, including revision-bearing asset requests, using normal TLS verification. Live Listen had its first control at y390 on a 390 × 844 viewport, loaded the synthetic example with focus on the recording heading and no autoplay, then cleared cleanly. The community page and its five network entries were inspected live. Proof: ignored `tmp/site-audit/live-files.json`, `tmp/site-audit/offline-export.json` and `tmp/site-preview/site-reliability-live.png`.

Temporary local tabs and preview servers were closed; network, script-execution and viewport overrides were restored. The updated live Listen page remains as the deliverable. The optional test offline shell contains public files only and may remain in local browser storage; no audio was persisted by it. Current deployed revision is `7da32b5`; the following documentation receipt does not redeploy. This audit fixes the reproduced public-site issues. Physical devices, independent first-time users, specialist scientific review and private hosting remain separate open work.
