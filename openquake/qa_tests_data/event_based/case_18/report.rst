Event-Based Hazard QA Test, Case 18
===================================

gem-tstation:/home/michele/ssd/calc_19689.hdf5 updated Wed May 25 08:34:31 2016

num_sites = 1, sitecol = 739 B

Parameters
----------
============================ ===================
calculation_mode             'event_based'      
number_of_logic_tree_samples 3                  
maximum_distance             {'default': 200.0} 
investigation_time           1.0                
ses_per_logic_tree_path      350                
truncation_level             0.0                
rupture_mesh_spacing         1.0                
complex_fault_mesh_spacing   1.0                
width_of_mfd_bin             0.001              
area_source_discretization   10.0               
random_seed                  1064               
master_seed                  0                  
oqlite_version               '0.13.0-git1cc9966'
============================ ===================

Input files
-----------
======================= ============================================================
Name                    File                                                        
======================= ============================================================
gsim_logic_tree         `three_gsim_logic_tree.xml <three_gsim_logic_tree.xml>`_    
job_ini                 `job.ini <job.ini>`_                                        
source                  `source_model.xml <source_model.xml>`_                      
source_model_logic_tree `source_model_logic_tree.xml <source_model_logic_tree.xml>`_
======================= ============================================================

Composite source model
----------------------
========= ====== ====================================== =============== ================
smlt_path weight source_model_file                      gsim_logic_tree num_realizations
========= ====== ====================================== =============== ================
b1        0.333  `source_model.xml <source_model.xml>`_ simple(3)       3/3             
========= ====== ====================================== =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== ====================================== ========= ========== ==========
trt_id gsims                                  distances siteparams ruptparams
====== ====================================== ========= ========== ==========
0      AkkarBommer2010() CauzziFaccioli2008() rhypo rjb vs30       rake mag  
====== ====================================== ========= ========== ==========

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=2, rlzs=3)
  0,AkkarBommer2010(): ['<0,b1,AB,w=0.333333333333>', '<1,b1,AB,w=0.333333333333>']
  0,CauzziFaccioli2008(): ['<2,b1,CF,w=0.333333333333>']>

Number of ruptures per tectonic region type
-------------------------------------------
================ ====== ==================== =========== ============ ======
source_model     trt_id trt                  num_sources eff_ruptures weight
================ ====== ==================== =========== ============ ======
source_model.xml 0      Active Shallow Crust 1           6            75    
================ ====== ==================== =========== ============ ======

Informational data
------------------
======== ==============
hostname 'gem-tstation'
======== ==============

Specific information for event based
------------------------------------
======================== =====
Total number of ruptures 6    
Total number of events   6    
Rupture multiplicity     1.000
======================== =====

Slowest sources
---------------
============ ========= ============ ====== ========= =========== ========== =========
trt_model_id source_id source_class weight split_num filter_time split_time calc_time
============ ========= ============ ====== ========= =========== ========== =========
0            1         PointSource  75     1         0.005       2.217E-05  2.864    
============ ========= ============ ====== ========= =========== ========== =========

Computation times by source typology
------------------------------------
============ =========== ========== ========= ======
source_class filter_time split_time calc_time counts
============ =========== ========== ========= ======
PointSource  0.005       2.217E-05  2.864     1     
============ =========== ========== ========= ======

Information about the tasks
---------------------------
================================= ========= ========= ========= ========= =========
measurement                       mean      stddev    min       max       num_tasks
compute_ruptures.time_sec         2.864     NaN       2.864     2.864     1        
compute_ruptures.memory_mb        -0.515625 NaN       -0.515625 -0.515625 1        
compute_gmfs_and_curves.time_sec  0.001     3.245E-04 9.589E-04 0.002     6        
compute_gmfs_and_curves.memory_mb 0.0       0.0       0.0       0.0       6        
================================= ========= ========= ========= ========= =========

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
total compute_ruptures         2.864     0.0       1     
reading composite source model 0.011     0.0       1     
store source_info              0.011     0.0       1     
total compute_gmfs_and_curves  0.008     0.0       6     
saving ruptures                0.008     0.0       1     
managing sources               0.008     0.0       1     
filtering sources              0.005     0.0       1     
saving gmfs                    0.004     0.0       6     
make contexts                  0.003     0.0       6     
compute poes                   0.003     0.0       6     
aggregate curves               0.002     0.0       1     
filtering ruptures             0.001     0.0       6     
reading site collection        3.815E-05 0.0       1     
splitting sources              2.217E-05 0.0       1     
============================== ========= ========= ======