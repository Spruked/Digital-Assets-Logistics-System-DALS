# predictive_engine.py

"""
Predictive Engine - Advanced Forecasting and Pattern Recognition

This module provides predictive analytics capabilities for the vault system,
including pattern recognition, trend analysis, and future state forecasting.
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque
import statistics
import math
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')


class PredictionModel(Enum):
    """Types of prediction models"""
    LINEAR_REGRESSION = "linear_regression"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    ARIMA = "arima"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"


class PredictionHorizon(Enum):
    """Prediction time horizons"""
    SHORT_TERM = "short_term"      # 1-7 days
    MEDIUM_TERM = "medium_term"    # 1-4 weeks
    LONG_TERM = "long_term"        # 1-12 months
    STRATEGIC = "strategic"        # 1+ years


@dataclass
class PredictionResult:
    """
    Result of a prediction operation.
    """
    model_type: PredictionModel
    horizon: PredictionHorizon
    predicted_values: List[float]
    confidence_intervals: Optional[List[Tuple[float, float]]] = None
    accuracy_score: Optional[float] = None
    feature_importance: Optional[Dict[str, float]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class PatternRecognition:
    """
    Recognized pattern in data.
    """
    pattern_type: str
    confidence: float
    occurrences: List[datetime]
    trend_direction: str  # "increasing", "decreasing", "stable"
    seasonality_period: Optional[int] = None
    anomaly_score: Optional[float] = None


class PredictiveEngine:
    """
    Advanced predictive analytics engine for the vault system.

    Provides forecasting, pattern recognition, anomaly detection,
    and trend analysis capabilities.
    """

    def __init__(self, telemetry_stream, reflection_manager):
        """
        Initialize predictive engine.

        Args:
            telemetry_stream: Telemetry stream for data access
            reflection_manager: Reflection manager for learning
        """
        self.telemetry_stream = telemetry_stream
        self.reflection_manager = reflection_manager

        # Prediction models
        self.models = {}
        self.active_models: Dict[str, PredictionModel] = {}

        # Historical data storage
        self.historical_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.data_window_size = 1000

        # Pattern recognition
        self.patterns: Dict[str, List[PatternRecognition]] = defaultdict(list)
        self.pattern_threshold = 0.75

        # Anomaly detection
        self.anomaly_detector = None
        self.anomaly_threshold = 3.0  # Standard deviations

        # Forecasting cache
        self.forecast_cache: Dict[str, PredictionResult] = {}
        self.cache_ttl = timedelta(hours=1)

        # Performance metrics
        self.prediction_accuracy = {
            "total_predictions": 0,
            "accurate_predictions": 0,
            "mean_absolute_error": 0.0,
            "root_mean_squared_error": 0.0
        }

        print("🔮 Predictive Engine initialized")

    def register_prediction_model(self, metric_name: str, model_type: PredictionModel,
                                horizon: PredictionHorizon):
        """
        Register a prediction model for a metric.

        Args:
            metric_name: Name of the metric to predict
            model_type: Type of prediction model
            horizon: Prediction horizon
        """
        model_key = f"{metric_name}_{model_type.value}_{horizon.value}"

        self.active_models[model_key] = model_type

        # Initialize model based on type
        if model_type == PredictionModel.LINEAR_REGRESSION:
            self.models[model_key] = LinearRegression()
        elif model_type == PredictionModel.EXPONENTIAL_SMOOTHING:
            self.models[model_key] = {"alpha": 0.3, "data": []}
        elif model_type == PredictionModel.ARIMA:
            self.models[model_key] = {"order": (1, 1, 1), "data": []}
        elif model_type == PredictionModel.NEURAL_NETWORK:
            # Simplified neural network placeholder
            self.models[model_key] = {"weights": np.random.randn(10, 1), "biases": np.random.randn(1)}
        elif model_type == PredictionModel.ENSEMBLE:
            self.models[model_key] = {
                "models": [LinearRegression(), {"alpha": 0.3, "data": []}],
                "weights": [0.6, 0.4]
            }

        print(f"✅ Registered prediction model: {model_key}")

    def unregister_prediction_model(self, metric_name: str, model_type: PredictionModel,
                                  horizon: PredictionHorizon):
        """
        Unregister a prediction model.

        Args:
            metric_name: Metric name
            model_type: Model type
            horizon: Prediction horizon
        """
        model_key = f"{metric_name}_{model_type.value}_{horizon.value}"

        if model_key in self.active_models:
            del self.active_models[model_key]

        if model_key in self.models:
            del self.models[model_key]

        print(f"✅ Unregistered prediction model: {model_key}")

    def update_historical_data(self, metric_name: str, value: float, timestamp: Optional[datetime] = None):
        """
        Update historical data for a metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            timestamp: Timestamp (current time if None)
        """
        if timestamp is None:
            timestamp = datetime.now()

        data_point = {
            "timestamp": timestamp,
            "value": value
        }

        self.historical_data[metric_name].append(data_point)

        # Keep only recent data
        while len(self.historical_data[metric_name]) > self.data_window_size:
            self.historical_data[metric_name].popleft()

    def get_historical_data(self, metric_name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get historical data for a metric.

        Args:
            metric_name: Metric name
            hours: Hours of history to retrieve

        Returns:
            List of historical data points
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        data = list(self.historical_data[metric_name])
        return [point for point in data if point["timestamp"] >= cutoff_time]

    async def generate_prediction(self, metric_name: str, model_type: PredictionModel,
                                horizon: PredictionHorizon, steps: int = 10) -> Optional[PredictionResult]:
        """
        Generate a prediction for a metric.

        Args:
            metric_name: Metric name
            model_type: Prediction model type
            horizon: Prediction horizon
            steps: Number of prediction steps

        Returns:
            Prediction result or None if insufficient data
        """
        model_key = f"{metric_name}_{model_type.value}_{horizon.value}"

        # Check cache first
        if model_key in self.forecast_cache:
            cached_result = self.forecast_cache[model_key]
            if cached_result.timestamp is not None and (datetime.now() - cached_result.timestamp < self.cache_ttl):
                return cached_result

        # Get historical data
        data = self.get_historical_data(metric_name)
        if len(data) < 10:  # Minimum data requirement
            return None

        values = [point["value"] for point in data]

        try:
            if model_type == PredictionModel.LINEAR_REGRESSION:
                result = self._predict_linear_regression(values, steps)
            elif model_type == PredictionModel.EXPONENTIAL_SMOOTHING:
                result = self._predict_exponential_smoothing(values, steps)
            elif model_type == PredictionModel.ARIMA:
                result = self._predict_arima(values, steps)
            elif model_type == PredictionModel.NEURAL_NETWORK:
                result = self._predict_neural_network(values, steps)
            elif model_type == PredictionModel.ENSEMBLE:
                result = self._predict_ensemble(values, steps)
            else:
                return None

            # Cache result
            self.forecast_cache[model_key] = result

            # Update performance metrics
            self._update_prediction_accuracy(result, values)

            return result

        except Exception as e:
            print(f"❌ Prediction failed for {metric_name}: {e}")
            return None

    def _predict_linear_regression(self, values: List[float], steps: int) -> PredictionResult:
        """Generate linear regression prediction"""
        # Prepare data
        X = np.arange(len(values)).reshape(-1, 1)
        y = np.array(values)

        # Fit model
        model = LinearRegression()
        model.fit(X, y)

        # Generate predictions
        future_X = np.arange(len(values), len(values) + steps).reshape(-1, 1)
        predictions = model.predict(future_X)

        # Calculate confidence intervals (simplified)
        residuals = y - model.predict(X)
        std_error = np.std(residuals)
        confidence_interval = 1.96 * std_error  # 95% confidence

        confidence_intervals = [
            (pred - confidence_interval, pred + confidence_interval)
            for pred in predictions
        ]

        return PredictionResult(
            model_type=PredictionModel.LINEAR_REGRESSION,
            horizon=PredictionHorizon.SHORT_TERM,  # Simplified
            predicted_values=predictions.tolist(),
            confidence_intervals=confidence_intervals,
            accuracy_score=float(model.score(X, y))
        )

    def _predict_exponential_smoothing(self, values: List[float], steps: int) -> PredictionResult:
        """Generate exponential smoothing prediction"""
        alpha = 0.3
        smoothed = [values[0]]

        # Apply exponential smoothing
        for i in range(1, len(values)):
            smoothed_value = alpha * values[i] + (1 - alpha) * smoothed[-1]
            smoothed.append(smoothed_value)

        # Forecast future values
        last_smoothed = smoothed[-1]
        predictions = []

        for _ in range(steps):
            next_value = alpha * last_smoothed + (1 - alpha) * last_smoothed
            predictions.append(next_value)
            last_smoothed = next_value

        return PredictionResult(
            model_type=PredictionModel.EXPONENTIAL_SMOOTHING,
            horizon=PredictionHorizon.SHORT_TERM,
            predicted_values=predictions
        )

    def _predict_arima(self, values: List[float], steps: int) -> PredictionResult:
        """Generate ARIMA prediction (simplified implementation)"""
        # Simplified ARIMA implementation
        # In a real implementation, you'd use statsmodels or similar

        # Calculate trend
        if len(values) >= 3:
            trend = (values[-1] - values[0]) / len(values)
        else:
            trend = 0

        # Generate predictions with trend
        last_value = values[-1]
        predictions = []

        for i in range(steps):
            next_value = last_value + trend
            predictions.append(next_value)
            last_value = next_value

        return PredictionResult(
            model_type=PredictionModel.ARIMA,
            horizon=PredictionHorizon.MEDIUM_TERM,
            predicted_values=predictions
        )

    def _predict_neural_network(self, values: List[float], steps: int) -> PredictionResult:
        """Generate neural network prediction (simplified)"""
        # Very simplified neural network
        # Normalize data
        scaler = StandardScaler()
        normalized_values = scaler.fit_transform(np.array(values).reshape(-1, 1)).flatten()

        # Simple prediction based on recent trend
        recent_trend = np.mean(np.diff(normalized_values[-10:])) if len(values) >= 10 else 0

        # Generate predictions
        last_value = normalized_values[-1]
        predictions = []

        for _ in range(steps):
            next_value = last_value + recent_trend
            predictions.append(next_value)
            last_value = next_value

        # Denormalize predictions
        predictions_array = np.array(predictions).reshape(-1, 1)
        denormalized_predictions = scaler.inverse_transform(predictions_array).flatten()

        return PredictionResult(
            model_type=PredictionModel.NEURAL_NETWORK,
            horizon=PredictionHorizon.MEDIUM_TERM,
            predicted_values=denormalized_predictions.tolist()
        )

    def _predict_ensemble(self, values: List[float], steps: int) -> PredictionResult:
        """Generate ensemble prediction"""
        # Combine multiple models
        lr_result = self._predict_linear_regression(values, steps)
        es_result = self._predict_exponential_smoothing(values, steps)

        # Weighted average
        lr_weight = 0.6
        es_weight = 0.4

        ensemble_predictions = []
        for lr_pred, es_pred in zip(lr_result.predicted_values, es_result.predicted_values):
            ensemble_pred = lr_weight * lr_pred + es_weight * es_pred
            ensemble_predictions.append(ensemble_pred)

        return PredictionResult(
            model_type=PredictionModel.ENSEMBLE,
            horizon=PredictionHorizon.MEDIUM_TERM,
            predicted_values=ensemble_predictions
        )

    def _update_prediction_accuracy(self, result: PredictionResult, actual_values: List[float]):
        """Update prediction accuracy metrics"""
        if len(actual_values) < 2:
            return

        # Calculate error metrics (simplified)
        if result.predicted_values:
            # Use last actual value as baseline
            baseline_error = abs(actual_values[-1] - actual_values[-2]) if len(actual_values) >= 2 else 0
            prediction_error = abs(result.predicted_values[0] - actual_values[-1])

            # Update accuracy if prediction was better than baseline
            self.prediction_accuracy["total_predictions"] += 1
            if prediction_error <= baseline_error:
                self.prediction_accuracy["accurate_predictions"] += 1

    async def detect_patterns(self, metric_name: str) -> List[PatternRecognition]:
        """
        Detect patterns in metric data.

        Args:
            metric_name: Metric name

        Returns:
            List of detected patterns
        """
        data = self.get_historical_data(metric_name, hours=168)  # Last week
        if len(data) < 20:
            return []

        values = [point["value"] for point in data]
        timestamps = [point["timestamp"] for point in data]

        patterns = []

        # Trend detection
        trend_pattern = self._detect_trend_pattern(values, timestamps)
        if trend_pattern:
            patterns.append(trend_pattern)

        # Seasonality detection
        seasonal_pattern = self._detect_seasonal_pattern(values, timestamps)
        if seasonal_pattern:
            patterns.append(seasonal_pattern)

        # Anomaly detection
        anomalies = self._detect_anomalies(values, timestamps)
        patterns.extend(anomalies)

        # Update pattern storage
        self.patterns[metric_name] = patterns

        return patterns

    def _detect_trend_pattern(self, values: List[float], timestamps: List[datetime]) -> Optional[PatternRecognition]:
        """Detect trend patterns"""
        if len(values) < 10:
            return None

        # Calculate trend using linear regression
        X = np.arange(len(values)).reshape(-1, 1)
        y = np.array(values)

        model = LinearRegression()
        model.fit(X, y)

        slope = model.coef_[0]
        r_squared = model.score(X, y)

        if r_squared < self.pattern_threshold:
            return None

        # Determine trend direction
        if slope > 0.01:
            direction = "increasing"
        elif slope < -0.01:
            direction = "decreasing"
        else:
            direction = "stable"

        return PatternRecognition(
            pattern_type="trend",
            confidence=float(r_squared),
            occurrences=timestamps,
            trend_direction=direction
        )

    def _detect_seasonal_pattern(self, values: List[float], timestamps: List[datetime]) -> Optional[PatternRecognition]:
        """Detect seasonal patterns"""
        if len(values) < 50:  # Need more data for seasonality
            return None

        # Simple autocorrelation-based seasonality detection
        # This is a simplified implementation

        # Calculate autocorrelation for different lags
        autocorr = []
        for lag in range(1, min(24, len(values)//2)):  # Up to 24 hours
            if len(values) > lag:
                corr = np.corrcoef(values[:-lag], values[lag:])[0, 1]
                autocorr.append((lag, abs(corr)))

        if not autocorr:
            return None

        # Find strongest correlation
        best_lag, best_corr = max(autocorr, key=lambda x: x[1])

        if best_corr < self.pattern_threshold:
            return None

        return PatternRecognition(
            pattern_type="seasonal",
            confidence=best_corr,
            occurrences=timestamps,
            trend_direction="stable",  # Seasonality doesn't imply overall trend
            seasonality_period=best_lag
        )

    def _detect_anomalies(self, values: List[float], timestamps: List[datetime]) -> List[PatternRecognition]:
        """Detect anomalous patterns"""
        if len(values) < 10:
            return []

        # Calculate rolling statistics
        window_size = min(20, len(values)//2)
        rolling_mean = pd.Series(values).rolling(window=window_size).mean()
        rolling_std = pd.Series(values).rolling(window=window_size).std()

        anomalies = []

        for i in range(window_size, len(values)):
            if pd.isna(rolling_mean[i]) or pd.isna(rolling_std[i]):
                continue

            z_score = abs(values[i] - rolling_mean[i]) / rolling_std[i]

            if z_score > self.anomaly_threshold:
                anomaly = PatternRecognition(
                    pattern_type="anomaly",
                    confidence=min(z_score / self.anomaly_threshold, 1.0),
                    occurrences=[timestamps[i]],
                    trend_direction="stable",
                    anomaly_score=z_score
                )
                anomalies.append(anomaly)

        return anomalies

    def get_prediction_accuracy(self) -> Dict[str, Any]:
        """Get prediction accuracy metrics"""
        total = self.prediction_accuracy["total_predictions"]

        return {
            "total_predictions": total,
            "accurate_predictions": self.prediction_accuracy["accurate_predictions"],
            "accuracy_rate": round(self.prediction_accuracy["accurate_predictions"] / total * 100, 1) if total > 0 else 0,
            "mean_absolute_error": round(self.prediction_accuracy["mean_absolute_error"], 3),
            "root_mean_squared_error": round(self.prediction_accuracy["root_mean_squared_error"], 3)
        }

    def get_patterns(self, metric_name: str) -> List[Dict[str, Any]]:
        """
        Get detected patterns for a metric.

        Args:
            metric_name: Metric name

        Returns:
            List of pattern information
        """
        patterns = self.patterns.get(metric_name, [])

        return [
            {
                "pattern_type": p.pattern_type,
                "confidence": round(p.confidence, 3),
                "occurrences": len(p.occurrences),
                "trend_direction": p.trend_direction,
                "seasonality_period": p.seasonality_period,
                "anomaly_score": round(p.anomaly_score, 3) if p.anomaly_score else None
            }
            for p in patterns
        ]

    async def generate_forecast_report(self, metric_names: List[str]) -> Dict[str, Any]:
        """
        Generate a comprehensive forecast report.

        Args:
            metric_names: List of metrics to forecast

        Returns:
            Forecast report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "patterns": {},
            "recommendations": []
        }

        for metric_name in metric_names:
            # Generate predictions
            predictions = {}
            for model_type in PredictionModel:
                for horizon in PredictionHorizon:
                    try:
                        result = await self.generate_prediction(metric_name, model_type, horizon)
                        if result:
                            key = f"{model_type.value}_{horizon.value}"
                            predictions[key] = {
                                "values": result.predicted_values[:5],  # First 5 predictions
                                "confidence": result.accuracy_score
                            }
                    except Exception as e:
                        print(f"⚠️  Failed to generate prediction for {metric_name}: {e}")

            # Detect patterns
            patterns = await self.detect_patterns(metric_name)

            report["metrics"][metric_name] = {
                "predictions": predictions,
                "current_value": self.get_historical_data(metric_name, hours=1)[-1]["value"] if self.get_historical_data(metric_name, hours=1) else None
            }

            report["patterns"][metric_name] = [
                {
                    "type": p.pattern_type,
                    "confidence": round(p.confidence, 3),
                    "direction": p.trend_direction
                }
                for p in patterns
            ]

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on forecast report"""
        recommendations = []

        for metric_name, data in report["metrics"].items():
            predictions = data.get("predictions", {})

            # Check for concerning trends
            concerning_patterns = [
                p for p in report["patterns"].get(metric_name, [])
                if p["type"] in ["anomaly", "trend"] and p["direction"] in ["decreasing"]
            ]

            if concerning_patterns:
                recommendations.append(f"Monitor {metric_name} - concerning patterns detected")

            # Check prediction consistency
            if len(predictions) > 1:
                confidences = [p.get("confidence", 0) for p in predictions.values() if p.get("confidence")]
                if confidences and statistics.stdev(confidences) > 0.2:
                    recommendations.append(f"Review prediction models for {metric_name} - inconsistent results")

        if not recommendations:
            recommendations.append("All metrics showing normal patterns")

        return recommendations

    def clear_cache(self):
        """Clear prediction cache"""
        self.forecast_cache.clear()
        print("🧹 Prediction cache cleared")

    def get_system_health(self) -> Dict[str, Any]:
        """Get predictive engine health status"""
        return {
            "active_models": len(self.active_models),
            "cached_predictions": len(self.forecast_cache),
            "historical_data_points": sum(len(data) for data in self.historical_data.values()),
            "detected_patterns": sum(len(patterns) for patterns in self.patterns.values()),
            "prediction_accuracy": self.get_prediction_accuracy()
        }