from pydantic import BaseModel, Field
from typing import List

class FacilityFacts(BaseModel):
    """Extraction schema for unstructured medical notes."""
    
    # Removed the strict Literal/Enum to allow free-text specialties
    specialties: List[str] = Field(
        default=[],
        description="Medical focuses mentioned, e.g., 'HIV/AIDS', 'TB', 'Pediatrics', 'Maternal'."
    )
    # Changed 'procedure' to 'services' to capture general care
    services: List[str] = Field(
        default=[],
        description="General healthcare services, e.g., 'prevention', 'behavioral care', 'surgeries'."
    )
    equipment: List[str] = Field(
        default=[],
        description="Physical medical devices, imaging, or beds. E.g., 'MRI', 'Ambulance'."
    )
    capability: List[str] = Field(
        default=[],
        description="Level of care or facility descriptors, e.g., 'grassroots initiative', 'ICU', 'trauma center'."
    )