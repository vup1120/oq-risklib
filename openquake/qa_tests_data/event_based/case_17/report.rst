Event Based Hazard QA Test, Case 17
===================================

gem-tstation:/home/michele/ssd/calc_1018.hdf5 updated Thu Apr 28 15:42:40 2016

num_sites = 1, sitecol = 739 B

Parameters
----------
============================ ===================
calculation_mode             'event_based'      
number_of_logic_tree_samples 5                  
maximum_distance             {'default': 200.0} 
investigation_time           1.0                
ses_per_logic_tree_path      3                  
truncation_level             2.0                
rupture_mesh_spacing         1.0                
complex_fault_mesh_spacing   1.0                
width_of_mfd_bin             1.0                
area_source_discretization   10.0               
random_seed                  106                
master_seed                  0                  
oqlite_version               '0.13.0-git93d6f64'
============================ ===================

Input files
-----------
======================= ============================================================
Name                    File                                                        
======================= ============================================================
gsim_logic_tree         `gsim_logic_tree.xml <gsim_logic_tree.xml>`_                
job_ini                 `job.ini <job.ini>`_                                        
source                  `source_model_1.xml <source_model_1.xml>`_                  
source                  `source_model_2.xml <source_model_2.xml>`_                  
source_model_logic_tree `source_model_logic_tree.xml <source_model_logic_tree.xml>`_
======================= ============================================================

Composite source model
----------------------
========= ====== ========================================== =============== ================
smlt_path weight source_model_file                          gsim_logic_tree num_realizations
========= ====== ========================================== =============== ================
b1        0.200  `source_model_1.xml <source_model_1.xml>`_ trivial(0)      1/1             
b2        0.200  `source_model_2.xml <source_model_2.xml>`_ trivial(1)      4/4             
========= ====== ========================================== =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== ============== ========= ========== ==========
trt_id gsims          distances siteparams ruptparams
====== ============== ========= ========== ==========
1      SadighEtAl1997 rrup      vs30       rake mag  
====== ============== ========= ========== ==========

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=1, rlzs=5)
  1,SadighEtAl1997: ['<1,b2,b1,w=0.2>', '<2,b2,b1,w=0.2>', '<3,b2,b1,w=0.2>', '<4,b2,b1,w=0.2>']>

Number of ruptures per tectonic region type
-------------------------------------------
================== ====== ==================== =========== ============ ======
source_model       trt_id trt                  num_sources eff_ruptures weight
================== ====== ==================== =========== ============ ======
source_model_2.xml 1      Active Shallow Crust 1           3            0.175 
================== ====== ==================== =========== ============ ======

Informational data
------------------
======== ==============
hostname 'gem-tstation'
======== ==============

Specific information for event based
------------------------------------
======================== =====
Total number of ruptures 3    
Total number of events   8    
Rupture multiplicity     2.667
======================== =====

Slowest sources
---------------
============ ========= ============ ====== ========= =========== ========== =========
trt_model_id source_id source_class weight split_num filter_time split_time calc_time
============ ========= ============ ====== ========= =========== ========== =========
0            1         PointSource  0.975  1         1.631E-04   0.0        0.028    
1            2         PointSource  0.175  1         1.190E-04   0.0        0.006    
============ ========= ============ ====== ========= =========== ========== =========

Information about the tasks
---------------------------
================================= ===== ===== ===== ======
measurement                       min   max   mean  stddev
compute_ruptures.time_sec         0.006 0.028 0.017 0.016 
compute_ruptures.memory_mb        0.0   0.0   0.0   0.0   
compute_gmfs_and_curves.time_sec  0.004 0.010 0.007 0.003 
compute_gmfs_and_curves.memory_mb 0.0   0.0   0.0   0.0   
================================= ===== ===== ===== ======

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
total compute_ruptures         0.034     0.0       2     
store source_info              0.032     0.0       1     
total compute_gmfs_and_curves  0.021     0.0       3     
managing sources               0.019     0.0       1     
reading composite source model 0.010     0.0       1     
aggregating hcurves            0.010     0.0       12    
bulding hazard curves          0.009     0.0       3     
saving gmfs                    0.006     0.0       12    
make contexts                  0.006     0.0       3     
compute poes                   0.004     0.0       3     
saving ruptures                0.004     0.0       1     
aggregate curves               0.002     0.0       14    
filtering ruptures             0.001     0.0       3     
filtering sources              2.820E-04 0.0       2     
reading site collection        4.697E-05 0.0       1     
============================== ========= ========= ======