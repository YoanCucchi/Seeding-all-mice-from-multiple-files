import tkinter as tk
from tkinter import filedialog
import csv
import os

def main():
	root = tk.Tk()
	root.withdraw()

	file_paths = []
	while True:
		selected_files = filedialog.askopenfilenames(title="Select files for each mouse containing the 'Average' matrix",
													 filetypes=[("CSV files", "*.csv")])
		if not selected_files:
			break
		file_paths.extend(selected_files)

	if not file_paths:
		print("No files selected.")
		return

	brain_zones_in_all_files = None

	for file_path in file_paths:
		brain_zones = extract_brain_zones(file_path)

		if brain_zones_in_all_files is None:
			brain_zones_in_all_files = brain_zones
		else:
			brain_zones_in_all_files.intersection_update(brain_zones)

	if not brain_zones_in_all_files:
		print("No common brain zones found in the files.")
		return

	output_file_path = filedialog.asksaveasfilename(title="Save the output file",
													defaultextension=".csv",
													filetypes=[("CSV files", "*.csv")])

	if not output_file_path:
		print("No output file selected.")
		return
	file_name_without_extension, _ = os.path.splitext(output_file_path)
	output_file_path = file_name_without_extension + '_All_Average.csv'

	with open(output_file_path, "w", newline='') as csvfile:
		writer = csv.writer(csvfile, delimiter=";")

		for file_path in file_paths:
			average_matrix = extract_average_matrix(file_path)
			cleaned_matrix = remove_uncommon_brain_zones(average_matrix, brain_zones_in_all_files)
			save_cleaned_matrix(cleaned_matrix, file_path, writer)

	print(f"Cleaned 'Average' matrices saved to {output_file_path}")

def extract_brain_zones(file_path):
	with open(file_path, "r") as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		brain_zones = set()
		record = False

		for row in reader:
			if not row:
				continue

			if 'Average' in row[0]:
				record = True
				continue

			if record:
				brain_zones.add(row[0])

	return brain_zones

def extract_average_matrix(file_path):
	with open(file_path, "r") as csvfile:
		reader = csv.reader(csvfile, delimiter=';')

		average_matrix = []
		record = False

		for row in reader:
			if not row:
				continue

			if 'Average' in row[0]:
				record = True

			if record:
				average_matrix.append(row)

	return average_matrix

def remove_uncommon_brain_zones(matrix, common_brain_zones):
	cleaned_matrix = []

	for row in matrix:
		if row[0] in common_brain_zones or row[0] == "":
			cleaned_matrix.append(row)

	columns_to_keep = [0]
	for col_idx in range(len(cleaned_matrix[0])):
		values = [row[col_idx] for row in cleaned_matrix[0:]]
		if "1.0" in values:
			columns_to_keep.append(col_idx)

	final_matrix = [[row[col_idx] for col_idx in columns_to_keep] for row in cleaned_matrix]

	return final_matrix

def save_cleaned_matrix(matrix, original_file_path, writer):
	# Get the correct order of the common brain zones
	correct_order = [row[0] for row in matrix if row[0] != ""]

	# Insert a row with the file name and the common brain zones in the correct order
	header_row = [os.path.basename(original_file_path)] + correct_order
	writer.writerow(header_row)

	# Write the remaining rows of the cleaned matrix
	writer.writerows(matrix)
	writer.writerow([])


if __name__ == "__main__":
	main()