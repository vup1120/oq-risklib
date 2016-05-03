Classical PSHA - Loss fractions QA test
=======================================

gem-tstation:/home/michele/ssd/calc_953.hdf5 updated Thu Apr 28 15:38:20 2016

num_sites = 13, sitecol = 1.26 KB

Parameters
----------
============================ ===================
calculation_mode             'classical_risk'   
number_of_logic_tree_samples 1                  
maximum_distance             {'default': 200.0} 
investigation_time           50.0               
ses_per_logic_tree_path      1                  
truncation_level             3.0                
rupture_mesh_spacing         5.0                
complex_fault_mesh_spacing   5.0                
width_of_mfd_bin             0.2                
area_source_discretization   10.0               
random_seed                  23                 
master_seed                  0                  
avg_losses                   False              
sites_per_tile               1000               
oqlite_version               '0.13.0-git93d6f64'
============================ ===================

Input files
-----------
======================== ============================================================
Name                     File                                                        
======================== ============================================================
exposure                 `exposure_model.xml <exposure_model.xml>`_                  
gsim_logic_tree          `gmpe_logic_tree.xml <gmpe_logic_tree.xml>`_                
job_ini                  `job.ini <job.ini>`_                                        
source                   `source_model.xml <source_model.xml>`_                      
source_model_logic_tree  `source_model_logic_tree.xml <source_model_logic_tree.xml>`_
structural_vulnerability `vulnerability_model.xml <vulnerability_model.xml>`_        
======================== ============================================================

Composite source model
----------------------
========= ====== ====================================== =============== ================
smlt_path weight source_model_file                      gsim_logic_tree num_realizations
========= ====== ====================================== =============== ================
b1        1.000  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
========= ====== ====================================== =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== =============== =========== ======================= =================
trt_id gsims           distances   siteparams              ruptparams       
====== =============== =========== ======================= =================
0      ChiouYoungs2008 rx rjb rrup vs30measured vs30 z1pt0 rake dip ztor mag
====== =============== =========== ======================= =================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=1, rlzs=1)
  0,ChiouYoungs2008: ['<0,b1,b1,w=1.0>']>

Number of ruptures per tectonic region type
-------------------------------------------
================ ====== ==================== =========== ============ ======
source_model     trt_id trt                  num_sources eff_ruptures weight
================ ====== ==================== =========== ============ ======
source_model.xml 0      Active Shallow Crust 2           1,613        53    
================ ====== ==================== =========== ============ ======

Informational data
------------------
================ ==============
hostname         'gem-tstation'
require_epsilons True          
================ ==============

Exposure model
--------------
=========== ==
#assets     13
#taxonomies 4 
=========== ==

======== =======
Taxonomy #Assets
======== =======
A        4      
DS       2      
UFB      2      
W        5      
======== =======

Slowest sources
---------------
============ ========= ============ ====== ========= =========== ========== =========
trt_model_id source_id source_class weight split_num filter_time split_time calc_time
============ ========= ============ ====== ========= =========== ========== =========
0            232       AreaSource   40     1         0.001       0.0        4.589    
0            225       AreaSource   13     1         0.001       0.0        0.847    
============ ========= ============ ====== ========= =========== ========== =========

Information about the tasks
---------------------------
======================== ===== ===== ===== ======
measurement              min   max   mean  stddev
classical_risk.time_sec  0.995 1.275 1.135 0.098 
classical_risk.memory_mb 1.160 1.262 1.193 0.044 
classical.time_sec       0.850 4.592 2.721 2.646 
classical.memory_mb      2.836 2.910 2.873 0.052 
classical.time_sec       0.850 4.592 2.721 2.646 
classical.memory_mb      2.836 2.910 2.873 0.052 
======================== ===== ===== ===== ======

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
total classical_risk           14        1.262     13    
computing risk                 14        0.0       13    
total classical                5.442     2.910     2     
making contexts                3.084     0.0       2,132 
reading composite source model 2.164     0.0       1     
computing poes                 1.065     0.0       1,613 
managing sources               0.116     0.0       1     
store source_info              0.025     0.0       1     
filtering sources              0.023     0.0       15    
reading exposure               0.009     0.0       1     
save curves_by_trt_gsim        0.002     0.0       1     
building hazard                0.002     0.0       13    
building riskinputs            0.001     0.0       1     
save curves_by_rlz             9.780E-04 0.0       1     
aggregate curves               9.429E-04 0.0       2     
combine curves_by_rlz          1.550E-04 0.0       1     
reading site collection        1.001E-05 0.0       1     
============================== ========= ========= ======