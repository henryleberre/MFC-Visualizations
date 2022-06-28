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

filepaths = [
    os.path.abspath(os.path.join(f"{args.input}/root", filename)) for filename in os.listdir(f"{args.input}/root")
]

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
smooth1Display.OSPRayScaleFunction.Points = [88778.1059934707, 0.0, 0.5, 0.0, 248758.5670000251, 1.0, 0.5, 0.0]
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
slice1Display.OSPRayScaleFunction.Points = [88778.1059934707, 0.0, 0.5, 0.0, 248758.5670000251, 1.0, 0.5, 0.0]

ColorBy(slice1Display, ('CELLS', 'pres'))

slice1Display.RescaleTransferFunctionToDataRange(True, False)
slice1Display.SetScalarBarVisibility(renderView1, False)

presLUT = GetColorTransferFunction('pres')
presPWF = GetOpacityTransferFunction('pres')

slice1Display.SetScalarBarVisibility(renderView1, False)

presLUT.ApplyPreset('Cool to Warm', True)
presLUT.RGBPoints = [101324.45136132241, 0.23137254902, 0.298039215686, 0.752941176471, 101332.72568066121, 0.5098039215686274, 0.6470588235294118, 0.984313725490196, 101332.72568066121, 0.865, 0.865, 0.865, 101332.78125, 0.9686274509803922, 0.6627450980392157, 0.5450980392156862, 101341.0, 0.705882352941, 0.0156862745098, 0.149019607843]

presLUT.RescaleTransferFunction(-1000.0, 1000000.0)
presPWF.RescaleTransferFunction(-1000.0, 1000000.0)

print("    -- Camera...")

renderView1.CameraPosition      = [-0.6483354062224631, -1.4821377484240263, 1.1946868818785603]
renderView1.CameraFocalPoint    = [0.5401537335192009,  0.45586146097184693, 0.14008397033907388]
renderView1.CameraViewUp        = [0.12344579326116971, 0.4148529769175945, 0.9014755369219568]
renderView1.CameraParallelScale = 0.6486262778710543
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
    print(f"    -- t={t}... {int(100*(t-tBegin)/(tEnd-tBegin))}%")

    animationScene1.AnimationTime = t
    SaveScreenshot(
        os.sep.join([
            os.path.abspath(args.output),
            f"frame{t}.png"
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
