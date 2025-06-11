from pydantic import BaseModel, ConfigDict


class DataModel(BaseModel):
    """
    A model for shared configuration of data models.
    """

    # Allow instances to be created from other objects' attributes
    model_config = ConfigDict(from_attributes=True)
