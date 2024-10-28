#Here all the global settings and required information for the application is set

import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#=======================================global settings
configuration_file_path:str = None
source_directory:str = "C:\\Schanner\\DDM_16_april_2024\\Elasto_Plastic\\Source"                       
destination_directory:str = "C:\\Users\\PC\\Desktop\\DDM_Algo\\results"
input_file_name:str = "Surface_2.csv"
x_amount:int = 100   # How many points to work on - X Axis
y_amount:int = 100   # How many points to work on - Y Axis
decimal_accuracy:int = 9    #Maximum value is 30.
innerloop_convergance_upper_bound:float = 0.01
outerloop_calculations_kernel_size:int = 3
maximum_pressure:float = 15000       #Mega Pascal
calculation_time_in_seconds:float = 0.0 #it gets updated after each calculation
#=======================================Set Parameters for Plots
z_axis_3d_plot:float = 0.00003
image_color_pallet:str = 'rainbow'        #'red' is not a valid value for cmap; supported values are 'Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Grays', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_grey', 'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 
                                        #'gist_yerg', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r', 'grey', 'hot', 'hot_r', 'hsv', 'hsv_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 'magma_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r', 'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'turbo', 'turbo_r', 'twilight', 'twilight_r', 'twilight_shifted', 'twilight_shifted_r', 'viridis', 'viridis_r', 'winter', 'winter_r'
#=======================================Set Parameters of Loading CSV files (File.py > __load__ class)
separator:str = ';'
decimal_character:str = ','
encode_type:str = "ISO-8859-1"
basic_encode_type:str = "utf8"
skip_rows:int = 15
take_these_rows:int = 18    #it is nrows=18 in pandas read_CSV() method
header = None

#=======================================Set Parameters for G and F coefficients
coefficient_kernel_length:int = 7
EPrime:int = 115000
instead_of_zero:float = 0.233
laplac_padding_mode:str = 'wrap'                #other values: 'reflect' and 'mirror'
fast_fourier_transform_norm:str = 'ortho'       #other values: 'backward', 'forward'; read the scipy manual for further information.
signal_convolve_mode:str = 'valid'                  #other values: 'full', 'same'; read the scipy manual for further information.
signal_convolve_method:str = 'fft'                  #other values: 'direct', 'auto'; read the scipy manual for further information.
signal_convolve_2d_mode:str = 'valid'                  #other values: 'full', 'same'; read the scipy manual for further information.
signal_convolve_2d__boundry:str = 'wrap'                #other values: 'fill', 'symm'; read the scipy manual for further information.
image_convolve_mode:str = 'wrap'                    #other values: 'reflect', 'mirror'; read the scipy manual for further information.
#=======================================Set Parameters of Algorithm
approach_distance:float = 9.0                   #The S factor of DDM.
padding_size:int = 4                            #How many pixels do you want to pad the matrixes before starting the calculations.
initial_pressure: float = 150.0
data_type:float = 'float64'                      #Matrices are using this data type. It can change for calculation optimisation
initial_pressure_over_padded_points:float = 0.0
p_type:str = 'mirrored_lt'                       #other values: 'None', 'mirrored_rb'
#=======================================After Preprocess run, this variables are Updated
x_interval:float = None
y_interval:float = None
R_max:float = None
R_min:float = None
R_max_location:tuple = None
R_min_location:tuple = None
#=======================================Aij convergence accuracy
Aij_convergance_upper_bound:float = 0.01               #Note that increasing the accuracy (smaller number) leades to decrease in calculatio speed
##=======================================This scope checkes wether to load the configurations from a file or use the default values have set above================================================================================
if(configuration_file_path is not None): 
    pass
