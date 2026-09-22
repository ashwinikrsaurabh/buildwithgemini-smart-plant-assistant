# Copyright 2026 Google LLC
# Seed script for Smart Plant & Greenhouse Assistant Firestore collection

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-02-bac4296bfb63"
COLLECTION_NAME = "plants"

SEED_PLANTS = [
    {
        "id": "monstera-deliciosa",
        "name": "Monstera Deliciosa",
        "species": "Monstera deliciosa",
        "water_frequency_days": 7,
        "sunlight": "Bright indirect light",
        "care_notes": "Prefers well-draining potting soil. Wipe leaves regularly with damp cloth.",
        "stock_count": 15,
        "status": "Healthy",
        "last_watered": "2026-09-18",
    },
    {
        "id": "golden-pothos",
        "name": "Golden Pothos",
        "species": "Epipremnum aureum",
        "water_frequency_days": 10,
        "sunlight": "Low to bright indirect light",
        "care_notes": "Hardy trailer. Let top 2 inches of soil dry out between waterings.",
        "stock_count": 25,
        "status": "Healthy",
        "last_watered": "2026-09-15",
    },
    {
        "id": "peace-lily",
        "name": "Peace Lily",
        "species": "Spathiphyllum",
        "water_frequency_days": 5,
        "sunlight": "Medium to low indirect light",
        "care_notes": "Sensitive to tap water chemicals. Keep soil consistently moist.",
        "stock_count": 8,
        "status": "Needs Attention",
        "last_watered": "2026-09-20",
    },
    {
        "id": "fiddle-leaf-fig",
        "name": "Fiddle Leaf Fig",
        "species": "Ficus lyrata",
        "water_frequency_days": 8,
        "sunlight": "Bright direct to indirect light",
        "care_notes": "Avoid moving frequently; sensitive to cold drafts and changes in humidity.",
        "stock_count": 5,
        "status": "Healthy",
        "last_watered": "2026-09-19",
    },
]


def seed_firestore():
    """Seeds initial plant inventory items into Firestore."""
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    print(f"Seeding Firestore collection '{COLLECTION_NAME}' in project '{PROJECT_ID}'...")
    for plant in SEED_PLANTS:
        plant_id = plant["id"]
        doc_ref = collection_ref.document(plant_id)
        doc_ref.set(plant)
        print(f"  - Seeded plant: {plant_id} ({plant['name']})")

    print("Firestore seeding completed successfully!")


if __name__ == "__main__":
    seed_firestore()
