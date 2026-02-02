import numpy as np
from tensorflow.keras.models import load_model
import pickle, os

# Load model and scaler
base = os.path.dirname(__file__)
model = load_model(
    os.path.join(base, "../lstm/global_lstm_model"),
    compile=False
)

with open(os.path.join(base, "../lstm/scaler.pkl"), "rb") as f:
    scaler = pickle.load(f)

def predict_demand(product, sales_history):
    if not sales_history:
        return 0.0

    # Convert to array and scale
    sales_history = np.array(sales_history).reshape(-1, 1)
    sales_history = scaler.transform(sales_history)

    # Model expects 2 features → create a dummy second column (zeros)
    second_feature = np.zeros((len(sales_history), 1))
    combined = np.hstack([sales_history, second_feature])

    expected_timesteps = model.input_shape[1]

    # Pad or trim sequence to match model’s expected length
    if len(combined) < expected_timesteps:
        pad_width = expected_timesteps - len(combined)
        combined = np.pad(combined, ((pad_width, 0), (0, 0)), mode="edge")
    elif len(combined) > expected_timesteps:
        combined = combined[-expected_timesteps:]

    # Reshape for LSTM input: (1, timesteps, features)
    x_input = np.reshape(combined, (1, expected_timesteps, 2))

    # Predict and inverse transform
    forecast = model.predict(x_input)
    return float(scaler.inverse_transform(forecast)[0][0])
