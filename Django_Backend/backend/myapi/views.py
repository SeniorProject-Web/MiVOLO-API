from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .serializers import elementCustomerServiceModelSerializer

from django.core.files.uploadedfile import UploadedFile
from django.http.multipartparser import MultiPartParser

import json     
from django.http import JsonResponse
from .models import createCustomerServiceModel as Customers
from .models import elementCustomerServiceModel as elementCustomer
from imagePredict import getImgtoModel
import os
import PIL
from io import BytesIO
import base64

import logging
import numpy as np
from mivolo.predictor import Predictor
from timm.utils import setup_default_logging
import torch

import firebase_admin
from firebase_admin import firestore
import jwt

db = firestore.client()

ACCESS_TOKEN_SECRET= "CxTq8dpnGz8i2yRr9P71XK82E2nFz78B"

# model weights permanent path
detector_weights_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..','models', 'yolov8x_person_face.pt'))
checkpoint_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','..', 'models', 'model_imdb_cross_person_4.22_99.46.pth.tar'))

def load_model():
    global predictor
    config = {
        'detector-weights': detector_weights_path,
        'checkpoint': checkpoint_path,
        'with-persons': False,
        'disable-faces': False,
        'draw': False,
        'device': 'cpu'
    }
    setup_default_logging()

    if torch.cuda.is_available():
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.benchmark = True
    
    predictor = Predictor(config, verbose=True)

# load model mivolo
load_model()

@api_view(['GET', 'POST'])

# Create your views here.

@csrf_exempt            
def customerTest(request):
    
    ONLY_TOPS = ["dress","t-shirt","jacket","top","long-sleeve"]
    ONLY_BOTTOMS = ["short","skirt","trouser"]
    
    try:
        if request.method == "POST":  
            requestHeader = request.headers.get("accessToken") # get token from header
            
            if requestHeader:
                payload = jwt.decode(requestHeader, ACCESS_TOKEN_SECRET, algorithms=["HS256"])
                owner = payload["email"]
            else:
                return JsonResponse({"message": "missing token in customerFeature"}, status=401)
            
            if request.FILES.get("data") is None:
                return JsonResponse({"message": "No data found"}, status=400)

            jsonRecieves = request.FILES["data"] # get data.json with list customer data            
            CustomerList = json.loads(jsonRecieves.read())
            
            if CustomerList["data"]:
                for customer in CustomerList["data"]:
                    maxTop = 0
                    maxBottom = 0
                    targetId = customer["img-name"].split(".jpg")[0] # {trackId}.jpg
                    
                    finalTop = None
                    finalBottom = None
                    customerAge = 0
                    customerGender = None
                    customerData = {}
                        
                    for topEntity in ONLY_TOPS:
                        if customer[topEntity] > maxTop:
                            maxTop = customer[topEntity]
                            finalTop = topEntity
                    if maxTop == 0:
                        finalTop = None

                    if finalTop == "dress": # if top is dress, bottom is none
                        finalBottom = "-"
                    else:                            
                        for bottomEntity in ONLY_BOTTOMS:
                            if customer[bottomEntity] > maxBottom:
                                maxBottom = customer[bottomEntity]
                                finalBottom = bottomEntity
                        if maxBottom == 0:
                            finalBottom = None
                        
                    print(f"target {targetId} ===> finalTop: {finalTop}, finalBottom: {finalBottom}")
                    
                    if finalTop is None or finalBottom is None: # if top or bottom is none
                        # return JsonResponse({"error": f"top or bottom is none in {targetId}", "message": f"top or bottom is none in {targetId}"}, status=402)
                        print(f"top or bottom is none in {targetId}")
                        continue
                                
                    targetImage = request.FILES.get(f"image_{targetId}", None) # get image from customer track id
                    
                    if targetImage is not None: # send image to mivolo model to predict age/gender
                        img = PIL.Image.open(targetImage)
                        img_rgb = img.convert("RGB")
                        img_array = np.array(img_rgb)
                        prediction,_ = predictor.recognize(img_array)
                        
                        print(f"feature track number {targetId} : \n")
                        print(f"face_count: {prediction.n_faces}, person_count: {prediction.n_persons}")
                        
                        if(prediction.n_faces == 0 and prediction.n_persons == 0):
                            continue
                        customerAge = int(prediction.ages[0])
                        customerGender = prediction.genders[0]
                        
                        if(customerAge >= 15 and customerAge <= 29):
                            customerAge = "15-29"
                        elif(customerAge >= 30 and customerAge <= 59):
                            customerAge = "30-59"
                        elif(customerAge >= 60):
                            customerAge = "60up"
                            
                        customerData = {
                            "gender": customerGender,
                            "age": customerAge,
                            "location": customer["location"],
                            "owner": owner,
                            "lowerPart": finalBottom,
                            "time": customer["time"],
                            "upperPart" : finalTop
                        }
                        
                        doc_ref = db.collection(u'customers').document()
                        doc_ref.set(customerData)
                    else:
                        print(f"No image in {targetId} found")
                        continue  
                    
                return JsonResponse({"message":"customerFeature Done"}, status=200)

            else:
                print("No key argument => data <= found")
                return JsonResponse({"message":"No key argument => data <= found"}, status=400) 
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
@csrf_exempt
def customerAttention(request):
    try:
        
        if request.method == "POST":  
            requestHeader = request.headers.get("accessToken") # get token from header
            
            if requestHeader:
                payload = jwt.decode(requestHeader, ACCESS_TOKEN_SECRET, algorithms=["HS256"])
                owner = payload["email"]
            else:
                return JsonResponse({"message": "missing token in customerFeature"}, status=401)
            
            if request.FILES.get("data") is None:
                print("No data found")
                return JsonResponse({"message": "No data found"}, status=400)
            
            jsonRecieves = request.FILES["data"] # get data.json with list customer data
            AttentionList = json.loads(jsonRecieves.read())
            
            if AttentionList["data"]:
                for cusAttention in AttentionList["data"]:
                    customerAge = 0
                    customerGender = None
                    attentionData = {}
                    
                    targetId = cusAttention["img-name"].split(".jpg")[0]
                    look_status = cusAttention["look_status"]
                    targetImage = request.FILES.get(f"image_{targetId}", None)
                    
                    if targetImage is not None:
                        img = PIL.Image.open(targetImage)
                        img_rgb = img.convert("RGB")
                        img_array = np.array(img_rgb)
                        prediction,_ = predictor.recognize(img_array)

                        if(prediction.n_faces == 0 and prediction.n_persons == 0):
                            continue
                        
                        customerAge = int(prediction.ages[0])
                        customerGender = prediction.genders[0]
                        
                        print(f"attention track number {targetId} : \n")
                        print(f"face_count: {prediction.n_faces}, person_count: {prediction.n_persons}")
                        
                        if(customerAge >= 15 and customerAge <= 29):
                            customerAge = "15-29"
                        elif(customerAge >= 30 and customerAge <= 59):
                            customerAge = "30-59"
                        elif(customerAge >= 60):
                            customerAge = "60up"
                            
                    else:
                        # return JsonResponse({"error": f"No image in {targetId} found", "message": f"No image in {targetId} found"}, status=400)
                        print(f"No image in {targetId} found")
                        continue
                    
                    attentionData = {
                        "gender": customerGender,
                        "age": customerAge,
                        "location": cusAttention["location"],
                        "owner": owner,
                        "time": cusAttention["time"],
                        "look_status" : look_status
                    }
                    
                    doc_ref = db.collection(u'attention').document()
                    doc_ref.set(attentionData)
                    
                return JsonResponse({"message": "customerAttention Done"}, status=200)
            else:
                print("No key argument => data <= found")
                return JsonResponse({"message":"No key argument => data <= found"}, status=400) 
    
    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=400)  