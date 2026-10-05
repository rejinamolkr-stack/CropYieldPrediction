from flask import Flask, request, render_template_string
import joblib
import pandas as pd

app = Flask(__name__)

# Load model and supporting files
model = joblib.load("crop_yield_model.pkl")
scaler = joblib.load("crop_yield_scaler.pkl")
feature_columns = joblib.load("feature_columns.pkl")
feature_defaults = joblib.load("feature_defaults.pkl")
X_train_reference = joblib.load("X_train_reference.pkl")

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crop Yield Prediction</title>

        <style>
            body {
                background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
                font-family: Arial, sans-serif;
                min-height: 100vh;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .container {
                background: white;
                width: 380px;
                padding: 30px;
                border-radius: 20px;
                text-align: center;
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
            }

            h1 {
                color: #2e7d32;
                font-family: Georgia, serif;
            }

            .input-group {
                width: 48%;
                display: inline-block;
                box-sizing: border-box;
                padding: 5px;
            }

            input {
                width: 100%;
                padding: 10px;
                box-sizing: border-box;
                border: 1px solid #aaa;
                border-radius: 8px;
            }

            button {
                margin-top: 20px;
                padding: 12px 25px;
                background: #388e3c;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
            }
        </style>
    </head>

    <body>
        <div class="container">

            <h1>🌾 Crop Yield Prediction 🍚</h1>

           <form method="POST" action="/predict">

    <label>Farm Size (hectares)</label>
    <input type="number" step="any"
           name="farm_size" required>

    <label>Average Temperature (°C)</label>
    <input type="number" step="any"
           name="temperature" required>

    <label>Annual Rainfall (mm)</label>
    <input type="number" step="any"
           name="rainfall" required>

    <label>Soil Moisture (%)</label>
    <input type="number" step="any"
           name="soil_moisture" required>

    <label>Fertilizer (kg/ha)</label>
    <input type="number" step="any"
           name="fertilizer" required>

    <label>Pesticide (litre/ha)</label>
    <input type="number" step="any"
           name="pesticide" required>

    <button type="submit">Predict Yield</button>

</form>


        </div>
    </body>
    </html>
    """)


@app.route("/predict", methods=["POST"])
def predict():

    farm_size = float(request.form["farm_size"])
    temperature = float(request.form["temperature"])
    rainfall = float(request.form["rainfall"])
    soil_moisture = float(request.form["soil_moisture"])
    fertilizer = float(request.form["fertilizer"])
    pesticide = float(request.form["pesticide"])
    
    # Create input using the saved feature defaults
    input_data = feature_defaults.copy()
    reference_data = X_train_reference.copy()
    input_values = pd.Series({
    "farm_size_hectares": farm_size,
    "avg_temperature_c": temperature,
    "annual_rainfall_mm": rainfall,
    "soil_moisture_percent": soil_moisture,
    "fertilizer_kg_per_ha": fertilizer,
    "pesticide_litre_per_ha": pesticide
})

    reference_features = reference_data[input_values.index]

    reference_mean = reference_features.mean()
    reference_std = reference_features.std()

    normalized_reference = (reference_features - reference_mean) / reference_std
    normalized_input = (input_values - reference_mean) / reference_std

    distances = (
       (normalized_reference - normalized_input) ** 2
).sum(axis=1)

    nearest_index = distances.idxmin()
    input_data = reference_data.loc[nearest_index].copy()
 
    # Replace user-entered values
    input_data["farm_size_hectares"] = farm_size
    input_data["avg_temperature_c"] = temperature
    input_data["annual_rainfall_mm"] = rainfall
    input_data["soil_moisture_percent"] = soil_moisture
    fertilizer = float(request.form["fertilizer"])
    pesticide = float(request.form["pesticide"])
    

    input_data["fertilizer_kg_per_ha"] = fertilizer
    input_data["pesticide_litre_per_ha"] = pesticide
    
    print("USER INPUT:", farm_size, temperature, rainfall, soil_moisture, fertilizer, pesticide)

    print("MODEL INPUT:", input_data[["farm_size_hectares", "avg_temperature_c",
                                     "annual_rainfall_mm", "soil_moisture_percent",
                                     "fertilizer_kg_per_ha", "pesticide_litre_per_ha"]])

    input_df = pd.DataFrame([input_data], columns=feature_columns)

    # Scale the input
    input_scaled = scaler.transform(input_df)
    # Predict
    prediction = model.predict(input_scaled)[0]
    return f'''
    



<body style="background:#e8f5e9; min-height:100vh; margin:0;
display:flex; justify-content:center; align-items:center;">
    <div style="background:#c8e6c9; color:#2e6b3e; padding:40px;
                border-radius:20px; font-size:28px; text-align:center;">
        Predicted Crop Yield: {prediction:.2f} ton/ha
    </div>

</body>
'''


if __name__ == "__main__":
    app.run(debug=True)