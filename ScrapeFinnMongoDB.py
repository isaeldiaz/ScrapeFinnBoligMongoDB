import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# Load your data
data = pd.read_csv('bil_data.csv')
km_price_data = data[['ad_km', 'ad_price']]

# Create polynomial features
poly = PolynomialFeatures(degree=2)
X = km_price_data[['ad_km']]
y = km_price_data['ad_price']
X_poly = poly.fit_transform(X)

# Fit polynomial regression model
poly_model = LinearRegression()
poly_model.fit(X_poly, y)

# Generating points for a smooth curve
X_fit = np.linspace(X.min(), X.max(), 100)
y_poly_pred = poly_model.predict(poly.fit_transform(X_fit.reshape(-1, 1)))

# Plotting
plt.figure(figsize=(10, 6))
plt.scatter(km_price_data['ad_km'], km_price_data['ad_price'], alpha=0.5)
plt.plot(X_fit, y_poly_pred, color='green', linewidth=2, label='2nd Order Polynomial Fit')
plt.title('Scatter plot of Kilometers vs Price with Polynomial Fit')
plt.xlabel('Kilometers (km)')
plt.ylabel('Price (SEK)')
plt.legend()
plt.grid(True)
plt.show()

