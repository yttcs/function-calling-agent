from sqlmodel import Session, create_engine

# name of the database to connect to
db = "users"

mysql_url = f"mysql+pymysql://root:password@IP_address:3306/{db}"
engine = create_engine(mysql_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
