from fastapi import FastAPI # type: ignore
from routes import base ,data ,nlp
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore


app = FastAPI()

#@app.on_event("startup")
async def startup_span():
    settings = get_settings()

    # Initialize MongoDB connection
    #app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    #app.db_client = app.mongodb_conn[settings.MONGODB_DB_NAME]

    # Initialize PostgreSQL connection
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRESQL_USERNAME}:{settings.POSTGRESQL_PASSWORD}@{settings.POSTGRESQL_HOST}:{settings.POSTGRESQL_PORT}/{settings.POSTGRESQL_DB_NAME}"
    app.db_engine = create_async_engine(postgres_conn, echo=True)

    app.db_client = sessionmaker(
        bind=app.db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Initialize LLM and VectorDB provider factories
    llm_provider_factory = LLMProviderFactory(config=settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings)

    # Initialize generation client
    app.generation_client = llm_provider_factory.creat(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Initialize embedding client
    app.embedding_client = llm_provider_factory.creat(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE
    )

    # Initialize vector DB client
    app.vector_db_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect()

    app.template_parser = TemplateParser(language=settings.PRIMARY_LANG,
                                         default_language=settings.DEFAULT_LANG)
    

#@app.on_event("shutdown")
async def shutdown_span():
    app.mongodb_conn.close()
    app.vector_db_client.disconnect()

#app.router.lifespan.on_startup.append(startup_span)
#app.router.lifespan.on_shutdown.append(shutdown_span)

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)

