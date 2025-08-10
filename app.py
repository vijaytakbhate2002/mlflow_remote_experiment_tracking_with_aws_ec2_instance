import pandas as pd
import sys
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import train_test_split
import mlflow
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from urllib import parse
import os
from mlflow.models.signature import infer_signature
import boto3

os.environ["MLFLOW_TRACKING_URI"] = "ENTER YOUR TRACKING URI GENERATED FROM AWS EC2 INSTANCE"
os.environ['MLFLOW_TRACKING_USERNAME'] = 'ENTER YOUR USERNAME USED FOR AWS ACCOUNT'
os.environ['MLFLOW_TRACKING_PASSWORD'] = 'ENTER YOUR PASSWORD USED FOR AWS ACCOUNT'

def evalulate_model(y_true, y_pred):
    """
    Evaluate the model's predictions against the true values."""
    mse = mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    return mse, r2, mae

alpha = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
l1_ratio = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

print(f"Alpha: {alpha}, L1 Ratio: {l1_ratio}")

if __name__ == "__main__":

    data_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-white.csv"
    input_df = pd.read_csv(data_url, sep=';')

    train_x, test_x, train_y, test_y = train_test_split(input_df.drop(['quality'], axis='columns'), input_df['quality'])

    with mlflow.start_run():

        model = ElasticNet(
        alpha=alpha,
        l1_ratio=l1_ratio
            )
        model.fit(train_x, train_y)

        pred_y = model.predict(test_x)
        (mse, r2, mae) = evalulate_model(test_y, pred_y)

        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)

        mlflow.log_metric("mse", mse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)

        tracking_uri = "http://ec2-51-20-114-151.eu-north-1.compute.amazonaws.com:5000/"
        mlflow.set_tracking_uri(tracking_uri)
        tracking_uri_sheme = parse.urlparse(mlflow.get_tracking_uri()).scheme

        print("tracking_uri_sheme", tracking_uri_sheme)

        signature = infer_signature(test_x, pred_y)

        print("signature", signature)

        if tracking_uri_sheme != "file":
            print("logging model to remote uri tracking mlflow ... ")
            mlflow.sklearn.log_model(
                model, 
                name="model",  
                registered_model_name="WINE_QUALITY_ELASTIC_NET_MODEL",
                signature=signature
                )
        else:
            print("logging model to local uri tracking mlflow ... ")
            mlflow.sklearn.log_model(
                model, 
                name="model",
                signature=signature
            )
        print("model logged successfully ... ")






        

