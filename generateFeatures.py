import argparse
import os
import numpy as np
from scipy.io import wavfile
import operator
import sys
from features import mfcc

debugging = True
DEFAULT_COEFFICIENTS = 10


########################
# HIGH-LEVEL FUNCTIONS
########################

def run(coefficients, outputFilename):

	info("Creating file " + outputFilename + "...")

	output = open(outputFilename, 'w')

	features = generateAttributes(coefficients)
	writeArffAttributes(features, output)

	maleFilenames, femaleFilenames = getAudioFiles()
	info("Found " +
	     str(len(maleFilenames)) + " male recordings and " +
	     str(len(femaleFilenames)) + " female recordings.")

	info("Generating features...")
	data = generateFeatureData(maleFilenames, femaleFilenames, coefficients)
	writeArffData(data, output)

	info("Done.")

def generateAttributes(coefficients):
	features = []
	for i in range(coefficients):
		n = i + 1
		feature = ("coefficient" + str(n), "Continuous")
		features.append(feature)
	features.append( ("gender", ["male", "female"]) )
	return features

def generateFeatureData(maleFilenames, femaleFilenames, coefficients):
	data = []
	for filename in maleFilenames:
		features = generateFeatures(filename, "male", coefficients)
		data.append(features)
	for filename in femaleFilenames:
		features = generateFeatures(filename, "female", coefficients)
		data.append(features)
	return data


####################
# AUDIO PROCESSING
####################

def generateFeatures(filename, outputClass, coefficients):
	instance = []

	# Read the audio file.
	sampFreq, data = wavfile.read(filename)

	# Compute cepstral coefficients for each window
	mfcc_feat = mfcc(data, samplerate=sampFreq, numcep=coefficients)
	# Compute mean vector from ceptral coefficients
	mean_vector = mfcc_feat.mean(axis=0)
	for i in range(0, len(mean_vector)):
		instance.append(str(mean_vector[i]))

	# Add the output class too.
	instance.append(outputClass)

	return instance

########################
# ARFF FILE GENERATION
########################

def writeArffAttributes(features, output):
	output.write("@relation voiceCepstrums\n\n")
	for feature in features:
		key = feature[0]
		value = feature[1]
		if type(value) == list:
			output.write("@attribute " + key + " {" + ", ".join(value) + "}\n")
		else:
			output.write("@attribute " + key + " " + value + "\n")
	output.write("\n")

def writeArffData(data, output):
	output.write("@data\n")
	for instance in data:
		first = True
		for feature in instance:
			if not first:
				output.write(", ")
			output.write(str(feature))
			first = False
		output.write("\n")


##############
# FILESYSTEM
##############

def getAudioFiles():
	files = []
	for f in os.walk("AudioRecordings"):
		files.append(f)
	femaleFilenames = prepareAudioFilenames(files[1][2], "AudioRecordings/Female/")
	maleFilenames = prepareAudioFilenames(files[2][2], "AudioRecordings/Male/")
	return maleFilenames, femaleFilenames

def prepareAudioFilenames(filenames, prefix):
	filtered = filter(lambda filename: filename.endswith(".wav") or filename.endswith(".WAV"), filenames)
	return map(lambda filename: prefix+filename, filtered)


##############
# UTILITIES
##############

def info(message):
	print message

def debug(message):
	if debugging:
		print message


########
# MAIN
########

if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog='Feature Generator', description='CS478 Group Project: Speaker gender prediction based on a short phrase', add_help=True)
	parser.add_argument('-c', '--coefficients', type=int, action='store', help='The number of Cepstrum coefficients to generate', default=DEFAULT_COEFFICIENTS)
	parser.add_argument('output', metavar="output", type=str, action='store', help='The ARFF file to save to')

	args = parser.parse_args()
	coefficients = args.coefficients
	outputFilename = args.output

	run(coefficients, outputFilename)