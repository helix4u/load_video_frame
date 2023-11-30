from typing import Literal, Optional
import cv2
import json
import numpy as np
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter, ImageOps
from invokeai.app.invocations.primitives import ColorField, ImageField, ImageOutput, IntegerOutput
from pydantic import Field
from invokeai.app.services.image_records.image_records_common import ImageCategory, ResourceOrigin
from invokeai.app.invocations.baseinvocation import (
    BaseInvocation,
    BaseInvocationOutput,
    FieldDescriptions,
    Input,
    InputField,
    InvocationContext,
    OutputField,
    UIComponent,
    UIType,
    WithMetadata,
    WithWorkflow,
    invocation,
    invocation_output,
)

"""
Note: I always hate code breaking changes! XD
If work need to be made for others, clarity on when and why the change is going to be made and the advantages of the change for the user-base of the product would be cool. Otherwise it kinda just seems like we are just iterating for the sake of iterating. I don't live in the code and so consolidating docs into something digestable for someone not directly involved in the day to day project upkeep may be advantagious to maintain so that contributers can understand the changes without having to search a lot of text or find a thread. Somewhere that knowledge is consolidated in a presentation manner instead of tucked away beneath discord conversation and site fractured documantation stores.
"""

@invocation(
    "LoadVideoFrameInvocation", 
    title="Load Video Frame", 
    tags=["video", "load", "frame"], 
    category="image",
    version="1.0.1",
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
    version="1.0.1",
)
class ImageIndexCollectInvocation(BaseInvocation):
    """ImageIndexCollect takes Image and Index then outputs it as an (index,image_name)array converted to json"""
    index: int = InputField(default=0, description="The index")
    image: ImageField = InputField(default=None, description="The image associated with the index")

    def invoke(self, context: InvocationContext) -> ImageIndexCollectOutput:
        """Invoke with provided services and return outputs."""
        return ImageIndexCollectOutput(image_index_collection = json.dumps([self.index , self.image.image_name]))

@invocation_output("ImagesIndexToVideoOutput")  
class ImagesIndexToVideoOutput(BaseInvocationOutput):
    """ImagesIndexToVideoOutput returns nothing"""

@invocation(
    "ImagesIndexToVideoOutput", 
    title="Images Index To Video Output", 
    tags=["video", "collection", "image", "index", "frame", "collection"], 
    category="collections",
    version="1.0.1",
)
class ImagesIndexToVideoInvocation(BaseInvocation):#, PILInvocationConfig):
    """Load a collection of xyimage types (json of (x_item,y_item,image_name)array) and create a gridimage of them"""
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
    version="1.0.1",
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
    version="1.0.1",
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

@invocation_output("ImageToImageNameOutput")
class ImageToImageNameOutput(BaseInvocationOutput):
    """Output class for Image to Image Name Invocation"""
    image_name: str = OutputField(description="The name of the image")

@invocation(
    "ImageToImageNameInvocation",
    title="Image to Image Name",
    tags=["image", "name", "utility"],
    category="utility",
    version="1.0.0",
)
class ImageToImageNameInvocation(BaseInvocation):
    """Invocation to extract the image name from an ImageField."""

    # Input
    image: ImageField = InputField(description="The ImageField to extract the name from")

    def invoke(self, context: InvocationContext) -> ImageToImageNameOutput:
        """Invoke method to extract the image name."""
        # Extract the image name
        image_name = self.image.image_name

        # Return the image name in the output
        return ImageToImageNameOutput(image_name=image_name)
