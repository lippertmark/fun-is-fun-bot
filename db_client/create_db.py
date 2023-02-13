from models import BaseModel, engine

# import engine

BaseModel.metadata.create_all(engine)
