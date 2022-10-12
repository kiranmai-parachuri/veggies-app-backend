from veggies_service.utils.resource import BaseResource


class Ping(BaseResource):
    def get(self):
        return {"message": "success"}
