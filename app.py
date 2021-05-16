
import json
import time


from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import streamlit as st


with open('secret.json') as f:
    secret = json.load(f)

subscription_key = secret['subscription_key']
endpoint = secret['endpoint']

computervision_client = ComputerVisionClient(endpoint,
                                             CognitiveServicesCredentials(subscription_key))


def call_api_with_image(filepath):
    local_image = open(filepath, "rb")
    recognize_results = computervision_client.read_in_stream(
        local_image, raw=True)
    operation_location_local = recognize_results.headers["Operation-Location"]
    operation_id_local = operation_location_local.split("/")[-1]

    while True:
        recognize_result = computervision_client.get_read_result(
            operation_id_local)
        if recognize_result.status.lower() not in ['notstarted', 'running']:
            break
        print('Waiting for result...')
        time.sleep(10)

    if recognize_result.status == OperationStatusCodes.succeeded:
        for text_result in recognize_result.analyze_result.read_results:
            for line in text_result.lines:
                st.write(line.text)
                # print(line.text)
                img_draw = line.bounding_box
                draw.rectangle([(img_draw[0], img_draw[1]),
                                (img_draw[4], img_draw[5])],
                               fill=None, outline='yellow',
                               width=5)
                text_w, text_y = draw.textsize(line.text, font=font)
                draw.rectangle([(img_draw[0], img_draw[1]),
                                (img_draw[0]+text_w, img_draw[1]+text_y)],
                               fill='yellow', width=5)
                draw.text((img_draw[0], img_draw[1]),
                          line.text, fill='black', font=font)


st.title('文字認識アプリ')

uploaded_file = st.file_uploader('Choose an image...', type=['jpg', 'png'])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    img_path = f'img/{uploaded_file.name}'
    img.save(img_path)

    # img = Image.open(local_image_path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font='meiryo.ttc', size=70)

    call_api_with_image(img_path)

    st.image(img)
