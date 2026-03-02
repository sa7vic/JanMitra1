from apscheduler.schedulers.background import BackgroundScheduler
from services.data_collector import DataCollector
from services.ai_processor import AIProcessor
from models.database import db, Article
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_news_job(app):
    with app.app_context():
        logger.info("🔄 Auto-collecting news...")
        try:
            collector = DataCollector()
            count = collector.fetch_articles(max_per_source=15)
            logger.info(f"✅ Collected {count} articles")
            
           
            if count > 0:
                process_articles_job(app)
            
            return count
        except Exception as e:
            logger.error(f"❌ Collection failed: {e}")
            import traceback
            traceback.print_exc()
            return 0

def process_articles_job(app):
    with app.app_context():
        logger.info("🧠 Auto-processing articles...")
        try:
            ai_processor = AIProcessor()

            articles = Article.query.filter_by(processed=False).order_by(Article.created_at.desc()).limit(20).all()
            
            if not articles:
                logger.info("No new articles to process")
                return 0
            
            processed = 0
            for article in articles:
                try:
                    logger.info(f"Processing: {article.title[:50]}...")
                    ai_processor.extract_entities_and_relationships(article)
                    article.processed = True
                    db.session.commit()
                    processed += 1
                except Exception as e:
                    logger.error(f"Error processing article {article.id}: {e}")
                    db.session.rollback()
            
            logger.info(f"✅ Processed {processed} articles")
            
            if processed > 0:
                generate_predictions_job(app)
            
            return processed
        except Exception as e:
            logger.error(f"❌ Processing failed: {e}")
            import traceback
            traceback.print_exc()
            return 0

def generate_predictions_job(app):
    with app.app_context():
        logger.info("🔮 Generating predictions...")
        try:
            from services.crisis_predictor import CrisisPredictor
            predictor = CrisisPredictor()
            predictions = predictor.analyze_trends()
            logger.info(f"✅ Generated {len(predictions)} predictions")
            return len(predictions)
        except Exception as e:
            logger.error(f"❌ Prediction generation failed: {e}")
            return 0

def start_scheduler(app):
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        func=lambda: collect_news_job(app),
        trigger="interval",
        hours=1,
        id='collect_news',
        name='Collect news every hour',
        replace_existing=True
    )
    
    
    scheduler.add_job(
        func=lambda: process_articles_job(app),
        trigger="interval",
        minutes=30,
        id='process_articles',
        name='Process articles every 30 min',
        replace_existing=True
    )

    scheduler.add_job(
        func=lambda: generate_predictions_job(app),
        trigger="interval",
        hours=2,
        id='generate_predictions',
        name='Generate predictions every 2 hours',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("🚀 Scheduler started - full automation enabled")
    
    logger.info("🎬 Running initial data collection...")
    collect_news_job(app)
    
    return scheduler