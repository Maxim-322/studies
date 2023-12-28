#!/usr/bin/env python
import sys
from geant4_pybind import *
class X1DetectorConstruction(G4VUserDetectorConstruction):
   """
   Simple model: a sphere with water in the air box.
   """

   def __init__(self):
        super().__init__()
        self.fScoringVolume = None

   def Construct(self):

        nist = G4NistManager.Instance()

        envelop_x = 20*cm
        envelop_y = 20*cm
        envelop_z = 20*cm

        envelop_mat = nist.FindOrBuildMaterial("G4_AIR")

        sphere_rad = 7*cm
        mat = nist.FindOrBuildMaterial("G4_WATER")


        checkOverlaps = True

        world_x = 2*envelop_x
        world_y = 2*envelop_y
        world_z = 2*envelop_z

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


        self.fScoringVolume = lSphere

        return pWorld

ui = None
if len(sys.argv) == 1:
    ui = G4UIExecutive(len(sys.argv), sys.argv)

# Optionally: choose a different Random engine...
# G4Random.setTheEngine(MTwistEngine())

runManager = G4RunManagerFactory.CreateRunManager(G4RunManagerType.Serial)

runManager.SetUserInitialization(X1DetectorConstruction())

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
