import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from fastmcp import FastMCP
from typing import List

# Importer depuis main.py
from main import SessionLocal, ProductORM, ProductRead

mcp = FastMCP(name="Product Catalog MCP Server")

@mcp.tool()
def list_products() -> List[dict]:
    """List all available products with their ID, name, price, and description (from Postgres)."""
    with SessionLocal() as db:
        rows = db.query(ProductORM).all()
        return [ProductRead.from_orm(r).dict() for r in rows]

@mcp.tool()
def get_product(product_id: int) -> dict:
    """Retrieve details of a specific product by its ID (from Postgres)."""
    with SessionLocal() as db:
        row = db.get(ProductORM, product_id)
        if not row:
            return {"error": "Product not found"}
        return ProductRead.from_orm(row).dict()

app = mcp.app

if __name__ == "__main__":
    mcp.run()