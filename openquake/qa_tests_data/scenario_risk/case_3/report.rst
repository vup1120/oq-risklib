Scenario QA Test 3
==================

gem-tstation:/home/michele/ssd/calc_19699.hdf5 updated Wed May 25 08:35:05 2016

num_sites = 4, sitecol = 877 B

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
oqlite_version               '0.13.0-git1cc9966'
============================ ===================

Input files
-----------
======================== ====================================================
Name                     File                                                
======================== ====================================================
exposure                 `exposure_model.xml <exposure_model.xml>`_          
job_ini                  `job.ini <job.ini>`_                                
rupture_model            `fault_rupture.xml <fault_rupture.xml>`_            
structural_vulnerability `vulnerability_model.xml <vulnerability_model.xml>`_
======================== ====================================================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=1, rlzs=1)
  0,ChiouYoungs2008(): ['<0,b_1,b1,w=1.0>']>

Exposure model
--------------
=========== =
#assets     4
#taxonomies 3
=========== =

======== ===== ====== === === ========= ==========
taxonomy mean  stddev min max num_sites num_assets
RC       1.000 NaN    1   1   1         1         
RM       1.000 NaN    1   1   1         1         
W        1.000 0.0    1   1   2         2         
*ALL*    1.000 0.0    1   1   4         4         
======== ===== ====== === === ========= ==========

Information about the tasks
---------------------------
======================= ===== ========= ========= ===== =========
measurement             mean  stddev    min       max   num_tasks
scenario_risk.time_sec  0.001 3.676E-04 7.341E-04 0.002 4        
scenario_risk.memory_mb 0.0   0.0       0.0       0.0   4        
======================= ===== ========= ========= ===== =========

Slowest operations
------------------
======================= ========= ========= ======
operation               time_sec  memory_mb counts
======================= ========= ========= ======
computing gmfs          0.031     0.0       1     
filtering sites         0.006     0.0       1     
total scenario_risk     0.005     0.0       4     
reading exposure        0.004     0.0       1     
computing riskmodel     0.002     0.0       4     
saving gmfs             0.002     0.0       1     
building epsilons       6.380E-04 0.0       1     
building hazard         4.623E-04 0.0       4     
building riskinputs     4.621E-04 0.0       1     
reading site collection 8.821E-06 0.0       1     
======================= ========= ========= ======