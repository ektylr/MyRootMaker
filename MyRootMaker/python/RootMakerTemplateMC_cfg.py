import FWCore.ParameterSet.Config as cms

process = cms.Process("ROOTMAKER")

# initialize MessageLogger and output report
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.load('Configuration.StandardSequences.Services_cff')
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
#process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")

	
process.MessageLogger.cerr.threshold = 'INFO'
#process.MessageLogger.categories.append('PATSummaryTables')
process.GlobalTag.globaltag = cms.string('START70_V7::All')

process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(False))

process.source = cms.Source("PoolSource", 
     fileNames = cms.untracked.vstring(
#'/store/mc/Summer12_DR53X/T_t-channel_TuneZ2star_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v3/00000/90B3B34B-B00F-E211-B13A-003048678E24.root'
'/store/mc/Spring14dr/GluGluToHToMuMu_M-125_13TeV-powheg-pythia6/AODSIM/PU_S14_POSTLS170_V6-v1/00000/1E93B8DB-7CFD-E311-BFC7-7845C4FC346A.root'
)
#     noEventSort = cms.untracked.bool(True),
#     duplicateCheckMode = cms.untracked.string('noDuplicateCheck')
)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1) 
)
# The Good vertices collection _____________________________________________||
process.goodVertices = cms.EDFilter(
                "VertexSelector",
                filter = cms.bool(False),
                src = cms.InputTag("offlinePrimaryVertices"),
                cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.rho < 2")
                )
process.vertex_step=cms.Path(process.goodVertices)
#####Filter
## The good primary vertex filter ____________________________________________||
process.primaryVertexFilter = cms.EDFilter(
                "VertexSelector",
                src = cms.InputTag("offlinePrimaryVertices"),
                cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.Rho <= 2"),
                filter = cms.bool(True)
                )
## The beam scraping filter __________________________________________________||
process.noscraping = cms.EDFilter(
                "FilterOutScraping",
                applyfilter = cms.untracked.bool(True),
                debugOn = cms.untracked.bool(False),
                numtrack = cms.untracked.uint32(10),
                thresh = cms.untracked.double(0.25)
                )
## The iso-based HBHE noise filter ___________________________________________||
process.load('CommonTools.RecoAlgos.HBHENoiseFilter_cfi')
## The CSC beam halo tight filter ____________________________________________||
process.load('RecoMET.METFilters.CSCTightHaloFilter_cfi')
## The HCAL laser filter _____________________________________________________||
process.load("RecoMET.METFilters.hcalLaserEventFilter_cfi")
## The ECAL dead cell trigger primitive filter _______________________________||
process.load('RecoMET.METFilters.EcalDeadCellTriggerPrimitiveFilter_cfi')
## The EE bad SuperCrystal filter ____________________________________________||
process.load('RecoMET.METFilters.eeBadScFilter_cfi')
## The ECAL laser correction filter
process.load('RecoMET.METFilters.ecalLaserCorrFilter_cfi')
## The tracking failure filter _______________________________________________||
process.load('RecoMET.METFilters.trackingFailureFilter_cfi')

process.filters_step = cms.Path(
                process.primaryVertexFilter *
                process.noscraping *
                process.HBHENoiseFilter *
                process.CSCTightHaloFilter *
                process.hcalLaserEventFilter *
                process.EcalDeadCellTriggerPrimitiveFilter *
                process.trackingFailureFilter *
                process.eeBadScFilter *
                process.ecalLaserCorrFilter
                )

####### Jet MET corrections
process.load('RecoJets.Configuration.RecoPFJets_cff')
process.kt6PFJets.doRhoFastjet = True
process.kt6PFJets.doAreaFastjet = True
process.kt6PFJets.voronoiRfact = 0.9

process.load('JetMETCorrections.Configuration.DefaultJEC_cff')
process.load('JetMETCorrections.Configuration.JetCorrectionServices_cff')
process.load("JetMETCorrections.Type1MET.pfMETCorrectionType0_cfi")
process.load('JetMETCorrections.Type1MET.pfMETCorrections_cff')
process.pfJetMETcorr.jetCorrLabel = cms.string("ak5PFL1FastL2L3") #MC

from JetMETCorrections.Type1MET.pfMETCorrections_cff import pfType1CorrectedMet
process.pfType0Type1CorrectedMet = pfType1CorrectedMet.clone(
applyType0Corrections = cms.bool(False),
srcType1Corrections = cms.VInputTag(
    cms.InputTag('pfMETcorrType0'),
    cms.InputTag('pfJetMETcorr', 'type1')
)
)
process.metAnalysisSequence=cms.Sequence(process.type0PFMEtCorrection*process.producePFMETCorrections*process.pfType0Type1CorrectedMet)
process.jet_step = cms.Path(process.kt6PFJets*process.metAnalysisSequence)

######PF ISO calculation for Electrons
from CommonTools.ParticleFlow.Tools.pfIsolation import setupPFElectronIso, setupPFPhotonIso
#from CommonTools.ParticleFlow.Isolation.pfElectronIsolation_cff import *

# NEW STUFF ##################
process.stdElectronSequencePFIso = setupPFElectronIso(process, 'gedGsfElectrons')#'gsfElectrons')
process.stdPhotonSequencePFIso = setupPFPhotonIso(process, 'photons')
process.pfiso_step = cms.Path( process.pfParticleSelectionSequence +
                               process.stdElectronSequencePFIso +
                               process.stdPhotonSequencePFIso)
##############################

# OLD STUFF #########################
#process.eleIsoSequence = setupPFElectronIso(process, 'gsfElectrons')
#process.phoIsoSequence = setupPFPhotonIso(process, 'photons')
#process.pfiso_step = cms.Path( process.pfParticleSelectionSequence + process.eleIsoSequence + process.phoIsoSequence)
#####################################

######Electron ID
process.load("RecoEgamma.ElectronIdentification.cutsInCategoriesElectronIdentificationV06_cfi")
process.electron_step = cms.Path(process.eidHyperTight1MC*process.eidLooseMC)

######Matching Partons to Jets
process.load("PhysicsTools.JetMCAlgos.CaloJetsMCFlavour_cfi")
process.AK5byRef.jets = cms.InputTag("ak5PFJets")
process.jetflavour_step = cms.Path(process.myPartons * process.AK5Flavour)

######PAT
process.load("PhysicsTools.PatAlgos.patSequences_cff")
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContent
process.out = cms.OutputModule("PoolOutputModule",
		fileName = cms.untracked.string('patTuple.root'),
# save only events passing the full path
		SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
# save PAT Layer 1 output; you need a '*' to
# unpack the list of commands 'patEventContent'
		outputCommands = cms.untracked.vstring('drop *', *patEventContent )
		)
#from PhysicsTools.PatAlgos.tools.coreTools import *
#removeAllPATObjectsBut(process, ['Jets'])
from PhysicsTools.PatAlgos.tools.pfTools import usePF2PAT
postfix = "PFlow"
usePF2PAT(process,runPF2PAT=True,
		jetAlgo='AK5', runOnMC=False, postfix=postfix,
		#jetCorrections=('AK5PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute']),
                jetCorrections=('AK5PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'],'Type-1'),

		pvCollection=cms.InputTag('offlinePrimaryVertices')
	 )
process.pfPileUpPFlow.checkClosestZVertex = False
#getattr(process, "patPF2PATSequence"+postfix).remove(getattr(process, "cleanPatCandidates"+postfix))
#getattr(process, "patPF2PATSequence"+postfix).remove(getattr(process, "countPatCandidates"+postfix))
#process.patseq = cms.Sequence(getattr(process,"patPF2PATSequence"+postfix))
#process.pat_step = cms.Path(process.patseq)

######Pileup Jet ID (Hendrik)
#https://twiki.cern.ch/twiki/bin/view/CMS/PileupJetID#Running_the_algorithm_on_reco_je
from CMGTools.External.pujetidsequence_cff import puJetId, puJetMva

process.recoPuJetId = puJetId.clone(
		jets = cms.InputTag("ak5PFJets"),
		applyJec = cms.bool(True),
		inputIsCorrected = cms.bool(False),                
		)

process.recoPuJetMva = puJetMva.clone(
		jets = cms.InputTag("ak5PFJets"),
		jetids = cms.InputTag("recoPuJetId"),
		applyJec = cms.bool(True),
		inputIsCorrected = cms.bool(False),                
		)
process.recoPuJetIdSqeuence = cms.Sequence(process.recoPuJetId * process.recoPuJetMva)
process.jetpuid_step = cms.Path(process.recoPuJetIdSqeuence)


######ROOTMAKER 
process.makeroottree = cms.EDAnalyzer("RootMaker",
GenAllParticles = cms.untracked.bool(False),
GenSomeParticles = cms.untracked.bool(True),
GenAK5Jets = cms.untracked.bool(True),

Trigger = cms.untracked.bool(True),
HLTriggerSelection = cms.untracked.vstring(),
#TriggerProcess = cms.untracked.string('REDIGI311X'),
RecPrimVertex = cms.untracked.bool(True),
RecBeamSpot = cms.untracked.bool(True),

RecPFMet = cms.untracked.bool(True),

RecTrack = cms.untracked.bool(True),
RecTrackPtMin = cms.untracked.double(10.),
RecTrackEtaMax = cms.untracked.double(2.5),
RecTrackNum = cms.untracked.int32(100000),
RecTrackFilterPtMin = cms.untracked.double(18.),

RecSuperCluster = cms.untracked.bool(True),
RecSuperClusterFilterPtMin = cms.untracked.double(8.),
RecSuperClusterBasicCluster = cms.untracked.bool(False),
RecSuperClusterHit = cms.untracked.bool(False),

RecMuon = cms.untracked.bool(True),
RecMuonPtMin = cms.untracked.double(20),
RecMuonTrackIso = cms.untracked.double(1000000),
RecMuonEtaMax = cms.untracked.double(2.5),
RecMuonNum = cms.untracked.int32(1000),
RecMuonHLTriggerMatching = cms.untracked.vstring(
'HLT_Mu17_Mu8_v.*:FilterTrue',
'HLT_Mu17_TkMu8_v.*:FilterTrue',
'HLT_Mu22_TkMu22_v.*:FilterTrue',
'HLT_Mu(8|17)_v.*',
'HLT_IsoMu(24|30)_v.*',
'HLT_IsoMu(24|30)_eta2p1_v.*',
'HLT_Mu40_v.*',
'HLT_Mu50_eta2p1_v.*',
'HLT_Mu40_eta2p1_v.*'
),
#RecMassMuMuMin = cms.untracked.double(2.6),
#RecMassMuMuMax = cms.untracked.double(3.5),

RecPhoton = cms.untracked.bool(True),
RecPhotonHLTriggerMatching = cms.untracked.vstring(),
RecPhotonPtMin = cms.untracked.double(10.),
RecPhotonEtaMax = cms.untracked.double(2.5),
RecPhotonNum = cms.untracked.int32(100000),
RecPhotonFilterPtMin = cms.untracked.double(10),

RecElectron = cms.untracked.bool(True),
RecElectronHLTriggerMatching = cms.untracked.vstring(
'HLT_Ele17_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_Ele8_CaloIdT_CaloIsoVL_TrkIdVL_TrkIsoVL_v.*:FilterTrue',
'HLT_DoubleEle33_CaloIdL_GsfTrkIdVL_v.*:FilterTrue',
'HLT_Ele27_WP80_v.*',
'HLT_Ele80_CaloIdVT_TrkIdT_v.*',
'HLT_Ele80_CaloIdVT_GsfTrkIdT_v.*'
),
RecElectronPtMin = cms.untracked.double(20.),
RecElectronTrackIso = cms.untracked.double(1000000.),
RecElectronEta = cms.untracked.double(2.5),
RecElectronNum = cms.untracked.int32(100000),
RecElectronFilterPtMin = cms.untracked.double(20.),

RecTau = cms.untracked.bool(False),
RecTauHLTriggerMatching = cms.untracked.vstring(),
RecTauDiscriminators = cms.untracked.vstring(
'hpsPFTauDiscriminationByDecayModeFinding',
'hpsPFTauDiscriminationByLooseElectronRejection',
'hpsPFTauDiscriminationByLooseIsolation',
'hpsPFTauDiscriminationByLooseMuonRejection',
'hpsPFTauDiscriminationByMediumElectronRejection',
'hpsPFTauDiscriminationByMediumIsolation',
'hpsPFTauDiscriminationByTightElectronRejection',
'hpsPFTauDiscriminationByTightIsolation',
'hpsPFTauDiscriminationByTightMuonRejection',
'hpsPFTauDiscriminationByVLooseIsolation'
),

RecTauPtMin = cms.untracked.double(0.),
RecTauEta = cms.untracked.double(0.),
RecTauNum = cms.untracked.int32(100000),

RecAK5CaloJet = cms.untracked.bool(False),
RecAK5CaloPtMin = cms.untracked.double(20.),
RecAK5CaloEtaMax = cms.untracked.double(2.4),
RecAK5CaloNum = cms.untracked.int32(100000),
RecAK5CaloFilterPtMin = cms.untracked.double(20.),

RecAK5JPTJet = cms.untracked.bool(False),
RecAK5JPTPtMin = cms.untracked.double(20.),
RecAK5JPTEtaMax = cms.untracked.double(2.4),
RecAK5JPTNum = cms.untracked.int32(100000),
RecAK5JPTFilterPtMin = cms.untracked.double(20.),

#JetCorrection = cms.untracked.string('L1FastL2L3Residual'),#Data
JetCorrection = cms.untracked.string('L1FastL2L3'),#MC
RecJetHLTriggerMatching = cms.untracked.vstring(),

RecAK5PFJet = cms.untracked.bool(True),
RecAK5PFPtMin = cms.untracked.double(20.),
RecAK5PFEtaMax = cms.untracked.double(3.0),
RecAK5PFNum = cms.untracked.int32(100000),
RecAK5PFFilterPtMin = cms.untracked.double(20.),

RecAK5PFCHSJet = cms.untracked.bool(True),
RecAK5PFCHSPtMin = cms.untracked.double(20.),
RecAK5PFCHSEtaMax = cms.untracked.double(3.0),
RecAK5PFCHSNum = cms.untracked.int32(100000),
RecAK5PFCHSFilterPtMin = cms.untracked.double(20.),

RecSecVertices = cms.untracked.bool(False),
RecVertexTRKChi2 = cms.untracked.double(5),
RecVertexTRKHitsMin = cms.untracked.int32(6),
RecVertexChi2 = cms.untracked.double(3),
RecVertexSig2D = cms.untracked.double(15),
RecKaonMasswin = cms.untracked.double(0.05),
RecLambdaMasswin = cms.untracked.double(0.02)
)

#process.genPlusSimParticles = cms.EDProducer("GenPlusSimParticleProducer",
#src = cms.InputTag("g4SimHits"),
#setStatus = cms.int32(8),
#filter = cms.vstring("pt > 0.0"),
#genParticles = cms.InputTag("genParticles")
#)

process.TFileService = cms.Service("TFileService",
	fileName = cms.string('AC1B_test.root')
)

process.roottree_step = cms.EndPath(process.makeroottree)

