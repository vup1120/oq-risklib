Event Based QA Test, Case 12
============================

gem-tstation:/home/michele/ssd/calc_1029.hdf5 updated Thu Apr 28 15:44:05 2016

num_sites = 1, sitecol = 739 B

Parameters
----------
============================ ===================
calculation_mode             'event_based'      
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 200.0} 
investigation_time           1.0                
ses_per_logic_tree_path      3500               
truncation_level             2.0                
rupture_mesh_spacing         1.0                
complex_fault_mesh_spacing   1.0                
width_of_mfd_bin             1.0                
area_source_discretization   10.0               
random_seed                  1066               
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
source                  `source_model.xml <source_model.xml>`_                      
source_model_logic_tree `source_model_logic_tree.xml <source_model_logic_tree.xml>`_
======================= ============================================================

Composite source model
----------------------
========= ====== ====================================== =============== ================
smlt_path weight source_model_file                      gsim_logic_tree num_realizations
========= ====== ====================================== =============== ================
b1        1.000  `source_model.xml <source_model.xml>`_ trivial(1,1)    1/1             
========= ====== ====================================== =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== ================= ========= ========== ==========
trt_id gsims             distances siteparams ruptparams
====== ================= ========= ========== ==========
0      SadighEtAl1997    rrup      vs30       rake mag  
1      BooreAtkinson2008 rjb       vs30       rake mag  
====== ================= ========= ========== ==========

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=2, rlzs=1)
  0,SadighEtAl1997: ['<0,b1,b1_b2,w=1.0>']
  1,BooreAtkinson2008: ['<0,b1,b1_b2,w=1.0>']>

Number of ruptures per tectonic region type
-------------------------------------------
================ ====== ==================== =========== ============ ======
source_model     trt_id trt                  num_sources eff_ruptures weight
================ ====== ==================== =========== ============ ======
source_model.xml 0      Active Shallow Crust 1           1            0.025 
source_model.xml 1      Stable Continental   1           1            0.025 
================ ====== ==================== =========== ============ ======

=============== =====
#TRT models     2    
#sources        2    
#eff_ruptures   2    
filtered_weight 0.050
=============== =====

Informational data
------------------
======== ==============
hostname 'gem-tstation'
======== ==============

Specific information for event based
------------------------------------
======================== =====
Total number of ruptures 2    
Total number of events   6,906
Rupture multiplicity     3,453
======================== =====

Slowest sources
---------------
============ ========= ============ ====== ========= =========== ========== =========
trt_model_id source_id source_class weight split_num filter_time split_time calc_time
============ ========= ============ ====== ========= =========== ========== =========
0            1         PointSource  0.025  1         1.471E-04   0.0        0.131    
1            2         PointSource  0.025  1         1.721E-04   0.0        0.109    
============ ========= ============ ====== ========= =========== ========== =========

Information about the tasks
---------------------------
================================= ===== ===== ===== ======
measurement                       min   max   mean  stddev
compute_ruptures.time_sec         0.109 0.131 0.120 0.015 
compute_ruptures.memory_mb        0.0   0.113 0.057 0.080 
compute_gmfs_and_curves.time_sec  0.035 0.042 0.038 0.005 
compute_gmfs_and_curves.memory_mb 0.0   0.0   0.0   0.0   
================================= ===== ===== ===== ======

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
total compute_ruptures         0.241     0.113     2     
saving ruptures                0.154     0.0       1     
total compute_gmfs_and_curves  0.077     0.0       2     
compute poes                   0.052     0.0       2     
reading composite source model 0.040     0.0       1     
managing sources               0.025     0.0       1     
bulding hazard curves          0.022     0.0       2     
store source_info              0.008     0.0       1     
aggregating hcurves            0.002     0.0       2     
aggregate curves               0.002     0.0       4     
saving gmfs                    0.001     0.0       2     
make contexts                  0.001     0.0       2     
filtering ruptures             8.769E-04 0.0       2     
filtering sources              3.192E-04 0.0       2     
reading site collection        4.911E-05 0.0       1     
============================== ========= ========= ======