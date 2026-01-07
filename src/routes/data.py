from fastapi import FastAPI  , APIRouter , Depends , UploadFile , status , Request # type: ignore
from fastapi.responses import JSONResponse # type: ignore
import os
from helpers.config import get_settings ,Settings
from controllers import DataController , ProjectController , ProcessController
import aiofiles # type: ignore
from models import responseSignal
import logging
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk , Asset
from models.AssetModel import AssetModel
from models.enums.AssetsTypeEnum import AssetsTypeEnum


logger = logging.getLogger("uvicorn.error")


data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(requst:Request, project_id: str, file:UploadFile ,
                       app_settings: Settings = Depends(get_settings)):
    
    project_model = await ProjectModel.creat_instance(
        db_client= requst.app.db_client

    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
        )

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
    

    asset_model = await AssetModel.creat_instance(
        db_client= requst.app.db_client
    )

    asset_resorce = Asset(
        asset_project_id= project.id,
        asset_type= AssetsTypeEnum.FILE_F.value,
        asset_name= file_id,
        asset_size= os.path.getsize(file_path),

    )

    asset_record= await asset_model.create_asset(asset= asset_resorce)




    return JSONResponse(
        
        content={
            "message": responseSignal.File_Is_Valid.value
            ,"file_id": str(asset_record.id)
            
            }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(requst:Request,project_id: str, process_request: ProcessRequest ):

    #file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    chunk_overlap = process_request.overlap_size
    do_reset = process_request.do_reset

    chunk_model = await ChunkModel.creat_instance(
        db_client= requst.app.db_client

    )

    project_model = await ProjectModel.creat_instance(
        db_client= requst.app.db_client

    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    asset_model = await AssetModel.creat_instance(
        db_client= requst.app.db_client
    )
    project_file_ids = {}


    if process_request.file_id:
        asset_record = await asset_model.gert_asset_record(
            asset_project_id= project.id,
            asset_name= process_request.file_id
        )

        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": responseSignal.File_ID_Errore.value}
            )


        project_file_ids= {
            asset_record.id : asset_record.asset_name
        }
    else:
       
        project_files = await asset_model.get_all_project_assets(
            asset_project_id= project.id,
            asset_type= AssetsTypeEnum.FILE_F.value
        )

        project_file_ids = {
             record.id : record.asset_name for record in project_files
               }

    if len( project_file_ids) ==0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": responseSignal.Processing_Failed.value}
        )



    process_controller = ProcessController(project_id=project_id)

    no_records = 0
    no_files = 0

    if do_reset == 1:
            await chunk_model.delete_chunk_by_project_id(project_id=project.id)

    for asset_id , file_id in project_file_ids.items():

        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.error(f"File processing failed")
            continue

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
        file_chunks_records = [
            DataChunk(
                chunk_text= chunk.page_content,
                chunk_metadata= chunk.metadata,
                chunk_order= i+1,
                chunk_project_id= project.id,
                chunk_asset_id= asset_id
            ) for i, chunk in enumerate(file_chunks)   
        ]

        no_records += await chunk_model.insert_many_chunks(chunks= file_chunks_records)
        no_files +=1

    return JSONResponse(
        content={
            "message": responseSignal.Processing_Successful.value,
            "records_inserted": no_records ,
            "files_processed": no_files
        }
    )