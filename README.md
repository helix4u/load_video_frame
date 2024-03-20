# 4.0.0rc4 Updates

Mostly we needed to update the fields imports, such as InputField and OutputField, as they are now apart of as invocations.fields rather than invocations.baseinvocation. 
I removed some unnessary/unused imports while at it.

All instances of context.services were converted to context._services
graph_execution_state_id was switched to _data.queue_item.session_id in the LoadVideoFrameInvocation invoke() method

The ImagesIndexToVideoOutput image_index_collection ui_type was updated to _Collection and default_factory was removed, as they were giving deprication warnings.

Both LoadVideoFrameInvocation and ImagesIndexToVideoOutput have been updated to version 1.0.2

# Info
[Original/ Main Repo](https://github.com/helix4u/load_video_frame)

This community node is developed and maintained by [helix4u/Gille] (https://github.com/helix4u)

