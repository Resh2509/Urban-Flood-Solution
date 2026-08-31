import os
import glob
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import GradientBoostingClassifier
try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

class BlockageDetectionEngine:
    def __init__(self, data_dir: str = "hydro_twin_Data"):
        self.data_dir = data_dir
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_columns = [
            "rainfall_mm",
            "flow_in_lps",
            "flow_out_lps",
            "water_level_cm",
            "water_accumulation_lps",
            "flow_capacity_ratio"
        ]

    def _resolve_file(self, keyword: str) -> str:
        matched = glob.glob(os.path.join(self.data_dir, f"*{keyword}*.csv"))
        if not matched:
            for f in os.listdir(self.data_dir):
                if keyword.lower() in f.lower() and f.endswith(".csv"):
                    return os.path.join(self.data_dir, f)
            raise FileNotFoundError(f"Missing CSV containing '{keyword}' in '{self.data_dir}'")
        return matched[0]

    def load_training_data(self) -> pd.DataFrame:
        obs_file = self._resolve_file("hydraulic_obs")
        labels_file = self._resolve_file("blockage_label")

        df_obs = pd.read_csv(obs_file, encoding="utf-8-sig")
        df_obs.columns = df_obs.columns.str.strip()

        df_labels = pd.read_csv(labels_file, encoding="utf-8-sig")
        df_labels.columns = df_labels.columns.str.strip()

        # Merge on timestamp and node_id
        df_merged = df_obs.merge(df_labels, on=["timestamp", "node_id"], suffixes=("_obs", "_lbl"))
        return df_merged

    def train_model(self) -> dict:
        """Trains the ML blockage classifier and saves model artifacts."""
        df = self.load_training_data()

        X = df[self.feature_columns].fillna(0)
        y = df["blockage_status"].astype(str).str.strip()

        y_encoded = self.label_encoder.fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

        if HAS_XGBOOST:
            self.model = XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42,
                eval_metric="mlogloss"
            )
        else:
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )

        self.model.fit(X_train, y_train)
        accuracy = float(self.model.score(X_test, y_test))

        # Save model and encoder
        model_save_path = os.path.join(self.data_dir, "blockage_classifier_day3.joblib")
        joblib.dump({"model": self.model, "encoder": self.label_encoder, "features": self.feature_columns}, model_save_path)

        return {
            "accuracy": round(accuracy * 100.0, 2),
            "samples": len(df),
            "classes": list(self.label_encoder.classes_),
            "model_path": model_save_path
        }

    def predict_blockages(self, live_df: pd.DataFrame) -> pd.DataFrame:
        """Infers blockage state and risk score for real-time physics observations."""
        if self.model is None:
            raise RuntimeError("Model is not trained. Call train_model() first.")

        X_input = live_df[self.feature_columns].fillna(0)
        pred_encoded = self.model.predict(X_input)
        pred_probs = self.model.predict_proba(X_input)

        live_df["predicted_blockage_status"] = self.label_encoder.inverse_transform(pred_encoded)
        # Blockage probability: sum probabilities of non-normal states
        normal_idx = list(self.label_encoder.classes_).index("Normal") if "Normal" in self.label_encoder.classes_ else 0
        live_df["blockage_probability"] = [round(1.0 - p[normal_idx], 3) for p in pred_probs]
        
        return live_df