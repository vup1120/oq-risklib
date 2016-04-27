Classical PSHA QA test
======================

gem-tstation:/home/michele/ssd/calc_86.hdf5 updated Wed Apr 27 10:55:29 2016

num_sites = 21, sitecol = 1.62 KB

Parameters
----------
============================ ===================
calculation_mode             'classical'        
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 200.0} 
investigation_time           50.0               
ses_per_logic_tree_path      1                  
truncation_level             3.0                
rupture_mesh_spacing         4.0                
complex_fault_mesh_spacing   4.0                
width_of_mfd_bin             0.1                
area_source_discretization   10.0               
random_seed                  23                 
master_seed                  0                  
sites_per_tile               1000               
oqlite_version               '0.13.0-gitcbbc4a8'
============================ ===================

Input files
-----------
======================= ================================================================
Name                    File                                                            
======================= ================================================================
gsim_logic_tree         `gmpe_logic_tree.xml <gmpe_logic_tree.xml>`_                    
job_ini                 `job.ini <job.ini>`_                                            
sites                   `qa_sites.csv <qa_sites.csv>`_                                  
source                  `aFault_aPriori_D2.1.xml <aFault_aPriori_D2.1.xml>`_            
source                  `bFault_stitched_D2.1_Char.xml <bFault_stitched_D2.1_Char.xml>`_
source_model_logic_tree `source_model_logic_tree.xml <source_model_logic_tree.xml>`_    
======================= ================================================================

Composite source model
----------------------
========================= ====== ================================================================ =============== ================
smlt_path                 weight source_model_file                                                gsim_logic_tree num_realizations
========================= ====== ================================================================ =============== ================
aFault_aPriori_D2.1       0.500  `aFault_aPriori_D2.1.xml <aFault_aPriori_D2.1.xml>`_             simple(2)       2/2             
bFault_stitched_D2.1_Char 0.500  `bFault_stitched_D2.1_Char.xml <bFault_stitched_D2.1_Char.xml>`_ simple(2)       2/2             
========================= ====== ================================================================ =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== ================================= =========== ======================= =================
trt_id gsims                             distances   siteparams              ruptparams       
====== ================================= =========== ======================= =================
0      BooreAtkinson2008 ChiouYoungs2008 rx rjb rrup vs30measured z1pt0 vs30 ztor mag rake dip
1      BooreAtkinson2008 ChiouYoungs2008 rx rjb rrup vs30measured z1pt0 vs30 ztor mag rake dip
====== ================================= =========== ======================= =================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=4, rlzs=4)
  0,BooreAtkinson2008: ['<0,aFault_aPriori_D2.1,BooreAtkinson2008,w=0.25>']
  0,ChiouYoungs2008: ['<1,aFault_aPriori_D2.1,ChiouYoungs2008,w=0.25>']
  1,BooreAtkinson2008: ['<2,bFault_stitched_D2.1_Char,BooreAtkinson2008,w=0.25>']
  1,ChiouYoungs2008: ['<3,bFault_stitched_D2.1_Char,ChiouYoungs2008,w=0.25>']>

Number of ruptures per tectonic region type
-------------------------------------------
============================= ====== ==================== =========== ============ ======
source_model                  trt_id trt                  num_sources eff_ruptures weight
============================= ====== ==================== =========== ============ ======
aFault_aPriori_D2.1.xml       0      Active Shallow Crust 168         1,848        1,848 
bFault_stitched_D2.1_Char.xml 1      Active Shallow Crust 186         2,046        2,046 
============================= ====== ==================== =========== ============ ======

=============== =====
#TRT models     2    
#sources        354  
#eff_ruptures   3,894
filtered_weight 3,894
=============== =====

Informational data
------------------
======================================== ==============
count_eff_ruptures_max_received_per_task 3078          
count_eff_ruptures_num_tasks             72            
count_eff_ruptures_sent.monitor          203652        
count_eff_ruptures_sent.rlzs_assoc       347544        
count_eff_ruptures_sent.sitecol          66024         
count_eff_ruptures_sent.siteidx          360           
count_eff_ruptures_sent.sources          1312799       
count_eff_ruptures_tot_received          221616        
hazard.input_weight                      4686.0        
hazard.n_imts                            2             
hazard.n_levels                          13.0          
hazard.n_realizations                    4             
hazard.n_sites                           21            
hazard.n_sources                         0             
hazard.output_weight                     2184.0        
hostname                                 'gem-tstation'
======================================== ==============

Slowest sources
---------------
============ ========= ==================== ====== ========= =========== ========== =========
trt_model_id source_id source_class         weight split_num filter_time split_time calc_time
============ ========= ==================== ====== ========= =========== ========== =========
0            0_0       CharacteristicFaultS 11     1         0.001       0.0        0.0      
1            105_1     CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            81_0      CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            81_1      CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            43_1      CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            25_1      CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            22_0      CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            27_0      CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            29_0      CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            13_0      CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            35_0      CharacteristicFaultS 11     1         0.001       0.0        0.0      
1            103_1     CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            12_0      CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            31_1      CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            0_1       CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            48_0      CharacteristicFaultS 11     1         0.001       0.0        0.0      
1            100_1     CharacteristicFaultS 11     1         0.001       0.0        0.0      
1            31_1      CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            41_0      CharacteristicFaultS 11     1         0.001       0.0        0.0      
0            86_1      CharacteristicFaultS 11     1         0.001       0.0        0.0      
============ ========= ==================== ====== ========= =========== ========== =========

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
reading composite source model 2.821     0.0       1     
managing sources               0.581     0.0       1     
filtering sources              0.476     0.0       426   
total count_eff_ruptures       0.026     0.0       72    
store source_info              0.004     0.0       1     
aggregate curves               0.001     0.0       72    
reading site collection        2.890E-04 0.0       1     
============================== ========= ========= ======