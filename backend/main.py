"""
FastAPI application for LLM-powered Google Maps integration
Main entry point for the backend API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import asyncio
import os

from .config import settings
from .maps import maps_handler
from .llm import llm_handler
from .rate_limiter import RateLimitMiddleware


# Initialize FastAPI app
app = FastAPI(
    title="LLM Maps API",
    description="Local LLM powered Google Maps place finder",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)


# Request/Response Models
class PlaceQuery(BaseModel):
    """User place search request"""
    query: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PlaceResponse(BaseModel):
    """Place information response"""
    name: str
    address: str
    latitude: float
    longitude: float
    rating: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    google_maps_url: str
    types: Optional[list] = []


class SearchResponse(BaseModel):
    """Search results response"""
    query: str
    places: list[PlaceResponse]
    count: int


# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "debug": settings.debug
    }


@app.post("/search")
async def search_places(request: PlaceQuery) -> SearchResponse:
    """
    Search for places based on query

    Args:
        request: PlaceQuery with search parameters

    Returns:
        List of matching places with Google Maps information
    """
    if not request.query or len(request.query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

    try:
        # Search using Google Maps API
        location = (request.latitude, request.longitude) if request.latitude else None
        results = maps_handler.search_place(
            query=request.query,
            location=location
        )

        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])

        places = []
        for place in results.get("places", []):
            place_data = PlaceResponse(
                name=place.get("name", "Unknown"),
                address=place.get("address", ""),
                latitude=place.get("latitude", 0),
                longitude=place.get("longitude", 0),
                rating=place.get("rating"),
                phone=place.get("phone"),
                website=place.get("website"),
                google_maps_url=maps_handler.get_place_url(
                    place.get("latitude", 0),
                    place.get("longitude", 0)
                ),
                types=place.get("types", [])
            )
            places.append(place_data)

        return SearchResponse(
            query=request.query,
            places=places,
            count=len(places)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/llm-search")
async def llm_powered_search(request: PlaceQuery) -> SearchResponse:
    """
    Search places using LLM-powered natural language understanding
    
    LLM interprets user's intent and suggests appropriate places
    
    Args:
        request: User's natural language query
    
    Returns:
        List of places based on LLM interpretation
    """
    try:
        if not request.query or len(request.query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        
        # Query the LLM to understand user intent
        prompt = request.query
        llm_response = await llm_handler.query_llm(prompt)
        
        # Check for LLM errors
        if llm_response.startswith("Error:"):
            raise HTTPException(status_code=503, detail=f"LLM unavailable: {llm_response}")
        
        # Extract place query from LLM response
        place_query = llm_handler.extract_place_query(llm_response)
        
        if not place_query:
            raise HTTPException(
                status_code=400, 
                detail=f"LLM could not understand the query. Response: {llm_response}"
            )
        
        # Search Google Maps using LLM-extracted query
        location = (request.latitude, request.longitude) if request.latitude else None
        results = maps_handler.search_place(
            query=place_query,
            location=location
        )
        
        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])
        
        places = []
        for place in results.get("places", []):
            place_data = PlaceResponse(
                name=place.get("name", "Unknown"),
                address=place.get("address", ""),
                latitude=place.get("latitude", 0),
                longitude=place.get("longitude", 0),
                rating=place.get("rating"),
                phone=place.get("phone"),
                website=place.get("website"),
                google_maps_url=maps_handler.get_place_url(
                    place.get("latitude", 0),
                    place.get("longitude", 0)
                ),
                types=place.get("types", [])
            )
            places.append(place_data)
        
        return SearchResponse(
            query=f"{request.query} (LLM interpreted as: {place_query})",
            places=places,
            count=len(places)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM search failed: {str(e)}")


# Mount frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug
    )
