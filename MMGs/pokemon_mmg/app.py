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

pokemon_tiles = []
pokemon_tree = None

pokemon_colors = []

for file in os.listdir('tilesets/pokemon'):
  tile = Image.open('tilesets/pokemon/' + file).convert('RGB')
  pokemon_tiles.append(tile)
  average_color = np.array(tile).mean(axis=0).mean(axis=0)
  pokemon_colors.append(average_color)

pokemon_tree = spatial.KDTree(pokemon_colors)

requests.put(os.getenv('FLASK_ADDRESS'), data={ 'name' : "Pokemon MMG", 'url' : os.getenv('POKEMON_URL'), 'author' : 'oweny2', 'tileImageCount' : 60})

@app.route('/', methods=['GET'])
def GET_index():
  '''Route for '/' (frontend)'''
  return 'pokemon Mosaic'

@app.route('/makeMosaic', methods=['POST'])
def POST_makeMosaic():
  global pokemon_tiles

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

  pokemon_output = Image.new('RGB', (output_width, output_height))

  # Creating Mosaic

  for i in range(60):
    pokemon_tiles[i] = pokemon_tiles[i].resize((renderedTileSize, renderedTileSize))

  x_pixel = 0
  y_pixel = 0
  x_out = 0
  y_out = 0

  while(y_pixel < new_height):
    while(x_pixel < new_width):
      map_tile = main_image.crop((x_pixel, y_pixel, x_pixel + d, y_pixel + d))
      average_color = np.array(map_tile).mean(axis=0).mean(axis=0)

      index = pokemon_tree.query(average_color)[1]
      pokemon_output.paste(pokemon_tiles[index], (x_out, y_out))

      x_pixel += d
      x_out += renderedTileSize

    x_pixel = 0
    y_pixel += d
    x_out = 0
    y_out += renderedTileSize

  # Saving Output

  # pokemon_output.save('output/pokemon.' + fileFormat.lower() , fileFormat)

  output = BytesIO()
  pokemon_output.save(output, format=fileFormat)

  main_image.close()

  return make_response(output.getvalue()), 200