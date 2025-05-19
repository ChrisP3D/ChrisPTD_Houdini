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
#toggle UI
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



def getSceneGeo():
    """Get the display model settings object from the current Scene Viewer."""
    scene_viewer = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.SceneViewer)
    settings = scene_viewer.curViewport().settings()
    return settings.displaySet(hou.displaySetType.DisplayModel)


def togglePointMarkers():
    geo = getSceneGeo()
    geo.showPointMarkers(not geo.isShowingPointMarkers())


def togglePointNormals():
    geo = getSceneGeo()
    vert_normals = geo.isShowingVertexNormals()
    point_normals = geo.isShowingPointNormals()
    for norm in (vert_normals, point_normals):
        geo.showPointNormals(not norm)
        geo.showVertexNormals(not norm)


def togglePointNumbers():
    geo = getSceneGeo()
    geo.showPointNumbers(not geo.isShowingPointNumbers())


def togglePointTrails():
    geo = getSceneGeo()
    geo.showPointTrails(not geo.isShowingPointTrails())


def togglePrimNumbers():
    geo = getSceneGeo()
    geo.showPrimNumbers(not geo.isShowingPrimNumbers())


def togglePrimNormals():
    geo = getSceneGeo()
    geo.showPrimNormals(not geo.isShowingPrimNormals())


def toggleUVMarkers():
    geo = getSceneGeo()
    geo.showUVMarkers(not geo.isShowingUVMarkers())


def turnOffAllVisualizers():
    geo = getSceneGeo()
    geo.showPointMarkers(False)
    geo.showPointNormals(False)
    geo.showVertexNormals(False)
    geo.showPointNumbers(False)
    geo.showPointTrails(False)
    geo.showPrimNumbers(False)
    geo.showPrimNormals(False)
    geo.showUVMarkers(False)
