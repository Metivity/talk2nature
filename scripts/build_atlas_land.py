"""Derive the public land silhouette from a checked, pinned Natural Earth file.

Acquire the source separately; this script does not fetch or execute remote data.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(source, output):
    receipt = json.loads((ROOT / 'research/atlas-map-source.json').read_text())
    raw = source.read_bytes()
    if len(raw) != receipt['bytes'] or hashlib.sha256(raw).hexdigest() != receipt['sha256']:
        raise ValueError('Natural Earth input does not match its pinned receipt.')
    geo = json.loads(raw)
    paths = []
    for feature in geo['features']:
        geometry = feature['geometry']
        polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
        if geometry['type'] not in {'Polygon', 'MultiPolygon'}:
            raise ValueError('Unsupported map geometry.')
        for polygon in polygons:
            rings = []
            for ring in polygon:
                coords = []
                for lon, lat, *_ in ring:
                    if not (-180.001 <= lon <= 180.001 and -90.001 <= lat <= 90.001):
                        raise ValueError('Invalid map coordinate.')
                    coords.append(f'{(lon+180)/360*1000:.2f},{(90-lat)/180*500:.2f}')
                rings.append('M' + 'L'.join(coords) + 'Z')
            paths.append(''.join(rings))
    markup = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 500"><title>World land silhouette</title><desc>Natural Earth 1:110m land. Public domain. Equirectangular overview, not a boundary or navigation map.</desc><g fill="#41645b" fill-rule="evenodd" stroke="#8bac9438" stroke-width=".7">'
    output.write_text(markup + ''.join(f'<path d="{p}"/>' for p in paths) + '</g></svg>\n')


if __name__ == '__main__':
    build(ROOT/'data/external/natural-earth/ne_110m_land.geojson', ROOT/'web/assets/atlas-land.svg')
