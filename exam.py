#!/usr/bin/env python
import sys
import math
from geant4_pybind import *


class EXAMDetectorConstruction(G4VUserDetectorConstruction):

    def __init__(self):
        super().__init__()
        self.fScoringVolume = None
        
    def Construct(self):

        nist = G4NistManager.Instance()

        envelop_x = 30*cm
        envelop_y = 30*cm
        envelop_z = 30*cm
        leg_rad = 0.5*envelop_y
        leg_height = 0.7*envelop_z
        envelop_mat = nist.FindOrBuildMaterial("G4_AIR")
        Huckle_mat = nist.FindOrBuildMaterial("G4_TISSUE_SOFT_ICRP")

        checkOverlaps = True
 
        world_x = 2*envelop_x
        world_y = 2*envelop_y
        world_z = 2*envelop_z
        box_x = 2.1*leg_rad
        box_y = 2.1*leg_rad
        box_z = 2.1*leg_height

        sWorld = G4Box("World", 0.5*world_x, 0.5*world_y, 0.5*world_z)
        lWorld = G4LogicalVolume(sWorld, envelop_mat, "World")
        pWorld = G4PVPlacement(None, G4ThreeVector(),lWorld, "World", None, False,0, checkOverlaps)

        sBox = G4Box ("Box", 0.5*box_x, 0.5*box_y, 0.5*box_z)
        lBox = G4LogicalVolume(sBox, envelop_mat, "Box")
        pBox = G4PVPlacement (None, G4ThreeVector(), lBox, "Box", lWorld, True, 0, checkOverlaps)

        sHuckle = G4Tubs ("Huckle", 0, leg_rad, leg_height, 2*math.pi, 2*math.pi)
        lHuckle = G4LogicalVolume(sHuckle,Huckle_mat, "Huckle")
        pHuckle = G4PVPlacement (None, G4ThreeVector(), lHuckle, "Huckle", lBox, True, 0, checkOverlaps)

        self.fScoringVolume = lBox
 
        return pWorld

class EXAMActionInitialization(G4VUserActionInitialization):

  def BuildForMaster(self):

    self.SetUserAction(EXAMRunAction())

  def Build(self):

    self.SetUserAction(EXAMPrimaryGeneratorAction())
    runAction = EXAMRunAction()

    self.SetUserAction(runAction)
    eventAction = EXAMEventAction(runAction)

    self.SetUserAction(eventAction)
    self.SetUserAction(EXAMSteppingAction(eventAction))


class EXAMPrimaryGeneratorAction(G4VUserPrimaryGeneratorAction):
    def __init__(self):
        super().__init__()
        self.fEnvelopeBox = None
        self.fParticleGun = G4ParticleGun(1)

        particleTable = G4ParticleTable.GetParticleTable()
        particle = particleTable.FindParticle("e+")
        self.fParticleGun.SetParticleDefinition(particle)
        self.fParticleGun.SetParticleMomentumDirection(G4ThreeVector(1,1,0))
        self.fParticleGun.SetParticleEnergy(0.4*MeV)

    def GeneratePrimaries(self, anEvent):
        envSizeX = 0
        envSizeY = 0
        envSizeZ = 0

        if self.fEnvelopeBox == None:
            envLV = G4LogicalVolumeStore.GetInstance().GetVolume("Box")
            if envLV != None:
                self.fEnvelopeBox = envLV.GetSolid()

            if self.fEnvelopeBox != None:
                envSizeX = self.fEnvelopeBox.GetXHalfLength()*2
                envSizeY = self.fEnvelopeBox.GetYHalfLength()*2
                envSizeZ = self.fEnvelopeBox.GetZHalfLength()*2

            else:
                msg = "Envelope volume of box shape not found.\n"
                msg += "Perhaps you have changed geometry.\n"
                msg += "The gun will be place at the center."
                G4Exception("XXPrimaryGeneratorAction::GeneratePrimaries()","MyCode0002", G4ExceptionSeverity.JustWarning, msg)

            x0 = -0.5 * envSizeX
            y0 = -0.5 * envSizeY
            z0 = 0
 
            self.fParticleGun.SetParticlePosition(G4ThreeVector(x0, y0, z0))
            self.fParticleGun.GeneratePrimaryVertex(anEvent)


class EXAMRunAction(G4UserRunAction):
    def __init__(self):
        super().__init__()

        milligray = 1.e-3*gray
        microgray = 1.e-6*gray
        nanogray = 1.e-9*gray
        picogray = 1.e-12*gray

        G4UnitDefinition("milligray", "milliGy", "Dose", milligray)
        G4UnitDefinition("microgray", "microGy", "Dose", microgray)
        G4UnitDefinition("nanogray", "nanoGy", "Dose", nanogray)
        G4UnitDefinition("picogray", "picoGy", "Dose", picogray)

        self.edep = G4Accumulable(0)
        self.edep2 = G4Accumulable(0)

        accumulableManager = G4AccumulableManager.Instance()
        accumulableManager.RegisterAccumulable(self.edep)
        accumulableManager.RegisterAccumulable(self.edep2)

    def BeginOfRunAction(self, aRun):
        G4RunManager.GetRunManager().SetRandomNumberStore(False)

        accumulableManager = G4AccumulableManager.Instance()
        accumulableManager.Reset()

    def EndOfRunAction(self, aRun):
        nofEvents = aRun.GetNumberOfEvent()
        if nofEvents == 0:
            return

        # Merge accumulables
        accumulableManager = G4AccumulableManager.Instance()
        accumulableManager.Merge()

        edep = self.edep.GetValue()
        edep2 = self.edep2.GetValue()

        # Compute dose = total energy deposit in a run and its variance
        rms = edep2 - edep*edep/nofEvents
        if rms > 0:
            rms = math.sqrt(rms)
        else:
            rms = 0

        detectorConstruction = G4RunManager.GetRunManager().GetUserDetectorConstruction()
        mass = detectorConstruction.fScoringVolume.GetMass()
        dose = edep/mass
        rmsDose = rms/mass

        generatorAction = G4RunManager.GetRunManager().GetUserPrimaryGeneratorAction()
        runCondition = ""
        if generatorAction != None and isinstance(generatorAction, EXAMPrimaryGeneratorAction):
            particleGun = generatorAction.fParticleGun
            runCondition += particleGun.GetParticleDefinition().GetParticleName() + "(s)"
            runCondition += " of "
            particleEnergy = particleGun.GetParticleEnergy()
            runCondition += "{:.5g}".format(G4BestUnit(particleEnergy, "Energy"))
 
            if self.IsMaster():
                print("--------------------End of Global Run-----------------------")
            else:
                print("--------------------End of Local Run------------------------")

        print(" The run consists of", nofEvents, runCondition)
        print(" Cumulated dose per run, in scoring volume: ", end="")
        print("{:.5f} rms = {:.5f}".format(G4BestUnit(dose, "Dose"), G4BestUnit(rmsDose, "Dose")))
        print("------------------------------------------------------------")
        print("")

    def AddEdep(self, edep):
        self.edep += edep
        self.edep2 += edep*edep

class EXAMEventAction(G4UserEventAction):
	def __init__(self, runAction):
		super().__init__()
		self.fRunAction = runAction

	def BeginOfEventAction(self, anEvent):
		self.fEdep = 0

	def EndOfEventAction(self, anEvent):
		self.fRunAction.AddEdep(self.fEdep)

	def AddEdep(self, edep):
		self.fEdep += edep

class EXAMSteppingAction(G4UserSteppingAction):
	def __init__(self, eventAction):
		super().__init__()
		self.fEventAction = eventAction
		self.fScoringVolume = None

	def UserSteppingAction(self, aStep):
		if self.fScoringVolume == None:
			detectorConstruction = G4RunManager.GetRunManager().GetUserDetectorConstruction()
			self.fScoringVolume = detectorConstruction.fScoringVolume

		volume = aStep.GetPreStepPoint().GetTouchable().GetVolume().GetLogicalVolume()

		# check if we are in scoring volume
		if volume != self.fScoringVolume:
			return

		# collect energy deposited in this step
		edepStep = aStep.GetTotalEnergyDeposit()
		self.fEventAction.AddEdep(edepStep)


ui = None
if len(sys.argv) == 1:
    ui = G4UIExecutive(len(sys.argv), sys.argv)

# Optionally: choose a different Random engine...
# G4Random.setTheEngine(MTwistEngine())

runManager = G4RunManagerFactory.CreateRunManager(G4RunManagerType.Serial)
runManager.SetUserInitialization(EXAMDetectorConstruction())

# Physics list

physicsList = QBBC()
physicsList.SetVerboseLevel(1)
runManager.SetUserInitialization(physicsList)

# User action initialization

runManager.SetUserInitialization(EXAMActionInitialization())
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
