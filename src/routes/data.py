from fastapi import FastAPI  , APIRouter , Depends , UploadFile , status # type: ignore
from fastapi.responses import JSONResponse # type: ignore
import os
from helpers.config import get_settings ,Settings
from controllers import DataController , ProjectController
import aiofiles # type: ignore
from models import responseSignal
import logging

logger = logging.getLogger("uvicorn.error")


data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file:UploadFile ,
                       app_settings: Settings = Depends(get_settings)):
    #validation
    data_controller = DataController()
    is_valid , result = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result}
        )
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path = data_controller.generate_unique_filename(
        original_filename=file.filename,
        project_id=project_id
    )

    try:
        
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):  # Read file in chunks
                await f.write(chunk)
    except Exception as e:
        logger.error(f"File upload failed: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": responseSignal.File_Upload_Failed.value}
        )
    return JSONResponse(
        
        content={"message": responseSignal.File_Is_Valid.value}
    )

