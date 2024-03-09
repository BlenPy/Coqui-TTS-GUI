import os
import subprocess
import sys
import tkinter as tk
import shlex
import time
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

# Dictionary mapping language codes to available models
language_models = {
    "en": {'tacotron2': "ek1", 
           'tacotron2-DDC': "ljspeech", 
           'tacotron2-DDC_ph': "ljspeech", 
           'glow-tts': "ljspeech",
           'speedy-speech': "ljspeech", 
           'tacotron2-DCA': "ljspeech", 
           'vits': "ljspeech", 
           'vits--neon': "ljspeech",
           'fast_pitch': "ljspeech", 
           'overflow': "ljspeech", 
           'neural_hmm': "ljspeech", 
           'vits': "vctk", 
           'fast_pitch': "vctk",
           'tacotron-DDC': "sam", 
           'capacitron-t2-c50': "blizzard2013", 
           'capacitron-t2-c150_v2': "blizzard2013", 
           'tortoise-v2': "multi-dataset", 
           'jenny': "jenny"
           },
    "de": {'tacotron2-DCA': "thorsten", 
           'thorsten/vits': "thorsten", 
           'tacotron2-DDC': "thorsten", 
           'vits-neon': "css10"
           },
    "multilingual": {"xtts_v2": "multi-dataset", 
                     "xtts_v1.1": "multi-dataset", 
                     "your_tts": "multi-dataset", 
                     "bark": "multi-dataset"
                     }
}


def activate_venv():
    activate_path = os.path.join('/path/of/your/venv', 'bin', 'activate') #change the path to the path of your venv
    cmd = 'echo "Virtual environment activated successfully"'
    activate_cmd = f"source {activate_path} && {cmd}"

    # Activate virtual environment using subprocess.run
    result = subprocess.run(activate_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    print(result.stdout)
    print(result.stderr)


def deactivate_venv():
    # Restart the Python interpreter to deactivate the virtual environment
    python_executable = sys.executable
    os.execl(python_executable, python_executable, *sys.argv)


def update_models(event):
    selected_language = language_combobox.get()
    models = list(language_models[language_combobox.get()].keys()) if language_combobox.get() else []

    # Update the model dropdown menu
    model_combobox["values"] = models

    if models:
        model_combobox.set(models[0])  # Set the default model if models list is not empty
    else:
        model_combobox.set("")  # Set an empty string if models list is empty

    if models:
        model_combobox.set(models[0])

    update_generate_button_state()


def select_output_path():
    output_path = filedialog.askdirectory()
    output_path_entry.delete(0, tk.END)
    output_path_entry.insert(0, output_path)
    update_generate_button_state()


def update_generate_button_state():
    # Enable the "Generate" button only if both output path and file name are provided
    output_path = output_path_entry.get()
    file_name = file_name_entry.get()
    generate_button["state"] = "normal" if output_path and file_name else "disabled"


def tts():
    #Record the start time
    start_time =time.time()

    text = text_entry.get("1.0", "end-1c")
    selected_language = language_combobox.get()
    selected_model = model_combobox.get()
    file_name = file_name_entry.get()
    output_path = output_path_entry.get()

    # Determine the dataset for the selected model
    dataset = language_models[selected_language].get(selected_model, "unknown_dataset")

    # Activate the virtual environment
    activate_path = os.path.join('/path/of/your/venv', 'bin', 'activate') #change the path to the path of your venv
    activate_cmd = f"source {activate_path}"

    # Create the command to run the TTS model in the virtual environment
    tts_command = (
        f"tts --text {shlex.quote(text)} "
        f"--model_name tts_models/{selected_language}/{dataset}/{selected_model} "
        f"--out_path {shlex.quote(os.path.join(output_path, f'{file_name}.wav'))}"
    )

    # Combine the activation command and TTS command
    command = f"{activate_cmd} && {tts_command}"

    # Execute the combined command in the virtual environment
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Record the end time
    end_time = time.time()

    print()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print()

    print(result.stdout)
    print(result.stderr)


# GUI code
root = tk.Tk()
root.title("Coqui GUI")
root.minsize(650,480)

# Automatically activate the virtual environment upon running the script
activate_venv()

# Text entry using the Text widget
labeltext = Label(master=root, text="Text", fg="#FFFFFF", font=("Arial", 20))
labeltext.place(x=5, y=150, width=80, height=20)
text_entry = tk.Text(root, wrap="word", width=40, height=10)
text_entry.place(x=100, y=10, width=500, height=300)

# Scrollbar for the text entry
scrollbar = Scrollbar(root, command=text_entry.yview)
scrollbar.place(x=600, y=10, height=300)
text_entry.config(yscrollcommand=scrollbar.set)

# Choose the language
labellanguage = Label(master=root, text="Language", fg="#FFFFFF", font=("Arial", 18))
labellanguage.place(x=5, y=323, width=80, height=20)
languages = list(language_models.keys())
language_combobox = ttk.Combobox(root, values=languages, state="readonly")
language_combobox.set(languages[0])  # Set the default language
language_combobox.place(x=100, y=320, width=100, height=30)
language_combobox.bind("<<ComboboxSelected>>", update_models)  # Bind the event to update models

# Models for the Language
labelmodel = Label(master=root, text="Model", fg="#FFFFFF", font=("Arial", 18))
labelmodel.place(x=250, y=323, width=100, height=20)
models = language_models[languages[0]].keys() if languages else []
model_combobox = ttk.Combobox(root, values=models, state="readonly")
default_model = next(iter(models), None)  # Get the first model or None if models is empty
model_combobox.set(default_model)  # Set the default model
model_combobox.place(x=350, y=320, width=200, height=30)

# File name entry
label_filename = Label(master=root, text="File Name", fg="#FFFFFF", font=("Arial", 18))
label_filename.place(x=5, y=363, width=100, height=20)
file_name_entry = tk.Entry(root, width=20)
file_name_entry.place(x=120, y=360, width=150, height=30)
file_name_entry.bind("<KeyRelease>", lambda event: update_generate_button_state())

# Output path entry
label_output_path = Label(master=root, text="Output Path", fg="#FFFFFF", font=("Arial", 18))
label_output_path.place(x=5, y=403, width=100, height=20)
output_path_entry = tk.Entry(root, width=70)
output_path_entry.place(x=120, y=400, width=430, height=30)

# Browse button
browse_button = tk.Button(root, text="Browse", command=select_output_path)
browse_button.place(x=560, y=400, width=70, height=30)

# Generate button
generate_button = tk.Button(root, text="Generate", command=tts, state="disabled")
generate_button.place(x=5, y=440, width=100, height=30)

root.protocol("WM_DELETE_WINDOW", deactivate_venv)
root.mainloop()
