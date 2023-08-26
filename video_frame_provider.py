from typing import Literal, Optional
from PIL import Image
import cv2
import json
import numpy as np

from pydantic import Field
from ..models.image import (
    ImageCategory,
    ImageField,
    ResourceOrigin,
    ImageOutput,
)
from .baseinvocation import (
    BaseInvocation,
    InvocationContext,
    InvocationConfig,
    BaseInvocationOutput,
)


class LoadVideoFrameInvocation(BaseInvocation):
    """Load a specific frame from an MP4 video and provide it as output."""

    # fmt: off
    type: Literal["load_video_frame"] = "load_video_frame"

    # Inputs
    video_path: str = Field(description="The path to the MP4 video file")
    frame_number: int = Field(default=1, description="The frame number to load")
    # fmt: on

    class Config(InvocationConfig):
        schema_extra = {
            "ui": {"title": "Load Video Frame", "tags": ["video", "load", "frame"]},
        }

    def invoke(self, context: InvocationContext) -> ImageOutput:
        # Open the video file
        video = cv2.VideoCapture(self.video_path)

        # Set the frame position
        video.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number)

        # Read the frame
        ret, frame = video.read()

        # Close the video file
        video.release()

        if not ret:
            raise Exception(f"Failed to read frame {self.frame_number} from video {self.video_path}")

        # Convert the frame to a PIL Image
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Create the ImageField object
        image_dto = context.services.images.create(
            image=image,
            image_origin=ResourceOrigin.INTERNAL,
            image_category=ImageCategory.GENERAL,
            node_id=self.id,
            session_id=context.graph_execution_state_id,
            is_intermediate=self.is_intermediate,
        )

        return ImageOutput(
            image=ImageField(image_name=image_dto.image_name),
            width=image_dto.width,
            height=image_dto.height,
        )


class ImageIndexCollectOutput(BaseInvocationOutput):
    """XImageCollectOutput string containg an array of xItem, Image_name converted to json"""
    type: Literal["image_index_collect_output"] = "image_index_collect_output"
    image_index_collection: str = Field(description="The Image Index Collection ")

    class Config:
        schema_extra = {'required': ['type','ximage']}

class ImageIndexCollectInvocation(BaseInvocation):
    """ImageIndexCollect takes Image and Index then outputs it as an (index,image_name)array converted to json"""
    type: Literal["image_index_collect"] = "image_index_collect"
    index: int = Field(default=0, description="The index")
    image: ImageField = Field(default=None, description="The image associated with the index")

    class Config(InvocationConfig):
        schema_extra = {"ui": {"title": "Image Index Collect"}}

    def invoke(self, context: InvocationContext) -> ImageIndexCollectOutput:
        """Invoke with provided services and return outputs."""
        return ImageIndexCollectOutput(image_index_collection = json.dumps([self.index , self.image.image_name]))
    

class ImagesIndexToVideoOutput(BaseInvocationOutput):
    """ImagesIndexToVideoOutput returns nothing"""
    type: Literal["image_index_to_video_output"] = "image_index_to_video_output"

    class Config:
        schema_extra = {'required': ['type']}  

class ImagesIndexToVideoInvocation(BaseInvocation):#, PILInvocationConfig):
    """Load a collection of xyimage types (json of (x_item,y_item,image_name)array) and create a gridimage of them"""
    type: Literal["image_index_to_video"] = "image_index_to_video"
    image_index_collection: list[str] = Field(default=[], description="The Image Index Collection")
    video_out_path: str = Field(default='', description="Path and filename of output mp4")
    fps: int = Field(default=30, description="FPS")

    class Config(InvocationConfig):
        schema_extra = {"ui": {"title": "Image Index To Video"}}
  
    def invoke(self, context: InvocationContext) -> ImagesIndexToVideoOutput:
        """Convert an image list a video"""

        new_array = sorted([json.loads(s) for s in self.image_index_collection], key=lambda x: x[0])
        image = context.services.images.get_pil_image(new_array[0][1])
        
        video_writer = cv2.VideoWriter(self.video_out_path, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, (image.width, image.height))

        for item in new_array:
            image = context.services.images.get_pil_image(item[1])
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            video_writer.write(image)

        video_writer.release()

        return ImagesIndexToVideoOutput()
