import numpy as np
from sys import exit
import imas
import logging
logging.basicConfig(level=logging.DEBUG, filename='./output.log',filemode='w')
import time
import re
import os
 
def Find_grid_subset(grid_ggd,subset_name):
    # Searches for the subset with given name return subset index or -1 if search has failed
    ind = -1
    try:
        nr_subset = len(grid_ggd[0].grid_subset.array)
    except:
        logging.error('supplied object has no attribute grid_subset')
    else:
        for sub_id in range(nr_subset):
            sub_name = grid_ggd[0].grid_subset[sub_id].identifier.name
            if ( sub_name.lower() == subset_name.lower()):
                ind = sub_id

    return ind;

def Find_ion_specie(ggd, nucleus_charge):
    # Searches for the index of ion with given nuclei charge
    # Igonres molecular ions and other complex chemical stuff
    # Returns the list of isotopes associated with the given nucleus charge
    # If none found returns an empty list 
    isotope_list = []
    try:
        nr_ion = len(ggd[0].ion.array)
    except:
        logging.error('supplied object has no attribute ion')
    else:
        for ion_id in range(nr_ion):
            if ( (len(ggd[0].ion[ion_id].element.array) == 1) and (ggd[0].ion[ion_id].element[0].z_n == nucleus_charge) and (ggd[0].ion[ion_id].element[0].atoms_n == 1. ) ):
                isotope_list.append(ion_id)

    return isotope_list;


def Find_neut_specie(ggd, nucleus_charge):
    # Searches for the index of the ions with given nuclei charge
    # Includes simple molecules, complex ones are ignored
    # Returns the list of isotopes associated with the given nucleus charge
    # and second array with number of neucleus per particle
    # If none found returns an empty list 
    isotope_list = []
    isotope_count = []
    try:
        nr_neut = len(ggd[0].neutral.array)
    except:
        logging.error('supplied object has no attribute neutral')
    else:
        for neut_id in range(nr_neut):
            if ( (len(ggd[0].neutral[neut_id].element.array) == 1) and (ggd[0].neutral[neut_id].element[0].z_n == nucleus_charge) ):
                isotope_list.append(neut_id)
                isotope_count.append(ggd[0].neutral[neut_id].element[0].atoms_n)

    return isotope_list, isotope_count;

def SOLPS_target_loads_read(profiles, transport, slice_info):

    # Information about the time slice
    i_time       = slice_info["i_time"]
    shot         = slice_info["shot"  ]
    run          = slice_info["run"]

    # Constants
    H1_pot  = 1.35984340e+01
    He1_pot = 2.45873876e+01
    He2_pot = 5.44177630e+01
    eV2J    = 1.60217663e-19
    amu2kg  = 1.66054e-27


    # Output variables, _i - inner target, _o - outer
    ne_i = []   # electron density              [m^-3]
    flxi_i = [] # fuel ions flux                [m^-2s^-1]
    flxn_i = [] # fuel neutral flux             [m^-2s^-1]
    te_i = []   # electorn temperature          [eV]
    ti_i = []   # ion temperature               [eV]
    pwre_i = [] # power loads with electorns    [W/m^2] 
    pwri_i = [] # power loads with ions         [W/m^2] 
    pwrn_i = [] # power loads with neutrals     [W/m^2] 
    ne_o = []   # electron density              [m^-3]
    flxi_o = [] # fuel ions flux                [m^-2s^-1]
    flxn_o = [] # fuel neutral flux             [m^-2s^-1]
    te_o = []   # electorn temperature          [eV]
    ti_o = []   # ion temperature               [eV]
    pwre_o = [] # power loads with electorns    [W/m^2] 
    pwri_o = [] # power loads with ions         [W/m^2] 
    pwrn_o = [] # power loads with neutrals     [W/m^2] 
    # values are given at [r,z] - centers of cell faces that compose the divertor targets
    r_i = []  # r coordinate                    [m]
    z_i = []  # z coordinate                    [m]
    r_o = []  # r coordinate                    [m]
    z_o = []  # z coordinate                    [m]
    r1_i = [] # r beginning of the element      [m]
    z1_i = [] # z beginning of the element      [m]
    r2_i = [] # r end of the element            [m]
    z2_i = [] # z end of the element            [m]
    r1_o = [] # r beginning of the element      [m]
    z1_o = [] # z beginning of the element      [m]
    r2_o = [] # r end of the element            [m]
    z2_o = [] # z end of the element            [m]
    # values of x are given along the target, from PFR to SOL edge, 0 corresponds to strike point
    x_i = []  # x coordinate                    [m]
    x_o = []  # x coordinate                    [m]

    # Keep all the geometry reading just in case
    nr_nodes = len(profiles.grid_ggd[0].space[0].objects_per_dimension[0].object.array)
    nr_edges = len(profiles.grid_ggd[0].space[0].objects_per_dimension[1].object.array)
    nr_faces = len(profiles.grid_ggd[0].space[0].objects_per_dimension[2].object.array)

    # 0d
    pts = []
    for node_id in range(nr_nodes):
        pts.append(profiles.grid_ggd[0].space[0].objects_per_dimension[0].object[node_id].geometry)
    # 1d
    edges = []
    for edge_id in range(nr_edges):
        edges.append(profiles.grid_ggd[0].space[0].objects_per_dimension[1].object[edge_id].nodes)
    # 2d
    faces = []
    for face_id in range(nr_faces):
        faces.append(profiles.grid_ggd[0].space[0].objects_per_dimension[2].object[face_id].nodes)
    #3d
    volumes = []
    for face_id in range(nr_faces):
        volumes.append(profiles.grid_ggd[0].space[0].objects_per_dimension[2].object[face_id].geometry)

    # Find inner and outer target subsets
    inner_ind = Find_grid_subset(profiles.grid_ggd,'inner_target')
    outer_ind = Find_grid_subset(profiles.grid_ggd,'outer_target')
    sep_ind   = Find_grid_subset(profiles.grid_ggd,'Separatrix')
    if ( (inner_ind < 0) or (outer_ind < 0) or (sep_ind <0) ):
        logging.critical('Could not find inner, outer divertor or separatrix cannot procceed. inner_subset:%s/outer_subset:%s:separatrix_subset:%s', inner_ind,outer_ind,sep_ind)
        sys.exit()

    # Find hydrogenic and helium species in transport ids to account for the recombination loads
    # Impurities other than helium are ignored because thier density is always low
    H_isotope = Find_ion_specie(transport.model[0].ggd,1.0)
    He_isotope = Find_ion_specie(transport.model[0].ggd,2.0)

    #Find fuel neutrals
    Hn_isotope, Hn_count = Find_neut_specie(transport.model[0].ggd,1.0)

    # Check for the data avaiabbility in the ids
    nr_inner = len(profiles.grid_ggd[0].grid_subset[inner_ind].element.array)
    dummy = np.zeros(nr_inner, dtype=np.float64)
    # te
    try:
        te = profiles.ggd[0].electrons.temperature[inner_ind].values[0]
    except:
        logging.error('no data for the electron temperature found in edge_profiles ids, corresponding massive will be filled with zeros')
        te_avail = False
        te_i = dummy
    else:
        te_avail = True
    # ti
    try:
        ti = profiles.ggd[0].ion[0].temperature[inner_ind].values[0]
        ti = 1./ti
    except:
        logging.error('no data for the ion temperature found in edge_profiles ids, trying average ion temperature')
        try:
            ti = profiles.ggd[0].t_i_average[inner_ind].values[0]
        except:
            logging.error('no data for the ion temperature found in edge_profiles ids, corresponding massive will be filled with zeros')
            ti_avail = False
            ti_i = dummy
        else:
            ti_avail = True
            ti_avg = True
    else:
        ti_avail = True
        ti_avg = False
    # ne
    try:
        ne = profiles.ggd[0].electrons.density[inner_ind].values[0]
    except:
        logging.error('no data for the electron density found in edge_profiles ids, corresponding massive will be filled with zeros')
        ne_avail = False
        ne_i = dummy
    else:
        ne_avail = True
    # pwre
    try:
        pwre = transport.model[0].ggd[0].electrons.energy.flux[inner_ind].values[0]
    except:
        logging.error('no data for the electron heat flux found in edge_transport ids, corresponding massive will be filled with zeros')
        pwre_avail = False
        pwre_i = dummy
    else:
        pwre_avail = True
    # pwri
    try:
        pwri = transport.model[0].ggd[0].total_ion_energy.flux[inner_ind].values[0]
    except:
        logging.error('no data for the ion heat flux found in edge_transport ids, corresponding massive will be filled with zeros')
        pwri_avail = False
        pwri_i = dummy
    else:
        pwri_avail = True
    # ion recombination component of pwri
    try:
        tri = transport.model[0].ggd[0].ion[0].particles.flux[inner_ind].values[0]
    except:
        logging.error('no data for the ion particle flux found in edge_transport ids, the data for recombination heat loads to the target wont be added to the ion heat flux')
        tri_avail = False
    else:
        tri_avail = True
    # pwrn
    try:
        pwrn = transport.model[0].ggd[0].neutral[0].energy.flux[inner_ind].values[0]
        hlp = transport.model[0].ggd[0].neutral[0].energy.flux[inner_ind].values[0:nr_inner]
        if ( np.amax(hlp) <= 0. ):
            pwrn = transport.model[0].ggd[0].neutral[0].energy.flux[inner_ind].values[999999]
    except:
        logging.error('no data for the neutral heat flux found in edge_transport ids, trying crude estimate: Pneut = 1/2*k*n*T*u, where u=sqrt(8kT/pi/M)')
        try:
            pwrn = profiles.ggd[0].neutral[0].state[0].density[inner_ind].values[0]
            pwrn = profiles.ggd[0].neutral[0].state[0].temperature[inner_ind].values[0]
        except:
            logging.error('no data for the neutral heat flux found in edge_transport ids, corresponding massive will be filled with zeros')
            pwrn_avail = False
            pwrn_i = dummy
        else:
            pwrn_avail = True
            pwrn_calc = True
    else:
        pwrn_avail = True
        pwrn_calc = False
    if ( pwrn_avail == True ):
        if ( pwrn_calc == True ):
            nr_neut = len(profiles.ggd[0].neutral.array)
        else:
            nr_neut = len(transport.model[0].ggd[0].neutral.array)

    # Define x, r and z coordinates of the inner target data and extract corresponding data
    edge_index = profiles.grid_ggd[0].grid_subset[sep_ind].element[0].object[0].index
    sep_1 = pts[edges[edge_index-1][0]][0]
    sep_2 = pts[edges[edge_index-1][0]][1]
    dsp = 0.
    x_0 = 0.
    x_current = 0.
    for elem_id in range(nr_inner):
        edge_index = profiles.grid_ggd[0].grid_subset[inner_ind].element[elem_id].object[0].index
        node_1 = edges[edge_index-1][0]
        node_2 = edges[edge_index-1][1]
        r_current = 0.5 * (pts[node_1-1][0] + pts[node_2-1][0])
        z_current = 0.5 * (pts[node_1-1][1] + pts[node_2-1][1])
        r_i.append(r_current)
        z_i.append(z_current)
        r1_i.append(pts[node_1-1][0])
        r2_i.append(pts[node_2-1][0])
        z1_i.append(pts[node_1-1][1])
        z2_i.append(pts[node_2-1][1])
        x_1 = 0.5*np.sqrt((pts[node_2-1][0] - pts[node_1-1][0])**2. + (pts[node_2-1][1] - pts[node_1-1][1])**2.) 
        x_i.append(x_current)
        x_current = x_current + x_0 + x_1
        x_0 = x_1
        if ((sep_1 == pts[node_2-1][0]) and (sep_2 == pts[node_2-1][1])):
            dsp = x_current - x_0
        if ( te_avail == True ):
            te = profiles.ggd[0].electrons.temperature[inner_ind].values[elem_id]
            te_i.append(te)
        if ( ti_avail == True ):
            if ( ti_avg == True ):
                ti = profiles.ggd[0].t_i_average[inner_ind].values[elem_id]
            else:
                ti = profiles.ggd[0].ion[0].temperature[inner_ind].values[elem_id]
            ti_i.append(ti)
        if ( ne_avail == True ):
            ne = profiles.ggd[0].electrons.density[inner_ind].values[elem_id]
            ne_i.append(ne)
        if ( pwre_avail == True ):
            pwre = -transport.model[0].ggd[0].electrons.energy.flux[inner_ind].values[elem_id]
            pwre_i.append(pwre)
        if ( pwri_avail == True ):
            pwri = -transport.model[0].ggd[0].total_ion_energy.flux[inner_ind].values[elem_id]
            if ( tri_avail == True ):
                for H_isotope_ind in range(0,len(H_isotope)):
                    ion_ind = H_isotope[H_isotope_ind]
                    flxi = -transport.model[0].ggd[0].ion[ion_ind].particles.flux[inner_ind].values[elem_id]
                    pwri = pwri - transport.model[0].ggd[0].ion[ion_ind].particles.flux[inner_ind].values[elem_id]*H1_pot*eV2J
                for He_isotope_ind in range(0,len(He_isotope)):
                    ion_ind = He_isotope[He_isotope_ind]
                    if (transport.model[0].ggd[0].ion[ion_ind].z_ion == 1.0):
                        pwri = pwri - transport.model[0].ggd[0].ion[ion_ind].state[0].particles.flux[inner_ind].values[elem_id]*He1_pot*eV2J
                    elif (transport.model[0].ggd[0].ion[ion_ind].z_ion == 2.0): 
                        pwri = pwri - transport.model[0].ggd[0].ion[ion_ind].state[0].particles.flux[inner_ind].values[elem_id]*He2_pot*eV2J
                    else:
                        logging.warning("He ion with Z neither 1, nor 2 found.. skipping")
            pwri_i.append(pwri)
            flxi_i.append(flxi)
        if ( pwrn_avail == True ):
            pwrn = 0.
            flxn = 0.
            for neut_id in range(nr_neut):
                if ( pwrn_calc == True ):
                    n_neut = profiles.ggd[0].neutral[neut_id].state[0].density[inner_ind].values[elem_id]
                    t_neut = profiles.ggd[0].neutral[neut_id].state[0].temperature[inner_ind].values[elem_id]*eV2J
                    m_neut = profiles.ggd[0].neutral[neut_id].element[0].a*amu2kg
                    v_neut = np.sqrt(8.*t_neut/np.pi/m_neut)
                    pwrn = pwrn + 0.5*n_neut*t_neut*v_neut 
                    for p in range(0,np.size(Hn_isotope)):
                        if ( neut_id == Hn_isotope[p] ):
                            flxn = flxn + 0.25*n_neut*v_neut*Hn_count[p]
                else:
                    pwrn = pwrn - transport.model[0].ggd[0].neutral[neut_id].energy.flux[inner_ind].values[elem_id]
                    for p in (Hn_isotope):
                        if ( neut_id == p ):
                            flxn = flxn - transport.model[0].ggd[0].neutral[neut_id].state[0].particles.flux[inner_ind].values[elem_id]
            pwrn_i.append(pwrn)
            flxn_i.append(flxn)
    x_i = x_i - dsp

    # Repeat for the outer divertor
    # In current SOLPS version the some checks are unnecessary because nr_outer and nr_outer are always the same
    # things can change in wide_grids version comming 2023 though
    nr_outer = len(profiles.grid_ggd[0].grid_subset[outer_ind].element.array)
    dummy = np.zeros(nr_outer, dtype=np.float64)
    # te
    try:
        te = profiles.ggd[0].electrons.temperature[outer_ind].values[0]
    except:
        logging.error('no data for the electron temperature found in edge_profiles ids, corresponding massive will be filled with zeros')
        te_avail = False
        te_o = dummy
    else:
        te_avail = True
    # ti
    try:
        ti = profiles.ggd[0].ion[0].temperature[outer_ind].values[0]
    except:
        logging.error('no data for the ion temperature found in edge_profiles ids, trying average ion temperature')
        try:
            ti = profiles.ggd[0].t_i_average[outer_ind].values[0]
            ti = 1./ti
        except:
            logging.error('no data for the ion temperature found in edge_profiles ids, corresponding massive will be filled with zeros')
            ti_avail = False
            ti_o = dummy
        else:
            ti_avail = True
            ti_avg = True
    else:
        ti_avail = True
        ti_avg = False
    # ne
    try:
        ne = profiles.ggd[0].electrons.density[outer_ind].values[0]
    except:
        logging.error('no data for the electron density found in edge_profiles ids, corresponding massive will be filled with zeros')
        ne_avail = False
        ne_o = dummy
    else:
        ne_avail = True
    # pwre
    try:
        pwre = transport.model[0].ggd[0].electrons.energy.flux[outer_ind].values[0]
    except:
        logging.error('no data for the electron heat flux found in edge_transport ids, corresponding massive will be filled with zeros')
        pwre_avail = False
        pwre_o = dummy
    else:
        pwre_avail = True
    # pwri
    try:
        pwri = transport.model[0].ggd[0].total_ion_energy.flux[outer_ind].values[0]
    except:
        logging.error('no data for the ion heat flux found in edge_transport ids, corresponding massive will be filled with zeros')
        pwri_avail = False
        pwri_o = dummy
    else:
        pwri_avail = True
    # ion recombination component of pwri
    try:
        tri = transport.model[0].ggd[0].ion[0].particles.flux[outer_ind].values[0]
    except:
        logging.error('no data for the ion particle flux found in edge_transport ids, the data for recombination heat loads to the target wont be added to the ion heat flux')
        tri_avail = False
    else:
        tri_avail = True
    # pwrn
    try:
        pwrn = transport.model[0].ggd[0].neutral[0].energy.flux[outer_ind].values[0]
        hlp = transport.model[0].ggd[0].neutral[0].energy.flux[outer_ind].values[0:nr_inner]
        if ( np.amax(hlp) <= 0. ):
            pwrn = transport.model[0].ggd[0].neutral[0].energy.flux[outer_ind].values[999999]
    except:
        logging.error('no data for the neutral heat flux found in edge_transport ids, trying crude estimate: Pneut = 1/2*k*n*T*u, where u=sqrt(8kT/pi/M)')
        try:
            pwrn = profiles.ggd[0].neutral[0].state[0].density[outer_ind].values[0]
            pwrn = profiles.ggd[0].neutral[0].state[0].temperature[outer_ind].values[0]
        except:
            logging.error('no data for the neutral heat flux found in edge_transport ids, corresponding massive will be filled with zeros')
            pwrn_avail = False
            pwrn_i = dummy
        else:
            pwrn_avail = True
            pwrn_calc = True
    else:
        pwrn_avail = True
        pwrn_calc = False
    if ( pwrn_avail == True ):
        if ( pwrn_calc == True ):
            nr_neut = len(profiles.ggd[0].neutral.array)
        else:
            nr_neut = len(transport.model[0].ggd[0].neutral.array)

    # Define x, r and z coordinates of the outer target data and extract corresponding data
    nr_sep = len(profiles.grid_ggd[0].grid_subset[sep_ind].element.array)
    edge_index = profiles.grid_ggd[0].grid_subset[sep_ind].element[nr_sep-1].object[0].index
    sep_1 = pts[edges[edge_index-1][1]][0]
    sep_2 = pts[edges[edge_index-1][1]][1]
    dsp = 0.
    x_0 = 0.
    x_current = 0.
    for elem_id in range(nr_outer):
        edge_index = profiles.grid_ggd[0].grid_subset[outer_ind].element[elem_id].object[0].index
        node_1 = edges[edge_index-1][0]
        node_2 = edges[edge_index-1][1]
        r_current = 0.5 * (pts[node_1-1][0] + pts[node_2-1][0])
        z_current = 0.5 * (pts[node_1-1][1] + pts[node_2-1][1])
        r_o.append(r_current)
        z_o.append(z_current)
        r1_o.append(pts[node_1-1][0])
        r2_o.append(pts[node_2-1][0])
        z1_o.append(pts[node_1-1][1])
        z2_o.append(pts[node_2-1][1])
        x_1 = 0.5*np.sqrt((pts[node_2-1][0] - pts[node_1-1][0])**2. + (pts[node_2-1][1] - pts[node_1-1][1])**2.) 
        x_o.append(x_current)
        x_current = x_current + x_0 + x_1
        x_0 = x_1
        if ((sep_1 == pts[node_2-1][0]) and (sep_2 == pts[node_2-1][1])):
            dsp = x_current - x_0
        if ( te_avail == True ):
            te = profiles.ggd[0].electrons.temperature[outer_ind].values[elem_id]
            te_o.append(te)
        if ( ti_avail == True ):
            if ( ti_avg == True ):
                ti = profiles.ggd[0].t_i_average[outer_ind].values[elem_id]
            else:
                ti = profiles.ggd[0].ion[0].temperature[outer_ind].values[elem_id]
            ti_o.append(ti)
        if ( ne_avail == True ):
            ne = profiles.ggd[0].electrons.density[outer_ind].values[elem_id]
            ne_o.append(ne)
        if ( pwre_avail == True ):
            pwre = transport.model[0].ggd[0].electrons.energy.flux[outer_ind].values[elem_id]
            pwre_o.append(pwre)
        if ( pwri_avail == True ):
            pwri = transport.model[0].ggd[0].total_ion_energy.flux[outer_ind].values[elem_id]
            if ( tri_avail == True ):
                for H_isotope_ind in range(0,len(H_isotope)):
                    ion_ind = H_isotope[H_isotope_ind]
                    flxi = transport.model[0].ggd[0].ion[ion_ind].particles.flux[outer_ind].values[elem_id] 
                    pwri = pwri + transport.model[0].ggd[0].ion[ion_ind].particles.flux[outer_ind].values[elem_id]*H1_pot*eV2J
                for He_isotope_ind in range(0,len(He_isotope)):
                    ion_ind = He_isotope[He_isotope_ind]
                    if (transport.model[0].ggd[0].ion[ion_ind].z_ion == 1.0):
                        pwri = pwri + transport.model[0].ggd[0].ion[ion_ind].state[0].particles.flux[outer_ind].values[elem_id]*He1_pot*eV2J
                    elif (transport.model[0].ggd[0].ion[ion_ind].z_ion == 2.0): 
                        pwri = pwri + transport.model[0].ggd[0].ion[ion_ind].state[0].particles.flux[outer_ind].values[elem_id]*He2_pot*eV2J
                    else:
                        logging.warning("He ion with Z neither 1, nor 2 found.. skipping")
            pwri_o.append(pwri)
            flxi_o.append(flxi)
        if ( pwrn_avail == True ):
            pwrn = 0.
            flxn = 0.
            for neut_id in range(nr_neut):
                if ( pwrn_calc == True ):
                    n_neut = profiles.ggd[0].neutral[neut_id].state[0].density[outer_ind].values[elem_id]
                    t_neut = profiles.ggd[0].neutral[neut_id].state[0].temperature[outer_ind].values[elem_id]*eV2J
                    m_neut = profiles.ggd[0].neutral[neut_id].element[0].a*amu2kg
                    v_neut = np.sqrt(8.*t_neut/np.pi/m_neut)
                    pwrn = pwrn + 0.5*n_neut*t_neut*v_neut 
                    for p in range(0,np.size(Hn_isotope)):
                        if ( neut_id == Hn_isotope[p] ):
                            flxn = flxn + 0.25*n_neut*v_neut*Hn_count[p]
                else:
                    pwrn = pwrn + transport.model[0].ggd[0].neutral[neut_id].energy.flux[outer_ind].values[elem_id]
                    for p in (Hn_isotope):
                        if ( neut_id == p ):
                            flxn = flxn + transport.model[0].ggd[0].neutral[neut_id].state[0].particles.flux[outer_ind].values[elem_id]
            pwrn_o.append(pwrn)
            flxn_o.append(flxn)
    x_o = x_o - dsp

    inner_coords = np.array([[r_i[i], z_i[i]] for i in range(len(r_i))])
    outer_coords = np.array([[r_o[i], z_o[i]] for i in range(len(r_o))])

###########
#    # Sample output for the demonstration purpose, to be removed by user
#    print('##########################################################')
#    print('Shot : run : i_time', shot,run,i_time) 
#    print('##########################################################')
#    print('=================== Inner target =========================') 
#    for i in range(nr_inner):
#        print('Segment : [r, z]    || ', i+1,inner_coords[i])
#        print('  te : ti : ne      || ', te_i[i], ti_i[i], ne_i[i])
#        print(' pwre : pwri : pwrn || ', pwre_i[i], pwri_i[i], pwrn_i[i])
#        print('  flxi : flxn       || ', flxi_i[i], flxn_i[i])
#        print('------------------------------------------------------')
#    print('=================== Outer target =========================') 
#    for i in range(nr_outer):
#        print('Segment : [r, z]    || ', i+1,outer_coords[i])
#        print('  te : ti : ne      || ', te_o[i], ti_o[i], ne_o[i])
#        print(' pwre : pwri : pwrn || ', pwre_o[i], pwri_o[i], pwrn_o[i])
#        print('  flxi : flxn       || ', flxi_o[i], flxn_o[i])
#        print('------------------------------------------------------')
#############

    # Writting output to files
    subfolder_path = os.path.dirname(__file__)
    names = [subfolder_path+'/inner_target',subfolder_path+'/outer_target']
    files = []
    for i in range(0,np.size(names)):
        ffile = '{0}{1}{2}{3}{4}{5}'.format(names[i],'.shot',str(shot),'.run',str(run),'.dat')
        files.append(ffile)
    for f in range(0,np.size(files)):

        ffile = files[f]

        with open(ffile,'w') as ff:

            header = ' # r1,r2 - radial coordinates of the segment    [m]        \n' + \
                     ' # z1,z2 - vertical coordinates of the segemnt  [m]        \n' + \
                     ' # rc,zc - coordinates of the segment center    [m]        \n' + \
                     ' # ne    - electron density                     [m^-3]     \n' + \
                     ' # Te    - electron temperature                 [eV]       \n' + \
                     ' # Ti    - ion temperature                      [eV]       \n' + \
                     ' # flxi  - ion flux (only fuel ions)            [m^-2*s^-1]\n' + \
                     ' # flxn  - neutral flux (only fuel atoms)       [m^-2*s^-1]\n' + \
                     ' # pwre  - electron power flux                  [W/m^2]    \n' + \
                     ' # pwri  - ion power flux (including recomb.)   [W/m^2]    \n' + \
                     ' # pwrn  - neutral power flux                   [W/m^2]    \n' 
            ff.write(header)
            
            str_len = 14
            ttls = ['r1','z1','r2','z2','rc','zc','ne','Te','Ti','flxi','flxn','pwre','pwri','pwrn']
            
            prin = ' #'
            for p in range(0,np.size(ttls)):
                ttl_len = len(ttls[p])
                step1 = ''
                step2 = ''
                if ( ttl_len > str_len ):
                    logging.warning('title length is greater than limit and will be truncated, title:limit:%s:%s',ttls[p],str_len)
                    ttl=ttls[p][0:str_len]
                else:
                    step1 = int((str_len - ttl_len)/2.)
                    step2 = str_len - step1 - ttl_len
                    ttl = ttls[p]
                prin = prin + ' '*step1 + ttl + ' '*step2
            prin = prin + '\n'
            ff.write(prin)

            if ( f == 0 ):
                data = (r1_i,z1_i,r2_i,z2_i,r_i,z_i,ne_i,te_i,ti_i,flxi_i,flxn_i,pwre_i,pwri_i,pwrn_i)
            elif ( f == 1 ):
                data = (r1_o,z1_o,r2_o,z2_o,r_o,z_o,ne_o,te_o,ti_o,flxi_o,flxn_o,pwre_o,pwri_o,pwrn_o)
            for l in range(0,np.size(data[0])):
                prin = '  '
                for i in range(0,np.size(ttls)):
                    prin = '{0}{1}'.format(prin,' % 7.6E' % data[i][l])
                prin = prin + '\n'
                ff.write(prin)

    return {'inner_target_coords':inner_coords,'inner_target_te:':te_i,'inner_target_ti':ti_i, \
            'inner_target_ne':ne_i,'inner_target_pwre':pwre_i,'inner_target_pwri':pwri_i, \
            'inner_target_pwrn':pwrn_i,'outer_target_coords':outer_coords,'outer_target_te:':te_o, \
            'outer_target_ti':ti_o,'outer_target_ne':ne_o,'outer_target_pwre':pwre_o, \
            'outer_target_pwri':pwri_o,'outer_target_pwrn':pwrn_o }

# Main program
def divertor_target_loads(username,device,shot_list,run,code_origin):

    for shot in shot_list:

        logging.info("Reading shot = %s, run = %s from database = %s of user = %s "%(shot,run,device,username))
        xinput = imas.DBEntry(imas.imasdef.MDSPLUS_BACKEND,device,shot,run,username)
        xinput.open()

        time_array = xinput.partial_get(ids_name='edge_profiles',data_path='time')
        N_times = np.size(time_array)
        for i_time in range(0, N_times):

            time_now = time_array[i_time]
            logging.info('Time  = ' + str(time_now) + ' s ')

            slice_info = { 'shot' : shot, 'run' : run, 'i_time' : i_time }

            xedge_profiles = xinput.get_slice('edge_profiles',time_now,2)
            xedge_transport = xinput.get_slice('edge_transport',time_now,2)

            if ( code_origin == 'SOLPS' ):
                trgloadsdata = SOLPS_target_loads_read(xedge_profiles, xedge_transport,  slice_info)

################# OLD CLUSTER IMPLEMENTATION (PROBABLY OLD IMAS STANDARD #####################################
#
#        x = imas.ids(shot, run)
#        x.open_env(username, device, "3")
#        x.edge_profiles.get()
#        x.edge_transport.get()
#
#        # Time loop: Go over time slices in the IDS
#        N_times = len(x.edge_profiles.time)
#        logging.info( "Number of time slices = " + str(N_times))
#
#        for i_time in range(0, N_times):
#
#            time_now = x.edge_profiles.time[i_time]
#            logging.info('Time  = ' + str(time_now) + ' s ')
#
#            slice_info = { 'shot' : shot, 'run' : run, 'i_time' : i_time }
#
#            if ( code_origin == 'SOLPS' ):
#                trgloadsdata = SOLPS_target_loads_read(x.edge_profiles, x.edge_transport,  slice_info)
#
##############################################################################################################

if __name__ == "__main__":

    # Global input parameters
    username     = "public"
    device       = "iter"
#    shot_list    = [122481,122258]
    shot_list    = [122258]
    run          = 1
    code_origin  = 'SOLPS'          # Code from which the radiation IDS was computed
#    code_origin  = 'SOLEDGE3X'          # SOLEDGE3X requires further work

    divertor_target_loads(username,device,shot_list,run,code_origin)
