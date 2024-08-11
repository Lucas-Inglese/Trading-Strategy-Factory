# Trading Strategy Factory

**Trading Strategy Factory** is a Python codebase designed to assist you at any stage of your quant trading journey: from data import to live trading, including robustness testing... (All the possibilities are detailed here.)

## Setup the Environment

After completing the setup, you should be able to run any code from this repository, which contains only Python code.

### 🔹 Install the Necessary Software

- **Python version used**: Python 3.10
- **MetaTrader 5 version**: Use the latest available [MetaQuotes](https://www.metaquotes.net/)

### 🔹 Create a New Environment

Depending on the platform you are using to code, you can create a new environment without using any commands. If you're unsure how to do this, you can create it directly in the terminal using the following command:

```bash
python -m venv environment_name
```

### 🔹 Install the Requirements
Select the appropriate environment and install the required dependencies for this project. Note: You need a Windows environment as the MetaTrader5 library only works on Windows.
```bash
pip install -r requirements.txt
```


### 🔹 Add Path to the Interpreter
You need to add the path to your folder in the interpreter path. The best option is to use software like PyCharm, which allows you to easily add a new path to your interpreter.
If you're unable to add the path using a software, you need to add this code at the beginning of each file you run (be sure to use the correct path to the folder):
```py
import sys
sys.path.append('/path/to/the/folder/Trading-Strategy-Factory')
```
