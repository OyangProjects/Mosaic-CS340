from flask import Flask, request, make_response
import requests
from PIL import Image
from dotenv import load_dotenv
from scipy import spatial
import numpy as np
from io import BytesIO
import os

app = Flask(__name__)

load_dotenv()

gacha_names = [
    "puzzles_dragons.png", "another_eden.png", "sds.png", "princess_connect.png", "monster_super_league.png", "alchemy_stars.png", 
    "honkai_impact.png", "mahjong_soul.png", "brave_frontier.png", 
    "hbr.png", "feh.png", "world_flipper.png", "pokemon_masters.png", "monster_strike.png", "ensemble_stars.png", "grand_chase.png", "epic_seven.png", "afk_arena.png", 
    "cookie_run.png", "unison_league.png", "limbus_company.png", "king_raid.png", 
    "neural_cloud.png", "genshin.png", "sinoalice.png", "bleach.png", "nikke.png", "romancing_saga.png", "fgo.png", "guardian_tales.png", "pgr.png", "langrisser.png", 
    "onmyoji.png", "konosuba.png", "honkai_starrail.png", "blue_archive.png", "tears.png", "danmachi.png", "raid.png", "battle_cats.png", 
    "granblue.png", "memento_mori.png", "girls_frontline.png", "diablo_immortal.png", "mha.png", 
    "uma_musume.png", "dokkan_battle.png", "one_piece.png", "counterside.png", "summoners_war.png", "azur_lane.png", 
    "tof.png", "illusion_connect.png", "dragalia_lost.png", "identity_v.png", "project_sekai.png", "arknights.png", "eversoul.png", "slime.png", "grand_summoners.png"
]

gacha_tiles = []
gacha_tree = None

gacha_colors = []

for i in range(60):
  tile = Image.open('tilesets/gacha_icons/' + gacha_names[i]).convert('RGB')
  gacha_tiles.append(tile)
  average_color = np.array(tile).mean(axis=0).mean(axis=0)
  gacha_colors.append(average_color)

gacha_tree = spatial.KDTree(gacha_colors)

requests.put(os.getenv('FLASK_ADDRESS'), data={ 'name' : "Gacha Icons MMG", 'url' : os.getenv('GACHA_URL'), 'author' : 'oweny2', 'tileImageCount' : 60})

@app.route('/', methods=['GET'])
def GET_index():
  '''Route for '/' (frontend)'''
  return 'Gacha Icons Mosaic'

@app.route('/makeMosaic', methods=['POST'])
def POST_makeMosaic():
  global gacha_tiles

  # Parameters/Inputs

  tilesAcross = int(request.args.get('tilesAcross'))
  renderedTileSize = int(request.args.get('renderedTileSize'))
  fileFormat = request.args.get('fileFormat')
  bytes_image = request.files['image']

  main_image = Image.open(bytes_image).convert('RGB')

  width = main_image.width
  height = main_image.height
  
  # Resizing 

  d = width / tilesAcross
  verticalTiles = int(height / d)

  new_width = width
  new_height = verticalTiles * d
  main_image = main_image.crop((0, 0, new_width, new_height))
 
  output_width = int(tilesAcross * renderedTileSize)
  output_height = int(verticalTiles * renderedTileSize)

  gacha_output = Image.new('RGB', (output_width, output_height))

  # Creating Mosaic

  for i in range(60):
    gacha_tiles[i] = gacha_tiles[i].resize((renderedTileSize, renderedTileSize))

  x_pixel = 0
  y_pixel = 0
  x_out = 0
  y_out = 0

  while(y_pixel < new_height):
    while(x_pixel < new_width):
      map_tile = main_image.crop((x_pixel, y_pixel, x_pixel + d, y_pixel + d))
      average_color = np.array(map_tile).mean(axis=0).mean(axis=0)

      index = gacha_tree.query(average_color)[1]
      gacha_output.paste(gacha_tiles[index], (x_out, y_out))

      x_pixel += d
      x_out += renderedTileSize

    x_pixel = 0
    y_pixel += d
    x_out = 0
    y_out += renderedTileSize

  # Saving Output

  # gacha_output.save('output/gacha.' + fileFormat.lower() , fileFormat)

  output = BytesIO()
  gacha_output.save(output, format=fileFormat)

  main_image.close()

  return make_response(output.getvalue()), 200