# SnapShop

SnapShop is a web-based eCommerce platform for buying and selling tech products, that supports multiple user roles (buyers and sellers).

## Technologies

- **Backend:** Python (Flask), SQLAlchemy ORM
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Database:** PostgreSQL

## Features

### 👤 User Registration and Login
- Users can register as Buyers, Sellers, or both.
- Seamless switching between Buyer and Seller modes within the same account.
- Role selection at login.

### 🛒 Shopping and Cart
- Buyers can add products to their cart and proceed to checkout.
- At checkout, users can select a default or custom shipping address and a payment method.
- Real-time stock verification before purchase completion.

### 🏪 Product Management
- Sellers can create and manage products.
- Each product belongs to a category and has attributes like name, brand, price, and stock quantity.

### 🔍 Search and Filters
- Product search by name.
- Filtering by category, brand, store, and price range.

### 📦 Order Management
- Buyers have access to an "Orders" section with real-time order status tracking (Pending, Shipped, Delivered).
- Sellers can manage incoming orders and update shipping status.
- Orders from multiple sellers are split into sub-orders by vendor.

### ⭐ Reviews
- Buyers can leave a review only for products they've purchased and received.
- Reviews include a 1–5 star rating and an optional comment.

### ⚙️ User Profile
- Users can update personal information.
- Toggle between Buyer and Seller dashboards.

## Database & ORM

- Models are defined using SQLAlchemy, mapping each class to a database table.
- Queries are built using SQLAlchemy’s fluent interface to filter products, orders, and reviews.
