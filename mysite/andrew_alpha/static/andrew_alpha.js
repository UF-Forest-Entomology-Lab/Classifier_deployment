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
const webcamFeed = document.getElementById("webcamFeed");
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
      webcamFeed.innerHTML = "No webcam detected.";
      document.body.appendChild(message);
    });
} else {
  console.error("getUserMedia is not supported by this browser");
}

/////////////////////////////////

// Variable to store latest captured frame URL
let latestFrameURL;

// Add click handler to capture button
captureButton.addEventListener("click", function() {

  // Remove previously displayed captured frame (if any)
  while (capturedFrame.firstChild) {
    capturedFrame.firstChild.remove();
  }

  // Clear processed image display
  while (processedFrame.firstChild) {
    processedFrame.firstChild.remove();
  }

  // Create canvas element 
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");

  // Set canvas dimensions to match video
  canvas.width = video.videoWidth; 
  canvas.height = video.videoHeight;

  // Draw current video frame to canvas
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Convert canvas to data URL
  const dataURL = canvas.toDataURL("image/png");

  // Save data URL to reuse when appending to form
  latestFrameURL = dataURL;

  // Create img element for captured frame
  const capturedImage = document.createElement("img");
  capturedImage.src = latestFrameURL;

  // Append to captured frame div
  capturedFrame.appendChild(capturedImage);
  if (canvas) {

    // Convert canvas to blob
    canvas.toBlob(function(blob) {

      // Create file from blob
      const file = new File([blob], 'capturedImage.jpg', {type: 'image/jpeg'})

      // Create FormData
      const formData = new FormData();

      // Append file 
      formData.append('image', file);

      // Headers with token
      const headers = new Headers();
      headers.append('X-CSRFToken', csrftoken);

      // Send FormData
      fetch('/process_uploaded_image/', {
        method: 'POST',
        headers: headers,
        body: formData
      })
      .then(response => response.blob())
      .then(blob => {

        // Create image from blob
        const img = document.createElement('img');
        img.src = URL.createObjectURL(blob);

        // // Replace original image with processed one
        // while (capturedFrame.firstChild) {
        //   capturedFrame.firstChild.remove();
        // }
        // document.getElementById('capturedFrame').appendChild(img);

        // Display processed image
        // Append to DOM
        document.getElementById('processedFrame').appendChild(img);
      
      })
      .catch(error => {
        console.error('Error processing image'); 
      });

    }, 'image/jpeg');

  } else {
    console.error("Canvas not found"); 
  }

});


  /////////////////////////////////

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
      // Clear processed image display
      while (processedFrame.firstChild) {
        processedFrame.firstChild.remove();
      }

      // Create an image element for displaying uploaded image
      const uploadedImage = document.createElement("img");
      uploadedImage.src = uploadedImageURL;
      const imageFile = fileInput.files[0];
      let formData = new FormData();
      formData.append('image', imageFile);

      fetch('/process_uploaded_image/', {
        method: 'POST',
        body: formData
      })
      .then(response => response.blob())
      .then(blob => {

        // Create image from blob
        const img = document.createElement('img');
        img.src = URL.createObjectURL(blob);

        // // Replace original image with processed one
        // while (capturedFrame.firstChild) {
        //   capturedFrame.firstChild.remove();
        // }
        // document.getElementById('capturedFrame').appendChild(img);

        // Display processed image
        // Append to DOM
        document.getElementById('processedFrame').appendChild(img);
      
      })
      .catch(error => {
        console.error('Error processing image');
      });


      // Append uploaded image to captured frame div
      capturedFrame.appendChild(uploadedImage);
      
    });

    if (fileInput.files.length > 0) {
      fileReader.readAsDataURL(fileInput.files[0]);
    }
  });

  fileInput.click();
});