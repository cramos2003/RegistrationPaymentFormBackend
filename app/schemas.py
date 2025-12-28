from pydantic import BaseModel, EmailStr
    
# CAR REGISTRATION SCHEMA
class CarOrderCreate(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    zip: str
    carMake: str
    carModel: str
    year: str

# SPONSOR REGISTRATION SCHEMA
class SponsorOrderCreate(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: str
    company: str
    address: str
    city: str
    state: str
    zip: str
    
# VENDOR REGISTRATION SCHEMA
class VendorOrderCreate(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: str
    company: str
    address: str
    city: str
    state: str
    zip: str
    vendorType: str
    vendorSize: str
    businessLicense: str
    insuranceNumber: str
    vendorDescription: str
    agreement: bool