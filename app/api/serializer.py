
def serialize_product(product):
    return {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'created_at': product.created_at
    }

def serialize_paginated_products(paginated_products):
    products = [serialize_product(product) for product in paginated_products.items]
    return {
        'products': products,
        'total': paginated_products.total,
        'pages': paginated_products.pages,
        'current_page': paginated_products.page,
        'has_next': paginated_products.has_next,
        'has_prev': paginated_products.has_prev
    }