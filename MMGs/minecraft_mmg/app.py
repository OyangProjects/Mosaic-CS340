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

minecraft_tiles = []
minecraft_tree = None

minecraft_colors = []

for file in os.listdir('tilesets/minecraft'):
  tile = Image.open('tilesets/minecraft/' + file).convert('RGB')
  minecraft_tiles.append(tile)
  average_color = np.array(tile).mean(axis=0).mean(axis=0)
  minecraft_colors.append(average_color)

minecraft_tree = spatial.KDTree(minecraft_colors)

requests.put(os.getenv('FLASK_ADDRESS'), data={ 'name' : "Minecraft MMG", 'url' : os.getenv('MINECRAFT_URL'), 'author' : 'oweny2', 'tileImageCount' : 60})

@app.route('/', methods=['GET'])
def GET_index():
  '''Route for '/' (frontend)'''
  return 'minecraft Mosaic'

@app.route('/makeMosaic', methods=['POST'])
def POST_makeMosaic():
  global minecraft_tiles

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

  minecraft_output = Image.new('RGB', (output_width, output_height))

  # Creating Mosaic

  for i in range(60):
    minecraft_tiles[i] = minecraft_tiles[i].resize((renderedTileSize, renderedTileSize))

  x_pixel = 0
  y_pixel = 0
  x_out = 0
  y_out = 0

  while(y_pixel < new_height):
    while(x_pixel < new_width):
      map_tile = main_image.crop((x_pixel, y_pixel, x_pixel + d, y_pixel + d))
      average_color = np.array(map_tile).mean(axis=0).mean(axis=0)

      index = minecraft_tree.query(average_color)[1]
      minecraft_output.paste(minecraft_tiles[index], (x_out, y_out))

      x_pixel += d
      x_out += renderedTileSize

    x_pixel = 0
    y_pixel += d
    x_out = 0
    y_out += renderedTileSize

  # Saving Output

  # minecraft_output.save('output/minecraft.' + fileFormat.lower() , fileFormat)

  output = BytesIO()
  minecraft_output.save(output, format=fileFormat)

  main_image.close()

  return make_response(output.getvalue()), 200