from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database URL - use SQLite for development, can be changed to PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./videohook.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    email_notifications_enabled = Column(Boolean, default=True)
    
    # Relationships
    social_connections = relationship("SocialMediaConnection", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("PostHistory", back_populates="user", cascade="all, delete-orphan")
    integrations = relationship("IntegrationConnection", back_populates="user", cascade="all, delete-orphan")


class SocialMediaConnection(Base):
    """Social media account connections via OAuth"""
    __tablename__ = "social_media_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional - no user required
    platform = Column(String, nullable=False)  # 'instagram', 'linkedin', 'x', 'tiktok'
    account_username = Column(String, nullable=False)
    account_id = Column(String, nullable=False)  # Platform-specific account ID
    access_token = Column(Text, nullable=False)  # Encrypted in production
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="social_connections")
    posts = relationship("PostHistory", back_populates="connection")


class PostHistory(Base):
    """History of posts made to social media platforms"""
    __tablename__ = "post_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    connection_id = Column(Integer, ForeignKey("social_media_connections.id"), nullable=False)
    platform = Column(String, nullable=False)
    post_id = Column(String, nullable=True)  # Platform-specific post ID
    post_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    caption = Column(Text, nullable=True)
    status = Column(String, default="pending")  # 'pending', 'posted', 'failed'
    error_message = Column(Text, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="posts")
    connection = relationship("SocialMediaConnection", back_populates="posts")


class IntegrationConnection(Base):
    """Third-party integration connections (Notion, Google Drive, etc.)"""
    __tablename__ = "integration_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False)  # 'notion', 'google_drive'
    access_token = Column(Text, nullable=False)  # Encrypted in production
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    platform_user_id = Column(String, nullable=True)  # User ID from the platform
    platform_user_email = Column(String, nullable=True)  # User email from the platform
    is_active = Column(Boolean, default=True)
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="integrations")




# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


