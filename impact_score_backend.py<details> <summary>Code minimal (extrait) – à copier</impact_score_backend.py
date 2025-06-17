"""
impact_score_backend.py  –  Backend FastAPI pour « Impact Score App »
---------------------------------------------------------------------
• Modèle 4 critères (1-3) → total /12  (Alignement, Couverture,
  Expérience-Impact, Réputation)
• Renvoie JSON prêt à être consommé par le front React.
• Fonctionne hors-ligne (fallback) ou en mode “réel” si tu branches
  SerpAPI + OpenAI plus tard.

Run local :
    uvicorn impact_score_backend:app --reload
"""

from __future__ import annotations

import os, hashlib
from datetime import datetime
from typing import List

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
SERP_KEY   = os.getenv("SERPAPI_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

app = FastAPI(title="Impact Score API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────── models ────────────────────────────────
class Sub4(BaseModel):
    alignement_strategique: int = Field(..., ge=1, le=3)
    couverture: int             = Field(..., ge=1, le=3)
    experience_impact: int      = Field(..., ge=1, le=3)
    reputation: int             = Field(..., ge=1, le=3)

class Score12(BaseModel):
    entity: str
    total: int                  # 0-12
    decision: str
    sub_scores: Sub4
    confidence: int             # 0-100
    sources: List[str]
    fallback: bool
    timestamp: datetime

# ────────────────────────── helpers ────────────────────────────────
def fallback_scoring(name: str) -> Score12:
    """
    Score déterministe (hors-ligne) basé sur un hash du nom.
    Garantit des valeurs 1-3 et reproduisibles.
    """
    h = int(hashlib.md5(name.encode()).hexdigest(), 16)
    def pick(seed): return 1 + ((h + seed) % 3)

    sub = Sub4(
        alignement_strategique = pick(1),
        couverture             = pick(2),
        experience_impact      = pick(3),
        reputation             = pick(4),
    )
    total = sum(sub.model_dump().values())
    decision = "À prioriser" if total >= 11 else "À suivre" if total >= 7 else "À écarter"

    return Score12(
        entity      = name,
        total       = total,
        decision    = decision,
        sub_scores  = sub,
        confidence  = 0,          # 0 % car pas de data réelle
        sources     = [],
        fallback    = True,
        timestamp   = datetime.utcnow(),
    )

def todo_real_scoring(name: str) -> Score12:
    """
    --->  Tu peux implémenter ici la vraie logique :
          1) Recherche Web via SerpAPI / Bing
          2) Résumé & extraction via OpenAI
          3) Calcul des 4 notes (1-3) et confidence
          4) Retourne Score12
    """
    # Pour l’instant on renvoie fallback mais avec confidence 0
    return fallback_scoring(name)

# ───────────────────────── endpoints ───────────────────────────────
@app.get("/score", response_model=Score12)
def get_score(entity: str = Query(..., min_length=3, max_length=100)):
    """
    Retourne le score sur 12 points pour l’entité demandée.
    Utilise le mode « réel » si les clés API sont présentes,
    sinon bascule en fallback déterministe.
    """
    if SERP_KEY and OPENAI_KEY:
        return todo_real_scoring(entity)

    return fallback_scoring(entity)

@app.get("/")
def root():
    return {"msg": "Impact Score API up", "time": datetime.utcnow()}
