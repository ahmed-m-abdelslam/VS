from fastapi import FastAPI  , APIRouter , Depends , UploadFile , status # type: ignore
from fastapi.responses import JSONResponse # type: ignore
import os
from helpers.config import get_settings ,Settings
from controllers import DataController , ProjectController , ProcessController
import aiofiles # type: ignore
from models import responseSignal
import logging
from .schemes.data import ProcessRequest

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
    file_path , file_id = data_controller.generate_unique_filepath(
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
        
        content={
            "message": responseSignal.File_Is_Valid.value
            ,"file_id": file_id}
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, process_request: ProcessRequest ):

    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    chunk_overlap = process_request.overlap_size


    process_controller = ProcessController(project_id=project_id)

    file_content = process_controller.get_file_content(file_id=file_id)

    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": responseSignal.Processing_Failed.value}
        )
    return file_chunks

