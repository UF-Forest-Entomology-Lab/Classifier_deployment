from io import BytesIO
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import os
import random
import hashlib
import cv2
import torch
import numpy as np
from groundingdino.util.inference import load_model, load_image, predict, annotate
from PIL import Image
from math import ceil
# from fastai.learner import load_learner
from huggingface_hub import from_pretrained_fastai
# from huggingface_hub import hf_hub_download
from torchvision.transforms import GaussianBlur
from torchvision.ops import box_convert


# Define a custom transform for Gaussian blur
def gaussian_blur(
    x,
    p=0.5,
    kernel_size_min=3,
    kernel_size_max=20,
    sigma_min=0.1,
    sigma_max=3):
    if x.ndim == 4:
        for i in range(x.shape[0]):
            if random.random() < p:
                kernel_size = random.randrange(
                    kernel_size_min,
                    kernel_size_max + 1, 2)
                sigma = random.uniform(sigma_min, sigma_max)
                x[i] = GaussianBlur(kernel_size=kernel_size, sigma=sigma)(x[i])
    return x


# load model
learn = from_pretrained_fastai("ChristopherMarais/beetle-model")
# learn = load_learner(
#     hf_hub_download(
#       'ChristopherMarais/Andrew_AI-BB_classification-beta',
#       filename="model.pkl")
#     )

# get class names
labels = np.append(np.array(learn.dls.vocab), "Unknown")


# this function only describes how much a singular value in al ist stands out.
# if all values in the lsit are high or low this is 1
# the smaller the proportiopn of number of disimilar vlaues are to other more
# similar values the lower this number
# the larger the gap between the dissimilar numbers and the simialr number the
# smaller this number
# only able to interpret probabilities or values between 0 and 1
# this function outputs an estimate an inverse of the classification
# confidence based on the probabilities of all the classes.
# the wedge threshold splits the data on a threshold with a magnitude of a
# positive int to force a ledge/peak in the data
def unkown_prob_calc(
    probs,
    wedge_threshold,
    wedge_magnitude=1,
    wedge='strict'):
    if wedge == 'strict':
        increase_var = (1/(wedge_magnitude))
        decrease_var = (wedge_magnitude)
    # this allows points that are furhter from the threshold ot be moved less
    # and points clsoer to be moved more
    if wedge == 'dynamic':
        increase_var = (
            1/(wedge_magnitude*((1-np.abs(probs-wedge_threshold))))
            )
        decrease_var = (wedge_magnitude*((1-np.abs(probs-wedge_threshold))))
    else:
        print("Error: use 'strict' (default) or 'dynamic' as options for the wedge parameter!")
    probs = np.where(probs >= wedge_threshold, probs**increase_var, probs)
    probs = np.where(probs <= wedge_threshold, probs**decrease_var, probs)
    diff_matrix = np.abs(probs[:, np.newaxis] - probs)
    diff_matrix_sum = np.sum(diff_matrix)
    probs_sum = np.sum(probs)
    class_val = (diff_matrix_sum/probs_sum)
    max_class_val = ((len(probs)-1)*2)
    kown_prob = class_val/max_class_val
    unknown_prob = 1-kown_prob
    return (unknown_prob)


def detect_objects(og_image_path):

    TEXT_PROMPT = "bug"
    BOX_TRESHOLD = 0.35
    TEXT_TRESHOLD = 0.25
    DEVICE = 'cpu'  # cuda or cpu
    MODEL_PATH = "./mysite/andrew_alpha/0_object_detection_model/GroundingDINO_SwinT_OGC.cfg.py"
    MODEL_CONFIG_PATH = "./mysite/andrew_alpha/0_object_detection_model/groundingdino_swint_ogc.pth"
    # MODEL_PATH = "./mysite/andrew_alpha/0_object_detection_model/GroundingDINO_SwinB.cfg.py"
    # MODEL_CONFIG_PATH = "./mysite/andrew_alpha/0_object_detection_model/groundingdino_swinb_cogcoor.pth"

    model = load_model(
        MODEL_PATH,
        MODEL_CONFIG_PATH)

    image_source, image = load_image(og_image_path)

    boxes, logits, phrases = predict(
        model=model,
        image=image,
        caption=TEXT_PROMPT,
        box_threshold=BOX_TRESHOLD,
        text_threshold=TEXT_TRESHOLD,
        device=DEVICE
    )

    # # replace phrases
    # na_phrase = ("OD score:-"*len(phrases)).split("-")
    # annotated_frame = annotate(
    #     image_source=image_source,
    #     boxes=boxes,
    #     logits=logits,
    #     phrases=na_phrase)
    # im_col = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    # od_image_obj = Image.fromarray(im_col, 'RGB')

    # create a list of all the identified object images
    # Crop the image using PIL
    og_image_obj = Image.open(og_image_path)
    height, width = og_image_obj.size

    boxes_norm = boxes * torch.Tensor([width, height, width, height])

    xywh = box_convert(
        boxes=boxes_norm,
        in_fmt="cxcywh",
        out_fmt="xywh").numpy()

    img_lst = []
    for i in range(len(boxes_norm)):
        left = int(xywh[i][0])
        top = int(xywh[i][1])
        right = ceil(xywh[i][0])+ceil(xywh[i][2])
        bottom = ceil(xywh[i][1])+ceil(xywh[i][3])
        crop_img = og_image_obj.crop((left, top, right, bottom))
        img_lst.append(crop_img)

    # return (od_image_obj, img_lst, boxes)
    return (image_source, img_lst, boxes)


def bark_beetle_predict(og_image_path):
    # Detect objects in image
    # crop into list of smaller images
    # processed_image, image_lst, boxes = detect_objects(og_image_path)
    image_source, image_lst, boxes = detect_objects(og_image_path)
    # get predictions for all segments
    conf_dict_lst = []
    img_cnt = len(image_lst)

    for i in range(0, img_cnt):
        prob_ar = np.array(learn.predict(image_lst[i])[2])
        unkown_prob = unkown_prob_calc(
            probs=prob_ar,
            wedge_threshold=0.85,
            wedge_magnitude=5,
            wedge='dynamic')
        prob_ar = np.append(prob_ar, unkown_prob)
        # prob_ar = np.around(prob_ar*100, decimals=1)

        conf_dict = {labels[i]: float(prob_ar[i]) for i in range(len(prob_ar))}
        conf_dict = dict(sorted(
            conf_dict.items(),
            key=lambda item: item[1],
            reverse=True))
        conf_dict_lst.append(conf_dict)  # str(conf_dict)
        result = list(zip(image_lst, conf_dict_lst))

    # only get max class and confidence
    max_conf_lst = []
    max_class_lst = []
    for i in range(len(result)):
        temp_dict = result[i][1]
        max_conf = max(temp_dict.values())
        key_list = list(temp_dict.keys())
        position = list(temp_dict.values()).index(max_conf)
        max_class = key_list[position]
        max_conf_lst.append(float(max_conf))
        max_class_lst.append(max_class)

    # annotate image with classification results
    annotated_frame = annotate(
        image_source=image_source,
        boxes=boxes,
        logits=max_conf_lst,
        phrases=max_class_lst)
    im_col = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    od_image_obj = Image.fromarray(im_col, 'RGB')

    return (od_image_obj, result)


def andrew_alpha(request):
    return render(request, 'andrew_alpha.html', {})


@csrf_exempt
def process_uploaded_image(request):

    if request.method == 'POST':
        # Get uploaded file data
        image_data = request.FILES['image'].read()

        # Open image and make a copy to avoid read-after-close error
        img = Image.open(BytesIO(image_data))
        img = img.convert('RGB')
        processed_img = img.copy()

        # hash the image for a unique name
        md5hash = hashlib.md5(processed_img.tobytes())
        image_path = f"./mysite/andrew_alpha/2_submitted_images/{md5hash.hexdigest()}.png"

        # save uploaded image
        processed_img.save(image_path)

        # Process image
        processed_img, result = bark_beetle_predict(
            og_image_path=image_path
            )

        # Save processed image to BytesIO in memory
        buffer = BytesIO()
        processed_img.save(buffer, 'JPEG')
        img_data = buffer.getvalue()
        return HttpResponse(img_data, content_type='image/jpeg')

    return JsonResponse({"message": "No image received"})
