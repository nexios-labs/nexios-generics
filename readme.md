

This documentation provides a comprehensive guide to using `nexios-generic` built on top of **Nexios**, a lightweight Python web framework. The framework is designed to simplify the creation of CRUD (Create, Read, Update, Delete) APIs using **Tortoise ORM** for database management and **Pydantic** for data validation. While this framework is a side project and not extensively tested, it provides a solid foundation for building APIs quickly and efficiently.

---

## Table of Contents

1. [Core Components](#core-components)
   - [GenericAPIView](#genericapiview)
   - [Mixins](#mixins)
   - [Views](#views)
2. [Getting Started](#getting-started)
   - [Installation](#installation)
   - [Project Setup](#project-setup)
3. [Usage Guide](#usage-guide)
   - [Defining Models](#defining-models)
   - [Defining Pydantic Schemas](#defining-pydantic-schemas)
   - [Creating Views](#creating-views)
   - [Adding Routes](#adding-routes)
4. [Advanced Usage](#advanced-usage)
   - [Customizing Querysets](#customizing-querysets)
   - [Customizing Validation](#customizing-validation)
   - [Error Handling](#error-handling)
   - [Extending Mixins](#extending-mixins)
5. [Example Project](#example-project)
6. [Conclusion](#conclusion)

---

## Core Components

### GenericAPIView

The `GenericAPIView` class is the base class for all views in the framework. It provides the foundational logic for handling requests, validating data, and formatting responses. Key methods include:

- **`get_queryset()`**: Returns the queryset for the view.
- **`get_pydantic_class()`**: Returns the Pydantic model class used for data validation and serialization.
- **`validate_request()`**: Validates the incoming request data using the Pydantic model.
- **`get_object()`**: Retrieves a single object from the database based on the lookup field.
- **`format_error_response()`**: Formats an error response with a status code and details.
- **`format_success_response()`**: Formats a success response with data and a status code.

### Mixins

Mixins provide reusable functionality for common CRUD operations. They are designed to be combined with `GenericAPIView` to create views with specific behavior.

- **`CreateModelMixin`**: Handles creating new objects.
- **`RetrieveModelMixin`**: Handles retrieving a single object.
- **`ListModelMixin`**: Handles listing multiple objects.
- **`UpdateModelMixin`**: Handles updating existing objects.
- **`DeleteModelMixin`**: Handles deleting objects.

### Views

The framework provides pre-built views that combine the mixins for common use cases:

- **`ListCreateAPIView`**: Combines `ListModelMixin` and `CreateModelMixin` for listing and creating objects.
- **`RetrieveUpdateDestroyAPIView`**: Combines `RetrieveModelMixin`, `UpdateModelMixin`, and `DeleteModelMixin` for retrieving, updating, and deleting objects.
- **`ListCreateRetrieveUpdateDestroyAPIView`**: Combines all mixins for full CRUD functionality.

---

## Getting Started

### Installation

Before using the framework, ensure you have the following installed:

- Python 3.7 or higher
- **Nexios** (a lightweight Python web framework)
- **Tortoise ORM** (for database management)
- **Pydantic** (for data validation)

You can install the required packages using `pip`:

```bash
pip install nexios tortoise-orm pydantic
```

### Project Setup

1. **Initialize Nexios**: Create a new Nexios application.
2. **Configure Tortoise ORM**: Set up your database configuration.
3. **Define Models**: Create your database models using Tortoise ORM.
4. **Define Pydantic Schemas**: Create Pydantic schemas for data validation and serialization.
5. **Create Views**: Use the provided mixins and views to create your API endpoints.
6. **Add Routes**: Add your views as routes in your Nexios application.

---

## Usage Guide

### Defining Models

Define your database models using Tortoise ORM. For example, a `User` model:

```python
from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)

    class Meta:
        table = "users"
```

### Defining Pydantic Schemas

Define Pydantic schemas for data validation and serialization. For example, a `UserSchema`:

```python
from pydantic import BaseModel

class UserSchema(BaseModel):
    id: int | None = None
    username: str
    email: str

    class Config:
        from_attributes = True
```

### Creating Views

Use the provided mixins and views to create your API endpoints. For example, to create a view for listing and creating users:

```python
from src.views import ListCreateAPIView
from src.base import GenericAPIView

class UserView(ListCreateAPIView):
    pydantic_class = UserSchema

    async def get_queryset(self):
        return User.all()
```

### Adding Routes

Add your views as routes in your Nexios application:

```python
from nexios import get_application

app = get_application()
app.add_route(UserView.as_route("/users"))
```

---

## Advanced Usage

### Customizing Querysets

You can customize the queryset used by your views by overriding the `get_queryset()` method. For example, to filter users by a specific condition:

```python
class UserView(ListCreateAPIView):
    pydantic_class = UserSchema

    async def get_queryset(self):
        return User.filter(username__icontains="admin")
```

### Customizing Validation

You can customize the validation logic by overriding the `validate_request()` method. For example, to add custom validation rules:

```python
class UserView(ListCreateAPIView):
    pydantic_class = UserSchema

    async def validate_request(self):
        data = await self.request.json()
        if "username" not in data:
            raise ValueError("Username is required")
        return self.pydantic_class(**data)
```

### Error Handling

You can customize error handling by overriding the error-handling methods in the mixins. For example, to customize the error response format:

```python
class UserView(ListCreateAPIView):
    pydantic_class = UserSchema

    def handle_validation_error(self, res, error):
        return res.status(400).json({"error": "Validation failed", "details": str(error)})
```

### Extending Mixins

You can extend the mixins to add custom behavior. For example, to add logging to the `CreateModelMixin`:

```python
class LoggingCreateMixin(CreateModelMixin):
    async def perform_create(self, instance):
        print(f"Creating object: {instance}")
        return await super().perform_create(instance)
```

---

## Example Project

Here’s a complete example of a simple API for managing users:

```python
from tortoise import fields, models
from pydantic import BaseModel
from src.views import ListCreateAPIView
from nexios import get_application

# Define the User model
class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)

    class Meta:
        table = "users"

# Define the Pydantic schema
class UserSchema(BaseModel):
    id: int | None = None
    username: str
    email: str

    class Config:
        from_attributes = True

# Create the view
class UserView(ListCreateAPIView):
    pydantic_class = UserSchema

    async def get_queryset(self):
        return User.all()

# Add the route to Nexios
app = get_application()
app.add_route(UserView.as_route("/users"))
```

---

## Conclusion

This framework provides a lightweight and easy-to-use solution for building CRUD APIs with **Nexios**, **Tortoise ORM**, and **Pydantic**. While it is not extensively tested, it offers a solid foundation for quickly creating APIs. Feel free to extend and modify the framework to suit your needs!

For more information on **Nexios**, visit the official documentation: [Nexios Documentation](https://nexios.io).

---

## GitHub Badges

[![GitHub License](https://img.shields.io/github/license/yourusername/your-repo)](https://github.com/yourusername/your-repo)
[![GitHub Issues](https://img.shields.io/github/issues/yourusername/your-repo)](https://github.com/yourusername/your-repo/issues)
[![GitHub Stars](https://img.shields.io/github/stars/yourusername/your-repo)](https://github.com/yourusername/your-repo/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/yourusername/your-repo)](https://github.com/yourusername/your-repo/network)

---

## Logo

![Nexios Logo](https://nexios.io/logo.png)

---

Thank you for using this framework! If you have any questions or feedback, please open an issue on [GitHub](https://github.com/yourusername/your-repo).