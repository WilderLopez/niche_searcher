import datetime

from sqlalchemy import asc, desc

from models.model import AppstoreCandidate, AppstoreNiche, getSession


def _now_millis():
    return round(datetime.datetime.now().timestamp() * 1000)


class AppstoreCandidateModel:

    @staticmethod
    def insert_ids(app_ids: list):
        """Inserta ids de apps que aún no estén en el pool. Devuelve las nuevas."""
        session = getSession()
        existing = {a for (a,) in session.query(AppstoreCandidate.app_id).all()}

        inserted = []
        for app_id in app_ids:
            if app_id in existing:
                continue
            session.add(AppstoreCandidate(
                app_id=app_id,
                register_date=_now_millis(),
                last_scan_date=0,
            ))
            inserted.append(app_id)
            existing.add(app_id)

        session.commit()
        return inserted

    @staticmethod
    def get_batch_to_scan(limit: int):
        """
        Próximos ids a evaluar: primero los que hace más tiempo que no se
        escanean y, a igualdad, los descubiertos más recientemente. Marca su
        last_scan_date para no repetirlos.
        """
        session = getSession()
        rows = (
            session.query(AppstoreCandidate)
            .order_by(asc(AppstoreCandidate.last_scan_date), desc(AppstoreCandidate.register_date))
            .limit(limit)
            .all()
        )
        now = _now_millis()
        ids = []
        for row in rows:
            row.last_scan_date = now
            ids.append(row.app_id)
        session.commit()
        return ids

    @staticmethod
    def count():
        return getSession().query(AppstoreCandidate).count()


class AppstoreNicheModel:

    _FIELDS = [
        "bundle_id", "url", "title", "developer", "genre", "genre_id",
        "avg_rating", "rating_count", "price", "currency", "free",
        "released", "released_millis", "age_days", "updated",
        "content_rating", "ratings_per_day", "file_size_mb",
        "screenshot_count", "language_count",
        "clone_score", "s_demand", "s_monetization", "s_buildability",
        "s_competibility", "flags",
    ]

    @staticmethod
    def upsert(data: dict):
        """Inserta o actualiza un nicho por app_id (no duplica al reevaluar)."""
        session = getSession()
        row = session.query(AppstoreNiche).where(
            AppstoreNiche.app_id == data["app_id"]
        ).one_or_none()

        if row is None:
            row = AppstoreNiche(app_id=data["app_id"])
            session.add(row)

        for f in AppstoreNicheModel._FIELDS:
            setattr(row, f, data[f])
        row.evaluated_at = _now_millis()

        session.commit()
        return row

    @staticmethod
    def count():
        return getSession().query(AppstoreNiche).count()

    @staticmethod
    def top(limit: int = 50):
        return (
            getSession().query(AppstoreNiche)
            .order_by(desc(AppstoreNiche.clone_score), desc(AppstoreNiche.ratings_per_day))
            .limit(limit)
            .all()
        )

    @staticmethod
    def all():
        return (
            getSession().query(AppstoreNiche)
            .order_by(desc(AppstoreNiche.clone_score), desc(AppstoreNiche.ratings_per_day))
            .all()
        )
