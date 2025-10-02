from sqlmodel import SQLModel, Session, create_engine

# name of the database to connect to
db = "users"




mysql_url = f"mysql+pymysql://root:xcr223@152.42.164.213:3306/{db}"
engine = create_engine(mysql_url, echo=True)
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
