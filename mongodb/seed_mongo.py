"""
Fleet Command - MongoDB Setup Script
=====================================
Creates all collections with validators and indexes,
then loads seed data from mongodb_seed_data.json.

Usage:
    pip install pymongo
    python seed_mongo.py

    # Or with Atlas URI:
    MONGO_URI="mongodb+srv://..." python seed_mongo.py
"""

import os
import json
import sys
from datetime import datetime

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from pymongo.errors import CollectionInvalid, OperationFailure
except ImportError:
    print("[ERROR] pymongo not installed. Run: pip install pymongo")
    sys.exit(1)

# ── Config ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "mongodb_config.json")
SCHEMA_FILE = os.path.join(SCRIPT_DIR, "mongodb_schemas.json")
SEED_FILE   = os.path.join(SCRIPT_DIR, "mongodb_seed_data.json")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_client(config):
    uri = os.environ.get("MONGO_URI", config["connection"]["uri"])
    opts = config["connection"]["options"].copy()
    # Remove non-pymongo keys
    opts.pop("retryWrites", None)
    opts.pop("w", None)
    return MongoClient(uri, **{
        "serverSelectionTimeoutMS": opts["serverSelectionTimeoutMS"],
        "connectTimeoutMS": opts["connectTimeoutMS"],
        "maxPoolSize": opts["maxPoolSize"],
    })

# ── Collection creation ────────────────────────────────────────────────────────
def create_collections(db, schemas):
    created, skipped = 0, 0
    for coll_name, coll_def in schemas["collections"].items():
        validator = coll_def.get("validator")
        try:
            if validator:
                db.create_collection(coll_name, validator=validator)
            else:
                db.create_collection(coll_name)
            print(f"  [+] Created collection: {coll_name}")
            created += 1
        except CollectionInvalid:
            print(f"  [~] Already exists:     {coll_name}")
            skipped += 1

    return created, skipped

# ── Index creation ─────────────────────────────────────────────────────────────
def create_indexes(db, schemas):
    total = 0
    for coll_name, coll_def in schemas["collections"].items():
        indexes = coll_def.get("indexes", [])
        if not indexes:
            continue
        coll = db[coll_name]
        for idx in indexes:
            key_pairs = [
                (field, ASCENDING if direction == 1 else DESCENDING)
                for field, direction in idx["key"].items()
            ]
            kwargs = {}
            if idx.get("unique"):
                kwargs["unique"] = True
            if idx.get("sparse"):
                kwargs["sparse"] = True
            try:
                coll.create_index(key_pairs, **kwargs)
                total += 1
            except OperationFailure as e:
                print(f"  [!] Index error on {coll_name}: {e}")
    print(f"  [+] Created {total} indexes")

# ── Seed data loading ──────────────────────────────────────────────────────────
def load_seed_data(db, seed):
    total_inserted = 0
    for coll_name, documents in seed.items():
        if coll_name.startswith("_"):
            continue  # skip _meta
        if not isinstance(documents, list) or not documents:
            continue

        coll = db[coll_name]
        # Drop existing seed data
        coll.delete_many({})

        # Use _id if present, otherwise let MongoDB auto-assign
        try:
            result = coll.insert_many(documents, ordered=False)
            count = len(result.inserted_ids)
            total_inserted += count
            print(f"  [+] {coll_name}: {count} documents inserted")
        except Exception as e:
            print(f"  [!] Error inserting into {coll_name}: {e}")

    return total_inserted

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("\nFleet Command — MongoDB Setup")
    print("=" * 45)

    # Load files
    config  = load_json(CONFIG_FILE)
    schemas = load_json(SCHEMA_FILE)
    seed    = load_json(SEED_FILE)

    db_name = config["connection"]["database"]

    # Connect
    print(f"\n[1] Connecting to MongoDB...")
    try:
        client = get_client(config)
        client.admin.command("ping")
        print(f"  [OK] Connected. Database: {db_name}")
    except Exception as e:
        print(f"  [ERROR] Cannot connect: {e}")
        print("\n  Make sure MongoDB is running:")
        print("  - Local:  mongod --dbpath /data/db")
        print("  - Atlas:  set MONGO_URI env variable")
        sys.exit(1)

    db = client[db_name]

    # Create collections
    print(f"\n[2] Creating collections...")
    created, skipped = create_collections(db, schemas)
    print(f"  Created: {created}, Already existed: {skipped}")

    # Create indexes
    print(f"\n[3] Creating indexes...")
    create_indexes(db, schemas)

    # Load seed data
    print(f"\n[4] Loading seed data...")
    total = load_seed_data(db, seed)
    print(f"  Total documents inserted: {total}")

    # Summary
    print(f"\n{'='*45}")
    print(f"  Setup complete for database: {db_name}")
    print(f"  Collections: {len(db.list_collection_names())}")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*45}\n")

    client.close()

if __name__ == "__main__":
    main()
