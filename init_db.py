import logging
from sqlalchemy.orm import sessionmaker

from app.db.session import engine, SessionLocal
from app.models import Base, User, UserRole
from app.services.security_service import get_password_hash
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == "admin@prawoasystent.ai").first()
        if not admin_user:
            logger.info("Creating initial admin user...")
            hashed_password = get_password_hash("adminpassword")
            admin_user = User(
                email="admin@prawoasystent.ai",
                hashed_password=hashed_password,
                first_name="Admin",
                last_name="User",
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
            )
            db.add(admin_user)
            db.commit()
            logger.info("Admin user created successfully.")
        else:
            logger.info("Admin user already exists.")
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialization finished.")
