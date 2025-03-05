import os
import json
import datetime
import requests
import gzip
import shutil
import urllib.parse
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models import Payer, Plan, FeeSchedule, PlanFeeSchedule

# Database setup
DATABASE_URL = "postgresql://postgres:Smartchoice1!@localhost/innersense"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

FILES_DIR = "files"
BCBS_IL_ID = 100 # Known BCBS IL

os.makedirs(FILES_DIR, exist_ok=True)

def load_json(file_path):
    """Load JSON file safely."""
    with open(file_path, "r") as file:
        return json.load(file)

def get_payer(session, payer_id):
    """Ensures a payer exists and returns the payer object."""
    payer = session.get(Payer, payer_id)
    return payer

def get_plan(session, payer_id, plan_data):
    """Ensures a plan exists and returns its ID."""
    plan = session.query(Plan).filter_by(
        payer_id=payer_id,
        name=plan_data["plan_name"]
    ).first()
    return plan.id

def get_fee_schedule(session, payer_id, file_info):
    """Ensures a plan exists and returns its ID."""
    fee_schedule = session.query(FeeSchedule).filter_by(
        payer_id=payer_id,
        source_file_url=file_info["location"]
    ).first()
    return fee_schedule.id

def process_fee_schedules(session, payer_id, data):
    try:
        # Use a set to track unique URLs (avoiding duplicate records)
        unique_files = set()

        # Extract in_network_files efficiently
        for structure in data.get("reporting_structure", []):
            for file_entry in structure.get("in_network_files", []):
                url = file_entry["location"]
                description = file_entry["description"]
                unique_files.add((url, description))

        # Check existing URLs in the database to avoid redundant inserts
        existing_urls = set(row[0] for row in session.query(FeeSchedule.source_file_url).filter(
            FeeSchedule.payer_id == payer_id
        ).all())
        
        # Insert only new URLs
        new_fee_schedules = [
            FeeSchedule(payer_id=payer_id, source_file_url=url, description=description)
            for url, description in unique_files if (url,) not in existing_urls
        ]

        if new_fee_schedules:
            session.bulk_save_objects(new_fee_schedules)
            session.commit()
            print(f"✅ Inserted {len(new_fee_schedules)} new fee schedule records.")
        else:
            print("✅ No new fee schedules to insert.")

    except Exception as e:
        session.rollback()
        raise(e)
        print(f"❌ Error processing file: {e}")

def process_plans(session, payer_id, data):
    try:
        # Use a set to track unique plan names (avoiding duplicate records)
        unique_plans = set()

        # Extract reporting plans efficiently
        for structure in data.get("reporting_structure", []):
            for plan_entry in structure.get("reporting_plans", []):
                name = plan_entry["plan_name"]
                category_id = plan_entry["plan_id"]
                category_id_type = plan_entry["plan_id_type"]
                plan_market_type = plan_entry["plan_market_type"]
                unique_plans.add((name, category_id, category_id_type, plan_market_type))

        # Check existing URLs in the database to avoid redundant inserts
        existing_plans = set(row[0] for row in session.query(Plan.name).filter(
            Plan.payer_id == payer_id
        ).all())

        # Insert only new URLs
        new_plans = [
            Plan(payer_id=payer_id, name=name, category_id=category_id, category_id_type=category_id_type, plan_market_type=plan_market_type)
            for name, category_id, category_id_type, plan_market_type in unique_plans if (name,) not in existing_plans
        ]

        if new_plans:
            session.bulk_save_objects(new_plans)
            session.commit()
            print(f"✅ Inserted {len(new_plans)} new plan records.")
        else:
            print("✅ No new plan records to insert.")

    except Exception as e:
        session.rollback()
        raise(e)
        print(f"❌ Error processing file: {e}")

def process_plan_fee_schedule_mappings(session, payer_id, data):
    try:
        # Use a set to track unique plan names (avoiding duplicate records)
        unique_mappings = set()

        # Extract mappings
        total_entries = len(data["reporting_structure"])
        i = 0
        for reporting_structure_entity in data["reporting_structure"]:
            print(f"✅ Processing entity {i}/{total_entries}...")
            i += 1
            # Each entity can have multiple reporting plans, process each one
            j = 1
            total_plans = len(reporting_structure_entity["reporting_plans"])

            # Just skipping this for now, will piece through it later
            if total_plans > 10:
                continue

            for plan_data in reporting_structure_entity["reporting_plans"]:
                print(f"🔄 Processing plan {j}/{total_plans}...")
                j += 1
                plan_id = get_plan(session, payer_id, plan_data)
                for file_info in reporting_structure_entity.get("in_network_files", []):
                    fee_schedule_id = get_fee_schedule(session, payer_id, file_info)
                    unique_mappings.add((plan_id, fee_schedule_id))

                #TODO: Process allowed amount files

        #TODO: Check existing mappings
        # Check existing URLs in the database to avoid redundant inserts
        #existing_mappings = set(session.query(PlanFeeSchedule.plan_id, PlanFeeSchedule.fee_schedule_id).all())
        # Insert only new URLs
        new_mappings = [
            PlanFeeSchedule(plan_id=plan_id, fee_schedule_id=fee_schedule_id)
            for plan_id, fee_schedule_id in unique_mappings
        ]

        if new_mappings:
            session.bulk_save_objects(new_mappings)
            session.commit()
            print(f"✅ Inserted {len(new_mappings)} new plan <> fee schedule mapping records.")
        else:
            print("✅ No new plan <> fee schedule mapping records to insert.")

    except Exception as e:
        session.rollback()
        raise(e)
        print(f"❌ Error processing file: {e}")

def process_json_index():
    """Downloads and reads index file, updates list of fee schedules, updates list of plans, maps plans to fee schedules."""
    session = SessionLocal()
    
    try:
        # Create or retrieve the payer entity
        payer = get_payer(session, payer_id=BCBS_IL_ID)
        payer_id = payer.id
        payer_index_file_url = payer.mrf_index_file_url
        index_filepath = os.path.join(FILES_DIR, f"BCBS IL Index.json {datetime.datetime.now().strftime('%m-%d-%Y')}")

        # Download the file and load the data from json
        response = requests.get(payer_index_file_url, stream=True)
        with open(index_filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        index_data = load_json(index_filepath)

        # Update list of fee schedules
        print(f"🔄 Creating fee schedules...")
        process_fee_schedules(session, payer_id, index_data)

        # Update list of plans
        print(f"🔄 Creating plan records...")
        process_plans(session, payer_id, index_data)

        # Update list of plan <> fee_schedule mappings
        print(f"🔄 Creating plan <> fee schedule mapping records...")
        process_plan_fee_schedule_mappings(session, payer_id, index_data)

        print("✅ Metadata stored successfully.")

    except Exception as e:
        session.rollback()
        raise(e)
        print(f"❌ Error: {e}")
    
    finally:
        session.close()

if __name__ == "__main__":
    
    process_json_index()
