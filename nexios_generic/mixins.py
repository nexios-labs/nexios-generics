from typing import Type, Any, List
from nexios.http import Response, Request
from tortoise.models import Model
from tortoise.queryset import QuerySet
from pydantic import BaseModel

class CreateModelMixin:
    async def create(self, req: Request, res: Response) -> Response:
        try:
            instance = await self.validate_request()
        except ValueError as e:
            return self.handle_validation_error(res, e)

        try:
            db_instance = await self.perform_create(instance)
        except Exception as e:
            return self.handle_create_error(res, e)

        return self.handle_create_success(res, db_instance)

    async def perform_create(self, instance: BaseModel) -> Model:
        return await self.queryset.create(**instance.dict())

    def handle_validation_error(self, res: Response, error: ValueError) -> Response:
        return res.status(400).json(self.format_error_response("Validation failed", details=error.args[0]))

    def handle_create_error(self, res: Response, error: Exception) -> Response:
        return res.status(500).json(self.format_error_response("Failed to create object", details=str(error)))

    def handle_create_success(self, res: Response, instance: Model) -> Response:
        return res.status(201).json(self.format_success_response(instance.dict()))

class RetrieveModelMixin:
    async def retrieve(self, req: Request, res: Response) -> Response:
        try:
            obj = await self.get_object()
        except ValueError as e:
            return self.handle_not_found_error(res, e)

        serialized_obj = await self.serialize_object(obj)
        return self.handle_retrieve_success(res, serialized_obj)

    async def serialize_object(self, obj: Model) -> dict:
        pydantic_class = self.get_pydantic_class()
        return pydantic_class.from_orm(obj).dict()

    def handle_not_found_error(self, res: Response, error: ValueError) -> Response:
        return res.status(404).json(self.format_error_response(str(error)))

    def handle_retrieve_success(self, res: Response, serialized_obj: dict) -> Response:
        return res.status(200).json(self.format_success_response(serialized_obj))

class ListModelMixin:
    async def list(self, req: Request, res: Response) -> Response:
        queryset = await self.get_queryset()
        try:
            objects = await self.perform_list(queryset)
        except Exception as e:
            return self.handle_list_error(res, e)

        serialized_objects = await self.serialize_objects(objects)
        return self.handle_list_success(res, serialized_objects)

    async def perform_list(self, queryset: QuerySet) -> List[Model]:
        return queryset

    async def serialize_objects(self, objects: List[Model]) -> List[dict]:
        pydantic_class = self.get_pydantic_class()
        return [pydantic_class.from_orm(obj).dict() for obj in objects]

    def handle_list_error(self, res: Response, error: Exception) -> Response:
        raise error
    def handle_list_success(self, res: Response, serialized_objects: List[dict]) -> Response:
        return res.status(200).json(self.format_success_response(serialized_objects))

class DeleteModelMixin:
    async def delete(self, req: Request, res: Response) -> Response:
        try:
            obj = await self.get_object()
        except ValueError as e:
            return self.handle_not_found_error(res, e)

        try:
            await self.perform_delete(obj)
        except Exception as e:
            return self.handle_delete_error(res, e)

        return self.handle_delete_success(res)

    async def perform_delete(self, obj: Model) -> None:
        await obj.delete()

    def handle_delete_error(self, res: Response, error: Exception) -> Response:
        raise error

    def handle_delete_success(self, res: Response) -> Response:
        return res.status(204).json(self.format_success_response(None, status_code=204))

class UpdateModelMixin:
    async def update(self, req: Request, res: Response) -> Response:
        try:
            obj = await self.get_object()
        except ValueError as e:
            return self.handle_not_found_error(res, e)

        try:
            instance = await self.validate_request()
        except ValueError as e:
            return self.handle_validation_error(res, e)

        try:
            updated_obj = await self.perform_update(obj, instance)
        except Exception as e:
            return self.handle_update_error(res, e)

        serialized_obj = await self.serialize_object(updated_obj)
        return self.handle_update_success(res, serialized_obj)

    async def perform_update(self, obj: Model, instance: BaseModel) -> Model:
        for key, value in instance.dict().items():
            setattr(obj, key, value)
        await obj.save()
        return obj

    def handle_update_error(self, res: Response, error: Exception) -> Response:
        return res.status(500).json(self.format_error_response("Failed to update object", details=str(error)))

    def handle_update_success(self, res: Response, serialized_obj: dict) -> Response:
        return res.status(200).json(self.format_success_response(serialized_obj))