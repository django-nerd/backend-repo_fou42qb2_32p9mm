import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Event, Blogpost, Contact, Volunteer

app = FastAPI(title="Atmasakshi Foundation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"name": "Atmasakshi Foundation API", "status": "ok"}


@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, "name", None) or "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# ---- Content Endpoints ----

@app.get("/api/events")
def list_events(limit: int = 6):
    try:
        events = []
        if db is not None:
            events = get_documents("event", {}, limit)
            # Normalize ObjectId
            for e in events:
                e["id"] = str(e.get("_id"))
                e.pop("_id", None)
        if not events:
            events = [
                {
                    "title": "Guided Meditation Camp",
                    "description": "A calm evening of breath awareness and mantra meditation.",
                    "date": datetime(2025, 1, 20, 18, 0).isoformat(),
                    "location": "Vidya Nagar, Gokak",
                    "image_url": "https://images.unsplash.com/photo-1540569014015-19a7be504e3a?q=80&w=1600&auto=format&fit=crop",
                    "tags": ["meditation", "peace"],
                },
                {
                    "title": "Blood Donation Drive",
                    "description": "Serve humanity by donating blood and saving lives.",
                    "date": datetime(2025, 2, 5, 10, 0).isoformat(),
                    "location": "Gokak City Hospital",
                    "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?q=80&w=1600&auto=format&fit=crop",
                    "tags": ["service", "health"],
                },
                {
                    "title": "Organic Farming Workshop",
                    "description": "Hands-on session on natural living and soil health.",
                    "date": datetime(2025, 2, 22, 9, 0).isoformat(),
                    "location": "Community Farm, Gokak",
                    "image_url": "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?q=80&w=1600&auto=format&fit=crop",
                    "tags": ["farming", "environment"],
                },
            ][:limit]
        return {"items": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/contact")
def submit_contact(payload: Contact):
    try:
        if db is not None:
            doc_id = create_document("contact", payload)
            return {"status": "received", "id": doc_id}
        return {"status": "received", "id": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/volunteer")
def submit_volunteer(payload: Volunteer):
    try:
        if db is not None:
            doc_id = create_document("volunteer", payload)
            return {"status": "received", "id": doc_id}
        return {"status": "received", "id": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/blogs")
def list_blogs(limit: int = 3):
    try:
        posts = []
        if db is not None:
            posts = get_documents("blogpost", {}, limit)
            for p in posts:
                p["id"] = str(p.get("_id"))
                p.pop("_id", None)
        if not posts:
            posts = [
                {
                    "title": "Meditation for Inner Clarity",
                    "slug": "meditation-for-inner-clarity",
                    "excerpt": "A gentle practice to quiet the mind and open the heart.",
                    "cover_image": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1600&auto=format&fit=crop",
                    "author": "Team Atmasakshi",
                    "published_at": datetime(2025, 1, 10).isoformat(),
                },
                {
                    "title": "Serving with Compassion",
                    "slug": "serving-with-compassion",
                    "excerpt": "Seva as a path to self-realization and community well-being.",
                    "cover_image": "https://images.unsplash.com/photo-1493836512294-502baa1986e2?q=80&w=1600&auto=format&fit=crop",
                    "author": "Team Atmasakshi",
                    "published_at": datetime(2025, 1, 5).isoformat(),
                },
                {
                    "title": "Why Organic Farming Matters",
                    "slug": "why-organic-farming-matters",
                    "excerpt": "Nurturing the earth is nurturing ourselves.",
                    "cover_image": "https://images.unsplash.com/photo-1465406325902-283296f2c1c7?q=80&w=1600&auto=format&fit=crop",
                    "author": "Team Atmasakshi",
                    "published_at": datetime(2024, 12, 20).isoformat(),
                },
            ][:limit]
        return {"items": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/blogs/{slug}")
def get_blog(slug: str):
    try:
        if db is not None:
            docs = get_documents("blogpost", {"slug": slug}, 1)
            if docs:
                p = docs[0]
                p["id"] = str(p.get("_id"))
                p.pop("_id", None)
                return p
        # Fallback samples
        samples = {p["slug"]: p for p in list_blogs(limit=10)["items"]}
        if slug in samples:
            return samples[slug]
        raise HTTPException(status_code=404, detail="Blog not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Optional: simple schema descriptor for viewers
class SchemaField(BaseModel):
    name: str
    type: str
    required: bool = True

class SchemaDescription(BaseModel):
    name: str
    fields: List[SchemaField]

@app.get("/schema", response_model=List[SchemaDescription])
def get_schema():
    return [
        SchemaDescription(
            name="event",
            fields=[
                SchemaField(name="title", type="string"),
                SchemaField(name="description", type="string", required=False),
                SchemaField(name="date", type="datetime"),
                SchemaField(name="location", type="string", required=False),
                SchemaField(name="image_url", type="string", required=False),
                SchemaField(name="tags", type="list[string]", required=False),
            ],
        ),
        SchemaDescription(
            name="blogpost",
            fields=[
                SchemaField(name="title", type="string"),
                SchemaField(name="slug", type="string"),
                SchemaField(name="excerpt", type="string", required=False),
                SchemaField(name="content", type="string"),
                SchemaField(name="cover_image", type="string", required=False),
                SchemaField(name="author", type="string", required=False),
                SchemaField(name="published_at", type="datetime", required=False),
            ],
        ),
        SchemaDescription(
            name="contact",
            fields=[
                SchemaField(name="name", type="string"),
                SchemaField(name="email", type="email"),
                SchemaField(name="phone", type="string", required=False),
                SchemaField(name="message", type="string"),
            ],
        ),
        SchemaDescription(
            name="volunteer",
            fields=[
                SchemaField(name="name", type="string"),
                SchemaField(name="email", type="email"),
                SchemaField(name="phone", type="string"),
                SchemaField(name="areas", type="list[string]"),
                SchemaField(name="notes", type="string", required=False),
            ],
        ),
    ]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
