from app import app
from models.database import db, Entity, Relationship, Article
from datetime import datetime
import json

with app.app_context():
    # Clear existing
    db.session.query(Relationship).delete()
    db.session.query(Entity).delete()
    
    # Create entities
    entities = [
        # Places
        Entity(name='Delhi', type='place', description='National capital, population 32M'),
        Entity(name='Mumbai', type='place', description='Financial capital, Maharashtra'),
        Entity(name='Bangalore', type='place', description='IT hub, Karnataka'),
        Entity(name='Chennai', type='place', description='Auto manufacturing hub, Tamil Nadu'),
        Entity(name='Kolkata', type='place', description='Cultural capital, West Bengal'),
        Entity(name='Hyderabad', type='place', description='Pharma & IT hub, Telangana'),
        Entity(name='Pune', type='place', description='Education hub, Maharashtra'),
        Entity(name='Ahmedabad', type='place', description='Textile hub, Gujarat'),
        Entity(name='Jaipur', type='place', description='Tourism hub, Rajasthan'),
        Entity(name='Lucknow', type='place', description='Capital of UP'),
        
        # Commodities
        Entity(name='Petrol', type='commodity', description='Motor fuel, ₹102/L avg'),
        Entity(name='Diesel', type='commodity', description='Commercial fuel, ₹88/L avg'),
        Entity(name='Crude Oil', type='commodity', description='Global commodity affecting India'),
        Entity(name='Onion', type='commodity', description='Essential vegetable, volatile pricing'),
        Entity(name='Tomato', type='commodity', description='Essential vegetable'),
        Entity(name='Rice', type='commodity', description='Staple food grain'),
        Entity(name='Wheat', type='commodity', description='Staple food grain'),
        
        # Policies
        Entity(name='PM-KISAN', type='policy', description='Direct farmer income support'),
        Entity(name='Ayushman Bharat', type='policy', description='Health insurance scheme'),
        Entity(name='Make in India', type='policy', description='Manufacturing initiative'),
        Entity(name='Digital India', type='policy', description='Digital transformation program'),
        
        # Indicators
        Entity(name='GDP Growth', type='indicator', description='Economic growth rate'),
        Entity(name='Inflation', type='indicator', description='Price increase rate'),
        Entity(name='Unemployment', type='indicator', description='Joblessness rate'),
        Entity(name='Monsoon', type='indicator', description='Annual rainfall pattern'),
        
        # Events
        Entity(name='US-Iran Conflict', type='event', description='Middle East tensions'),
        Entity(name='Election 2024', type='event', description='General elections'),
        Entity(name='Dengue Outbreak', type='event', description='Seasonal health crisis'),
    ]
    
    for e in entities:
        e.data = json.dumps({})
        db.session.add(e)
    
    db.session.flush()
    
    # Create relationships
    entity_map = {e.name: e for e in entities}
    
    relationships = [
        # Crude Oil affects Petrol/Diesel
        ('Crude Oil', 'Petrol', 'causes', 'Global crude prices directly impact petrol prices', 0.9),
        ('Crude Oil', 'Diesel', 'causes', 'Global crude prices directly impact diesel prices', 0.9),
        ('US-Iran Conflict', 'Crude Oil', 'affects', 'Geopolitical tensions increase oil prices', 0.8),
        
        # Fuel affects economy
        ('Petrol', 'Inflation', 'causes', 'Rising fuel costs increase overall inflation', 0.85),
        ('Diesel', 'Inflation', 'causes', 'Commercial transport costs increase prices', 0.85),
        
        # Agriculture connections
        ('Monsoon', 'Rice', 'affects', 'Rainfall patterns determine rice production', 0.9),
        ('Monsoon', 'Wheat', 'affects', 'Water availability affects wheat yield', 0.85),
        ('Rice', 'Inflation', 'affects', 'Food grain prices impact overall inflation', 0.7),
        
        # Onion/Tomato volatility
        ('Monsoon', 'Onion', 'affects', 'Excess rain damages onion crops', 0.8),
        ('Onion', 'Inflation', 'causes', 'Onion price spikes affect inflation', 0.65),
        ('Tomato', 'Inflation', 'affects', 'Vegetable price volatility', 0.6),
        
        # Policy connections
        ('PM-KISAN', 'Rice', 'relates_to', 'Farmer support scheme for grain production', 0.7),
        ('Make in India', 'Unemployment', 'affects', 'Manufacturing jobs program', 0.7),
        ('Digital India', 'GDP Growth', 'affects', 'Digital economy contribution', 0.6),
        
        # City-specific
        ('Mumbai', 'GDP Growth', 'relates_to', 'Financial capital drives 6% of GDP', 0.8),
        ('Bangalore', 'Digital India', 'relates_to', 'IT hub central to digital transformation', 0.85),
        ('Delhi', 'Inflation', 'relates_to', 'Capital city inflation indicator', 0.7),
        
        # Health
        ('Dengue Outbreak', 'Delhi', 'affects', 'Annual monsoon season outbreak', 0.75),
        ('Dengue Outbreak', 'Mumbai', 'affects', 'Coastal region mosquito breeding', 0.7),
        ('Ayushman Bharat', 'Dengue Outbreak', 'relates_to', 'Health insurance covers treatment', 0.6),
        
        # Elections
        ('Election 2024', 'PM-KISAN', 'relates_to', 'Farmer welfare scheme political impact', 0.7),
        ('Election 2024', 'Unemployment', 'relates_to', 'Job creation major electoral issue', 0.8),
    ]
    
    for source, target, rel_type, context, strength in relationships:
        if source in entity_map and target in entity_map:
            rel = Relationship(
                source_id=entity_map[source].id,
                target_id=entity_map[target].id,
                relationship_type=rel_type,
                context=context,
                strength=strength
            )
            db.session.add(rel)
    
    db.session.commit()
    
    print(f"✅ Created {len(entities)} entities")
    print(f"✅ Created {len(relationships)} relationships")
    print("\nKnowledge graph is now populated!")