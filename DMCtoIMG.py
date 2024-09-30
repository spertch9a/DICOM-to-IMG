import tkinter as tk
from tkinter import filedialog, messagebox
import pydicom
import numpy as np
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter

def apply_brightness_contrast(pixel_array, brightness=1.0, contrast=1.0):
    """Adjust brightness and contrast using Pillow."""
    image = Image.fromarray(pixel_array)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)
    enhancer = ImageEnhance.Contrast(image)
    return np.array(enhancer.enhance(contrast))

def apply_filter(pixel_array):
    """Apply median filter for basic noise reduction."""
    return median_filter(pixel_array, size=3)

def recognize_modality(ds):
    """Basic DICOM metadata recognition."""
    modality = ds.Modality if 'Modality' in ds else "Unknown"
    return modality

def convert_dicom_to_image(dicom_file, output_image, brightness=1.0, contrast=1.0, apply_noise_filter=False):
    # Load DICOM file
    ds = pydicom.dcmread(dicom_file)
    
    # Extract pixel data from DICOM
    pixel_array = ds.pixel_array
    
    # Normalize pixel data to the range 0-255 for visualization
    pixel_array = ((pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)

    # Apply image manipulations (brightness, contrast, filter)
    pixel_array = apply_brightness_contrast(pixel_array, brightness, contrast)
    
    if apply_noise_filter:
        pixel_array = apply_filter(pixel_array)
    
    # Save the processed image
    image = Image.fromarray(pixel_array)
    image.save(output_image)

    # Display the image
    plt.imshow(pixel_array, cmap='gray')
    plt.title(f'Converted Image: {output_image}')
    plt.show()

    # Return modality for recognition
    return recognize_modality(ds)

def open_file_dialog():
    # Open file dialog to select a DICOM file
    dicom_file = filedialog.askopenfilename(
        title="Select a DICOM file",
        filetypes=[("DICOM files", "*.dcm")])

    if dicom_file:
        try:
            # Output image path
            output_image_path = dicom_file.replace(".dcm", ".png")
            
            # Fetch brightness and contrast from the interface (default: 1.0)
            brightness = float(brightness_var.get())
            contrast = float(contrast_var.get())
            apply_noise_filter = noise_var.get()

            # Convert and process DICOM file
            modality = convert_dicom_to_image(dicom_file, output_image_path, brightness, contrast, apply_noise_filter)

            # Notify user of success and show recognized modality
            messagebox.showinfo("Success", f"DICOM file converted to {output_image_path}\nRecognized Modality: {modality}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

# GUI Setup
root = tk.Tk()
root.title("DICOM to Image Converter")

# Set window size
root.geometry("400x300")

# Brightness control
brightness_var = tk.StringVar(value="1.0")
tk.Label(root, text="Brightness:").pack(pady=5)
tk.Entry(root, textvariable=brightness_var).pack(pady=5)

# Contrast control
contrast_var = tk.StringVar(value="1.0")
tk.Label(root, text="Contrast:").pack(pady=5)
tk.Entry(root, textvariable=contrast_var).pack(pady=5)

# Noise reduction checkbox
noise_var = tk.BooleanVar()
tk.Checkbutton(root, text="Apply Noise Reduction (Median Filter)", variable=noise_var).pack(pady=10)

# Import button
import_button = tk.Button(root, text="Import DICOM File", command=open_file_dialog)
import_button.pack(pady=20)

# Run the Tkinter main loop
root.mainloop()
# TODO  : Enable to import multiple dcm files and export them all at once in a single folder 