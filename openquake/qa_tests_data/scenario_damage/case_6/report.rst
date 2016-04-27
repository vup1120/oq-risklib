oq-test03, depth=15km
=====================

gem-tstation:/home/michele/ssd/calc_43.hdf5 updated Wed Apr 27 10:54:21 2016

num_sites = 1, sitecol = 739 B

Parameters
----------
============================ ===================
calculation_mode             'scenario_damage'  
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 300}   
investigation_time           None               
ses_per_logic_tree_path      1                  
truncation_level             3.0                
rupture_mesh_spacing         0.1                
complex_fault_mesh_spacing   0.1                
width_of_mfd_bin             None               
area_source_discretization   None               
random_seed                  3                  
master_seed                  0                  
oqlite_version               '0.13.0-gitcbbc4a8'
============================ ===================

Input files
-----------
==================== ============================================================================
Name                 File                                                                        
==================== ============================================================================
exposure             `exposure_model_Antioquia_test03.xml <exposure_model_Antioquia_test03.xml>`_
job_ini              `job_h.ini <job_h.ini>`_                                                    
rupture_model        `rupture_Romeral_15km.xml <rupture_Romeral_15km.xml>`_                      
structural_fragility `fragility_model_test03.xml <fragility_model_test03.xml>`_                  
==================== ============================================================================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(1)
  0,SadighEtAl1997: ['SadighEtAl1997']>

Exposure model
--------------
=========== =
#assets     5
#taxonomies 5
=========== =

============== =======
Taxonomy       #Assets
============== =======
MUR/LWAL/HEX:1 1      
MUR/LWAL/HEX:2 1      
MUR/LWAL/HEX:3 1      
MUR/LWAL/HEX:4 1      
MUR/LWAL/HEX:5 1      
============== =======

Slowest operations
------------------
======================= ========= ========= ======
operation               time_sec  memory_mb counts
======================= ========= ========= ======
reading exposure        0.003     0.0       1     
filtering sites         9.000E-04 0.0       1     
computing gmfs          4.070E-04 0.0       1     
reading site collection 5.007E-06 0.0       1     
======================= ========= ========= ======