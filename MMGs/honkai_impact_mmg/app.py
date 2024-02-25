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

honkai_tiles = []
honkai_tree = None

honkai_colors = []

for file in os.listdir('tilesets/honkai_impact'):
  tile = Image.open('tilesets/honkai_impact/' + file).convert('RGB')
  honkai_tiles.append(tile)
  average_color = np.array(tile).mean(axis=0).mean(axis=0)
  honkai_colors.append(average_color)

honkai_tree = spatial.KDTree(honkai_colors)

requests.put(os.getenv('FLASK_ADDRESS'), data={ 'name' : "Honkai Impact MMG", 'url' : os.getenv('HONKAI_URL'), 'author' : 'oweny2', 'tileImageCount' : 60})

@app.route('/', methods=['GET'])
def GET_index():
  '''Route for '/' (frontend)'''
  return 'Honkai Impact Mosaic'

@app.route('/makeMosaic', methods=['POST'])
def POST_makeMosaic():
  global honkai_tiles

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

  honkai_output = Image.new('RGB', (output_width, output_height))

  # Creating Mosaic

  for i in range(60):
    honkai_tiles[i] = honkai_tiles[i].resize((renderedTileSize, renderedTileSize))

  x_pixel = 0
  y_pixel = 0
  x_out = 0
  y_out = 0

  while(y_pixel < new_height):
    while(x_pixel < new_width):
      map_tile = main_image.crop((x_pixel, y_pixel, x_pixel + d, y_pixel + d))
      average_color = np.array(map_tile).mean(axis=0).mean(axis=0)

      index = honkai_tree.query(average_color)[1]
      honkai_output.paste(honkai_tiles[index], (x_out, y_out))

      x_pixel += d
      x_out += renderedTileSize

    x_pixel = 0
    y_pixel += d
    x_out = 0
    y_out += renderedTileSize

  # Saving Output

  # honkai_output.save('output/honkai.' + fileFormat.lower() , fileFormat)

  output = BytesIO()
  honkai_output.save(output, format=fileFormat)

  main_image.close()

  return make_response(output.getvalue()), 200