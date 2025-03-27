from .base import GenericAPIView
from .mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DeleteModelMixin

class ListCreateAPIView(ListModelMixin, CreateModelMixin, GenericAPIView):
    async def get(self, req, res):
        return await self.list(req, res)
    
    async def post(self, req, res):
        return await self.create(req, res)

class RetrieveUpdateDestroyAPIView(RetrieveModelMixin, UpdateModelMixin, DeleteModelMixin, GenericAPIView):
    async def get(self, req, res):
        return await self.retrieve(req, res)
    
    async def put(self, req, res):
        return await self.update(req, res)
    
    async def delete(self, req, res):
        return await self.delete(req, res)

class ListCreateRetrieveUpdateDestroyAPIView(ListCreateAPIView, RetrieveUpdateDestroyAPIView):
    pass