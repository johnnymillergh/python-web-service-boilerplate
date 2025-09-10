from advanced_alchemy import repository

from python_web_service_boilerplate.core.auth.models import User


class Repository(repository.SQLAlchemyAsyncRepository[User]):
    model_type = User
