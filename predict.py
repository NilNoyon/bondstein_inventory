from statsmodels.tsa.ar_model import AutoReg
from random import random
# contrived dataset
data = [0,0,2,0]
# fit model
model = AutoReg(data, lags=1)
model_fit = model.fit()
# make prediction
yhat = model_fit.predict(len(data), len(data))
print(yhat[0])