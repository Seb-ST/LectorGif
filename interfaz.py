# interfaz.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from procesamiento_gif import parse_gif_metadata, save_metadata_to_txt

# Variables globales
metadata_entries = {}
preview_label = None


# Funciones de la interfaz
def open_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        process_folder(folder_path)


def process_folder(folder_path):
    gif_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.gif'):
                gif_files.append(os.path.join(root, file))
    listbox.delete(0, tk.END)
    for gif in gif_files:
        listbox.insert(tk.END, gif)


def load_metadata():
    selected_file = listbox.get(listbox.curselection())
    try:
        metadata = parse_gif_metadata(selected_file)
        display_metadata(metadata)
        display_preview(selected_file)
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar el archivo: {e}")


def display_metadata(metadata):
    for key, entry in metadata_entries.items():
        entry.delete(0, tk.END)
        entry.insert(0, str(metadata.get(key, "")))


def save_metadata():
    selected_file = listbox.get(listbox.curselection())
    metadata = {key: entry.get() for key, entry in metadata_entries.items()}
    save_path = 'metadatos.txt'
    try:
        save_metadata_to_txt(save_path, metadata)
        messagebox.showinfo("Éxito", "Metadatos guardados en metadatos.txt.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")


def load_from_txt():
    try:
        with open("metadatos.txt", "r") as file:
            txt_data = file.read()
            text_display.delete(1.0, tk.END)
            text_display.insert(tk.END, txt_data)
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo metadatos.txt no existe.")


def display_preview(file_path):
    try:
        img = Image.open(file_path)
        img.thumbnail((200, 200))  # Tamaño de la miniatura
        img_tk = ImageTk.PhotoImage(img)
        preview_label.config(image=img_tk)
        preview_label.image = img_tk
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar la vista previa: {e}")


root = tk.Tk()
root.title("Extractor y Editor de Metadatos de GIF")
root.geometry("1000x700")
root.configure(bg="#1e1e1e")

bg_color = "#1e1e1e"
fg_color = "#ffffff"
button_color = "#333333"
highlight_color = "#444444"

frame_files = tk.Frame(root, bg=bg_color)
frame_files.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

open_button = ttk.Button(frame_files, text="Abrir Carpeta", command=open_folder)
open_button.pack(fill=tk.X, pady=5)

listbox = tk.Listbox(frame_files, width=50, bg=highlight_color, fg=fg_color, selectbackground="#5e5e5e")
listbox.pack(fill=tk.BOTH, expand=True)
listbox.bind("<<ListboxSelect>>", lambda e: load_metadata())

preview_frame = tk.Frame(root, bg=bg_color)
preview_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)

preview_label = tk.Label(preview_frame, bg=bg_color)
preview_label.pack(pady=10)

frame_metadata = tk.Frame(root, bg=bg_color)
frame_metadata.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

metadata_labels = ["Número de versión", "Tamaño de imagen", "Cantidad de colores", "Resolución de color",
                   "Color de fondo", "Cantidad de imágenes", "Fecha de creación", "Fecha de modificación", "Comentarios"]

for label_text in metadata_labels:
    label = tk.Label(frame_metadata, text=label_text, bg=bg_color, fg=fg_color)
    label.pack(anchor="w")
    entry = tk.Entry(frame_metadata, width=50, bg=highlight_color, fg=fg_color, insertbackground=fg_color)
    entry.pack(fill=tk.X, padx=5, pady=2)
    metadata_entries[label_text] = entry

save_button = ttk.Button(frame_metadata, text="Guardar Cambios", command=save_metadata)
save_button.pack(pady=10)

load_button = ttk.Button(frame_metadata, text="Cargar metadatos guardados", command=load_from_txt)
load_button.pack(pady=10)

text_display = tk.Text(root, height=10, wrap=tk.WORD, bg=highlight_color, fg=fg_color, insertbackground=fg_color)
text_display.pack(fill=tk.BOTH, padx=10, pady=10)

root.mainloop()
