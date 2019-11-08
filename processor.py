# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 11:36:40 2019

@author: christina reissel
"""

import numpy as np
import ROOT as r
import rootpy
from rootpy.tree import Tree
from rootpy.io import root_open
import time

perJet_Variables = [
"Jet_DeepFlavourBDisc", 
"Jet_DeepFlavourCvsLDisc",
"Jet_DeepFlavourCvsBDisc",
"Jet_pt",
"Jet_eta",
"Jet_hadronFlavour",
"Jet_nseltracks"
]

perEvent_Variables = [
"nPUtrue"
]

new_Variables = [
"nTracks",
"nPixelHits",
"SV_mass",
"nTracks_fromSV"
]

# Function to create histograms
def process(dataset, file_names, output): 

	# Adding all files to TChain    
	chain = r.TChain("btagana/ttree")     
	for file_name in file_names:         
		print "Adding file {0}".format(file_name)         
		chain.AddFile(file_name)         
	print "Chain contains {0} events".format(chain.GetEntries())     
	
	# Output file
	o = root_open(output, 'update')

	# Create dictionary with histograms
	tree = Tree("tree")
	branches = { v: 'F' for v in perJet_Variables }
	branches.update({v: 'F' for v in perEvent_Variables})
	branches.update({v: 'F' for v in new_Variables})
	tree.create_branches(branches)

	#total number of bytes read     
	nBytes = 0     
	t0 = time.time()     
	t1_old = t0     
	
	# Looping over events
	for iEv in range(0, chain.GetEntries()):         
		nBytes += chain.GetEntry(iEv)                 
		if iEv % 1000 == 0:             
			t1_new = time.time()            
			print "time per 1000 ev: {0:.2f}".format((t1_new - t1_old))             
			t1_old = t1_new                 

		#do something with event
		chain.GetEntry(iEv)
	
		# Looping over jets
		for iJet in range(chain.nJet):
			if chain.Jet_pt[iJet] >= 30 and abs(chain.Jet_eta[iJet]) <= 2.5:

				for v in perJet_Variables:
					setattr(tree, v, getattr(chain,v)[iJet])
				for v in perEvent_Variables:
					setattr(tree, v, getattr(chain,v))

				nTracks = 0
				nTracks_fromSV = 0
				SV = r.TLorentzVector(0., 0., 0., 0.)
				nPixelHits = 0
				for iTrack in range(chain.Jet_nFirstTrack[iJet], chain.Jet_nLastTrack[iJet]):

					if (chain.Track_nHitAll[iTrack]>8) and (chain.Track_nHitPixel[iTrack]>2) and (chain.Track_pt[iTrack]>1.) and (chain.Track_chi2[iTrack]<5):
						nTracks += 1
						nPixelHits += chain.Track_nHitPixel[iTrack]

						if chain.Track_isfromSV[iTrack]:
							nTracks_fromSV += 1
							track_p4 = r.TLorentzVector(0., 0., 0., 0.)
							track_p4.SetPtEtaPhiM(chain.Track_pt[iTrack], chain.Track_eta[iTrack], chain.Track_phi[iTrack], 0.)
							SV += track_p4

				SV_mass = SV.M()

				setattr(tree, "nTracks", nTracks)
				setattr(tree, "nTracks_fromSV", nTracks_fromSV)
				setattr(tree, "nPixelHits", nPixelHits)
				setattr(tree, "SV_mass", SV_mass)

				tree.fill()


	t2 = time.time()     
	tot_time = t2 - t0     
	print "Read {0:.2f} Mb in {1:.2f} seconds, {2:.2f} ev/s".format(nBytes/1024.0/1024.0, tot_time, chain.GetEntries()/tot_time)   

	# Save tree	
	tree.write()
		
	o.Close()
	print 'Processor finished, all variables saved'


##### Main
if __name__ == "__main__":  

	# Settings  
	
	#dataset = 'chs_RunIII2021'                 
	#skip_events = 0         
	#max_events = 100
	#file_names = ["root://t3se01.psi.ch:1094//store/user/creissel/btag/10_6_X__chs/TTbar_14TeV_TuneCP5_Pythia8/Run3Summer19MiniAOD-106X_mcRun3_2021_realistic_v3-v2/191023_163910/0000/JetTree_mc_1.root"]           
	#puProfile = [55, 60, 65, 70, 75]

        import argparse
        parser = argparse.ArgumentParser(description='Fill histograms with ntuple content by BTagAnalyzer.')
        parser.add_argument('--file', help='files to be processed')
        parser.add_argument('--dataset', help='Label of dataset')
        parser.add_argument('--output', help='Name of output .root file containing the per Jet trees')
        args = parser.parse_args()

        print(args.dataset)
        print(args.file)

	process(args.dataset, [args.file], args.output)

