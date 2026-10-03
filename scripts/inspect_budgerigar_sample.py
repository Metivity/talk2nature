"""Inspect one reviewed MAT file, without executing MATLAB or exporting audio.

Optional isolated analysis dependencies: NumPy and SciPy. These are not public
website/backend dependencies. This report describes structure, not call meaning.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = '20220502_Blue571_response1_postproof.mat'
SHA256 = '1130e0426ad81cec26d631d1cc86eb6388ebbe15ed47c011297f239d75c83ef0'


def inspect(folder):
    import numpy as np
    import scipy
    from scipy.io import loadmat, whosmat

    path = Path(folder) / NAME
    if path.stat().st_size != 1486634:
        raise ValueError('Not the reviewed inspection file.')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != SHA256:
        raise ValueError('Source changed; inspect before parsing.')
    inventory = whosmat(path)
    # Explicit variable selection avoids interpreting the saved function workspace.
    rows = loadmat(path, variable_names=['callStructProof'])['callStructProof']
    if rows.shape != (15, 1):
        raise ValueError('Unexpected call structure.')
    rates = [float(row['fs'].item()) for row in rows.flat]
    lengths = [int(row['signalRaw'].size) for row in rows.flat]
    durations = [float(row['duration'].item()) for row in rows.flat]
    return {
        'resource_id': 'budgerigar-vocal-signature-data',
        'source_url': 'https://data.mendeley.com/datasets/j8rpy4dc6c/1',
        'source_version': '10.17632/j8rpy4dc6c.1',
        'source_file': NAME, 'source_bytes': path.stat().st_size,
        'source_sha256': digest, 'license': 'CC-BY-4.0',
        'attribution': 'Zhao, Zhilei (2023), Mendeley Data, version 1.',
        'inspection_date': '2026-10-03',
        'inspection_environment': {'numpy': np.__version__, 'scipy': scipy.__version__},
        'variables': [{'name': n, 'shape': list(s), 'type': t} for n, s, t in inventory],
        'inspected_variable': 'callStructProof', 'struct_rows': rows.size,
        'fields': list(rows.dtype.names), 'declared_fs_values': sorted(set(rates)),
        'raw_sample_count': sum(lengths), 'raw_samples_per_row': {'min': min(lengths), 'max': max(lengths)},
        'total_seconds_if_declared_fs_is_hz': sum(n / fs for n, fs in zip(lengths, rates)),
        'declared_duration_range': {'min': min(durations), 'max': max(durations)},
        'raw_samples_all_finite': all(bool(np.isfinite(row['signalRaw']).all()) for row in rows.flat),
        'raw_filtered_normalized_shapes_match': all(row['signalRaw'].shape == row['signalFiltered'].shape == row['signalNorm'].shape for row in rows.flat),
        'training_admitted': False,
        'limitations': [
            'One smallest-file convenience sample from ColonyNoiseCalls, not a representative corpus.',
            'The stored fs value is 44101; preserved without silently rounding to 44100. Units and acquisition settings need method review.',
            'Fifteen structure rows are not fifteen independent animals, sessions or verified behavior labels.',
            'This container has no explicit independent visible-behavior annotation field. Caller and intervention status remain unverified.',
            'MATLAB object timestamps and the saved function workspace were not interpreted or executed.',
            'No audio playback, model training, conversation inference or public audio redistribution was performed.',
            'Full methods, component rights and suitability for home-recording comparisons remain unreviewed.'
        ]
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, default=ROOT / 'data/external/budgerigar-vocal-signature-data')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(inspect(args.folder), indent=2) + '\n'
    if args.output:
        args.output.write_text(result)
    else:
        print(result, end='')
