import sys, os
import os
import sys

# # Get the current file's directory
# current_file_path = os.path.abspath(__file__)

# # Get the parent directory of the current file
# parent_directory = os.path.dirname(os.path.dirname(current_file_path)) + '/scripts'

# #Add the parent directory to sys.path
# #To Do: Do this correctly
# sys.path.append(parent_directory)
# from scripts.create_kml_from_shared_album import convert_heic_to_jpg_ffmpeg

# def test_convert_heic_to_jpg_ffmpeg():
#     current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current test file
#     heic_file = os.path.abspath(os.path.join(current_dir, "data/IMG_5107.HEIC"))
#     jpg_file = os.path.abspath(os.path.join(current_dir, "data/test.jpg"))
#     convert_heic_to_jpg_ffmpeg(heic_file, jpg_file)
#     assert os.path.exists(jpg_file)