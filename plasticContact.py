import ContactMechanics.CommandLineInterface
import ContactMechanics.CommandLineInterface.HardWall
import numpy as np
import matplotlib.pyplot as plt
import time

from SurfaceTopography import Topography, PlasticTopography
from ContactMechanics import FreeFFTElasticHalfSpace
from ContactMechanics.Factory import make_plastic_system
from ContactMechanics.Tools.Logger import screen
import ContactMechanics


#========================================================================
def get_domain_area(dx:float, dy:float, shape:tuple ) -> float:
    return (dx*dy*shape[0]*shape[1])*1e-3*1e-3

def get_force(pressure_nom:float, area_total_surface:float) -> float:
    return pressure_nom*area_total_surface
#========================================================================

def run_plastic_contact_model(dx_:float, dy_:float, shape_:tuple, pressure_:float, 
                              roughness_path_:str, hardness_:float, 
                              Es_:float=210000,penetration_:float = 0.000001,maximum_iteration_:int=10000, 
                              projected_area_:float= None, projected_tolerance:float= 0.04) -> tuple:
    
    
    dx=dx_
    dy= dy_
    #roughness = np.genfromtxt('./CSV_NEW/AN01_Höhe.csv',delimiter=',')
    roughness = np.genfromtxt(roughness_path_,delimiter=',')[:shape_[0],:shape_[1]]
    #_min = np.min(roughness)
    #if(_min <0):
    #    _min = abs(_min)
    #roughness += _min
    #
    roughness *= 0.001

    nx:int = shape_[0] #mesh size
    ny:int = shape_[1] #mesh size
    sx = nx*dx*1e-3 # mm physical length in direction x
    sy = ny*dy*1e-3 # mm

    print("physical length: (",sx,",",sy,")\n")
    #========================================================================
    domain_area = get_domain_area(dx=dx,dy=dy, shape=(nx,ny))
    calculated_force = get_force(pressure_nom=pressure_, area_total_surface=domain_area)
    #========================================================================

    topography= Topography(roughness, physical_sizes=(sx, sy) ) 

    Es = Es_ # MPa
    hardness = hardness_ # MPa - This is the maximum pressure


    #nb_grid_pts = number of grid points = (128,128)
    _substrate = FreeFFTElasticHalfSpace(nb_grid_pts=topography.nb_grid_pts, young=Es, physical_sizes=topography.physical_sizes)
    system = make_plastic_system(
                substrate = _substrate, 
                surface= PlasticTopography(topography=topography, hardness=hardness)
            )

    external_forces = [calculated_force]
    for force in external_forces:
        print("\ncalculated force: ",force,"\n")

    penetration = penetration_ #on mm => 0.000001 is 1 micrometer
    disp0 = np.zeros(system.substrate.nb_domain_grid_pts) # all zeroes
    disp0[system.surface.subdomain_slices] = system.surface.heights() + penetration #calculate height out of surface ----- IS THIS LIKE WHAT WE HAVE in OUR DDM or it simply gives the Roughness height!? It is roughness height not like our DDM
    disp0 = np.where(disp0 > 0, disp0, 0) # Only Consideres the heights bigger than 0 !!?? So, non-negetive displacement
    #plt.imshow(disp0)
    #plt.show()


    #SIMULATE
    # prepare empty arrays to contain results
    offsets = []
    plastic_areas = []
    contact_areas = []
    forces = np.zeros((len(external_forces), *topography.nb_grid_pts)) # forces[timestep,...]: array of forces for each gridpoint
    print(forces.shape)
    plt.imshow(forces[0])
    plt.colorbar()
    #plt.show()
    elastic_displacements = np.zeros((len(external_forces), *topography.nb_grid_pts))
    plastified_topographies = []

    i=0

    current_time = time.time()

    for external_force in external_forces:
        sol = system.minimize_proxy(external_force=external_force, #load controlled
                                    #mixfac = 1e-4,
                                    initial_displacements=disp0,
                                    pentol=None, # for the default value I had some spiky pressure fields during unloading - is it convergence criteria?
                                    logger=screen,
                                    maxiter = maximum_iteration_,
                                    ) # display informations about each iteration
        #minimize_proxy returns a solution named sol
        assert sol.success
        disp0 = system.disp #now that solution is successfully asserted the displacement is updated
        offsets.append(system.offset)
        plastic_areas.append(system.surface.plastic_area)
        contact_areas.append(system.compute_contact_area())
        
        plastified_topographies.append(system.surface.squeeze())
        #system.surface=PlasticTopography(topography=topography, hardness=hardness) # reset surface
        forces[i,...] = system.force
        elastic_displacements[i, ...] = system.disp[system.surface.subdomain_slices]
        
        i+=1
        #print(np.max(system.surface.plastic_displ))
        #print(np.min(system.surface.plastic_displ))


    current_time = time.time() - current_time
    print("\n\n=====================\ncalculation time for 7 different Force loads: ",current_time,"\n=====================\n\n")
    #PLOT pressure distributin and deformed profile

    #ContactMechanics.CommandLineInterface.HardWall.save_pressure()



    forces_sum = np.sum(forces[0])
    print("forces sum:",forces_sum)
    n = nx*ny
    print("pressure nominal: ",forces_sum/domain_area) 

    contact_points_sum = np.sum(forces > 0)
    platic_points_sum = sum(1 for x in plastic_areas if x > 0)
    domain_points_total = nx*ny
    projected_area = contact_points_sum/domain_points_total
    projected_area_plastic = platic_points_sum/domain_points_total
    print("Projected area - In contact Area:",projected_area)
    print("Projected area - Plastic Area:",projected_area_plastic)


    for i in range(len(external_forces)):
        
        fig, (axf, axfcut, axtopcut) = plt.subplots(1,3, figsize=(14,3))
        
        axf.set_xlabel("x (mm)")
        axf.set_ylabel("y (mm)")
        
        axfcut.plot(system.surface.positions()[0], forces[i, :, ny//2]/ system.area_per_pt)
        axfcut.set_xlabel("x")
        axfcut.set_ylabel("pressures MPa")
        
        for a in (axfcut, axtopcut):
            a.set_xlabel("x (mm)")
        axtopcut.set_ylabel("height (mm)")
        
        plt.colorbar(axf.imshow(forces[i,...]/ system.area_per_pt, extent=[-sx/2, sx/2, -sy/2, sy/2]), label="pressures MPa", ax = axf)
        axf.set_aspect(1)
        
        axtopcut.plot(system.surface.positions()[0][:,0], topography.heights()[:, ny//2], 
                    color="k", label = "original")
        axtopcut.plot(system.surface.positions()[0][:,0], plastified_topographies[i].heights()[:, ny//2], 
                    color = "r", label="plast.")
        axtopcut.plot(system.surface.positions()[0][:,0], plastified_topographies[i].heights()[:, ny//2] - elastic_displacements[i,:, ny//2], 
                    c="b", label="plast. el.")
        axtopcut.legend()
        
        fig.tight_layout()
        plt.show()




    #Scalar quantities during loading

    #1
    fig, ax = plt.subplots()

    ax.plot(offsets, external_forces,"+-")
    ax.set_xlabel("rigid body penetration [mm]")
    ax.set_ylabel("Force [N]")



    #2
    fig, ax = plt.subplots()

    ax.plot(external_forces, plastic_areas, "-+")
    ax.set_xlabel("Force (N)")
    ax.set_ylabel("plastic area (mm^2)")
    fig.tight_layout()

    #3
    fig, ax = plt.subplots()

    ax.plot(external_forces, contact_areas, "+-")
    ax.set_xlabel("indentation force (N)")
    ax.set_ylabel("contact area (mm^2)")
    fig.tight_layout()


if __name__ == "__main__":
    roughness_path:str = "./AN01_Höhe.csv"
    run_plastic_contact_model(dx_=1.112,
                              dy_=1.112,
                              shape_= (1000,500),
                              pressure_= 100, #100Mpa
                              roughness_path_= roughness_path,
                              hardness_= 3500, #Maximum Pressure as MPa
                              Es_=210000,
                              penetration_=0.000001,
                              maximum_iteration_=10000)











