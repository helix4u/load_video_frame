from typing import Literal, Optional
from PIL import Image
import cv2
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
