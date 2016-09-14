SHARE OpenQuake Computational Settings
======================================

gem-tstation:/home/michele/ssd/calc_19679.hdf5 updated Wed May 25 08:34:15 2016

num_sites = 1, sitecol = 739 B

Parameters
----------
============================ ===================
calculation_mode             'classical'        
number_of_logic_tree_samples 0                  
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
sites_per_tile               10000              
oqlite_version               '0.13.0-git1cc9966'
============================ ===================

Input files
-----------
======================= ==========================================================================
Name                    File                                                                      
======================= ==========================================================================
gsim_logic_tree         `complete_gmpe_logic_tree.xml <complete_gmpe_logic_tree.xml>`_            
job_ini                 `job.ini <job.ini>`_                                                      
source                  `simple_area_source_model.xml <simple_area_source_model.xml>`_            
source_model_logic_tree `simple_source_model_logic_tree.xml <simple_source_model_logic_tree.xml>`_
======================= ==========================================================================

Composite source model
----------------------
========= ====== ============================================================== ===================== ================
smlt_path weight source_model_file                                              gsim_logic_tree       num_realizations
========= ====== ============================================================== ===================== ================
b1        1.000  `simple_area_source_model.xml <simple_area_source_model.xml>`_ simple(0,4,0,0,0,0,0) 4/4             
========= ====== ============================================================== ===================== ================

Required parameters per tectonic region type
--------------------------------------------
====== ==================================================================================== ========== ========== ==============
trt_id gsims                                                                                distances  siteparams ruptparams    
====== ==================================================================================== ========== ========== ==============
4      AtkinsonBoore2003SSlab() LinLee2008SSlab() YoungsEtAl1997SSlab() ZhaoEtAl2006SSlab() rhypo rrup vs30       hypo_depth mag
====== ==================================================================================== ========== ========== ==============

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=4, rlzs=4)
  4,AtkinsonBoore2003SSlab(): ['<0,b1,@_@_@_@_b51_@_@,w=0.2>']
  4,LinLee2008SSlab(): ['<1,b1,@_@_@_@_b52_@_@,w=0.2>']
  4,YoungsEtAl1997SSlab(): ['<2,b1,@_@_@_@_b53_@_@,w=0.2>']
  4,ZhaoEtAl2006SSlab(): ['<3,b1,@_@_@_@_b54_@_@,w=0.4>']>

Number of ruptures per tectonic region type
-------------------------------------------
============================ ====== ================= =========== ============ ======
source_model                 trt_id trt               num_sources eff_ruptures weight
============================ ====== ================= =========== ============ ======
simple_area_source_model.xml 4      Subduction Inslab 1           7770         194   
============================ ====== ================= =========== ============ ======

Informational data
------------------
======================================== =================
count_eff_ruptures_max_received_per_task 4644             
count_eff_ruptures_num_tasks             1                
count_eff_ruptures_sent.monitor          4387             
count_eff_ruptures_sent.rlzs_assoc       41432            
count_eff_ruptures_sent.sitecol          437              
count_eff_ruptures_sent.siteidx          5                
count_eff_ruptures_sent.sources          2787             
count_eff_ruptures_tot_received          4644             
hazard.input_weight                      49408.67500000002
hazard.n_imts                            3                
hazard.n_levels                          26.0             
hazard.n_realizations                    160              
hazard.n_sites                           1                
hazard.n_sources                         0                
hazard.output_weight                     12480.0          
hostname                                 'gem-tstation'   
======================================== =================

Slowest sources
---------------
============ ========= ============ ====== ========= =========== ========== =========
trt_model_id source_id source_class weight split_num filter_time split_time calc_time
============ ========= ============ ====== ========= =========== ========== =========
4            s46       AreaSource   194    1         9.639E-04   0.0        0.0      
============ ========= ============ ====== ========= =========== ========== =========

Computation times by source typology
------------------------------------
============ =========== ========== ========= ======
source_class filter_time split_time calc_time counts
============ =========== ========== ========= ======
AreaSource   9.639E-04   0.0        0.0       1     
============ =========== ========== ========= ======

Information about the tasks
---------------------------
Not available

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
reading composite source model 4.729     0.0       1     
managing sources               0.113     0.0       1     
filtering sources              0.023     0.0       18    
store source_info              0.004     0.0       1     
total count_eff_ruptures       3.362E-04 0.0       1     
reading site collection        3.290E-05 0.0       1     
aggregate curves               1.597E-05 0.0       1     
============================== ========= ========= ======