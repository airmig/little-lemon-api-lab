# Project API Documentation

This document outlines all the API endpoints available in this project, grouped by functionality.

## User Registration and Token Generation Endpoints

The following endpoints are automatically generated using the Djoser library for user registration, authentication, and token management.

| Endpoint             | Role                           | Method | Purpose                                                       -------------------------------------------------------------------------------------------|
| `/api/users`         | No role required               | POST   | Creates a new user with name, email, and password.                                        |
| `/api/users/me/`     | Anyone with a valid user token | GET    | Displays the current user.                                                                |
| `/token/login/`      | Anyone with a valid username and password | POST   | Generates access tokens for use in other API calls.                                        |

**Note:** When you include Djoser endpoints, it will create other useful endpoints for better authentication as well.

## Menu-items Endpoints

These endpoints manage the menu items and their access based on user roles.

### Endpoints for Customers and Delivery Crew

| Endpoint                          | Role                   | Method                 | Purpose
| `/api/menu-items`                 | Customer, Delivery Crew| GET                    | Lists all menu items. Returns a 200 – OK HTTP status code.    |
| `/api/menu-items`                 | Customer, Delivery Crew| POST, PUT, PATCH, DELETE | Denies access and returns 403 – Unauthorized.                |
| `/api/menu-items/{menuItem}`      | Customer, Delivery Crew| GET                    | Lists a single menu item.                                    |
| `/api/menu-items/{menuItem}`      | Customer, Delivery Crew| POST, PUT, PATCH, DELETE | Returns 403 – Unauthorized.                                  |

### Endpoints for Managers

| Endpoint                          | Role   | Method   | Purpose                                                 |
|-----------------------------------|--------|----------|---------------------------------------------------------|
| `/api/menu-items`                 | Manager| GET      | Lists all menu items.                                   |
| `/api/menu-items`                 | Manager| POST     | Creates a new menu item and returns 201 - Created.      |
| `/api/menu-items/{menuItem}`      | Manager| GET      | Lists a single menu item.                               |
| `/api/menu-items/{menuItem}`      | Manager| PUT, PATCH | Updates the specified menu item.                        |
| `/api/menu-items/{menuItem}`      | Manager| DELETE   | Deletes the specified menu item.                        |

## User Group Management Endpoints

Endpoints for managing user groups like managers and delivery crew.

### Manager Group Endpoints

| Endpoint                                | Role    | Method | Purpose                                                                
| `/api/groups/manager/users`             | Manager | GET    | Returns all managers.                                                   |
| `/api/groups/manager/users`             | Manager | POST   | Assigns a user to the manager group and returns 201 - Created.          |
| `/api/groups/manager/users/{userId}`    | Manager | DELETE | Removes a user from the manager group and returns 200 - Success.        |
|                                         |         |        | If the user is not found, returns 404 – Not Found.                      |

### Delivery Crew Group Endpoints

| Endpoint                                     | Role    | Method | Purpose                                                           
| `/api/groups/delivery-crew/users`            | Manager | GET    | Returns all delivery crew members.                                      |
| `/api/groups/delivery-crew/users`            | Manager | POST   | Assigns a user to the delivery crew group and returns 201 - Created.    |
| `/api/groups/delivery-crew/users/{userId}`   | Manager | DELETE | Removes a user from the delivery crew group and returns 200 - Success.  |
|                                              |         |        | If the user is not found, returns 404 – Not Found.                      |

## Cart Management Endpoints

Endpoints for managing the user's cart.

| Endpoint                   | Role     | Method | Purpose
| `/api/cart/menu-items`      | Customer | GET    | Returns current items in the cart for the current user token.                       |
| `/api/cart/menu-items`      | Customer | POST   | Adds a menu item to the cart and associates it with the authenticated user.         |
| `/api/cart/menu-items`      | Customer | DELETE | Deletes all menu items created by the current user token.                           |

## Order Management Endpoints

Endpoints for managing orders and order items.

### Endpoints for Customers

| Endpoint                          | Role     | Method
| `/api/orders`                     | Customer | GET            | Returns all orders with order items created by the current user.                                         |
| `/api/orders`                     | Customer | POST           | Creates a new order for the current user, moving items from the cart to the order.                       |
| `/api/orders/{orderId}`           | Customer | GET            | Returns all items for the specified order. If the order ID doesn’t belong to the current user, returns an error. |
| `/api/orders/{orderId}`           | Customer | PUT, PATCH     | Updates the specified order. Customers can only update their own orders.                                |

### Endpoints for Managers

| Endpoint                          | Role    | Method         | Purpose                                                         
| `/api/orders`                     | Manager | GET            | Returns all orders with order items from all users.                                                     |
| `/api/orders/{orderId}`           | Manager | PUT, PATCH     | Updates the specified order. Can assign delivery crew and update order status (0 for out for delivery, 1 for delivered). 
| `/api/orders/{orderId}`           | Manager | DELETE         | Deletes the specified order.                                                                            |

### Endpoints for Delivery Crew

| Endpoint                          | Role          | Method | Purpose                                                      
| `/api/orders`                     | Delivery Crew | GET    | Returns all orders with order items assigned to the delivery crew.                           |
| `/api/orders/{orderId}`           | Delivery Crew | PATC  | Updates the order status (0 for out for delivery, 1 for delivered). Cannot update other order details. |

---

This `README.md` file serves as a guide for developers interacting with the API endpoints. Make sure to include authentication tokens where required, and refer to the appropriate roles when accessing these endpoints.
