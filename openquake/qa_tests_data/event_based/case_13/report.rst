Event Based QA Test, Case 13
============================

gem-tstation:/home/michele/ssd/calc_105.hdf5 updated Wed Apr 27 10:56:36 2016

num_sites = 1, sitecol = 739 B

Parameters
----------
============================ ===================
calculation_mode             'event_based'      
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 200.0} 
investigation_time           1.0                
ses_per_logic_tree_path      5000               
truncation_level             2.0                
rupture_mesh_spacing         1.0                
complex_fault_mesh_spacing   1.0                
width_of_mfd_bin             1.0                
area_source_discretization   10.0               
random_seed                  1066               
master_seed                  0                  
oqlite_version               '0.13.0-gitcbbc4a8'
============================ ===================

Input files
-----------
======================= ============================================================
Name                    File                                                        
======================= ============================================================
gsim_logic_tree         `gsim_logic_tree.xml <gsim_logic_tree.xml>`_                
job_ini                 `job.ini <job.ini>`_                                        
source                  `source_model.xml <source_model.xml>`_                      
source_model_logic_tree `source_model_logic_tree.xml <source_model_logic_tree.xml>`_
======================= ============================================================

Composite source model
----------------------
========= ====== ====================================== =============== ================
smlt_path weight source_model_file                      gsim_logic_tree num_realizations
========= ====== ====================================== =============== ================
b1        1.000  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
========= ====== ====================================== =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== ================= ========= ========== ==========
trt_id gsims             distances siteparams ruptparams
====== ================= ========= ========== ==========
0      BooreAtkinson2008 rjb       vs30       rake mag  
====== ================= ========= ========== ==========

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=1, rlzs=1)
  0,BooreAtkinson2008: ['<0,b1,b1,w=1.0>']>

Number of ruptures per tectonic region type
-------------------------------------------
================ ====== ==================== =========== ============ ======
source_model     trt_id trt                  num_sources eff_ruptures weight
================ ====== ==================== =========== ============ ======
source_model.xml 0      Active Shallow Crust 1           1            0.025 
================ ====== ==================== =========== ============ ======

Informational data
------------------
======== ==============
hostname 'gem-tstation'
======== ==============

Specific information for event based
------------------------------------
Total number of ruptures: 1
Total number of events: 5031

Slowest sources
---------------
============ ========= ============ ====== ========= =========== ========== =========
trt_model_id source_id source_class weight split_num filter_time split_time calc_time
============ ========= ============ ====== ========= =========== ========== =========
0            1         PointSource  0.025  1         1.900E-04   0.0        0.071    
============ ========= ============ ====== ========= =========== ========== =========

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
total compute_ruptures         0.071     0.211     1     
saving ruptures                0.048     0.0       1     
store source_info              0.010     0.0       1     
reading composite source model 0.008     0.0       1     
managing sources               0.003     0.0       1     
aggregate curves               0.001     0.0       2     
aggregating hcurves            7.610E-04 0.0       1     
saving gmfs                    6.101E-04 0.0       1     
filtering ruptures             5.372E-04 0.0       1     
filtering sources              1.900E-04 0.0       1     
reading site collection        6.580E-05 0.0       1     
============================== ========= ========= ======