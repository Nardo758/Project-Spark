#!/usr/bin/env python3
"""
Florida DOT AADT Traffic Data Import Script

Downloads Annual Average Daily Traffic (AADT) data from Florida DOT's
ArcGIS RCI_Layers FeatureServer and imports it into the local PostgreSQL database.

Florida DOT RCI Layers AADT API:
https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/0/query
"""

import os
import sys
import json
import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.database import get_db, engine
from app.models.traffic_road import TrafficRoad

FLORIDA_DOT_API = "https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/0/query"

BATCH_SIZE = 1000
MAX_RECORDS_PER_REQUEST = 1000

def fetch_record_count() -> int:
    """Get total number of records available."""
    params = {
        "where": "1=1",
        "returnCountOnly": "true",
        "f": "json"
    }
    response = requests.get(FLORIDA_DOT_API, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("count", 0)


def fetch_records(offset: int = 0, limit: int = MAX_RECORDS_PER_REQUEST) -> Dict[str, Any]:
    """Fetch a batch of records from Florida DOT API."""
    params = {
        "where": "1=1",
        "outFields": "*",
        "f": "geojson",
        "resultOffset": offset,
        "resultRecordCount": limit,
        "outSR": "4326"
    }
    
    response = requests.get(FLORIDA_DOT_API, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def parse_feature(feature: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse a GeoJSON feature into database fields."""
    props = feature.get("properties", {})
    geometry = feature.get("geometry", {})
    
    geom_type = geometry.get("type")
    if geom_type == "MultiLineString":
        all_coords = geometry.get("coordinates", [[]])
        if not all_coords or not all_coords[0]:
            return None
        coords = all_coords[0]
    elif geom_type == "LineString":
        coords = geometry.get("coordinates", [])
    else:
        return None
    
    if len(coords) < 2:
        return None
    
    aadt = props.get("AADT")
    if not aadt or aadt <= 0:
        return None
    
    wkt_coords = ", ".join([f"{c[0]} {c[1]}" for c in coords])
    wkt_geometry = f"SRID=4326;LINESTRING({wkt_coords})"
    
    return {
        "state": "FL",
        "county": props.get("COUNTY"),
        "district": str(props.get("DISTRICT")) if props.get("DISTRICT") else None,
        "roadway_id": props.get("ROADWAY"),
        "road_name": props.get("COSITE"),
        "description_from": props.get("DESC_FRM"),
        "description_to": props.get("DESC_TO"),
        "aadt": int(aadt),
        "year": int(props.get("YEAR_", 2024)),
        "k_factor": props.get("KFCTR"),
        "d_factor": props.get("DFCTR"),
        "t_factor": props.get("TFCTR"),
        "geometry_wkt": wkt_geometry,
        "begin_post": props.get("BEGIN_POST"),
        "end_post": props.get("END_POST"),
        "shape_length": props.get("Shape__Length"),
        "raw_attributes": props
    }


def insert_batch(db: Session, records: List[Dict[str, Any]]) -> int:
    """Insert a batch of records into the database."""
    if not records:
        return 0
    
    insert_sql = text("""
        INSERT INTO traffic_roads 
        (state, county, district, roadway_id, road_name, description_from, description_to,
         aadt, year, k_factor, d_factor, t_factor, geometry, begin_post, end_post, 
         shape_length, raw_attributes)
        VALUES 
        (:state, :county, :district, :roadway_id, :road_name, :description_from, :description_to,
         :aadt, :year, :k_factor, :d_factor, :t_factor, ST_GeomFromEWKT(:geometry_wkt), :begin_post, :end_post,
         :shape_length, CAST(:raw_attributes AS jsonb))
    """)
    
    inserted = 0
    for record in records:
        try:
            params = {**record}
            params["raw_attributes"] = json.dumps(params.get("raw_attributes", {}))
            db.execute(insert_sql, params)
            inserted += 1
        except Exception as e:
            print(f"  Warning: Failed to insert record: {e}")
    
    db.commit()
    return inserted


def clear_florida_data(db: Session):
    """Clear existing Florida data."""
    db.execute(text("DELETE FROM traffic_roads WHERE state = 'FL'"))
    db.commit()
    print("Cleared existing Florida data")


def import_florida_data(clear_existing: bool = True):
    """Main import function."""
    print("=" * 60)
    print("Florida DOT AADT Traffic Data Import")
    print("=" * 60)
    print(f"API: {FLORIDA_DOT_API}")
    print(f"Started: {datetime.now().isoformat()}")
    print()
    
    total_count = fetch_record_count()
    print(f"Total records available: {total_count:,}")
    
    db = next(get_db())
    
    try:
        if clear_existing:
            clear_florida_data(db)
        
        offset = 0
        total_imported = 0
        total_skipped = 0
        batch_num = 0
        
        while offset < total_count:
            batch_num += 1
            print(f"\nBatch {batch_num}: Fetching records {offset:,} - {offset + MAX_RECORDS_PER_REQUEST:,}...")
            
            try:
                data = fetch_records(offset=offset, limit=MAX_RECORDS_PER_REQUEST)
            except requests.RequestException as e:
                print(f"  Error fetching batch: {e}")
                print("  Retrying in 5 seconds...")
                time.sleep(5)
                continue
            
            features = data.get("features", [])
            print(f"  Received {len(features)} features")
            
            if not features:
                break
            
            records = []
            for feature in features:
                parsed = parse_feature(feature)
                if parsed:
                    records.append(parsed)
                else:
                    total_skipped += 1
            
            inserted = insert_batch(db, records)
            total_imported += inserted
            
            print(f"  Imported: {inserted}, Total: {total_imported:,}")
            
            offset += len(features)
            time.sleep(0.5)
        
        print()
        print("=" * 60)
        print(f"Import Complete!")
        print(f"Total imported: {total_imported:,}")
        print(f"Total skipped: {total_skipped:,}")
        print(f"Finished: {datetime.now().isoformat()}")
        print("=" * 60)
        
        return total_imported
        
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Import Florida DOT traffic data")
    parser.add_argument("--no-clear", action="store_true", help="Don't clear existing data")
    args = parser.parse_args()
    
    import_florida_data(clear_existing=not args.no_clear)
