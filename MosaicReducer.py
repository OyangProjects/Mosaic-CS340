from flask import Flask, request, make_response
import requests
from PIL import Image
import numpy as np
from io import BytesIO
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

requests.put(os.getenv('REDUCER_ADDRESS'), data={ 'name' : 'oweny2 Reducer', 'url' : os.getenv('REDUCER_URL'), 'author' : 'oweny2'} )


@app.route("/")
def index():
    return "Hallo World", 200

@app.route("/reduceMosaic", methods=["POST"])
def reduce():
    baseImage = request.files["baseImage"]
    mosaic1 = request.files["mosaic1"]
    mosaic2 = request.files["mosaic2"]

    renderedTileSize = int(request.args.get("renderedTileSize"))
    tilesAcross = int(request.args.get("tilesAcross"))
    fileFormat = request.args.get("fileFormat")

    baseImage = Image.open(baseImage).convert('RGB')
    mosaic1 = Image.open(mosaic1)
    mosaic2 = Image.open(mosaic2)

    width = baseImage.width
    height = baseImage.height

    d = width / tilesAcross
    verticalTiles = int(height / d)

    new_width = width
    new_height = verticalTiles * d
    baseImage = baseImage.crop((0, 0, new_width, new_height))

    reduction_output = Image.new(mode='RGB', size=mosaic1.size)

    x_pixel = 0
    y_pixel = 0
    x_out = 0
    y_out = 0
    
    while(y_pixel < new_height):
        while(x_pixel < new_width):
            base_tile = baseImage.crop((x_pixel, y_pixel, x_pixel + d, y_pixel + d))
            mosaic1_tile = mosaic1.crop((x_out, y_out, x_out + renderedTileSize, y_out + renderedTileSize))
            mosaic2_tile = mosaic2.crop((x_out, y_out, x_out + renderedTileSize, y_out + renderedTileSize))
            
            base_color = np.array(base_tile).mean(axis=0).mean(axis=0)
            mosaic1_color = np.array(mosaic1_tile).mean(axis=0).mean(axis=0)
            mosaic2_color = np.array(mosaic2_tile).mean(axis=0).mean(axis=0)

            distance1 = (base_color[0] - mosaic1_color[0]) ** 2 + (base_color[1] - mosaic1_color[1]) ** 2 + (base_color[2] - mosaic1_color[2]) ** 2
            distance2 = (base_color[0] - mosaic2_color[0]) ** 2 + (base_color[1] - mosaic2_color[1]) ** 2 + (base_color[2] - mosaic2_color[2]) ** 2

            reduction_output.paste(mosaic1_tile, (x_out, y_out)) if distance1 <= distance2 else reduction_output.paste(mosaic2_tile, (x_out, y_out))

            x_pixel += d
            x_out += renderedTileSize

        x_pixel = 0
        y_pixel += d
        x_out = 0
        y_out += renderedTileSize

    # reduction_output.save('output/reduction.' + fileFormat.lower(), fileFormat)

    output = BytesIO()
    reduction_output.save(output, format=fileFormat)

    baseImage.close()
    mosaic1.close()
    mosaic2.close()

    return make_response(output.getvalue()), 200

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=6969)