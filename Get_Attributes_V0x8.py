#region README
#Code by: Edgard Melo (edgard.melo@hatch.com) - Belo Horizonte Office Intern - PAT
#Code by: Kirsten Barrie (kristen.barrie@hatch.com) - Saskatoon Office - Mechanical EIT
##Consulting on technical necessities: Luis Moura(luis.moura@hatch.com) - Belo Horizonte Office Senior Engineer - Piping
#date: 2024-09-17 (YYYY-MM-DD)
#version: 0.8
#Belo Horizonte / Saskatoon Offices
#endregion

#region Patch Notes
#********************************************         Patch Notes          ********************************************
#Version 0.8:
#- Added TOPWORKS as one of the excluded items in line 141 of the code.
#- 
#Known Issues:
#- No issues related to the code for now, but we know that we have an issue with Hatch's supports, that depends on fixing on another application
#-
#Future Improvements:
#- working on adding new functions to the code by checking in different projects, what types of components are present
#- continuous support and improvement as needed
#- 
#**********************************************************************************************************************
#endregion

#region Import Section
#*******************************************         Import section        *******************************************
import numpy as np
import sys
import os
import logging
from PyQt5.QtWidgets import QMessageBox
#**********************************************************************************************************************
#endregion

#region Class Section
#*******************************************         Class section        *******************************************
""" No classes defined yet but placed here in case we need to implement them later on"""
#**********************************************************************************************************************
#endregion

#region Function Section
#*******************************************         Function section        *******************************************
#region Data Colletion and Treatment
def get_pxf_array(filename): #working properly
    """
    Reads a file and returns its content as a list of lines, where each line is a list of words.

    Parameters:
    filename (str): The name of the file to read.

    Returns:
    list: A list of lines from the file, where each line is a list of words.
    """
    with open(filename, 'r') as file:
        lines = file.read().splitlines() # Read the file and split it into lines
    
    lines = [line.split() for line in lines if line] # Split each line into a list of words and remove empty words

    
    lines = [line for line in lines if len(line) > 1] # Remove lines that only contain one word

    return lines

def get_reference_coordinates(is_checked, filename, min_diameter): #working properly
    """
    Returns the reference coordinates from a file if the user has checked the reference coordinates.

    Parameters:
    is_checked (bool): Whether the user has checked the box the reference coordinates.
    filename (str): The name of the file to read.

    Returns:
    tuple: The reference coordinates as a tuple of three floats, or (0, 0, 0) if the user has not checked the reference coordinates or if the reference coordinates are not found.
    """
    log_filename = os.path.dirname(filename)
    log_filename = os.path.join(log_filename, 'PCF_Conversion.log')

    logging.basicConfig(filename=log_filename, level=logging.INFO, filemode='w')
    pxf_array = get_pxf_array(filename)
    for line in pxf_array:
            if line[0] == CODE_3000: # Check for the reference coordinates
                Coordenate_X = float(line[1])
                Coordenate_Y = float(line[2])
                Coordenate_Z = float(line[3])
                break

    if is_checked:
        logging.info("** User has checked the reference coordinates to be 0,0,0 **")
        logging.info(f"** Original Coordinates: X: {Coordenate_X} Y: {Coordenate_Y} Z: {Coordenate_Z} **")
        logging.info(f"-----------------------------")
        logging.info(f"min_diameter used: {min_diameter}")
        logging.info(f"-----------------------------")
        return float(Coordenate_X), float(Coordenate_Y), float(Coordenate_Z) # Return the reference coordinates
    elif not is_checked:

        # Check if the coordinates are outside the spatial limits of Caesar II
        if Coordenate_X / (10 ** 8) > 1:
            QMessageBox.warning(None, "Warning", "The project coordinates are likely outside the spatial limits of Caesar II. The model was automatically moved using the option 'Drag model to x=0, y=0 and z=0'")
            logging.warning("!! The project coordinates are likely outside the spatial limits of Caesar II. So the option 'Drag model to x=0, y=0 and z=0' was automatically used !!")
            logging.info(f"** Original Coordinates: X: {Coordenate_X} Y: {Coordenate_Y} Z: {Coordenate_Z} **")
            logging.info(f"-----------------------------")
            logging.info(f"min_diameter used: {min_diameter}")
            logging.info(f"-----------------------------")
            return float(Coordenate_X), float(Coordenate_Y), float(Coordenate_Z)

        if Coordenate_Y / (10 ** 8) > 1:
            QMessageBox.warning(None, "Warning", "The project coordinates are likely outside the spatial limits of Caesar II. The model was automatically moved using the option 'Drag model to x=0, y=0 and z=0'")
            logging.warning("!! The project coordinates are likely outside the spatial limits of Caesar II. So the option 'Drag model to x=0, y=0 and z=0' was automatically used !!")
            logging.info(f"** Original Coordinates: X: {Coordenate_X} Y: {Coordenate_Y} Z: {Coordenate_Z} **")
            logging.info(f"-----------------------------")
            logging.info(f"min_diameter used: {min_diameter}")
            logging.info(f"-----------------------------")
            return float(Coordenate_X), float(Coordenate_Y), float(Coordenate_Z)
        
        logging.info("** User has checked the reference coordinates to be the original coordinates **")
        logging.info(f"** Initial Coordinates: X: {Coordenate_X} Y: {Coordenate_Y} Z: {Coordenate_Z} **")
        logging.info(f"-----------------------------")
        logging.info(f"min_diameter used: {min_diameter}")
        logging.info(f"-----------------------------")
        return 0, 0, 0 # return 0 so the program knows to subtract the original coordinates
    logging.info("Reference coordinates not found")
    return 0, 0, 0 # Return 0 if the reference coordinates are not found
#endregion

#region Special String Generation
def get_no_item_string(array, index, actual_min_diameter, initial_point): #not tested
    """
    Get the string representation of a generic item from the array starting at the given index.

    Parameters:
    array: A 2D list where each sublist has a code at index 0 and a value at index 1.
    index: The index in the array to start looking for the non-item.
    actual_min_diameter: The actual minimum diameter of the non-item.
    initial_point: The initial point of the non-item.

    Returns:
    The string representation of the non-item.
    """
    component_title = ' '.join(str(e) for e in array[index])
    #print(component_title)
    if any(substring in array[index][1] for substring in ['BALLLEVER', 'GEAR', 'BOLT', 'TAP', 'WELD', 'TOPWORKS']):
        logging.info(f"No line returned due to type {component_title}")
        return ""

    component_description = "none"
    diameter, shed = get_txt_values(array, index)

    if float(actual_min_diameter) >= float(diameter):
        logging.info(f"Item {component_title} not added, because of minimum diameter filter, the item has description : {component_description}")
        return ""


    for offset in range(1, len(array) - index - 1):
        if array[index + offset][0] == CODE_2056:
            component_description = ' '.join(str(e) for e in array[index + offset])
        if array[index + offset][0] == CODE_3000:
            item_initial_point = np.array(array[index + offset][1:4], dtype='float') - initial_point
        if array[index + offset][0] == CODE_3020:
            item_final_point = np.array(array[index + offset][1:4], dtype='float') - initial_point
            break

    index += offset
    initial_x, initial_y, initial_z = item_initial_point[:3]
    final_x, final_y, final_z = item_final_point[:3]

    logging.info(f"Item not added fully {component_title} has description : {component_description}")

    return f"\nMISC-COMPONENT\n\nEND-POINT {initial_x} {initial_y} {initial_z} {diameter}\nEND-POINT {final_x} {final_y} {final_z} {diameter}\n"

#region Finishing String
def end_string(array, current_index: int): #not tested
    """
    Generates a string based on the codes and values in the given array starting at the given index. (the original code uses this a lot to finish each item string)

    Parameters:
    array (list): A 2D list where each sublist has a code at index 0 and a value at index 1.
    current_index (int): The index in the array to start generating the string.

    Returns:
    str: The generated string.
    """
    code_action_map = {
        CODE_2051: lambda x: ('COMPONENT-ATTRIBUTE4 S\n' if 'STD' in x else 'COMPONENT-ATTRIBUTE4 XS\n'),           # Schedule
        CODE_2023: lambda x: f"COMPONENT-ATTRIBUTE5 {x}\n",                                                         # Insulation thickness
        CODE_2056: lambda x: f"ITEM-DESCRIPTION  {x}\n",                                                            # Item short description
        #CODE_2022: lambda x: f"WEIGHT  {x}\n",                                                                     # Weight (Don't know if it's needed/helpful to import)
        #CODE_????: lambda x: f"COMPONENT-ATTRIBUTE6 {x}\n",                                                        # Insulation density (still need to find the correct code for it)
    }

    result_strings = []
    for i in range(1, len(array) - current_index - 1):
        code = array[current_index + i][0]
        if code in code_action_map:
            result_strings.append(code_action_map[code](array[current_index + i][1]))
        if code == CODE_3000:
            break

    return "".join(result_strings)
#endregion
#endregion

#region Functions for data treatment
def get_txt_values(array: list, current_index: int) -> tuple: #not sure if it will be working properly, need to test
    """
    Function that gets repeated values, diam and sched. 
    
    Parameters:
    data_array: The Array of data
    current_index: The current index in the array
    
    Returns:
    A tuple containing diam and sched
    """
    sched = ""
    for j in range(1, len(array) - current_index - 1):
        if array[current_index + j][0] == CODE_2040:
            diam = array[current_index + j][1]
        if array[current_index + j][0] == CODE_2051:
            if 'STD' in array[current_index + j][1]:
                sched = 'COMPONENT-ATTRIBUTE4 S\n'
                break
            elif 'XS' in array[current_index + j][1]:
                sched = 'COMPONENT-ATTRIBUTE4 XS\n'
                break
        if array[current_index + j][0] == CODE_3000:
            j -= 1
            break
    return diam, sched

#region Get Pipe
def get_pipe_string(array, current_index, min_diameter, initial_point, inch_or_mm): #not implemented yet
    """
    Get the string representation of a pipe from the array starting at the given index.

    Parameters:
    array: The array of data.
    current_index: The current index in the array.
    actual_min_diameter: The minimum diameter selected by the user.
    initial_point: The initial point of the pipe.

    Returns:
    The string representation of the pipe.
    """
    item_diameter, sched = get_txt_values(array, current_index)
    aux1_diameter = item_diameter
    aux2_diameter = item_diameter

    if float(min_diameter) <= float(item_diameter):
        for i in range(1, len(array) - current_index - 1):
            code = array[current_index + i][0]
            if code == CODE_3000:
                point_0_0 = np.array(array[current_index + i][1:4], dtype='float') - initial_point
            elif code == CODE_3002:
                aux1_diameter = array[current_index + i][1]
            elif code == CODE_3020:
                point_f_0 = np.array(array[current_index + i][1:4], dtype='float') - initial_point
            elif code == CODE_3022:
                aux2_diameter = array[current_index + i][1]
                break
            elif array[current_index + i + 1][0] == CODE_2100:  # need to check if this line is necessary
                break                                           # need to check if this line is necessary  

        x_0_0, y_0_0, z_0_0 = point_0_0[:3]
        x_f_0, y_f_0, z_f_0 = point_f_0[:3]
        ending_string = end_string(array, current_index)
        return f"\nPIPE\n\nEND-POINT {x_0_0} {y_0_0} {z_0_0} {aux1_diameter}\nEND-POINT {x_f_0} {y_f_0} {z_f_0} {aux2_diameter}\n{ending_string}"
    return ""
#endregion

#region Get Tee 
def get_tee_string(array, current_index, min_diameter, initial_point,inch_or_mm): #not implemented yet
    """
    Get the string representation of a tee from the array starting at the given index.

    Parameters:
    array: The array of data.
    current_index: The current index in the array.
    actual_min_diameter: The minimum diameter selected by the user.
    initial_point: The initial point of the tee.
    inch_or_mm: The unit of measurement the file is in.

    Returns:
    The string representation of the tee.
    """
    item_diameter, sched = get_txt_values(array, current_index)
    
    if float(min_diameter)<=float(item_diameter):
        for i in range(1, len(array) - current_index - 1):
            code = array[current_index + i][0]
            if code == CODE_3000:
                point_0 = np.array(array[current_index + i][1:4], dtype='float') - initial_point
            elif code == CODE_3020:
                point_f=np.array(array[current_index + i][1:4], dtype='float') - initial_point
            elif code == CODE_3040:
                point_m=np.array(array[current_index + i][1:4], dtype='float') - initial_point
            elif code == CODE_3042:
                branch_diameter = array[current_index + i][1]
            elif code == CODE_3060:
                point_m1 = np.array(array[current_index + i][1:4], dtype='float') - initial_point
                break
            
        x_0, y_0, z_0 = point_0[:3]
        x_f, y_f, z_f = point_f[:3]
        x_m, y_m, z_m = point_m[:3]
        x_m1, y_m1, z_m1 = point_m1[:3]
        closing_string = end_string(array, current_index)

        return f"\nTEE\n\nEND-POINT {x_0} {y_0} {z_0} {item_diameter}\nEND-POINT {x_f} {y_f} {z_f} {item_diameter}\nCENTRE-POINT {x_m1} {y_m1} {z_m1}\nBRANCH1-POINT {x_m} {y_m} {z_m} {branch_diameter}\n{closing_string}"
    return ""
#endregion

#region Get Flange
def get_flange_weight(flangeclass, flangetype, diam):
        
        """ Get the weight of a flange from the FLWeight.txt file."""
        """ It's important that the user ensures that the file FLWeight.txt is on the same folder as the .exe"""
        try:
            # Determine the base directory depending on how the application is run
            if getattr(sys, 'frozen', False):
                # If the application is running as a bundled executable, use the executable's directory
                basedir = os.path.dirname(sys.executable)
            else:
                # If the application is running as a script, use the script's directory
                basedir = os.path.dirname(os.path.abspath(__file__))

            filepath = os.path.join(basedir, 'FLWeight.txt')
            if os.path.exists(filepath):
                with open(filepath, 'r') as flgm:
                    arrayflg = [line.strip().split(';') for line in flgm]
                    for flange in arrayflg:
                        if flange[0] == flangeclass and flange[2] == flangetype and float(flange[1]) == float(diam):
                            return flange[3]
            else:
                logging.warning(f"File FLWeight.txt not found in directory {basedir}")
                return 0;
        except FileNotFoundError:
            logging.warning(f"File FLWeight.txt not found in directory {basedir}")
            raise FileNotFoundError(f"File FLWeight.txt not found in directory {basedir}")
        return None  

def find_flange_type(array, count): #part of the rewritten code
    """"""
    flange_type_dict = {
        'SLP': 'SO',
        'BLD': 'BL',
        'WNK': 'WN',
        'SW': 'SO',
        'STUB': 'LJ',
        'THD': 'SO'
    }
    for key, val in flange_type_dict.items():
        if key in array[count][1]:
            return val
    return None

def find_diameter_and_class(array, current_index): #part of the rewritten code
    for j in range(1, len(array) - current_index - 1):
        if array[current_index + j][0] == CODE_2040:
            diameter = array[current_index + j][1]
        if array[current_index + j][0] == CODE_2052:
            if 'CL' in array[current_index + j][1]:
                flange_class = array[current_index + j][1]
            else:
                flange_class = 'CL' + array[current_index + j][1]
            return diameter, flange_class
    return None, None

def get_flange_string(array, current_index, min_diameter, initial_point,inch_or_mm): #rewritten code
    """
    Get the string representation of a flange from the array starting at the given index.

    Parameters:
    array: The array of data.
    current_index: The current index in the array.
    min_diameter: The minimum diameter selected by the user.
    initial_point: The initial point of the flange.

    Returns:
    The string representation of the flange.
    """
    flangetype = find_flange_type(array, current_index)
    diam, flangeclass = find_diameter_and_class(array, current_index)
    flangewg = None #initiating the variable with None in case the weight is not found

    if flangetype and diam and flangeclass:
        flangewg = get_flange_weight(flangeclass, flangetype, diam)

    if float(min_diameter) <= float(diam):
        for i in range(1, len(array) - current_index - 1):
            if array[current_index + i][0] == CODE_3000:
                point_0 = np.array(array[current_index + i][1:4], dtype='float') - initial_point
            if array[current_index + i][0] == CODE_3020:
                point_f = np.array(array[current_index + i][1:4], dtype='float') - initial_point
                break

        x_0_0, y_0_0, z_0_0 = point_0[:3]
        x_f_0, y_f_0, z_f_0 = point_f[:3]

        closing_string = end_string(array, current_index)

        if flangewg:
            return f"\nFLANGE\n\nEND-POINT {x_0_0} {y_0_0} {z_0_0} {diam}\nEND-POINT {x_f_0} {y_f_0} {z_f_0} {diam}\nCOMPONENT-ATTRIBUTE8 {flangewg}\n{closing_string}\n"
        else:
            return f"\nFLANGE\n\nEND-POINT {x_0_0} {y_0_0} {z_0_0} {diam}\nEND-POINT {x_f_0} {y_f_0} {z_f_0} {diam}\n{closing_string}\n"
    return ""
#endregion

#region Get Supports
def get_support_string(array, current_index, min_diameter, initial_point,inch_or_mm):
    """
    Get the string representation of a support from the array starting at the given index.

    Parameters:
    array: The array of data.
    current_index: The current index in the array.
    actual_min_diameter: The minimum diameter selected by the user. !!! Not used in the function (possible removal) !!!
    initial_point: The initial point of the support.

    Returns:
    The string representation of the support.
    """
    
    """this first loop is being used to locate the diameter of the support 
    and to stop on that part of the array (using j as a reference)"""
    for j in range(1,len(array)-current_index-1):
        if array[current_index+j][0] == CODE_2040:
            diam=array[current_index+j][1]
            break
    
    #to try to implement the imperial / metric selection
    if inch_or_mm == 'MM':
        Supports_malfunction = 1
    
    if inch_or_mm == 'INCH':
        Supports_malfunction = 25.4


    """this second loop is being used to identify if it's a Hatch support and to get the coordinates of it"""
    for i in range(1,len(array)-current_index-1):
        if array[current_index+j+i][0] == CODE_2106:
            if float(array[current_index+j+i][1])==0:
                Supports_malfunction= Supports_malfunction*1000 #if it's a hatch support, it's multiplying for 1000
        if array[current_index+j+i][0] == CODE_3000:
            point_0=np.array(array[current_index+j+i][1:4],dtype='float')*Supports_malfunction - initial_point
            break
    
    x_0_0,y_0_0,z_0_0   = point_0[:3]
    return "\n"+"SUPPORT"+"\n"+"\n"+"CO-ORDS"+" "+str(x_0_0)+" "+str(y_0_0)+" "+str(z_0_0)+" "+diam+"\n"+"SUPPORT-DIRECTION UP"+"\n"
#endregion

#region Get Elbows
def get_elbow_string(array, current_index, min_diameter, initial_point,inch_or_mm): #just transcribed
    """
    Get the string representation of an elbow from the array starting at the given index.

    Parameters:
    array: The array of data.
    current_index: The current index in the array.
    actual_min_diameter: The minimum diameter selected by the user.
    initial_point: The initial point of the elbow.
    
    Returns:
    The string representation of the elbow.
    """

    item_diameter, sched = get_txt_values(array, current_index)
    point_0, point_m, point_f = None, None, None

    if float(min_diameter) <= float(item_diameter):
        for i in range(1,len(array)-current_index-1):
            key=array[current_index+i][0]
            if key == CODE_3000:
                point_0 = np.array(array[current_index+i][1:4], dtype='float') - initial_point
            elif key == CODE_3020:
                point_m = np.array(array[current_index+i][1:4], dtype='float') - initial_point
            elif key == CODE_3040:
                point_f = np.array(array[current_index+i][1:4], dtype='float') - initial_point
                break
            
        x_0, y_0, z_0 = point_0[:3]
        x_f, y_f, z_f = point_m[:3]
        x_m, y_m, z_m = point_f[:3]
        closing_string = end_string(array, current_index)
        
        #checking if the variables need to be set as strings or not
        return f"\nBEND\n\nEND-POINT {x_0} {y_0} {z_0} {item_diameter}\nEND-POINT {x_f} {y_f} {z_f} {item_diameter}\nCENTRE-POINT {x_m} {y_m} {z_m}\n{closing_string}"
    return ""
#endregion

#region Get Reducers
def get_reducer_string(array, current_index, min_diameter, initial_point,inch_or_mm): #just transcribed
    """
    Get the string representation of a reducer from the array starting at the given index.

    Parameters:
    array: The array of data.
    current_index: The current index in the array.
    actual_min_diameter: The minimum diameter selected by the user.
    initial_point: The initial point of the reducer.

    Returns:
    The string representation of the reducer.
    """
    if 'CON' in array[current_index][1]:
        concentric_reducer = True
    else:
        concentric_reducer = False

    item_diameter, sched = get_txt_values(array, current_index)
 
    if float(min_diameter) <= float(item_diameter):
        for i in range(1,len(array)-current_index-1):
            if array[current_index+i][0] == CODE_3000:
                point_0 = np.array(array[current_index+i][1:4], dtype='float') - initial_point
            elif array[current_index+i][0] == CODE_3002:
                item_diameter = array[current_index+i][1]
            elif array[current_index+i][0] == CODE_3020:
                point_f = np.array(array[current_index+i][1:4], dtype='float') - initial_point
            elif array[current_index+i][0] == CODE_3022:
                item_diameter_final = array[current_index+i][1]
                break
                
        x_0, y_0, z_0 = point_0[:3]
        x_f, y_f, z_f = point_f[:3]
        closing_string = end_string(array, current_index)
        if concentric_reducer:
            return f"\nREDUCER-CONCENTRIC\n\nEND-POINT {x_0} {y_0} {z_0} {item_diameter}\nEND-POINT {x_f} {y_f} {z_f} {item_diameter_final}\n{closing_string}"
        else:
            return f"\nREDUCER-ECCENTRIC\n\nEND-POINT {x_0} {y_0} {z_0} {item_diameter}\nEND-POINT {x_f} {y_f} {z_f} {item_diameter_final}\n{closing_string}"  
    return ""
#endregion

#region Get Gaskets
def get_gasket_string(array, current_index, min_diameter, initial_point, inch_or_mm): #just transcribed
    """
    Get the string representation of a gasket from the array starting at the given index.

    Parameters:
    array: The array of data.
    current_index: The current index in the array.
    min_diameter: The minimum diameter selected by the user.
    initial_point: The initial point of the gasket.

    Returns:
    The string representation of the gasket.
    """
    
    """ The first loop is used to locate the diameter of the gasket """
    for j in range(1,len(array)-current_index-1):
        if array[current_index+j][0] == CODE_2040:
            item_diameter=array[current_index+j][1]
            break
        
    if float(min_diameter)<=float(item_diameter):
        for i in range(1,len(array)-current_index-1):
            if array[current_index+i][0] == CODE_3000:
                point_0 = np.array(array[current_index+i][1:4], dtype='float') - initial_point
            elif array[current_index+i][0] == CODE_3020:
                point_f = np.array(array[current_index+i][1:4], dtype='float') - initial_point
                break
        
        x_0, y_0, z_0 = point_0[:3]
        x_f, y_f, z_f = point_f[:3]
        #closing_string = end_string(array, current_index)
        return f"\nPIPE\n\nEND-POINT {x_0} {y_0} {z_0} {item_diameter}\nEND-POINT {x_f} {y_f} {z_f} {item_diameter}\nITEM-DESCRIPTION GASKET\n"
    return ""
#endregion

#region Get Valves
def get_valve_string(array, current_index, min_diameter, initial_point,inch_or_mm): #just transcribed
    """
    Get the string representation of a valve from the array starting at the given index.

    Parameters:
    array: The array of data.
    current_index: The current index in the array.
    min_diameter: The minimum diameter selected by the user.
    initial_point: The initial point of the valve.

    Returns:
    The string representation of the valve.
    """

    item_diameter, sched = get_txt_values(array, current_index)
    item_diameter_s = item_diameter
    item_diameter_f = item_diameter

    if float(min_diameter) <= float(item_diameter):
        for i in range(1,len(array)-current_index-1):
            if array[current_index+i][0] == CODE_3000:
                point_0 = np.array(array[current_index+i][1:4], dtype='float') - initial_point
            elif array[current_index+i][0] == CODE_3002:
                item_diameter_s = array[current_index+i][1]
            elif array[current_index+i][0] == CODE_3020:
                point_f = np.array(array[current_index+i][1:4], dtype='float') - initial_point
            elif array[current_index+i][0] == CODE_3022:
                item_diameter_f = array[current_index+i][1]
                break

            elif array[current_index+i+1][0] == CODE_2100: #need to check if this line is necessary
                break
        
        x_0, y_0, z_0 = point_0[:3]
        x_f, y_f, z_f = point_f[:3]

        if 'ANG' in array[current_index][1]:
            for d in range(1,len(array)-current_index-1):
                if array[current_index+d][0] == CODE_3022:
                    forDebug2=array[current_index+d][0]
                    data_forDebug2=array[current_index+d][1]
                    item_diameter_f = array[current_index+d][1]
                    break
            for v in range(1,len(array)-current_index-1):
                forDebug=array[current_index+v][0]
                data_forDebug=array[current_index+v][1]
                if array[current_index+v][0] == CODE_3040:
                    point_m=np.array(array[current_index+v][1:4], dtype='float') - initial_point
                    break
            
            x_m, y_m, z_m = point_m[:3]
            
            string1 = f"\nVALVE\n\nEND-POINT {x_0} {y_0} {z_0} {item_diameter}\nEND-POINT {x_m} {y_m} {z_m} 0.5\n"
            return f"{string1}\nVALVE\n\nEND-POINT {x_m} {y_m} {z_m} {item_diameter_f}\nEND-POINT {x_f} {y_f} {z_f} {item_diameter_f}\n" 
        else:
            return f"\nVALVE\n\nEND-POINT {x_0} {y_0} {z_0} {item_diameter_s}\nEND-POINT {x_f} {y_f} {z_f} {item_diameter_f}\n"
    return ""
#endregion

#region Get Nipple
def get_nipple_string(array, current_index, min_diameter, initial_point, inch_or_mm): #not implemented yet
    """
    Get the string representation of a pipe from the array starting at the given index.

    Parameters:
    array: The array of data.
    current_index: The current index in the array.
    actual_min_diameter: The minimum diameter selected by the user.
    initial_point: The initial point of the pipe.

    Returns:
    The string representation of the pipe.
    """
    item_diameter, sched = get_txt_values(array, current_index)
    aux1_diameter = item_diameter
    aux2_diameter = item_diameter

    if float(min_diameter) <= float(item_diameter):
        for i in range(1, len(array) - current_index - 1):
            code = array[current_index + i][0]
            if code == CODE_3000:
                point_0_0 = np.array(array[current_index + i][1:4], dtype='float') - initial_point
            elif code == CODE_3002:
                aux1_diameter = array[current_index + i][1]
            elif code == CODE_3020:
                point_f_0 = np.array(array[current_index + i][1:4], dtype='float') - initial_point
            elif code == CODE_3022:
                aux2_diameter = array[current_index + i][1]
                break
            elif array[current_index + i + 1][0] == CODE_2100:  # need to check if this line is necessary
                break                                           # need to check if this line is necessary  

        x_0_0, y_0_0, z_0_0 = point_0_0[:3]
        x_f_0, y_f_0, z_f_0 = point_f_0[:3]

        return f"\nPIPE\n\nEND-POINT {x_0_0} {y_0_0} {z_0_0} {aux1_diameter}\nEND-POINT {x_f_0} {y_f_0} {z_f_0} {aux2_diameter}\n{sched}ITEM-DESCRIPTION NIPPLE\n"
    return ""
#endregion

#region Get Olets
def get_olet_string(array, current_index, min_diameter, initial_point, inch_or_mm): #just transcribed
    """
    Get the string representation of an olet from the array starting at the given index.

    Parameters:
    array: The array of data.
    current_index: The current index in the array.
    min_diameter: The minimum diameter selected by the user.
    initial_point: The initial point of the olet.
    inch_or_mm: The unit of measurement the file is in.

    Returns:
    The string representation of the olet.
    """
    """ The first loop is used to locate the diameter of the gasket """
    for j in range(1,len(array)-current_index-1):
        if array[current_index+j][0] == CODE_2044:
            item_diameter=array[current_index+j][1]
            break
    
    if float(min_diameter)<=float(item_diameter):
        for i in range(1,len(array)-current_index-1):
            if array[current_index+i][0] == CODE_3000:
                point_0 = np.array(array[current_index+i][1:4], dtype='float') - initial_point
            elif array[current_index+i][0] == CODE_3020:
                point_f = np.array(array[current_index+i][1:4], dtype='float') - initial_point
                break

        x_0, y_0, z_0 = point_0[:3]
        x_f, y_f, z_f = point_f[:3]
        #closing_string = end_string(array, current_index)
        return f"\nPIPE\n\nEND-POINT {x_0} {y_0} {z_0} {item_diameter}\nEND-POINT {x_f} {y_f} {z_f} {item_diameter}\nITEM-DESCRIPTION OLET\n"
    return ""
#endregion

#region Get Cap
def get_pcap_string(array, current_index, min_diameter, initial_point, inch_or_mm):
    """
    Get the string representation of a cap from the array starting at the given index.

    Parameters:
    array: The array of data.
    current_index: The current index in the array.
    actual_min_diameter: The minimum diameter selected by the user.
    initial_point: The initial point of the cap.
    inch_or_mm: The unit of measurement the file is in.

    Returns:
    The string representation of the cap.
    """
    item_diameter, sched = get_txt_values(array, current_index)
    aux1_diameter = item_diameter
    aux2_diameter = item_diameter

    if float(min_diameter) <= float(item_diameter):
        for i in range(1, len(array) - current_index - 1):
            code = array[current_index + i][0]
            if code == CODE_3000:
                point_0_0 = np.array(array[current_index + i][1:4], dtype='float') - initial_point
            elif code == CODE_3002:
                aux1_diameter = array[current_index + i][1]
            elif code == CODE_3020:
                point_f_0 = np.array(array[current_index + i][1:4], dtype='float') - initial_point
            elif code == CODE_3022:
                aux2_diameter = array[current_index + i][1]
                break
            elif array[current_index + i + 1][0] == CODE_2100:  # a break point to ensure that we don't enter the next component
                break                                             

        x_0_0, y_0_0, z_0_0 = point_0_0[:3]
        x_f_0, y_f_0, z_f_0 = point_f_0[:3]

        return f"\nPIPE\n\nEND-POINT {x_0_0} {y_0_0} {z_0_0} {aux1_diameter}\nEND-POINT {x_f_0} {y_f_0} {z_f_0} {aux2_diameter}\n{sched}ITEM-DESCRIPTION CAP\n"
    return ""
#endregion

#region Get Flow Meter
def get_flow_meter_string(array, current_index, min_diameter, initial_point, inch_or_mm):
    """
    Get the string representation of a flow meter from the array starting at the given index.

    Parameters:
    array: The array of data.
    current_index: The current index in the array.
    actual_min_diameter: The minimum diameter selected by the user.
    initial_point: The initial point of the flow meter.
    inch_or_mm: The unit of measurement the file is in.

    Returns:
    The string representation of the flow meter.
    """
    item_diameter, sched = get_txt_values(array, current_index)
    aux1_diameter = item_diameter
    aux2_diameter = item_diameter

    if float(min_diameter) <= float(item_diameter):
        for i in range(1, len(array) - current_index - 1):
            code = array[current_index + i][0]
            if code == CODE_3000:
                point_0_0 = np.array(array[current_index + i][1:4], dtype='float') - initial_point
            elif code == CODE_3002:
                aux1_diameter = array[current_index + i][1]
            elif code == CODE_3020:
                point_f_0 = np.array(array[current_index + i][1:4], dtype='float') - initial_point
            elif code == CODE_3022:
                aux2_diameter = array[current_index + i][1]
                break
            elif array[current_index + i + 1][0] == CODE_2100:  # a break point to ensure that we don't enter the next component
                break                                             

        x_0_0, y_0_0, z_0_0 = point_0_0[:3]
        x_f_0, y_f_0, z_f_0 = point_f_0[:3]

        return f"\nPIPE\n\nEND-POINT {x_0_0} {y_0_0} {z_0_0} {aux1_diameter}\nEND-POINT {x_f_0} {y_f_0} {z_f_0} {aux2_diameter}\n{sched}ITEM-DESCRIPTION FLOW METER\n"
    return ""
#endregion

#region Line String Log
def line_string_log(file_path):
    """
    Function that logs the string of the line in a file.

    Parameters:
    file_path: The path to the file.
    """
    file_name = os.path.basename(file_path)
    logging.info(f"************************************ ^^^ File: {file_name} ^^^ ************************************")

#endregion
#endregion

#**********************************************************************************************************************
#endregion

#region Mapping Section
#*******************************************         Mapping section        *******************************************
""" defining the codes to avoid 'magic numbers' """
CODE_1000 = "1000" # Name of the line
CODE_1001 = "1001" # Metric or imperial identification
CODE_2006 = "2006" # Database Link, for example: '5f7f1a41-1b8f-4235-b764-2f8cdf6a1022' 
CODE_2022 = "2022" # Weight of the component in Kg if in metric and in Lb if in imperial
CODE_2023 = "2023" # Insulation thickness  <-- Important for the current task
CODE_2040 = "2040" # Nominal main size
CODE_2044 = "2044" # 
CODE_2050 = "2050" # Piping spec
CODE_2051 = "2051" # Pipe schedule
CODE_2052 = "2052" # Pressure class
CODE_2053 = "2053" # Line Name/Number
CODE_2055 = "2055" # Long description
CODE_2056 = "2056" # Short description
CODE_2062 = "2062" # Material of the component
CODE_2100 = "2100" # Class name
CODE_2106 = "2106" # 
CODE_3000 = "3000" # Initial point coordinates
CODE_3002 = "3002" # Nominal size at the initial coordinates
CODE_3020 = "3020" # Second point coordinates
CODE_3022 = "3022" # Norminal size at the second coordinates
CODE_3040 = "3040" # Third point coordinates
CODE_3042 = "3042" # Norminal size at the third coordinates
CODE_3060 = "3060" # Fourth point coordinates *used for tees*
#**********************************************************************************************************************
#endregion