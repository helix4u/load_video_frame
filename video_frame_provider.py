from typing import Literal, Optional
import cv2
import json
import numpy as np
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter, ImageOps
from invokeai.app.invocations.primitives import ColorField, ImageField, ImageOutput, IntegerOutput
from pydantic import Field
from ..models.image import ImageCategory, ResourceOrigin
from .baseinvocation import BaseInvocation, FieldDescriptions, InputField, InvocationContext, invocation, BaseInvocationOutput, UIComponent, invocation_output, OutputField, UIType

"""
ImagesIndexToVideoInvocation and it's output still need to be sorted out but does function as-is.

Notes: 

the @invocation decorator replaces  type: Literal.
it's first argument is that value.
for example, @invocation("load_video_frame" technically is the same as type: Literal but more succinct and lets us change any implementation details as needed without impacting functionality of the node.
same for outputs.

use @invocation_output("output_type") ()) instead of type

class Config is totally replaced by the decorator. you can omit this on all nodes.

suggest to include workflow=self.workflow in the call to context.services.images.create(). this allows the images created by that node to embed the workflow into them. this checkbox will be displayed on every node that outputs an image

all outputs should use OutputField instead of Field

Todo:
Translate ImagesIndexToVideoOutput and it's output into invocation decorator speak using notes and links as context:

links for reading the how:
invokeai/app/invocations/primitives.py
invokeai/app/invocations/baseinvocation.py
a.k.a. if it doesnt make sense, just go look at working examples and adapt from there.
"""

@invocation(
    "LoadVideoFrameInvocation", 
    title="Load Video Frame", 
    tags=["video", "load", "frame"], 
    category="image",
    version="1.0.0",
)
class LoadVideoFrameInvocation(BaseInvocation):
    """Load a specific frame from an MP4 video and provide it as output."""
    # Inputs
    video_path: str = InputField(description="The path to the MP4 video file")
    frame_number: int = InputField(default=1, ge=1, description="The frame number to load")

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
            workflow=self.workflow,
        )

        return ImageOutput(
            image=ImageField(image_name=image_dto.image_name),
            width=image_dto.width,
            height=image_dto.height,
        )



@invocation_output("image_index_collect_output")
class ImageIndexCollectOutput(BaseInvocationOutput):
    """XImageCollectOutput string containing an array of xItem, Image_name converted to json"""
    image_index_collection: str = OutputField(description="The Image Index Collection ")

@invocation(
    "ImageIndexCollectInvocation", 
    title="Image Index Collect", 
    tags=["video", "collection", "image", "index", "frame", "collection"], 
    category="collections",
    version="1.0.0",
)
class ImageIndexCollectInvocation(BaseInvocation):
    """ImageIndexCollect takes Image and Index then outputs it as an (index,image_name)array converted to json"""
    type: Literal["image_index_collect"] = "image_index_collect"
    index: int = InputField(default=0, description="The index")
    image: ImageField = InputField(default=None, description="The image associated with the index")

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
    image_index_collection: list[str] = InputField(default_factory=list, description="The Image Index Collection", ui_type=UIType.ImageCollection)
    video_out_path: str = InputField(default='', description="Path and filename of output mp4")
    fps: int = InputField(default=30, description="FPS")

  
    def invoke(self, context: InvocationContext) -> ImagesIndexToVideoOutput:
        """Convert an image list a video"""
        new_array = sorted([json.loads(s) for s in self.image_index_collection], key=lambda x: x[0])
        image = context.services.images.get_pil_image(new_array[0][1])
        
        video_writer = cv2.VideoWriter(self.video_out_path, cv2.VideoWriter_fourcc(*'X264'), self.fps, (image.width, image.height))

        for item in new_array:
            image = context.services.images.get_pil_image(item[1])
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            video_writer.write(image)

        video_writer.release()

        return ImagesIndexToVideoOutput()
 
 
@invocation(
    "GetTotalFramesInvocation", 
    title="Get Total Frames", 
    tags=["video", "frames", "count"], 
    category="video",
    version="1.0.0",
)
class GetTotalFramesInvocation(BaseInvocation):
    """Get the total number of frames in an MP4 video and provide it as output."""
    
    # Inputs
    video_path: str = InputField(description="The path to the MP4 video file")

    def invoke(self, context: InvocationContext) -> IntegerOutput:
        # Open the video file
        video = cv2.VideoCapture(self.video_path)
        
        # Get the total number of frames
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Close the video file
        video.release()

        return IntegerOutput(value=total_frames)
        
@invocation(
    "GetSourceFrameRateInvocation", 
    title="Get Source Frame Rate", 
    tags=["video", "framerate"], 
    category="video",
    version="1.0.0",
)
class GetSourceFrameRateInvocation(BaseInvocation):
    """Get the source framerate of an MP4 video and provide it as output."""
    
    # Inputs
    video_path: str = InputField(description="The path to the MP4 video file")

    def invoke(self, context: InvocationContext) -> IntegerOutput:
        # Open the video file
        video = cv2.VideoCapture(self.video_path)
        
        # Get the source framerate
        framerate = int(video.get(cv2.CAP_PROP_FPS))
        
        # Close the video file
        video.release()

        return IntegerOutput(value=framerate)
