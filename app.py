import os
from flask import Flask
from flask_restful import Api, Resource, reqparse
from flasgger import Swagger
from fastai.learner import load_learner
from fastai.vision import *
from fastai.vision.core import *
from werkzeug.datastructures import FileStorage
import ssl
from io import BytesIO

app = Flask(__name__)
api = Api(app)
app.config['SWAGGER'] = {
    'title': 'Covid XRay Model',
    'uiversion': 3
}
swag = Swagger(app)

parser = reqparse.RequestParser()
parser.add_argument('covidxray')

def label_func(x): return x.parent.name # get the folder the file is in for a label (for inference)

class COVIDXRay(Resource):

  def __init__(self):
    self.parser = reqparse.RequestParser()
    self.model = load_learner('models/multi-class-pg.pkl') # a secret is stored here

  def post(self):
      """
      Validate data meets requirements
      ---
      tags:
        - COVIDXRay
      consumes: [multipart/form-data]
      parameters:
          - name: covidxray
            in: formData
            required: true
            type: file
            description: An x-ray image
      responses:
        201:
          description: image processed and a prediction will be returned
      """
      
      self.parser.add_argument('covidxray', type=FileStorage, location='files', required=True)

      args = self.parser.parse_args()
      uploadedImage = load_image(BytesIO(args['covidxray'].read())).reshape(256,256) # this may not work for all images

      pred_class,pred_idx,outputs = self.model.predict(PILImage(uploadedImage))
      i = pred_idx.item()
      classes = ['covid', 'nofinding', 'pneumonia']
      prediction = classes[i]
      result = {'prediction':prediction}

      return result, 201

api.add_resource(COVIDXRay, '/algo')

if __name__ == '__main__':
    certs = ['/run/cert.pem', '/run/key.pem']
    for cert in certs:
        if not (os.path.exists(cert) and os.access(cert, os.R_OK)):
            print("Unable to locate ", cert, " or it is not readable.")
            break
    else:
        # all files exist and can be read
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain("/run/cert.pem", "/run/key.pem")
        app.run(host='0.0.0.0', debug=False, threaded=False, ssl_context = context)

    # if we get here, one of the files is missing or not readable, and we use flask adhoc ssl        
    app.run(host='0.0.0.0', debug=False, threaded=False, ssl_context = 'adhoc')