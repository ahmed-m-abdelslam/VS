from enum import Enum

class responseSignal(Enum):
    Invalid_File_Type = "Invalid file type"
    File_Size_Exceeds = "File size exceeds the maximum allowed size."
    File_Is_Valid = "File is valid"
    File_Upload_Failed = "File upload failed due to an internal error."
    Processing_Failed = "File processing failed."
    Processing_Successful = "File processed successfully."
    