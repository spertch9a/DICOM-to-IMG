import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pydicom
import numpy as np
from PIL import Image
import io
import base64

# Initialize the Dash app
app = dash.Dash(__name__)

# Global variable to hold the DICOM series
dicom_series = []

# Convert DICOM to a format Dash can display (Base64 PNG)
def dicom_to_image(ds, brightness=1.0, contrast=1.0):
    pixel_array = ds.pixel_array

    # Normalize pixel array to range 0-255
    pixel_array = ((pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)

    # Apply brightness and contrast
    image = Image.fromarray(pixel_array)
    image = Image.eval(image, lambda x: int(x * contrast + (brightness - 1.0) * 128))

    # Convert the image to PNG
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_data = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_data}"

# Layout of the app
app.layout = html.Div([
    html.H1("Interactive DICOM Viewer (Series Navigation)"),
    
    # Upload DICOM files directly (multiple)
    dcc.Upload(
        id='upload-dicom',
        children=html.Button('Upload DICOM Files'),
        multiple=True  # Allow multiple DICOM file uploads
    ),
    
    # Slider for navigating slices
    html.Div([
        html.Label("Slice Navigation"),
        dcc.Slider(id='slice-slider', min=0, max=0, step=1, value=0, marks={}),
    ], style={'width': '80%', 'padding': '20px'}),

    # Sliders for brightness and contrast
    html.Div([
        html.Label("Brightness"),
        dcc.Slider(id='brightness-slider', min=0.5, max=2.0, step=0.1, value=1.0),
        html.Label("Contrast"),
        dcc.Slider(id='contrast-slider', min=0.5, max=2.0, step=0.1, value=1.0),
    ], style={'width': '80%', 'padding': '20px'}),

    # Area to display the image (smaller size)
    html.Div([
        html.Img(id='dicom-image', style={'width': '50%', 'height': '50%'}),
    ]),
])

# Helper function to extract DICOM files from uploaded files
def load_dicom_files(uploaded_files):
    global dicom_series
    dicom_series = []

    # Process each uploaded file
    for content in uploaded_files:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        
        # Convert bytes back to DICOM file
        dicom_file = io.BytesIO(decoded)
        try:
            # Attempt to read the DICOM file normally
            ds = pydicom.dcmread(dicom_file)
        except pydicom.errors.InvalidDicomError:
            # Force reading the DICOM file if the header is missing or incomplete
            ds = pydicom.dcmread(dicom_file, force=True)

        dicom_series.append(ds)

    # Sort by InstanceNumber (if available) for correct slice order
    dicom_series.sort(key=lambda x: int(x.InstanceNumber) if 'InstanceNumber' in x else 0)

# Callback to handle the DICOM file uploads and slice navigation
@app.callback(
    [Output('slice-slider', 'max'),
     Output('slice-slider', 'marks')],
    [Input('upload-dicom', 'contents')]
)
def handle_dicom_upload(contents):
    if contents is not None:
        # Load the uploaded DICOM files
        load_dicom_files(contents)
        
        # Set the slider max based on the number of slices
        max_slices = len(dicom_series) - 1
        marks = {i: str(i+1) for i in range(len(dicom_series))}
        return max_slices, marks

    return 0, {}

# Callback to update image based on slice navigation and brightness/contrast changes
@app.callback(
    Output('dicom-image', 'src'),
    [Input('slice-slider', 'value'),
     Input('brightness-slider', 'value'),
     Input('contrast-slider', 'value')]
)
def update_image(slice_idx, brightness, contrast):
    if dicom_series:
        # Get the selected slice
        ds = dicom_series[slice_idx]
        
        # Convert to image with brightness/contrast
        return dicom_to_image(ds, brightness, contrast)

    return None

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
