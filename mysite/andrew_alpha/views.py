import hashlib
from io import BytesIO
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import cv2
from groundingdino.util.inference import load_model, load_image, predict, annotate
from PIL import Image


def detect_objects(og_image_path):

    TEXT_PROMPT = "bug"
    BOX_TRESHOLD = 0.35
    TEXT_TRESHOLD = 0.25
    DEVICE = 'cpu'
    MODEL_PATH = "./andrew_alpha/0_object_detection_model/GroundingDINO_SwinT_OGC.cfg.py"
    MODEL_CONFIG_PATH = "./andrew_alpha/0_object_detection_model/groundingdino_swint_ogc.pth"
    # MODEL_PATH = "./andrew_alpha/0_object_detection_model/GroundingDINO_SwinB.cfg.py"
    # MODEL_CONFIG_PATH = "./andrew_alpha/0_object_detection_model/groundingdino_swinb_cogcoor.pth"

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

    annotated_frame = annotate(
        image_source=image_source,
        boxes=boxes,
        logits=logits,
        phrases=phrases)
    im_col = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    od_image_obj = Image.fromarray(im_col, 'RGB')

    return od_image_obj


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
        image_path = f"./andrew_alpha/2_submitted_images/{md5hash.hexdigest()}.png"

        # save uploaded image
        processed_img.save(image_path)

        # Process image
        processed_img = detect_objects(og_image_path=image_path)
        # processed_img = processed_img.rotate(180)

        # Save processed image to BytesIO in memory
        buffer = BytesIO()
        processed_img.save(buffer, 'JPEG')
        img_data = buffer.getvalue()
        return HttpResponse(img_data, content_type='image/jpeg')

    return JsonResponse({"message": "No image received"})
