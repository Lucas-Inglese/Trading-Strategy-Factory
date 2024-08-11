# Trading Strategy Factory
**Trading Strategy Factory** is a Python codebase designed to assist you at any stage of your quant trading journey: from data import to live trading, including robustness testing... (All the possibilities are detailed below.)
![Live Trading Results](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/raw/main/Results/Live%20Trading.png)


<br>

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

### 🔹 MetaTrader 5 Configuration
You can use the MetaQuotes demo account that you will have during your first connection or connect your own demo account to perform your tests.  
**Note**: Do not forget to activate the algorithmic trading authorization.

### 🔹 Run a File
The best way to ensure that everything was set up correctly is to run one of the live trading files.

<br>
<br> 

## Features

- **Data Management**: Import and transform data using the scripts in this [folder](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/tree/main/Data).

- **Features and Target Engineering**: Create new variables focused on specific characteristics using the provided [file](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/blob/main/Quantreo/DataPreprocessing.py).

- **Trading Strategy Structure**: Find examples of how to create your trading strategies within this [folder](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/tree/main/Strategies).

- **Walk-Forward Optimization**: Optimize the parameters of your trading strategies over time using this [class](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/blob/main/Quantreo/WalkForwardOptimization.py). Examples of utilization can be found in the corresponding [folder](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/tree/main/Launching%20(WFO)).
  

- **Robustness Testing**: Use CPCV (Combinatorial Purged Cross Validation) on your trading strategies to calculate the probability of success and the probability of overfitting using this [class](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/blob/main/Quantreo/CombinatorialPurgedCV.py). Examples of utilization are available in this [folder](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/tree/main/Launching%20(CPCV)).

- **Monte Carlo Simulation**: Run Monte Carlo simulations on your trading strategies to test them on generated data using this [class](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/blob/main/Quantreo/MonteCarlo.py). Examples of utilization can be found in the corresponding [folder](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/tree/main/Launching%20(MC)).

- **Live Trading**: Implement strategies that have successfully passed your selection process into live trading by placing your live trading signals in this [files](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/blob/main/Quantreo/LiveTradingSignal.py) and creating similar files as those in this [folder](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/tree/main/LiveTrading).

<br>
<br>

## Backtesting Output
- Result from the walk-forward optimization: more than 10 metrics and the following graphs
![Walk forward](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/blob/main/Results/Walk%20Forward.png)
- Result from the robustness testing: Probability of overfiting, degradation between the train and test sets and the following graphs:
![Robustness testing](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/blob/main/Results/CPCV.png)
- Result from the walk-forward optimization: The 3 following graphs
![Monte Carlo](https://github.com/Lucas-Inglese/Trading-Strategy-Factory/blob/main/Results/Monte%20Carlo%20Simulations.png)
