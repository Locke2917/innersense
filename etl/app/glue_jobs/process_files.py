import json
import sys
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from ..models import (
    Provider, ProviderGroup, ProviderGroupMember,
    FeeSchedule, ServiceLine, NegotiatedRate,
    NegotiatedRateProviderGroup
)
from ..helpers import download_and_extract


# Database Connection (Change to your actual DB connection string)
DATABASE_URL = "postgresql://postgres:Smartchoice1!@localhost/innersense"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def process_json(fee_schedule_id):
    session = Session()
    try:
        # Load the JSON file
        fee_schedule = session.get(FeeSchedule, fee_schedule_id)
        payer_id = fee_schedule.payer_id
        file_path, filesize = download_and_extract(fee_schedule.source_file_url, "files")
        print(file_path)

        with open(file_path, "r") as file:
            data = json.load(file)

        # Process Provider Groups
        print(f"🔄 Creating provider groups...")
        i = 0
        total_provider_groups = len(data.get("provider_references", []))
        provider_groups = {}
        for entry in data.get("provider_references", []):
            print(f"🔄 Processing provider group {i}/{total_provider_groups}...")
            i += 1
            provider_group_id = str(entry["provider_group_id"])
            tin_value = entry["provider_groups"][0]["tin"]["value"]

            provider_group = ProviderGroup(
                payer_id=payer_id,
                payer_assigned_id=provider_group_id,
                ein=tin_value
            )
            session.add(provider_group)
            session.commit()  # Get provider_group.id
            provider_groups[provider_group_id] = provider_group.id

            # Add provider group members (NPIs)
            for npi in entry["provider_groups"][0]["npi"]:
                provider = session.execute(select(Provider).where(Provider.npi == str(npi))).scalar()
                if not provider:
                    provider = Provider(npi=str(npi))
                    session.add(provider)
                    session.commit()

                session.add(ProviderGroupMember(provider_group_id=provider_group.id, provider_id=provider.id))

        total_in_network = len(data.get("in_network"))
        print(f"🔄 Processing {total_in_network} in-network services...")
        i = 0
        # Process Service Lines and Negotiated Rates
        for service in data.get("in_network", []):
            print(f"🔄 Processing service {i}/{total_in_network}...")
            i += 1
            billing_code = service["billing_code"]
            billing_code_type = service["billing_code_type"]
            billing_code_version = service["billing_code_type_version"]

            service_line = session.execute(select(ServiceLine).where(
                (ServiceLine.billing_code == billing_code) &
                (ServiceLine.billing_code_type == billing_code_type) &
                (ServiceLine.billing_code_type_version == billing_code_version)
            )).scalar()

            if not service_line:
                service_line = ServiceLine(
                    billing_code=billing_code,
                    billing_code_type=billing_code_type,
                    billing_code_type_version=billing_code_version
                )
                session.add(service_line)
                session.commit()

            # Process Negotiated Rates
            for rate_entry in service["negotiated_rates"]:
                for price in rate_entry["negotiated_prices"]:
                    negotiated_rate = NegotiatedRate(
                        payer_id=payer_id,
                        fee_schedule_id=fee_schedule.id,
                        service_line_id=service_line.id,
                        negotiation_arrangement=service["negotiation_arrangement"],
                        negotiated_type=price["negotiated_type"],
                        negotiated_rate=price["negotiated_rate"],
                        expiration_date=price.get("expiration_date"),
                        billing_class=price["billing_class"],
                        service_codes=price.get("service_code", None)  # Store as an array if present
                    )
                    session.add(negotiated_rate)
                    session.commit()  # Get negotiated_rate.id

                    # Link Negotiated Rates to Provider Groups
                    for provider_group_ref in rate_entry["provider_references"]:
                        provider_group_internal_id = provider_groups.get(str(provider_group_ref))
                        if provider_group_internal_id:
                            session.add(NegotiatedRateProviderGroup(
                                negotiated_rate_id=negotiated_rate.id,
                                provider_group_id=provider_group_internal_id
                            ))

        session.commit()
        print("✅ File processed successfully.")

    except Exception as e:
        session.rollback()
        print(f"❌ Error processing file: {e}")

    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_files.py <fee_schedule_id>")
        sys.exit(1)

    fee_schedule_id = int(sys.argv[1])

    process_json(fee_schedule_id)
