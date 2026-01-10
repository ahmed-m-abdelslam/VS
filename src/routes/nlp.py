from fastapi import FastAPI  , APIRouter , Depends , UploadFile , status , Request # type: ignore
from fastapi.responses import JSONResponse # type: ignore
import os
import logging
from .schemes.nlp import PushRequest
from models.ProjectModel import ProjectModel


from helpers.config import get_settings ,Settings
from controllers import DataController , ProjectController , ProcessController
import aiofiles # type: ignore
from models import responseSignal

from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk , Asset
from models.AssetModel import AssetModel
from models.enums.AssetsTypeEnum import AssetsTypeEnum


logger = logging.getLogger("uvicorn.error")


nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def index_and_push_data(request:Request, project_id: str, push_request:PushRequest):
    
    project_model = await ProjectModel.creat_instance(db_client=request.app.db_client)

    project= await project_model.get_project_or_create_one(project_id=project_id)

    
    
   