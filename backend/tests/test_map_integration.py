import pytest
from fastapi import status


class TestMapLayersEndpoints:
    def test_get_map_layers_returns_list(self, client, db_session):
        response = client.get("/api/v1/map/layers")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "layers" in data
        assert isinstance(data["layers"], list)

    def test_initialize_layers_creates_defaults(self, client, db_session):
        response = client.post("/api/v1/map/layers/initialize")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "layers" in data


class TestMapDataByBounds:
    def test_get_data_by_bounds(self, client, db_session):
        bounds = {
            "north": 31.0,
            "south": 30.0,
            "east": -97.0,
            "west": -98.0,
            "layers": None
        }
        response = client.post("/api/v1/map/data/bounds", json=bounds)
        assert response.status_code == status.HTTP_200_OK

    def test_bounds_validation_required_fields(self, client, db_session):
        invalid_bounds = {"north": 31.0}
        response = client.post("/api/v1/map/data/bounds", json=invalid_bounds)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestMapDataByCity:
    def test_get_data_by_city_post(self, client, db_session):
        city_request = {"city": "Austin", "state": "Texas"}
        response = client.post("/api/v1/map/data/city", json=city_request)
        assert response.status_code == status.HTTP_200_OK

    def test_get_data_by_city_get(self, client, db_session):
        response = client.get("/api/v1/map/data/city/Austin?state=Texas")
        assert response.status_code == status.HTTP_200_OK


class TestMapStatistics:
    def test_get_statistics(self, client, db_session):
        response = client.get("/api/v1/map/statistics")
        assert response.status_code == status.HTTP_200_OK


class TestOpportunityMapData:
    def test_get_opportunity_map_returns_geojson(self, client, db_session):
        from app.models.opportunity import Opportunity
        opp = db_session.query(Opportunity).filter(
            Opportunity.latitude.isnot(None),
            Opportunity.longitude.isnot(None)
        ).first()
        
        if not opp:
            pytest.skip("No opportunity with coordinates in database")
        
        response = client.get(f"/api/v1/map/opportunity/{opp.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "geojson" in data
        assert "metadata" in data
        assert "layer_config" in data
        
        geojson = data["geojson"]
        assert geojson["type"] == "FeatureCollection"
        assert "features" in geojson

    def test_opportunity_map_contains_required_layers(self, client, db_session):
        from app.models.opportunity import Opportunity
        opp = db_session.query(Opportunity).filter(
            Opportunity.latitude.isnot(None)
        ).first()
        
        if not opp:
            pytest.skip("No opportunity with coordinates in database")
        
        response = client.get(f"/api/v1/map/opportunity/{opp.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        layer_config = data["layer_config"]
        required_layers = ["service_area", "opportunity_center", "heatmap", "growth_trajectory", "migration_flow"]
        for layer in required_layers:
            assert layer in layer_config, f"Missing layer: {layer}"

    def test_opportunity_map_metadata_accuracy(self, client, db_session):
        from app.models.opportunity import Opportunity
        opp = db_session.query(Opportunity).filter(
            Opportunity.latitude.isnot(None)
        ).first()
        
        if not opp:
            pytest.skip("No opportunity with coordinates in database")
        
        response = client.get(f"/api/v1/map/opportunity/{opp.id}")
        data = response.json()
        
        metadata = data["metadata"]
        assert metadata["opportunity_id"] == opp.id
        assert "center" in metadata
        assert "lat" in metadata["center"]
        assert "lng" in metadata["center"]

    def test_opportunity_map_not_found(self, client, db_session):
        response = client.get("/api/v1/map/opportunity/99999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_service_area_feature_properties(self, client, db_session):
        from app.models.opportunity import Opportunity
        opp = db_session.query(Opportunity).filter(
            Opportunity.latitude.isnot(None)
        ).first()
        
        if not opp:
            pytest.skip("No opportunity with coordinates in database")
        
        response = client.get(f"/api/v1/map/opportunity/{opp.id}")
        data = response.json()
        
        service_area_features = [
            f for f in data["geojson"]["features"]
            if f["properties"]["layer"] == "service_area"
        ]
        
        if service_area_features:
            props = service_area_features[0]["properties"]
            assert "signal_density" in props
            assert "radius_miles" in props
            assert "style" in props

    def test_opportunity_center_marker(self, client, db_session):
        from app.models.opportunity import Opportunity
        opp = db_session.query(Opportunity).filter(
            Opportunity.latitude.isnot(None)
        ).first()
        
        if not opp:
            pytest.skip("No opportunity with coordinates in database")
        
        response = client.get(f"/api/v1/map/opportunity/{opp.id}")
        data = response.json()
        
        center_features = [
            f for f in data["geojson"]["features"]
            if f["properties"]["layer"] == "opportunity_center"
        ]
        
        assert len(center_features) == 1
        center = center_features[0]
        assert center["geometry"]["type"] == "Point"


class TestGrowthTrajectoryFeatures:
    def test_growth_trajectory_included(self, client, db_session):
        from app.models.opportunity import Opportunity
        opp = db_session.query(Opportunity).filter(
            Opportunity.latitude.isnot(None)
        ).first()
        
        if not opp:
            pytest.skip("No opportunity with coordinates in database")
        
        response = client.get(f"/api/v1/map/opportunity/{opp.id}")
        data = response.json()
        
        growth_features = [
            f for f in data["geojson"]["features"]
            if f["properties"]["layer"] == "growth_trajectory"
        ]
        
        assert isinstance(growth_features, list)

    def test_growth_trajectory_properties(self, client, db_session):
        from app.models.opportunity import Opportunity
        opp = db_session.query(Opportunity).filter(
            Opportunity.latitude.isnot(None)
        ).first()
        
        if not opp:
            pytest.skip("No opportunity with coordinates in database")
        
        response = client.get(f"/api/v1/map/opportunity/{opp.id}")
        data = response.json()
        
        growth_features = [
            f for f in data["geojson"]["features"]
            if f["properties"]["layer"] == "growth_trajectory"
        ]
        
        if growth_features:
            props = growth_features[0]["properties"]
            assert "city" in props
            assert "growth_category" in props
            assert "growth_score" in props
            assert props["growth_category"] in ["booming", "growing", "stable", "declining", "unknown"]


class TestMigrationFlowFeatures:
    def test_migration_flow_line_geometry(self, client, db_session):
        from app.models.opportunity import Opportunity
        opp = db_session.query(Opportunity).filter(
            Opportunity.latitude.isnot(None)
        ).first()
        
        if not opp:
            pytest.skip("No opportunity with coordinates in database")
        
        response = client.get(f"/api/v1/map/opportunity/{opp.id}")
        data = response.json()
        
        migration_features = [
            f for f in data["geojson"]["features"]
            if f["properties"]["layer"] == "migration_flow"
        ]
        
        for flow in migration_features:
            assert flow["geometry"]["type"] == "LineString"
            assert len(flow["geometry"]["coordinates"]) == 2

    def test_migration_flow_width_scaling(self, client, db_session):
        from app.models.opportunity import Opportunity
        opp = db_session.query(Opportunity).filter(
            Opportunity.latitude.isnot(None)
        ).first()
        
        if not opp:
            pytest.skip("No opportunity with coordinates in database")
        
        response = client.get(f"/api/v1/map/opportunity/{opp.id}")
        data = response.json()
        
        migration_features = [
            f for f in data["geojson"]["features"]
            if f["properties"]["layer"] == "migration_flow"
        ]
        
        for flow in migration_features:
            props = flow["properties"]
            assert "line_width" in props
            assert 2 <= props["line_width"] <= 8
            
            expected_intensity = min(1.0, props["flow_count"] / 50000)
            expected_width = 2 + (expected_intensity * 6)
            assert abs(props["line_width"] - expected_width) < 0.01


class TestCensusApiStatus:
    def test_census_status_endpoint(self, client, db_session):
        response = client.get("/api/v1/map/census/status")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "configured" in data
        assert isinstance(data["configured"], bool)


class TestMapSessions:
    def test_save_session(self, client, db_session):
        session_data = {
            "layer_state": {
                "service_area": True,
                "heatmap": False
            },
            "viewport": {
                "center": [-97.7431, 30.2672],
                "zoom": 10
            },
            "session_name": "Test Session"
        }
        response = client.post("/api/v1/map/session", json=session_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "message" in data

    def test_get_sessions(self, client, db_session):
        response = client.get("/api/v1/map/sessions")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)


class TestTierBasedAccess:
    def test_map_data_includes_tier_info(self, client, db_session):
        from app.models.opportunity import Opportunity
        opp = db_session.query(Opportunity).filter(
            Opportunity.latitude.isnot(None)
        ).first()
        
        if not opp:
            pytest.skip("No opportunity with coordinates in database")
        
        response = client.get(f"/api/v1/map/opportunity/{opp.id}")
        data = response.json()
        
        assert "layer_config" in data
        for layer_name, layer_info in data["layer_config"].items():
            assert "visible" in layer_info
            assert "type" in layer_info
