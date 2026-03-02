from app import app
from models.database import db, Prediction
from datetime import datetime, timedelta
import json

with app.app_context():
    print("🔮 Generating sample predictions...")
    
    # Clear old predictions
    Prediction.query.delete()
    db.session.commit()
    
    predictions_data = [
        {
            'title': 'Dengue Outbreak Risk - Delhi NCR',
            'description': 'Increased rainfall and temperature patterns indicate high dengue risk. Mosquito breeding conditions optimal. Hospital admissions rising.',
            'category': 'health',
            'severity': 'high',
            'confidence': 0.82,
            'predicted_date': datetime.utcnow() + timedelta(days=15),
            'location': 'Delhi',
            'evidence': json.dumps({
                'rainfall': '+40% above normal',
                'temperature': '28-32°C ideal for breeding',
                'hospital_queries': '+45% YoY',
                'sources': ['Health Ministry', 'IMD', 'AIIMS Delhi']
            })
        },
        {
            'title': 'Onion Price Spike Expected',
            'description': 'Warehouse stocks 35% below normal. Late monsoon damaged Kharif crop. Transport costs rising due to fuel prices. Retail prices may hit ₹80-100/kg.',
            'category': 'economy',
            'severity': 'medium',
            'confidence': 0.76,
            'predicted_date': datetime.utcnow() + timedelta(days=12),
            'location': 'National',
            'evidence': json.dumps({
                'stock_level': '35% below normal',
                'crop_damage': '20% Kharif loss',
                'transport_cost': '+15%',
                'sources': ['Agriculture Ministry', 'Market Committees']
            })
        },
        {
            'title': 'Water Shortage Warning - Bangalore',
            'description': 'Reservoir levels 22% below last year. Rainfall deficit 18%. Summer demand increasing. Water rationing likely by April.',
            'category': 'environment',
            'severity': 'high',
            'confidence': 0.79,
            'predicted_date': datetime.utcnow() + timedelta(days=25),
            'location': 'Bangalore',
            'evidence': json.dumps({
                'reservoir_level': '65% vs 78% last year',
                'rainfall_deficit': '18%',
                'demand_growth': '+12%',
                'sources': ['BWSSB', 'Karnataka Water Board']
            })
        },
        {
            'title': 'Fuel Price Hike Imminent',
            'description': 'Crude oil at $88/barrel due to Middle East tensions. Rupee weakening. OMCs absorbing ₹6/L loss. Petrol may increase by ₹4-5/L.',
            'category': 'economy',
            'severity': 'medium',
            'confidence': 0.73,
            'predicted_date': datetime.utcnow() + timedelta(days=7),
            'location': 'National',
            'evidence': json.dumps({
                'crude_price': '$88/barrel (+12%)',
                'rupee': '₹83.5/$ (-2%)',
                'omc_loss': '₹6/L',
                'sources': ['PPAC', 'Oil Ministry']
            })
        },
        {
            'title': 'Flood Alert - Coastal Karnataka',
            'description': 'IMD predicts heavy rainfall 150-200mm in 48hrs. Dams at 85% capacity. Low-lying areas at risk. Evacuation advisory issued.',
            'category': 'environment',
            'severity': 'high',
            'confidence': 0.88,
            'predicted_date': datetime.utcnow() + timedelta(days=2),
            'location': 'Coastal Karnataka',
            'evidence': json.dumps({
                'rainfall_prediction': '150-200mm/48hrs',
                'dam_capacity': '85%',
                'advisory': 'Orange alert issued',
                'sources': ['IMD', 'Karnataka SDMA']
            })
        },
        {
            'title': 'Wheat Procurement Target at Risk',
            'description': 'Early heatwave damaged crops in Punjab, Haryana. Production estimates down 8%. MSP procurement may fall short of 35 MT target.',
            'category': 'agriculture',
            'severity': 'medium',
            'confidence': 0.71,
            'predicted_date': datetime.utcnow() + timedelta(days=20),
            'location': 'Punjab, Haryana',
            'evidence': json.dumps({
                'production_loss': '8% estimated',
                'heatwave_days': '15 days >40°C',
                'target': '35 MT',
                'sources': ['Agriculture Ministry', 'FCI']
            })
        },
        {
            'title': 'Air Quality Crisis - Delhi',
            'description': 'Stubble burning season starting. Wind patterns unfavorable. AQI may exceed 400 (severe) in November. Health advisory likely.',
            'category': 'environment',
            'severity': 'high',
            'confidence': 0.84,
            'predicted_date': datetime.utcnow() + timedelta(days=30),
            'location': 'Delhi NCR',
            'evidence': json.dumps({
                'stubble_fires': '+150 detected',
                'wind_direction': 'Towards Delhi',
                'historical_aqi': 'Average 420 same period',
                'sources': ['CPCB', 'SAFAR', 'NASA FIRMS']
            })
        },
    ]
    
    for pred_data in predictions_data:
        pred = Prediction(**pred_data)
        db.session.add(pred)
    
    db.session.commit()
    
    print(f"✅ Generated {len(predictions_data)} predictions")
    print("\nPredictions by severity:")
    print(f"   - High: {len([p for p in predictions_data if p['severity'] == 'high'])}")
    print(f"   - Medium: {len([p for p in predictions_data if p['severity'] == 'medium'])}")
    print(f"   - Low: {len([p for p in predictions_data if p['severity'] == 'low'])}")