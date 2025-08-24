import importlib
import pkgutil

from fastapi import APIRouter, FastAPI
from loguru import logger


# noinspection D
def include_routers(app: FastAPI, base_package: str = "app") -> None:
    try:
        # Import the base package to get its path
        package = importlib.import_module(base_package)
        package_path = package.__path__
        logger.warning(f"Including routers in base package: {base_package}, from path: {package_path}")

        router_counter = 0
        routes_counter = 0
        # Walk through all modules in the package and subpackages
        for _finder, module_name, _is_pkg in pkgutil.walk_packages(package_path, base_package + "."):
            try:
                # Skip __pycache__ and other non-module directories
                if "__pycache__" in module_name:
                    continue

                module = importlib.import_module(module_name)

                # Find any APIRouter instance in the module
                for attr_name in dir(module):
                    if not attr_name.startswith("_"):  # Skip private attributes
                        attr = getattr(module, attr_name)
                        if isinstance(attr, APIRouter):
                            app.include_router(attr)
                            router_counter += 1
                            routes_counter += len(attr.routes)
                            logger.warning(
                                f"Included router from {module_name}.{attr_name}. "
                                f"{len(attr.routes)} routes: {attr.routes}"
                            )
            except ImportError as e:
                # Log the error but continue with other modules
                logger.warning(f"Failed to import module {module_name}: {e}")
                continue
        logger.warning(
            f"Included {router_counter} routers with total {routes_counter} routes "
            f"from base package `{base_package}`"
        )
    except ImportError as e:
        logger.error(f"Failed to include routers from base package `{base_package}`: {e}")
        return
