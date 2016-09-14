Scenario QA Test for occupants
==============================

gem-tstation:/home/michele/ssd/calc_19697.hdf5 updated Wed May 25 08:35:01 2016

num_sites = 3, sitecol = 831 B

Parameters
----------
============================ ===================
calculation_mode             'scenario'         
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 300}   
investigation_time           None               
ses_per_logic_tree_path      1                  
truncation_level             3.0                
rupture_mesh_spacing         10.0               
complex_fault_mesh_spacing   10.0               
width_of_mfd_bin             None               
area_source_discretization   None               
random_seed                  3                  
master_seed                  0                  
oqlite_version               '0.13.0-git1cc9966'
============================ ===================

Input files
-----------
======================= ========================================================================
Name                    File                                                                    
======================= ========================================================================
exposure                `exposure_model.xml <exposure_model.xml>`_                              
job_ini                 `job_haz.ini <job_haz.ini>`_                                            
occupants_vulnerability `vulnerability_model_occupants.xml <vulnerability_model_occupants.xml>`_
rupture_model           `fault_rupture.xml <fault_rupture.xml>`_                                
======================= ========================================================================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=1, rlzs=1)
  0,ChiouYoungs2008(): ['<0,b_1,b1,w=1.0>']>

Exposure model
--------------
=========== =
#assets     3
#taxonomies 3
=========== =

======== ===== ====== === === ========= ==========
taxonomy mean  stddev min max num_sites num_assets
RC       1.000 NaN    1   1   1         1         
RM       1.000 NaN    1   1   1         1         
W        1.000 NaN    1   1   1         1         
*ALL*    1.000 0.0    1   1   3         3         
======== ===== ====== === === ========= ==========

Information about the tasks
---------------------------
Not available

Slowest operations
------------------
======================= ========= ========= ======
operation               time_sec  memory_mb counts
======================= ========= ========= ======
filtering sites         0.006     0.0       1     
reading exposure        0.004     0.0       1     
computing gmfs          0.002     0.0       1     
reading site collection 7.868E-06 0.0       1     
======================= ========= ========= ======