from flask import Flask, request, make_response
import requests
from PIL import Image
from dotenv import load_dotenv
from scipy import spatial
import numpy as np
from io import BytesIO
import os

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

load_dotenv()

arknights_names = [
    'ch\'en', 'siege', 'nightingale', 'eyjafjalla', 'exusiai', 'angelina', 'silverash', 'saria', 'skadi', 'schwarz',
    'hellagur', 'mostima', 'blaze', 'bagpipe', 'phantom', 'w', 'weedy', 'suzuran', 'thorns', 'eunectes',
    'surtr', 'blemishine', 'rosmontis', 'mudrock', 'gavial the invincible', 'archetto', 'dusk', 'skadi the corrupting heart', 'kal\'tsit', 'pallas',
    'mizuki', 'saileach', 'fartooth', 'flametail', 'gnosis', 'ling', 'goldenglow', 'fiammetta', 'horn', 'irene',
    'ptilopsis', 'amiya', 'manticore', 'blue poison', 'platinum', 'texas', 'lappland', 'nearl', 'specter', 'liskarm',
    'ceylon', 'astesia', 'shamare', 'mint', 'kirara', 'mulberry', 'aurora', 'myrtle', 'ethan', 'purestream'
]

arknights_tiles = []
arknights_tree = None 

arknights_colors = []

for i in range(60):
  tile = Image.open('arknights/' + arknights_names[i] + '.png').convert('RGB')
  arknights_tiles.append(tile)
  average_color = np.array(tile).mean(axis=0).mean(axis=0)
  arknights_colors.append(average_color)

arknights_tree = spatial.KDTree(arknights_colors)

requests.put(os.getenv('FLASK_ADDRESS'), data={ 'name' : "Arknights MMG", 'url' : os.getenv('ARKNIGHTS_URL'), 'author' : 'oweny2', 'tileImageCount' : 60})

@app.route('/', methods=['GET'])
def GET_index():
  '''Route for '/' (frontend)'''
  return 'Arknights Mosaic'

@app.route('/makeMosaic', methods=['POST'])
def POST_makeMosaic():
  global arknights_tiles

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

  arknights_output = Image.new('RGB', (output_width, output_height))

  # Creating Mosaic

  for i in range(60):
    arknights_tiles[i] = arknights_tiles[i].resize((renderedTileSize, renderedTileSize))

  x_pixel = 0
  y_pixel = 0
  x_out = 0
  y_out = 0

  while(y_pixel < new_height):
    while(x_pixel < new_width):
      map_tile = main_image.crop((x_pixel, y_pixel, x_pixel + d, y_pixel + d))
      average_color = np.array(map_tile).mean(axis=0).mean(axis=0)

      index = arknights_tree.query(average_color)[1]
      arknights_output.paste(arknights_tiles[index], (x_out, y_out))

      x_pixel += d
      x_out += renderedTileSize

    x_pixel = 0
    y_pixel += d
    x_out = 0
    y_out += renderedTileSize

  # Saving Output

  # arknights_output.save('output/arknights.' + fileFormat.lower() , fileFormat)

  output = BytesIO()
  arknights_output.save(output, format=fileFormat)

  main_image.close()

  return make_response(output.getvalue()), 200
