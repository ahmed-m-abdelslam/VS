from .BaseController import BaseController
from fastapi import  UploadFile # type: ignore
from models import responseSignal
from .ProjectController import ProjectController
import os
import re

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024*1024  # MB to Bytes

    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False , responseSignal.Invalid_File_Type.value
        if file.size > self.app_settings.FILE_MAX_SIZE_MB * self.size_scale:
            return False , responseSignal.File_Size_Exceeds.value

        return True , responseSignal.File_Is_Valid.value
    

    def generate_unique_filepath(self, original_filename: str, project_id: str):
        random_key = self.get_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

        clean_file_name = self.get_clean_filename(
            original_filename=original_filename)
        
        new_file_path = os.path.join(
            project_path, f"{random_key}_{clean_file_name}")
        
        while os.path.exists(new_file_path):
            random_key = self.get_random_string()
            new_file_path = os.path.join(
                project_path, f"{random_key}_{clean_file_name}")
        return new_file_path , random_key + "_" + clean_file_name
    
    

    def get_clean_filename(self, original_filename: str):
        # Remove any unwanted characters from the filename
        clean_name = re.sub(r'[^\w.]', '', original_filename.strip())
        clean_file_name = clean_name.replace(" ", "_")
        return clean_file_name