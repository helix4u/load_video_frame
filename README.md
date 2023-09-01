# Load Video Frame

This is a video frame image provider + indexer/video creation nodes for hooking up to iterators and ranges and ControlNets and such for [invokeAI](https://github.com/invoke-ai/InvokeAI) node experimentation >
Think animation + ControlNet outputs.

# Caveats: 
> Pick the correct versions to try... 
> There have changes in how nodes and workflows work since original publication, so version matters and **MUST MATCH**.

A high number of frames may cause a bit of time to create with the example workflow. I'd stick to smaller batches of frames at first and slowly ramp up to find a length of time you're willing to wait for the task to start/complete.

# Tips: 
Render every other frame and then interpolate the in-between frames with something like RIFE or FILM for some more smoothing and a lot less rendering time.

Feel free to contribute or take ispiration for your own ideas and thanks to those who already have!

[Example 3.0 Workflow](Example_Workflow.json):
![Example_Workflow](https://i.imgur.com/GuwNHN8.png)
[Invoke AI Discord Thread](https://discord.com/channels/1020123559063990373/1136905319839174728)

<a href='https://ko-fi.com/gille' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' />
