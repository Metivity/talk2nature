# Field Companion first-use walkthrough

**Status:** internal protocol draft. No testers have been recruited or tested with this document. It is not an ethics approval or authorization to contact people.

## Purpose

Check whether a first-time visitor can find and complete the microphone-free practice, save it, reopen it in Compare, and understand that the session is invented practice material rather than an animal observation. This is formative software usability work, not animal research and not evidence of biological communication.

## Boundaries and consent

- Use the same frozen site revision for every participant; record its commit or build identifier, route, date and device/browser family.
- Obtain voluntary consent to observe the task and keep minimal anonymous notes. Explain that the person may stop at any time and that no names, contact details, screen recordings, voice recordings, microphone access, real animal audio, photos or location data will be collected.
- If the browser requests microphone permission, ask the participant to cancel it and record the request as a failure of the microphone-free path. Do not continue into real recording.
- Do not ask participants to observe or record animals. Do not use their own audio, account or device files.
- Record only a participant code, device/browser family, task completion, whether help was needed, approximate elapsed time and brief neutral notes about confusion or errors. Keep raw notes in a private, access-limited working file; delete them within 30 days after summarizing. The repository may retain aggregate outcomes and resulting product decisions, not identifiable notes or quotations.
- If the results will be used as publishable human-subject research, pause and seek the relevant institutional ethics review before recruitment.

## Walkthrough

Start each session on `/app/` in a clean browser profile. After consent, read this prompt once, then observe without coaching:

> Please find a way to try the Field Companion without recording, add one observation note, finish the practice, save it, and reopen it. Then tell me what the saved session represents and where you think it went.

Do not name the button labels, describe the file format, or tell the participant where to tap. If they ask for help, ask what they would try next; count that as assistance. Stop immediately if a permission prompt, real recording, animal file or personal data appears.

Observe whether they can:

1. Find and start microphone-free practice without granting permission.
2. Add one human-entered note and finish the session.
3. Save the practice and determine what the app asks next. If it asks the person to confirm the download, let them check the ordinary download location without hints; observe whether they find the visible Compare step and reopen the same file with the normal picker, without JSON editing or archive extraction.
4. Explain that the example is invented practice material, not a recording or interpretation of an animal.
5. Understand whether anything was uploaded or played automatically, based on the interface wording.

Record completion, approximate time, assistance, first hesitation, whether the person confirms finding the download, and any mismatch between what the interface says and what the participant believes. Do not record a participant's name, audio, screen or verbatim comments.

## Acceptance and reporting

The formative target is at least 4 of 5 participants completing the save-and-reopen path without coaching, and at least 4 of 5 correctly identifying the session as invented practice with no microphone capture. Any participant who believes the session contains real animal data is a copy/flow failure to investigate. These small counts are product signals, not a statistical usability study or validation of science claims.

Report the tested revision, device/browser mix, counts, observed failure points, assistance and changes. Keep the result labeled as formative and do not claim broader usability from five people. Actual microphone capture, interruption behavior and hardware performance require a separate controlled device check and remain outside this walkthrough.
