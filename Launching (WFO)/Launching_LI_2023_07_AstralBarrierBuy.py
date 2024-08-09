from Strategies.LI_2023_07_AstralBarrierBuy import *
from Quantreo.Backtest import *
from Quantreo.WalkForwardOptimization import *

import warnings
warnings.filterwarnings("ignore")

# SAVE WEIGHTS
save = False
name = "LI_2024_07_FxMajorBarrier"

df = pd.read_csv("../Data/FixTimeBars/EURUSD_IBF_4H_READY.csv", index_col="time", parse_dates=True)


params_range = {
    "tp": [0.0035],
    "sl": [-0.0020],
}

params_fixed = {
    "cost": 0.0001,
    "leverage": 10,
    "list_X": ["velocity", "acceleration", "candle_way",
          'ret_log_1', 'ret_log_2', 'ret_log_5',
          "rolling_volatility_yang_zhang", "rolling_volatility_parkinson", 'hurst',
       '0_to_20', '20_to_40', '40_to_60', '60_to_80', '80_to_100',
       'linear_slope', 'linear_slope_last_25'],
    "train_mode": True,
}

# You can initialize the class into the variable RO, WFO or the name that you want (I put WFO for Walk forward Opti)

WFO = WalkForwardOptimization(df, AstralBarrierBuy, params_fixed, params_range,length_train_set=5_000, randomness=1.00, anchored=False)
WFO.run_optimization()

# Extract best parameters
params = WFO.best_params_smoothed[-1]
print("BEST PARAMETERS")
print(params)

# Extract the
model = params["model"]
sc = params["sc"]
pca = params["pca"]

if save:
    dump(model, f"../models/saved/{name}_model.jolib")
    dump(sc, f"../models/saved/{name}_sc.jolib")
    dump(pca, f"../models/saved/{name}_pca.jolib")

# Show the results
WFO.display()
