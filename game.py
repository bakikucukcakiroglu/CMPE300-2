# Hasan Baki Kucukcakiroglu 2018400141
# Mirac Batuhan Malazgirt 	2018400156
# Working succesfully
# Use "mpiexec -n [P] python game.py input.txt output.txt" command to execute.


from mpi4py import MPI
import numpy as np
import sys


comm = MPI.COMM_WORLD							# Creates multi-processors environment. 
rank = comm.Get_rank()							# Initialize ranks from 0 to size-1.
size = comm.Get_size()							# Gets size from command line argument. 
p_num = size+1
worker_num=size-1								# Woker size is size-1. Because first processor is main processor. 


if rank == 0:

	with open(sys.argv[1]) as f:

		lines = f.readlines() 					#Takes all lines from input file.
		lines= [line.strip() for line in lines] #Gets rows. Deletes leading and trailing spaces.

		parameters=lines[0].split()				# Splits first line which includes N, W and T.

		N=int(parameters[0])					# N, dimension of table. Table is N*N.
		global W
		W=int(parameters[1])					# Wave number of simulation.
		T=int(parameters[2])					# Number of towers that will be inserted each wave.

	
		for i in range(0, W):					# For each wave, this part of code takes two line of input file. Organises and split the data. Send datas to correspondin processors exclusively. 

			global interval_width				# How many row a processor responsible for
			interval_width= N//worker_num 	

			o_coordinates= lines[i*2+1].split(", ") # List of tower 'o' coordinates. They are kept as strings such that '3 0'.(row 3, column 0) We have to split them and convert to integer.
			p_coordinates=lines[i*2+2].split(", ")	# List of tower '+' coordinates. They are kept as strings such that '3 0'.(row 3, column 0) We have to split them and convert to integer.

			line_list=[]  							# List of lists of datas of all rows. It includes lists that keeps row data. Each row list keeps two map. First keeps tower 'o' coordinates, second keeps tower 'p' coordinates.

			for p in range(0, N):					# From 0 to N-1, we create lists of row data(one list for each row). Each row data list will be insterted to line_list that keeps all row lists.

				map_o={}							# Map that keeps tower 'o' locations. It keeps locations like {1:3}. That means in the p'th row and 1th column, there is an o tower with health 3. 
				map_p={}							# Map that keeps tower '+' locations. It keeps locations like {2:4}. That means in the p'th row and 2th column, there is an o tower with health 4. 
				list_p=[]

				for o in o_coordinates:				# Fills the map_o with the coordinates of tower 'o's in the corresponding row. It initializes their health as 6.

					row=int(o.split()[0])			
					column=int(o.split()[1])

					if(row==p):

						map_o[column]=6

				for pp in p_coordinates:			# Fills the map_p with the coordinates of tower '+'s in the corresponding row. It initializes their health as 6.

					row=int(pp.split()[0])
					column=int(pp.split()[1])

					if(row==p):

						map_p[column]=8

				list_p.append(map_o)				# Insert map_o and map_p to the data list of the row. 
				list_p.append(map_p)

				line_list.append(list_p)			# Insert data list of the row to the list of data lists of rows.

			for processor_number in range(1, worker_num+1):

				data=[]

				for r in range((processor_number-1)*interval_width,processor_number*interval_width):

					data.append(line_list[r])

				data.append(W)

				comm.send(data, dest=processor_number, tag=10) #tag=0 tower datası

	with open(sys.argv[2], "w") as file1:						# Opens output file with the name that is taken from command line argument.

		final_data=[]											# Final data to keep all rows that is coming from different processors.

		for ppp in range(1, worker_num+1):						# It appends all rows coming from different processors to the final data.

			final_data.append( comm.recv(source=ppp, tag=5))	

		for rows_final in final_data:							# Iterares over list of row lists of different processors.

			for k in range(0,len(rows_final)-1):				# Iterate over rows of corresponding processors.

				for b in range(0,N):							# Iterate over N different column index. 

					if(b in rows_final[k][0].keys() ):			# Checks if there is a tower 'o' in the final output.

						file1.write('o')

					elif(b in rows_final[k][1].keys() ):		# Checks if there is a tower '+' in the final output.

						file1.write('+')	

					else: 										# If there is no tower in the corresponding index. Puts '.'

						file1.write('.')
					if(b!=N-1):
						file1.write(' ')

				file1.write('\n')

else:
	m=0
	processor_local_data=[[]]
	if(m==0):
		processor_local_data=comm.recv(source=0, tag=10)		# Takes data from main processor for first wave. Since it is first wave, it just assign th data to local processor data.


	for w in range(0, processor_local_data[-1]):				# Takes data from main processor for waves except first wave. It makes tower insertions at the beginning of every wave. Start rounds. 
																# After rounds end. Deletes dead towers. Iterates these operations for all waves. 	
		if(m==0):
			m=m+1

		else:
			data=comm.recv(source=0, tag=10)					# Incoming data from main processor. 
			for i in range(0, len(processor_local_data)-1):		# It iterates all rows of data of the corresponding processor. If there is no tower in the coordinates to be insterted, insters the tower. Otherwise, skips.

				data_row= data[i]
				local_data_row=processor_local_data[i]

				for o_coor in list(data_row[0].keys()):																		# Iterates over incoming the row datas of processor to add tower 'o's to local processor data if it is possible.

					if (o_coor not in list(local_data_row[0].keys()) and  o_coor not in list(local_data_row[1].keys())): 	# Checks if there is any kind of tower in the coordinates to be inserted. 

						local_data_row[0][o_coor]=6																			# If there is no tower, insert corresponding tower. Initializes its health.

				for p_coor in list(data_row[1].keys()):																		# Iterates over incoming the row datas of processor to add tower '+'s to local processor data if it is possible.

					if (p_coor not in list(local_data_row[1].keys()) and p_coor not in list(local_data_row[0].keys())):		# Checks if there is any kind of tower in the coordinates to be inserted. 

						local_data_row[1][p_coor]=8																			# If there is no tower, insert corresponding tower. Initializes its health.

		width= len(processor_local_data)-1
		
		for rounds in range(1,9):   											# Rounds starts.

			neighbour_lower=[{},{}]												# Keeps lower row taken from lower processor.
			neighbour_upper=[{},{}]												# Keeps upper row taken from upper processor.

			if(rank%2==1):														# If processor is odd-ranked.

				comm.send(processor_local_data[-2], dest=rank+1, tag=10) 		# Odd-ranked sends its lower bound row to even-ranked processor below.

				if(rank!=1): 													# First processor cannot send to or receive from upper processor.

					neighbour_upper=comm.recv(source=rank-1, tag=10)			# Odd-ranked recieves its upper neighbour row from even-ranked processor above..
					comm.send(processor_local_data[0], dest=rank-1, tag=10) 	# Odd-ranked sends its upper bound row to even-ranked processor above.

				neighbour_lower= comm.recv(source=rank+1, tag=10) 				# Odd-ranked recieves its lower neighbour row from even-ranked processor below.

			else:																# If processor is even-ranked.

				neighbour_upper=comm.recv(source=rank-1, tag=10) 				# Even-ranked recieves its upper neighbour row from odd-ranked processor above..

				if(rank!=worker_num):											# Last processor cannot send to or receive from lower processor.

					comm.send(processor_local_data[-2], dest=rank+1, tag=10) 	# Even-ranked sends its lower bound row to odd-ranked processor below.
					neighbour_lower=comm.recv(source=rank+1, tag=10)			# Even-ranked recieves its lower neighbour row from odd-ranked processor below.

				comm.send(processor_local_data[0], dest=rank-1, tag=10) 		# Even-ranked sends its upper bound row to odd-ranked processor above.

			rows_delete_o=[]													# Keeps 'o' tower coordinates (row indexed list, just keeps columns) that will be deleted at the end of round.
			rows_delete_p=[]													# Keeps '+' tower coordinates (row indexed list, just keeps columns) that will be deleted at the end of round.
			for row in range(0, len(processor_local_data)-1):					# Fight starts. Checks all towers of the processor. Calculates their damages taken. 

				row_delete_o=[]													# Keeps 'o' tower coordinates for the corresponding row that will be deleted at the end of the round.									
				row_delete_p=[]													# Keeps 'o' tower coordinates for the corresponding row that will be deleted at the end of the round.

				for map_o_key in list(processor_local_data[row][0].keys()):		# Checks 'o' towers. Checks their neighbour coordinates to obtain if there are any enemy tower or not. 

					damage=0  													# Initializes count of damage as 0.

					if(map_o_key+1 in processor_local_data[row][1].keys()):		# If there is a enemy tower at the right.

						damage=damage+1
					if(map_o_key-1 in processor_local_data[row][1].keys()):		# If there is a enemy tower at the left.
						damage=damage+1

					if(row-1==-1):#en üst row için								# If it is first row. Instead of checking upper row, it checks upper neighbour row taken from upper neighbour processor.

						if(map_o_key in neighbour_upper[1].keys()):
							damage=damage+1
					else: 
						if(map_o_key in processor_local_data[row-1][1].keys()):	#Checks upper row. Looks the above index. 
							damage=damage+1		

					if(row==len(processor_local_data) -2):						# If it is last row. Instead of checking lower row, it checks lower neighbour row taken from lower neighbour processor.

						if(map_o_key in neighbour_lower[1].keys()):
							damage=damage+1

					else: 
						if(map_o_key in processor_local_data[row+1][1].keys()):	#Checks lower row. Looks the below index. 
							damage=damage+1	
				

					processor_local_data[row][0][map_o_key]=processor_local_data[row][0][map_o_key]-(2*damage)  # If a tower has a health of zero or below. It is inserted to lists of towers to be deleted at the end of the round.

					if(processor_local_data[row][0][map_o_key]<=0):

						row_delete_o.append(map_o_key)

				for map_p_key in list(processor_local_data[row][1].keys()): 	# Checks '+' towers. Checks their neighbour coordinates to obtain if there are any enemy tower or not. 

					damage=0

					if(map_p_key+1 in processor_local_data[row][0].keys()): 	# If there is a enemy tower at the right.
						damage=damage+1

					if(map_p_key-1 in processor_local_data[row][0].keys()):		# If there is a enemy tower at the left.
						damage=damage+1

					if(row-1==-1):												# If it is first row. Instead of checking upper row, it checks upper neighbour row taken from upper neighbour processor.

						if(map_p_key in neighbour_upper[0].keys()):				# Looks above.
							damage=damage+1
						if(map_p_key+1 in neighbour_upper[0].keys()):			# Looks above right.
							damage=damage+1
						if(map_p_key-1 in neighbour_upper[0].keys()):			# Looks above left.
							damage=damage+1
					
					else:														#Checks upper row. 
						
						if(map_p_key+1 in processor_local_data[row-1][0].keys()): 	# Looks above right.

							damage=damage+1
						if(map_p_key-1 in processor_local_data[row-1][0].keys()): 	# Looks above left.
							damage=damage+1
						if(map_p_key in processor_local_data[row-1][0].keys()): 	# Looks above.
							damage=damage+1


					if(row==len(processor_local_data) -2):						# If it is last row. Instead of checking lower row, it checks lower neighbour row taken from lower neighbour processor

						if(map_p_key in neighbour_lower[0].keys()):				# Looks below.
							damage=damage+1
						if(map_p_key+1 in neighbour_lower[0].keys()):			# Looks below right.
							damage=damage+1
						if(map_p_key-1 in neighbour_lower[0].keys()):			# Looks below left.
							damage=damage+1

					else: 														#Checks lower row. Looks the below index. 

						if(map_p_key+1 in processor_local_data[row+1][0].keys()):	# Looks below right.

							damage=damage+1
						if(map_p_key-1 in processor_local_data[row+1][0].keys()):	# Looks below left.
							damage=damage+1
						if(map_p_key in processor_local_data[row+1][0].keys()):		# Looks below.
							damage=damage+1


					processor_local_data[row][1][map_p_key]=processor_local_data[row][1][map_p_key]-damage	# If a tower has a health of zero or below. It is inserted to lists of towers to be deleted at the end of the round.

					if(processor_local_data[row][1][map_p_key]<=0): 				
						row_delete_p.append(map_p_key)

				rows_delete_o.append(row_delete_o)
				rows_delete_p.append(row_delete_p)

			for s in range(0, len(processor_local_data)-1):				# Checks all rows of the processor. Deletes all towers to be deleted.

				for d in rows_delete_o[s]:								# Deletes the 'o' towers to be deleted. 

					del processor_local_data[s][0][d]

				for d2 in rows_delete_p[s]:								# Deletes the 'o' towers to be deleted. 

					del processor_local_data[s][1][d2]


	comm.send(processor_local_data, dest=0, tag=5) 						# Sends all row datas to the main processor.


