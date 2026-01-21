"""Unit tests for the layer command parser endpoint."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.maps import (
    _parse_center,
    _parse_radius,
    _parse_layers,
    LAYER_KEYWORDS,
    RADIUS_KEYWORDS,
)


client = TestClient(app)


class TestParseCenterFunction:
    """Tests for the _parse_center helper function."""

    def test_parse_known_city_austin(self):
        result = _parse_center("set center to austin")
        assert result is not None
        assert result.action == "set_center"
        assert result.center["lat"] == pytest.approx(30.2672, rel=1e-3)
        assert result.center["lng"] == pytest.approx(-97.7431, rel=1e-3)
        assert result.address == "Austin"

    def test_parse_known_city_nyc(self):
        result = _parse_center("show me nyc area")
        assert result is not None
        assert result.address == "New York City"
        assert result.center["lat"] == pytest.approx(40.7128, rel=1e-3)

    def test_parse_known_city_san_francisco(self):
        result = _parse_center("san francisco downtown")
        assert result is not None
        assert result.address == "San Francisco"

    def test_parse_unknown_city(self):
        result = _parse_center("set center to paris")
        assert result is None

    def test_parse_empty_prompt(self):
        result = _parse_center("")
        assert result is None


class TestParseRadiusFunction:
    """Tests for the _parse_radius helper function."""

    def test_parse_quarter_mile(self):
        result = _parse_radius("within quarter mile")
        assert result is not None
        assert result.action == "set_radius"
        assert result.radius == 0.25

    def test_parse_1_mile(self):
        result = _parse_radius("1 mile radius")
        assert result is not None
        assert result.radius == 1.0

    def test_parse_one_mile_word(self):
        result = _parse_radius("one mile around")
        assert result is not None
        assert result.radius == 1.0

    def test_parse_5_mile(self):
        result = _parse_radius("5 mile area")
        assert result is not None
        assert result.radius == 5.0

    def test_parse_10_mile(self):
        result = _parse_radius("ten mile radius")
        assert result is not None
        assert result.radius == 10.0

    def test_parse_no_radius(self):
        result = _parse_radius("show me demographics")
        assert result is None


class TestParseLayersFunction:
    """Tests for the _parse_layers helper function."""

    def test_parse_demographics_layer(self):
        result = _parse_layers("show demographics data", [])
        assert len(result) == 1
        assert result[0].action == "add_layer"
        assert result[0].layer_type == "demographics"

    def test_parse_population_keyword(self):
        result = _parse_layers("show population data", [])
        assert len(result) == 1
        assert result[0].layer_type == "demographics"

    def test_parse_competition_layer(self):
        result = _parse_layers("find competitors nearby", [])
        assert len(result) == 1
        assert result[0].layer_type == "competition"

    def test_parse_competition_with_business_type(self):
        result = _parse_layers("find coffee shop competitors", [])
        assert len(result) == 1
        assert result[0].layer_type == "competition"
        assert result[0].config["searchQuery"] == "coffee"

    def test_parse_deep_clone_layer(self):
        result = _parse_layers("clone this business model", [])
        assert len(result) == 1
        assert result[0].layer_type == "deep_clone"

    def test_parse_traffic_layer(self):
        result = _parse_layers("show foot traffic data", [])
        assert len(result) == 1
        assert result[0].layer_type == "traffic"

    def test_skip_already_active_layer(self):
        result = _parse_layers("show demographics", ["demographics"])
        assert len(result) == 0

    def test_parse_multiple_layers(self):
        result = _parse_layers("show demographics and find competitors", [])
        assert len(result) == 2
        layer_types = {r.layer_type for r in result}
        assert "demographics" in layer_types
        assert "competition" in layer_types

    def test_parse_no_layers(self):
        result = _parse_layers("hello world", [])
        assert len(result) == 0


class TestParseLayerCommandEndpoint:
    """Integration tests for the /parse-layer-command endpoint."""

    def test_empty_prompt_returns_helpful_message(self):
        response = client.post(
            "/api/v1/maps/parse-layer-command",
            json={"prompt": "", "active_layers": []}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["actions"]) == 0
        assert "provide a description" in data["message"].lower()

    def test_unrecognized_prompt_returns_suggestions(self):
        response = client.post(
            "/api/v1/maps/parse-layer-command",
            json={"prompt": "xyz abc 123", "active_layers": []}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["actions"]) == 0
        assert "couldn't understand" in data["message"].lower()

    def test_full_command_with_city_and_radius(self):
        response = client.post(
            "/api/v1/maps/parse-layer-command",
            json={
                "prompt": "set center to austin with 2 mile radius",
                "active_layers": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["actions"]) == 2
        
        actions_by_type = {a["action"]: a for a in data["actions"]}
        assert "set_center" in actions_by_type
        assert "set_radius" in actions_by_type
        assert actions_by_type["set_center"]["address"] == "Austin"
        assert actions_by_type["set_radius"]["radius"] == 2.0

    def test_add_layer_command(self):
        response = client.post(
            "/api/v1/maps/parse-layer-command",
            json={
                "prompt": "show me demographics for this area",
                "active_layers": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["actions"]) == 1
        assert data["actions"][0]["action"] == "add_layer"
        assert data["actions"][0]["layer_type"] == "demographics"

    def test_combined_command(self):
        response = client.post(
            "/api/v1/maps/parse-layer-command",
            json={
                "prompt": "show miami area with 5 mile radius and demographics",
                "active_layers": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["actions"]) == 3
        
        action_types = [a["action"] for a in data["actions"]]
        assert "set_center" in action_types
        assert "set_radius" in action_types
        assert "add_layer" in action_types

    def test_response_includes_descriptive_message(self):
        response = client.post(
            "/api/v1/maps/parse-layer-command",
            json={
                "prompt": "austin 1 mile demographics",
                "active_layers": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "Applied:" in data["message"]
        assert "Austin" in data["message"]
