#!/usr/bin/env python
import sys
from geant4_pybind import *
class X5DetectorConstruction(G4VUserDetectorConstruction):
   """
   Simple model: a sphere with water in the air box.
   """

   def __init__(self):
        super().__init__()
        self.fScoringVolume = None

   def Construct(self):

        nist = G4NistManager.Instance()

        envelop_x = 54*cm
        envelop_y = 54*cm
        envelop_z = 54*cm
        envelop_mat = nist.FindOrBuildMaterial("G4_AIR")

        sphere_rad1 = 25*cm
        sphere_rad2 = 24*cm
        x_axis3 = 12*cm
        y_axis3 = 6*cm
        z_axis3 = 12*cm
        x_axis4 = 8*cm
        y_axis4 = 4*cm
        z_axis4 = 8*cm
        mat1 = nist.FindOrBuildMaterial("B-100_BONE")
        mat2 = nist.FindOrBuildMaterial("G4_WATER")
        mat3 = nist.FindOrBuildMaterial("G4_ACETONE")
        mat4 = nist.FindOrBuildMaterial("G4_BENZENE")



        checkOverlaps = True

        world_x = 1.2*envelop_x
        world_y = 1.2*envelop_y
        world_z = 1.2*envelop_z

        sWorld = G4Box("World", 0.5*world_x, 0.5*world_y, 0.5*world_z)
        lWorld = G4LogicalVolume(sWorld, envelop_mat, "World")
        pWorld = G4PVPlacement(None, G4ThreeVector(),lWorld, "World", None, False,0, checkOverlaps)

        sEnvelop = G4Box ("Envelop", 0.5*envelop_x, 0.5*envelop_y, 0.5*envelop_z)
        lEnvelop = G4LogicalVolume(sEnvelop, envelop_mat, "Envelop")
        pEnvelop = G4PVPlacement (None, G4ThreeVector(), lEnvelop, "Envelop", lWorld, True, 0, checkOverlaps)


        sSphere1 = G4Orb("Bonehead", sphere_rad1)
        #lSphere1 = G4LogicalVolume(sSphere1, mat1, "Bonehead")
        #pSphere1 = G4PVPlacement(None, G4ThreeVector(), lSphere1, "Bonehead", lEnvelop, True, 0, checkOverlaps)

        sSphere2 = G4Orb("Waterhead", sphere_rad2)
        #lSphere2 = G4LogicalVolume(sSphere2, mat2, "Waterhead")
        #pSphere2 = G4PVPlacement(None, G4ThreeVector(), lSphere2, "Waterhead", lSphere1, True, 0, checkOverlaps)

        sCutSphere = G4SubtractionSolid ("Bone-Water", sSphere1, sSphere2)
        lSphere3 = G4LogicalVolume (sSphere2, mat2, "WaterCore")
        lSphere4 = G4LogicalVolume (sCutSphere, mat1, "BoneSurface")

        G4PVPlacement (None, G4ThreeVector(), lSphere4, "BoneSurface", lEnvelop, True, 0, checkOverlaps)
        G4PVPlacement (None, G4ThreeVector(), lSphere3, "WaterCore", lSphere4, True, 0, checkOverlaps)

        sEllipsoid1 = G4Ellipsoid ("Acetonebody", x_axis3, y_axis3, z_axis3)
        #lEllipsoid1 = G4LogicalVolume(sEllipsoid1, mat3, "Acetonebody")
        #pEllipsoid1 = G4PVPlacement(None, G4ThreeVector(0,0,0), lEllipsoid1, "Acetonebody", lSphere3, True, 0, checkOverlaps)

        sEllipsoid2 = G4Ellipsoid("Benzenebody", x_axis4, y_axis4, z_axis4)
        #lEllipsoid2 = G4LogicalVolume(sEllipsoid2, mat4, "Benzenebody")
        #pEllipsoid2 = G4PVPlacement(None, G4ThreeVector(0,-0.6*x_axis4,), lEllipsoid2, "Benzenebody", lSphere3, True, 0, checkOverlaps)

        shift = -1*y_axis4
        zTrans = G4ThreeVector(0, shift, 0)
        sCutBrain = G4SubtractionSolid("Brain", sEllipsoid1, sEllipsoid2, G4RotationMatrix(), zTrans)
        lLowerBrain = G4LogicalVolume (sEllipsoid2, mat4, "LowerBrain")
        lUpperBrain = G4LogicalVolume (sCutBrain, mat3, "UpperBrain")

        G4PVPlacement (None, G4ThreeVector(0,0.5*y_axis4,0), lUpperBrain, "UpperBrain", lSphere3, True, 0, checkOverlaps)
        G4PVPlacement (None, G4ThreeVector(0,-0.5*y_axis4,0), lLowerBrain, "LowerBrain", lSphere3, True, 0, checkOverlaps)

        self.fScoringVolume = lSphere4

        return pWorld

ui = None
if len(sys.argv) == 1:
    ui = G4UIExecutive(len(sys.argv), sys.argv)

# Optionally: choose a different Random engine...
# G4Random.setTheEngine(MTwistEngine())

runManager = G4RunManagerFactory.CreateRunManager(G4RunManagerType.Serial)
runManager.SetUserInitialization(X5DetectorConstruction())

# Physics list

physicsList = QBBC()
physicsList.SetVerboseLevel(1)
runManager.SetUserInitialization(physicsList)

# User action initialization

#runManager.SetUserInitialization(XXActionInitialization())
visManager = G4VisExecutive()

# G4VisExecutive can take a verbosity argument - see /vis/verbose guidance.
# visManager = G4VisExecutive("Quiet")

visManager.Initialize()

# Get the User Interface manager

UImanager = G4UImanager.GetUIpointer()

# # Process macro or start UI session

if ui == None:

   # batch mode

   command = "/control/execute "
   fileName = sys.argv[1]
   UImanager.ApplyCommand(command + fileName)
else:

   # interactive mode

   UImanager.ApplyCommand("/control/execute init_vis.mac")
   ui.SessionStart()
