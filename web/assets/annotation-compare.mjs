import {validateDocument} from './listen-model.mjs';

export const MAX_ANNOTATION_BYTES = 2 * 1024 * 1024;
export const MAX_OVERLAP_PAIRS = 10000;

export function parseAnnotationText(text) {
  if (typeof text !== 'string' || new TextEncoder().encode(text).byteLength > MAX_ANNOTATION_BYTES) {
    throw Error('Choose an annotation file smaller than 2 MB.');
  }
  let document;
  try { document = JSON.parse(text); }
  catch { throw Error('This file is not valid JSON. Open a Talk2Nature annotation export.'); }
  validateDocument(document);
  return document;
}

function sameSource(a, b) {
  const fields = ['sha256', 'duration_seconds', 'sample_rate', 'channels', 'origin'];
  return fields.every(key => a.recording[key] === b.recording[key]);
}

function hasObservedContext(event) {
  return event.context !== 'unknown' && event.context_source !== 'not observed';
}

function rounded(value) { return Math.round(value * 1_000_000) / 1_000_000; }

export function compareAnnotations(first, second) {
  validateDocument(first);
  validateDocument(second);
  if (!sameSource(first, second)) {
    throw Error('These annotations do not declare the same WAV checksum, duration, sample rate, channels and origin. Comparison stopped.');
  }
  if (first.recording.annotator_id === second.recording.annotator_id) {
    throw Error('The two files declare the same annotator ID. Use distinct independent annotations for this comparison.');
  }

  const aEvents = [...first.events].sort((a,b) => a.start_seconds - b.start_seconds || a.end_seconds - b.end_seconds || a.id - b.id);
  const bEvents = [...second.events].sort((a,b) => a.start_seconds - b.start_seconds || a.end_seconds - b.end_seconds || a.id - b.id);
  const pairs = [], overlappedA = new Set(), overlappedB = new Set();
  for (const a of aEvents) {
    for (const b of bEvents) {
      if (b.start_seconds >= a.end_seconds) break;
      if (b.end_seconds <= a.start_seconds) continue;
      const start = Math.max(a.start_seconds, b.start_seconds);
      const end = Math.min(a.end_seconds, b.end_seconds);
      const overlap = end - start;
      const union = (a.end_seconds - a.start_seconds) + (b.end_seconds - b.start_seconds) - overlap;
      if (pairs.length >= MAX_OVERLAP_PAIRS) {
        throw Error(`More than ${MAX_OVERLAP_PAIRS} positive-overlap pairs. Narrow the annotation files; partial reports are not created.`);
      }
      overlappedA.add(a.id); overlappedB.add(b.id);
      pairs.push({
        event_a_id:a.id,
        event_b_id:b.id,
        overlap_start_seconds:rounded(start),
        overlap_end_seconds:rounded(end),
        overlap_seconds:rounded(overlap),
        temporal_iou:rounded(overlap / union),
        kind_a:a.kind,
        kind_b:b.kind,
        kind_exact_match:a.kind === b.kind,
        context_a:hasObservedContext(a) && hasObservedContext(b) ? a.context : null,
        context_b:hasObservedContext(a) && hasObservedContext(b) ? b.context : null,
        context_comparison:hasObservedContext(a) && hasObservedContext(b)
          ? (a.context === b.context ? 'same_declared_category' : 'different_declared_category')
          : 'not_comparable_from_independent_context'
      });
    }
  }

  return {
    report_schema:'talk2nature.annotation-comparison.v1',
    method:'All positive temporal overlaps; no one-to-one assignment, consensus, or agreement statistic.',
    source:{sha256:first.recording.sha256,duration_seconds:first.recording.duration_seconds,sample_rate:first.recording.sample_rate,channels:first.recording.channels,declared_origin:first.recording.origin},
    annotation_counts:{a:aEvents.length,b:bEvents.length},
    positive_overlap_pair_count:pairs.length,
    event_ids_without_positive_overlap:{a:aEvents.filter(e=>!overlappedA.has(e.id)).map(e=>e.id),b:bEvents.filter(e=>!overlappedB.has(e.id)).map(e=>e.id)},
    pairwise_overlaps:pairs,
    limitations:[
      'Recording identity and metadata are declared by the input files and are not independently verified.',
      'An interval overlap or exact label match is not biological truth, inter-rater agreement, or evidence of communication.',
      'Events may appear in several overlap rows. No events are merged, assigned, adjudicated, or aggregated.',
      'Notes and annotator IDs are deliberately omitted from this report.'
    ]
  };
}
