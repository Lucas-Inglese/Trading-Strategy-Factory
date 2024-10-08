"""
Description:  Trading strategy based on a Machine Learning algorithm (Decision Tree). As input, we take a LOT of
              different features that we will reduce using a PCA

              We standardize the data to put all the data at the same scale (necessary for PCA, not especially for the
              Decision Tree)

              We apply an PCA to reduce the number of variable and remove the multicolinearity


Entry signal: We need that the ML algo say to buy in the same time

Exit signal:  Basic Take-profit and Stop-loss

Good to know: Only one trade at time (we can't have a buy and a sell position in the same time)

How to improve this algorithm?: Put variable Take-profit and Stop loss
"""

from Quantreo.DataPreprocessing import *
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from joblib import dump, load

from sklearn.ensemble import VotingClassifier, RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

class FxMajorBarrier:

    def __init__(self, data, parameters):
        # Set parameters
        self.list_X = parameters["list_X"]
        self.tp, self.sl = parameters["tp"], parameters["sl"]
        self.cost, self.leverage = parameters["cost"], parameters["leverage"]
        self.train_mode = parameters["train_mode"]

        self.model, self.sc, self.pca = None, None, None
        self.saved_model_path, self.saved_sc_path = None, None

        # Get test parameters
        self.output_dictionary = parameters.copy()
        self.output_dictionary["train_mode"] = False

        if self.train_mode:
            self.data_train = data
            self.data = data
            self.train_model()
        else:
            self.model = parameters["model"]
            self.sc = parameters["sc"]
            self.pca = parameters["pca"]
            self.data = data

        self.start_date_backtest = self.data.index[0]
        self.get_predictions()

        # Get Entry parameters
        self.buy, self.sell = False, False
        self.open_buy_price, self.open_sell_price = None, None
        self.entry_time, self.exit_time = None, None

        # Get exit parameters
        self.var_buy_high, self.var_sell_high = None, None
        self.var_buy_low, self.var_sell_low = None, None

    def get_features(self, data_sample):

        data_sample = derivatives(data_sample, "close")
        data_sample = candle_information_bis(data_sample)
        data_sample = moving_yang_zhang_estimator(data_sample, 100)
        data_sample = moving_parkinson_estimator(data_sample, 20)
        for i in [1, 2, 5]:
            data_sample = log_transform(data_sample, "close", i)
        data_sample = data_sample.fillna(value=0)

        return data_sample

    def train_model(self):
        # Create the features and the target
        full_split = 1.00

        # features to reply in the get_features function
        self.data_train = self.get_features(self.data_train)

        # Create lists with the columns name of the features used and the target
        self.data_train["time"] = self.data_train.index.astype(str)
        self.data_train = get_barrier(self.data_train, tp=.0050, sl=-.0020, buy=True)

        dummy_0 = self.data_train[self.data_train['dummy'] == 0]
        dummy_1 = self.data_train[self.data_train['dummy'] == 1]

        # Trouver la taille minimale entre les deux groupes
        min_size = min(len(dummy_0), len(dummy_1))

        # Échantillonner aléatoirement sans remise pour obtenir des groupes équilibrés
        dummy_0_sample = dummy_0.sample(n=min_size, random_state=42)
        dummy_1_sample = dummy_1.sample(n=min_size, random_state=42)

        # Combiner les échantillons pour obtenir un DataFrame équilibré
        balanced_df = pd.concat([dummy_0_sample, dummy_1_sample])

        # Mélanger les lignes pour éviter tout biais
        self.data_train = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

        list_y = ["dummy"]

        # Split our dataset in a train and a test set
        split = int(len(self.data_train) * full_split)
        X_train, X_test, y_train, y_test = data_split(self.data_train, split, self.list_X, list_y)

        # Initialize the standardization model
        sc = StandardScaler()
        X_train_sc = sc.fit_transform(X_train)

        # Create a PCA to remove multicolinearity and reduce the number of variable keeping many information
        pca = PCA(n_components=12)
        X_train_pca = pca.fit_transform(X_train_sc)

        # Create the model
        #ml_model = SVC()
        clf1 = RandomForestClassifier(n_estimators=100, random_state=42)
        clf2 = GradientBoostingClassifier(n_estimators=100, random_state=42)
        clf3 = AdaBoostClassifier(n_estimators=100, random_state=42)
        clf4 = DecisionTreeClassifier(random_state=42)
        clf5 = LogisticRegression(max_iter=1000, random_state=42)
        clf6 = SVC(probability=True, random_state=42)

        # Création du VotingClassifier avec les classificateurs de base
        ml_model = VotingClassifier(
            estimators=[
                ('rf', clf1),
                ('gb', clf2),
                ('ada', clf3),
                ('dt', clf4),
                ('lr', clf5),
                ('svc', clf6)
            ],
            voting='hard'  # 'soft' pour utiliser les probabilités, 'hard' pour les prédictions majoritaires
        )

        ml_model.fit(X_train_sc, y_train)

        # Save models as attributes
        self.model = ml_model
        self.sc = sc
        self.pca = pca

        self.output_dictionary["model"] = ml_model
        self.output_dictionary["sc"] = sc
        self.output_dictionary["pca"] = pca

    def get_predictions(self):
        self.data = self.get_features(self.data)

        X = self.data[self.list_X]
        X_sc = self.sc.transform(X)
        # X_pca = self.pca.transform(X_sc)

        predict_array = self.model.predict(X_sc)
        self.data["ml_signal"] = 0
        self.data["ml_signal"] = predict_array

        nb_0 = self.data[self.data["ml_signal"] == 0].count()["ml_signal"]
        nb_1 = self.data[self.data["ml_signal"] == 1].count()["ml_signal"]
        print(nb_0, nb_1)
    def get_entry_signal(self, time):
        """
        Random Entry signal
        :param i: row number
        :return: Open a buy or sell position using a random signal
        """
        if time not in self.data.index:
            return 0, self.entry_time

        if len(self.data.loc[:time]["ml_signal"]) < 2:
            return 0, self.entry_time

        # Create entry signal --> -1,0,1
        entry_signal = 0
        if self.data.loc[:time]["ml_signal"][-2] == 1:
            entry_signal = 1
        elif self.data.loc[:time]["ml_signal"][-2] == -1:
            entry_signal = -1

        # Enter in buy position only if we want to, and we aren't already
        if entry_signal == 1 and not self.buy and not self.sell:
            self.buy = True
            self.open_buy_price = self.data.loc[time]["open"]
            self.entry_time = time

        # Enter in sell position only if we want to, and we aren't already
        elif entry_signal == -1 and not self.sell and not self.buy:
            self.sell = True
            self.open_sell_price = self.data.loc[time]["open"]
            self.entry_time = time

        else:
            entry_signal = 0

        return entry_signal, self.entry_time

    def get_exit_signal(self, time):
        """
        Take-profit & Stop-loss exit signal
        :param i: row number
        :return: P&L of the position IF we close it

        **ATTENTION**: If you allow your bot to take a buy and a sell position in the same time,
        you need to return 2 values position_return_buy AND position_return_sell
        """
        # Verify if we need to close a position and update the variations IF we are in a buy position
        if self.buy:
            self.var_buy_high = (self.data.loc[time]["high"] - self.open_buy_price) / self.open_buy_price
            self.var_buy_low = (self.data.loc[time]["low"] - self.open_buy_price) / self.open_buy_price

            # Let's check if AT LEAST one of our threshold are touched on this row
            if (self.tp < self.var_buy_high) and (self.var_buy_low < self.sl):

                # Close with a positive P&L if high_time is before low_time
                if self.data.loc[time]["high_time"] < self.data.loc[time]["low_time"]:
                    self.buy = False
                    self.open_buy_price = None
                    position_return_buy = (self.tp - self.cost) * self.leverage
                    self.exit_time = time
                    return position_return_buy, self.exit_time

                # Close with a negative P&L if low_time is before high_time
                elif self.data.loc[time]["low_time"] < self.data.loc[time]["high_time"]:
                    self.buy = False
                    self.open_buy_price = None
                    position_return_buy = (self.sl - self.cost) * self.leverage
                    self.exit_time = time
                    return position_return_buy, self.exit_time

                else:
                    self.buy = False
                    self.open_buy_price = None
                    position_return_buy = 0
                    self.exit_time = time
                    return position_return_buy, self.exit_time

            elif self.tp < self.var_buy_high:
                self.buy = False
                self.open_buy_price = None
                position_return_buy = (self.tp - self.cost) * self.leverage
                self.exit_time = time
                return position_return_buy, self.exit_time

            # Close with a negative P&L if low_time is before high_time
            elif self.var_buy_low < self.sl:
                self.buy = False
                self.open_buy_price = None
                position_return_buy = (self.sl - self.cost) * self.leverage
                self.exit_time = time
                return position_return_buy, self.exit_time

        # Verify if we need to close a position and update the variations IF we are in a sell position
        if self.sell:
            self.var_sell_high = -(self.data.loc[time]["high"] - self.open_sell_price) / self.open_sell_price
            self.var_sell_low = -(self.data.loc[time]["low"] - self.open_sell_price) / self.open_sell_price

            # Let's check if AT LEAST one of our threshold are touched on this row
            if (self.tp < self.var_sell_low) and (self.var_sell_high < self.sl):

                # Close with a positive P&L if high_time is before low_time
                if self.data.loc[time]["low_time"] < self.data.loc[time]["high_time"]:
                    self.sell = False
                    self.open_sell_price = None
                    position_return_sell = (self.tp - self.cost) * self.leverage
                    self.exit_time = time
                    return position_return_sell, self.exit_time

                # Close with a negative P&L if low_time is before high_time
                elif self.data.loc[time]["high_time"] < self.data.loc[time]["low_time"]:
                    self.sell = False
                    self.open_sell_price = None
                    position_return_sell = (self.sl - self.cost) * self.leverage
                    self.exit_time = time
                    return position_return_sell, self.exit_time

                else:
                    self.sell = False
                    self.open_sell_price = None
                    position_return_sell = 0
                    self.exit_time = time
                    return position_return_sell, self.exit_time

            # Close with a positive P&L if high_time is before low_time
            elif self.tp < self.var_sell_low:
                self.sell = False
                self.open_sell_price = None
                position_return_sell = (self.tp - self.cost) * self.leverage
                self.exit_time = time
                return position_return_sell, self.exit_time

            # Close with a negative P&L if low_time is before high_time
            elif self.var_sell_high < self.sl:
                self.sell = False
                self.open_sell_price = None
                position_return_sell = (self.sl - self.cost) * self.leverage
                self.exit_time = time
                return position_return_sell, self.exit_time

        return 0, None
