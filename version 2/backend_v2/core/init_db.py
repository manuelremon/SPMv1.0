from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend_v2.core.config import Settings
from backend_v2.core.base import Base
from backend_v2.models.user import User
from backend_v2.models.solicitud import Solicitud


def build_db(force: bool = False):
    engine = create_engine(Settings.DB_URL, future=True)
    if force:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Insert a default test user if not present
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        from werkzeug.security import generate_password_hash
        if session.query(User).count() == 0:
            new = User(username='admin', email='admin@example.com', password_hash=generate_password_hash('test'), full_name='Admin')
            session.add(new)
            session.commit()
    finally:
        session.close()
