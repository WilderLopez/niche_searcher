import os

from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# Ruta absoluta a la BD para que funcione se ejecute desde donde se ejecute.
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DB_PATH = os.path.join(_BASE_DIR, "databases", "g_scraper.db")

engine = create_engine("sqlite:///" + _DB_PATH)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class GpUrlBase(Base):
    """Pool de candidatas: URLs de apps descubiertas, pendientes de evaluar."""
    __tablename__ = "gp_url_base"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String)
    register_date = Column(BigInteger)
    last_view_date = Column(BigInteger)
    last_scan_date = Column(BigInteger)


class Niche(Base):
    """App que ha superado el criterio de nicho, con todos sus datos."""
    __tablename__ = "niche"
    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String, unique=True)
    url = Column(String)
    title = Column(String)
    developer = Column(String)
    genre_id = Column(String)
    min_installs = Column(BigInteger)
    real_installs = Column(BigInteger)
    score = Column(Float)
    ratings = Column(BigInteger)
    reviews = Column(BigInteger)
    free = Column(Boolean)
    contains_ads = Column(Boolean)
    offers_iap = Column(Boolean)
    released = Column(String)
    released_millis = Column(BigInteger)
    age_days = Column(Integer)
    installs_per_day = Column(Float)
    evaluated_at = Column(BigInteger)


class AppstoreCandidate(Base):
    """Pool de candidatas iOS descubiertas, pendientes de evaluar."""
    __tablename__ = "appstore_candidate"
    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String, unique=True)
    register_date = Column(BigInteger)
    last_scan_date = Column(BigInteger)


class AppstoreNiche(Base):
    """App iOS que ha superado el criterio de nicho, con todos sus datos."""
    __tablename__ = "appstore_niche"
    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String, unique=True)
    bundle_id = Column(String)
    url = Column(String)
    title = Column(String)
    developer = Column(String)
    genre = Column(String)
    genre_id = Column(String)
    avg_rating = Column(Float)
    rating_count = Column(BigInteger)
    price = Column(Float)
    currency = Column(String)
    free = Column(Boolean)
    released = Column(String)
    released_millis = Column(BigInteger)
    age_days = Column(Integer)
    updated = Column(String)
    content_rating = Column(String)
    ratings_per_day = Column(Float)
    file_size_mb = Column(Integer)
    screenshot_count = Column(Integer)
    language_count = Column(Integer)
    # clone score y sus componentes
    clone_score = Column(Integer)
    s_demand = Column(Integer)
    s_monetization = Column(Integer)
    s_buildability = Column(Integer)
    s_competibility = Column(Integer)
    flags = Column(String)
    evaluated_at = Column(BigInteger)


def init():
    Base.metadata.create_all(engine)


def getSession():
    return session
