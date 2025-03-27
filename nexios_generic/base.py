from typing import Type, Any, Dict, List, Optional, Generic, TypeVar
from pydantic import BaseModel, ValidationError
from tortoise.queryset import QuerySet
from tortoise.models import Model
from nexios.views import APIView

T = TypeVar('T', bound=Model)
P = TypeVar('P', bound=BaseModel)

class GenericAPIView(APIView, Generic[T, P]):
    queryset: QuerySet[T] = None
    pydantic_class: Type[P] = None
    lookup_field: str = 'pk'
    lookup_url_kwarg: str = None

    async def get_queryset(self) -> QuerySet[T]:
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        if isinstance(self.queryset, QuerySet):
            queryset = self.queryset.all()
        else:
            queryset = self.queryset
        return queryset

    def get_pydantic_class(self) -> Type[P]:
        assert self.pydantic_class is not None, (
            "'%s' should either include a `pydantic_class` attribute, "
            "or override the `get_pydantic_class()` method."
            % self.__class__.__name__
        )
        return self.pydantic_class

    async def validate_request(self) -> P:
        pydantic_class = self.get_pydantic_class()
        data = await self.request.json()
        try:
            instance = pydantic_class(**data)
        except ValidationError as e:
            raise ValueError({"errors": e.errors()})
        return instance

    async def get_object(self) -> T:
        queryset = await self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.request.path_params[lookup_url_kwarg]}
        try:
            obj = await queryset.get(**filter_kwargs)
        except Exception as e:
            raise ValueError(f"Object not found: {e}")
        return obj

    def format_error_response(self, message: str, status_code: int = 400, details: Optional[Dict] = None) -> Dict:
        return {
            "status": "error",
            "message": message,
            "code": status_code,
            "details": details or {}
        }

    def format_success_response(self, data: Any, status_code: int = 200) -> Dict:
        return {
            "status": "success",
            "code": status_code,
            "data": data
        }