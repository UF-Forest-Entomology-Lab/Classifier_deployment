# import base64
import hashlib
from io import BytesIO
from django.shortcuts import render
from PIL import Image
from django.http import JsonResponse, FileResponse, HttpResponse

# from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt


def andrew_alpha(request):
    return render(request, 'andrew_alpha.html', {})


@csrf_exempt
def process_image(request):

    if request.method == 'POST':
        # Get uploaded file data
        image_data = request.FILES['image'].read()

        # Open image and make a copy to avoid read-after-close error
        img = Image.open(BytesIO(image_data))
        img = img.convert('RGB')
        processed_img = img.copy()

        # hash the image for a unique name
        md5hash = hashlib.md5(processed_img.tobytes())
        image_path = f"./andrew_alpha/submitted_images/{md5hash.hexdigest()}.png"

        # save uploaded image
        processed_img.save(image_path)

        # Process image
        processed_img = processed_img.rotate(180)

        # # save processed image
        # processed_img_path = f"./andrew_alpha/processed_images/{md5hash.hexdigest()}.png"
        # processed_img.save(processed_img_path)

        # # convert to base64
        # processed_img_base64 = base64.b64encode(
        #         processed_img.tobytes()
        #         ).decode('utf-8')

        # Return processed image data back
        # response = JsonResponse({
        #     "message": "Image processed successfully",
        #     "processed_image": processed_img_base64
        # })
        # response = FileResponse(open(processed_img_path, 'rb'))

        # Cross-Origin Resource Sharing (CORS)
        # response['Access-Control-Allow-Origin'] = '*'

        # return response

        # Save processed image to BytesIO in memory
        buffer = BytesIO()
        processed_img.save(buffer, 'JPEG')
        img_data = buffer.getvalue()
        return HttpResponse(img_data, content_type='image/jpeg')

    return JsonResponse({"message": "No image received"})
