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

yugioh_tiles = []
yugioh_tree = None

yugioh_colors = []

for file in os.listdir('tilesets/yugioh'):
  tile = Image.open('tilesets/yugioh/' + file).convert('RGB')
  yugioh_tiles.append(tile)
  average_color = np.array(tile).mean(axis=0).mean(axis=0)
  yugioh_colors.append(average_color)

yugioh_tree = spatial.KDTree(yugioh_colors)

requests.put(os.getenv('FLASK_ADDRESS'), data={ 'name' : "Yu-Gi-Oh! MMG", 'url' : os.getenv('YUGIOH_URL'), 'author' : 'oweny2', 'tileImageCount' : 60})

@app.route('/', methods=['GET'])
def GET_index():
  '''Route for '/' (frontend)'''
  return 'yugioh Mosaic'

@app.route('/makeMosaic', methods=['POST'])
def POST_makeMosaic():
  global yugioh_tiles

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

  yugioh_output = Image.new('RGB', (output_width, output_height))

  # Creating Mosaic

  for i in range(60):
    yugioh_tiles[i] = yugioh_tiles[i].resize((renderedTileSize, renderedTileSize))

  x_pixel = 0
  y_pixel = 0
  x_out = 0
  y_out = 0

  while(y_pixel < new_height):
    while(x_pixel < new_width):
      map_tile = main_image.crop((x_pixel, y_pixel, x_pixel + d, y_pixel + d))
      average_color = np.array(map_tile).mean(axis=0).mean(axis=0)

      index = yugioh_tree.query(average_color)[1]
      yugioh_output.paste(yugioh_tiles[index], (x_out, y_out))

      x_pixel += d
      x_out += renderedTileSize

    x_pixel = 0
    y_pixel += d
    x_out = 0
    y_out += renderedTileSize

  # Saving Output

  # yugioh_output.save('output/yugioh.' + fileFormat.lower() , fileFormat)

  output = BytesIO()
  yugioh_output.save(output, format=fileFormat)

  main_image.close()

  return make_response(output.getvalue()), 200