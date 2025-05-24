import os
import sys
import subprocess
import json
import urllib.request
import zipfile

# --- Configuration ---
VENV_DIR = "./venv"
TEMP_DIR = "./temp" # For downloads
DATA_DIR = "./data"
MODELS_DIR = os.path.join(DATA_DIR, "models")
LLAMA_BOX_DIR = os.path.join(DATA_DIR, "llama-box")
LLAMA_BOX_AVX2_DIR = os.path.join(LLAMA_BOX_DIR, "avx2")
LLAMA_BOX_VULKAN_DIR = os.path.join(LLAMA_BOX_DIR, "vulkan")
SCRIPTS_DIR = "./scripts"
CONFIG_FILE_PATH = os.path.join(DATA_DIR, "persistent.json") # Changed filename

DEFAULT_CONFIG = {
    "username": "User",
    "llm_engine": "llama-box", # New
    "llm_processing_method": "vulkan", # New: 'vulkan' or 'cpu'
    "llama_box_vulkan_path": os.path.join(LLAMA_BOX_VULKAN_DIR, "llama-box.exe").replace("\\", "/"), # New
    "llama_box_cpu_path": os.path.join(LLAMA_BOX_AVX2_DIR, "llama-box.exe").replace("\\", "/"), # New
    "llm_model_repo_id": "Qwen/Qwen2-0.5B-Instruct-GGUF", # For GGUF model download
    "llm_model_filename": "qwen2-0.5b-instruct-q4_0.gguf", # For GGUF model download
    "llm_model_path": os.path.join(MODELS_DIR, "qwen2-0.5b-instruct-q4_0.gguf").replace("\\", "/"),
    "ocr_language": "eng",
    "log_level": "INFO"
    # "vulkan_offload": True, # Removed, covered by llm_processing_method and specific paths
}

CORE_DEPENDENCIES = ["huggingface-hub", "Pillow", "pytesseract", "pyautogui"]

# llama-box URLs
LLAMA_BOX_AVX2_URL = "https://github.com/gpustack/llama-box/releases/download/v0.0.147/llama-box-windows-amd64-avx2.zip"
LLAMA_BOX_VULKAN_URL = "https://github.com/gpustack/llama-box/releases/download/v0.0.147/llama-box-windows-amd64-vulkan-1.4.zip"
LLAMA_BOX_AVX2_ZIP_NAME = "llama_box_avx2.zip"
LLAMA_BOX_VULKAN_ZIP_NAME = "llama_box_vulkan.zip"

# --- Helper Functions ---
def get_venv_python_executable():
    """Gets the path to the Python executable within the virtual environment."""
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "python")

def run_subprocess(command, error_message):
    """Runs a subprocess command and handles potential errors."""
    try:
        print(f"Executing: {' '.join(command)}")
        subprocess.check_call(command)
        print(f"Successfully executed: {' '.join(command)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {error_message}")
        print(f"Command failed: {' '.join(command)}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.output}")
        return False
    except FileNotFoundError:
        print(f"ERROR: Command not found. Ensure '{command[0]}' is installed and in PATH.")
        print(f"Failed command: {' '.join(command)}")
        return False

# --- Setup Functions ---

def setup_directories():
    """Creates necessary project directories if they don't exist."""
    print("\n--- Setting up directories ---")
    dirs_to_create = [
        TEMP_DIR, 
        DATA_DIR, 
        MODELS_DIR, 
        LLAMA_BOX_DIR, 
        LLAMA_BOX_AVX2_DIR, 
        LLAMA_BOX_VULKAN_DIR, 
        SCRIPTS_DIR, 
        VENV_DIR
    ]
    for dir_path in dirs_to_create:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                print(f"Created directory: {os.path.abspath(dir_path)}")
            except OSError as e:
                print(f"ERROR: Could not create directory {dir_path}: {e}")
                # Decide if this is fatal or not; for now, continue
        else:
            print(f"Directory already exists: {os.path.abspath(dir_path)}")
    print("Directory setup complete.")

def create_config_file():
    """Creates the default JSON persistent configuration file if it doesn't exist."""
    print("\n--- Creating persistent configuration file ---")
    if os.path.exists(CONFIG_FILE_PATH):
        print(f"Persistent configuration file already exists at: {os.path.abspath(CONFIG_FILE_PATH)}")
        print("Skipping creation to avoid overwriting existing settings.")
    else:
        try:
            # Ensure all paths in default config use forward slashes
            config_to_write = DEFAULT_CONFIG.copy()
            config_to_write["llama_box_vulkan_path"] = os.path.join(LLAMA_BOX_VULKAN_DIR, "llama-box.exe").replace("\\", "/")
            config_to_write["llama_box_cpu_path"] = os.path.join(LLAMA_BOX_AVX2_DIR, "llama-box.exe").replace("\\", "/")
            config_to_write["llm_model_path"] = os.path.join(MODELS_DIR, config_to_write["llm_model_filename"]).replace("\\", "/")
            
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(config_to_write, f, indent=2)
            print(f"Default persistent configuration file created at: {os.path.abspath(CONFIG_FILE_PATH)}")
        except IOError as e:
            print(f"ERROR: Could not create persistent configuration file {CONFIG_FILE_PATH}: {e}")
    print("Persistent configuration file setup complete.")


def install_dependencies():
    """Handles virtual environment creation and installation of Python dependencies."""
    print("\n--- Installing Dependencies ---")

    # 1. Prerequisites Information
    print("\n** Prerequisites **")
    print("- Python 3.12+ (You are running this script, so Python is present)")
    # C++ Compiler prerequisite removed as llama-cpp-python is no longer installed by default.
    print("- Tesseract OCR: Please ensure Tesseract OCR is installed and its installation directory (containing tesseract.exe) is in your system's PATH.")
    print("  Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("- Vulkan SDK (Optional, for llama-box Vulkan): If you plan to use llama-box with Vulkan, ensure the Vulkan SDK is installed and your graphics drivers are up to date.")
    print("  Vulkan SDK: https://vulkan.lunarg.com/sdk/home")


    # 2. Virtual Environment Setup
    print("\n** Virtual Environment Setup **")
    venv_python_exe = get_venv_python_executable()
    
    if not os.path.exists(os.path.join(VENV_DIR, "pyvenv.cfg")): # A more reliable check for venv existence
        print(f"Creating virtual environment in ./{VENV_DIR}...")
        if not run_subprocess([sys.executable, "-m", "venv", VENV_DIR], "Failed to create virtual environment."):
            print("CRITICAL: Virtual environment creation failed. Cannot proceed with dependency installation.")
            return False # Indicate failure
        print(f"Virtual environment created. Path: {os.path.abspath(VENV_DIR)}")
    else:
        print(f"Virtual environment already exists at: {os.path.abspath(VENV_DIR)}")

    print(f"Important: Subsequent scripts should ideally be run using the Python interpreter from this virtual environment: {os.path.abspath(venv_python_exe)}")
    print("The SecondLlama.bat launcher (if used) should handle venv activation.")

    # 3. Python Libraries Installation (Core)
    print("\n** Installing Core Python Libraries into Virtual Environment **")
    if not os.path.exists(venv_python_exe):
        print(f"ERROR: Virtual environment Python executable not found at {venv_python_exe}. Cannot install packages.")
        return False

    for package in CORE_DEPENDENCIES:
        print(f"\nInstalling {package}...")
        if not run_subprocess([venv_python_exe, "-m", "pip", "install", package], f"Failed to install {package}."):
            print(f"Warning: Could not install {package}. Some features may not work.")
            # Decide if this is fatal or allow continuation
    
    # llama-cpp-python installation removed. llama-box is a pre-compiled executable.

    print("\nCore Python dependency installation phase complete.")
    return True # Indicate success

def download_and_extract_llama_box():
    """Downloads and extracts llama-box.exe for AVX2 and Vulkan."""
    print("\n--- Downloading and Extracting llama-box ---")

    files_to_download = [
        {"url": LLAMA_BOX_AVX2_URL, "zip_name": LLAMA_BOX_AVX2_ZIP_NAME, "extract_dir": LLAMA_BOX_AVX2_DIR, "exe_name": "llama-box.exe", "desc": "AVX2 (CPU)"},
        {"url": LLAMA_BOX_VULKAN_URL, "zip_name": LLAMA_BOX_VULKAN_ZIP_NAME, "extract_dir": LLAMA_BOX_VULKAN_DIR, "exe_name": "llama-box.exe", "desc": "Vulkan (GPU)"}
    ]

    for item in files_to_download:
        url = item["url"]
        zip_name = item["zip_name"]
        extract_dir = item["extract_dir"]
        exe_name = item["exe_name"]
        desc = item["desc"]
        
        zip_path = os.path.join(TEMP_DIR, zip_name)
        exe_path = os.path.join(extract_dir, exe_name)

        print(f"\nChecking for llama-box ({desc}) at {os.path.abspath(exe_path)}...")
        if os.path.exists(exe_path):
            print(f"llama-box.exe for {desc} already exists. Skipping download and extraction.")
            continue

        # Download
        print(f"Downloading {desc} version from {url} to {os.path.abspath(zip_path)}...")
        try:
            # Create User-Agent to avoid potential blocking
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
                data = response.read() # Read all data from response
                out_file.write(data)
            print(f"Successfully downloaded {zip_name}.")
        except urllib.error.URLError as e:
            print(f"ERROR: Failed to download {zip_name}: {e.reason}")
            print("Please check your internet connection and the URL. Skipping this version.")
            continue
        except Exception as e:
            print(f"ERROR: An unexpected error occurred during download of {zip_name}: {e}")
            continue
            
        # Extraction
        print(f"Extracting {exe_name} from {os.path.abspath(zip_path)} to {os.path.abspath(extract_dir)}...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check if exe_name is in the zip file before extracting
                if exe_name not in zip_ref.namelist():
                    print(f"ERROR: '{exe_name}' not found in '{zip_name}'. Archive contents: {zip_ref.namelist()}")
                    # Attempt to find any .exe if the name is different (simple heuristic)
                    found_exe = None
                    for name_in_zip in zip_ref.namelist():
                        if name_in_zip.lower().endswith(".exe"):
                            found_exe = name_in_zip
                            print(f"Found alternative EXE: '{found_exe}'. Attempting to extract it as '{exe_name}'.")
                            break
                    if found_exe:
                        zip_ref.extract(found_exe, extract_dir)
                        # Rename it to the expected exe_name if different
                        if found_exe != exe_name:
                            os.rename(os.path.join(extract_dir, found_exe), exe_path)
                        print(f"Successfully extracted '{found_exe}' as '{exe_name}' to {extract_dir}.")
                    else:
                        print(f"No suitable .exe found in {zip_name}. Skipping extraction for {desc}.")
                        continue
                else: # Expected exe_name is found
                    zip_ref.extract(exe_name, extract_dir)
                    print(f"Successfully extracted {exe_name} to {extract_dir}.")

            # Optional: Delete the zip file after successful extraction
            # print(f"Deleting temporary file {zip_path}...")
            # os.remove(zip_path)

        except zipfile.BadZipFile:
            print(f"ERROR: Failed to open zip file '{zip_name}'. It might be corrupted or not a zip file.")
        except FileNotFoundError:
            print(f"ERROR: Zip file '{zip_name}' not found for extraction. Download may have failed.")
        except Exception as e:
            print(f"ERROR: An unexpected error occurred during extraction of {zip_name}: {e}")

    print("\nlama-box download and extraction phase complete.")
    return True


def download_llm_model():
    """Downloads the LLM model specified in the persistent configuration file."""
    print("\n--- Downloading LLM Model ---")
    
    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"ERROR: Persistent configuration file not found at {CONFIG_FILE_PATH}. Cannot determine which model to download.")
        print("Please run the persistent configuration file creation step first.")
        return False

    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not read or parse persistent configuration file {CONFIG_FILE_PATH}: {e}")
        return False

    repo_id = config.get("llm_model_repo_id")
    filename = config.get("llm_model_filename")
    model_path_config = config.get("llm_model_path") # Path from config

    if not repo_id or not filename:
        print("ERROR: llm_model_repo_id or llm_model_filename not found in config file.")
        return False

    # Construct the expected local path based on MODELS_DIR and filename for verification
    expected_local_model_path = os.path.join(MODELS_DIR, filename)

    if os.path.exists(expected_local_model_path):
        print(f"Model file '{filename}' already exists at: {os.path.abspath(expected_local_model_path)}")
        # Verify if the path in config matches the actual location
        if os.path.abspath(model_path_config) != os.path.abspath(expected_local_model_path):
            print(f"Warning: Model path in persistent config ('{model_path_config}') does not match expected path ('{expected_local_model_path}').")
            print(f"Consider updating persistent.json if '{expected_local_model_path}' is the correct location.")
        print("Skipping download.")
        return True # Model exists

    print(f"Attempting to download '{filename}' from repository '{repo_id}' to '{os.path.abspath(MODELS_DIR)}'.")

    try:
        from huggingface_hub import hf_hub_download
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=MODELS_DIR,
            local_dir_use_symlinks=False, # Important for Windows
            resume_download=True,
        )
        print(f"Model downloaded successfully: {os.path.abspath(downloaded_path)}")
        
        # Update config with the actual downloaded path if it's different (though it should match expected_local_model_path)
        # Ensure path in config is using forward slashes for consistency
        normalized_downloaded_path = downloaded_path.replace("\\", "/")
        if config.get("llm_model_path") != normalized_downloaded_path:
            config["llm_model_path"] = normalized_downloaded_path
            try:
                with open(CONFIG_FILE_PATH, 'w') as f:
                    json.dump(config, f, indent=2)
                print(f"Persistent configuration file updated with model path: {normalized_downloaded_path}")
            except IOError as e:
                print(f"Warning: Could not update persistent configuration file with new model path: {e}")
        return True
    except ImportError:
        print("ERROR: huggingface-hub library is not installed. This should have been installed in the previous step.")
        print("Please ensure dependencies are installed correctly.")
        return False
    except Exception as e: # Catching a broader range of hf_hub_download errors
        print(f"ERROR: Failed to download model '{filename}' from '{repo_id}':")
        print(e)
        print("Please check your internet connection, model repository details, and Hugging Face Hub token if required for private models.")
        return False


# --- Main Execution ---
def main():
    print("Starting SecondLlama Project Installer...")
    print(f"Running with Python: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")

    setup_directories()
    create_config_file() 

    if not install_dependencies():
        print("\nCore Python dependency installation failed. Some parts of the setup might be incomplete.")
        print("Please review the error messages above and try to resolve them.")
        # Not returning, as user might want to proceed with llama-box and model download

    if not download_and_extract_llama_box():
        print("\nlama-box download or extraction failed for one or more versions.")
        print("The LLM engine might not be available.")

    if not download_llm_model(): # For GGUF models
        print("\nLLM GGUF Model download failed or was skipped due to issues.")
        print("The application might not function correctly without the GGUF model for llama-box.")
    
    print("\n--- Installation Complete ---")
    print("Next steps:")
    print("1. If you encountered errors, please review the messages above.")
    print(f"2. Ensure Tesseract OCR is installed and its directory is in your system PATH (mentioned in prerequisites).")
    print(f"3. If using llama-box with Vulkan, ensure Vulkan SDK is installed and drivers are up-to-date.")
    print(f"4. You can now try running the main application, for example, using a launcher script like 'SecondLlama.bat' (if available),")
    print(f"   which should handle activating the virtual environment ({os.path.abspath(VENV_DIR)}).")
    print(f"   Or, activate manually: cd .\\{VENV_DIR}\\Scripts && activate && cd ..\\.. && python your_main_script.py") # Adjust for your main script

if __name__ == "__main__":
    main()
    print("\nInstaller script finished.")
