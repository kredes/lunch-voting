from pydantic import BaseModel, ConfigDict


class DataModel(BaseModel):
    """
    A model for shared configuration of data models.
    """

    # Allow instances to be created from other objects' attributes
    model_config = ConfigDict(from_attributes=True)


class PaginationInfo(DataModel):
    """
    Information about the pagination of an endpoint.
    """

    offset: int
    limit: int
    total: int
