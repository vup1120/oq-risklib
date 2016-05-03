Classical Tiling for Turkey reduced
===================================

gem-tstation:/home/michele/ssd/calc_1040.hdf5 updated Thu Apr 28 15:44:25 2016

num_sites = 83, sitecol = 4.42 KB

Parameters
----------
============================ ===================
calculation_mode             'classical'        
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 100.0} 
investigation_time           10.0               
ses_per_logic_tree_path      1                  
truncation_level             3.0                
rupture_mesh_spacing         15.0               
complex_fault_mesh_spacing   15.0               
width_of_mfd_bin             0.1                
area_source_discretization   25.0               
random_seed                  323                
master_seed                  0                  
sites_per_tile               10                 
oqlite_version               '0.13.0-git93d6f64'
============================ ===================

Input files
-----------
======================== ==========================================================================
Name                     File                                                                      
======================== ==========================================================================
gsim_logic_tree          `gmpe_logic_tree.xml <gmpe_logic_tree.xml>`_                              
job_ini                  `job.ini <job.ini>`_                                                      
site_model               `site_model.xml <site_model.xml>`_                                        
source                   `as_model.xml <as_model.xml>`_                                            
source                   `fsbg_model.xml <fsbg_model.xml>`_                                        
source                   `ss_model.xml <ss_model.xml>`_                                            
source_model_logic_tree  `source_model_logic_tree.xml <source_model_logic_tree.xml>`_              
structural_vulnerability `structural_vulnerability_model.xml <structural_vulnerability_model.xml>`_
======================== ==========================================================================

Composite source model
----------------------
======================== ====== ======================================================== ====================== ================
smlt_path                weight source_model_file                                        gsim_logic_tree        num_realizations
======================== ====== ======================================================== ====================== ================
AreaSource               0.500  `models/src/as_model.xml <models/src/as_model.xml>`_     simple(0,0,0,0,0,4,0)  4/4             
FaultSourceAndBackground 0.200  `models/src/fsbg_model.xml <models/src/fsbg_model.xml>`_ simple(0,0,0,0,0,4,0)  4/4             
SeiFaCrust               0.300  `models/src/ss_model.xml <models/src/ss_model.xml>`_     trivial(0,0,0,0,0,0,0) 0/0             
======================== ====== ======================================================== ====================== ================

Required parameters per tectonic region type
--------------------------------------------
====== ================================================================== ================= ======================= ============================
trt_id gsims                                                              distances         siteparams              ruptparams                  
====== ================================================================== ================= ======================= ============================
4      AkkarBommer2010 CauzziFaccioli2008 ChiouYoungs2008 ZhaoEtAl2006Asc rhypo rx rjb rrup vs30measured z1pt0 vs30 ztor mag hypo_depth rake dip
9      AkkarBommer2010 CauzziFaccioli2008 ChiouYoungs2008 ZhaoEtAl2006Asc rhypo rx rjb rrup vs30measured z1pt0 vs30 ztor mag hypo_depth rake dip
====== ================================================================== ================= ======================= ============================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=8, rlzs=8)
  4,AkkarBommer2010: ['<0,AreaSource,AkkarBommer2010asc_@_@_@_@_@_@,w=0.25>']
  4,CauzziFaccioli2008: ['<1,AreaSource,CauzziFaccioli2008asc_@_@_@_@_@_@,w=0.25>']
  4,ChiouYoungs2008: ['<2,AreaSource,ChiouYoungs2008asc_@_@_@_@_@_@,w=0.142857142857>']
  4,ZhaoEtAl2006Asc: ['<3,AreaSource,ZhaoEtAl2006Ascasc_@_@_@_@_@_@,w=0.0714285714286>']
  9,AkkarBommer2010: ['<4,FaultSourceAndBackground,AkkarBommer2010asc_@_@_@_@_@_@,w=0.1>']
  9,CauzziFaccioli2008: ['<5,FaultSourceAndBackground,CauzziFaccioli2008asc_@_@_@_@_@_@,w=0.1>']
  9,ChiouYoungs2008: ['<6,FaultSourceAndBackground,ChiouYoungs2008asc_@_@_@_@_@_@,w=0.0571428571429>']
  9,ZhaoEtAl2006Asc: ['<7,FaultSourceAndBackground,ZhaoEtAl2006Ascasc_@_@_@_@_@_@,w=0.0285714285714>']>

Number of ruptures per tectonic region type
-------------------------------------------
========================= ====== ==================== =========== ============ ======
source_model              trt_id trt                  num_sources eff_ruptures weight
========================= ====== ==================== =========== ============ ======
models/src/as_model.xml   4      Active Shallow Crust 1           3,876        96    
models/src/fsbg_model.xml 9      Active Shallow Crust 2           915          51    
========================= ====== ==================== =========== ============ ======

=============== =====
#TRT models     2    
#sources        3    
#eff_ruptures   4,791
filtered_weight 148  
=============== =====

Informational data
------------------
======================================== ==================
count_eff_ruptures_max_received_per_task 6018              
count_eff_ruptures_num_tasks             13                
count_eff_ruptures_sent.monitor          74854             
count_eff_ruptures_sent.rlzs_assoc       2810470           
count_eff_ruptures_sent.sitecol          13852             
count_eff_ruptures_sent.siteidx          65                
count_eff_ruptures_sent.sources          41008             
count_eff_ruptures_tot_received          78234             
hazard.input_weight                      3359.8500000000004
hazard.n_imts                            2                 
hazard.n_levels                          45.0              
hazard.n_realizations                    684               
hazard.n_sites                           83                
hazard.n_sources                         0                 
hazard.output_weight                     5109480.0         
hostname                                 'gem-tstation'    
require_epsilons                         False             
======================================== ==================

Slowest sources
---------------
============ ============ ============ ====== ========= =========== ========== =========
trt_model_id source_id    source_class weight split_num filter_time split_time calc_time
============ ============ ============ ====== ========= =========== ========== =========
4            AS_GEAS343   AreaSource   96     1         0.021       0.0        0.0      
9            FSBG_TRBG103 AreaSource   43     1         0.008       0.0        0.0      
9            FSBG_ARAS462 AreaSource   7.650  1         0.002       0.0        0.0      
============ ============ ============ ====== ========= =========== ========== =========

Information about the tasks
---------------------------
Not available

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
managing sources               6.346     0.0       1     
reading composite source model 2.105     0.0       1     
filtering sources              0.503     0.0       248   
reading site collection        0.017     0.0       1     
store source_info              0.011     0.0       1     
total count_eff_ruptures       0.005     0.0       13    
aggregate curves               3.135E-04 0.0       13    
============================== ========= ========= ======