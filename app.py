import urllib
import json
import os

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms, models
import numpy as np

# transformations to apply on inference img
transform_test = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

# Pre Load model from /model dir
model = models.resnet18(pretrained=False)
num_ftrs = model.fc.in_features        
model.fc = nn.Sequential(
    nn.Linear(num_ftrs, 256),
    nn.ReLU(),
    nn.Dropout(0.4),
    nn.Linear(256, 4), 
    nn.LogSoftmax(dim=1) 
)
model.load_state_dict(torch.load('model/model.pth'))
model.eval()

# obj classes
objects_category = ['beer-mug','coffee-mug','teapot','wine-bottle']

# lambda handler
def lambda_handler(event, context):
    print(event)
    url = event['queryStringParameters']['url']
    
    img = Image.open(urllib.request.urlopen(url))
    scaled_img = transform_test(img)
    torch_images = scaled_img.unsqueeze(0)

    with torch.no_grad():
            predict = model(torch_images)
            output = torch.exp(predict)
            index = np.argmax(output)

    return {
        'statusCode': 200,
        'body': json.dumps({
            "Label": objects_category[index],
            "Probability": str(output[0][index])
        })
    }
