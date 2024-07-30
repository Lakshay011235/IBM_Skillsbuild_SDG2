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
    try:
        crop_pairings = sorted_pairs_crops[sorted_pairs_crops['Column Name'] == crop]
        
        # Debugging: Print crop_pairings DataFrame
        print(f"Crop Pairings DataFrame for {crop}:\n{crop_pairings}")

        if crop_pairings.empty:
            return jsonify({"error": f"No pairing data available for crop: {crop}"}), 404
        
        fig1, ax1 = plt.subplots()
        crop_pairings.plot(kind='bar', x='Crop', y='Correlation', ax=ax1)
        ax1.set_title('Crop Pairings')
        ax1.set_xlabel('Crop')
        ax1.set_ylabel('Correlation')
        plt.xticks(rotation=90)

        # Convert plot to base64
        img1 = io.BytesIO()
        fig1.savefig(img1, format='png')
        img1.seek(0)
        plot1_url = base64.b64encode(img1.getvalue()).decode()
    except Exception as e:
        return jsonify({"error": f"Error generating crop pairings plot: {str(e)}"}), 500

    # Rainfall Trend Plot
    try:
        fig2, ax2 = plt.subplots()
        df_grouped = df[df['District'] == district].groupby('Month')['Rainfall'].mean()
        df_grouped.plot(kind='line', ax=ax2)
        ax2.set_title('Rainfall Trend')
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Average Rainfall')

        # Convert plot to base64
        img2 = io.BytesIO()
        fig2.savefig(img2, format='png')
        img2.seek(0)
        plot2_url = base64.b64encode(img2.getvalue()).decode()
    except Exception as e:
        return jsonify({"error": f"Error generating rainfall trend plot: {str(e)}"}), 500

    response = {
        'season': crop_info['Season'].values[0] if not crop_info.empty else 'N/A',
        'pairings_plot': plot1_url,
        'rainfall_trend_plot': plot2_url
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
