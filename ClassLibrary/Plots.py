import Configuration
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import os
import Configuration
import Preprocess
import comparison
import extensions 
import datetime

def Plot_3D_Surface(x_values_1dArray,y_values_1dArray,height_2DMatrix):

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    # Make data.
    X, Y = np.meshgrid(x_values_1dArray, y_values_1dArray)
    

    # Plot the surface.
    surf = ax.plot_surface(X, Y, height_2DMatrix, cmap=cm.coolwarm,
                        linewidth=0, antialiased=False)

    # Customize the z axis.
    ax.set_zlim(-(Configuration.z_axis_3d_plot), Configuration.z_axis_3d_plot)
    ax.zaxis.set_major_locator(LinearLocator(10))
    # A StrMethodFormatter is used automatically
    ax.zaxis.set_major_formatter('{x:.05f}')

    # Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=5)

    plt.show()

def Plot_Hmap(array:np.ndarray):
    plt.imshow(array, cmap=Configuration.image_color_pallet)  # 'gray' colormap for grayscale visualization
    plt.colorbar()  # Add a color bar to show intensity scale
    plt.show()

def Multiplot_Hmap_runtime(preprocessor:Preprocess.Preprocessor, directoryToWrite:str) -> None:
    # Create an empty dictionary to store the dataframes
    csv_files = {}
    csv_files["Roughness_Matrix"]= preprocessor.Roughness_Matrix
    csv_files["Height_Matrix"]= preprocessor.Height_Matrix
    csv_files["Height_Matrix2"]= preprocessor.Height_Matrix
    csv_files["Delast_Matrix"]= preprocessor.Delast_Matrix
    csv_files["P_Matrix"]= preprocessor.P_Matrix
    csv_files["Dplast_Matrix"]= preprocessor.Dplast_Matrix

    
    row = 2
    column = 3
    fig, axs = plt.subplots(row,column)
    
    i:int = 0
    j:int = 0
    for key, value in csv_files.items():
        axs[i,j].set_xticks([])
        axs[i,j].set_yticks([])
        axs[i,j].imshow(value, cmap=Configuration.image_color_pallet)
        axs[i,j].set_title(key)
        axs[i,j].set_xticks(np.arange(value.shape[1]))
        axs[i,j].set_yticks(np.arange(value.shape[0]))
        axs[i,j].set_aspect('auto')
        j += 1
        if(j == column):
            j = 0
            i = i+1
    
    now = datetime.datetime.now()
    custom_format = '%Y_%m_%d'
    today = now.strftime(custom_format)
    S_aggregate_values = comparison.get_s_aggregate(preprocessor=preprocessor)
    footer = f"Date: {today} - Duration:  {extensions.format_time(seconds=Configuration.calculation_time_in_seconds)} ({round(Configuration.calculation_time_in_seconds,4)} s) - size: ({Configuration.x_amount},{Configuration.y_amount})"
    footer += "\n"
    footer += f"P_Mean:{S_aggregate_values["Pmean"]} -- S_Average: {S_aggregate_values["Average"]} -- S_Max: {S_aggregate_values["Max"]} -- S_Min: {S_aggregate_values["Min"]}"
    plt.figtext(0.5, 0.01, footer, ha='center', va='center', fontsize=5)
    filename = os.path.join(directoryToWrite, "plot.png")
    plt.savefig(filename, dpi=600, bbox_inches='tight')
    plt.tight_layout()
    plt.show()


def Multiplot_Hmap_from_files(directoryToRead:str) -> None:
    # Create an empty dictionary to store the dataframes
    csv_files = {}

    # Loop through all files in the folder
    for file_name in os.listdir(directoryToRead):
        # Check if the file has a .csv extension
        if file_name.endswith('.csv'):
            # Create the full file path
            file_path = os.path.join(directoryToRead, file_name)
            # Read the csv file into a numpy ndarray
            ndarray = np.genfromtxt(file_path, delimiter=',')
            # Store the ndarray in the dictionary
            csv_files[file_name] = ndarray
    
    row = 2
    column = 3
    fig, axs = plt.subplots(row,column)
    
    i:int = 0
    j:int = 0
    for key, value in csv_files.items():
        axs[i,j].set_xticks([])
        axs[i,j].set_yticks([])
        axs[i,j].imshow(value, cmap=Configuration.image_color_pallet)
        axs[i,j].set_title(key)
        axs[i,j].set_xticks(np.arange(value.shape[1]))
        axs[i,j].set_yticks(np.arange(value.shape[0]))
        axs[i,j].set_aspect('auto')
        j += 1
        if(j == column):
            j = 0
            i = i+1
    
    now = datetime.datetime.now()
    custom_format = '%Y_%m_%d'
    today = now.strftime(custom_format)

    footer = f"Date: {today} - Duration:  {extensions.format_time(seconds=Configuration.calculation_time_in_seconds)} ({round(Configuration.calculation_time_in_seconds,4)} s) - size: ({Configuration.x_amount},{Configuration.y_amount})"
    plt.figtext(0.5, 0.01, footer, ha='center', va='center', fontsize=5)
    filename = os.path.join(directoryToRead, "plot.png")
    plt.savefig(filename, dpi=600, bbox_inches='tight')
    plt.tight_layout()
    plt.show()


def show_3d_image(roughness_matrix:np.ndarray) -> None:
    # Create a 2D matrix of roughness values (example data)
    rows, cols = roughness_matrix.shape
    x = np.linspace(-21, 21, cols)
    y = np.linspace(-5, 5, rows)
    x, y = np.meshgrid(x, y)

    # Example roughness values (z-values) as a 2D Gaussian distribution
    #z = np.exp(-(x**2 + y**2))

    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the surface
    surf = ax.plot_surface(x, y, roughness_matrix, cmap='viridis', edgecolor='none')

    # Add a color bar to show the mapping of values to colors
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)

    # Customize the plot (optional)
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Roughness')

    plt.show()


