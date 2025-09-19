from pydantic import BaseModel, ConfigDict


class ProductOrderBase(BaseModel):
    order_number: str
    product_name: str
    shipping_address: str
    shipping_status: str


class ProductOrderCreate(ProductOrderBase):
    pass


class ProductOrderUpdate(ProductOrderBase):
    pass


class ProductOrderRead(ProductOrderBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
