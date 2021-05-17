from fastapi import Path


def owner_id_parameter(
    owner_id: str = Path(..., regex="^[a-z0-9]{32}$", description="オーナーID")
):
    return owner_id
