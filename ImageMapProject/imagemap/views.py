from django.shortcuts import render
import os
import folium
from PIL import Image
from io import BytesIO
import base64
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_map_with_overlay_images(image_paths, map_center=(0, 0), zoom_start=12):
    # Create a Folium map centered at the specified location
    map_object = folium.Map(location=map_center, zoom_start=zoom_start)

    for image_path in image_paths:
        # Load the image using Pillow
        image = Image.open(image_path)

        # Convert the image to a data URL format
        data_url = BytesIO()
        image.save(data_url, format='png')
        data_url = 'data:image/png;base64,' + base64.b64encode(data_url.getvalue()).decode()

        # Add the image as an overlay to the map
        folium.raster_layers.ImageOverlay(
            image=data_url,
            bounds=[[map_center[0] - 0.001, map_center[1] - 0.001], [map_center[0] + 0.001, map_center[1] + 0.001]],
            opacity=1,
            interactive=True,
            cross_origin=False,
            zindex=1
        ).add_to(map_object)

    # Save the map to an HTML file
    output_map_path = os.path.join(settings.MEDIA_ROOT, 'map.html')
    map_object.save(output_map_path)
    return output_map_path

def index(request):
    if request.method == 'POST' and request.FILES.getlist('file[]'):
        uploaded_files = request.FILES.getlist('file[]')
        image_paths = []

        for file in uploaded_files:
            if allowed_file(file.name):
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                image_paths.append(fs.url(filename))

        if image_paths:
            latitude = 46.778642
            longitude = -92.431184
            map_center = (latitude, longitude)
            output_map_path = create_map_with_overlay_images(image_paths, map_center)
            return redirect(settings.MEDIA_URL + 'map.html')

    return render(request, 'imagemap/index.html')

