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
"Jet_hadronFlavour"
]

perEvent_Variables = [
"nPUtrue"
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
	parser.add_argument('--filelist', help='files to be processed')
	args = parser.parse_args()

	f = open(args.filelist, "r")
	dataset = f.readline().rstrip()[1:-1]
	files = [l.rstrip() for l in f][1:]
	print(dataset)
	print(files)
	output_file = dataset + ".root"

	process(dataset, files, output_file)

