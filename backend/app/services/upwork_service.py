import os
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import httpx
from authlib.integrations.httpx_client import OAuth1Client

logger = logging.getLogger(__name__)

UPWORK_API_KEY = os.getenv("UPWORK_API_KEY", "")
UPWORK_API_SECRET = os.getenv("UPWORK_API_SECRET", "")
UPWORK_GRAPHQL_URL = "https://api.upwork.com/graphql"


@dataclass
class UpworkFreelancer:
    id: str
    name: str
    title: str
    description: Optional[str]
    hourly_rate: Optional[float]
    skills: List[str]
    country: Optional[str]
    city: Optional[str]
    profile_url: str
    avatar_url: Optional[str]
    job_success_score: Optional[float]
    total_hours: Optional[float]
    total_jobs: Optional[int]
    avg_rating: Optional[float]


class UpworkService:
    
    @staticmethod
    def _get_oauth_client() -> OAuth1Client:
        return OAuth1Client(
            client_id=UPWORK_API_KEY,
            client_secret=UPWORK_API_SECRET
        )
    
    @staticmethod
    async def search_freelancers(
        query: Optional[str] = None,
        skills: Optional[List[str]] = None,
        category: Optional[str] = None,
        hourly_rate_min: Optional[float] = None,
        hourly_rate_max: Optional[float] = None,
        country: Optional[str] = None,
        job_success_min: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for freelancers on Upwork using GraphQL API.
        
        Returns dict with 'freelancers' list and 'total_count'.
        """
        if not UPWORK_API_KEY or not UPWORK_API_SECRET:
            logger.warning("Upwork API credentials not configured")
            return {"freelancers": [], "total_count": 0, "error": "API not configured"}
        
        search_filter = {}
        if query:
            search_filter["q"] = query
        if skills:
            search_filter["skills_v2"] = skills
        if category:
            search_filter["categories_v2"] = [category]
        if hourly_rate_min is not None or hourly_rate_max is not None:
            hourly_rate = {}
            if hourly_rate_min is not None:
                hourly_rate["min"] = hourly_rate_min
            if hourly_rate_max is not None:
                hourly_rate["max"] = hourly_rate_max
            search_filter["hourlyRate"] = hourly_rate
        if country:
            search_filter["locations"] = [{"country": country}]
        if job_success_min is not None:
            search_filter["jobSuccessScore"] = {"min": job_success_min}
        
        graphql_query = """
        query freelancerProfileSearchRecords(
          $searchFilter: FreelancerProfileSearchFilter!,
          $pagination: Pagination!
        ) {
          freelancerProfileSearchRecords(
            searchFilter: $searchFilter,
            pagination: $pagination
          ) {
            edges {
              node {
                id
                user {
                  nid
                  name
                }
                title
                description
                hourlyRate {
                  amount
                  currency
                }
                skills {
                  name
                }
                location {
                  country
                  city
                }
                portrait {
                  portrait
                }
                stats {
                  jobSuccessScore
                  totalHours
                  totalJobs
                }
                rating {
                  overallScore
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
            totalCount
          }
        }
        """
        
        variables = {
            "searchFilter": search_filter if search_filter else {},
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    UPWORK_GRAPHQL_URL,
                    json={
                        "query": graphql_query,
                        "variables": variables
                    },
                    headers={
                        "Authorization": f"Bearer {UPWORK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Upwork API error: {response.status_code} - {response.text}")
                    return {"freelancers": [], "total_count": 0, "error": f"API error: {response.status_code}"}
                
                data = response.json()
                
                if "errors" in data:
                    logger.error(f"Upwork GraphQL errors: {data['errors']}")
                    return {"freelancers": [], "total_count": 0, "error": str(data['errors'])}
                
                search_results = data.get("data", {}).get("freelancerProfileSearchRecords", {})
                edges = search_results.get("edges", [])
                total_count = search_results.get("totalCount", 0)
                
                freelancers = []
                for edge in edges:
                    node = edge.get("node", {})
                    user = node.get("user", {})
                    hourly_rate_data = node.get("hourlyRate", {})
                    location = node.get("location", {})
                    stats = node.get("stats", {})
                    rating = node.get("rating", {})
                    skills_data = node.get("skills", [])
                    
                    freelancer = UpworkFreelancer(
                        id=node.get("id", ""),
                        name=user.get("name", ""),
                        title=node.get("title", ""),
                        description=node.get("description"),
                        hourly_rate=hourly_rate_data.get("amount") if hourly_rate_data else None,
                        skills=[s.get("name", "") for s in skills_data] if skills_data else [],
                        country=location.get("country") if location else None,
                        city=location.get("city") if location else None,
                        profile_url=f"https://www.upwork.com/freelancers/{user.get('nid', '')}",
                        avatar_url=node.get("portrait", {}).get("portrait") if node.get("portrait") else None,
                        job_success_score=stats.get("jobSuccessScore") if stats else None,
                        total_hours=stats.get("totalHours") if stats else None,
                        total_jobs=stats.get("totalJobs") if stats else None,
                        avg_rating=rating.get("overallScore") if rating else None
                    )
                    freelancers.append(freelancer)
                
                return {
                    "freelancers": [vars(f) for f in freelancers],
                    "total_count": total_count,
                    "has_next_page": search_results.get("pageInfo", {}).get("hasNextPage", False)
                }
                
        except httpx.TimeoutException:
            logger.error("Upwork API timeout")
            return {"freelancers": [], "total_count": 0, "error": "API timeout"}
        except Exception as e:
            logger.error(f"Upwork API exception: {str(e)}")
            return {"freelancers": [], "total_count": 0, "error": str(e)}
    
    @staticmethod
    async def get_freelancer_profile(freelancer_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed profile of a specific freelancer."""
        if not UPWORK_API_KEY or not UPWORK_API_SECRET:
            return None
        
        graphql_query = """
        query freelancerProfile($id: ID!) {
          freelancerProfile(id: $id) {
            id
            user {
              nid
              name
            }
            title
            description
            hourlyRate {
              amount
              currency
            }
            skills {
              name
            }
            location {
              country
              city
            }
            portrait {
              portrait
            }
            stats {
              jobSuccessScore
              totalHours
              totalJobs
            }
            rating {
              overallScore
            }
            employmentHistory {
              company
              title
              startDate
              endDate
              description
            }
            education {
              institution
              degree
              areaOfStudy
              startDate
              endDate
            }
          }
        }
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    UPWORK_GRAPHQL_URL,
                    json={
                        "query": graphql_query,
                        "variables": {"id": freelancer_id}
                    },
                    headers={
                        "Authorization": f"Bearer {UPWORK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                if "errors" in data:
                    return None
                
                return data.get("data", {}).get("freelancerProfile")
                
        except Exception as e:
            logger.error(f"Error fetching Upwork profile: {str(e)}")
            return None
    
    @staticmethod
    def get_upwork_categories() -> List[Dict[str, str]]:
        """Return list of Upwork talent categories for filtering."""
        return [
            {"id": "531770282580668418", "name": "Web Development"},
            {"id": "531770282580668419", "name": "Mobile Development"},
            {"id": "531770282580668420", "name": "Design & Creative"},
            {"id": "531770282580668421", "name": "Writing"},
            {"id": "531770282580668422", "name": "Marketing"},
            {"id": "531770282580668423", "name": "Admin Support"},
            {"id": "531770282580668424", "name": "Customer Service"},
            {"id": "531770282580668425", "name": "Data Science & Analytics"},
            {"id": "531770282580668426", "name": "Engineering & Architecture"},
            {"id": "531770282580668427", "name": "IT & Networking"},
            {"id": "531770282580668428", "name": "Legal"},
            {"id": "531770282580668429", "name": "Accounting & Consulting"},
            {"id": "531770282580668430", "name": "Translation"},
            {"id": "531770282580668431", "name": "Sales"},
        ]
