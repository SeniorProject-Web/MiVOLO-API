from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .serializers import elementCustomerServiceModelSerializer

from django.core.files.uploadedfile import UploadedFile
from django.http.multipartparser import MultiPartParser

import json     
from django.http import JsonResponse, HttpResponseBadRequest
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

# load model
load_model()

@api_view(['GET', 'POST'])

# Create your views here.

def api_home(request, *args, **kwargs):
    customerData = Customers.objects.all().order_by("?").first()
    data = {}
    if customerData:
        data = {
            "id": customerData.id,
            "top": customerData.top,
            "pant": customerData.pant,
            "time": customerData.time,
            "owner": customerData.owner,
            "location": customerData.location,
        }
    else: 
        return JsonResponse({"error": "No data found"})
    return JsonResponse({"customer": data})

def firebaseTest(request):
    channel_customerId = db.child("Customer").child("Id").get().val()
    channel_top = db.child("Customer").child("top").get().val()
    channel_pant = db.child("Customer").child("pant").get().val()
    channel_time = db.child("Customer").child("time").get().val()
    channel_owner = db.child("Customer").child("owner").get().val()
    channel_location = db.child("Customer").child("location").get().val()
    
    data = {
        "id": channel_customerId,
        "top": channel_top,
        "pant": channel_pant,
        "time": channel_time,
        "owner": channel_owner,
        "location": channel_location
    }
    return JsonResponse({"customer": data})

def firebaseCustomerAdd(request):
    data = {
        "top": "t-shirt",
        "pant": "trouser",
        "time": "2021-07-20",
        "owner": "beambike2@gmail.com",
        "location": "KMUTT"
    }
    db.child("Customer").push(data)
    return JsonResponse({"message": "Data added"})

def getCustomerData(request):
    allData = db.child("Customer").get().val()
    return JsonResponse(allData)

def getCustomer(request):
    customerData = elementCustomer.objects.all().values()
    if customerData:
        return JsonResponse({"customer": list(customerData)})
    else:
        return JsonResponse({"error": "No data found"})

@csrf_exempt
def addCustomer(request): # get api from camera 
    if request.method == 'POST':
        
        try: 
            CustomerList = json.loads(request.body)
            if CustomerList["data"]:
                for customer in CustomerList["data"]:
                    if customer["image"]:
                        # send to mivolo model to predict ang and gender
                        prediction = getImgtoModel(customer["image"])
                        customerData = {
                            "image": customer["image"],
                            "dress": customer["dress"],
                            "tShirt": customer["t-shirt"],
                            "jacket": customer["jacket"] ,
                            "top": customer["top"],
                            "longSleeve" : customer["long-sleeve"],
                            "short": customer["short"],
                            "skirt": customer["skirt"],
                            "trouser": customer["trouser"],
                            "location": customer["location"],
                            "time": customer["time"]
                        }
                    
                    elementCustomer.objects.create(**customerData)
                    
                # return JsonResponse({"message": "Customer added!"})
                return JsonResponse({"predictd": prediction})
                    
            else:
                return JsonResponse({"error": "No data found"})
                
            
        except Exception as e:
            return JsonResponse({"error": str(e)})
            
@csrf_exempt            
def predictCustomer(request):
    if request.method == 'POST':
        
        ONLY_TOPS = ["dress","t-shirt","jacket","top","long-sleeve"]
        ONLY_BOTTOMS = ["short","skirt","trouser"]
        
        requestHeader = request.headers.get("Authorization")
        if not requestHeader:
            
            return JsonResponse({"error": "No token found"})
        
        else:
            print(requestHeader)
            payload = jwt.decode(requestHeader, ACCESS_TOKEN_SECRET, algorithms=["HS256"])
            owner = payload["email"]

            recieveJson = False
            recieveImage = False
            
            if 'customerDetail' in request.FILES and isinstance(request.FILES['customerDetail'], UploadedFile):
                jsonRecieves = request.FILES["customerDetail"]
                CustomerList = json.loads(jsonRecieves.read())
                recieveJson = True    
                            
                if request.FILES.getlist("customerImage"):
                    imageRecieves = request.FILES.getlist("customerImage")
                    recieveImage = True
                    
            if recieveJson and recieveImage:
                results = []
                for customer in CustomerList["data"]:
                    maxTop = 0
                    maxBottom = 0
                    
                    for topEntitie in ONLY_TOPS:
                        if customer[topEntitie] > maxTop:
                            maxTop = customer[topEntitie]
                            finalTop = topEntitie
                        
                    if finalTop == "dress":
                        finalBottom = "None"
                    else:                            
                        for bottomEntitie in ONLY_BOTTOMS:
                            if customer[bottomEntitie] > maxBottom:
                                maxBottom = customer[bottomEntitie]
                                finalBottom = bottomEntitie 
                                
                    for image in imageRecieves:
                        if image.name == f"{customer['image_file']}.jpg":
                            img = PIL.Image.open(image)
                            img_rgb = img.convert("RGB")
                            img_array = np.array(img_rgb)
                        
                            prediction, _ = predictor.recognize(img_array)
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
                        "pant": finalBottom,
                        "time": customer["time"],
                        "top" : finalTop
                    }
                    
                    # send to firestore
                    doc_ref = db.collection(u'customers').document()
                    doc_ref.set(customerData)

                    # results.append(customerData)
                return JsonResponse({"msg": "Done"})          
                                
            elif recieveJson and not recieveImage:
                return HttpResponseBadRequest({"msg": "Only data received!"})       
            elif not recieveJson and recieveImage:
                return HttpResponseBadRequest({"msg": len(imageRecieves)})     
            else:
                return HttpResponseBadRequest({"msg": "No data received!"})
    else:    
        return HttpResponseBadRequest("dont faking know what you want")