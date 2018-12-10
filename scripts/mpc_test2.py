	# -*- coding: utf-8 -*-
"""
cyipot: Python wrapper for the Ipopt optimization package, written in Cython.

Copyright (C) 2012 Amit Aides
Author: Amit Aides <amitibo@tx.technion.ac.il>
URL: <http://http://code.google.com/p/cyipopt/>
License: EPL 1.0
"""
#
# Test the "ipopt" Python interface on the Hock & Schittkowski test problem
# #71. See: Willi Hock and Klaus Schittkowski. (1981) Test Examples for
# Nonlinear Programming Codes. Lecture Notes in Economics and Mathematical
# Systems Vol. 187, Springer-Verlag.
#
# Based on matlab code by Peter Carbonetto.
#

import numpy as np
import scipy.sparse as sps
import ipopt
import matplotlib.pyplot as plt
import rospy
# from race.msg import drive_param
# from geometry_msgs.msg import PoseStamped
# import math
# from numpy import linalg as la
# from tf.transformations import euler_from_quaternion, quaternion_from_euler

ts = 0.25


class hs071(object):
	def __init__(self):
		pass
	
	def objective(self, x):
		#
		# The callback for calculating the objective
		#

		# return x[0] * x[3] * np.sum(x[0:3]) + x[2]
		return ((2 - np.sum(x[0]*np.cos(x[1:])*ts)) + 4*(2 - np.sum(x[0]*np.sin(x[1:])*ts)) + ((x[5]-x[4])+(x[4]-x[3])+(x[3]-x[2])+(x[2]-x[1])+x[1]))
		
	def gradient(self, x):
		#
		# The callback for calculating the gradient
		# #
		return np.array([
					 1-np.sum(np.cos(x[1:])*ts) - np.sum(np.sin(x[1:])*ts), 
					 -1 - (ts * x[0]*np.cos(x[1])) + (ts * x[0]*np.sin(x[1])),
					 - (ts * x[0]*np.cos(x[2])) + (ts * x[0]*np.sin(x[2])),
					 - (ts * x[0]*np.cos(x[3])) + (ts * x[0]*np.sin(x[3])), 
					 - (ts * x[0]*np.cos(x[4])) + (ts * x[0]*np.sin(x[4])), 
					 1 - (ts * x[0]*np.cos(x[5])) + (ts * x[0]*np.sin(x[5]))
					 ])
	
	def constraints(self, x):
		#
		# The callback for calculating the constraints
		#
		return np.array([x[5]-x[4] , x[4]-x[3] , x[3]-x[2]  ,  x[2]-x[1],  x[5]  , x[1] , (2 - np.sum(x[0]*np.cos(x[1:])*ts)) , (2 - np.sum(x[0]*np.sin(x[1:])*ts))])
	
	def jacobian(self, x):
		#
		# The callback for calculating the Jacobian
		#
		
		# j = np.concatenate((np.prod(x) / x, 2*x))
		# # print ("jacobian is : ")
		# # print (j)
		return np.array([0,0,0,0,-1,1,
						0,0,0,-1,1,0,
						0,0,-1,1,0,0, 
						0,-1,1,0,0,0,
						0,0,0,0,0,1,
						0,1,0,0,0,0,
						-np.sum(np.cos(x[1:])*ts) , (ts * x[0]*np.sin(x[1])) , (ts * x[0]*np.sin(x[2])) ,  (ts * x[0]*np.sin(x[3])) , (ts * x[0]*np.sin(x[4])) , (ts * x[0]*np.sin(x[5])),
						- np.sum(np.sin(x[1:])*ts) ,  - (ts * x[0]*np.cos(x[1])) ,  - (ts * x[0]*np.cos(x[2])) , - (ts * x[0]*np.cos(x[3])) , - (ts * x[0]*np.cos(x[4])) , - (ts * x[0]*np.cos(x[5]))])

	
	def intermediate(
			self, 
			alg_mod,
			iter_count,
			obj_value,
			inf_pr,
			inf_du,
			mu,
			d_norm,
			regularization_size,
			alpha_du,
			alpha_pr,
			ls_trials
			):

		pass
		# Example for the use of the intermediate callback.
		#
		# print("*****************************************")
		# print("Objective value at iteration #%d is - %g" % (iter_count, obj_value))


	
	
def main():
	#
	# Define the problem
	#
	x0 = [0, 0, 0, 0, 0 ,0 ]
	
	lb = [0, -3, -3, -3, -3, -3 ]
	ub = [8, 3, 3, 3, 3 , 3 ]
	
	cl = [-0.418, -0.428,-0.428, -0.428, 1.512 ,-0.1, 0 , 0 ]
	cu = [0.428, 0.428,0.428, 0.428,  1.512 , 0.1, 100 , 100]

	nlp = ipopt.problem(
				n=len(x0),
				m=len(cl),
				problem_obj=hs071(),
				lb=lb,
				ub=ub,
				cl=cl,
				cu=cu
				)

	#
	# Set solver options
	#
	#nlp.addOption('derivative_test', 'second-order')
	nlp.addOption(b'mu_strategy', b'adaptive')
	nlp.addOption(b'tol', 1e-7)

	#
	# Scale the problem (Just for demonstration purposes)
	#
	nlp.setProblemScaling(
		obj_scaling=2,
		x_scaling=[1, 1, 1, 1, 1, 1]
		)
	nlp.addOption(b'nlp_scaling_method', b'user-scaling')
	
	#
	# Solve the problem
	#
	x, info = nlp.solve(x0)
	
	print("Solution of the primal variables: x=%s\n" % repr(x))

	x_coord = np.zeros(6)
	y_coord = np.zeros(6)
	xdist=0
	ydist=0

	for i in range(len(x)-1):
	    x_coord[i] = xdist
	    y_coord[i] = ydist
	    xdist = xdist + x[0] * np.cos(x[i+1]) *ts
	    ydist = ydist + x[0] * np.sin(x[i+1]) *ts
	x_coord[5] = xdist + x[0] * np.cos(x[5]) *ts
	y_coord[5] = ydist + x[0] * np.sin(x[5]) *ts

	plt.plot(y_coord,x_coord)
	plt.show()



	
	# print("Solution of the dual variables: lambda=%s\n" % repr  (info['mult_g']))
	
	# print("Objective=%s\n" % repr(info['obj_val']))


if __name__ == '__main__':
	main()
