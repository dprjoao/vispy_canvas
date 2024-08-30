
from vispy import io
from vispy.util import keys
from vispy.gloo.util import _screenshot

from .xyz_axis import XYZAxis
from .axis_aligned_image import AxisAlignedImage

class CanvasControls:
    def on_mouse_press(self, event):
        # Hold <Ctrl> to enter drag mode or press <d> to toggle.
        if keys.CONTROL in event.modifiers or self.drag_mode:
            # Temporarily disable the interactive flag of the ViewBox because it
            # is masking all the visuals. See details at:
            # https://github.com/vispy/vispy/issues/1336
            self.view.interactive = False
            hover_on = self.visual_at(event.pos)

            if event.button == 1 and self.selected is None:
                # If no previous selection, make a new selection if cilck on a valid
                # visual node, and highlight this node.
                if hover_on is not None:
                    self.selected = hover_on
                    self.selected.highlight.visible = True
                    # Set the anchor point on this node.
                    self.selected.set_anchor(event)
            # Nothing to do if the cursor is NOT on a valid visual node.
            # Reenable the ViewBox interactive flag.
            self.view.interactive = True

    def on_mouse_release(self, event):
        # Hold <Ctrl> to enter drag mode or press <d> to toggle.
        if keys.CONTROL in event.modifiers or self.drag_mode:
            if self.selected is not None:
                # Erase the anchor point on this node.
                self.selected.anchor = None
                # Then, deselect any previous selection.
                self.selected = None

    def on_mouse_move(self, event):
        # Hold <Ctrl> to enter drag mode or press <d> to toggle.
        if keys.CONTROL in event.modifiers or self.drag_mode:
            # Temporarily disable the interactive flag of the ViewBox because it
            # is masking all the visuals. See details at:
            # https://github.com/vispy/vispy/issues/1336
            self.view.interactive = False
            hover_on = self.visual_at(event.pos)

            if event.button == 1:
                if  self.selected is not None:
                    self.selected.drag_visual_node(event)
            else:
                # If the left cilck is released, update highlight to the new visual
                # node that mouse hovers on.
                if hover_on != self.hover_on:
                    if self.hover_on is not None: # de-highlight previous hover_on
                        self.hover_on.highlight.visible = False
                    self.hover_on = hover_on
                    if self.hover_on is not None: # highlight the new hover_on
                        self.hover_on.highlight.visible = True

            # Reenable the ViewBox interactive flag.
            self.view.interactive = True

    def on_key_press(self, event):
        # Hold <Ctrl> to enter drag mode.
        if keys.CONTROL in event.modifiers:
            # TODO: I cannot get the mouse position within the key_press event ...
            # so it is not yet implemented. The purpose of this event handler
            # is simply trying to highlight the visual node when <Ctrl> is pressed
            # but mouse is not moved (just nicer interactivity), so not very
            # high priority now.
            pass
        # Press <Space> to reset camera.
        if event.text == ' ':
            self.camera.fov = self.fov
            self.camera.azimuth = self.azimuth
            self.camera.elevation = self.elevation
            self.camera.set_range()
            self.camera.scale_factor = self.scale_factor
            self.camera.scale_factor /= self.zoom_factor
            for child in self.view.children:
                if type(child) == XYZAxis:
                    child._update_axis()
        # Press <s> to save a screenshot.
        if event.text == 's':
            screenshot = _screenshot()
            io.write_png(self.title + '.png', screenshot)

        # Press <d> to toggle drag mode.
        if event.text == 'd':
            if not self.drag_mode:
                self.drag_mode = True
                self.camera.viewbox.events.mouse_move.disconnect(
                self.camera.viewbox_mouse_event)
            else:
                self.drag_mode = False
                self._exit_drag_mode()
                self.camera.viewbox.events.mouse_move.connect(
                self.camera.viewbox_mouse_event)
                
        # Press <a> to get the parameters of all visual nodes.
        if event.text == 'a':
            print("===== All useful parameters ====")
            # Canvas size.
            print("Canvas size = {}".format(self.size))
            # Collect camera parameters.
            print("Camera:")
            camera_state = self.camera.get_state()
            for key, value in camera_state.items():
                print(" - {} = {}".format(key, value))
            print(" - {} = {}".format('zoom factor', self.zoom_factor))
            # Collect slice parameters.
            print("Slices:")
            pos_dict = {'x':[], 'y':[], 'z':[]}
            for node in self.view.scene.children:
                if type(node) == AxisAlignedImage:
                    pos = node.pos
                    if node.seismic_coord_system and node.axis in ['y', 'z']:
                        pos = node.limit[1] - pos # revert y and z axis
                    pos_dict[node.axis].append(pos)
            for axis, pos in pos_dict.items():
                print(" - {}: {}".format(axis, pos))
                # Collect the axis legend parameters.
            for node in self.view.children:
                if type(node) == XYZAxis:
                    print("XYZAxis loc = {}".format(node.loc))

    def on_key_release(self, event):
        # Cancel selection and highlight if release <Ctrl>.
        if keys.CONTROL not in event.modifiers:
            self._exit_drag_mode()

    def _exit_drag_mode(self):
        if self.hover_on is not None:
            self.hover_on.highlight.visible = False
            self.hover_on = None
        if self.selected is not None:
            self.selected.highlight.visible = False
            self.selected.anchor = None
            self.selected = None