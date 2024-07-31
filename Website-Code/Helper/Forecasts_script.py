import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from fbprophet import Prophet
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
import warnings

warnings.filterwarnings("ignore")

for subdiv in rain_data["SUBDIVISION"].unique():
    print(subdiv)
    
    # Create subdivision folder
    subdiv_folder = f'subdivs/{subdiv}'
    os.makedirs(subdiv_folder, exist_ok=True)
    
    # 1. Data Loading and Preparation
    data = rain_data[rain_data["SUBDIVISION"] == subdiv]
    data = data.drop(columns=["SUBDIVISION", 'ANNUAL', 'Jan-Feb', 'Mar-May', 'Jun-Sep', 'Oct-Dec'])
    data = data.reset_index(drop=True)
    data.set_index('YEAR', inplace=True)
    monthly_data = data.stack().reset_index()
    monthly_data.columns = ['YEAR', 'MONTH', 'RAINFALL']
    month_map = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
    monthly_data['MONTH'] = monthly_data['MONTH'].map(month_map)
    monthly_data['DATE'] = pd.to_datetime(monthly_data[['YEAR', 'MONTH']].assign(DAY=1))
    monthly_data.set_index('DATE', inplace=True)
    monthly_data = monthly_data['RAINFALL']
    monthly_data.index = monthly_data.index.to_period('M')
    
    # Fit the SARIMA model
    model = SARIMAX(monthly_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    model_fit = model.fit(disp=False)

    # Forecast for the next few years (12 months in a year)
    forecast_steps = 5 * 12  # 5 years
    forecast = model_fit.get_forecast(steps=forecast_steps)
    forecast_index = pd.period_range(start=monthly_data.index[-1] + 1, periods=forecast_steps, freq='M')
    forecast_series = pd.Series(forecast.predicted_mean.values, index=forecast_index)

    # Save SARIMA forecast
    forecast_series.to_csv(f'{subdiv_folder}/sarima_forecast.csv')
    
    # Plot only the forecast
    plt.figure(figsize=(12, 8))
    plt.plot(forecast_series.index.to_timestamp(), forecast_series, label='Forecast', color='red')
    plt.title(f'Rainfall Forecast for Next 5 Years - {subdiv}')
    plt.xlabel('Date')
    plt.ylabel('Rainfall (mm)')
    plt.legend()
    plt.savefig(f'{subdiv_folder}/sarima_plot.png')
    plt.close()
    
    # Prophet model
    monthly_data = monthly_data.reset_index()
    monthly_data['DATE'] = monthly_data['DATE'].dt.to_timestamp()
    monthly_data_prophet = monthly_data.rename(columns={'DATE': 'ds', 'RAINFALL': 'y'})
    model_prophet = Prophet()
    model_prophet.fit(monthly_data_prophet)

    # Make a future dataframe for 5 years (60 months)
    future = model_prophet.make_future_dataframe(periods=60, freq='M')
    forecast_prophet = model_prophet.predict(future)

    # Save Prophet forecast
    forecast_prophet[['ds', 'yhat']].to_csv(f'{subdiv_folder}/prophet_forecast.csv', index=False)
    
    # Plot the forecast
    plt.figure(figsize=(25, 6))
    fig = model_prophet.plot(forecast_prophet)
    plt.title(f'Rainfall Forecast for Next 5 Years using Prophet - {subdiv}')
    plt.xlabel('Date')
    plt.ylabel('Rainfall (mm)')
    plt.savefig(f'{subdiv_folder}/prophet_plot.png')
    plt.close()
    
    # ETS model
    model = ExponentialSmoothing(monthly_data['RAINFALL'], seasonal='add', seasonal_periods=12)
    fit = model.fit()
    forecast = fit.forecast(steps=60)
    
    # Save ETS forecast
    forecast.to_csv(f'{subdiv_folder}/ets_forecast.csv')

    # Plot results
    plt.figure(figsize=(12, 6))
    plt.plot(monthly_data.index[-20:], monthly_data['RAINFALL'][-20:], label='Observed')
    plt.plot(forecast.index, forecast, label='Forecast', color='red')
    plt.title(f'ETS Forecast - {subdiv}')
    plt.xlabel('Date')
    plt.ylabel('Rainfall')
    plt.legend()
    plt.savefig(f'{subdiv_folder}/ets_plot.png')
    plt.close()

    # LSTM model
    if not isinstance(monthly_data['DATE'], pd.DatetimeIndex):
        monthly_data.index = pd.to_datetime(monthly_data['DATE'])
    values = monthly_data['RAINFALL'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_values = scaler.fit_transform(values)

    def create_dataset(data, time_step=1):
        X, Y = [], []
        for i in range(len(data) - time_step):
            X.append(data[i:(i + time_step), 0])
            Y.append(data[i + time_step, 0])
        return np.array(X), np.array(Y)

    time_step = 12
    X, Y = create_dataset(scaled_values, time_step)
    X = X.reshape((X.shape[0], X.shape[1], 1))
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    Y_train, Y_test = Y[:split], Y[split:]

    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, Y_train, epochs=20, batch_size=32, validation_split=0.1, verbose=0)
    
    last_sequence = scaled_values[-time_step:].reshape((1, time_step, 1))
    predictions = []

    for _ in range(60):  # Predict next 12 months
        pred = model.predict(last_sequence, verbose=0)
        predictions.append(pred[0, 0])
        new_sequence = np.zeros((1, time_step, 1))
        new_sequence[0, :-1, :] = last_sequence[0, 1:, :]
        new_sequence[0, -1, :] = pred
        last_sequence = new_sequence

    predictions = np.array(predictions).reshape(-1, 1)
    predictions = scaler.inverse_transform(predictions)
    forecast_start = monthly_data.index[-1] + pd.DateOffset(months=1)
    forecast_index = pd.date_range(start=forecast_start, periods=60, freq='M')
    
    # Save LSTM forecast
    forecast_df = pd.DataFrame(data={'DATE': forecast_index, 'RAINFALL': predictions.flatten()})
    forecast_df.to_csv(f'{subdiv_folder}/lstm_forecast.csv', index=False)
    
    # Plot results
    plt.figure(figsize=(12, 6))
    plt.plot(monthly_data.index[-20:], monthly_data['RAINFALL'][-20:], label='Actual')
    plt.plot(forecast_index, predictions, label='Forecast', color='red')
    plt.title(f'LSTM Forecast - {subdiv}')
    plt.xlabel('Date')
    plt.ylabel('Rainfall')
    plt.legend()
    plt.savefig(f'{subdiv_folder}/lstm_plot.png')
    plt.close()
