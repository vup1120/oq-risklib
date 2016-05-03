Classical PSHA QA test with sites_csv
=====================================

gem-tstation:/home/michele/ssd/calc_1008.hdf5 updated Thu Apr 28 15:40:59 2016

num_sites = 10, sitecol = 1.13 KB

Parameters
----------
============================ ===================
calculation_mode             'classical'        
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 200.0} 
investigation_time           50.0               
ses_per_logic_tree_path      1                  
truncation_level             3.0                
rupture_mesh_spacing         2.0                
complex_fault_mesh_spacing   2.0                
width_of_mfd_bin             0.1                
area_source_discretization   10.0               
random_seed                  23                 
master_seed                  0                  
sites_per_tile               1000               
oqlite_version               '0.13.0-git93d6f64'
============================ ===================

Input files
-----------
======================= ============================================================
Name                    File                                                        
======================= ============================================================
gsim_logic_tree         `gmpe_logic_tree.xml <gmpe_logic_tree.xml>`_                
job_ini                 `job.ini <job.ini>`_                                        
sites                   `qa_sites.csv <qa_sites.csv>`_                              
source                  `simple_fault.xml <simple_fault.xml>`_                      
source_model_logic_tree `source_model_logic_tree.xml <source_model_logic_tree.xml>`_
======================= ============================================================

Composite source model
----------------------
============ ====== ====================================== =============== ================
smlt_path    weight source_model_file                      gsim_logic_tree num_realizations
============ ====== ====================================== =============== ================
simple_fault 1.000  `simple_fault.xml <simple_fault.xml>`_ simple(2)       2/2             
============ ====== ====================================== =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== ========================================= =========== ============================= =======================
trt_id gsims                                     distances   siteparams                    ruptparams             
====== ========================================= =========== ============================= =======================
0      AbrahamsonSilva2008 CampbellBozorgnia2008 rx rjb rrup vs30measured vs30 z2pt5 z1pt0 rake width ztor mag dip
====== ========================================= =========== ============================= =======================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=2, rlzs=2)
  0,AbrahamsonSilva2008: ['<0,simple_fault,AbrahamsonSilva2008,w=0.5>']
  0,CampbellBozorgnia2008: ['<1,simple_fault,CampbellBozorgnia2008,w=0.5>']>

Number of ruptures per tectonic region type
-------------------------------------------
================ ====== ==================== =========== ============ ======
source_model     trt_id trt                  num_sources eff_ruptures weight
================ ====== ==================== =========== ============ ======
simple_fault.xml 0      Active Shallow Crust 1           447          447   
================ ====== ==================== =========== ============ ======

Informational data
------------------
======================================== ==============
count_eff_ruptures_max_received_per_task 2814          
count_eff_ruptures_num_tasks             15            
count_eff_ruptures_sent.monitor          38505         
count_eff_ruptures_sent.rlzs_assoc       45975         
count_eff_ruptures_sent.sitecol          9795          
count_eff_ruptures_sent.siteidx          75            
count_eff_ruptures_sent.sources          16295         
count_eff_ruptures_tot_received          42210         
hazard.input_weight                      447.0         
hazard.n_imts                            1             
hazard.n_levels                          13.0          
hazard.n_realizations                    2             
hazard.n_sites                           10            
hazard.n_sources                         0             
hazard.output_weight                     260.0         
hostname                                 'gem-tstation'
======================================== ==============

Slowest sources
---------------
============ ========= ================= ====== ========= =========== ========== =========
trt_model_id source_id source_class      weight split_num filter_time split_time calc_time
============ ========= ================= ====== ========= =========== ========== =========
0            3         SimpleFaultSource 447    15        0.003       0.083      0.0      
============ ========= ================= ====== ========= =========== ========== =========

Information about the tasks
---------------------------
Not available

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
managing sources               0.122     0.0       1     
splitting sources              0.083     0.0       1     
reading composite source model 0.012     0.0       1     
store source_info              0.006     0.0       1     
total count_eff_ruptures       0.004     0.0       15    
filtering sources              0.003     0.0       1     
aggregate curves               3.738E-04 0.0       15    
reading site collection        1.640E-04 0.0       1     
============================== ========= ========= ======