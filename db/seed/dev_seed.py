"""Script to give the developer an example to work with"""

import os

from common.database_engine import DBEngine
from common.models import Account, CuecodeConfig, OpenAPISpec

engine: DBEngine = DBEngine()
session = engine.get_session()

PET_CONFIG_ID = "ca7c4e5d-4f5d-47b6-a06e-e786b8e45b55"
PET_SPEC_ID = "ca754e5d-4f5d-47b6-a06e-e786b8e45b55"
ACCOUNT_ID = "ca754e5d-4f5d-47b6-a06e-e786b8e45b53"

pet_cuecode_config = CuecodeConfig(cuecode_config_id=PET_CONFIG_ID)

USER = Account(cuecode_account_id=ACCOUNT_ID, email="Guest", password="Guest")

session.add(USER)

session.add(pet_cuecode_config)

with open(
    os.path.join("src", "tests", "fixtures", "openapi", "pet-store.json"),
    "r",
    encoding="UTF-8",
) as f:
    pet_spec: OpenAPISpec = OpenAPISpec(
        openapi_spec_id=PET_SPEC_ID,
        spec_text=f.read(),
        cuecode_config_id=pet_cuecode_config.cuecode_config_id,
        base_url="https://localhost/",
    )  # type: ignore

    session.add(pet_spec)

session.commit()
