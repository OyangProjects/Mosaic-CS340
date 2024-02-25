from flask import Flask, jsonify, request, make_response
import base64
import requests
from PIL import Image
from dotenv import load_dotenv
from scipy import spatial
import numpy as np
from io import BytesIO
import os

app = Flask(__name__)

load_dotenv()

genshin_names = [
    'albedo.png', 'alhaitham.png', 'amber.png', 'ayaka.png', 'ayato.png', 'barbara.png', 'beidou.png', 'bennett.png', 'childe.png', 
    'chongyun.png', 'dehya.png', 'diluc.png', 'diona.png', 'dori.png', 'eula.png', 'fischl.png', 'ganyu.png', 'ganyu2.png',
    'gorou.png', 'heizou.png', 'hutao.png', 'itto.png', 'jean.png', 'kaeya.png', 'kazuha.png', 'keqing.png', 'keqing2.png', 
    'klee.png', 'kokomi.png', 'kuki.png', 'layla.png', 'lisa.png', 'mona.png', 'nilou.png', 'ningguang.png', 'noelle.png', 'paimon.png',
    'qiqi.png', 'raiden.png', 'razor.png', 'rosaria.png', 'sara.png', 'sayu.png', 'shenhe.png', 'sucrose.png', 'tartaglia.png', 'thoma.png', 'tighnari.png',
    'venti.png', 'wanderer.png', 'xiangling.png', 'xiao.png', 'xingqiu.png', 'xinyan.png', 'yae.png', 'yanfei.png', 'yaoyao.png', 
    'yoimiya.png', 'yunjin.png', 'zhongli.png'
]

genshin_tiles = []
genshin_tree = None

genshin_colors = []

for i in range(60):
  tile = Image.open('genshin/' + genshin_names[i]).convert('RGB')
  genshin_tiles.append(tile)
  average_color = np.array(tile).mean(axis=0).mean(axis=0)
  genshin_colors.append(average_color)

genshin_tree = spatial.KDTree(genshin_colors)

requests.put(os.getenv('FLASK_ADDRESS'), data={ 'name' : "Genshin MMG", 'url' : os.getenv('GENSHIN_URL'), 'author' : 'oweny2', 'tileImageCount' : 60})

@app.route('/', methods=['GET'])
def GET_index():
  '''Route for '/' (frontend)'''
  return 'Genshin Mosaic'

@app.route('/makeMosaic', methods=['POST'])
def POST_makeMosaic():
  global genshin_tiles

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

  genshin_output = Image.new('RGB', (output_width, output_height))

  # Creating Mosaic

  for i in range(60):
    genshin_tiles[i] = genshin_tiles[i].resize((renderedTileSize, renderedTileSize))

  x_pixel = 0
  y_pixel = 0
  x_out = 0
  y_out = 0

  while(y_pixel < new_height):
    while(x_pixel < new_width):
      map_tile = main_image.crop((x_pixel, y_pixel, x_pixel + d, y_pixel + d))
      average_color = np.array(map_tile).mean(axis=0).mean(axis=0)

      index = genshin_tree.query(average_color)[1]
      genshin_output.paste(genshin_tiles[index], (x_out, y_out))

      x_pixel += d
      x_out += renderedTileSize

    x_pixel = 0
    y_pixel += d
    x_out = 0
    y_out += renderedTileSize

  # Saving Output

  # genshin_output.save('output/genshin.' + fileFormat.lower() , fileFormat)

  output = BytesIO()
  genshin_output.save(output, format=fileFormat)

  main_image.close()

  return make_response(output.getvalue()), 200