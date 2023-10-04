import base64
import hashlib
from io import BytesIO
from django.shortcuts import render
from PIL import Image
from django.http import JsonResponse

# from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt


def andrew_alpha(request):
    return render(request, 'andrew_alpha.html', {})


@csrf_exempt
def upload_image(request):

    if request.method == 'POST':

        # Get uploaded file data
        image_data = request.FILES['image'].read()

        # Open image and make a copy to avoid read-after-close error
        img = Image.open(BytesIO(image_data))
        processed_img = img.copy()

        # hash the image for a unique name
        md5hash = hashlib.md5(processed_img.tobytes())
        processed_img.save(f"./saved_images/{md5hash.hexdigest()}.png")

        # Process image
        processed_img = processed_img.rotate(90)

        # Save processed image to BytesIO object to get bytes
        with BytesIO() as output:
            processed_img.save(output, format='JPEG')
            processed_img_data = output.getvalue()

        # Return processed image data back
        response = JsonResponse({
            "message": "Image processed successfully",
            "processed_image": base64.b64encode(
                processed_img_data
                ).decode('utf-8')
        })

        response['Access-Control-Allow-Origin'] = '*'

        return response

    return JsonResponse({"message": "No image received"})
