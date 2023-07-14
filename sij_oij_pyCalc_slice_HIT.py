# state file generated using paraview version 5.9.0

#### import the simple module from the paraview
from paraview.simple import *
import numpy as np
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'EnSight Reader'
artscase = EnSightReader(registrationName='arts.case', CaseFileName='/scratch/sverma/aish_enstrophy/hit/generateEnstrophy/ensDir/arts.case')
artscase.PointArrays = ['U', 'V', 'W', 'P', 'BCH']


dataset = servermanager.Fetch(artscase)

yStart = dataset.GetBlock(0).GetPoint(0)[1]
yEnd = dataset.GetBlock(0).GetPoint(255*255 - 1)[1] # -1 becoz very last plane excluded
numPlanes = 100
yTargets = np.linspace(yStart, yEnd, numPlanes)
print(yTargets)

# create a new 'Calculator'
calculator1 = Calculator(registrationName='Calculator1', Input=artscase)
calculator1.ResultArrayName = 'velVec'
calculator1.Function = 'U*iHat + V*jHat + W*kHat'

# create a new 'Compute Derivatives'
computeDerivatives1 = ComputeDerivatives(registrationName='ComputeDerivatives1', Input=calculator1)
computeDerivatives1.Scalars = ['POINTS', '']
computeDerivatives1.Vectors = ['POINTS', 'velVec']
computeDerivatives1.OutputVectorType = 'Vorticity'
computeDerivatives1.OutputTensorType = 'Strain'

# create a new 'Calculator'
vortMagSquaredHalf = Calculator(registrationName='vortMagSquaredHalf', Input=computeDerivatives1)
vortMagSquaredHalf.AttributeType = 'Cell Data'
vortMagSquaredHalf.ResultArrayName = 'vortMagSquaredHalf'
vortMagSquaredHalf.Function = '0.5*(mag(Vorticity))^2'

# create a new 'Slice'
sliceOmegaOmega = Slice(registrationName='SliceOmegaOmega', Input=vortMagSquaredHalf)
sliceOmegaOmega.SliceType = 'Plane'
sliceOmegaOmega.HyperTreeGridSlicer = 'Plane'
sliceOmegaOmega.SliceOffsetValues = [0.0]
sliceOmegaOmega.SliceType.Normal = [0.0, 1.0, 0.0]

# create a new 'Calculator'
sijSij = Calculator(registrationName='SijSij', Input=computeDerivatives1)
sijSij.AttributeType = 'Cell Data'
sijSij.ResultArrayName = 'SijSij'

sijSij.Function = 'Strain_0*Strain_0 + Strain_1*Strain_1 + Strain_2*Strain_2 + Strain_3*Strain_3 + Strain_4*Strain_4 + Strain_5*Strain_5 + Strain_6*Strain_6 + Strain_7*Strain_7 + Strain_8*Strain_8'

# create a new 'Slice'
sliceSijSij = Slice(registrationName='SliceSijSij', Input=sijSij)
sliceSijSij.SliceType = 'Plane'
sliceSijSij.HyperTreeGridSlicer = 'Plane'
sliceSijSij.SliceOffsetValues = [0.0]
sliceSijSij.SliceType.Normal = [0.0, 1.0, 0.0]

# create a new 'Python Calculator'
calcAvgOmegaOmega = PythonCalculator(registrationName='calcAvgOmegaOmega', Input=sliceOmegaOmega)
calcAvgOmegaOmega.Expression = "mean(inputs[0].CellData['vortMagSquaredHalf'])"
calcAvgOmegaOmega.ArrayName = 'avgOmegaOmega'
calcAvgOmegaOmega.CopyArrays = 0

# create a new 'Python Calculator'
calcAvgSijSij = PythonCalculator(registrationName='calcAvgSijSij', Input=sliceSijSij)
calcAvgSijSij.Expression = "mean(inputs[0].CellData['SijSij'])"
calcAvgSijSij.ArrayName = 'avgSijSij'
calcAvgSijSij.CopyArrays = 0

# Create storage arrays
yLocations = np.empty(0)
sVector = np.empty(0)
oVector = np.empty(0)


for y in yTargets:

	y = 1.001*y # To work in between extreme planes

	# init the 'Plane' selected for 'SliceType'
	sliceOmegaOmega.SliceType.Origin = [0.0, y, 0.0]
	sliceOmegaOmega.HyperTreeGridSlicer.Origin = [0.0, y, 0.0]

	# init the 'Plane' selected for 'SliceType'
	sliceSijSij.SliceType.Origin = [0.0, y, 0.0]
	sliceSijSij.HyperTreeGridSlicer.Origin = [0.0, y, 0.0]

	dataset = servermanager.Fetch(calcAvgOmegaOmega)
	avgOijOij_val = dataset.GetBlock(0).GetPointData().GetArray("avgOmegaOmega").GetValue(0)


	dataset = servermanager.Fetch(calcAvgSijSij)
	avgSijSij_val = dataset.GetBlock(0).GetPointData().GetArray("avgSijSij").GetValue(0)
	print("ylocation = ", y, "oij, sij = ", avgOijOij_val, avgSijSij_val)
	print("Percentage difference = ", 100*(avgSijSij_val - avgOijOij_val)/avgOijOij_val)

	yLocations = np.append(yLocations, [y])
	sVector = np.append(sVector, [avgSijSij_val])
	oVector = np.append(oVector, avgOijOij_val)
	
	
percDiffVector = 100*(sVector - oVector)/oVector
#print(yLocations, sVector, oVector)
#print(percDiffVector)

print([yLocations, sVector, oVector, percDiffVector])

np.savetxt('hit_planeAvg.csv', np.stack((yLocations, sVector, oVector, percDiffVector),axis=-1), delimiter=',', header='y, sijsij, oijoij, percDiff')
