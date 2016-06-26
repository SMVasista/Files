#Python program to simulate biological reaction

from __future__ import division

#import math

def ror_smm(v,k,s):
	return v*s/(k+s)
#return (math.sin (s/k)) * v

def ror_rma(kf,kr,a1,a2,p1):
	return (kf*a1*a2) - (kr*p1)

def ror_tro(kf,kr,a,b):
	return (kf*a) - (kr*b)

#Initial Conditions
#Simulating Lotka-Volterra Equation
#dS1/dt = k1*A*S1 - k2*S1*S2
#dS2/dt =  k2*S1*S2 - k3*S2
MEK = 0.1
MEK_p = 0
MEK_pp = 0
MEK_ppp = 0
k1 = 0.01
ENZ = 0.1
I = 0.1
I_p = 0

for i in range(1,2001): #50000 is simulation time in seconds

#Dynamic parameters in calling order

#Reactions simulation
	
#Updated Concentrations
#	A = A*0.999
	MEK = MEK - MEK_p
	MEK_p = MEK_p + 1.1*ENZ*MEK*((1+MEK)**-1) - MEK_pp
	MEK_pp = MEK_pp + 1.1*ENZ*MEK_p*((1+MEK_p)**-1) - MEK_ppp
	MEK_ppp = MEK_ppp + 1.1*ENZ*MEK_pp*((1+MEK_pp)**-1) -k1*MEK_ppp
#	I = I - I_p
#	I_p = I_p + 1.1*MEK_pp*I*((1+I)**-1) - k1*I_p
	
#Output
	print MEK,MEK_p,MEK_pp,MEK_ppp





