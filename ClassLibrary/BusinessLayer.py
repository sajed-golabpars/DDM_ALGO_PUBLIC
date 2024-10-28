from numpy import ndarray

import Configuration
import extensions
import File
import Preprocess
import Filters
import Numerical_methods
import Objects
import Deflections
from Pressure import Pressure_kernel
import Neighborhoods
import Plots
import time
import comparison
from datetime import datetime

#--------------------------------------------------------------------- Check the convolution part in the step 9 (calculation of the far contributions). It seems there need some changes.
#--------------------------------------------------------------------- Check the step 6. It is interesting to note that the P_old is updated before going to the next point so it have to require an iteration!!!!!!!!!!!
class algorithm_logic():

    def __init__(self) -> None:
        self._p_matrix:ndarray = None
        self.file_manager = File.Manager()
        self.preprocessor = Preprocess.Preprocessor()
        self.coefficients = Filters.Coefficients()
        self.transformations = Numerical_methods.Transformations()
        self.matrix_calculations = Numerical_methods.Matrix_calculations()
        self.parameters = Objects.claculation_parameters()
        self.pressure_kernel = Pressure_kernel()
        self.neighbors = Neighborhoods.Calculations()
    @property
    def P_Matrix(self,) ->ndarray:
        return self.preprocessor.P_Matrix

    def run(self):
        #steps 1 and 2 --- Note: All the required Matrices are defined
        self.file_manager = File.Manager()
        print("Loading data...")
        self.file_manager.Load.from_csv(encode_type=Configuration.encode_type)
        print("Preprocessing ...")
        self.preprocessor.run(roughness_data_frame=self.file_manager.Loaded_CSV,
                       roughness_header_rows=self.file_manager.Loaded_CSV_header)
        #steps 3 and 4
        print("Preparation of Coeficients: G and F and their Laplacian")
        self.coefficients.generate_G_coeficient_axisymmetric()
        self.coefficients.generate_G_coeficient_wrapped_around()
        self.coefficients.generate_F_coefficient_axisymmetric()
        self.coefficients.generate_F_coeficient_wrapped_around()
        #step 5
        self.coefficients.G_Fourier_coefficint_wrapped_around = self.transformations.get_fast_fourier_transorm_2d(numpy_array_2d=self.coefficients.G_coefficint_wrapped_around)
        self.coefficients.F_Fourier_coefficint_wrapped_around = self.transformations.get_fast_fourier_transorm_2d(numpy_array_2d=self.coefficients.F_coefficint_wrapped_around)
        
        #calculation of B Coefficients to be used in step 10
        print("Preparation of Coeficients: B and B0")
        self.parameters.B_coefficient_B00excluded , self.parameters.B0 = self.neighbors.get_B_Coefficients_Bexluded_and_B00(DeltaX=Configuration.x_interval, DeltaY=Configuration.y_interval)

        #Iterations begin. steps 6 to 14. All the parameters that are generaing in each step are stored in self.parameter object
        time_counter = time.time() 
        print(f'Calculation Start - time: {datetime.now()}')
        #step 6 and 7
        _i_length,_j_length = self.preprocessor.Roughness_Matrix.shape
        for i in range(_i_length):
            #check if the i is not in the padded points:
            if((i < Configuration.padding_size) or (i > _i_length - Configuration.padding_size -1)):
                continue #skip
            for j in range(_j_length):
                #check if the j is not in the padded points:
                if((j < Configuration.padding_size) or (j > _j_length - Configuration.padding_size -1)):
                    continue #skip
                
                #outer loop _ lets provide a simple condition so it has only one sweep over each point _This condition has to be changed based on the requirements of the problem 
                outer_loop_counter = 0
                while(outer_loop_counter < 1):
                    outer_loop_counter += 1

                    #calculation of pressure kernel for the location (i,j)
                    self.parameters.P_kernel = self.pressure_kernel.get_p_kernel(self.preprocessor.P_Matrix,
                                                                                 location=(i,j),p_type=Configuration.p_type)
                    self.parameters.P_kernel_fourier = self.transformations.get_fast_fourier_transorm_2d(numpy_array_2d=self.parameters.P_kernel)
                    #Step 6.
                    #calculation of Delast for point (i,j)
                    self.parameters.Delast_ij_value_DDMethod = Deflections.get_Delast_ij_value(g_coefficient_fourier_2d_array_wrapped_around=self.coefficients.G_Fourier_coefficint_wrapped_around,
                                                                                            p_kernel_fourier=self.parameters.P_kernel_fourier)
                    #Step 7.
                    #calculation of Delast_laplace for point (i,j)
                    self.parameters.Delast_laplace_ij_value_DDMethod = Deflections.get_Delast_laplace_ij_value(f_coefficient_fourier_2d_array_wrapped_around = self.coefficients.F_Fourier_coefficint_wrapped_around,
                                                                                            p_kernel_fourier=self.parameters.P_kernel_fourier)
                    #Step 8. Calculating the Hmax and Hi0j0
                    #-----------------------------calculate the Hmax
                    i0,j0 = self.preprocessor.Min_Point #Note that finding i0 and j0 might be required to solve the harmonic problem for the avaiable roughness/height matrix
                    self.parameters.Delast_i0j0 = self.preprocessor.Delast_Matrix[i0][j0]
                    self.parameters.Hmax = self.preprocessor.get_Hmax_using_available_S(Delast_i0j0=self.parameters.Delast_i0j0)
                    #-----------------------------calculate the Hi0j0
                    self.parameters.Hi0j0 = self.parameters.Hmax ########Note: It resets to Hmax in every iteration. Should it recalculated with some formula?
                    #-----------------------------Update the calculated Delast_ij (using DDMethod)
                    self.preprocessor.Delast_Matrix[i,j] = self.parameters.Delast_ij_value_DDMethod
                    #Calculating the Hij_old --> suffix "old" in the "Hij_old" means the Hij which is calculated in the previous iteration.
                    self.parameters.Hij_old = self.preprocessor.get_the_calculated_Hij_old(Delast_i0j0=self.parameters.Delast_i0j0,
                                                                                           Hmax=self.parameters.Hmax,
                                                                                           point=(i,j))
                    #-----------------------------Update the new calculated H for the point (i,j) in the H matrix
                    if(extensions.safe_float_comparison(a=self.parameters.Hij_old,b= self.preprocessor.Height_Matrix[i,j],decimal_accuracy=3)):
                        pass #this means the Hij_old has no change. This criteria and a similar one for the Pij_old has to be checked as a convergence criteria for outer loop!!!!!!!!!!!
                    else:
                        self.preprocessor.Height_Matrix[i,j] = self.parameters.Hij_old

                    #step 9. Inner loop initialization
                
                    convergence_difference:float = 1000

                    while(convergence_difference > Configuration.innerloop_convergance_upper_bound):
                        print('i:',i,' - ','j:',j, ' - Hij:', self.preprocessor.Height_Matrix[i,j],' is the active point',end="\r")
                        self.parameters.update_F00(F_Coefficient= self.coefficients.F_coefficint_axisymmetric)                                                                #self.parameters.F00
                        self.parameters.Pij = self.preprocessor.P_Matrix[i,j]                                       #self.parameters.Pij
                        self.parameters.F00_Pold_ij = float(self.parameters.Pij * self.parameters.F00)              #self.parameters.F00_Pold_ij
                        self.parameters.update_F_Kernel_IJexcluded_3x3(Fij=self.coefficients.F_coefficint_axisymmetric) #self.parameters.F_Kernel_IJexcluded
                        self.parameters.crop_P_Kernel_3x3(P_Matrix=self.preprocessor.P_Matrix,location=(i,j))                     #self.parameters.Pold_Kernel -> it is P_near_neighbors
                        self.parameters.far_contributions = self.neighbors.get_far_contributions(Delast_laplacian_ij=self.parameters.Delast_laplace_ij_value_DDMethod
                                                             ,F00_Pold_ij= self.parameters.F00_Pold_ij
                                                             ,base_array = self.parameters.P_Kernel_3x3
                                                             ,kernel = self.parameters.F_Kernel_IJexcluded_3x3)
                        #Note: B Coefficient will be calculated only once so it is calculated outside the loops after Step 5.

                        self.parameters.RHSij = self.parameters.far_contributions - self.preprocessor.Roughness_Matrix_Laplacian[i,j]
                        self.parameters.update_height_kernel_3x3(location=(i,j), Preprocessor=self.preprocessor, Hmax= self.parameters.Hmax, Rmin= Configuration.R_min, Delast_i0j0= self.parameters.Delast_i0j0)                                                  #self.neighbors_Height_Kernel_3x3
                        self.parameters.update_Dplast_near_neighbors_3x3(Dplast_matrix= self.preprocessor.Dplast_Matrix, location=(i,j))
                        #calculate B Landa
                        self.parameters.B_landa_summation = self.neighbors.get_B_landa_summation(B_Matrix= self.parameters.B_coefficient_B00excluded
                                                                                                 , D_plast_Matrix= self.parameters.Dplast_near_neighbors_3x3
                                                                                                 , F_kernel= self.parameters.F_Kernel_IJexcluded_3x3
                                                                                                 , H_Matrix= self.parameters.neighbors_height_kernel_3x3
                                                                                                 , P_Matrix= self.parameters.P_Kernel_3x3)
                        
                        self.parameters.Aij_eq20 = self.parameters.B0*(float(self.preprocessor.Height_Matrix[i,j])) - self.preprocessor.Dplast_Matrix[i,j] - self.parameters.F00_Pold_ij
                        self.parameters.Aij_eq21 = self.parameters.RHSij - self.parameters.B_landa_summation

                        #Step 11.
                        #Apply Contact Conditoin (22)
                        self.parameters.Pij_new = 0.0
                        self.parameters.Hij_new = 0.0
                        self.parameters.Dplast_ij_new = 0.0
                        self.parameters.F0_Pmax = self.parameters.F00*Configuration.maximum_pressure
                        #Set a new variable for Aij to proceed the calculations
                        self.parameters.Aij = self.parameters.Aij_eq21

                        #first Check
                        if (self.parameters.Aij < 0):
                            self.parameters.Pij_new = 0.00
                            self.parameters.Dplast_ij_new = 0.00
                            self.parameters.Hij_new = self.parameters.Aij/self.parameters.B0
                        elif ((self.parameters.Aij > 0) and (self.parameters.Aij < (-1)*self.parameters.F0_Pmax)):
                            self.parameters.Pij_new = (-1)*(self.parameters.Aij/self.parameters.F00)
                            self.parameters.Dplast_ij_new = 0.00
                            self.parameters.Hij_new = 0.00
                        elif(self.parameters.Aij > (-1)*self.parameters.F0_Pmax):
                            self.parameters.Pij_new = Configuration.maximum_pressure
                            self.parameters.Dplast_ij_new = (-1)*((self.parameters.Aij + self.parameters.F0_Pmax)/self.parameters.B0)
                            self.parameters.Hij_new = 0.0
                        else: #Aij = 0.00
                            raise Exception('Aij is 0. Please check your entries')



                        self.parameters.update_H_P_Dplast_cached_5x5(location=(i,j), preprocessor=self.preprocessor) # to increase the performance, it might be possible to be set in the outer loop not here in the inner loop
                        self.parameters.Hij_cached_5x5[self.parameters.centerindex_5x5,self.parameters.centerindex_5x5] = self.parameters.Hij_new
                        self.parameters.Pij_cached_5x5[self.parameters.centerindex_5x5,self.parameters.centerindex_5x5] = self.parameters.Pij_new
                        self.parameters.Dplast_cached_5x5[self.parameters.centerindex_5x5,self.parameters.centerindex_5x5] = self.parameters.Dplast_ij_new

                        #Control Parameters
                        loop_counter = 1
                        cycle_counter = 1

                        #Check Convergence of Aij
                        delta_Aij: float = abs(self.parameters.Aij - self.parameters.Aij_previous)
                        while(delta_Aij > Configuration.Aij_convergance_upper_bound):
                            self.parameters.Aij_previous = self.parameters.Aij
                            

                            self.parameters.Aij_eq20 = self.parameters.B0*(float(self.preprocessor.Height_Matrix[i,j])) - self.preprocessor.Dplast_Matrix[i,j] - self.parameters.F00_Pold_ij
                            self.parameters.Aij_eq21 = self.parameters.RHSij - self.parameters.B_landa_summation
                            #Set a new variable for Aij to proceed the calculations
                            self.parameters.Aij = self.parameters.Aij_eq21
                            #Next Checks
                            if (self.parameters.Aij < 0):
                                self.parameters.Pij_new = 0.00
                                self.parameters.Dplast_ij_new = 0.00
                                self.parameters.Hij_new = self.parameters.Aij/self.parameters.B0
                            elif ((self.parameters.Aij > 0) and (self.parameters.Aij < (-1)*self.parameters.F0_Pmax)):
                                self.parameters.Pij_new = (-1)*(self.parameters.Aij/self.parameters.F00)
                                self.parameters.Dplast_ij_new = 0.00
                                self.parameters.Hij_new = 0.00
                            elif(self.parameters.Aij > (-1)*self.parameters.F0_Pmax):
                                self.parameters.Pij_new = Configuration.maximum_pressure
                                self.parameters.Dplast_ij_new = (-1)*((self.parameters.Aij + self.parameters.F0_Pmax)/self.parameters.B0)
                                self.parameters.Hij_new = 0.0
                            else: #Aij = 0.00
                                raise Exception('Aij is 0. Please check your entries')

                            #Here we have different Options: 1. To replace all the neighbor points with Pij_new 2. To not change the already calculated neighbor points and change only the othe points with Pij_new 3. the same as approach 2 but this time instead of Pij_new, calculating Pij for remaining neighbor points so the mean value of all neighbor points would be Pij_new   
                            self.parameters.update_P_kernel_3x3(approach=2)

                            delta_Aij: float = abs(self.parameters.Aij - self.parameters.Aij_previous)
                            if(delta_Aij < Configuration.Aij_convergance_upper_bound):
                                self.preprocessor.P_Matrix[i,j] = self.parameters.Pij_new
                                self.preprocessor.Height_Matrix[i,j] = self.parameters.Hij_new
                                self.preprocessor.Dplast_Matrix[i,j] = self.parameters.Dplast_ij_new

                                self.parameters.Aij_previous = 1000         #reset to avoid similarity equivalence in next steps

                                break
                                


                        #Update this line --- Currently, it allows only one cycle
                        convergence_difference = Configuration.innerloop_convergance_upper_bound

                    #extensions.print_as_DataFrame(numpy_array=self.parameters.P_kernel,
                    #                      caption="self.parameters.P_kernel")
                    #extensions.print_as_DataFrame(numpy_array=self.parameters.P_kernel_fourier,
                    #                      caption="self.parameters.P_kernel_fourier")

        time_counter = time.time() - time_counter
        print(f'Calculation Finished Successfully - Time: {datetime.now()} - Duration = {time_counter} seconds')
        Configuration.calculation_time_in_seconds = time_counter
        
        #---------------------STORE RESULTS -----------------
        dict_matrices = { "Roughness": self.preprocessor.Roughness_Matrix
                         ,"Height": self.preprocessor.Height_Matrix
                         ,"Pressure": self.preprocessor.P_Matrix
                         ,"Dplast": self.preprocessor.Dplast_Matrix
                         ,"Delast": self.preprocessor.Delast_Matrix
                         }
        resultsDirectory:str = self.file_manager.Save.to_csv_make_auto_directory(ndarrays_dictionary=dict_matrices)
        Plots.show_3d_image(roughness_matrix=self.preprocessor.Roughness_Matrix)
        Plots.Multiplot_Hmap_runtime(preprocessor=self.preprocessor,directoryToWrite= resultsDirectory) #Show all data in a plot


        #---------------------TEST DATA -----------------
        
        #extensions.print_as_DataFrame(numpy_array=self.coefficients.G_coefficint_axisymmetric,
        #                                  caption="G_coefficint_axisymmetric")
        #extensions.print_as_DataFrame(numpy_array=self.coefficients.G_coefficint_wrapped_around,
        #                                  caption="G_coefficint_wrapped_around")
        #extensions.print_as_DataFrame(numpy_array=self.coefficients.F_coefficint_axisymmetric,
        #                                  caption="F_coefficint_axisymmetric")
        #extensions.print_as_DataFrame(numpy_array=self.coefficients.F_coefficint_wrapped_around,
        #                                  caption="F_coefficint_wrapped_around")
        

        import numpy as np
        #plot.Plot_3D_Surface(coefficients.mesh_row_x_axis,coefficients.mesh_row_y_axis,np.array(coefficients.gxy_AxiSymmetric))
        #Plots.Plot_3D_Surface(self.coefficients.mesh_row_x_axis,self.coefficients.mesh_row_y_axis,np.array(self.coefficients.G_coefficint_axisymmetric))
        #plot.Plot_3D_Surface(coefficients.mesh_row_x_axis,coefficients.mesh_row_y_axis,np.array(coefficients.gxy_Axi_Symmetric))
        #Plots.Plot_3D_Surface(self.coefficients.mesh_row_x_axis,self.coefficients.mesh_row_y_axis,np.array(self.coefficients.F_coefficint_axisymmetric))
        #------------------------------------------------
        
        