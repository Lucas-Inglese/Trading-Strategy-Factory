import ta
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
from tqdm import tqdm

def sma(df, col, n):
    df[f"SMA_{n}"] = ta.trend.SMAIndicator(df[col],int(n)).sma_indicator()
    return df


def sma_diff(df, col, n, m):
    df = df.copy()
    df[f"SMA_d_{n}"] = ta.trend.SMAIndicator(df[col], int(n)).sma_indicator()
    df[f"SMA_d_{m}"] = ta.trend.SMAIndicator(df[col], int(m)).sma_indicator()

    df[f"SMA_diff"] = df[f"SMA_d_{n}"] - df[f"SMA_d_{m}"]
    return df


def rsi(df, col, n):
    df = df.copy()
    df[f"RSI"] = ta.momentum.RSIIndicator(df[col],int(n)).rsi()
    return df


def atr(df, n):
    df = df.copy()
    df[f"ATR"] = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"], int(n)).average_true_range()
    return df


def sto_rsi(df, col, n):
    df = df.copy()

    StoRsi = ta.momentum.StochRSIIndicator(df[col], int(n))
    df[f"STO_RSI"] = StoRsi.stochrsi() * 100
    df[f"STO_RSI_D"] = StoRsi.stochrsi_d() * 100
    df[f"STO_RSI_K"] = StoRsi.stochrsi_k() * 100
    return df


def ichimoku(df,n1,n2):
    ICHIMOKU = ta.trend.IchimokuIndicator(df["high"], df["low"], int(n1), int(n2))
    df["SPAN_A"] = ICHIMOKU.ichimoku_a()
    df["SPAN_B"] = ICHIMOKU.ichimoku_b()
    df["BASE"] = ICHIMOKU.ichimoku_base_line()
    df["CONVERSION"] = ICHIMOKU.ichimoku_conversion_line()
    return df

def previous_ret(df,col,n):
    df["previous_ret"] = (df[col].shift(int(n)) - df[col]) / df[col]
    return df


def k_enveloppe(df, n=10):
    df[f"EMA_HIGH_{n}"] = df["high"].ewm(span=n).mean()
    df[f"EMA_LOW_{n}"] = df["low"].ewm(span=n).mean()

    df["pivots_high"] = (df["close"] - df[f"EMA_HIGH_{n}"])/ df[f"EMA_HIGH_{n}"]
    df["pivots_low"] = (df["close"] - df[f"EMA_LOW_{n}"])/ df[f"EMA_LOW_{n}"]
    df["pivots"] = (df["pivots_high"]+df["pivots_low"])/2
    return df

def candle_information(df):
    # Candle color
    df["candle_way"] = -1
    df.loc[(df["open"] - df["close"]) < 0, "candle_way"] = 1

    # Filling percentage
    df["filling"] = np.abs(df["close"] - df["open"]) / np.abs(df["high"] - df["low"])

    # Amplitude
    df["amplitude"] = np.abs(df["close"] - df["open"]) / (df["open"] / 2 + df["close"] / 2) * 100

    return df

def astral(df):
    df_copy = df.copy()
    df_copy["5_days_high"] = df_copy["high"].pct_change(5)
    df_copy["5_days_low"] = df_copy["low"].pct_change(5)
    df_copy["3_days_close"] = df_copy["close"].pct_change(3)

    df_copy["ponctual_long_astral"] = 0
    df_copy["ponctual_short_astral"] = 0

    df_copy.loc[(df_copy["5_days_low"]<0) &  (df_copy["3_days_close"]<0), "ponctual_long_astral"] = 1
    df_copy.loc[(df_copy["5_days_high"]>0) &  (df_copy["3_days_close"]>0), "ponctual_short_astral"] = -1


    df_copy["long_astral"] = df_copy["ponctual_long_astral"]
    for i in range(1,8):
        df_copy.loc[(df_copy["ponctual_long_astral"].shift(i)==1) & (df_copy["ponctual_long_astral"]==1) , "long_astral"] = df_copy["long_astral"] + 1

    df_copy["short_astral"] = df_copy["ponctual_short_astral"]
    for i in range(1,8):
        df_copy.loc[(df_copy["ponctual_short_astral"].shift(i)==-1) & (df_copy["ponctual_short_astral"]==-1) , "short_astral"] = df_copy["short_astral"] - 1

    df_copy["astral"] = df_copy["long_astral"]+df_copy["short_astral"]
    return df_copy


def derivatives(df, col):
    """
    Calculates the first and second derivatives of a given column in a DataFrame
    and adds them as new columns 'velocity' and 'acceleration'.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the column for which derivatives are to be calculated.

    col : str
        The column name for which the first and second derivatives are to be calculated.

    Returns:
    --------
    df_copy : pandas.DataFrame
        A new DataFrame with 'velocity' and 'acceleration' columns added.

    """

    df_copy = df.copy()

    df_copy["velocity"] = df_copy[col].diff().fillna(0)
    df_copy["acceleration"] = df_copy["velocity"].diff().fillna(0)

    return df_copy

def candle_information_bis(df):
    df_copy = df.copy()
    # Candle color
    df_copy["candle_way"] = -1
    df_copy.loc[(df_copy["open"] - df_copy["close"]) < 0, "candle_way"] = 1

    # Filling percentage
    df_copy["filling"] = np.abs(df_copy["close"] - df_copy["open"]) / np.abs(df_copy["high"] - df_copy["low"])

    # Amplitude
    df_copy["amplitude"] = np.abs(df_copy["close"] - df_copy["open"]) / (df_copy["open"] / 2 + df_copy["close"] / 2) * 100

    return df_copy


def moving_parkinson_estimator(df, window_size=30):
    """
    Calculate Parkinson's volatility estimator based on high and low prices.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing 'high' and 'low' columns for each trading period.

    Returns:
    --------
    volatility : float
        Estimated volatility based on Parkinson's method.
    """

    def parkinson_estimator(df):
        N = len(df)
        sum_squared = np.sum(np.log(df['high'] / df['low']) ** 2)

        volatility = math.sqrt((1 / (4 * N * math.log(2))) * sum_squared)
        return volatility

    df_copy = df.copy()
    # Create an empty series to store mobile volatility
    rolling_volatility = pd.Series(dtype='float64')

    # Browse the DataFrame by window size `window_size` and apply `parkinson_estimator`.
    for i in range(window_size, len(df)):
        window = df_copy.loc[df_copy.index[i - window_size]: df_copy.index[i]]
        volatility = parkinson_estimator(window)
        rolling_volatility.at[df_copy.index[i]] = volatility

    # Add the mobile volatility series to the original DataFrame
    df_copy['rolling_volatility_parkinson'] = rolling_volatility

    return df_copy


def moving_yang_zhang_estimator(df, window_size=30):
    """
    Calculate Parkinson's volatility estimator based on high and low prices.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing 'high' and 'low' columns for each trading period.

    Returns:
    --------
    volatility : float
        Estimated volatility based on Parkinson's method.
    """

    def yang_zhang_estimator(df):
        N = len(window)

        term1 = np.log(window['high'] / window['close']) * np.log(window['high'] / window['open'])
        term2 = np.log(window['low'] / window['close']) * np.log(window['low'] / window['open'])

        sum_squared = np.sum(term1 + term2)
        volatility = np.sqrt(sum_squared / N)

        return volatility

    df_copy = df.copy()

    # Create an empty series to store mobile volatility
    rolling_volatility = pd.Series(dtype='float64')

    # Browse the DataFrame by window size `window_size` and apply `yang_zhang_estimator`.
    for i in range(window_size, len(df)):
        window = df_copy.loc[df_copy.index[i - window_size]: df_copy.index[i]]
        volatility = yang_zhang_estimator(window)
        rolling_volatility.at[df_copy.index[i]] = volatility

    # Add the mobile volatility series to the original DataFrame
    df_copy['rolling_volatility_yang_zhang'] = rolling_volatility

    return df_copy


def log_transform(df, col, n):
    """
    Applies a logarithmic transformation to a specified column in a DataFrame
    and calculates the percentage change of the log-transformed values over a
    given window size.

    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame containing the column to be logarithmically transformed.
    col : str
        The name of the column to which the logarithmic transformation is to be applied.
    n : int
        The window size over which to calculate the percentage change of the log-transformed values.

    Returns:
    --------
    df_copy : pandas.DataFrame
        A new DataFrame containing two new columns:
        1. log_{col}: Log-transformed values of the specified column.
        2. ret_log_{n}: Percentage change of the log-transformed values over the window size n.
    """
    df_copy = df.copy()
    df_copy[f"log_{col}"] = np.log(df_copy[col])
    df_copy[f"ret_log_{n}"] = df_copy[f"log_{col}"].pct_change(n)

    return df_copy


##### SIGNALS

def data_split(df_model, split, list_X, list_y):

    # Train set creation
    X_train = df_model[list_X].iloc[0:split-1, :]
    y_train = df_model[list_y].iloc[1:split]

    # Test set creation
    X_test = df_model[list_X].iloc[split:-1, :]
    y_test = df_model[list_y].iloc[split+1:]

    return X_train, X_test, y_train, y_test

def quantile_signal(df, n, quantile_level=0.67,pct_split=0.8):

    n = int(n)

    # Create the split between train and test set to do not create a Look-Ahead bais
    split = int(len(df) * pct_split)

    # Copy the dataframe to do not create any intereference
    df_copy = df.copy()

    # Create the fut_ret column to be able to create the signal
    df_copy["fut_ret"] = (df_copy["close"].shift(-n) - df_copy["open"]) / df_copy["open"]

    # Create a column by name, 'Signal' and initialize with 0
    df_copy['Signal'] = 0

    # Assign a value of 1 to 'Signal' column for the quantile with the highest returns
    df_copy.loc[df_copy['fut_ret'] > df_copy['fut_ret'][:split].quantile(q=quantile_level), 'Signal'] = 1

    # Assign a value of -1 to 'Signal' column for the quantile with the lowest returns
    df_copy.loc[df_copy['fut_ret'] < df_copy['fut_ret'][:split].quantile(q=1-quantile_level), 'Signal'] = -1

    return df_copy

def binary_signal(df, n):

    n = int(n)

    # Copy the dataframe to do not create any intereference
    df_copy = df.copy()

    # Create the fut_ret column to be able to create the signal
    df_copy["fut_ret"] = (df_copy["close"].shift(-n) - df_copy["open"]) / df_copy["open"]

    # Create a column by name, 'Signal' and initialize with 0
    df_copy['Signal'] = -1

    # Assign a value of 1 to 'Signal' column for the quantile with the highest returns
    df_copy.loc[df_copy['fut_ret'] > 0, 'Signal'] = 1

    return df_copy


def get_barrier_buy(df, nb_row, tp=0.015, sl=-0.015):
    i = nb_row
    # LOOP FOR UNTIL WE CROSS THE TP OR SL
    for j in range(5000):

        # Extract starting line
        row_i = df.iloc[i:i + 1]

        # Extract current line
        row_i_j = df.iloc[i + j:i + j + 1]

        # Compute variations from the start to current high and low
        var_high = (row_i_j["high"].values[0] - row_i["open"].values[0]) / row_i["open"].values[0]
        var_low = (row_i_j["low"].values[0] - row_i["open"].values[0]) / row_i["open"].values[0]

        if (tp < var_high) and (var_low < sl):
            if row_i_j["high_time"].values[0] < row_i_j["low_time"].values[0]:
                time_datetime = datetime.strptime(row_i_j["high_time"].values[0],
                                                  "%Y-%m-%d %H:%M:%S") - datetime.strptime(row_i["time"].values[0],
                                                                                           "%Y-%m-%d %H:%M:%S")
                break
            elif row_i_j["low_time"].values[0] < row_i_j["high_time"].values[0]:
                time_datetime = -(datetime.strptime(row_i_j["low_time"].values[0],
                                                    "%Y-%m-%d %H:%M:%S") - datetime.strptime(
                    row_i["time"].values[0], "%Y-%m-%d %H:%M:%S"))
                break

        # IF we touch the tp we break the loop
        elif (tp < var_high):
            time_datetime = datetime.strptime(row_i_j["high_time"].values[0],
                                              "%Y-%m-%d %H:%M:%S") - datetime.strptime(row_i["time"].values[0],
                                                                                       "%Y-%m-%d %H:%M:%S")
            break

        # IF we touch the sl we break the loop
        elif (var_low < sl):
            time_datetime = -(
                        datetime.strptime(row_i_j["low_time"].values[0], "%Y-%m-%d %H:%M:%S") - datetime.strptime(
                    row_i["time"].values[0], "%Y-%m-%d %H:%M:%S"))
            break

        else:
            time_datetime = timedelta(0)

    time = time_datetime.total_seconds() / 3600
    return time
def get_barrier_sell(df, nb_row, tp=0.015, sl=-0.015):
    i = nb_row
    # LOOP FOR UNTIL WE CROSS THE TP OR SL
    for j in range(5000):

        # Extract starting line
        row_i = df.iloc[i:i + 1]

        # Extract current line
        row_i_j = df.iloc[i + j:i + j + 1]

        # Compute variations from the start to current high and low
        var_high = (row_i_j["high"].values[0] - row_i["open"].values[0]) / row_i["open"].values[0]
        var_low = (row_i_j["low"].values[0] - row_i["open"].values[0]) / row_i["open"].values[0]

        if (tp < -var_low) and (-var_high < sl):
            if row_i_j["low_time"].values[0] < row_i_j["high_time"].values[0]:
                time_datetime = datetime.strptime(row_i_j["low_time"].values[0],
                                                  "%Y-%m-%d %H:%M:%S") - datetime.strptime(row_i["time"].values[0],
                                                                                           "%Y-%m-%d %H:%M:%S")
                break
            elif row_i_j["high_time"].values[0] < row_i_j["low_time"].values[0]:
                time_datetime = -(datetime.strptime(row_i_j["high_time"].values[0],
                                                    "%Y-%m-%d %H:%M:%S") - datetime.strptime(
                    row_i["time"].values[0], "%Y-%m-%d %H:%M:%S"))
                break

        # IF we touch the tp we break the loop
        elif (tp < -var_low):
            time_datetime = datetime.strptime(row_i_j["low_time"].values[0],
                                              "%Y-%m-%d %H:%M:%S") - datetime.strptime(row_i["time"].values[0],
                                                                                       "%Y-%m-%d %H:%M:%S")
            break

        # IF we touch the sl we break the loop
        elif (-var_high < sl):
            time_datetime = -(
                        datetime.strptime(row_i_j["high_time"].values[0], "%Y-%m-%d %H:%M:%S") - datetime.strptime(
                    row_i["time"].values[0], "%Y-%m-%d %H:%M:%S"))
            break

        else:
            time_datetime = timedelta(0)

    time = time_datetime.total_seconds() / 3600
    return time

def get_ind_barrier(df, nb_row, tp=0.015, sl=-0.015, buy=True):
    if buy:
        time = get_barrier_buy(df, nb_row, tp=tp, sl=sl)
    else:
        time = get_barrier_sell(df, nb_row, tp=tp, sl=sl)
    return time

def get_barrier(df, tp=0.015, sl=-0.015, buy=True):
    # Empty list to contain the labeling
    tpl = list()

    df_copy = df.copy()
    # Loop for to search the labels
    for i in range(len(df)):

        # IMPORTANT: try/except for the last row to avoid errors if we don't have found the TP or SL
        try:
            tpl.append(get_ind_barrier(df_copy, i, tp=tp, sl=sl, buy=buy))
        except Exception as e:
            print(e)
            tpl.append(0)

    # Place the label columns in the dataframe
    df_copy["labeling"] = tpl

    df_copy["dummy"] = -1
    df_copy.loc[df_copy["labeling"] < 0, "dummy"] = 0
    df_copy.loc[0 < df_copy["labeling"], "dummy"] = 1
    df_copy = df_copy[df_copy["dummy"] != -1]

    return df_copy