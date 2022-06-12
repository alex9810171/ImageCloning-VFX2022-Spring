from flask import Flask, render_template, request, Response, jsonify
import numpy as np
import cv2
from cloning import cloning_api_for_web

config = {
    'background_image_path': r'test/ice-coast.png',
    'test_image_path': r'test/polarbear.png',
    'result_image_path': r'result.png',
    'temp_image_path': r'image/temp/',
    'paste_position_x': 200,
    'paste_position_y': 200,
    'kernel': np.ones((3, 3), np.uint8),
    'object_threshold': 500
}

app = Flask(__name__)
bkg_image = cv2.imread(config['background_image_path'])

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/cloning")
def cloning():
    return render_template('cloning.html', image_url=request.args.get('image_url', ''))

@app.route('/api/cloning', methods=['POST'])
def cloning_api():
    if 'image' not in request.files:
        return Response(status=400)
    image_buffer = np.frombuffer(request.files['image'].read(), np.uint8)
    if len(image_buffer) == 0:
        return Response(status=400)
    img = cv2.imdecode(image_buffer, cv2.IMREAD_COLOR)
    if img.shape[2] != 3:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    result = cloning_api_for_web(bkg_image, img, int(request.form.get('x-axis', 200)), int(request.form.get('y-axis', 200)))
    # print(result)
    result_link = upload_to_imgur(result)
    if result_link is None:
        return Response(status=500)
    else:
        return jsonify({'result': result_link})


import requests
from base64 import b64encode
import random
import string
import cv2
CLIENT_ID = '47a12b43b020d51'
def upload_to_imgur(img):
    # get a random name string for the image
    name = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    # encode the image to base64
    ret, img_encoded = cv2.imencode('.jpg', img)
    img_encoded = b64encode(img_encoded)
    # upload the image to imgur
    response = requests.post('https://api.imgur.com/3/image',
                                headers={'Authorization': 'Client-ID ' + CLIENT_ID},
                                data={
                                    'image': img_encoded,
                                    'type': 'base64',
                                    'name': f'img_encoded.jpg',
                                    'title': name}).json()
    if response['status'] == 200:
        return response['data']['link']
    else:
        return None
if __name__ == '__main__':
    app.run(debug=True)
