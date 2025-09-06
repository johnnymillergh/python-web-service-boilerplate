import ast
import importlib
import pkgutil
from pathlib import Path
from types import ModuleType
from typing import Final

from fastapi import APIRouter, FastAPI
from loguru import logger

from python_web_service_boilerplate.common.profiling import elapsed_time

ALL_SCOPES: Final[set[str]] = set()


# noinspection D
def extract_scopes(module: ModuleType) -> None:
    # Scope extraction logic
    # Try to get the module's file path
    module_file = Path(getattr(module, "__file__", ""))
    if module_file.is_file():
        try:
            with module_file.open(mode="r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=module_file)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for deco in node.decorator_list:
                        # Check for require_scopes decorator
                        if (
                            isinstance(deco, ast.Call)
                            and getattr(deco.func, "id", None) == "require_scopes"
                            and deco.args
                            and isinstance(deco.args[0], ast.Set)
                        ):
                            # Only handle set literals: require_scopes({"scope1", "scope2"})
                            logger.warning(f"Found @require_scopes args[0]: {ast.dump(deco.args[0])}, in {module_file}")
                            # noinspection PyUnresolvedReferences
                            for elt in deco.args[0].elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    ALL_SCOPES.add(elt.value)
        except Exception as e:
            logger.warning(f"Failed to parse {module_file} for scopes: {e}")


# noinspection D
@elapsed_time("WARNING")
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

                extract_scopes(module)

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
            f"from base package `{base_package}`. All scopes: {ALL_SCOPES}"
        )
    except ImportError as e:
        logger.error(f"Failed to include routers from base package `{base_package}`: {e}")
        return
