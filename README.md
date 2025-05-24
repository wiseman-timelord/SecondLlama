# SecondLlama
Status - Alpha (not working)

# Description:
Its secondlife, its llama, its time!!...Testing Jules, I intend to make the complete program with Jules, with, a lot of decisions and some editing, by me, and some back and forth with deepseek/grok with notepad++. Dunno what will happen or if its even possible, we will see.

# Development:
- Here is the original prompt...
```
To create a program, that uses the llama 3.x models, in gguf and that feature image recognition, to be able to identify and read the chat log in a SecondLife window, and given configuration of the username...

- it will keep note people whom mention the name, for a period of time, like 10 minutes, with a higher assumption they are talking to the user.
- it must have a prompt between responses in which it assesses if people are likely talking to the user or not.
- it should also assess conversations in the chat, and occasionally produce input into the conversation, enumerating conversation from the topics discussed.
- So its sortoff an auto-responder or chat-bot.
- answers should be around the length of the average communication interaction between others, so batch size should auto-adjust to match average message length.
- also possibly if the user opens the direction controls, then it should be able to identify this, and logically click on directions to move and turns left/right, as it deems appropriate.
- the amount of text wont be such an issue as the number of different people talking, so possibly generation of logs for each individual avatar should be kept, in order to understand the context of the specific people the chatbot is talking to. It should also have a maximum of like 3 people it should plan to talk to at any given time, and it would read all up to 3 peoples inputs in one, to get best context on the response.
so, mouse/keyboard input will be important too.
```
- here are some other bits of information...
```
- downloads should be to .\temp, while the extracted files should be in .\data\llama-box\avx2 and .\data\llama-box\vulkan.
- dont install llama-cpp-python, unless we need it, or can use it to enable the program to detect settings, that will then be used in llama-box, or possibly we should use gguf (library) for such purposes, I think that would be better given the context, but only if we need it for something.
- lets make it configurable, so that the user can switch processing method, because, even though it may fit it, it may not leave enough gpu ram, and then secondlife may have issues. a choice between the hardware I potentially will use, we have 2 pre-compiled binaries to include, `https://github.com/gpustack/llama-box/releases/download/v0.0.147/llama-box-windows-amd64-avx2.zip`, `https://github.com/gpustack/llama-box/releases/download/v0.0.147/llama-box-windows-amd64-vulkan-1.4.zip`.
```

# Requirements: 
Platform: Windows 10 non-wsl with python 3.12+ Hardware AMD GPU 8GB rx 470 (NON-ROCM).

# File Structure: 
Here is how the files are organised...
```
.\launcher.py  (entry point for program)
.\README.md  (documentation for github)
.\SecondLlama.bat  (batch menu to run installer/launcher)
.\data
.\data\persistent.json  (persistent settings)
.\data\llama-box\*  (pre-compiled binaries)
.\scripts
.\scripts\configure.py  (application configuration)
.\scripts\interface.py  (program interface (text))
.\scripts\models.py  (llama-box and model handling)
.\scripts\prompts.py  (LLM Prompt Management)
.\scripts\temporary.py  (runtime state management)
.\scripts\utilities.py  (common helper function)
```
