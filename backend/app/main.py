from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import engine, Base, get_db
from .models import User, Payer, Plan, ProviderGroup, Provider, ServiceLine, FeeSchedule
from .schemas import UserCreate, UserResponse, UserUpdate, PlanCreate, PlanResponse, PlanUpdate, PayerCreate, PayerResponse, PayerUpdate, ProviderGroupCreate, ProviderGroupResponse, ProviderGroupUpdate, ProviderCreate, ProviderResponse, ProviderUpdate, ServiceLineCreate, ServiceLineResponse, ServiceLineUpdate, FeeScheduleCreate, FeeScheduleResponse, FeeScheduleUpdate
from .services.etl import start_etl_job

# Create tables automatically
#Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow frontend to call FastAPI from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify your frontend URL)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root():
    return {"message": "FastAPI is running with PostgreSss@"}

@app.get("/rates/{billing_code}/{payer_id}")
def get_rates(billing_code: str, payer_id: int, db: Session = Depends(get_db)):
    sql_query = text("""
        SELECT pg.payer_assigned_id, nr.negotiated_rate
        FROM negotiated_rates nr
        JOIN service_lines sl ON nr.service_line_id = sl.id
        JOIN negotiated_rate_provider_groups nrpg ON nr.id = nrpg.negotiated_rate_id
        JOIN provider_groups pg ON nrpg.provider_group_id = pg.id
        WHERE sl.billing_code = :billing_code
        AND nr.payer_id = :payer_id
        ORDER BY nr.negotiated_rate DESC
    """)

    result = db.execute(sql_query, {"billing_code": billing_code, "payer_id": payer_id}).fetchall()
    
    # Convert result to a list of dictionaries
    return [{"payer_assigned_id": row[0], "negotiated_rate": row[1]} for row in result]

@app.post("/etl/start")
def trigger_etl():
    job_id = start_etl_job("process_data")
    return {"message": "ETL job started", "job_id": job_id}

### 🟢 CREATE a New User
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

### 🔵 READ All Users
@app.get("/users/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

### 🟡 READ a Single User by ID
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    print(user_id)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

### 🟠 UPDATE a User by ID
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = user_update.name
    user.email = user_update.email
    db.commit()
    db.refresh(user)
    return user

### 🔴 DELETE a User by ID
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

### 🟢 CREATE a New Plan
@app.post("/plans/", response_model=PlanResponse)
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    new_plan = Plan(**plan.dict())
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan 

### 🔵 READ All Plans
@app.get("/plans/", response_model=list[PlanResponse])
def get_plans(
    db: Session = Depends(get_db),
    name: str | None = Query(None),  # Optional filtering by name
    category: str | None = Query(None)  # Example: filter by category
):
    query = db.query(Plan)

    if name:
        query = query.filter(Plan.name.ilike(f"%{name}%"))  # Case-insensitive search
    if category:
        query = query.filter(Plan.category == category)

    return query.all()

### 🟡 READ a Single Plan by ID
@app.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

### 🟠 UPDATE a Plan by ID
@app.put("/plans/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: int, plan_update: PlanUpdate, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    for key, value in plan_update.dict(exclude_unset=True).items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan

### 🔴 DELETE a Plan by ID
@app.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    db.delete(plan)
    db.commit()
    return {"message": "Plan deleted successfully"}

### 🟢 CREATE a New Payer
@app.post("/payers/", response_model=PayerResponse)
def create_payer(payer: PayerCreate, db: Session = Depends(get_db)):
    new_payer = Payer(**payer.dict())
    db.add(new_payer)
    db.commit()
    db.refresh(new_payer)
    return new_payer

### 🔵 READ All Payers
@app.get("/payers/", response_model=list[PayerResponse])
def get_payers(
        db: Session = Depends(get_db),
        name: str | None = Query(None),  # Optional filtering by name
):
    query = db.query(Payer)

    if name:
        query = query.filter(Payer.name.ilike(f"%{name}%"))  # Case-insensitive search
    
    return query.all()

### 🟡 READ a Single Payer by ID
@app.get("/payers/{payer_id}", response_model=PayerResponse)
def get_payer(payer_id: int, db: Session = Depends(get_db)):
    payer = db.query(Payer).filter(Payer.id == payer_id).first()
    if not payer:
        raise HTTPException(status_code=404, detail="Payer not found")
    return payer

### 🟠 UPDATE a Payer by ID
@app.put("/payers/{payer_id}", response_model=PayerResponse)
def update_payer(payer_id: int, payer_update: PayerUpdate, db: Session = Depends(get_db)):
    payer = db.query(Payer).filter(Payer.id == payer_id).first()
    if not payer:
        raise HTTPException(status_code=404, detail="Payer not found")

    for key, value in payer_update.dict(exclude_unset=True).items():
        setattr(payer, key, value)
    db.commit()
    db.refresh(payer)
    return payer

### 🔴 DELETE a Payer by ID
@app.delete("/payers/{payer_id}")
def delete_payer(payer_id: int, db: Session = Depends(get_db)):
    payer = db.query(Payer).filter(Payer.id == payer_id).first()
    if not payer:
        raise HTTPException(status_code=404, detail="Payer not found")

    db.delete(payer)
    db.commit()
    return {"message": "Payer deleted successfully"}

### 🟢 CREATE a New Provider Group
@app.post("/provider-groups/", response_model=ProviderGroupResponse)
def create_provider_group(provider_group: ProviderGroupCreate, db: Session = Depends(get_db)):
    new_provider_group = ProviderGroup(**provider_group.dict())
    db.add(new_provider_group)
    db.commit()
    db.refresh(new_provider_group)
    return new_provider_group

### 🔵 READ All Provider Groups
@app.get("/provider-groups/", response_model=list[ProviderGroupResponse])
def get_provider_groups(
        db: Session = Depends(get_db),
        payer_id: int | None = Query(None),  # Optional filtering by payer_id
        payer_assigned_id: int | None = Query(None),  # Optional filtering by payer_assigned_id
        ein: int | None = Query(None),  # Optional filtering by ein
):
    query = db.query(ProviderGroup)

    if payer_id:
        query = query.filter(ProviderGroup.payer_id == payer_id)
    
    if payer_assigned_id:
        query = query.filter(ProviderGroup.payer_assigned_id == payer_assigned_id)
    
    if ein:
        query = query.filter(ProviderGroup.ein == ein)
    
    return query.all()

### 🟡 READ a Single Provider Group by ID
@app.get("/provider-groups/{provider_group_id}", response_model=ProviderGroupResponse)
def get_provider_group(provider_group_id: int, db: Session = Depends(get_db)):
    provider_group = db.query(ProviderGroup).filter(ProviderGroup.id == provider_group_id).first()
    if not provider_group:
        raise HTTPException(status_code=404, detail="Provider Group not found")
    return provider_group

### 🟠 UPDATE a Provider Group by ID
@app.put("/provider-groups/{provider_group_id}", response_model=ProviderGroupResponse)
def update_provider_group(provider_group_id: int, provider_group_update: ProviderGroupUpdate, db: Session = Depends(get_db)):
    provider_group = db.query(ProviderGroup).filter(ProviderGroup.id == provider_group_id).first()
    if not provider_group:
        raise HTTPException(status_code=404, detail="Provider Group not found")

    for key, value in provider_group_update.dict(exclude_unset=True).items():
        setattr(provider_group, key, value)
    db.commit()
    db.refresh(provider_group)
    return provider_group

### 🔴 DELETE a Provider Group by ID
@app.delete("/provider-groups/{provider_group_id}")
def delete_provider_group(provider_group_id: int, db: Session = Depends(get_db)):
    provider_group = db.query(ProviderGroup).filter(ProviderGroup.id == provider_group_id).first()
    if not provider_group:
        raise HTTPException(status_code=404, detail="Provider Group not found")

    db.delete(provider_group)
    db.commit()
    return {"message": "Provider Group deleted successfully"}

### 🟢 CREATE a New Provider
@app.post("/providers/", response_model=ProviderResponse)
def create_provider(provider: ProviderCreate, db: Session = Depends(get_db)):
    new_provider = Provider(**provider.dict())
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    return new_provider

### 🔵 READ All Providers
@app.get("/providers/", response_model=list[ProviderResponse])
def get_providers(
        db: Session = Depends(get_db),
        npi: str | None = Query(None),  # Optional filtering by npi
):
    query = db.query(Provider)

    if npi:
        query = query.filter(Provider.npi == npi)
    
    return query.all()

### 🟡 READ a Single Provider by ID
@app.get("/providers/{provider_id}", response_model=ProviderResponse)
def get_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

### 🟠 UPDATE a Provider by ID
@app.put("/providers/{provider_id}", response_model=ProviderResponse)
def update_provider(provider_id: int, provider_update: ProviderUpdate, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    for key, value in provider_update.dict(exclude_unset=True).items():
        setattr(provider, key, value)
    db.commit()
    db.refresh(provider)
    return

### 🔴 DELETE a Provider by ID
@app.delete("/providers/{provider_id}")
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    db.delete(provider)
    db.commit()
    return {"message": "Provider deleted successfully"}

### 🟢 CREATE a New Service Line
@app.post("/service-lines/", response_model=ServiceLineResponse)
def create_service_line(service_line: ServiceLineCreate, db: Session = Depends(get_db)):
    new_service_line = ServiceLine(**service_line.dict())
    db.add(new_service_line)
    db.commit()
    db.refresh(new_service_line)
    return new_service_line

### 🔵 READ All Service Lines
@app.get("/service-lines/", response_model=list[ServiceLineResponse])
def get_service_lines(
        db: Session = Depends(get_db),
        billing_code: str | None = Query(None),  # Optional filtering by billing_code
        billing_code_type: str | None = Query(None),  # Optional filtering by billing_code_type
):
    query = db.query(ServiceLine)

    if billing_code:
        query = query.filter(ServiceLine.billing_code == billing_code)
    
    if billing_code_type:
        query = query.filter(ServiceLine.billing_code_type == billing_code_type)
    
    return query.all()

### 🟡 READ a Single Service Line by ID
@app.get("/service-lines/{service_line_id}", response_model=ServiceLineResponse)
def get_service_line(service_line_id: int, db: Session = Depends(get_db)):
    service_line = db.query(ServiceLine).filter(ServiceLine.id == service_line_id).first()
    if not service_line:
        raise HTTPException(status_code=404, detail="Service Line not found")
    return service_line

### 🟠 UPDATE a Service Line by ID
@app.put("/service-lines/{service_line_id}", response_model=ServiceLineResponse)
def update_service_line(service_line_id: int, service_line_update: ServiceLineUpdate, db: Session = Depends(get_db)):
    service_line = db.query(ServiceLine).filter(ServiceLine.id == service_line_id).first()
    if not service_line:
        raise HTTPException(status_code=404, detail="Service Line not found")

    for key, value in service_line_update.dict(exclude_unset=True).items():
        setattr(service_line, key, value)
    db.commit()
    db.refresh(service_line)
    return service_line

### 🔴 DELETE a Service Line by ID
@app.delete("/service-lines/{service_line_id}")
def delete_service_line(service_line_id: int, db: Session = Depends(get_db)):
    service_line = db.query(ServiceLine).filter(ServiceLine.id == service_line_id).first()
    if not service_line:
        raise HTTPException(status_code=404, detail="Service Line not found")

    db.delete(service_line)
    db.commit()
    return {"message": "Service Line deleted successfully"}

### 🟢 CREATE a New Fee Schedule
@app.post("/fee-schedules/", response_model=FeeScheduleResponse)
def create_fee_schedule(fee_schedule: FeeScheduleCreate, db: Session = Depends(get_db)):
    new_fee_schedule = FeeSchedule(**fee_schedule.dict())
    db.add(new_fee_schedule)
    db.commit()
    db.refresh(new_fee_schedule)

### 🔵 READ All Fee Schedules
@app.get("/fee-schedules/", response_model=list[FeeScheduleResponse])
def get_fee_schedules(
        db: Session = Depends(get_db),
        payer_id: int | None = Query(None),  # Optional filtering by payer_id
        description: str | None = Query(None),  # Optional filtering by description
        source_file_url: str | None = Query(None),  # Optional filtering by source_file_url
):
    query = db.query(FeeSchedule)

    if payer_id:
        query = query.filter(FeeSchedule.payer_id == payer_id)

    if description:
        query = query.filter(FeeSchedule.description.ilike(f"%{description}%"))

    if source_file_url:
        query = query.filter(FeeSchedule.source_file_url == source_file_url)

    return query.all()

### 🟡 READ a Single Fee Schedule by ID
@app.get("/fee-schedules/{fee_schedule_id}", response_model=FeeScheduleResponse)
def get_fee_schedule(fee_schedule_id: int, db: Session = Depends(get_db)):
    fee_schedule = db.query(FeeSchedule).filter(FeeSchedule.id == fee_schedule_id).first()
    if not fee_schedule:
        raise HTTPException(status_code=404, detail="Fee Schedule not found")
    return fee_schedule

### 🟠 UPDATE a Fee Schedule by ID
@app.put("/fee-schedules/{fee_schedule_id}", response_model=FeeScheduleResponse)
def update_fee_schedule(fee_schedule_id: int, fee_schedule_update: FeeScheduleUpdate, db: Session = Depends(get_db)):
    fee_schedule = db.query(FeeSchedule).filter(FeeSchedule.id == fee_schedule_id).first()
    if not fee_schedule:
        raise HTTPException(status_code=404, detail="Fee Schedule not found")

    for key, value in fee_schedule_update.dict(exclude_unset=True).items():
        setattr(fee_schedule, key, value)
    db.commit()
    db.refresh(fee_schedule)
    return fee_schedule

### 🔴 DELETE a Fee Schedule by ID
@app.delete("/fee-schedules/{fee_schedule_id}")
def delete_fee_schedule(fee_schedule_id: int, db: Session = Depends(get_db)):
    fee_schedule = db.query(FeeSchedule).filter(FeeSchedule.id == fee_schedule_id).first()
    if not fee_schedule:
        raise HTTPException(status_code=404, detail="Fee Schedule not found")

    db.delete(fee_schedule)
    db.commit()
    return {"message": "Fee Schedule deleted successfully"}

@app.get("/plans/{plan_id}/rates/{rate_id}")
def get_rate_with_benchmark(plan_id: int, rate_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            r.id AS rate_id,
            r.plan_id,
            r.service_code,
            r.amount AS provider_rate,
            p.group_name AS provider_group,
            br.amount AS benchmark_rate
        FROM rates r
        JOIN providers p ON r.provider_id = p.id
        LEFT JOIN rates br ON br.service_code = r.service_code 
            AND br.plan_id != :plan_id  -- Get benchmark rates from other plans
        WHERE r.id = :rate_id AND r.plan_id = :plan_id
    """)

    result = db.execute(query, {"plan_id": plan_id, "rate_id": rate_id}).fetchall()

    if not result:
        raise HTTPException(status_code=404, detail="Rate not found for this plan")

    return {
        "rate_id": result[0].rate_id,
        "plan_id": result[0].plan_id,
        "service_code": result[0].service_code,
        "provider_rate": result[0].provider_rate,
        "benchmarks": [
            {"provider_group": row.provider_group, "benchmark_rate": row.benchmark_rate}
            for row in result if row.benchmark_rate is not None
        ],
    }
