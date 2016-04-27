Scenario QA Test, Case 9, Multiple GSIMs
========================================

gem-tstation:/home/michele/ssd/calc_51.hdf5 updated Wed Apr 27 10:54:22 2016

num_sites = 3, sitecol = 831 B

Parameters
----------
============================ ===================
calculation_mode             'scenario'         
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 200}   
investigation_time           None               
ses_per_logic_tree_path      1                  
truncation_level             1.0                
rupture_mesh_spacing         1.0                
complex_fault_mesh_spacing   1.0                
width_of_mfd_bin             None               
area_source_discretization   None               
random_seed                  3                  
master_seed                  0                  
oqlite_version               '0.13.0-gitcbbc4a8'
============================ ===================

Input files
-----------
=============== ============================================
Name            File                                        
=============== ============================================
gsim_logic_tree `gsim_logic_tree.xml <gsim_logic_tree.xml>`_
job_ini         `job.ini <job.ini>`_                        
rupture_model   `rupture_model.xml <rupture_model.xml>`_    
=============== ============================================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(2)
  0,LinLee2008SSlab: ['LinLee2008SSlab']
  0,YoungsEtAl1997SSlab: ['YoungsEtAl1997SSlab']>

Slowest operations
------------------
======================= ========= ========= ======
operation               time_sec  memory_mb counts
======================= ========= ========= ======
filtering sites         0.037     0.0       1     
computing gmfs          5.760E-04 0.0       1     
reading site collection 2.789E-05 0.0       1     
======================= ========= ========= ======