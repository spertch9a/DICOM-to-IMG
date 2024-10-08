import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Scrollbar, Text
import os
import pydicom
import numpy as np
import vtk
from vtk import vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor
from vtk import vtkImageActor, vtkPolyData, vtkPolyDataMapper, vtkActor, vtkPoints, vtkCellArray
from vtk import vtkImageImport
from vtk import vtkTransform, vtkTransformPolyDataFilter


class DICOMViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM Viewer")
        self.slices = []
        self.non_image_dicom_files = []
        self.dicom_dir = ""

        # Buttons
        self.load_button = tk.Button(root, text="Load DICOM Directory", command=self.load_directory)
        self.load_button.pack(pady=10)

        self.view_2d_button = tk.Button(root, text="View 2D", command=self.view_2d)
        self.view_2d_button.pack(pady=10)

        self.view_3d_button = tk.Button(root, text="View 3D", command=self.view_3d)
        self.view_3d_button.pack(pady=10)

    def load_directory(self):
        self.dicom_dir = filedialog.askdirectory()
        if not self.dicom_dir:
            return

        self.slices = []
        self.non_image_dicom_files = []
        for root, dirs, files in os.walk(self.dicom_dir):
            for file in files:
                try:
                    filepath = os.path.join(root, file)
                    ds = pydicom.dcmread(filepath)
                    if 'PixelData' in ds:
                        self.slices.append(ds.pixel_array)
                    else:
                        self.non_image_dicom_files.append(ds)  # Store non-image DICOM datasets
                        self.show_non_image_metadata(ds)
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")

        if not self.slices:
            messagebox.showwarning("Warning", "No DICOM files with pixel data found.")

    def show_non_image_metadata(self, ds):
        """Show the metadata of non-image DICOM files in a new window."""
        metadata_window = Toplevel(self.root)
        metadata_window.title("Non-Image DICOM Metadata")

        text_area = Text(metadata_window, wrap='word')
        scrollbar = Scrollbar(metadata_window, command=text_area.yview)
        text_area.config(yscrollcommand=scrollbar.set)

        for elem in ds:
            text_area.insert(tk.END, f"{elem}: {ds[elem]}\n")

        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_area.config(state=tk.DISABLED)  # Make text area read-only

    def view_2d(self):
        if not self.slices:
            messagebox.showwarning("Warning", "No slices loaded.")
            return

        # Example to visualize the first slice in 2D
        first_slice = self.slices[0]
        self.display_image(first_slice)

    def display_image(self, image):
        from matplotlib import pyplot as plt

        plt.imshow(image, cmap="gray")
        plt.axis('off')
        plt.show()

    def view_3d(self):
        if not self.slices:
            messagebox.showwarning("Warning", "No slices loaded.")
            return

        self.render_3d()

    def render_3d(self):
        # Setup VTK rendering
        renderer = vtkRenderer()
        render_window = vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window_interactor = vtkRenderWindowInteractor()
        render_window_interactor.SetRenderWindow(render_window)

        for idx, slice_data in enumerate(self.slices):
            # Convert the slice data to a VTK image
            vtk_image = vtkImageImport()
            vtk_image.CopyImportVoidPointer(slice_data.tobytes(), slice_data.nbytes)
            vtk_image.SetDataScalarTypeToUnsignedShort()
            vtk_image.SetNumberOfScalarComponents(1)
            vtk_image.SetDataExtent(0, slice_data.shape[1] - 1, 0, slice_data.shape[0] - 1, 0, 0)
            vtk_image.SetWholeExtent(0, slice_data.shape[1] - 1, 0, slice_data.shape[0] - 1, 0, 0)

            # Create an image actor for the slice
            image_actor = vtkImageActor()
            image_actor.GetMapper().SetInputConnection(vtk_image.GetOutputPort())

            # Position the slice in 3D space
            transform = vtkTransform()
            transform.Translate(0, 0, idx)  # Position slices along the Z-axis
            image_actor.SetUserTransform(transform)

            # Add the actor to the renderer
            renderer.AddActor(image_actor)

        renderer.SetBackground(1, 1, 1)  # Background color white
        render_window.Render()
        render_window_interactor.Start()


if __name__ == "__main__":
    root = tk.Tk()
    viewer = DICOMViewer(root)
    root.mainloop()
