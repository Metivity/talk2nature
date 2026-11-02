# Independent annotations in the university walkthrough

## Research basis

Dubus et al. studied detection of two blue-whale vocalization types in a citizen-science annotation campaign. Nineteen novice annotators received task-specific training and annotated independently; the workflow retained annotator, source and timing provenance. Separate expert-annotated recordings were used for evaluation. The article treats expert labels as pseudo-ground truth. Its results concern these call-detection tasks, not behavior or meaning, and its reported annotator counts are not universal thresholds.

Source: Dubus et al. (2024), [DOI 10.1016/j.ecoinf.2024.102642](https://doi.org/10.1016/j.ecoinf.2024.102642). Talk2Nature's [review note](https://metivity.github.io/talk2nature/research/blue-whale-multi-annotator-labels-2024/) records the reviewed scope, limits and component rights.

## Applied design

The university page uses three invented cards to illustrate a possible record shape:

- Preserve each annotator's label and uncertainty as a separate record.
- Hide other reviewers' labels during independent annotation.
- Keep disagreement visible; do not silently convert it to a majority label.
- If an adjudication or aggregate is later used, record its author/rule and retain links to the original labels.

The cards contain no audio, biological observations, predictions, contributor accounts or study records. They teach a workflow boundary; they are not a running annotation system or a validated schema. No real-data intake or cloud storage was added.

## Review gate

The cards collapse to one column at viewports below 700 CSS pixels. Before a multi-annotator feature is designed, a named research group must provide a concrete task and codebook; then the project needs independent scientific and data-governance review, a rights-cleared synthetic or permitted fixture, and an explicit decision about identity, privacy, retention and withdrawal. No such review or field protocol has been completed.
