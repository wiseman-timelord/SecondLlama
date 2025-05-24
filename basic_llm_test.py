# Basic GGUF Model Test Script for llama-cpp-python on Windows with AMD GPU (Vulkan)
#
# Prerequisites:
# 1. Python 3.12+
# 2. C++ Compiler:
#    - Visual Studio Community Edition: Install with the "Desktop development with C++" workload.
#      (Make sure cl.exe is in your PATH, usually by running from "x64 Native Tools Command Prompt for VS")
#    - OR MinGW-w64: Ensure g++/gcc are in your PATH.
#
# Installation Instructions:
#
# 1. Install essential Python libraries:
#    pip install llama-cpp-python huggingface-hub
#
# 2. Attempt Installation with Vulkan GPU Support (Recommended for AMD GPUs):
#    Open PowerShell or Command Prompt.
#    For PowerShell:
#      $env:CMAKE_ARGS = "-DGGML_VULKAN=on"
#      pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python
#
#    For Command Prompt (cmd.exe):
#      set CMAKE_ARGS=-DGGML_VULKAN=on
#      pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python
#
#    Verification: After installation, run python and try `import llama_cpp`.
#                  Look for "VULKAN" in the llama.cpp build information output.
#
# 3. Install for CPU-Only Support (If Vulkan fails or is not desired):
#    If the Vulkan build has issues, or you prefer CPU, uninstall first (optional but recommended):
#      pip uninstall llama-cpp-python
#    Then install the standard CPU version:
#      pip install --upgrade --force-reinstall --no-cache-dir llama-cpp-python
#
#    (Note: This CPU build won't use specific BLAS libraries like OpenBLAS initially
#     to minimize external dependencies for this basic test. For better CPU performance
#     on production systems, consider a build with OpenBLAS or another BLAS library.)

import os
import time
try:
    from llama_cpp import Llama, LlamaGrammarException # LlamaGrammarException for more specific error handling if needed
    is_llama_cpp_installed = True
except ImportError:
    print("llama-cpp-python is not installed. Please follow the installation instructions in the script preamble.")
    print("Attempting to install with CPU support as a fallback to run the script...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "llama-cpp-python"])
        from llama_cpp import Llama, LlamaGrammarException
        is_llama_cpp_installed = True
        print("llama-cpp-python installed successfully (CPU support). Please re-run the script.")
        print("For GPU support, please stop this script and follow the GPU installation instructions in the preamble.")
    except Exception as e:
        print(f"Failed to automatically install llama-cpp-python: {e}")
        print("Please install it manually based on the instructions in the script preamble.")
        is_llama_cpp_installed = False
    exit() # Exit after attempting install, user should re-run

try:
    from huggingface_hub import hf_hub_download
    is_huggingface_hub_installed = True
except ImportError:
    print("huggingface-hub is not installed. Please install it using: pip install huggingface-hub")
    is_huggingface_hub_installed = False
    # Attempt to install
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface-hub"])
        from huggingface_hub import hf_hub_download
        is_huggingface_hub_installed = True
        print("huggingface-hub installed successfully. Please re-run the script.")
    except Exception as e:
        print(f"Failed to automatically install huggingface-hub: {e}")
    exit()

# Script Parameters
USE_VULKAN_IF_AVAILABLE = True  # Set to False to force CPU-only mode for testing
MODEL_REPO_ID = "Qwen/Qwen2-0.5B-Instruct-GGUF"
MODEL_FILENAME_GLOB = "*q4_0.gguf" # Small model, ~270MB, Q4_0 quantized
MODELS_DIR = "./models"

def main():
    if not is_llama_cpp_installed or not is_huggingface_hub_installed:
        print("Exiting due to missing critical libraries. Please see messages above and install them.")
        return

    print(f"Attempting to use llama-cpp-python version: {getattr(Llama, '__version__', 'unknown')}")
    print(f"Running with Python version: {os.sys.version}")


    # --- 1. Model Definition and Download ---
    print(f"\n--- Model Setup ---")
    print(f"Target model repository: {MODEL_REPO_ID}")
    print(f"Target model filename pattern: {MODEL_FILENAME_GLOB}")
    print(f"Local models directory: {os.path.abspath(MODELS_DIR)}")

    if not os.path.exists(MODELS_DIR):
        try:
            os.makedirs(MODELS_DIR)
            print(f"Created models directory: {os.path.abspath(MODELS_DIR)}")
        except OSError as e:
            print(f"Error creating models directory {MODELS_DIR}: {e}")
            return

    model_path = ""
    try:
        print(f"Downloading model '{MODEL_FILENAME_GLOB}' from '{MODEL_REPO_ID}'...")
        # hf_hub_download expects a specific filename, not a glob.
        # We need to list files and pick one if a glob is used, or use a known good filename.
        # For this example, Qwen/Qwen2-0.5B-Instruct-GGUF has 'qwen2-0.5b-instruct-q4_0.gguf'
        # Let's adjust filename_glob to be the exact filename for simplicity here.
        # If truly dynamic globbing is needed, huggingface_hub.list_repo_files would be used first.
        exact_model_filename = "qwen2-0.5b-instruct-q4_0.gguf" # Specific file for this repo
        if MODEL_FILENAME_GLOB != "*q4_0.gguf" and MODEL_FILENAME_GLOB != exact_model_filename :
             print(f"Warning: MODEL_FILENAME_GLOB ('{MODEL_FILENAME_GLOB}') seems specific. Overriding with known good filename '{exact_model_filename}' for stability of this script for {MODEL_REPO_ID}.")
        
        # Check if we really mean the glob or the specific filename for this known model
        # For this specific model, we know the filename.
        if MODEL_REPO_ID == "Qwen/Qwen2-0.5B-Instruct-GGUF" and MODEL_FILENAME_GLOB == "*q4_0.gguf":
            target_filename_for_download = "qwen2-0.5b-instruct-q4_0.gguf"
            print(f"Adjusted filename for download to: {target_filename_for_download} (specific for {MODEL_REPO_ID})")
        else:
            target_filename_for_download = MODEL_FILENAME_GLOB # Use as is if user changed it. May fail if it's a real glob.
            if "*" in target_filename_for_download or "?" in target_filename_for_download:
                print(f"Warning: MODEL_FILENAME_GLOB ('{target_filename_for_download}') looks like a glob pattern. ")
                print(f"hf_hub_download requires an exact filename. This may fail.")
                print(f"Consider using a more specific filename from the Hugging Face Hub repo page for {MODEL_REPO_ID}.")


        model_path = hf_hub_download(
            repo_id=MODEL_REPO_ID,
            filename=target_filename_for_download, # Use the adjusted filename
            local_dir=MODELS_DIR,
            local_dir_use_symlinks=False # Recommended for Windows to avoid issues
        )
        print(f"Model downloaded to: {model_path}")
    except Exception as e:
        print(f"Error downloading model: {e}")
        print("Please check your internet connection and the model repository details.")
        print("If using a glob, ensure it resolves to a unique downloadable file on the Hub or specify an exact filename.")
        return

    if not os.path.exists(model_path):
        print(f"Model file was reported as downloaded but not found at: {model_path}")
        return

    # --- 2. LLM Initialization and Inference ---
    print(f"\n--- LLM Initialization ---")
    llm = None
    attempt_vulkan = USE_VULKAN_IF_AVAILABLE

    if attempt_vulkan:
        print("Attempting to initialize LLM with Vulkan GPU support...")
        try:
            llm = Llama(
                model_path=model_path,
                n_gpu_layers=-1,  # Offload all possible layers to GPU
                verbose=True,
                # n_ctx=2048 # Example: Set context size if needed, defaults usually fine for small models
            )
            print("LLM initialized successfully with GPU (Vulkan) support.")
            # Quick check if GPU was actually used (n_gpu_layers > 0 in practice)
            # llama.cpp prints this, but we can check the object if it exposes this info.
            # For now, verbose=True output from llama.cpp itself is the primary indicator.
        except Exception as e: # Broad exception to catch various init failures
            print(f"ERROR: GPU (Vulkan) initialization failed: {e}")
            print("This could be due to several reasons:")
            print("  - llama-cpp-python not compiled with Vulkan support (see script preamble).")
            print("  - Vulkan drivers not installed correctly or outdated.")
            print("  - GPU not having enough VRAM for the model (even small ones can be an issue).")
            print("  - Other system-specific Vulkan issues.")
            print("Falling back to CPU-only mode.")
            llm = None # Ensure llm is None before CPU attempt
    
    if llm is None: # Either Vulkan was not attempted or it failed
        print("Initializing LLM with CPU-only support...")
        try:
            llm = Llama(
                model_path=model_path,
                n_gpu_layers=0,   # CPU only
                verbose=True
            )
            print("LLM initialized successfully in CPU-only mode.")
        except Exception as e:
            print(f"CRITICAL ERROR: CPU initialization failed: {e}")
            print("This is unexpected for CPU mode. Common causes:")
            print("  - Corrupted model file.")
            print("  - Fundamental issue with llama-cpp-python installation (even for CPU).")
            print("  - Insufficient system RAM (less likely for CPU init itself, but for loading).")
            print("Please review the error and installation steps.")
            return

    # --- 3. Text Generation ---
    print(f"\n--- Text Generation ---")
    prompt = "Q: Write a short story about a curious cat exploring a mysterious attic. A:"
    print(f"Prompt: {prompt}")

    try:
        print("Generating text...")
        start_time = time.time()

        output = llm(
            prompt,
            max_tokens=150,       # Max new tokens to generate
            stop=["Q:", "\n\n"],  # Stop sequences for Q&A or story end
            echo=True             # Echo the prompt in the output
        )
        
        end_time = time.time()
        time_taken = end_time - start_time

        print("\n--- LLM Output ---")
        if output and 'choices' in output and output['choices']:
            full_text = output['choices'][0]['text']
            print(full_text)

            # --- 4. Performance ---
            print("\n--- Performance ---")
            prompt_tokens = output['usage']['prompt_tokens']
            completion_tokens = output['usage']['completion_tokens']
            total_tokens = output['usage']['total_tokens']
            
            print(f"Time taken for generation: {time_taken:.2f} seconds")
            print(f"Prompt tokens: {prompt_tokens}")
            print(f"Completion tokens (generated): {completion_tokens}")
            print(f"Total tokens: {total_tokens}")
            if time_taken > 0 and completion_tokens > 0:
                tokens_per_second = completion_tokens / time_taken
                print(f"Tokens per second (completion): {tokens_per_second:.2f} T/s")
            else:
                print("Not enough data for tokens per second calculation.")

        else:
            print("No output or unexpected output format from LLM.")
            print(f"Raw output: {output}")

    except LlamaGrammarException as e: # More specific error if using grammars
        print(f"Error during text generation (grammar related): {e}")
    except Exception as e:
        print(f"Error during text generation: {e}")

if __name__ == "__main__":
    if not (is_llama_cpp_installed and is_huggingface_hub_installed):
        print("Script cannot run due to missing libraries. Please install them as per the instructions at the top of the script.")
    else:
        main()
    print("\nScript finished.")
    print("If you had issues with GPU, ensure your CMAKE_ARGS were set correctly during llama-cpp-python install,")
    print("and that your AMD drivers and Vulkan SDK are up to date.")

# End of script
