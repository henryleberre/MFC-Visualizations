import os
import os.path
import argparse

print(f" -- Initialize")
print(f"    -- Loading Paraview...")

from paraview.simple import *

paraview.simple._DisableFirstRenderCameraReset()

print(f"    -- Parse Arguments...")

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input",  help="Path to silo_hdf5",      type=str)
parser.add_argument("-o", "--output", help="Frame output directory", type=str)
parser.add_argument("-W", "--width",  help="Width (px)",             type=int)
parser.add_argument("-H", "--height", help="Height (px)",            type=int)
args = parser.parse_args()


root_dirpath=os.path.abspath(os.sep.join([args.input, "root"]))

ts=[]
for filename in os.listdir(root_dirpath):
    ts.append(int(filename.replace('collection_', '').replace('.silo', '')))

filepaths = []
for t in sorted(ts):
    filepaths.append(os.sep.join([root_dirpath, f"collection_{t}.silo"]))

tBegin,tEnd=0,len(filepaths)-1
print(f"    -- Located {len(filepaths)} files: t={tBegin}..{tEnd}")

print(f" -- Setup Scene...")

print(f"    -- VisItSiloReader...")
collection_ = VisItSiloReader(registrationName='collection_*', FileName=filepaths)
collection_.MeshStatus      = ['rectilinear_grid']
collection_.CellArrayStatus = ['alpha2', 'pres']


print(f"    -- GetAnimationScene...")
animationScene1 = GetAnimationScene()
animationScene1.UpdateAnimationUsingDataTimeSteps()


print(f"    -- GetActiveViewOrCreate...")
renderView1 = GetActiveViewOrCreate('RenderView')
renderView1.Background = [1.0, 1.0, 1.0]
renderView1.UseColorPaletteForBackground = 0


print(f"    -- Threshold...")
threshold1 = Threshold(registrationName='Threshold1', Input=collection_)
threshold1.Scalars = ['CELLS', 'alpha2']
threshold1.UpperThreshold = 1.0
threshold1.LowerThreshold = 0.95

print(f"    -- ExtractSurface...")
extractSurface1 = ExtractSurface(registrationName='ExtractSurface1', Input=threshold1)

print(f"    -- Smooth...")
smooth1 = Smooth(registrationName='Smooth1', Input=extractSurface1)
smooth1.NumberofIterations = 500

print(f"    -- Smooth::Show...")
smooth1Display = Show(smooth1, renderView1, 'GeometryRepresentation')
smooth1Display.AmbientColor = [0.0, 0.6666666666666666, 0.4980392156862745]
smooth1Display.DiffuseColor = [0.0, 0.6666666666666666, 0.4980392156862745]

print(f"    -- Slice...")
slice1 = Slice(registrationName='Slice1', Input=collection_)
slice1.SliceType = 'Plane'
slice1.HyperTreeGridSlicer = 'Plane'
slice1.SliceOffsetValues = [0.0]
slice1.SliceType.Origin = [0.5, 0.5, 0.5] # init the 'Plane' selected for 'SliceType'
slice1.HyperTreeGridSlicer.Origin = [0.5, 0.5, 0.5] # init the 'Plane' selected for 'HyperTreeGridSlicer'
slice1.SliceType.Origin = [0.5, 0.5, 0.01]
slice1.SliceType.Normal = [0.0, 0.0, 1.0]

print(f"    -- Slice::Show...")
slice1Display = Show(slice1, renderView1, 'GeometryRepresentation')

ColorBy(slice1Display, ('CELLS', 'pres'))

slice1Display.RescaleTransferFunctionToDataRange()
slice1Display.SetScalarBarVisibility(renderView1, False)

presLUT = GetColorTransferFunction('pres')
presPWF = GetOpacityTransferFunction('pres')

slice1Display.SetScalarBarVisibility(renderView1, False)

presLUT.ApplyPreset('Cool to Warm', True)
presLUT.RescaleTransferFunctionToDataRange()
presPWF.RescaleTransferFunctionToDataRange()

print("    -- Camera...")

renderView1.CameraPosition = [
    2.4865321746026474,
    1.2779948204175584,
    1.4973212057509766,
]

renderView1.CameraFocalPoint = [
    0.488354302970065,
    0.521430160774283,
    0.014759905472983
]

renderView1.CameraViewUp = [
    -0.473695660569662,
    -0.340500634876452,
    0.8122017845376877
]

renderView1.CenterOfRotation = [
    0.4999999925494194,
    0.4999999925494194,
    0.0100000002421438
]

renderView1.CameraParallelScale       = 0.44748450634427417
renderView1.CameraParallelProjection  = 1
renderView1.OrientationAxesVisibility = 0

print("    -- GetLayout...")

layout1 = GetLayout()
layout1.SetSize(args.width, args.height)

print(f"    -- SetActiveSource...")
SetActiveSource(collection_)

print(f"  -- Render...")
SetActiveSource(collection_)

if not os.path.exists(args.output):
    os.mkdir(args.output)

for t in range(tBegin, tEnd+1):
    print(f"    -- t={t:04}... {int(100*(t-tBegin)/(tEnd-tBegin))}%")

    animationScene1.AnimationTime = t
    SaveScreenshot(
        os.sep.join([
            os.path.abspath(args.output),
            f"frame{t:04}.png"
        ]),
        renderView1
    )

# save animation
# SaveAnimation(
#     os.sep.join([os.path.abspath(args.output), "frame.png"]),
#     renderView1,
#     ImageResolution=[args.width, args.height],
#     FrameWindow=[tBegin, tEnd]
# )
