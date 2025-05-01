def getDefaultSceneViewer():
    return hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)

def setCamera(camera, scene_viewer = None):
    """Will use the first found scene viewer if scene_viewer arg is None"""
    if scene_viewer is None:
        scene_viewer = getDefaultSceneViewer()
    cv = scene_viewer.curViewport()
    
    #if user provides am absolute path string to the camera, turn it into a node ref
    if isinstance(camera, str):
        camera = hou.node(camera)
    cv.setCamera(camera)

#UI For keyboard shortcuts
#toggles
def toggleOperationsBar(scene_viewer = None):
    if scene_viewer is None:
        scene_viewer = getDefaultSceneViewer()
    scene_viewer.showOperationBar(not sv.isShowingOperationBar())

def toggleshowSelectionBar(scene_viewer = None):
    if scene_viewer is None:
        scene_viewer = getDefaultSceneViewer()
    scene_viewer.showSelectionBar(not sv.isShowingSelectionBar())

def toggleshowDisplayBar(scene_viewer = None):
    if scene_viewer is None:
        scene_viewer = getDefaultSceneViewer()
    scene_viewer.showDisplayBar(not sv.isShowingDisplayBar())

    
#display settings

def toggleHDRILight(scene_viewer = None):
    if scene_viewer is None:
        scene_viewer = getDefaultSceneViewer()
    settings = scene_viewer.curViewport().settings()
    settings.setDisplayEnvironmentBackgroundImage(not settings.displayEnvironmentBackgroundImage())
    
def cycleColorScheme(scene_viewer = None):
    if scene_viewer is None:
        scene_viewer = getDefaultSceneViewer()

    settings = scene_viewer.curViewport().settings()
    menuTargets = {hou.viewportColorScheme.Light : hou.viewportColorScheme.Dark, 
                        hou.viewportColorScheme.Dark : hou.viewportColorScheme.Grey, 
                        hou.viewportColorScheme.Grey : hou.viewportColorScheme.DarkGrey,
                        hou.viewportColorScheme.DarkGrey : hou.viewportColorScheme.Light}
    
    settings.setColorScheme(menuTargets[settings.colorScheme()])




sv.showOperationBar(1)