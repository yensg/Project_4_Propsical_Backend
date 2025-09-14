import os
from dotenv import load_dotenv
import cloudinary
load_dotenv()

cloudinary.config( # we didnt pass the config to the app.config why?
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
    secure=True,
)