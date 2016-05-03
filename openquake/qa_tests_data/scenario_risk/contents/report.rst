QA Scenario Risk for contents
=============================

gem-tstation:/home/michele/ssd/calc_1032.hdf5 updated Thu Apr 28 15:44:06 2016

num_sites = 3, sitecol = 831 B

Parameters
----------
============================ ===================
calculation_mode             'scenario_risk'    
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
avg_losses                   False              
oqlite_version               '0.13.0-git93d6f64'
============================ ===================

Input files
-----------
======================== ========================================================================
Name                     File                                                                    
======================== ========================================================================
contents_vulnerability   `vulnerability_model_contents.xml <vulnerability_model_contents.xml>`_  
exposure                 `exposure_model.xml <exposure_model.xml>`_                              
job_ini                  `job.ini <job.ini>`_                                                    
rupture_model            `fault_rupture.xml <fault_rupture.xml>`_                                
structural_vulnerability `vulnerability_model_structure.xml <vulnerability_model_structure.xml>`_
======================== ========================================================================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(1)
  0,ChiouYoungs2008: ['ChiouYoungs2008']>

Exposure model
--------------
=========== =
#assets     3
#taxonomies 3
=========== =

======== =======
Taxonomy #Assets
======== =======
RC       1      
RM       1      
W        1      
======== =======

Information about the tasks
---------------------------
======================= ===== ===== ===== =========
measurement             min   max   mean  stddev   
scenario_risk.time_sec  0.002 0.002 0.002 6.204E-05
scenario_risk.memory_mb 0.004 0.004 0.004 0.0      
======================= ===== ===== ===== =========

Slowest operations
------------------
======================= ========= ========= ======
operation               time_sec  memory_mb counts
======================= ========= ========= ======
filtering sites         0.011     0.0       1     
reading exposure        0.008     0.0       1     
total scenario_risk     0.007     0.004     3     
computing risk          0.005     0.0       3     
computing gmfs          0.002     0.0       1     
saving gmfs             0.002     0.0       1     
building riskinputs     5.109E-04 0.0       1     
building epsilons       1.659E-04 0.0       1     
building hazard         7.796E-05 0.0       3     
reading site collection 1.001E-05 0.0       1     
======================= ========= ========= ======