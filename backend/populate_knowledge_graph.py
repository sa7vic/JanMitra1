from app import app
from models.database import db, Entity, Relationship
import json

with app.app_context():
    print("🧹 Clearing existing graph data...")
    Relationship.query.delete()
    Entity.query.delete()
    db.session.commit()
    
    print("📊 Creating entities...")
    
    entities_data = [
        # Places
        ('Delhi', 'place', 'National Capital Territory, 32M population', {'population': 32000000, 'gdp_contribution': '4.5%'}),
        ('Mumbai', 'place', 'Financial capital of India, Maharashtra', {'population': 21000000, 'gdp_contribution': '6.2%'}),
        ('Bangalore', 'place', 'IT hub, Silicon Valley of India', {'population': 13000000, 'it_companies': 4000}),
        ('Chennai', 'place', 'Auto manufacturing hub, Tamil Nadu', {'population': 11000000, 'auto_exports': '$6B'}),
        ('Kolkata', 'place', 'Cultural capital, West Bengal', {'population': 15000000, 'port_traffic': '45M tons'}),
        ('Hyderabad', 'place', 'Pharma capital, Telangana', {'population': 10000000, 'pharma_output': '40%'}),
        ('Pune', 'place', 'Education & IT hub, Maharashtra', {'population': 8000000}),
        ('Ahmedabad', 'place', 'Textile hub, Gujarat', {'population': 8500000}),
        
        # Commodities
        ('Petrol', 'commodity', 'Motor vehicle fuel, ₹102/L average', {'price': 102, 'unit': 'per_liter'}),
        ('Diesel', 'commodity', 'Commercial fuel, ₹88/L average', {'price': 88, 'unit': 'per_liter'}),
        ('Crude Oil', 'commodity', 'Global energy commodity, affects India heavily', {'import_dependency': '85%'}),
        ('Onion', 'commodity', 'Essential vegetable, highly volatile pricing', {'annual_production': '26M tons'}),
        ('Tomato', 'commodity', 'Essential vegetable for Indian cuisine', {'annual_production': '20M tons'}),
        ('Rice', 'commodity', 'Primary staple food grain', {'annual_production': '130M tons'}),
        ('Wheat', 'commodity', 'Secondary staple food grain', {'annual_production': '110M tons'}),
        ('Gold', 'commodity', 'Investment & jewelry commodity', {'imports': '$45B annually'}),
        
        # Economic Indicators
        ('GDP Growth', 'indicator', 'Economic growth rate, 7.2% current', {'current_rate': 7.2, 'target': 8.0}),
        ('Inflation', 'indicator', 'Consumer price inflation, 5.4% current', {'current_rate': 5.4, 'target': 4.0}),
        ('Unemployment', 'indicator', 'Joblessness rate, 8.1% current', {'current_rate': 8.1}),
        ('Rupee-Dollar', 'indicator', 'Exchange rate ₹83/$', {'current_rate': 83}),
        
        # Policies
        ('PM-KISAN', 'policy', 'Direct farmer income support ₹6000/year', {'beneficiaries': '11 crore', 'budget': '₹60,000 crore'}),
        ('Ayushman Bharat', 'policy', 'Health insurance ₹5L per family', {'coverage': '50 crore', 'hospitals': 27000}),
        ('Make in India', 'policy', 'Manufacturing & FDI initiative', {'fdi_increase': '28%'}),
        ('Digital India', 'policy', 'Digital infrastructure program', {'internet_users': '850M'}),
        ('GST', 'policy', 'Goods & Services Tax reform', {'revenue': '₹18L crore annually'}),
        
        # Events
        ('US-Iran Conflict', 'event', 'Middle East tensions affecting oil prices', {'impact': 'high'}),
        ('Monsoon 2026', 'event', 'Annual rainfall pattern critical for agriculture', {'prediction': 'normal'}),
        ('Election 2024', 'event', 'General elections completed', {'voter_turnout': '67%'}),
        ('Dengue Outbreak', 'event', 'Seasonal mosquito-borne disease', {'cases': '200K annually'}),
        
        # Technologies
        ('UPI', 'technology', 'Unified Payments Interface', {'transactions': '12B per month', 'value': '₹18L crore'}),
        ('Aadhaar', 'technology', 'Biometric identity system', {'enrolled': '134 crore'}),
        ('5G Network', 'technology', 'Next-gen mobile network rollout', {'coverage': '50 cities'}),
    ]
    
    entities = {}
    for name, type_, desc, data in entities_data:
        entity = Entity(
            name=name,
            type=type_,
            description=desc,
            data=json.dumps(data)
        )
        db.session.add(entity)
        db.session.flush()
        entities[name] = entity
    
    db.session.commit()
    print(f"✅ Created {len(entities)} entities")
    
    print("🔗 Creating relationships...")
    
    relationships_data = [
        # Oil price chain
        ('US-Iran Conflict', 'Crude Oil', 'causes', 'Geopolitical tensions spike oil prices', 0.85),
        ('Crude Oil', 'Petrol', 'causes', 'Crude price directly affects petrol cost', 0.95),
        ('Crude Oil', 'Diesel', 'causes', 'Crude price directly affects diesel cost', 0.95),
        ('Petrol', 'Inflation', 'causes', 'Transport costs increase overall prices', 0.80),
        ('Diesel', 'Inflation', 'causes', 'Commercial logistics costs rise', 0.85),
        ('Rupee-Dollar', 'Crude Oil', 'affects', 'Weak rupee increases oil import costs', 0.75),
        
        # Agriculture chain
        ('Monsoon 2026', 'Rice', 'affects', 'Rainfall determines rice production', 0.90),
        ('Monsoon 2026', 'Wheat', 'affects', 'Water availability affects yield', 0.85),
        ('Monsoon 2026', 'Onion', 'affects', 'Heavy rain damages onion crops', 0.80),
        ('Rice', 'Inflation', 'affects', 'Food grain prices impact CPI', 0.70),
        ('Wheat', 'Inflation', 'affects', 'Staple food price volatility', 0.70),
        ('Onion', 'Inflation', 'causes', 'Onion price spikes create political pressure', 0.65),
        ('Tomato', 'Inflation', 'affects', 'Vegetable price contribution', 0.60),
        ('PM-KISAN', 'Rice', 'relates_to', 'Farmer income support boosts production', 0.60),
        ('PM-KISAN', 'Wheat', 'relates_to', 'Direct benefit to grain farmers', 0.60),
        
        # Economic relationships
        ('GDP Growth', 'Unemployment', 'affects', 'Growth should reduce joblessness', 0.75),
        ('Inflation', 'Rupee-Dollar', 'affects', 'High inflation weakens rupee', 0.70),
        ('Make in India', 'GDP Growth', 'affects', 'Manufacturing boosts growth', 0.65),
        ('Make in India', 'Unemployment', 'affects', 'Job creation through manufacturing', 0.70),
        ('GST', 'GDP Growth', 'relates_to', 'Tax reform enables business growth', 0.60),
        
        # Technology impact
        ('Digital India', 'UPI', 'causes', 'Policy enabled payment revolution', 0.90),
        ('UPI', 'GDP Growth', 'affects', 'Digital payments boost economy', 0.55),
        ('Aadhaar', 'PM-KISAN', 'relates_to', 'Direct benefit transfer via Aadhaar', 0.85),
        ('Aadhaar', 'Ayushman Bharat', 'relates_to', 'Identity verification for healthcare', 0.85),
        ('5G Network', 'Digital India', 'relates_to', 'Infrastructure for digital transformation', 0.75),
        
        # City-specific
        ('Mumbai', 'GDP Growth', 'relates_to', 'Financial hub drives 6% of GDP', 0.80),
        ('Bangalore', 'Digital India', 'relates_to', 'IT capital central to digital economy', 0.85),
        ('Bangalore', '5G Network', 'relates_to', 'Early 5G adopter city', 0.70),
        ('Delhi', 'Inflation', 'relates_to', 'Capital represents national trends', 0.70),
        ('Hyderabad', 'Ayushman Bharat', 'relates_to', 'Pharma hub for health program', 0.65),
        ('Chennai', 'Make in India', 'relates_to', 'Auto manufacturing center', 0.75),
        
        # Health
        ('Dengue Outbreak', 'Delhi', 'affects', 'Annual monsoon season crisis', 0.75),
        ('Dengue Outbreak', 'Mumbai', 'affects', 'Coastal mosquito breeding', 0.70),
        ('Dengue Outbreak', 'Kolkata', 'affects', 'High humidity region', 0.75),
        ('Ayushman Bharat', 'Dengue Outbreak', 'relates_to', 'Health insurance covers treatment', 0.60),
        ('Monsoon 2026', 'Dengue Outbreak', 'causes', 'Rainfall increases mosquito breeding', 0.85),
        
        # Political
        ('Election 2024', 'PM-KISAN', 'relates_to', 'Farmer welfare electoral issue', 0.70),
        ('Election 2024', 'Unemployment', 'relates_to', 'Jobs major campaign topic', 0.80),
        ('Election 2024', 'GST', 'relates_to', 'Tax policy political debate', 0.60),
        
        # Commodities
        ('Gold', 'Inflation', 'relates_to', 'Hedge against inflation', 0.65),
        ('Gold', 'Rupee-Dollar', 'affects', 'Dollar price affects gold imports', 0.75),
    ]
    
    for source_name, target_name, rel_type, context, strength in relationships_data:
        if source_name in entities and target_name in entities:
            rel = Relationship(
                source_id=entities[source_name].id,
                target_id=entities[target_name].id,
                relationship_type=rel_type,
                context=context,
                strength=strength
            )
            db.session.add(rel)
    
    db.session.commit()
    print(f"✅ Created {len(relationships_data)} relationships")
    
    print("\n🎉 Knowledge Graph populated successfully!")
    print(f"   - {len(entities)} entities")
    print(f"   - {len(relationships_data)} relationships")
    print("\nCategories:")
    print(f"   - Places: {len([e for e in entities.values() if e.type == 'place'])}")
    print(f"   - Commodities: {len([e for e in entities.values() if e.type == 'commodity'])}")
    print(f"   - Indicators: {len([e for e in entities.values() if e.type == 'indicator'])}")
    print(f"   - Policies: {len([e for e in entities.values() if e.type == 'policy'])}")
    print(f"   - Events: {len([e for e in entities.values() if e.type == 'event'])}")
    print(f"   - Technologies: {len([e for e in entities.values() if e.type == 'technology'])}")