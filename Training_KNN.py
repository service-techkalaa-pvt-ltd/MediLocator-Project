import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
import pickle

# --- Step 1: Load dataset ---
df = pd.read_excel('Medical_Final_Dataset.xlsx')

print(df.columns)
# Columns assumed: ['address', 'latitude', 'longitude', 'rating']

# --- Step 2: Prepare features and labels ---
x = df[['Latitude', 'Longitude']].values      # Features: only lat & lon
y = df['Address'].values                       # Labels: addresses

# --- Step 3: Scale features for KNN ---
scaler = StandardScaler()
x_scaled = scaler.fit_transform(x)

# --- Step 4: Train KNN ---
model = KNeighborsClassifier(n_neighbors=3)
model.fit(x_scaled, y)   # Train on lat/lon to predict address

# --- Step 5: Save model, scaler, and full dataframe for rating lookup ---
data_to_save = {
    'model': model,
    'scaler': scaler,
    'df': df
}
pickle.dump(data_to_save, open('knn_address_model.sav', 'wb'))
print("Model saved successfully.")

