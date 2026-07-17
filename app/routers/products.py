from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from app.models import Product, ProductPage
from app.repository import get_product, list_products

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductPage)
def read_products(
    q: str | None = Query(default=None),
    sort: Literal["name", "price"] | None = Query(default=None),
    order: Literal["asc", "desc"] = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=20),
) -> ProductPage:
    products = list_products()

    if q is not None:
        lowered_query = q.lower()
        products = [
            product
            for product in products
            if lowered_query in product.name.lower() or lowered_query in product.category.lower()
        ]

    if sort is not None:
        products = sorted(
            products,
            key=lambda product: getattr(product, sort),
            reverse=order == "desc",
        )

    total = len(products)
    start_index = (page - 1) * page_size
    products = products[start_index : start_index + page_size]

    return ProductPage(
        items=products,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{product_id}", response_model=Product)
def read_product(product_id: int) -> Product:
    product = get_product(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product
