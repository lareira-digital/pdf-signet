from typing import Optional
from pydantic import BaseModel, Field

class Coordinates(BaseModel):
    pos_x: Optional[int] = Field(
        ...,
        title="Position in X axis",
        description="Position in X axis in units within the document"
    )
    pos_y: Optional[int] = Field(
        ...,
        title="Position in Y axis",
        description="Position in Y axis in units within the document"
    )
    height: Optional[int] = Field(
        ...,
        title="Bounding box height",
        description="Bounding box height in units within the document"
    )
    width: Optional[int] = Field(
        ...,
        title="Bounding box width",
        description="Bounding box width in units within the document"
    )

class PDFPayload(BaseModel):
    certificate: bytes = Field(
        ...,
        title="Certificate file",
        description="Certificate file in base64 format"
    )
    pdf: bytes = Field(
        ...,
        title="PDF file",
        description="PDF file in base64 format"
    )
    pages: Optional[list] = Field(
        ...,
        title="Pages to sign",
        description="Selector of the pages you want to sign"
    )
    coordinates: Optional[Coordinates]
    background: Optional[bytes] = Field(
        ...,
        title="Image background",
        description="Image background for the stamp"
    )
    text: str = Field(
        default="Signed by: %(signer)s\nDate: %(ts)s",
        title="Signature text",
        description="Signature text"
    )
