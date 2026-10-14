"""Render GPL KMahjongg tiles from a clean pinned source checkout."""
from pathlib import Path
import hashlib
import os
import shutil
import subprocess
ROOT = Path(__file__).resolve().parents[1]
PIN = '56e7407bfebb53498e6219fbd3df89869483f287'
source = ROOT/'.sources/libkmahjongg'
if not source.exists():
    source.mkdir(parents=True)
    subprocess.run(['git','init',str(source)],check=True)
    subprocess.run(['git','-C',str(source),'remote','add','origin','https://github.com/KDE/libkmahjongg.git'],check=True)
    subprocess.run(['git','-C',str(source),'fetch','--depth','1','origin',PIN],check=True)
    subprocess.run(['git','-C',str(source),'checkout','--detach',PIN],check=True)
if subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()!=PIN:
    raise SystemExit('Use the pinned libkmahjongg commit; preserve any existing checkout.')
if subprocess.run(['git','-C',str(source),'diff','--quiet']).returncode:
    raise SystemExit('Preserve changed tile sources rather than replacing them.')
metadata = (source/'tilesets/default.desktop').read_text()
if 'License=GPL-2.0-or-later' not in metadata:
    raise SystemExit('Tile licence changed; review before bundling.')
build = ROOT/'build/mahjong-art'
build.mkdir(parents=True,exist_ok=True)
subprocess.run([os.environ.get('JOYORBIT_HOST_QMAKE','/opt/homebrew/opt/qt@5/bin/qmake'),str(ROOT/'scripts/render-mahjong.pro')],cwd=build,check=True)
subprocess.run(['make','-j4'],cwd=build,check=True)
data = ROOT/'games/data'
data.mkdir(parents=True,exist_ok=True)
atlas = data/'kmahjongg-default-atlas.png'
subprocess.run([str(build/'render-mahjong'),str(source/'tilesets/default.svg'),str(atlas)],env={**os.environ,'QT_QPA_PLATFORM':'offscreen'},check=True)
notices = ROOT/'theme/licenses'
credits = ['KMahjongg default tiles','Source: https://github.com/KDE/libkmahjongg/tree/'+PIN]
credits += [line for line in metadata.splitlines() if line.startswith(('Author=','Copyright=','License='))]
credits += ['JoyOrbit adaptation: SVG faces rendered separately into a PNG atlas; original art is unchanged.']
(notices/'KMahjongg-tiles.txt').write_text('\n'.join(credits)+'\n')
shutil.copy2(source/'LICENSES/GPL-2.0-or-later.txt',notices/'KMahjongg-GPL2.txt')
print('Mahjong licensed atlas prepared:',hashlib.file_digest(atlas.open('rb'),'sha256').hexdigest())
