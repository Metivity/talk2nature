# Make first-use reports reproducible

The existing public first-use task is issue [115](https://github.com/Metivity/talk2nature/issues/115). It should cover the released sequence of invented practice, stop, review note, save and reopening. The observed-use protocol in [FIRST_USE_WALKTHROUGH.md](../FIRST_USE_WALKTHROUGH.md) remains a separate formative study requiring voluntary participation. Public issue replies remain self-reports.

App feedback links now include the public asset-build token. The local report records it as the build referenced by that link, separately from the feedback page's own build. A cached app can differ from the current feedback page. Missing or malformed values are labeled as not supplied, and unrelated URL fields are omitted. This metadata identifies software versions; it provides no participant or recording identity and does not prove which operations were completed.

The feedback form offers specific saved-and-reopened and saved-but-could-not-reopen outcomes while retaining the existing general choices. It still prepares a local draft for deliberate copying or opening in the user's mail client. The GitHub issue form also offers the save-and-reopen task. The README now accurately describes End rehearsal opening review.

Verification covered the app-home-to-feedback link, both build fields, saved/reopened outcome, optional missing device details and the prepared email body. Browser emulation measured a 390px document matching the viewport. No message was sent. Node tests check version separation, rejection of arbitrary query text, and the absence of network or storage access. Python checks verify generated feedback links across app pages.

No physical phone was attached in the inspected device inventory. Independent completion and named-phone acceptance remain open. The next evidence should be a report from a willing outside user or an authorized observed-use session, rather than another maintainer rehearsal.
