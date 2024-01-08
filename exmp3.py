#!/usr/bin/env python
import sys
from geant4_pybind import *
class X3DetectorConstruction(G4VUserDetectorConstruction):
   """
   Simple model: a sphere with water in the air box.
   """

   def __init__(self):
        super().__init__()
        self.fScoringVolume = None

   def Construct(self):
        nist = G4NistManager.Instance()

        envelop_x = 36*cm
        envelop_y = 36*cm
        envelop_z = 36*cm

        envelop_mat = nist.FindOrBuildMaterial("G4_AIR")

        sphere_rad = 15*cm
        sphere_rad1 = 4*cm
        sphere_rad2 = 8*cm
        mat = nist.FindOrBuildMaterial("G4_WATER")
        mat1 = nist.FindOrBuildMaterial("G4_Fe")
        mat2 = nist.FindOrBuildMaterial("G4_C")


        checkOverlaps = True

        world_x = 1.2*envelop_x
        world_y = 1.2*envelop_y
        world_z = 1.2*envelop_z

        sWorld = G4Box("World", 0.5*world_x, 0.5*world_y,
                    0.5*world_z)

        lWorld = G4LogicalVolume(sWorld, envelop_mat, "World")

        pWorld = G4PVPlacement(None, G4ThreeVector(),
                            lWorld, "World", None, False,
                            0, checkOverlaps)

        sEnvelop = G4Box ("Envelop", 0.5*envelop_x, 0.5*envelop_y, 0.5*envelop_z)
        lEnvelop = G4LogicalVolume(sEnvelop, envelop_mat, "Envelop")
        pEnvelop = G4PVPlacement (None, G4ThreeVector(), lEnvelop, "Envelop", lWorld, True, 0, checkOverlaps)


        sSphere = G4Orb("Head", sphere_rad)
        lSphere = G4LogicalVolume(sSphere, mat, "Head")
        G4PVPlacement(None, G4ThreeVector(), lSphere,
                   "Head", lEnvelop, True, 0, checkOverlaps)

        sOrb1 = G4Orb("Bullet", sphere_rad1)
        lOrb1 = G4LogicalVolume(sOrb1, mat1, "Bullet")
        G4PVPlacement(None, G4ThreeVector(0,0,-0.4*sphere_rad), lOrb1,
                   "Bullet", lSphere, True, 0, checkOverlaps)

        sOrb2 = G4Orb("Coal", sphere_rad2)
        lOrb2 = G4LogicalVolume(sOrb2, mat2, "Coal")
        G4PVPlacement(None, G4ThreeVector(0,0,0.2*sphere_rad), lOrb2,
                   "Coal", lSphere, True, 0, checkOverlaps)


        self.fScoringVolume = lSphere

        return pWorld

ui = None
if len(sys.argv) == 1:
    ui = G4UIExecutive(len(sys.argv), sys.argv)

# Optionally: choose a different Random engine...
# G4Random.setTheEngine(MTwistEngine())

runManager = G4RunManagerFactory.CreateRunManager(G4RunManagerType.Serial)
runManager.SetUserInitialization(X3DetectorConstruction())

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
