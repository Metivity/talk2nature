"""Public mobile shell, explicit offline allowlist and reproducible app icons."""
import hashlib
import json
import math
import struct
import zlib
from functools import lru_cache


@lru_cache(maxsize=3)
def icon_png(size):
    """Rasterize our original leaf mark; no downloaded art or imaging dependency."""
    def bezier(points, t):
        return tuple(sum(math.comb(3, i) * (1-t)**(3-i) * t**i * p[d] for i, p in enumerate(points)) for d in (0, 1))
    leaf = [bezier([(20,45),(14,30),(17,18),(44,15)], i/24) for i in range(25)]
    leaf += [bezier([(44,15),(46,38),(35,49),(20,45)], i/24) for i in range(25)]
    def inside(x,y):
        hit=False
        for a,b in zip(leaf, leaf[1:]+leaf[:1]):
            if (a[1]>y)!=(b[1]>y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]: hit=not hit
        return hit
    def distance(x,y,a,b):
        dx,dy=b[0]-a[0],b[1]-a[1]
        t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
        return math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)
    raw=bytearray()
    for row in range(size):
        raw.append(0)
        for col in range(size):
            x,y=(col+.5)*64/size,(row+.5)*64/size
            color=(16,40,47)
            if inside(x,y): color=(181,245,217)
            if min(distance(x,y,a,b) for a,b in [((19,47),(42,20)),((27,37),(25,26)),((33,30),(42,29))])<1.25: color=(16,40,47)
            raw.extend(color)
    def chunk(kind, data): return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')


def build_mobile(root, output, prefix, page, station, listen, asset_revision):
    base=prefix
    common=f'<link rel="manifest" href="{base}/app/manifest.webmanifest"><link rel="apple-touch-icon" href="{base}/app/icons/icon-180.png"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Talk2Nature"><link rel="stylesheet" href="{base}/assets/app.css"><script type="module" src="{base}/assets/app.js"></script>'
    def template(name): return (root/'web/templates'/name).read_text().replace('{{base}}',base)
    page('app/','Talk2Nature mobile: your field companion','A local-first mobile companion for outdoor listening, familiar animals and careful audio review. Open immediately or add it to your home screen.',template('app.html'),extra_head=common,app=True)
    station_body=station[station.index('<section id="station-console"'):station.index('<section class="section station-future"')]
    station_body=template('app-station-intro.html')+station_body
    page('app/station/','Listen and observe with your phone','A guided foreground listening session with private local clips and encounter markers. Choose an outdoor, companion or synthetic rehearsal workflow.',station_body,extra_head=f'<link rel="stylesheet" href="{base}/assets/station.css">'+common+f'<script type="module" src="{base}/assets/station.js"></script>',app=True)
    page('app/review/','Review a recording on your device','Inspect a short local WAV, annotate what you heard and observed, and export your work without uploading the recording.',listen,extra_head=f'<link rel="stylesheet" href="{base}/assets/listen.css">'+common+f'<script type="module" src="{base}/assets/listen.js"></script>',app=True)
    page('app/compare/','Compare two moments','Reopen two saved sessions on your device. Compare recordings, observations and context without uploading files.',template('compare.html'),extra_head=common+f'<link rel="stylesheet" href="{base}/assets/compare.css"><script type="module" src="{base}/assets/compare.js"></script>',app=True)
    page('mobile/','Get the Talk2Nature mobile app','Try the Talk2Nature web app on Android or iPhone. Installation instructions, practical scenarios and an honest look at what the first release can do.',template('mobile.html'),extra_head=f'<link rel="stylesheet" href="{base}/assets/app.css"><script defer src="{base}/assets/mobile-launch.js"></script>')
    app_root=output/'app'; (app_root/'icons').mkdir(exist_ok=True)
    for size in (180,192,512): (app_root/f'icons/icon-{size}.png').write_bytes(icon_png(size))
    manifest={'id':base+'/app/','name':'Talk2Nature — Field companion','short_name':'Talk2Nature','description':'Listen, observe and review sound locally. Short foreground sessions; no animal translation.','lang':'en','start_url':base+'/app/','scope':base+'/app/','display':'standalone','background_color':'#10282f','theme_color':'#10282f','icons':[{'src':base+f'/app/icons/icon-{s}.png','sizes':f'{s}x{s}','type':'image/png','purpose':'any maskable'} for s in (192,512)],'shortcuts':[{'name':'Outdoor listening','url':base+'/app/station/?mode=outdoor'},{'name':'Companion observations','url':base+'/app/station/?mode=companion'},{'name':'Sound desk','url':base+'/app/review/'}]}
    (app_root/'manifest.webmanifest').write_text(json.dumps(manifest,indent=2)+'\n')
    # Exact public shell only. No runtime responses, private routes or user media.
    paths=['app/','app/station/','app/review/','app/compare/','app/manifest.webmanifest']+[f'app/icons/icon-{s}.png' for s in (180,192,512)]
    paths += ['assets/'+p for p in ('style.css','design.css','personality.css','hub.css','site.js','atmosphere.js','mark.svg','app.css','app.js','app-scene.svg','station.css','station.js','station-model.mjs','window-model.mjs','observation-ui.mjs','station-audio.mjs','station-capture.mjs','station-export.mjs','listen.css','listen.js','listen-model.mjs','notebook.mjs','audacity-export.mjs','animal-model.mjs','animal-picker.mjs','compare.css','compare.js','session-import.mjs')]
    def local(path): return output/(path+'index.html' if path.endswith('/') else path)
    worker_source=(root/'web/templates/app-sw.js').read_text()
    revision=hashlib.sha256(worker_source.encode()+b''.join(local(p).read_bytes() for p in paths)).hexdigest()[:16]
    worker=worker_source.replace('__REVISION__',revision).replace('__ASSETS__',json.dumps([base+'/'+p+(f'?v={asset_revision}' if p.startswith('assets/') else '') for p in paths])).replace('__SCOPE__',json.dumps(base+'/app/'))
    (app_root/'sw.js').write_text(worker)
