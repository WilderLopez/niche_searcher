import datetime

from sqlalchemy import desc

from models.model import Niche, getSession


class NicheModel:

    @staticmethod
    def upsert(data: dict):
        """
        Inserta o actualiza un nicho a partir del dict que devuelve PlayService.
        Se identifica por app_id (único), de modo que reevaluar una app
        actualiza sus cifras en lugar de duplicarla.
        """
        session = getSession()
        row = session.query(Niche).where(Niche.app_id == data["app_id"]).one_or_none()

        if row is None:
            row = Niche(app_id=data["app_id"])
            session.add(row)

        row.url = data["url"]
        row.title = data["title"]
        row.developer = data["developer"]
        row.genre_id = data["genre_id"]
        row.min_installs = data["min_installs"]
        row.real_installs = data["real_installs"]
        row.score = data["score"]
        row.ratings = data["ratings"]
        row.reviews = data["reviews"]
        row.free = data["free"]
        row.contains_ads = data["contains_ads"]
        row.offers_iap = data["offers_iap"]
        row.released = data["released"]
        row.released_millis = data["released_millis"]
        row.age_days = data["age_days"]
        row.installs_per_day = data["installs_per_day"]
        row.evaluated_at = round(datetime.datetime.now().timestamp() * 1000)

        session.commit()
        return row

    @staticmethod
    def count():
        return getSession().query(Niche).count()

    @staticmethod
    def top(limit: int = 50, order_by: str = "installs_per_day"):
        """Devuelve los nichos ordenados por momentum (o el campo indicado)."""
        column = getattr(Niche, order_by, Niche.installs_per_day)
        return (
            getSession()
            .query(Niche)
            .order_by(desc(column))
            .limit(limit)
            .all()
        )

    @staticmethod
    def all():
        return getSession().query(Niche).order_by(desc(Niche.installs_per_day)).all()
