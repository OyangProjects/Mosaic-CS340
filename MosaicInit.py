import os
import subprocess
from flask import Flask, request, make_response


file_paths = ['MMGs/arknights_mmg/app.py', 'MMGs/genshin_mmg/app.py', 'MMGs/gacha_icons_mmg/app.py', 'MMGs/starrail_mmg/app.py', 'MMGs/honkai_impact_mmg/app.py',
              'MMGs/minecraft_mmg/app.py', 'MMGs/pokemon_mmg/app.py', 'MMGs/epicseven_mmg/app.py', 'MMGs/yugioh_mmg/app.py', 'MMGs/scenic_art_mmg/app.py',
              'MMGs/anime_mmg/app.py', 'MMGs/flag_mmg/app.py', 'MMGs/app_mmg/app.py', 'MosaicReducer.py']
processes = []

for i, file_path in enumerate(file_paths):
    port = 5001 + i
    command = f'FLASK_APP={file_path} python3 -m flask run --port={port} --host=0.0.0.0'
    process = subprocess.Popen(command, shell=True)
    processes.append(process)

for process in processes:
    process.wait()