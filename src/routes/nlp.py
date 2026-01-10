from fastapi import FastAPI  , APIRouter , Depends , UploadFile , status , Request # type: ignore
from fastapi.responses import JSONResponse # type: ignore
import os
import logging
from .schemes.nlp import PushRequest
from models.ProjectModel import ProjectModel
from controllers import  NLPController
from models import responseSignal
from models.ChunkModel import ChunkModel




logger = logging.getLogger("uvicorn.error")


nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def index_and_push_data(request:Request, project_id: str, push_request:PushRequest):
    
    project_model = await ProjectModel.creat_instance(db_client=request.app.db_client)

    project= await project_model.get_project_or_create_one(project_id=project_id)

    chunk_model = await ChunkModel.creat_instance(db_client=request.app.db_client)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": responseSignal.Project_Not_Found.value
            }
            )
        


    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )

    has_records = True
    page_no = 1 
    inserted_items_count = 0
    idx = 0

    while has_records:

        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page_no=page_no)
        if len(page_chunks):
            page_no+=1
    
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunk_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        is_inserted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            do_rset = push_request.do_reset
            ,chunks_ids=chunk_ids
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "signal": responseSignal.Insert_into_VectorDB_Error.value
                }
            )
        inserted_items_count += len(page_chunks)
        
    return JSONResponse(
        content={
            "signal": responseSignal.Insert_into_VectorDB_Success.value,
            "inserted_items_count": inserted_items_count
        }
    )