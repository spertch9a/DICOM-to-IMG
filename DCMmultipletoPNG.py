import tkinter as tk
from tkinter import filedialog, messagebox
import pydicom
import numpy as np
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter
import os  # Import for creating directories

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

def convert_dicom_to_image(dicom_file, output_folder, slice_number, brightness=1.0, contrast=1.0, apply_noise_filter=False):
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
    
    # Create output filename with slice number
    output_image_path = f"{output_folder}/{patient_name}_{patient_age}_{slice_number}.png"

    # Save the processed image
    image = Image.fromarray(pixel_array)
    image.save(output_image_path)

    # Display the image (optional)
    # plt.imshow(pixel_array, cmap='gray')
    # plt.title(f'Converted Image: {output_image_path}')
    # plt.show()

    # Return modality for recognition
    return recognize_modality(ds)

def open_file_dialog():
    # Open file dialog to select DICOM files (multiple selection)
    dicom_files = filedialog.askopenfilenames(
        title="Select DICOM files",
        filetypes=[("DICOM files", "*.dcm")])

    if dicom_files:
        global patient_name, patient_age  # Access global variables for folder name and image title
        patient_name = name_var.get()
        patient_age = age_var.get()

        # Create output folder based on user input and date
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        output_folder = f"{patient_name}_{patient_age}_{today}"
        try:
            os.makedirs(output_folder)  # Create folder if it doesn't exist
        except FileExistsError:
            pass  # Ignore error if folder already exists

        # Process each selected DICOM file
        for i, dicom_file in enumerate(dicom_files):
            try:
                modality = convert_dicom_to_image(dicom_file, output_folder, i+1, float(brightness_var.get()), float(contrast_var.get()), noise_var.get())
               # messagebox.showinfo("Success", f"DICOM file converted (Slice {i+1})")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

# GUI Setup
root = tk.Tk()
root.title("DICOM to Image Converter (Multi-Slice)")

# Set window size
root.geometry("600x400")

# Patient Name
name_label = tk.Label(root, text="Patient Name:")
name_label.pack(pady=5)
name_var = tk.StringVar()
name_entry = tk.Entry(root, textvariable=name_var)
name_entry.pack(pady=5)

# Patient Age
age_label = tk.Label(root, text="Patient Age:")
age_label.pack(pady=5)
age_var = tk.StringVar()
age_entry = tk.Entry(root, textvariable=age_var)
age_entry.pack(pady=5)

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
import_button = tk.Button(root, text="Import DICOM Files", command=open_file_dialog)
import_button.pack(pady=20)

# Run the Tkinter main loop
root.mainloop()