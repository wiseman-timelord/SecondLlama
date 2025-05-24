import os
import sys
import subprocess
import json

# --- Configuration ---
VENV_DIR = "./venv"
DATA_DIR = "./data"
MODELS_DIR = os.path.join(DATA_DIR, "models")
SCRIPTS_DIR = "./scripts"
CONFIG_FILE_PATH = os.path.join(DATA_DIR, "config.json")

DEFAULT_CONFIG = {
    "username": "User",
    "llm_model_repo_id": "Qwen/Qwen2-0.5B-Instruct-GGUF",
    "llm_model_filename": "qwen2-0.5b-instruct-q4_0.gguf",
    "llm_model_path": os.path.join(MODELS_DIR, "qwen2-0.5b-instruct-q4_0.gguf").replace("\\", "/"), # Ensure forward slashes
    "vulkan_offload": True,
    "ocr_language": "eng",
    "log_level": "INFO"
}

CORE_DEPENDENCIES = ["huggingface-hub", "Pillow", "pytesseract", "pyautogui"]

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
    dirs_to_create = [DATA_DIR, MODELS_DIR, SCRIPTS_DIR, VENV_DIR]
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
    """Creates the default JSON configuration file if it doesn't exist."""
    print("\n--- Creating configuration file ---")
    if os.path.exists(CONFIG_FILE_PATH):
        print(f"Configuration file already exists at: {os.path.abspath(CONFIG_FILE_PATH)}")
        print("Skipping creation to avoid overwriting existing settings.")
    else:
        try:
            # Ensure model path in default config uses correct separators for the current OS
            # and then replace with forward slashes for consistency in the JSON.
            default_model_path = os.path.join(MODELS_DIR, DEFAULT_CONFIG["llm_model_filename"])
            DEFAULT_CONFIG["llm_model_path"] = default_model_path.replace("\\", "/")

            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            print(f"Default configuration file created at: {os.path.abspath(CONFIG_FILE_PATH)}")
        except IOError as e:
            print(f"ERROR: Could not create configuration file {CONFIG_FILE_PATH}: {e}")
    print("Configuration file setup complete.")


def install_dependencies():
    """Handles virtual environment creation and installation of Python dependencies."""
    print("\n--- Installing Dependencies ---")

    # 1. Prerequisites Information
    print("\n** Prerequisites **")
    print("- Python 3.12+ (You are running this script, so Python is present)")
    print("- C++ Compiler: Ensure you have a C++ compiler installed.")
    print("  - Windows: Visual Studio Community Edition with 'Desktop development with C++' workload.")
    print("             (Ensure cl.exe is in your PATH, e.g., by running from a VS Developer Command Prompt).")
    print("  - Windows (Alternative): MinGW-w64 (ensure g++/gcc are in PATH).")
    print("- Tesseract OCR: Please ensure Tesseract OCR is installed and its installation directory (containing tesseract.exe) is in your system's PATH.")
    print("  Download from: https://github.com/UB-Mannheim/tesseract/wiki")

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
    
    # 4. llama-cpp-python Installation
    print("\n** Installing llama-cpp-python **")
    print("llama-cpp-python requires compilation and can be built for CPU or GPU.")
    print("This script will attempt a CPU-only installation by default for broader compatibility.")

    print("\n--- Option 1: CPU Default (Attempting this now) ---")
    print("Installing llama-cpp-python (CPU version)...")
    if not run_subprocess([venv_python_exe, "-m", "pip", "install", "llama-cpp-python"], "Failed to install llama-cpp-python (CPU)."):
        print("ERROR: llama-cpp-python (CPU) installation failed.")
        print("Common issues: Missing C++ compiler, outdated pip/setuptools, or network problems.")
        print("Please ensure a C++ compiler is installed and in your PATH (see prerequisites).")
        print("You can try running 'pip install --upgrade pip setuptools' in your venv first, then retry.")
    else:
        print("llama-cpp-python (CPU) installed successfully into the virtual environment.")

    print("\n--- Option 2: Vulkan GPU Accelerated (Manual Steps for AMD/Intel GPUs) ---")
    print("If you have an AMD or modern Intel GPU and want Vulkan support (recommended for better performance):")
    print("1. Ensure your Vulkan drivers and SDK are installed and up to date (https://vulkan.lunarg.com/sdk/home).")
    print("2. After this script finishes, activate the virtual environment manually:")
    print(f"   - On Windows CMD: .\\{VENV_DIR}\\Scripts\\activate.bat")
    print(f"   - On PowerShell:  .\\{VENV_DIR}\\Scripts\\Activate.ps1")
    print("3. Then, in the activated environment, run the following commands:")
    print("   For PowerShell:")
    print('     $env:CMAKE_ARGS = "-DGGML_VULKAN=on"')
    print(f"     {os.path.basename(venv_python_exe)} -m pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python")
    print("   Alternatively, for Command Prompt (cmd.exe):")
    print('     set CMAKE_ARGS=-DGGML_VULKAN=on')
    print(f"     {os.path.basename(venv_python_exe)} -m pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python")
    print("   (You might need to uninstall the CPU version first: pip uninstall llama-cpp-python)")

    print("\nDependency installation phase complete.")
    return True # Indicate success

def download_llm_model():
    """Downloads the LLM model specified in the config file."""
    print("\n--- Downloading LLM Model ---")
    
    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"ERROR: Configuration file not found at {CONFIG_FILE_PATH}. Cannot determine which model to download.")
        print("Please run the configuration file creation step first.")
        return False

    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not read or parse config file {CONFIG_FILE_PATH}: {e}")
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
            print(f"Warning: Model path in config ('{model_path_config}') does not match expected path ('{expected_local_model_path}').")
            print(f"Consider updating config.json if '{expected_local_model_path}' is the correct location.")
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
                print(f"Configuration file updated with model path: {normalized_downloaded_path}")
            except IOError as e:
                print(f"Warning: Could not update config file with new model path: {e}")
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
    create_config_file() # Creates config with default model path

    # Install dependencies including huggingface_hub
    if not install_dependencies():
        print("\nDependency installation failed. Some parts of the setup might be incomplete.")
        print("Please review the error messages above and try to resolve them.")
        # Optionally, exit here if core dependencies are critical
        # return

    # Download model (uses config created/verified earlier)
    if not download_llm_model():
        print("\nLLM Model download failed or was skipped due to issues.")
        print("The application might not function correctly without the model.")
    
    print("\n--- Installation Complete ---")
    print("Next steps:")
    print("1. If you encountered errors, please review the messages above.")
    print("2. If you want GPU (Vulkan) acceleration for the LLM, follow the manual steps printed during the dependency installation for llama-cpp-python.")
    print(f"3. Ensure Tesseract OCR is installed and its directory is in your system PATH (mentioned in prerequisites).")
    print(f"4. You can now try running the main application, for example, using a launcher script like 'SecondLlama.bat' (if available),")
    print(f"   which should handle activating the virtual environment ({os.path.abspath(VENV_DIR)}).")
    print(f"   Or, activate manually: cd .\\{VENV_DIR}\\Scripts && activate && cd ..\\.. && python your_main_script.py")

if __name__ == "__main__":
    main()
    print("\nInstaller script finished.")
