#!/usr/bin/env python3
"""
OppGrid Foot Traffic System - Quick Test Script

This script tests the foot traffic system with a known high-traffic location.
Perfect for validating your setup before integrating with OppGrid.

Usage:
    python test_foot_traffic_system.py
"""

import os
import sys
import json
import psycopg2
from datetime import datetime

# Add utils to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.foot_traffic_collector import FootTrafficCollector
from utils.traffic_analyzer import TrafficAnalyzer


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def check_environment():
    """Verify environment variables are set"""
    print_section("1. Checking Environment")
    
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    db_url = os.getenv('DATABASE_URL')
    
    if not api_key:
        print("❌ GOOGLE_MAPS_API_KEY not set!")
        print("   Set it in Replit Secrets or .env file")
        return False
    
    if not db_url:
        print("❌ DATABASE_URL not set!")
        print("   Set it in Replit Secrets or .env file")
        return False
    
    print("✅ GOOGLE_MAPS_API_KEY is set")
    print("✅ DATABASE_URL is set")
    return True


def check_database():
    """Verify database tables exist"""
    print_section("2. Checking Database")
    
    try:
        db_conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = db_conn.cursor()
        
        # Check for required tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('foot_traffic', 'area_traffic_aggregations', 'opportunity_foot_traffic')
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['foot_traffic', 'area_traffic_aggregations', 'opportunity_foot_traffic']
        
        for table in required_tables:
            if table in tables:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing!")
                print(f"   Run: psql $DATABASE_URL -f migrations/foot_traffic_migration.sql")
                cursor.close()
                db_conn.close()
                return False
        
        cursor.close()
        db_conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False


def test_collector():
    """Test the foot traffic collector"""
    print_section("3. Testing Foot Traffic Collector")
    
    try:
        db_conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        collector = FootTrafficCollector(
            os.getenv('GOOGLE_MAPS_API_KEY'),
            db_conn
        )
        
        # Test with a known high-traffic location (Times Square, NYC)
        print("📍 Test Location: Times Square, NYC")
        print("   Latitude: 40.7589")
        print("   Longitude: -73.9851")
        print("   Radius: 300 meters (~1000 feet)")
        print("\n⏳ Collecting data... (this takes 30-60 seconds)")
        
        traffic_data = collector.get_area_traffic(
            latitude=40.7589,
            longitude=-73.9851,
            radius_meters=300
        )
        
        if not traffic_data:
            print("❌ No traffic data collected")
            print("   This could mean:")
            print("   - API key doesn't have Places API enabled")
            print("   - Rate limiting is active")
            print("   - Network connectivity issue")
            db_conn.close()
            return False
        
        print(f"\n✅ Collected traffic data for {len(traffic_data)} locations")
        
        # Show sample data
        if len(traffic_data) > 0:
            sample = traffic_data[0]
            print(f"\n📊 Sample Location:")
            print(f"   Name: {sample['place_name']}")
            print(f"   Type: {sample['place_type']}")
            print(f"   Quality Score: {sample['data_quality_score']}/1.0")
            
            if sample.get('popular_times'):
                monday_traffic = sample['popular_times'].get('Monday', [])
                if monday_traffic:
                    avg_traffic = sum(monday_traffic) / len(monday_traffic)
                    print(f"   Avg Monday Traffic: {avg_traffic:.0f}/100")
        
        # Save to database
        print("\n💾 Saving to database...")
        saved_count = collector.save_traffic_data(traffic_data)
        print(f"✅ Saved {saved_count} records")
        
        db_conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Collector test failed: {str(e)}")
        return False


def test_analyzer():
    """Test the traffic analyzer"""
    print_section("4. Testing Traffic Analyzer")
    
    try:
        db_conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        analyzer = TrafficAnalyzer(db_conn)
        
        print("📊 Analyzing area traffic for Times Square...")
        
        analysis = analyzer.analyze_area_traffic(
            latitude=40.7589,
            longitude=-73.9851,
            radius_meters=300
        )
        
        if analysis.get('total_locations_sampled', 0) == 0:
            print("❌ No locations available for analysis")
            print("   Run the collector test first to populate data")
            db_conn.close()
            return False
        
        print(f"\n✅ Analysis Complete")
        print(f"\n📈 Results:")
        print(f"   Locations Sampled: {analysis['total_locations_sampled']}")
        print(f"   Area Vitality Score: {analysis['area_vitality_score']}/100")
        print(f"   Business Density: {analysis['business_density_score']}/100")
        print(f"   Traffic Consistency: {analysis['traffic_consistency']}/100")
        
        if analysis.get('peak_day') and analysis.get('peak_hour') is not None:
            hour_12 = analysis['peak_hour'] % 12 or 12
            ampm = "AM" if analysis['peak_hour'] < 12 else "PM"
            print(f"\n🎯 Peak Traffic:")
            print(f"   Day: {analysis['peak_day']}")
            print(f"   Time: {hour_12}:00 {ampm}")
            print(f"   Traffic Level: {analysis['peak_traffic_score']}/100")
        
        if analysis.get('dominant_place_types'):
            print(f"\n🏪 Dominant Business Types:")
            for place_type, count in list(analysis['dominant_place_types'].items())[:3]:
                print(f"   - {place_type}: {count} locations")
        
        db_conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Analyzer test failed: {str(e)}")
        return False


def print_summary(results):
    """Print test summary"""
    print_section("Test Summary")
    
    all_passed = all(results.values())
    
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test}")
    
    print()
    
    if all_passed:
        print("🎉 All tests passed! Your foot traffic system is ready.")
        print("\nNext steps:")
        print("1. Integrate with OppGrid API endpoints")
        print("2. Add frontend components to display traffic data")
        print("3. Start collecting traffic for your opportunities")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Ensure all environment variables are set")
        print("- Run the database migration script")
        print("- Enable Places API in Google Cloud Console")
    
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  OppGrid Foot Traffic System - Test Suite")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    results = {}
    
    # Test 1: Environment
    results['Environment Check'] = check_environment()
    if not results['Environment Check']:
        print_summary(results)
        return
    
    # Test 2: Database
    results['Database Check'] = check_database()
    if not results['Database Check']:
        print_summary(results)
        return
    
    # Test 3: Collector
    results['Data Collection'] = test_collector()
    
    # Test 4: Analyzer
    results['Data Analysis'] = test_analyzer()
    
    # Summary
    print_summary(results)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
