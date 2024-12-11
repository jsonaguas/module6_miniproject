from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, validate
from marshmallow import ValidationError
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:a3$pa202O.@localhost/ecommerce"
CORS(app)
ma = Marshmallow(app)
db = SQLAlchemy(app)

# Association table for many-to-many relationship between orders and products
order_product = db.Table('order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    account = db.relationship('CustomerAccount', backref='customer', uselist=False)

class CustomerAccount(db.Model):
    __tablename__ = "customer_accounts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))  
    price = db.Column(db.Float) 
    stock = db.Column(db.Integer, nullable=False, default=0)
    orders = db.relationship('Order', secondary=order_product, back_populates='products')

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    quantity = db.Column(db.Integer)
    customer = db.relationship('Customer', backref='orders')
    products = db.relationship('Product', secondary=order_product, back_populates='orders')

class CustomerSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    phone = fields.String(required=True, validate=validate.Length(min=1))
    class Meta:
        fields = ('id', 'name', 'email', 'phone')

class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True, validate=validate.Length(min=1))
    customer = fields.Nested(CustomerSchema)  
    class Meta:
        fields = ('id', 'username', 'password', 'customer_id')

class ProductSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True)
    stock = fields.Integer(required=True)
    class Meta:
        fields = ('id', 'name', 'price', 'stock')

class OrderSchema(ma.Schema):
    customer_id = fields.Integer(required=True)
    product_ids = fields.List(fields.Integer(), required=True)
    quantity = fields.Integer(required=True)
    order_date = fields.DateTime(required=True)
    class Meta:
        fields = ('id', 'customer_id', 'product_ids', 'quantity', 'order_date')

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

@app.route('/')
def home():
    return "Welcome to the E-commerce API"

# @app.route('/customer', methods=['POST'])
# def add_customer():
#     try:
#         customer = customer_schema.load(request.json)
#         db.session.add(customer)
#         db.session.commit()
#         return jsonify(customer_schema.dump(customer)), 201
#     except ValidationError as err:
#         return jsonify(err.messages), 400

@app.route('/customer', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
        customer = Customer(**customer_data)
        db.session.add(customer)
        db.session.commit()
        return jsonify(customer_schema.dump(customer)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route('/customer', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route('/customer/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get(id)
    return customer_schema.jsonify(customer)

@app.route('/customer/<int:id>', methods=['PUT'])
def update_customer(id):
    try:
        customer = customer_schema.load(request.json)   
    except ValidationError as err:
        return jsonify(err.messages), 400
    customer = Customer.query.get(id)
    customer.name = request.json['name']
    customer.email = request.json['email']
    customer.phone = request.json['phone']
    db.session.commit()
    return jsonify("Customer updated successfully"), 200

@app.route('/customer/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify("Customer deleted successfully"), 200

@app.route('/customer_account', methods=['POST'])
def add_customer_account():
    try:
        customer_account = customer_account_schema.load(request.json)   
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_customer_account = CustomerAccount(username=customer_account['username'], password=customer_account['password'], customer_id=customer_account['customer_id'])
    db.session.add(new_customer_account)
    db.session.commit()
    return jsonify("Customer account added successfully"), 201

@app.route('/customer_account', methods=['GET'])
def get_customer_accounts():
    customer_accounts = CustomerAccount.query.all()
    return customer_accounts_schema.jsonify(customer_accounts)

@app.route('/customer_account/<int:id>', methods=['GET'])
def get_customer_account(id):
    customer_account = CustomerAccount.query.get(id)
    return customer_account_schema.jsonify(customer_account)

@app.route('/customer_account/<int:id>', methods=['PUT'])
def update_customer_account(id):
    try:
        customer_account = customer_account_schema.load(request.json)   
    except ValidationError as err:
        return jsonify(err.messages), 400
    customer_account = CustomerAccount.query.get(id)
    customer_account.username = request.json['username']
    customer_account.password = request.json['password']
    db.session.commit()
    return jsonify("Customer account updated successfully"), 200

@app.route('/customer_account/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    customer_account = CustomerAccount.query.get(id)
    db.session.delete(customer_account)
    db.session.commit()
    return jsonify("Customer account deleted successfully"), 200

@app.route('/product', methods=['POST'])
def add_product():
    try:
        product = product_schema.load(request.json)   
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_product = Product(name=product['name'], price=product['price'], stock=product['stock'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify("Product added successfully"), 201

@app.route('/product/<int:id>', methods=['GET'])
def get_product(id):
    try:
        product = Product.query.get_or_404(id)
    except ValidationError as err:
        return jsonify(err.messages), 400
    return product_schema.jsonify(product)


@app.route('/product/<int:id>', methods=['PUT'])
def update_product(id):
    try:
        product = Product.query.get_or_404(id)
    except ValidationError as err:
        return jsonify(err.messages), 400
    product.name = request.json['name']
    product.price = request.json['price']
    db.session.commit()
    return jsonify("Product updated successfully"), 200

@app.route('/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify("Product deleted successfully"), 200

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/product/<int:id>/stock', methods=['PATCH'])
def adjust_product_stock(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    try:
        data = request.json
        if 'stock' in data:
            product.stock += data['stock']
            db.session.commit()
            return jsonify({"message": "Stock level adjusted successfully"}), 200
        else:
            return jsonify({"message": "Invalid input"}), 400
    except KeyError:
        return jsonify({"message": "Invalid input"}), 400

@app.route('/order', methods=['POST'])
def add_order():
        try:
                order_data = request.json
                customer_id = order_data.get('customer_id')
                product_ids = order_data.get('product_ids')
                quantity = order_data.get('quantity')
                order_date = datetime.strptime(order_data.get('order_date'), '%Y-%m-%d')

                if not customer_id or not product_ids or not quantity or not order_date:
                    return jsonify({"message": "Invalid input"}), 400

                # Create the Order object
                order = Order(customer_id=customer_id, quantity=quantity, order_date=order_date)

                # Add products to the order
                for product_id in product_ids:
                    product = Product.query.get(product_id)
                    if product:
                        order.products.append(product)

                db.session.add(order)
                db.session.commit()

                return order_schema.jsonify(order), 201
        except Exception as e:
                return jsonify({"message": str(e)}), 400

@app.route('/orders/date/<string:order_date>', methods=['GET'])
def get_orders_by_date(order_date):
    try:
        date = datetime.strptime(order_date, '%Y-%m-%d')
        
        orders = Order.query.filter(db.func.date(Order.order_date) == date.date()).all()
        
        if not orders:
            return jsonify({"message": "No orders found for the specified date"}), 404
        
        return orders_schema.jsonify(orders), 200
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
@app.route('/order/<int:id>', methods=['GET'])
def get_order(id):
    order = Order.query.get(id)
    if not order:
        return jsonify({"message": "Order not found"}), 404
    return order_schema.jsonify(order)

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return orders_schema.jsonify(orders)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    try:
        db.create_all()
        print("Database connected and tables created successfully.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
    app.run(debug=True)

