import json
from TTS.api import TTS
import torch

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

def save_models_info_to_file(file_path="models_info.json"):
    tts_manager = TTS().list_models()
    all_models = tts_manager.list_models()

    model_types = sorted(set(model_info.split("/")[0] for model_info in all_models))
    print("Available Model Types:")
    for i, model_type in enumerate(model_types, start=1):
        print(f"{i}. {model_type}")

    model_type_choices = input("Select Model Types (enter the corresponding numbers separated by commas): ")
    model_type_choices = [int(choice.strip()) for choice in model_type_choices.split(",")]
    selected_model_types = [model_types[i - 1] for i in model_type_choices]

    languages = sorted(set(model_info.split("/")[1] for model_info in all_models if model_info.startswith(tuple(selected_model_types))))
    print(f"\nAvailable Languages:")
    for i, lang in enumerate(languages, start=1):
        print(f"{i}. {lang}")

    lang_choices = input("Select Languages (enter the corresponding numbers separated by commas): ")
    lang_choices = [int(choice.strip()) for choice in lang_choices.split(",")]
    selected_languages = [languages[i - 1] for i in lang_choices]

    models_info = []
    for model_info in all_models:
        model_type, lang, dataset, model = model_info.split("/")
        if model_type in selected_model_types and lang in selected_languages:
            model_item = {
                "type": model_type,
                "lang": lang,
                "dataset": dataset,
                "model": model,
            }
            models_info.append(model_item)

    with open(file_path, "w") as file:
        json.dump(models_info, file)

    print("\nSelected Model Parameters:")
    print("Model Types:", selected_model_types)
    print("Languages:", selected_languages)

    download_all = input("Do you want to download all models for the selected parameters? (y/n): ").lower() == 'y'

    # Download selected models
    for model_info in models_info:
        full_model_name = f"{model_info['type']}/{model_info['lang']}/{model_info['dataset']}/{model_info['model']}"
        if download_all or input(f"Do you want to download the model '{full_model_name}'? (y/n): ").lower() == 'y':
            tts = TTS(model_name=full_model_name, progress_bar=True).to(device)
            print(f"Downloading model: {full_model_name}")

if __name__ == "__main__":
    save_models_info_to_file()
