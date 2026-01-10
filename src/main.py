from fastapi import FastAPI # type: ignore
from routes import base ,data
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory

app = FastAPI()

#@app.on_event("startup")
async def startup_span():
    settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongodb_conn[settings.MONGODB_DB_NAME]

    llm_provider_factory = LLMProviderFactory(config=settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings)

    # Initialize generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Initialize embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE
    )

    # Initialize vector DB client
    app.vector_db_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect(
        embedding_client=app.embedding_client,
        db_path=settings.VECTORDB_PATH,
        distance_method=settings.VECTORDB_DISTANCE_METHOD
    )

#@app.on_event("shutdown")
async def shutdown_span():
    app.mongodb_conn.close()
    app.vector_db_client.disconnect()

app.router.lifespan.on_startup.append(startup_span)
app.router.lifespan.on_shutdown.append(shutdown_span)
app.include_router(base.base_router)
app.include_router(data.data_router)

