from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv
import os

# Charger variables d'environnement (.env)
load_dotenv()


# SQLAlchemy (sync)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set. Please set it in your .env file or environment.")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Modèle ORM
class ProductORM(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=True)

# Schémas Pydantic
class ProductBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int

    class Config:
        orm_mode = True

# Dépendance DB
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# App FastAPI
app = FastAPI(
    title="Product Catalog API",
    description="A simple API for managing a product catalog",
    version="1.0.0"
)

# Création des tables au démarrage
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Endpoints
@app.get("/products", response_model=List[ProductRead])
def list_products(db: Session = Depends(get_db)):
    return db.query(ProductORM).all()

@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(ProductORM, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products", response_model=ProductRead, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = ProductORM(
        name=product.name,
        price=product.price,
        description=product.description
    )
    db.add(new_product)
    db.commit()       # important pour persister
    db.refresh(new_product)
    return new_product