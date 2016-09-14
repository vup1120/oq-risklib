QA test for disaggregation case_1, taken from the disagg demo
=============================================================

gem-tstation:/home/michele/ssd/calc_19703.hdf5 updated Wed May 25 08:35:07 2016

num_sites = 2, sitecol = 785 B

Parameters
----------
============================ ===================
calculation_mode             'disaggregation'   
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 200.0} 
investigation_time           50.0               
ses_per_logic_tree_path      1                  
truncation_level             3.0                
rupture_mesh_spacing         5.0                
complex_fault_mesh_spacing   5.0                
width_of_mfd_bin             0.2                
area_source_discretization   10.0               
random_seed                  9000               
master_seed                  0                  
oqlite_version               '0.13.0-git1cc9966'
============================ ===================

Input files
-----------
======================= ============================================================
Name                    File                                                        
======================= ============================================================
gsim_logic_tree         `gmpe_logic_tree.xml <gmpe_logic_tree.xml>`_                
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
====== ================= =========== ======================= =================
trt_id gsims             distances   siteparams              ruptparams       
====== ================= =========== ======================= =================
0      ChiouYoungs2008() rx rjb rrup vs30measured vs30 z1pt0 rake dip ztor mag
====== ================= =========== ======================= =================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=1, rlzs=1)
  0,ChiouYoungs2008(): ['<0,b1,b1,w=1.0>']>

Number of ruptures per tectonic region type
-------------------------------------------
================ ====== ==================== =========== ============ ======
source_model     trt_id trt                  num_sources eff_ruptures weight
================ ====== ==================== =========== ============ ======
source_model.xml 0      Active Shallow Crust 4           2236         817   
================ ====== ==================== =========== ============ ======

Informational data
------------------
======================================== ==============
count_eff_ruptures_max_received_per_task 3078          
count_eff_ruptures_num_tasks             10            
count_eff_ruptures_sent.monitor          28210         
count_eff_ruptures_sent.rlzs_assoc       7470          
count_eff_ruptures_sent.sitecol          4610          
count_eff_ruptures_sent.siteidx          50            
count_eff_ruptures_sent.sources          82110         
count_eff_ruptures_tot_received          30771         
hazard.input_weight                      817.375       
hazard.n_imts                            2             
hazard.n_levels                          19.0          
hazard.n_realizations                    1             
hazard.n_sites                           2             
hazard.n_sources                         0             
hazard.output_weight                     76.0          
hostname                                 'gem-tstation'
======================================== ==============

Slowest sources
---------------
============ ========= ================== ====== ========= =========== ========== =========
trt_model_id source_id source_class       weight split_num filter_time split_time calc_time
============ ========= ================== ====== ========= =========== ========== =========
0            3         SimpleFaultSource  617    83        0.002       0.037      0.0      
0            4         ComplexFaultSource 164    1         0.001       0.0        0.0      
0            2         AreaSource         36     1         7.041E-04   0.0        0.0      
0            1         PointSource        0.375  1         9.489E-05   0.0        0.0      
============ ========= ================== ====== ========= =========== ========== =========

Computation times by source typology
------------------------------------
================== =========== ========== ========= ======
source_class       filter_time split_time calc_time counts
================== =========== ========== ========= ======
AreaSource         7.041E-04   0.0        0.0       1     
ComplexFaultSource 0.001       0.0        0.0       1     
PointSource        9.489E-05   0.0        0.0       1     
SimpleFaultSource  0.002       0.037      0.0       1     
================== =========== ========== ========= ======

Information about the tasks
---------------------------
Not available

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
managing sources               0.054     0.0       1     
splitting sources              0.037     0.0       1     
reading composite source model 0.032     0.0       1     
store source_info              0.004     0.0       1     
filtering sources              0.004     0.0       4     
total count_eff_ruptures       0.003     0.0       10    
aggregate curves               1.183E-04 0.0       10    
reading site collection        3.195E-05 0.0       1     
============================== ========= ========= ======