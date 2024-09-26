from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
import instructor
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware

# Définition du modèle de réponse
class CityDetail(BaseModel):
    amountVat: Optional[float]
    amountVat1: Optional[float]
    amountVat2: Optional[float]
    adresse: Optional[str]
    billDate: Optional[str]
    num: Optional[str]
    vat: Optional[float]
    vat1: Optional[float]
    vat2: Optional[float]
    net: Optional[float]
    net1: Optional[float]
    net2: Optional[float]
    emet: Optional[str]
    iban: Optional[str]
    currency: Optional[str]
    isMultiVat: Optional[bool]

    @validator('vat', 'vat1', 'vat2', pre=True, always=True)
    def convert_vat_fields(cls, value):
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        return value

# Définition du modèle de requête
class ContentRequest(BaseModel):
    content: str

# Initialiser FastAPI
app = FastAPI()

# Ajouter CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou spécifiez les domaines spécifiques comme ["http://example.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration du client
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # clé API requise, mais non utilisée
    ),
    mode=instructor.Mode.JSON,
)

@app.post("/api/facturation")
async def process_content(request: ContentRequest):
    try:
        # Exécuter la requête avec le contenu dynamique
        response = client.chat.completions.create(
            model="gemma2:latest",
            messages=[
                {"role": "user", "content": request.content}
            ],
            response_model=CityDetail,
        )

        # Afficher le résultat
        return response.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
