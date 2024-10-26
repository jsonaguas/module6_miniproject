I have created an app for a hypothetical ecommerce web application that track
customers and their respective orders with its respective products while demonstrating
competency with using ORMs, CRUD operations, and relationship models.

While utilizing the relationship models, I had to establish the direction of how
each model would interact with one another. Customer and the customer account
would be one-to-one. Orders and products would have a bidirectional relationship.
I created an association table for the latter. 

Afterward, I created the respective CRUD operations for each appropriate model, i.e,
customers, orders. 

To simulate the app, I would use Postman to post new customers, orders, and products into the database and then test out the other operations such as retrieving the customers
by IDs. I would also be able to retrieve customer account data with the respective
customer data through the nested function. I also experimented by using the
PATCH method for the first time to update the stock levels. 