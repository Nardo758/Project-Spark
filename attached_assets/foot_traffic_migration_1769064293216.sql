-- OppGrid Foot Traffic Database Migration
-- Run this to create all necessary tables and indexes

-- Enable PostGIS extension for geographic data
CREATE EXTENSION IF NOT EXISTS postgis;

-- ==============================================
-- FOOT TRAFFIC DATA TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS foot_traffic (
    id SERIAL PRIMARY KEY,
    place_id VARCHAR(255) NOT NULL,
    place_name VARCHAR(500) NOT NULL,
    place_address TEXT,
    place_type VARCHAR(100),
    
    -- Geographic data
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    
    -- Traffic data (JSON structure for flexibility)
    popular_times JSONB,
    current_popularity INTEGER,
    time_spent_min INTEGER,
    time_spent_max INTEGER,
    
    -- Metadata
    data_source VARCHAR(50) DEFAULT 'google_maps',
    data_quality_score DECIMAL(3, 2),
    collected_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    
    -- Ensure unique place_id
    UNIQUE(place_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_foot_traffic_location 
    ON foot_traffic USING GIST(location);

CREATE INDEX IF NOT EXISTS idx_foot_traffic_place_id 
    ON foot_traffic(place_id);

CREATE INDEX IF NOT EXISTS idx_foot_traffic_place_type 
    ON foot_traffic(place_type);

CREATE INDEX IF NOT EXISTS idx_foot_traffic_updated 
    ON foot_traffic(last_updated);

-- Add helpful comment
COMMENT ON COLUMN foot_traffic.popular_times IS 
'JSON object with day names as keys and arrays of 24 hourly traffic values (0-100). 
Example: {"Monday": [0, 0, 0, 0, 0, 0, 12, 25, 45, 67, 78, 85, 80, 75, 60, 45, 50, 65, 70, 55, 40, 20, 10, 5], "Tuesday": [...], ...}';

-- ==============================================
-- AREA TRAFFIC AGGREGATIONS TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS area_traffic_aggregations (
    id SERIAL PRIMARY KEY,
    area_name VARCHAR(255),
    center_latitude DECIMAL(10, 8) NOT NULL,
    center_longitude DECIMAL(11, 8) NOT NULL,
    center_location GEOGRAPHY(POINT, 4326),
    radius_meters INTEGER NOT NULL DEFAULT 800,
    
    -- Aggregated traffic data
    avg_popular_times JSONB,
    total_locations_sampled INTEGER,
    dominant_place_types JSONB,
    
    -- Peak patterns
    peak_day VARCHAR(20),
    peak_hour INTEGER,
    peak_traffic_score INTEGER,
    
    -- Area vitality metrics
    area_vitality_score DECIMAL(5, 2),
    business_density_score DECIMAL(5, 2),
    foot_traffic_consistency DECIMAL(5, 2),
    
    -- Metadata
    computed_at TIMESTAMP DEFAULT NOW(),
    last_refreshed TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_area_traffic_location 
    ON area_traffic_aggregations USING GIST(center_location);

CREATE INDEX IF NOT EXISTS idx_area_traffic_vitality 
    ON area_traffic_aggregations(area_vitality_score DESC);

-- ==============================================
-- OPPORTUNITY FOOT TRAFFIC LINK TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS opportunity_foot_traffic (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER REFERENCES opportunities(id) ON DELETE CASCADE,
    
    -- Traffic context for this opportunity
    area_traffic_score DECIMAL(5, 2),
    nearby_traffic_places INTEGER,
    peak_demand_alignment BOOLEAN,
    
    -- Geographic radius analyzed
    analysis_radius_meters INTEGER DEFAULT 800,
    
    -- Traffic insights (AI generated summary)
    traffic_insights TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure one record per opportunity
    UNIQUE(opportunity_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_opp_foot_traffic_score 
    ON opportunity_foot_traffic(area_traffic_score DESC);

CREATE INDEX IF NOT EXISTS idx_opp_foot_traffic_opp_id 
    ON opportunity_foot_traffic(opportunity_id);

-- ==============================================
-- HELPER FUNCTION: Calculate Distance
-- ==============================================
CREATE OR REPLACE FUNCTION calculate_distance_meters(
    lat1 DECIMAL, lng1 DECIMAL,
    lat2 DECIMAL, lng2 DECIMAL
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN ST_Distance(
        ST_MakePoint(lng1, lat1)::geography,
        ST_MakePoint(lng2, lat2)::geography
    );
END;
$$ LANGUAGE plpgsql;

-- ==============================================
-- VERIFICATION QUERIES
-- ==============================================

-- Verify tables created
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns 
     WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN ('foot_traffic', 'area_traffic_aggregations', 'opportunity_foot_traffic')
ORDER BY table_name;

-- Verify indexes created
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE tablename IN ('foot_traffic', 'area_traffic_aggregations', 'opportunity_foot_traffic')
ORDER BY tablename, indexname;

COMMIT;
