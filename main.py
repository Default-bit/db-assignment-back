from decimal import Decimal
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import databases
import sqlalchemy
from datetime import date
from datetime import time
from pydantic import BaseModel, Field
from typing import Optional

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATABASE_URL = 'postgresql://postgres:mysecretpassword@localhost/dbassignment'
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

user_tag = "User"
caregiver_tag = "Caregiver"
member_tag = "Member"
address_tag = "Address"
job_tag = "Job"
job_application_tag = "Job Application"
appointment_tag = "Appointment"



# Users
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("user_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(length=255)),
    sqlalchemy.Column("given_name", sqlalchemy.String(length=255)),
    sqlalchemy.Column("surname", sqlalchemy.String(length=255)),
    sqlalchemy.Column("city", sqlalchemy.String(length=255)),
    sqlalchemy.Column("phone_number", sqlalchemy.String(length=20)),
    sqlalchemy.Column("profile_description", sqlalchemy.Text),
    sqlalchemy.Column("password", sqlalchemy.String(length=255)),
)

class UserIn(BaseModel):
    email: EmailStr
    given_name: str
    surname: str
    city: str
    phone_number: str
    profile_description: Optional[str] = None
    password: str

class UserOut(UserIn):
    user_id: int

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    given_name: Optional[str] = None
    surname: Optional[str] = None
    city: Optional[str] = None
    phone_number: Optional[str] = None
    profile_description: Optional[str] = None
    password: Optional[str] = None

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# CRUD for Users Table
@app.post("/users/", response_model=UserOut, tags=[user_tag])
async def create_user(user: UserIn):
    query = users.insert().values(**user.dict())
    user_id = await database.execute(query)
    return {**user.dict(), "user_id": user_id}

@app.get("/users/", response_model=List[UserOut], tags=[user_tag])
async def read_users(skip: int = 0, limit: int = 20):
    query = users.select().offset(skip).limit(limit)
    return await database.fetch_all(query)

@app.get("/users/{user_id}", response_model=UserOut, tags=[user_tag])
async def read_user(user_id: int):
    query = users.select().where(users.c.user_id == user_id)
    user = await database.fetch_one(query)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserOut, tags=[user_tag])
async def update_user(user_id: int, user: UserUpdate):
    query = users.update().where(users.c.user_id == user_id).values(**user.dict())
    await database.execute(query)
    return {**user.dict(), "user_id": user_id}

@app.delete("/users/{user_id}", response_model=dict, tags=[user_tag])
async def delete_user(user_id: int):
    query = users.delete().where(users.c.user_id == user_id)
    await database.execute(query)
    return {"message": "User with id: {} deleted successfully".format(user_id)}



# Caregivers
caregivers = sqlalchemy.Table(
    "caregivers",
    metadata,
    sqlalchemy.Column("caregiver_user_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("photo", sqlalchemy.LargeBinary),  # bytea for binary data
    sqlalchemy.Column("gender", sqlalchemy.String(length=50)),
    sqlalchemy.Column("caregiving_type", sqlalchemy.String(length=255)),
    sqlalchemy.Column("hourly_rate", sqlalchemy.Numeric(5, 2)),
)

class CaregiverIn(BaseModel):
    caregiver_user_id: int
    photo: Optional[str] = None
    gender: str
    caregiving_type: str
    hourly_rate: Decimal

class CaregiverOut(CaregiverIn):
    caregiver_id: int

class CaregiverUpdate(BaseModel):
    photo: Optional[str] = None
    gender: Optional[str] = None
    caregiving_type: Optional[str] = None
    hourly_rate: Optional[Decimal] = None

# CRUD for caregivers
@app.post("/caregivers/", response_model=CaregiverOut, tags=[caregiver_tag])
async def create_caregiver(caregiver: CaregiverIn):
    query = caregivers.insert().values(**caregiver.dict())
    last_record_id = await database.execute(query)
    return {**caregiver.dict(), "caregiver_user_id": last_record_id}

@app.get("/caregivers/", response_model=List[CaregiverOut], tags=[caregiver_tag])
async def read_caregivers(skip: int = 0, limit: int = 20):
    query = caregivers.select().offset(skip).limit(limit)
    return await database.fetch_all(query)

@app.get("/caregivers/{caregiver_id}", response_model=CaregiverOut, tags=[caregiver_tag])
async def read_caregiver(caregiver_id: int):
    query = caregivers.select().where(caregivers.c.caregiver_user_id == caregiver_id)
    caregiver = await database.fetch_one(query)
    if caregiver is None:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    return caregiver

@app.put("/caregivers/{caregiver_id}", response_model=CaregiverOut, tags=[caregiver_tag])
async def update_caregiver(caregiver_id: int, caregiver: CaregiverUpdate):
    query = caregivers.update().where(caregivers.c.caregiver_user_id == caregiver_id).values(**caregiver.dict())
    await database.execute(query)
    return {**caregiver.dict(), "caregiver_user_id": caregiver_id}

@app.delete("/caregivers/{caregiver_id}", response_model=dict, tags=[caregiver_tag])
async def delete_caregiver(caregiver_id: int):
    query = caregivers.delete().where(caregivers.c.caregiver_user_id == caregiver_id)
    await database.execute(query)
    return {"message": f"Caregiver with id {caregiver_id} deleted successfully."}



# Members
members = sqlalchemy.Table(
    "members",
    metadata,
    sqlalchemy.Column("member_user_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("house_rules", sqlalchemy.Text, nullable=False),
)

class MemberIn(BaseModel):
    member_user_id: int
    house_rules: str

class MemberOut(MemberIn):
    member_id: int

class MemberUpdate(BaseModel):
    house_rules: Optional[str] = None


# CRUD for members
@app.post("/members/", response_model=MemberOut, tags=[member_tag])
async def create_member(member: MemberIn):
    query = members.insert().values(**member.dict())
    last_record_id = await database.execute(query)
    return {**member.dict(), "member_user_id": last_record_id}

@app.get("/members/{member_id}", response_model=MemberOut, tags=[member_tag])
async def read_member(member_id: int):
    query = members.select().where(members.c.member_user_id == member_id)
    member = await database.fetch_one(query)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member

@app.put("/members/{member_id}", response_model=MemberOut, tags=[member_tag])
async def update_member(member_id: int, member: MemberUpdate):
    query = members.update().where(members.c.member_user_id == member_id).values(**member.dict())
    await database.execute(query)
    return {**member.dict(), "member_user_id": member_id}

@app.delete("/members/{member_id}", response_model=dict, tags=[member_tag])
async def delete_member(member_id: int):
    query = members.delete().where(members.c.member_user_id == member_id)
    await database.execute(query)
    return {"message": f"Member with id {member_id} deleted successfully."}

@app.get("/members/", response_model=List[MemberOut], tags=[member_tag])
async def read_members(skip: int = 0, limit: int = 20):
    query = members.select().offset(skip).limit(limit)
    return await database.fetch_all(query)



# Address
address = sqlalchemy.Table(
    "address",
    metadata,
    sqlalchemy.Column("member_user_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("house_number", sqlalchemy.String(length=255), nullable=False),
    sqlalchemy.Column("street", sqlalchemy.String(length=255), nullable=False),
    sqlalchemy.Column("town", sqlalchemy.String(length=255), nullable=False),
)

class AddressIn(BaseModel):
    member_user_id: int
    house_number: str
    street: str
    town: str

class AddressOut(AddressIn):
    pass

class AddressUpdate(BaseModel):
    house_number: Optional[str] = None
    street: Optional[str] = None
    town: Optional[str] = None

# CRUD for address
@app.post("/address/", response_model=AddressOut, tags=[address_tag])
async def create_address(address_data: AddressIn):
    query = address.insert().values(**address_data.dict())
    last_record_id = await database.execute(query)
    return {**address_data.dict(), "member_user_id": last_record_id}

@app.get("/address/{member_user_id}", response_model=AddressOut, tags=[address_tag])
async def read_address(member_user_id: int):
    query = address.select().where(address.c.member_user_id == member_user_id)
    address_record = await database.fetch_one(query)
    if address_record is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return address_record

@app.put("/address/{member_user_id}", response_model=AddressOut, tags=[address_tag])
async def update_address(member_user_id: int, address_data: AddressUpdate):
    query = address.update().where(address.c.member_user_id == member_user_id).values(**address_data.dict())
    await database.execute(query)
    return {**address_data.dict(), "member_user_id": member_user_id}

@app.delete("/address/{member_user_id}", response_model=dict, tags=[address_tag])
async def delete_address(member_user_id: int):
    query = address.delete().where(address.c.member_user_id == member_user_id)
    await database.execute(query)
    return {"message": f"Address for member user id {member_user_id} deleted successfully."}

@app.get("/address/", response_model=List[AddressOut], tags=[address_tag])
async def read_all_addresses(skip: int = 0, limit: int = 20):
    query = address.select().offset(skip).limit(limit)
    return await database.fetch_all(query)



# Jobs
jobs = sqlalchemy.Table(
    "jobs",
    metadata,
    sqlalchemy.Column("job_id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("member_user_id", sqlalchemy.Integer),
    sqlalchemy.Column("required_caregiving_type", sqlalchemy.String(length=255), nullable=False),
    sqlalchemy.Column("other_requirements", sqlalchemy.Text),
    sqlalchemy.Column("date_posted", sqlalchemy.Date, nullable=False),
)

class JobIn(BaseModel):
    member_user_id: int
    required_caregiving_type: str
    other_requirements: Optional[str]
    date_posted: date

class JobOut(JobIn):
    job_id: int

class JobUpdate(BaseModel):
    member_user_id: Optional[int]
    required_caregiving_type: Optional[str]
    other_requirements: Optional[str]
    date_posted: Optional[date]

# CRUD for jobs
@app.post("/jobs/", response_model=JobOut, tags=[job_tag])
async def create_job(job: JobIn):
    query = jobs.insert().values(**job.dict())
    job_id = await database.execute(query)
    return {**job.dict(), "job_id": job_id}

@app.get("/jobs/{job_id}", response_model=JobOut, tags=[job_tag])
async def read_job(job_id: int):
    query = jobs.select().where(jobs.c.job_id == job_id)
    job = await database.fetch_one(query)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.put("/jobs/{job_id}", response_model=JobOut, tags=[job_tag])
async def update_job(job_id: int, job: JobUpdate):
    query = jobs.update().where(jobs.c.job_id == job_id).values(**job.dict())
    await database.execute(query)
    return {**job.dict(), "job_id": job_id}

@app.delete("/jobs/{job_id}", response_model=dict, tags=[job_tag])
async def delete_job(job_id: int):
    query = jobs.delete().where(jobs.c.job_id == job_id)
    await database.execute(query)
    return {"message": f"Job with id {job_id} deleted successfully."}

@app.get("/jobs/", response_model=List[JobOut], tags=[job_tag])
async def read_all_jobs(skip: int = 0, limit: int = 20):
    query = jobs.select().offset(skip).limit(limit)
    return await database.fetch_all(query)



# Job Applications
job_applications = sqlalchemy.Table(
    "job_applications",
    metadata,
    sqlalchemy.Column("caregiver_user_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("job_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("date_applied", sqlalchemy.Date, nullable=False),
)

class JobApplicationIn(BaseModel):
    caregiver_user_id: int
    job_id: int
    date_applied: date

class JobApplicationOut(JobApplicationIn):
    pass

# CRUD for job applications
@app.post("/job_applications/", response_model=JobApplicationOut, tags=[job_application_tag])
async def create_job_application(job_application: JobApplicationIn):
    query = job_applications.insert().values(**job_application.dict())
    await database.execute(query)
    return job_application

@app.get("/job_applications/{caregiver_user_id}/{job_id}", response_model=JobApplicationOut, tags=[job_application_tag])
async def read_job_application(caregiver_user_id: int, job_id: int):
    query = job_applications.select().where(
        (job_applications.c.caregiver_user_id == caregiver_user_id) &
        (job_applications.c.job_id == job_id)
    )
    job_application = await database.fetch_one(query)
    if job_application is None:
        raise HTTPException(status_code=404, detail="Job application not found")
    return job_application

@app.delete("/job_applications/{caregiver_user_id}/{job_id}", response_model=dict, tags=[job_application_tag])
async def delete_job_application(caregiver_user_id: int, job_id: int):
    query = job_applications.delete().where(
        (job_applications.c.caregiver_user_id == caregiver_user_id) &
        (job_applications.c.job_id == job_id)
    )
    await database.execute(query)
    return {"message": f"Job application from caregiver {caregiver_user_id} for job {job_id} deleted successfully."}

@app.get("/job_applications/", response_model=List[JobApplicationOut], tags=[job_application_tag])
async def read_all_job_applications(skip: int = 0, limit: int = 20):
    query = job_applications.select().offset(skip).limit(limit)
    return await database.fetch_all(query)



# Appointments
appointments = sqlalchemy.Table(
    "appointments",
    metadata,
    sqlalchemy.Column("appointment_id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("caregiver_user_id", sqlalchemy.Integer),
    sqlalchemy.Column("member_user_id", sqlalchemy.Integer),
    sqlalchemy.Column("appointment_date", sqlalchemy.Date, nullable=False),
    sqlalchemy.Column("appointment_time", sqlalchemy.Time, nullable=False),
    sqlalchemy.Column("work_hours", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("status", sqlalchemy.String(length=50), nullable=False),
)

class AppointmentIn(BaseModel):
    caregiver_user_id: int
    member_user_id: int
    appointment_date: date
    appointment_time: time
    work_hours: int
    status: str

class AppointmentOut(AppointmentIn):
    appointment_id: int

class AppointmentUpdate(BaseModel):
    caregiver_user_id: Optional[int] = None
    member_user_id: Optional[int] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    work_hours: Optional[int] = None
    status: Optional[str] = None


# CRUD for appointments
@app.post("/appointments/", response_model=AppointmentOut, tags=[appointment_tag])
async def create_appointment(appointment: AppointmentIn):
    query = appointments.insert().values(**appointment.dict())
    appointment_id = await database.execute(query)
    return {**appointment.dict(), "appointment_id": appointment_id}

@app.get("/appointments/{appointment_id}", response_model=AppointmentOut, tags=[appointment_tag])
async def read_appointment(appointment_id: int):
    query = appointments.select().where(appointments.c.appointment_id == appointment_id)
    appointment = await database.fetch_one(query)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@app.put("/appointments/{appointment_id}", response_model=AppointmentOut, tags=[appointment_tag])
async def update_appointment(appointment_id: int, appointment: AppointmentUpdate):
    query = appointments.update().where(appointments.c.appointment_id == appointment_id).values(**appointment.dict())
    await database.execute(query)
    return {**appointment.dict(), "appointment_id": appointment_id}

@app.delete("/appointments/{appointment_id}", response_model=dict, tags=[appointment_tag])
async def delete_appointment(appointment_id: int):
    query = appointments.delete().where(appointments.c.appointment_id == appointment_id)
    await database.execute(query)
    return {"message": f"Appointment with id {appointment_id} deleted successfully."}

@app.get("/appointments/", response_model=List[AppointmentOut], tags=[appointment_tag])
async def read_all_appointments(skip: int = 0, limit: int = 20):
    query = appointments.select().offset(skip).limit(limit)
    return await database.fetch_all(query)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")