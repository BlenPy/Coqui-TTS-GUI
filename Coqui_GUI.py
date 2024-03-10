import os
import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog
from TTS.api import TTS
import json
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize models_dict
models_dict = {"tts_models": {}}

def load_models_info_from_file(file_path="models_info.json"):
    with open(file_path, "r") as file:
        models_info = json.load(file)

    # Ensure that necessary keys exist in the dictionary
    for model_info in models_info:
        model_type = model_info.get("type", "")
        lang = model_info.get("lang", "")
        dataset = model_info.get("dataset", "")
        model = model_info.get("model", "")

        if model_type not in models_dict["tts_models"]:
            models_dict["tts_models"][model_type] = {}

        if lang not in models_dict["tts_models"][model_type]:
            models_dict["tts_models"][model_type][lang] = {}

        if dataset not in models_dict["tts_models"][model_type][lang]:
            models_dict["tts_models"][model_type][lang][dataset] = {}

        models_dict["tts_models"][model_type][lang][dataset][model] = model_info

    return models_info

def get_dataset_for_model(selected_model_name, models_info):
    # Iterate through the loaded models_info to find the matching dataset
    matching_dataset = None
    for model_info in models_info:
        if model_info["model"] == selected_model_name:
            matching_dataset = model_info["dataset"]
            break

    return matching_dataset

# Global variables to store the selected type, language, and dataset
selected_type = ""
selected_language = ""
selected_dataset = ""

def list_languages_by_type(type):
    return sorted(set(model_info["lang"] for model_info in models_info if model_info["type"] == type))

def update_languages(event):
    global selected_type, selected_language, selected_dataset  # Declare global to modify the global variables

    selected_type = type_combobox.get()

    # Get all languages for the selected type
    all_languages = list_languages_by_type(selected_type)

    # Update the language_combobox with the list of languages
    language_combobox['values'] = all_languages

    if all_languages:
        # Set the default language
        language_combobox.set(all_languages[0])

        # Trigger the update_models function
        update_models(None)
    else:
        # Clear the language_combobox
        language_combobox.set("")
        # Clear the model_combobox
        model_combobox.set("")
        update_generate_button_state()

def update_models(event):
    global selected_language, selected_dataset  # Declare global to modify the global variables

    selected_language = language_combobox.get()

    # Get all models for the selected type and language
    all_models = [model_info["model"] for model_info in models_info
                  if model_info["type"] == selected_type and model_info["lang"] == selected_language]

    # Update the model_combobox with the list of models
    model_combobox['values'] = all_models

    # Set the default model or clear if no models
    model_combobox.set(all_models[0] if all_models else "")

    # Get the dataset for the selected model
    selected_model_name = model_combobox.get()
    selected_dataset = get_dataset_for_model(selected_model_name, models_info)

    update_generate_button_state()

def select_output_path():
    output_path = filedialog.askdirectory()
    if output_path:
        output_path_entry.delete(0, END)  # Clear the entry widget
        output_path_entry.insert(0, output_path)  # Insert the selected path into the entry widget
    update_generate_button_state()

def update_generate_button_state():
    # Enable the "Generate" button only if both output path, file name, type, language, and dataset are provided
    output_path = output_path_entry.get()
    file_name = file_name_entry.get()
    type_selected = bool(selected_type)  # Check if a type is selected
    language_selected = bool(selected_language)  # Check if a language is selected
    model_selected = bool(model_combobox.get())  # Check if a model is selected
    generate_button["state"] = "normal" if output_path and file_name and type_selected and language_selected and model_selected else "disabled"

def tts():
    global selected_type, selected_language, selected_dataset

    selected_model = model_combobox.get()
    output_filename = file_name_entry.get()
    output_path = output_path_entry.get()

    # Construct the full model name
    full_model_name = f"{selected_type}/{selected_language}/{selected_dataset}/{selected_model}"

    # Init TTS with the target model name
    tts = TTS(model_name=full_model_name)

    # Run TTS
    text_to_speak = text_entry.get("1.0", "end-1c")  # Get the text from the Text widget
    output_file_path = os.path.join(output_path, f"{output_filename}.wav")
    tts.tts_to_file(text=text_to_speak, file_path=output_file_path)

# GUI code
root = tk.Tk()
root.title("Coqui GUI")
root.minsize(650, 700)  # Adjusted minsize

if __name__ == "__main__":
    # Load models_info before using it
    models_info = load_models_info_from_file()

# Text entry using the Text widget
label_text = Label(master=root, text="Text", fg="#FFFFFF", font=("Arial", 20))
label_text.place(x=5, y=150, width=80, height=20)
text_entry = tk.Text(root, wrap="word", width=40, height=10)
text_entry.place(x=100, y=10, width=500, height=300)

# Scrollbar for the text entry
scrollbar = Scrollbar(root, command=text_entry.yview)
scrollbar.place(x=600, y=10, height=300)
text_entry.config(yscrollcommand=scrollbar.set)

# Choose the Type
label_type = Label(master=root, text="Type", fg="#FFFFFF", font=("Arial", 18))
label_type.place(x=5, y=323, width=80, height=20)
types = sorted(set(model_info["type"] for model_info in models_info))
type_combobox = ttk.Combobox(root, values=types, state="readonly")
type_combobox.set(types[0] if types else "")
type_combobox.place(x=100, y=320, width=100, height=30)
type_combobox.bind("<<ComboboxSelected>>", update_languages)

# Choose the language
label_language = Label(master=root, text="Language", fg="#FFFFFF", font=("Arial", 18))
label_language.place(x=250, y=323, width=100, height=20)
languages = []  # Will be populated dynamically
language_combobox = ttk.Combobox(root, values=languages, state="readonly")
language_combobox.set(languages[0] if languages else "")
language_combobox.place(x=350, y=320, width=200, height=30)
language_combobox.bind("<<ComboboxSelected>>", update_models)

# Models for the Language
label_model = Label(master=root, text="Model", fg="#FFFFFF", font=("Arial", 18))
label_model.place(x=250, y=363, width=100, height=20)
models = []
model_combobox = ttk.Combobox(root, values=models, state="readonly")
model_combobox.set(models[0] if models else "")
model_combobox.place(x=350, y=360, width=200, height=30)

# File name entry
label_filename = Label(master=root, text="File Name", fg="#FFFFFF", font=("Arial", 18))
label_filename.place(x=5, y=403, width=100, height=20)
file_name_entry = tk.Entry(root, width=20)
file_name_entry.place(x=120, y=400, width=150, height=30)

# Output path entry
label_output_path = Label(master=root, text="Output Path", fg="#FFFFFF", font=("Arial", 18))
label_output_path.place(x=5, y=333, width=100, height=20)
output_path_entry = tk.Entry(root, width=70)
output_path_entry.place(x=120, y=430, width=430, height=30)

# Browse button
browse_button = tk.Button(root, text="Browse", command=select_output_path)
browse_button.place(x=560, y=430, width=70, height=30)

# Generate button
generate_button = tk.Button(root, text="Generate", command=tts, state="disabled")
generate_button.place(x=5, y=660, width=100, height=30)

root.mainloop()
