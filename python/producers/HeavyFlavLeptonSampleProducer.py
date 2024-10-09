from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection

from ..helpers.utils import deltaR
from ..helpers.triggerHelper import passTrigger
from .HeavyFlavBaseProducer import HeavyFlavBaseProducer


class LeptonSampleProducer(HeavyFlavBaseProducer):

    def __init__(self, **kwargs):
        super(LeptonSampleProducer, self).__init__(channel='muon', **kwargs)

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        super(LeptonSampleProducer, self).beginFile(inputFile, outputFile, inputTree, wrappedOutputTree)

        # trigger variables
        self.out.branch("passLeptonTrig", "O")

        # event variables
        self.out.branch("lepton_pt", "F")
        self.out.branch("lepton_eta", "F")
        

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        # Lepton selection (exactly one lepton, either muon or electron)
        self.selectedLepton(event)
        if len(event.lepton_Sel) !=1:
            return False
        
        # veto loose leptons (exactly one lepton is passing because is the selected lepton)
        self.selectedVetoLepton(event)
        if len(event.vetoLepton) !=1:
            return False

        self.selectLeptons(event)
        self.correctJetsAndMET(event)

        # Zero b-jet, passing medium WP
        event.bjets = [j for j in event.ak4jets if j.btagDeepFlavB > self.DeepJet_WP_M and deltaR(j,event.lepton_Sel[0]) > 0.4]
        if len(event.bjets) > 0:
            return False

        
        # require fatjet away from the lepton dR(fj, lept.) > 0.8
        probe_jets = [fj for fj in event.fatjets if deltaR(fj,event.lepton_Sel[0]) > 0.8]
        if len(probe_jets) == 0:
            return False

        probe_jets = probe_jets[:1]
        self.loadGenHistory(event, probe_jets)
        self.evalTagger(event, probe_jets)
        self.evalMassRegression(event, probe_jets)

        # fill output branches
        self.fillBaseEventInfo(event)
        self.fillFatJetInfo(event, probe_jets)

        # fill Triggers
        if self.year == 2016:
            self.out.fillBranch("passTrigEl", passTrigger(event, 'HLT_Ele27_WPTight_Gsf'))
            self.out.fillBranch("passTrigMu", passTrigger(event, ['HLT_IsoMu24', 'HLT_IsoTkMu24']))
        elif self.year == 2017:
            self.out.fillBranch("passTrigEl", passTrigger(event, 'HLT_Ele32_WPTight_Gsf_L1DoubleEG'))
            self.out.fillBranch("passTrigMu", passTrigger(event, 'HLT_IsoMu27'))
        elif self.year == 2018:
            self.out.fillBranch("passTrigEl", passTrigger(event, 'HLT_Ele32_WPTight_Gsf'))
            self.out.fillBranch("passTrigMu", passTrigger(event, 'HLT_IsoMu24'))
        self.out.fillBranch("lepton_pt", event.lepton_Sel[0].pt)
        self.out.fillBranch("lepton_eta", event.lepton_Sel[0].eta)
        

        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
def LeptonTree_2016(): return LeptonSampleProducer(year=2016)
def LeptonTree_2017(): return LeptonSampleProducer(year=2017)
def LeptonTree_2018(): return LeptonSampleProducer(year=2018)
