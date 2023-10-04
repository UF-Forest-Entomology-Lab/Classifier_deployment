// Get token from cookie 
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Get the video element
const video = document.getElementById("videoElement");
const captureButton = document.getElementById("captureButton");
const uploadButton = document.getElementById("uploadButton");
const capturedFrame = document.getElementById("capturedFrame");
const processedFrame = document.getElementById("processedFrame");
// Get CSRF token from cookie
const csrftoken = getCookie('csrftoken');
// Get reference to form
const form = document.getElementById('myForm');

// Check if the browser supports getUserMedia
if (navigator.mediaDevices.getUserMedia) {
  // Request access to the webcam
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then(function (stream) {
      // Set the video source to the stream from the webcam
      video.srcObject = stream;
    })
    .catch(function (error) {
      console.error("Error accessing the webcam:", error);
      const message = document.createElement("p");
      message.textContent = "No webcam detected";
      document.body.appendChild(message);
    });
} else {
  console.error("getUserMedia is not supported by this browser");
}

let latestFrameURL; // Variable to store the URL of the latest captured frame

// Add event listener to capture button
captureButton.addEventListener("click", function () {
  // Create a canvas element
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");

  // Set canvas dimensions to match video dimensions
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  // Draw current frame from video onto canvas
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Convert canvas image to data URL
  const dataURL = canvas.toDataURL("image/png");

  // Remove previously displayed captured frame (if any)
  while (capturedFrame.firstChild) {
    capturedFrame.firstChild.remove();
  }

  // Create an image element for displaying captured frame
  const capturedImage = document.createElement("img");
  capturedImage.src = dataURL;


  ///////////////////
  // Download image when clicking on capture frame
  // // Create a new anchor element with the URL
  // const anchorElement = document.createElement('a');
  // anchorElement.href = dataURL;
  // anchorElement.download = 'image.png';

  // // Click the anchor element to download the file
  // anchorElement.click();

  // Append image data to FormData object
  const formData = new FormData(form);
  // formData.append('image', latestFrameURL);

  // csrf for fetch approach
  // Create headers with token
  const headers = new Headers();
  headers.append('X-CSRFToken', csrftoken);

  // Send FormData
  fetch('/upload_image/', {
    method: 'POST',
    headers: headers,
    body: formData
  });
  

  // // Send FormData object to server using XMLHttpRequest
  // const xhr = new XMLHttpRequest();
  // xhr.open('POST', '/upload_image/');

  // // Add CSRF token to request headers
  // xhr.setRequestHeader('X-CSRFToken', csrftoken);

  // // send data
  // xhr.send(formData);

  ///////////////////

  // Append captured image to captured frame div
  capturedFrame.appendChild(capturedImage);
});

// Add event listener to upload button
uploadButton.addEventListener("click", function () {
  const fileInput = document.createElement("input");
  fileInput.type = "file";

  fileInput.addEventListener("change", function () {
    const fileReader = new FileReader();

    fileReader.addEventListener("load", function () {
      const uploadedImageURL = fileReader.result;

      // Remove previously displayed captured frame (if any)
      while (capturedFrame.firstChild) {
        capturedFrame.firstChild.remove();
      }

      // Create an image element for displaying uploaded image
      const uploadedImage = document.createElement("img");
      uploadedImage.src = uploadedImageURL;

      // Display processed image
      const processedImage = document.createElement('img');

        ///////////////////
        const imageFile = fileInput.files[0];
        let formData = new FormData();
        formData.append('image', imageFile);

        fetch('/upload_image/', {
          method: 'POST',
          body: formData
        })
        .then(response => {
          console.log('Success!');
        })
        .then(response => response.json())
        .then(data => {

          // Get base64 encoded image data
          const processedImgData = data.processed_image;
          console.log(processedImgData);

          // Decode base64 data to bytes
          const bytes = Uint8Array.from(atob(processedImgData), c => c.charCodeAt(0));
          console.log(bytes);
        
          // Create blob from bytes
          const blob = new Blob([bytes], {type: 'image/jpeg'}); 
        
          // Create image URL from blob
          const processedImageURL = URL.createObjectURL(blob);
        
          processedImage.src = processedImageURL;
        
        })
        .catch(error => {
          console.error('Error uploading image');
        });

        processedFrame.appendChild(processedImage);
        
        ///////////////////

      // Append uploaded image to captured frame div
      capturedFrame.appendChild(uploadedImage);
    });

    if (fileInput.files.length > 0) {
      fileReader.readAsDataURL(fileInput.files[0]);
    }
  });

  fileInput.click();
});