"""
State:          Tophe::InsectGeoState::1.0
State type:     tophe::InsectGeoState::1.0
Description:    Tophe::InsectGeoState::1.0
Author:         tophe
Date Created:   July 24, 2024 - 17:19:53
"""


import hou
import viewerstate.utils as su

class State(object):
    MSG = "LMB to add an instance point. Scroll to change pscale. Shift+Scroll to rotate. Shift+r to Reset"
    HUD_TEMPLATE = {
    "title": "Variant Painter", 
    "desc": "tool", "icon": "F:/HoudiniResources/Packages/MOPS/icons/mops_cloner_03.svg",
    "rows": [
        # {"id": "shape", "label": "Brush Shape", "key": "B / Shift B"},
        # {"id": "shape_g", "type": "choicegraph", "count": len(SHAPES)},
        # {"id": "mode", "label": "Mode", "key": "1-6"},
        # {"id": "mode_g", "type": "choicegraph", "count": len(MODES)},
        {"id": "pscale", "label": "Pscale", "key": "mousewheel"},
        {"id": "radius_g", "type": "bargraph"},
        # {"id": "frozen", "label": "Frozen", "key": "F"},
        # {"id": "setrest", "label": "Set rest state", "key": "H"},

        {"id": "modedev", "type": "divider"},
        {"id": "brush_act", "label": "Add Point", "key": "LMB"},
        # {"id": "sim_act", "label": "Simulate", "key": "Shift LMB"},
        {"id": "drag_act", "label": "Set pscale", "key": "mousewheel"},
        {"id": "add_act", "label": "Cycle Variants", "key": "Shift mousewheel"},
        {"id": "del_act", "label": "Rotate", "key": "Ctrl mousewheel"},
        
        {"id": "do_collision_label", "label": "Set Collision", "key": "Shift C"},
        {"id": "do_collision",  "type": "choicegraph", "value": 0 },
        {"id": "reset", "label": "Reset All", "key": "Shift R"},
    ]
}

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer
        
        #Node
        self.node = None
        #Parms
        self.mp = None
        self.inc = 0
        
        #Collision
        # self.gi.GeometryIntersector(hou.Geometry(), self.scene_viewer)
        self.collision_geo = hou.Geometry() #Abstract Class
        self.snapping = False
        self._snap_mode = None
        
        #Input
        self.key_pressed = None
        
        #InstanceAttributes
        self.active_pos = hou.Vector3(0,0,0)
        self.active_pscale = 1
        self.active_variant_id = 0
        self.active_angle = 0
        self.active_collide = 0
        
        self.variant_limits = {}
        self.scene_viewer.hudInfo(template=State.HUD_TEMPLATE)
    
    #$Life Cycle
    def onEnter(self,kwargs):
        """ Called on node bound states when it starts
        """
        self.scene_viewer.hudInfo(show = True)
        # Set the HUD with a template. This is normally done once during the state's lifetime. 
        # 

        # Update the HUD with new values
        # updates = {
        # "shape": self.current_spape_name,
        # "shape_g": self.all_shape_names.index(self.current_shape_name)
        # "mode": self.current_mode_name,
        # "mode_g": self.all_mode_names.index(self.current_mode_name),
        # "radius": "{:0.3f}".format(self.radius),
        # "radius_g": self.radius / self.max_radius,
        # "frozen": "true" if self.is_frozen else "false",
    # }
        # self.scene_viewer.hudInfo(values=updates)
    
                     
        self.node = kwargs["node"]
        state_parms = kwargs["state_parms"]
        
        #Multiparm
        self.mp = self.node.parm('mp')
        self.inc = self.mp.evalAsInt()
        if self.inc == 0:
            self.incrementMP()
        else:
            self.setNewParms()
            
        #Collision
        self.updateCollisionGeo()
        self._snap_mode = self.scene_viewer.snappingMode()
        
        #Messages
        self.scene_viewer.setPromptMessage( State.MSG )
        self.getVariantLimits()
        
    def onExit(self,kwargs):
        """ Called when the state terminates
        """
        state_parms = kwargs["state_parms"]


    def onMouseEvent(self, kwargs):
        """ Process mouse and tablet events
        """
        ui_event = kwargs["ui_event"]
        dev = ui_event.device()
        
        ray_origin, ray_dir = ui_event.ray()
        hit, pos, norm, uvw = su.sopGeometryIntersection(self.collision_geo, ray_origin, ray_dir)       

        if hit != -1:
            reason = ui_event.reason()

            inc = self.getInc()
            
           
            if reason == hou.uiEventReason.Picked:

                inc = self.getInc()
                self.node.parmTuple(f'pos{inc}').set(pos)
                self.node.parmTuple(f'norm{inc}').set(norm)                
                self.incrementMP()
                self.updateCollisionGeo()
                self.active_pos = pos
            elif reason == hou.uiEventReason.Changed:
                self.updateCollisionGeo()

                
            elif reason == hou.uiEventReason.Located:
                self.node.parmTuple(f'pos{inc}').set(pos)
                self.active_pos = pos
                self.node.parmTuple(f'norm{inc}').set(norm)
                

        


    def onMouseWheelEvent(self, kwargs):
        """ Process a mouse wheel event
        """

        ui_event = kwargs["ui_event"]
        state_parms = kwargs["state_parms"]

        device = ui_event.device()
        scroll = ui_event.device().mouseWheel()
        inc = self.getInc()
        if device.isCtrlKey():
            #set rotation
            new_value = self.node.parm(f"angle{inc}").evalAsFloat() + scroll
            self.node.parm(f"angle{inc}").set(new_value)
        elif device.isShiftKey():
            #set variant
            new_value = self.node.parm(f"variant_id{inc}").evalAsInt() + scroll
            self.node.parm(f"variant_id{inc}").set(new_value)
            self.testVariantLimits()
        else:
            #Set pscale
            new_value = self.node.parm(f"_pscale{inc}").evalAsFloat() + scroll/100
            self.node.parm(f"_pscale{inc}").set(new_value)
            self.testPscale()
        # Must return True to consume the event
        return False


    def onParmChangeEvent(self, kwargs):
        """ Implement this callback to react to state parameter changes. 
        """
        parm_name = kwargs["parm_name"]
        parm_value = kwargs["parm_value"]
        state_parms = kwargs["state_parms"]
        ui_event = kwargs["ui_event"]


    def onKeyEvent(self, kwargs):
        """ Called for processing a keyboard event
        """
        ## Log some key event info in the Viewer State Browser console
        # self.log( 'key string', ui_event.device().keyString() )
        # self.log( 'key value', ui_event.device().keyValue() )
        # self.log( 'isAutoRepeat', ui_event.device().isAutoRepeat() )
        
        ui_event = kwargs["ui_event"]
        state_parms = kwargs["state_parms"]
        self.log( 'key string', ui_event.device().keyString() )
        self.key_pressed = ui_event.device().keyString()
        if 'Shift+r' in self.key_pressed:
            self.resetMP()
            return True
        if 'Shift+c' in self.key_pressed:
            self.toggleCollideParm()
            
            
        # Must returns True to consume the event
        return False
    
    #Parm Methods
    def toggleCollideParm(self):
        inc = self.getInc()
        self.active_collide = not self.node.parm(f'do_collide{inc}').evalAsInt()
        self.node.parm(f'do_collide{inc}').set(self.active_collide)
        
        updates = {'do_collision' : self.active_collide}
        self.scene_viewer.hudInfo(hud_values=updates)
    
    def setNewParms(self):
        inc = self.getInc()
        self.node.parmTuple(f'pos{inc}').set(self.active_pos)
        self.node.parm(f'variant_id{inc}').set(self.active_variant_id)
        self.node.parm(f'angle{inc}').set(self.active_angle)
        self.node.parm(f'do_collide{inc}').set(self.active_collide)
        self.node.parm(f'_pscale{inc}').set(self.active_pscale)

    def setActiveParmValues(self):
        inc = self.getInc()

        self.active_variant_id = self.node.parm(f'variant_id{inc}').evalAsInt()
        self.active_angle = self.node.parm(f'angle{inc}').evalAsFloat()
        self.active_collide = self.node.parm(f'do_collide{inc}').evalAsInt()
        self.active_pscale = self.node.parm(f'_pscale{inc}').evalAsFloat()
        

    def logActiveValues(self):
        self.log(f'inc is {self.inc}')
        self.log(f'active variant is {self.active_variant_id}')
        self.log(f'angle is {self.active_angle}')
        self.log(f'collide is {self.active_collide}')
        self.log(f'pscale is {self.active_pscale}')
        
    #$Multiparm    
    def getInc(self):
        return self.mp.evalAsInt()
        
    def incrementMP(self):
        inc = self.getInc() + 1
        self.setActiveParmValues() 
        self.mp.set(inc)
        self.setNewParms()
        
    def decrementMP(self):
        inc = getInc() - 1
        self.mp.set(inc)    
    
    def resetMP(self):
        self.mp.set(1)
        self.node.parmTuple('pos1').set(hou.Vector3(0,0,0))
        self.node.parmTuple('norm1').set(hou.Vector3(0,0,0))
        self.node.parm('_pscale1').set(1)
        self.node.parm('angle1').set(0)
        self.node.parm('do_collide1').set(0)
    
    
    #$Collision
    def updateCollisionGeo(self):
        self.collision_geo = self.node.node('COLLISION').geometry().freeze()
        # self.collision_geo = self.node.node('COLLISION').geometry()
 
    def getVariantLimits(self):

        self.variant_limits['min'] = self.node.node('VARIANT_LIMITS').geometry().attribValue('min_variant')
        self.variant_limits['max'] = self.node.node('VARIANT_LIMITS').geometry().attribValue('max_variant')

    def testVariantLimits(self):
        inc = self.getInc()   

        parm_value = self.node.parm('variant_id1').evalAsInt()
        self.log(parm_value)
        if parm_value > self.variant_limits['max']:
            outlier = "higher than the maximum variant"
            msg = f"The current variant parameter is {outlier} attribute! Unable to copy variant to point."
            self.scene_viewer.setPromptMessage( msg,hou.promptMessageType.Warning )
        elif parm_value < self.variant_limits['min']:
            outlier = "lower than the minimum variant"
            msg = f"The current variant parameter is {outlier} attribute! Unable to copy variant to point."
            self.scene_viewer.setPromptMessage( msg,hou.promptMessageType.Warning )
        else:
            self.scene_viewer.clearPromptMessage()
            self.scene_viewer.setPromptMessage( State.MSG )
    def testPscale(self):
        if self.active_pscale == 0:
            msg = f"pscale is set to `0`."
            self.scene_viewer.setPromptMessage( msg,hou.promptMessageType.Warning )
        else:
            self.scene_viewer.clearPromptMessage()
            self.scene_viewer.setPromptMessage( State.MSG )       

            
        
def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state 
        template to register. """

    state_typename = kwargs["type"].definition().sections()["DefaultState"].contents()
    state_label = "Tophe::InsectGeoState::1.0"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)
    template.bindIcon(kwargs["type"].icon())


 

    template.bindNodeChangeEvent([hou.nodeEventType.ParmTupleChanged])


    return template
    
    
#$Graveyard
    # def onMouseEvent(self, kwargs):
    #     """ Process mouse and tablet events
    #     """
    #     snap_mode = self.scene_viewer.snappingMode()
    #     if snap_mode is hou.snappingMode.Off:
    #         self.sendRays(kwargs)
        
    #     else:
    #         self.sendSnappingRays(kwargs)
    #     # Must return True to consume the event

    #     return False
    # def sendRays(self, kwargs):
    #     ui_event = kwargs["ui_event"]
    #     dev = ui_event.device()
        
    #     ray_origin, ray_dir = ui_event.ray()
    #     self.hit, self.pos, self.norm, self.uvw = su.sopGeometryIntersection(self.collision_geo, ray_origin, ray_dir)       
        
    #     # return True
    # def sendSnappingRays(self,kwargs):

    #     ui_event = kwargs["ui_event"]
    #     snap_dict = ui_event.snappingRay()
        
    #     if snap_dict["snapped"] and snap_dict["geo_type"] == hou.snappingPriority.GeoPoint:
    #         self.pos = snap_dict['snap_pos']
    #         self.log(snap_dict["point_index"])
