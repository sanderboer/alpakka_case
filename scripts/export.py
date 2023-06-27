import bpy
import math
from pathlib import Path

context = bpy.context
scene = context.scene
viewlayer = context.view_layer

class Entry:
    def __init__(
            self, col_name, stl_name, axis_up='Z', axis_forward='Y', merge=False,
            multiple=False, transformation=None, tolerance=False):
        self.col_name = col_name
        self.stl_name = stl_name
        self.axis_up = axis_up
        self.axis_forward = axis_forward
        self.merge = merge
        self.multiple = multiple
        self.transformation = transformation
        self.tolerance = tolerance

    @staticmethod
    def find(name):
        for entry in entries:
            if entry.col_name == name:
                return entry

    def process(self, tolerance=False):
        bpy.ops.object.select_all(action='DESELECT')
        if tolerance:
            self.make_loose()
        obs = [o for o in scene.objects if o.type == 'MESH']
        for ob in obs:
            if not ob.visible_get(): continue
            viewlayer.objects.active = ob
            ob.select_set(True)
            if self.transformation:
                self.transformation(ob)
            if not self.merge:
                if self.multiple:
                    subentry = Entry.find(ob.name)
                    subentry.export()
                else:
                    self.export()
                ob.select_set(False)
        if self.merge:
            self.export()

    def make_loose(self):
        obs = [o for o in scene.objects if o.type == 'MESH']
        for ob in obs:
            for mod in ob.modifiers:
                if mod.name == 'Tolerance loose':
                    mod.show_viewport = True

    def export(self):
        root = Path(bpy.path.abspath("//")).parent
        path = root / 'stl' / f'{self.stl_name}.stl'
        bpy.ops.export_mesh.stl(
            filepath=str(path),
            use_selection=True,
            axis_up=self.axis_up,
            axis_forward=self.axis_forward)


def rotation(ob, x=0, y=0, z=0):
    if x: ob.rotation_euler.x = math.radians(x)
    if y: ob.rotation_euler.y = math.radians(y)
    if z: ob.rotation_euler.z = math.radians(z)


entries = [
    Entry('Case front',       'primary_015mm_front'),
    Entry('R1',               'primary_015mm_triggersR1'),
    Entry('R2',               'primary_015mm_triggersR2', '-Z'),
    Entry('R4',               'primary_015mm_triggersR4', '-Y', '-Z'),
    Entry('DHat',             'primary_015mm_dhat_(brim)'),
    Entry('Select',           'primary_007mm_select'),
    Entry('Case back',        'secondary_015mm_back', '-Z'),
    Entry('Case cover',       'secondary_015mm_cover'),
    Entry('Wheel',            'secondary_015mm_wheel', 'X'),
    Entry('Wheel shaft R',    'secondary_015mm_wheelshaft'),
    Entry('Abxy',             'secondary_007mm_abxy'),
    Entry('Dpad',             'secondary_007mm_dpad'),
    Entry('Thumbstick',       'secondary_007mm_thumbstick_(support)'),
    Entry('Home',             'secondary_007mm_home_(support)', transformation=lambda ob: rotation(ob, -8.4)),
    Entry('Hexagon',          'conductive_015mm_hexagon', '-Z', tolerance=True),
    Entry('Wheel support',    'any_015mm_wheelholder'),
    Entry('Anchor',           'any_015mm_anchors_(brim)', '-Z'),
    Entry('Soldering helper', 'any_020mm_solderstand', '-Z', merge=True),
    Entry('Scrollwheel', None, multiple=True),
]

for collection in bpy.data.collections:
    entry = Entry.find(collection.name)
    entry.process()
    if entry.tolerance:
        entry.stl_name = f'loose_variants/{entry.stl_name}_loose'
        entry.process(tolerance=True)
    break
