# state file generated using paraview version 5.9.0

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'EnSight Reader'
artscase = EnSightReader(registrationName='arts.case', CaseFileName='/scratch/sverma/aish_enstrophy/hit/generateEnstrophy/ensDir/arts.case')
artscase.PointArrays = ['U', 'V', 'W', 'P', 'BCH']

# create a new 'Calculator'
calculator1 = Calculator(registrationName='Calculator1', Input=artscase)
calculator1.ResultArrayName = 'velVec'
calculator1.Function = 'U*iHat + V*jHat + W*kHat'

# create a new 'Compute Derivatives'
computeDerivatives1 = ComputeDerivatives(registrationName='ComputeDerivatives1', Input=calculator1)
computeDerivatives1.Scalars = ['POINTS', 'U']
computeDerivatives1.Vectors = ['POINTS', 'velVec']
computeDerivatives1.OutputVectorType = 'Vorticity'
computeDerivatives1.OutputTensorType = 'Strain'

# create a new 'Calculator'
vortMagSquaredHalf = Calculator(registrationName='vortMagSquaredHalf', Input=computeDerivatives1)
vortMagSquaredHalf.AttributeType = 'Cell Data'
vortMagSquaredHalf.ResultArrayName = 'vortMagSquaredHalf'
vortMagSquaredHalf.Function = '0.5*(mag(Vorticity))^2'

# create a new 'Python Calculator'
calcAvgOmegaOmega = PythonCalculator(registrationName='calcAvgOmegaOmega', Input=vortMagSquaredHalf)
calcAvgOmegaOmega.Expression = "mean(inputs[0].CellData['vortMagSquaredHalf'])"
calcAvgOmegaOmega.ArrayName = 'avgOmegaOmega'
calcAvgOmegaOmega.CopyArrays = 0


dataset = servermanager.Fetch(calcAvgOmegaOmega)
avgOijOij_val = dataset.GetBlock(0).GetPointData().GetArray("avgOmegaOmega").GetValue(0)
print(avgOijOij_val)


# create a new 'Calculator'
sijSij = Calculator(registrationName='SijSij', Input=computeDerivatives1)
sijSij.AttributeType = 'Cell Data'
sijSij.ResultArrayName = 'SijSij'
sijSij.Function = 'Strain_0*Strain_0 + Strain_1*Strain_1 + Strain_2*Strain_2 + Strain_3*Strain_3 + Strain_4*Strain_4 + Strain_5*Strain_5 + Strain_6*Strain_6 + Strain_7*Strain_7 + Strain_8*Strain_8'

# create a new 'Python Calculator'
calcAvgSijSij = PythonCalculator(registrationName='calcAvgSijSij', Input=sijSij)
calcAvgSijSij.Expression = "mean(inputs[0].CellData['SijSij'])"
calcAvgSijSij.ArrayName = 'avgSijSij'
calcAvgSijSij.CopyArrays = 0



dataset = servermanager.Fetch(calcAvgSijSij)
avgSijSij_val = dataset.GetBlock(0).GetPointData().GetArray("avgSijSij").GetValue(0)
print(avgSijSij_val)

print("Percentage difference = ", 100*(avgSijSij_val - avgOijOij_val)/avgOijOij_val)



# ----------------------------------------------------------------
# restore active source
# SetActiveSource(calcAvgSijSij)
# ----------------------------------------------------------------


if __name__ == '__main__':
    # generate extracts
    SaveExtracts(ExtractsOutputDirectory='extracts')
