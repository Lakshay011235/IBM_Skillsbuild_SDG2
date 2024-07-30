from flask import Flask, jsonify, request, render_template
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Sample DataFrame
data = {
    'District': ['District1', 'District2', 'District1', 'District2'],
    'State': ['State1', 'State1', 'State2', 'State2'],
    'Month': ['January', 'February', 'March', 'April'],
    'Season': ['Winter', 'Winter', 'Spring', 'Spring'],
    'Crop1': ['WHEAT', 'Rice', 'Barley', 'Maize'],
    'Crop2': ['Corn', 'Wheat', 'Oats', 'Rice'],
    'Rainfall': [100, 150, 200, 250]
}
df = pd.DataFrame(data)

# Example sorted pairs data
sorted_pairs_seasons = pd.DataFrame({
    'Column Name': ['WHEAT', 'WHEAT', 'WHEAT', 'WHEAT'],
    'Season': ['Oct-Dec', 'Mar-May', 'Jun-Sep', 'Jan-Feb'],
    'Correlation': [-0.582526, -0.367133, -0.280149, 0.029938]
})

sorted_pairs_crops = pd.DataFrame({
    'Column Name': ['WHEAT']*27,
    'Crop': ['RAPESEED AND MUSTARD', 'BARLEY', 'FRUITS', 'FINGER MILLET', 'RABI SORGHUM', 
             'CHICKPEA', 'MAIZE', 'PEARL MILLET', 'PIGEONPEA', 'LINSEED', 
             'MINOR PULSES', 'POTATOES', 'FODDER', 'SAFFLOWER', 'SUNFLOWER', 
             'GROUNDNUT', 'SORGHUM', 'ONION', 'RICE', 'SUGARCANE', 'CASTOR', 
             'SESAMUM', 'KHARIF SORGHUM', 'COTTON', 'SOYABEAN', 'VEGETABLES', 
             'OILSEEDS'],
    'Correlation': [0.697734, 0.577132, -0.455622, -0.446333, -0.295990, 
                    0.285870, -0.231799, 0.229056, 0.206885, 0.173683, 
                    0.151290, 0.150121, 0.139388, -0.138866, -0.103962, 
                    -0.082805, -0.072365, -0.060503, -0.057967, 0.027976, 
                    0.019075, 0.016974, -0.013902, -0.007521, -0.002466, 
                    -0.002305, 0.000615]
})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/districts', methods=['GET'])
def get_districts():
    districts = df['District'].unique().tolist()
    return jsonify(districts)

@app.route('/crops', methods=['GET'])
def get_crops():
    crops = pd.concat([df['Crop1'], df['Crop2']]).unique().tolist()
    return jsonify(crops)

@app.route('/crop_info', methods=['GET'])
def get_crop_info():
    district = request.args.get('district')
    crop = request.args.get('crop')

    if not district or not crop:
        return jsonify({"error": "Please provide both district and crop"}), 400

    crop_info = df[(df['District'] == district) & ((df['Crop1'] == crop) | (df['Crop2'] == crop))]
    if crop_info.empty:
        return jsonify({"error": "No data available for the provided district and crop"}), 404

    # Crop Pairings Plot
    # try:
    #     crop_pairings = sorted_pairs_crops[sorted_pairs_crops['Column Name'] == crop]
        
    #     # Debugging: Print crop_pairings DataFrame
    #     print(f"Crop Pairings DataFrame for {crop}:\n{crop_pairings}")

    #     if crop_pairings.empty:
    #         return jsonify({"error": f"No pairing data available for crop: {crop}"}), 404
        
        
    #     import joblib
    #     import prophet
    #     from prophet import Prophet
    #     import pandas as pd
    #     import matplotlib.pyplot as plt

    #     # Version
    #     print(prophet.__version__)

    #     model_prophet = Prophet()
    #     # Load the model
    #     model_prophet = joblib.load('Helper/model_prophet.pkl')

    #     scaling_value = model_prophet.scaling
    #     print(f"Scaling value: {scaling_value}")

    #     # Make a future dataframe for 5 years (60 months)
    #     future = model_prophet.make_future_dataframe(periods=60, freq='M')
    #     forecast_prophet = model_prophet.predict(future)
        
    #     # Plot the forecast
    #     plt.figure(figsize=(25, 6))
    #     fig = model_prophet.plot(forecast_prophet)
    #     plt.title('Rainfall Forecast for Next 5 Years using Prophet')
    #     plt.xlabel('Date')
    #     plt.ylabel('Rainfall (mm)')
    #     plt.show()
        
    #     fig1, ax1 = plt.subplots()
    #     crop_pairings.plot(kind='bar', x='Crop', y='Correlation', ax=ax1)
    #     ax1.set_title('Crop Pairings')
    #     ax1.set_xlabel('Crop')
    #     ax1.set_ylabel('Correlation')
    #     plt.xticks(rotation=90)

    #     # Convert plot to base64
    #     img1 = io.BytesIO()
    #     fig1.savefig(img1, format='png')
    #     img1.seek(0)
    #     plot1_url = base64.b64encode(img1.getvalue()).decode()
        
    # except Exception as e:
    #     return jsonify({"error": f"Error generating crop pairings plot: {str(e)}"}), 500

    # New Prophet code trial
    # import joblib
    # from prophet import Prophet
    # import pandas as pd
    # import matplotlib.pyplot as plt
    # import io
    # import base64

    # try:
    #     crop_pairings = sorted_pairs_crops[sorted_pairs_crops['Column Name'] == crop]
        
    #     # Debugging: Print crop_pairings DataFrame
    #     print(f"Crop Pairings DataFrame for {crop}:\n{crop_pairings}")

    #     if crop_pairings.empty:
    #         return jsonify({"error": f"No pairing data available for crop: {crop}"}), 404

    #     # Load the model
    #     model_prophet = joblib.load('Helper/model_prophet.pkl')
        
    #     # Debugging: Print model_prophet object
    #     print(f"Loaded Prophet model: {model_prophet}")

    #     # Make a future dataframe for 5 years (60 months)
    #     future = model_prophet.make_future_dataframe(periods=60, freq='M')
        
    #     # Debugging: Print future DataFrame
    #     print(f"Future DataFrame:\n{future.head()}")

    #     # Predict with the loaded model
    #     forecast_prophet = model_prophet.predict(future)
        
    #     # Debugging: Print forecast DataFrame
    #     print(f"Forecast DataFrame:\n{forecast_prophet.head()}")

    #     # Plot the forecast
    #     plt.figure(figsize=(25, 6))
    #     fig = model_prophet.plot(forecast_prophet)
    #     plt.title('Rainfall Forecast for Next 5 Years using Prophet')
    #     plt.xlabel('Date')
    #     plt.ylabel('Rainfall (mm)')
    #     plt.show()

    #     fig1, ax1 = plt.subplots()
    #     crop_pairings.plot(kind='bar', x='Crop', y='Correlation', ax=ax1)
    #     ax1.set_title('Crop Pairings')
    #     ax1.set_xlabel('Crop')
    #     ax1.set_ylabel('Correlation')
    #     plt.xticks(rotation=90)

    #     # Convert plot to base64
    #     img1 = io.BytesIO()
    #     fig1.savefig(img1, format='png')
    #     img1.seek(0)
    #     plot1_url = base64.b64encode(img1.getvalue()).decode()

    # except Exception as e:
    #     return jsonify({"error": f"Error generating crop pairings plot: {str(e)}"}), 500


    # Rainfall Trend Plot
    try:

        # trying sarima model

        import pandas as pd
        import joblib
        import matplotlib.pyplot as plt

        # Load the saved SARIMA model using joblib
        model_fit = joblib.load('Helper/sarima_model.pkl')

        monthly_data = joblib.load('Helper/monthly_data.pkl')

        # Forecast for the next few years (12 months in a year)
        forecast_steps = 5 * 12  # 5 years
        forecast = model_fit.get_forecast(steps=forecast_steps)
        forecast_index = pd.period_range(start=monthly_data.index[-1] + 1, periods=forecast_steps, freq='M')
        forecast_series = pd.Series(forecast.predicted_mean.values, index=forecast_index)

        # Plot only the forecast
        plt.figure(figsize=(12, 8))
        plt.plot(forecast_series.index.to_timestamp(), forecast_series, label='Forecast', color='red')
        plt.title('Rainfall Forecast for Next 5 Years')
        plt.xlabel('Date')
        plt.ylabel('Rainfall (mm)')
        plt.legend()
        plt.show()

        # fig2, ax2 = plt.subplots()
        # df_grouped = df[df['District'] == district].groupby('Month')['Rainfall'].mean()
        # df_grouped.plot(kind='line', ax=ax2)
        # ax2.set_title('Rainfall Trend')
        # ax2.set_xlabel('Month')
        # ax2.set_ylabel('Average Rainfall')

        # Convert plot to base64
        img2 = io.BytesIO()
        # fig2.savefig(img2, format='png')
        img2.seek(0)
        plot2_url = base64.b64encode(img2.getvalue()).decode()
    except Exception as e:
        return jsonify({"error": f"Error generating rainfall trend plot: {str(e)}"}), 500


    # # Rainfall Trend Plot - ETS
    try:
        import pandas as pd
        import joblib
        import matplotlib.pyplot as plt

        # Load the saved ETS model
        fit = joblib.load('Helper/ets_model.pkl')

        # Check if monthly_data is a Series and ensure index is DatetimeIndex
        if isinstance(monthly_data, pd.Series):
            if isinstance(monthly_data.index, pd.PeriodIndex):
                monthly_data.index = monthly_data.index.to_timestamp()

            # Generate forecast for the next 60 periods (5 years)
            forecast = fit.forecast(steps=60)

            # Ensure forecast index is DatetimeIndex
            if isinstance(forecast.index, pd.PeriodIndex):
                forecast.index = forecast.index.to_timestamp()

            plt.figure(figsize=(12, 6))
            plt.plot(monthly_data.index[-20:], monthly_data[-20:], label='Observed')
            plt.plot(forecast.index, forecast, label='Forecast', color='red')
            plt.title('ETS Forecast')
            plt.xlabel('Date')
            plt.ylabel('Rainfall')
            plt.legend()
            plt.show()
        else:
            print("Error: monthly_data is not a pandas Series")

    except Exception as e:
        print(f"Error generating ETS forecast plot: {str(e)}")

    # Rainfall Trend Plot - LSTM
    try:
        from sklearn.preprocessing import MinMaxScaler
        from tensorflow.keras.models import load_model
        import joblib
        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt

        # Load the data
        monthly_data = joblib.load('Helper/monthly_data.pkl')

        # Ensure the Series has a DateTime index
        if not isinstance(monthly_data.index, pd.DatetimeIndex):
            if isinstance(monthly_data.index, pd.PeriodIndex):
                monthly_data.index = monthly_data.index.to_timestamp()
            else:
                monthly_data.index = pd.to_datetime(monthly_data.index)

        # Prepare data
        values = monthly_data.values.reshape(-1, 1)

        # Normalize data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_values = scaler.fit_transform(values)

        # Load the trained model
        model = load_model('Helper/lstm_model.h5')

        time_step = 10  # Define your time step value
        last_sequence = scaled_values[-time_step:].reshape((1, time_step, 1))
        predictions = []

        for _ in range(60):  # Predict next 60 months
            pred = model.predict(last_sequence, verbose=0)
            predictions.append(pred[0, 0])

            # Update the last sequence with the new prediction
            new_sequence = np.zeros((1, time_step, 1))  # Create a new sequence
            new_sequence[0, :-1, :] = last_sequence[0, 1:, :]  # Shift the old sequence
            new_sequence[0, -1, :] = pred  # Add the new prediction
            last_sequence = new_sequence

        # Inverse transform the predictions
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = scaler.inverse_transform(predictions)

        # Prepare actual data for plotting
        forecast_start = monthly_data.index[-1] + pd.DateOffset(months=1)
        forecast_index = pd.date_range(start=forecast_start, periods=60, freq='M')

        # Convert predictions to a DataFrame
        forecast = pd.Series(predictions.flatten(), index=forecast_index)

        # Plot results
        plt.figure(figsize=(12, 6))
        plt.plot(monthly_data.index[-20:], monthly_data[-20:], label='Observed')
        plt.plot(forecast.index, forecast, label='Forecast', color='red')
        plt.title('LSTM Forecast')
        plt.xlabel('Date')
        plt.ylabel('Rainfall')
        plt.legend()
        plt.show()
    except Exception as e:
        print(f"Error generating LSTM forecast plot: {str(e)}")




    response = {
        'season': crop_info['Season'].values[0] if not crop_info.empty else 'N/A',
        'pairings_plot': plot1_url,
        'rainfall_trend_plot': plot2_url
    }
    return jsonify(response)



if __name__ == '__main__':
    app.run(debug=True)
