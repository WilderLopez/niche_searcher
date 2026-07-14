import datetime

from sqlalchemy import asc

from models.model import GpUrlBase, getSession


def _now_millis():
    return round(datetime.datetime.now().timestamp() * 1000)


class GpUrlBaseModel:

    @staticmethod
    def insertAppLinks(links: list):
        """Inserta URLs de apps que aún no estén en la BD. Devuelve las nuevas."""
        session = getSession()
        inserted = []

        # Cargamos las existentes de un tirón para no lanzar una query por link.
        existing = {u for (u,) in session.query(GpUrlBase.url).all()}

        for url in links:
            if url in existing:
                continue
            temp = GpUrlBase(
                url=url,
                register_date=_now_millis(),
                last_view_date=0,
                last_scan_date=0,
            )
            session.add(temp)
            inserted.append(temp)
            existing.add(url)

        session.commit()
        return inserted

    @staticmethod
    def getBatchToScan(limit: int):
        """
        Devuelve las próximas `limit` URLs a evaluar (las que hace más tiempo
        que no se escanean) y marca su last_scan_date para no repetirlas.
        """
        session = getSession()
        rows = (
            session.query(GpUrlBase)
            .order_by(asc(GpUrlBase.last_scan_date))
            .limit(limit)
            .all()
        )
        now = _now_millis()
        urls = []
        for row in rows:
            row.last_scan_date = now
            urls.append(row.url)
        session.commit()
        return urls

    @staticmethod
    def delete(appUrl: str):
        session = getSession()
        try:
            session.query(GpUrlBase).where(GpUrlBase.url == appUrl).delete()
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False

    @staticmethod
    def count():
        return getSession().query(GpUrlBase).count()
