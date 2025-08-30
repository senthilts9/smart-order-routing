"""ML Routing Engine for Smart Order Routing"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from dataclasses import dataclass
from typing import List, Dict, Tuple
import time
from collections import deque

@dataclass
class ExchangeFeatures:
    exchange_id: str
    latency_ms: float
    liquidity_score: float
    spread: float
    volume_imbalance: float
    historical_fill_rate: float
    fee_percentage: float
    market_impact_estimate: float


class MLRoutingEngine:
    """Machine Learning engine for optimal order routing"""
    
    def __init__(self):
        self.impact_model = RandomForestRegressor(
            n_estimators=100, 
            max_depth=10,
            random_state=42
        )
        self.routing_model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.performance_history = deque(maxlen=1000)
        self.is_trained = False
        
        # Initialize with synthetic training data
        self._train_models()
    
    def _generate_synthetic_data(self, n_samples=10000):
        """Generate synthetic training data for the models"""
        np.random.seed(42)
        
        # Features
        latency = np.random.exponential(5, n_samples)
        liquidity = np.random.uniform(0, 1, n_samples)
        spread = np.random.exponential(0.01, n_samples)
        volume_imbalance = np.random.uniform(-1, 1, n_samples)
        fill_rate = np.random.beta(8, 2, n_samples)
        fees = np.random.uniform(0.001, 0.003, n_samples)
        order_size = np.random.lognormal(5, 1.5, n_samples)
        
        # Market impact
        market_impact = (
            0.001 * np.sqrt(order_size / 1000) +
            0.002 * spread +
            0.0001 * latency +
            np.random.normal(0, 0.0001, n_samples)
        )
        
        # Routing success
        success_prob = (
            0.3 * liquidity +
            0.2 * fill_rate +
            0.1 * (1 - np.tanh(latency/20)) +
            0.2 * (1 - np.tanh(spread*100)) +
            0.2 * (1 - fees*100)
        )
        routing_success = np.random.binomial(1, np.clip(success_prob, 0, 1))
        
        features = np.column_stack([
            latency, liquidity, spread, volume_imbalance,
            fill_rate, fees, order_size
        ])
        
        return features, market_impact, routing_success
    
    def _train_models(self):
        """Train the ML models with synthetic data"""
        X, y_impact, y_routing = self._generate_synthetic_data()
        X_scaled = self.scaler.fit_transform(X)
        self.impact_model.fit(X_scaled, y_impact)
        self.routing_model.fit(X_scaled, y_routing)
        self.is_trained = True
    
    def predict_market_impact(self, features: np.ndarray) -> float:
        """Predict market impact for given features"""
        if not self.is_trained:
            return 0.001
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        return float(self.impact_model.predict(features_scaled)[0])
    
    def predict_routing_success(self, features: np.ndarray) -> Tuple[bool, float]:
        """Predict routing success probability"""
        if not self.is_trained:
            return True, 0.5
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        success = bool(self.routing_model.predict(features_scaled)[0])
        prob = float(self.routing_model.predict_proba(features_scaled)[0, 1])
        return success, prob
    
    def calculate_optimal_routing(self, order_size: float, exchanges: List[ExchangeFeatures]) -> Dict[str, float]:
        """Calculate optimal order routing across exchanges"""
        routing_scores = {}
        
        for exchange in exchanges:
            features = np.array([
                exchange.latency_ms,
                exchange.liquidity_score,
                exchange.spread,
                exchange.volume_imbalance,
                exchange.historical_fill_rate,
                exchange.fee_percentage,
                order_size
            ])
            
            _, success_prob = self.predict_routing_success(features)
            impact = self.predict_market_impact(features)
            
            score = (
                0.3 * success_prob +
                0.2 * exchange.liquidity_score +
                0.2 * (1 - impact*100) +
                0.15 * (1 - exchange.fee_percentage*100) +
                0.15 * (1 - np.tanh(exchange.latency_ms/20))
            )
            
            routing_scores[exchange.exchange_id] = score
        
        total_score = sum(routing_scores.values())
        allocations = {
            ex_id: score/total_score * order_size 
            for ex_id, score in routing_scores.items()
        }
        
        return allocations
    
    def update_performance(self, execution_data: Dict):
        """Update model with execution performance data"""
        self.performance_history.append(execution_data)
