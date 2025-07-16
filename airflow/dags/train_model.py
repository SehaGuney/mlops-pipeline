# train_model.py
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

def train():
    mlflow.start_run()
    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42
    )
    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(X_train, y_train)
    acc = clf.score(X_test, y_test)
    mlflow.log_metric("accuracy", acc)
    mlflow.sklearn.log_model(clf, "rf_model")
    mlflow.end_run()

if __name__ == "__main__":
    train()
