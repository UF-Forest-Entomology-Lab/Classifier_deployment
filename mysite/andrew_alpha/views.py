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
        # Get uploaded file from request.FILES dictionary
        print(request.FILES.keys())
        # print(request.FILES['img'])
        uploaded_file = request.FILES['image'].read()

        # Process uploaded file here
        # Convert the image data to a PIL.Image object
        with BytesIO(uploaded_file) as f:
            img = Image.open(f)

        # Process the image using PIL
        img = img.rotate(90)

        # Save the processed image to disk
        img.save('image.jpg')

        # Convert the processed image back to a format that can be sent 
        # back to the client
        with BytesIO() as f:
            img.save(f, 'JPEG')
            response_data = f.getvalue()

        # Send the processed image back to the client
        return JsonResponse({
            "Message": "File Uploaded Successfully",
            'processed_image': response_data})

    return JsonResponse({"Message": ""})
