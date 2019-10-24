# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 11:36:40 2019

@author: christina reissel
"""

import numpy as np
import ROOT as r
#import rootpy
#from rootpy.tree import Tree
#from rootpy.io import root_open
import time

def_var = {
"Jet_DeepFlavourBDisc" : (0, 1.0, 10000),
"Jet_DeepFlavourCvsLDisc" : (0, 1.0, 10000),
"Jet_DeepFlavourCvsBDisc" : (0, 1.0, 10000),
}

variables = def_var.keys()

# Function to create histograms
def process(dataset, file_names, output, PU): 

	# Adding all files to TChain    
	chain = r.TChain("btagana/ttree")     
	for file_name in file_names:         
		print "Adding file {0}".format(file_name)         
		chain.AddFile(file_name)         
	print "Chain contains {0} events".format(chain.GetEntries())     
	
	# Error in case more events shall be processed than accessible
	#if skip_events > chain.GetEntries() or skip_events + max_events > chain.GetEntries():         
	#	raise Exception("Asked to process events [{0}, {1}) but chain contains only {1}".format(skip_events, skip_events + max_events, chain.GetEntries())) 

	# Output file
	o = r.TFile.Open(output, 'update')

	# Create dictionary with histograms
	histograms = {}
	for flv in ["bjet", "cjet", "ljet"]:
		histograms.update({'{0}_{2}_{1}'.format(dataset, v, flv) : r.TH1F('{0}_{2}_{1}'.format(dataset, v, flv), " ", def_var[v][2],def_var[v][0],def_var[v][1]) for v in variables})
		for puBin in PU:
			histograms.update({'{0}_{2}_{1}_PU{3}'.format(dataset, v, flv, puBin) : r.TH1F('{0}_{2}_{1}_PU{3}'.format(dataset, v, flv, puBin), " ", def_var[v][2],def_var[v][0],def_var[v][1]) for v in variables})

	#total number of bytes read     
	nBytes = 0     
	t0 = time.time()     
	t1_old = t0     
	
	# Looping over events
	for iEv in range(0, chain.GetEntries()):         
		nBytes += chain.GetEntry(iEv)                 
		if iEv % 100 == 0:             
			t1_new = time.time()            
			print "time per 100 ev: {0:.2f}".format((t1_new - t1_old))             
			t1_old = t1_new                 

		#do something with event
		chain.GetEntry(iEv)
	
		# Looping over jets
		for iJet in range(chain.nJet):
			if chain.Jet_pt[iJet] >= 30 and abs(chain.Jet_eta[iJet]) <= 2.5:
				if chain.Jet_hadronFlavour[iJet] == 5:
					for v in variables:
						histograms['{0}_bjet_{1}'.format(dataset, v)].Fill((getattr(chain,v)[iJet]))
					for puBin in PU:
						if chain.nPUtrue <= puBin:
							for v in variables:
								histograms['{0}_bjet_{1}_PU{2}'.format(dataset, v, puBin)].Fill((getattr(chain,v)[iJet]))
                                if chain.Jet_hadronFlavour[iJet] == 4:
                                        for v in variables:
                                                histograms['{0}_cjet_{1}'.format(dataset, v)].Fill((getattr(chain,v)[iJet])) 
                                        for puBin in PU:
                                                if chain.nPUtrue <= puBin:
                                                        for v in variables:
                                                                histograms['{0}_cjet_{1}_PU{2}'.format(dataset, v, puBin)].Fill((getattr(chain,v)[iJet]))

                                if chain.Jet_hadronFlavour[iJet] == 0:
                                        for v in variables:
                                                histograms['{0}_ljet_{1}'.format(dataset, v)].Fill((getattr(chain,v)[iJet]))
                                        for puBin in PU:
                                                if chain.nPUtrue <= puBin:
                                                        for v in variables:
                                                                histograms['{0}_ljet_{1}_PU{2}'.format(dataset, v, puBin)].Fill((getattr(chain,v)[iJet]))

	t2 = time.time()     
	tot_time = t2 - t0     
	print "Read {0:.2f} Mb in {1:.2f} seconds, {2:.2f} ev/s".format(nBytes/1024.0/1024.0, tot_time, chain.GetEntries()/tot_time)   

	# Save histograms	

	for h in histograms.keys():
		histograms[h].Write()
		
	o.Close()
	print 'Processor finished, all histogrames saved'


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
	parser.add_argument('--puBinning', help='binning for PU')

	args = parser.parse_args()

	f = open(args.filelist, "r")
	dataset = f.readline().rstrip()[1:-1]
	files = [l.rstrip() for l in f][1:]
	print(dataset)
	print(files)
    	puBinning = [int(x) for x in args.puBinning.split(",")]

	output_file = dataset + ".root"

	process(dataset, files, output_file, puBinning)

