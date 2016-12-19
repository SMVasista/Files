
#Python program to cluster mutations and pathways with drug response
from __future__ import division
from sys import argv
import pickle
import os
import math

#Defining global variales
training_list = []
pathways_initialized = {}
pathways_selected_for_patients = {}


def UpdatePathwayScores(default_location):
	'''Extracting information from Universal Pathways Repository.Generating a pickle file for pathways score once'''
	if os.path.isfile(default_location+'/list') == False:
		print "Pathway Relationsip Score data not found. Creating from scratch"
		loc_pathways = raw_input("Please enter location of pathways score file: ")
		if os.path.isfile(loc_pathways+'/list') == True:
			pathways = [pathways.split(',')[0] for pathways in open(loc_pathways+'/list')]
			target2 = open(default_location+'/list','w')
			for listed_paths in pathways:
				pathname = str(listed_paths)
				print pathname
				genes_in_pathways = [genes_in_pathways.split(',')[0] for genes_in_pathways in open(loc_pathways+'/'+listed_paths)]
				score_in_pathways = [score_in_pathways.split(',')[1] for score_in_pathways in open(loc_pathways+'/'+listed_paths)]
				score_in_pathways_strip = []
				for elements in score_in_pathways:
					score_in_pathways_strip.append(float(elements))
				listed_paths = dict(zip(genes_in_pathways, score_in_pathways_strip))
				target = open(default_location+'/'+pathname,'w')
				pickle.dump(listed_paths,target)
				target2.write(pathname)
				target2.write('\n')
				target.close()
			target2.close()
			print "Finished creating Pathway Relationship Score data files. Updated in location", default_location
		else:
			print "No list found in", loc_pathways, "to update pathways"
	else:
		print "Pathway Relationship Score data found. Proceeding..."

class Patient:
	def __init__(self):
		self.type = None
		self.gender = None
		self.disease = None
		self.response = None
		self.mutations = {}
		self.pathways = {}
		list_of_pathways = [list_of_pathways.rstrip('\n') for list_of_pathways in open(cwl+'/UpdatedPathwaysScores/list')]
		for component in list_of_pathways:
			pathway_name = str(component)
			self.pathways[pathway_name] = 0

	def source_mutation(self,a_list):
		gene = [gene.split(',')[0] for gene in open(a_list)]
		mut = [mut.split(',')[1] for mut in open(a_list)]
		disease = dict(zip(gene, mut))
		for component in gene:
			if disease[component] == 'OE' or disease[component] == 'OE\n':
				self.mutations[component] = 'GOF'
			elif disease[component] == 'KD' or disease[component] == 'KD\n':
				self.mutations[component] = 'LOF'
		print "Finished sourcing mutations for patient"

	def generate_pathways_signature(self,id,source,dest):
		for mutation in self.mutations:
			for pathway in self.pathways:
				target = open(source+'/'+pathway,'r')
				expanded_pathway = pickle.load(target)
				target.close()
				if mutation in expanded_pathway:
					if self.mutations[mutation] == 'GOF':
						self.pathways[pathway] += expanded_pathway[mutation]
					elif self.mutations[mutation] == 'LOF':
						self.pathways[pathway] += -1*expanded_pathway[mutation]
		target = open(dest+'/'+str(id), 'w')
		pathways_selected_for_patients = dict((k, v) for k, v in self.pathways.items() if v >= 1.5 or v <= -1.5)
		pickle.dump(pathways_selected_for_patients,target)
		pathways_selected_for_patients = {}
		target.close()
		target2 = open(dest+'/list','w')
		target2.write(str(id))
		target2.write('\n')
		target2.close()
		print "Finished generating patient specific pathways data for", id

def Categorize_Drug_Response(givenlist):
	drug_specific_pathways = {}
	list_of_pathways = [list_of_pathways.rstrip('\n') for list_of_pathways in open(cwl+'/UpdatedPathwaysScores/list')]
	for component in list_of_pathways:
		pathway_name = str(component)
		drug_specific_pathways[pathway_name] = 0
	for patient in givenlist:
		patient_name = str(patient)
		patient = Patient()
		patient.response = str(patient_response[patient_name])
		patient.source_mutation(patient_msource[patient_name])
		patient.generate_pathways_signature(patient_name, cwl+'/UpdatedPathwaysScores', cwl+'/PatientPathwaysTraining')
		target = open(cwl+'/PatientPathwaysTraining/'+patient_name,'r')
		patient_pathways = {}
		patient_pathways = pickle.load(target)
		target.close()
		for pathway in patient_pathways:
			if patient.response == 'R':
				drug_specific_pathways[pathway] += float(patient_pathways[pathway])
			elif patient.response == 'N':
				drug_specific_pathways[pathway] += -1*(float(patient_pathways[pathway]))
	print drug_specific_pathways
	target = open(cwl+'/PatientPathwaysTraining/DrugPathways','w')
	pickle.dump(drug_specific_pathways,target)
	target.close()
	print "Finished clustering pathways to drug response"

def ForceWeightage():
	if os.path.isfile(cwl+'/PatientPathwaysTraining/DrugPathways') == True:
		print "Begining to modify pathways weightages... Please type !x when finished"
		target = open(cwl+'/PatientPathwaysTraining/DrugPathways', 'r')
		drug_specific_pathways = pickle.load(target)
		target.close()
		print "Selected pathways:"
		for component in drug_specific_pathways:
			print component, drug_specific_pathways[component]
		while True:
			key = raw_input('Please enter key to be modified: ')
			if key == "!x":
				break
			else:
				value = raw_input('Please enter new value to be appended: ')
				drug_specific_pathways[key] = value
		target = open(cwl+'/PatientPathwaysTraining/DrugPathways', 'w')
		target.truncate()
		pickle.dump(drug_specific_pathways,target)
		target.close()
	else:
		print "pathway score for drugs not created to modify weightages"
	print "Modification completed and stored"


def Calibrate_Response_Coefficients(givenlist):
	calib_patient_pathways = {}
	calib_patient_response_probability = {}
	predicted_response = {}
	actual_response = {}
	positive_corelation_score = 0
	accuracy_by_pvalue = {}
	pset = [ '0.0', '0.1', '0.5', '1', '1.5', '2', '2.5', '5', '10', '15', '20' ]
	if os.path.isfile(cwl+'/PatientPathwaysTraining/DrugPathways') == True:
		if not os.path.exists(cwl+'/CalibrationData'):
			os.makedirs(cwl+'/CalibrationData')
		target0 = open(cwl+'/PatientPathwaysTraining/DrugPathways','r')
		drug_specific_pathways = pickle.load(target0)
		target0.close()
		for calib_patient in givenlist:
			calib_patient_name = str(calib_patient)
			calib_patient = Patient()
			calib_patient.response = str(calib_patient_response[calib_patient_name])
			actual_response[calib_patient_name] = calib_patient.response
			calib_patient.source_mutation(calib_patient_msource[calib_patient_name])
			calib_patient.generate_pathways_signature(calib_patient_name, cwl+'/UpdatedPathwaysScores', cwl+'/CalibrationData')
			target = open(cwl+'/CalibrationData/'+calib_patient_name,'r')
			calib_patient_pathways = pickle.load(target)
			target.close()
			calib_patient_response_probability[calib_patient_name] = 0
			for paths in calib_patient_pathways:
				for selected_paths in drug_specific_pathways:
					if paths == selected_paths:
						print paths
						calib_patient_response_probability[calib_patient_name] += float((calib_patient_pathways[paths] * drug_specific_pathways[selected_paths]))
		for pvalue in pset:
			for calib_patient_name in calib_patient_response_probability:
				if calib_patient_response_probability[calib_patient_name] >= pvalue:
					predicted_response[calib_patient_name] = 'R'
				elif calib_patient_response_probability[calib_patient_name] < pvalue:
					predicted_response[calib_patient_name] = 'N'
			for calib_patient in predicted_response:
				for calib_patient_1 in actual_response:
					if calib_patient_1 != calib_patient:
						break
					else:
						if predicted_response[calib_patient] == actual_response[calib_patient_1]:
							positive_corelation_score += 1
							print "This is a match"
			accuracy_by_pvalue[pvalue] = float(positive_corelation_score/len(calib_patient_response_probability))
		for values in accuracy_by_pvalue:
			print values, ":", accuracy_by_pvalue[values]
		print sorted(accuracy_by_pvalue, key=accuracy_by_pvalue.get)

#def Predict_Patient_Response(aclass):


if __name__ == "__main__":

	cwl = os.path.dirname(os.path.realpath(__file__))

	if not os.path.exists(cwl+'/UpdatedPathwaysScores'):
		os.makedirs(cwl+'/UpdatedPathwaysScores')
	if not os.path.exists(cwl+'/PatientPathwaysTraining'):
		os.makedirs(cwl+'/PatientPathwaysTraining')

	UpdatePathwayScores(cwl+'/UpdatedPathwaysScores')
	
	script, trainlist, caliblist, testlist = argv


	print "Reading training data..."

	patients = [patients.split(',')[0] for patients in open(trainlist)]
	response = [response.split(',')[1] for response in open(trainlist)]
	msource = [msource.split(',')[2] for msource in open(trainlist)]
	mosurce_split = []
	for elements in msource:
		mosurce_split.append(elements.rstrip('\n'))
	patient_response = dict(zip(patients, response))
	patient_msource = dict(zip(patients, mosurce_split))

	print "Finished reading training data"

	Categorize_Drug_Response(patients)
	
	print "Would you like to modify Pathway weightages?"
	modify_status = raw_input('Y/N: ')
	if modify_status == 'Y' or modify_status == 'y':
		ForceWeightage()

	print "Reading data for Calibration..."

	calib_patients = [calib_patients.split(',')[0] for calib_patients in open(caliblist)]
	calib_response = [calib_response.split(',')[1] for calib_response in open(caliblist)]
	calib_msource = [calib_msource.split(',')[2] for calib_msource in open(caliblist)]
	calib_msource_split = []
	for elements in calib_msource:
		calib_msource_split.append(elements.rstrip('\n'))
	calib_patient_response = dict(zip(calib_patients, calib_response))
	calib_patient_msource = dict(zip(calib_patients, calib_msource_split))

	Calibrate_Response_Coefficients(calib_patients)