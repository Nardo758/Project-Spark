"""
OppGrid Foot Traffic Analyzer
Aggregates and analyzes foot traffic patterns for areas and opportunities

Usage:
    from app.services.traffic_analyzer import TrafficAnalyzer
    
    analyzer = TrafficAnalyzer(db_session)
    analysis = analyzer.analyze_area_traffic(lat, lng, radius_meters=800)
    analyzer.link_opportunity_traffic(opp_id, lat, lng)
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import statistics
import logging

logger = logging.getLogger(__name__)


class TrafficAnalyzer:
    """
    Analyzes foot traffic patterns and generates insights
    """
    
    def __init__(self, db: Session):
        """
        Initialize analyzer with database session
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        logger.info("TrafficAnalyzer initialized")
    
    def analyze_area_traffic(self, latitude: float, longitude: float,
                            radius_meters: int = 800) -> Dict:
        """
        Aggregate and analyze foot traffic for an area
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_meters: Analysis radius
            
        Returns:
            Dictionary with aggregated traffic analysis
        """
        try:
            query = text("""
            SELECT 
                place_id, place_name, place_type,
                latitude, longitude,
                popular_times, current_popularity,
                time_spent_min, time_spent_max,
                data_quality_score
            FROM foot_traffic
            WHERE ST_DWithin(
                location,
                ST_MakePoint(:lng, :lat)::geography,
                :radius
            )
            AND popular_times IS NOT NULL
            ORDER BY data_quality_score DESC
            """)
            
            results = self.db.execute(query, {
                'lat': latitude,
                'lng': longitude,
                'radius': radius_meters
            }).fetchall()
            
            if not results:
                logger.info(f"No traffic data found for area ({latitude}, {longitude})")
                return self._empty_analysis(latitude, longitude, radius_meters)
            
            logger.info(f"Found {len(results)} locations with traffic data")
            
            all_traffic_patterns = []
            place_types_count = {}
            total_current_popularity = []
            
            for row in results:
                place_id, place_name, place_type, lat, lng, popular_times, \
                current_pop, time_min, time_max, quality = row
                
                if popular_times:
                    if isinstance(popular_times, str):
                        popular_times = json.loads(popular_times)
                    all_traffic_patterns.append(popular_times)
                
                if place_type:
                    place_types_count[place_type] = place_types_count.get(place_type, 0) + 1
                
                if current_pop is not None:
                    total_current_popularity.append(current_pop)
            
            avg_popular_times = self._average_traffic_patterns(all_traffic_patterns)
            peak_day, peak_hour, peak_value = self._find_peak_traffic(avg_popular_times)
            
            vitality_score = self._calculate_vitality_score(
                len(results),
                avg_popular_times,
                place_types_count,
                total_current_popularity
            )
            
            dominant_types = sorted(
                place_types_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            analysis = {
                'center_latitude': latitude,
                'center_longitude': longitude,
                'radius_meters': radius_meters,
                'total_locations_sampled': len(results),
                'avg_popular_times': avg_popular_times,
                'peak_day': peak_day,
                'peak_hour': peak_hour,
                'peak_traffic_score': peak_value,
                'current_avg_popularity': statistics.mean(total_current_popularity) if total_current_popularity else None,
                'area_vitality_score': vitality_score,
                'business_density_score': self._calculate_business_density(len(results), radius_meters),
                'traffic_consistency': self._calculate_consistency(all_traffic_patterns),
                'dominant_place_types': dict(dominant_types),
                'generated_at': datetime.now().isoformat()
            }
            
            self._save_area_aggregation(analysis)
            
            logger.info(f"Analysis complete: Vitality score {vitality_score}/100")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing area traffic: {str(e)}")
            return self._empty_analysis(latitude, longitude, radius_meters)
    
    def link_opportunity_traffic(self, opportunity_id: int,
                                 opportunity_lat: float, opportunity_lng: float,
                                 radius_meters: int = 800) -> Optional[Dict]:
        """
        Link an opportunity to surrounding foot traffic data
        
        Args:
            opportunity_id: OppGrid opportunity ID
            opportunity_lat: Opportunity latitude
            opportunity_lng: Opportunity longitude
            radius_meters: Analysis radius
            
        Returns:
            Traffic insights for this opportunity or None
        """
        logger.info(f"Linking traffic data to opportunity {opportunity_id}")
        
        area_analysis = self.analyze_area_traffic(
            opportunity_lat, opportunity_lng, radius_meters
        )
        
        if not area_analysis or area_analysis['total_locations_sampled'] == 0:
            logger.warning(f"No traffic data available for opportunity {opportunity_id}")
            return None
        
        insights = self._generate_traffic_insights(area_analysis)
        
        try:
            query = text("""
            INSERT INTO opportunity_foot_traffic (
                opportunity_id, area_traffic_score, nearby_traffic_places,
                peak_demand_alignment, analysis_radius_meters,
                traffic_insights, updated_at
            )
            VALUES (:opp_id, :score, :places, :peak_align, :radius, :insights, NOW())
            ON CONFLICT (opportunity_id) DO UPDATE SET
                area_traffic_score = EXCLUDED.area_traffic_score,
                nearby_traffic_places = EXCLUDED.nearby_traffic_places,
                peak_demand_alignment = EXCLUDED.peak_demand_alignment,
                traffic_insights = EXCLUDED.traffic_insights,
                updated_at = NOW()
            """)
            
            self.db.execute(query, {
                'opp_id': opportunity_id,
                'score': area_analysis['area_vitality_score'],
                'places': area_analysis['total_locations_sampled'],
                'peak_align': area_analysis['peak_traffic_score'] > 70 if area_analysis['peak_traffic_score'] else False,
                'radius': radius_meters,
                'insights': insights
            })
            
            self.db.commit()
            
            logger.info(f"Successfully linked traffic data to opportunity {opportunity_id}")
            
            return {
                'opportunity_id': opportunity_id,
                'traffic_score': area_analysis['area_vitality_score'],
                'insights': insights,
                'detailed_analysis': area_analysis
            }
            
        except Exception as e:
            logger.error(f"Error linking traffic to opportunity {opportunity_id}: {str(e)}")
            return None
    
    def get_opportunity_traffic(self, opportunity_id: int) -> Optional[Dict]:
        """
        Get cached traffic analysis for an opportunity
        """
        try:
            query = text("""
            SELECT 
                area_traffic_score, nearby_traffic_places,
                peak_demand_alignment, traffic_insights,
                analysis_radius_meters, updated_at
            FROM opportunity_foot_traffic
            WHERE opportunity_id = :opp_id
            """)
            
            result = self.db.execute(query, {'opp_id': opportunity_id}).fetchone()
            
            if not result:
                return None
            
            score, places, peak_align, insights, radius, updated = result
            
            return {
                'opportunity_id': opportunity_id,
                'area_traffic_score': float(score) if score else None,
                'nearby_traffic_places': places,
                'peak_demand_alignment': peak_align,
                'insights': insights,
                'analysis_radius_meters': radius,
                'last_updated': updated.isoformat() if updated else None
            }
            
        except Exception as e:
            logger.error(f"Error fetching opportunity traffic: {str(e)}")
            return None
    
    def get_heatmap_data(self, latitude: float, longitude: float,
                         radius_meters: int = 1000) -> List[Dict]:
        """
        Get foot traffic data formatted for heatmap visualization
        """
        try:
            query = text("""
            SELECT 
                place_id, place_name, place_type,
                latitude, longitude,
                popular_times, current_popularity,
                data_quality_score
            FROM foot_traffic
            WHERE ST_DWithin(
                location,
                ST_MakePoint(:lng, :lat)::geography,
                :radius
            )
            ORDER BY data_quality_score DESC
            """)
            
            results = self.db.execute(query, {
                'lat': latitude,
                'lng': longitude,
                'radius': radius_meters
            }).fetchall()
            
            heatmap_points = []
            for row in results:
                place_id, name, ptype, lat, lng, popular_times, current_pop, quality = row
                
                avg_traffic = 50
                if popular_times:
                    if isinstance(popular_times, str):
                        popular_times = json.loads(popular_times)
                    all_values = []
                    for day_data in popular_times.values():
                        if isinstance(day_data, list):
                            all_values.extend(day_data)
                    if all_values:
                        avg_traffic = sum(all_values) / len(all_values)
                
                heatmap_points.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [float(lng), float(lat)]
                    },
                    'properties': {
                        'place_id': place_id,
                        'name': name,
                        'type': ptype,
                        'traffic_intensity': avg_traffic,
                        'current_popularity': current_pop
                    }
                })
            
            return {
                'type': 'FeatureCollection',
                'features': heatmap_points
            }
            
        except Exception as e:
            logger.error(f"Error getting heatmap data: {str(e)}")
            return {'type': 'FeatureCollection', 'features': []}
    
    def _average_traffic_patterns(self, patterns: List[Dict]) -> Dict:
        """Average multiple traffic patterns into one aggregate pattern"""
        if not patterns:
            return {}
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        averaged = {}
        
        for day in days:
            hourly_values = []
            
            for pattern in patterns:
                if day in pattern and pattern[day]:
                    hourly_values.append(pattern[day])
            
            if hourly_values:
                averaged[day] = [
                    round(statistics.mean([hours[i] for hours in hourly_values if len(hours) > i]))
                    for i in range(24)
                ]
            else:
                averaged[day] = [0] * 24
        
        return averaged
    
    def _find_peak_traffic(self, popular_times: Dict) -> Tuple[str, int, int]:
        """Find the peak traffic day and hour"""
        peak_day = None
        peak_hour = None
        peak_value = 0
        
        for day, hours in popular_times.items():
            if not isinstance(hours, list):
                continue
            for hour, value in enumerate(hours):
                if value > peak_value:
                    peak_value = value
                    peak_day = day
                    peak_hour = hour
        
        return peak_day, peak_hour, peak_value
    
    def _calculate_vitality_score(self, num_locations: int,
                                 avg_traffic: Dict,
                                 place_types: Dict,
                                 current_popularity: List) -> float:
        """
        Calculate area vitality score (0-100)
        
        Factors:
        - Business density (0-30 points)
        - Average foot traffic levels (0-35 points)
        - Business diversity (0-20 points)
        - Current activity (0-15 points)
        """
        score = 0.0
        
        density_score = min(num_locations / 50.0 * 30, 30)
        score += density_score
        
        if avg_traffic:
            all_values = []
            for day in avg_traffic.values():
                if isinstance(day, list):
                    all_values.extend(day)
            avg_traffic_level = statistics.mean(all_values) if all_values else 0
            traffic_score = (avg_traffic_level / 100.0) * 35
            score += traffic_score
        
        diversity_score = min(len(place_types) / 10.0 * 20, 20)
        score += diversity_score
        
        if current_popularity:
            current_score = (statistics.mean(current_popularity) / 100.0) * 15
            score += current_score
        
        return round(score, 2)
    
    def _calculate_business_density(self, num_locations: int, radius_meters: int) -> float:
        """Calculate business density score"""
        import math
        area_sq_km = math.pi * (radius_meters / 1000) ** 2
        density_per_sq_km = num_locations / area_sq_km if area_sq_km > 0 else 0
        
        return round(min(density_per_sq_km / 100 * 100, 100), 2)
    
    def _calculate_consistency(self, patterns: List[Dict]) -> float:
        """Calculate traffic consistency across locations"""
        if not patterns or len(patterns) < 2:
            return 0.0
        
        try:
            all_avgs = []
            for pattern in patterns:
                values = []
                for day_data in pattern.values():
                    if isinstance(day_data, list):
                        values.extend(day_data)
                if values:
                    all_avgs.append(statistics.mean(values))
            
            if len(all_avgs) >= 2:
                std_dev = statistics.stdev(all_avgs)
                mean_val = statistics.mean(all_avgs)
                if mean_val > 0:
                    cv = std_dev / mean_val
                    consistency = max(0, 100 - cv * 100)
                    return round(consistency, 2)
        except:
            pass
        
        return 50.0
    
    def _generate_traffic_insights(self, analysis: Dict) -> str:
        """Generate human-readable traffic insights"""
        insights = []
        
        vitality = analysis.get('area_vitality_score', 0)
        if vitality >= 75:
            insights.append("This is a high-traffic area with excellent foot traffic potential.")
        elif vitality >= 50:
            insights.append("This area has moderate foot traffic, suitable for many business types.")
        elif vitality >= 25:
            insights.append("Foot traffic in this area is relatively low.")
        else:
            insights.append("This is a low-traffic area; consider if high foot traffic is needed for your business.")
        
        peak_day = analysis.get('peak_day')
        peak_hour = analysis.get('peak_hour')
        if peak_day and peak_hour is not None:
            hour_12 = peak_hour % 12 or 12
            ampm = "AM" if peak_hour < 12 else "PM"
            insights.append(f"Peak activity occurs on {peak_day} around {hour_12}:00 {ampm}.")
        
        dominant_types = analysis.get('dominant_place_types', {})
        if dominant_types:
            top_types = list(dominant_types.keys())[:3]
            insights.append(f"The area is characterized by: {', '.join(top_types)}.")
        
        business_density = analysis.get('business_density_score', 0)
        if business_density >= 70:
            insights.append("High business density indicates a commercial hub.")
        elif business_density >= 40:
            insights.append("Moderate business presence in the area.")
        
        return " ".join(insights)
    
    def _save_area_aggregation(self, analysis: Dict) -> None:
        """Save area aggregation to database for caching"""
        try:
            import json
            
            query = text("""
            INSERT INTO area_traffic_aggregations (
                center_latitude, center_longitude, center_location,
                radius_meters, avg_popular_times, total_locations_sampled,
                dominant_place_types, peak_day, peak_hour, peak_traffic_score,
                area_vitality_score, business_density_score, foot_traffic_consistency,
                last_refreshed
            )
            VALUES (
                :lat, :lng, ST_MakePoint(:lng, :lat)::geography,
                :radius, :avg_times::jsonb, :locations,
                :types::jsonb, :peak_day, :peak_hour, :peak_score,
                :vitality, :density, :consistency, NOW()
            )
            """)
            
            self.db.execute(query, {
                'lat': analysis['center_latitude'],
                'lng': analysis['center_longitude'],
                'radius': analysis['radius_meters'],
                'avg_times': json.dumps(analysis.get('avg_popular_times', {})),
                'locations': analysis['total_locations_sampled'],
                'types': json.dumps(analysis.get('dominant_place_types', {})),
                'peak_day': analysis.get('peak_day'),
                'peak_hour': analysis.get('peak_hour'),
                'peak_score': analysis.get('peak_traffic_score'),
                'vitality': analysis.get('area_vitality_score'),
                'density': analysis.get('business_density_score'),
                'consistency': analysis.get('traffic_consistency')
            })
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error saving area aggregation: {str(e)}")
    
    def _empty_analysis(self, latitude: float, longitude: float, radius_meters: int) -> Dict:
        """Return empty analysis structure"""
        return {
            'center_latitude': latitude,
            'center_longitude': longitude,
            'radius_meters': radius_meters,
            'total_locations_sampled': 0,
            'avg_popular_times': {},
            'peak_day': None,
            'peak_hour': None,
            'peak_traffic_score': 0,
            'current_avg_popularity': None,
            'area_vitality_score': 0,
            'business_density_score': 0,
            'traffic_consistency': 0,
            'dominant_place_types': {},
            'generated_at': datetime.now().isoformat(),
            'message': 'No foot traffic data available for this area. Try collecting data first.'
        }
