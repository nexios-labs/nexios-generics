from os import read
from typing import Optional
from tortoise import Tortoise, fields
from tortoise.models import Model
from pydantic import BaseModel,Field
from src.views import ListCreateAPIView
from nexios import get_application

app = get_application()

# Database Configuration
db_config = {
    "connections": {
        "default": "sqlite://db.sqlite3" 
    },
    "apps": {
        "models": {
            "models": [__name__],  
            "default_connection": "default",
        }
    }
}

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    
    class Meta:
        table = "users"

# Pydantic Schema
class UserSchema(BaseModel):
    id :Optional[int]
    username: str
    email: str

    class Config:
        from_attributes = True

# Initialize Tortoise ORM
@app.on_startup
async def init_db():
    await Tortoise.init(config=db_config)
    await Tortoise.generate_schemas()

@app.on_shutdown
async def close_db():
    await Tortoise.close_connections()



@app.get("/users")
async def get_users(request, response ):
    users = await User.all()
    return response.json([user for user in users])


class UserClassView(ListCreateAPIView):
    pydantic_class = UserSchema
    
    async def get_queryset(self):
        return User.all() 
    
    def format_success_response(self, data, status_code = 200):
        print(data)
        return super().format_success_response(data, 400)
    
    
    def perform_create(self, instance):
        print("instance :", instance)
        return super().perform_create(instance)
    
    
    
    
    
app.add_route(UserClassView.as_route("/c/users"))
    