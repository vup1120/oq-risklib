Classical PSHA with non-trivial logic tree (1 source model + 5 (a, b) pairs per source + 3 Mmax per source
==========================================================================================================

gem-tstation:/home/michele/ssd/calc_1013.hdf5 updated Thu Apr 28 15:42:21 2016

num_sites = 1, sitecol = 739 B

Parameters
----------
============================ ===================
calculation_mode             'classical'        
number_of_logic_tree_samples 10                 
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
source                  `source_model.xml <source_model.xml>`_                      
source_model_logic_tree `source_model_logic_tree.xml <source_model_logic_tree.xml>`_
======================= ============================================================

Composite source model
----------------------
============================================= ====== ====================================== =============== ================
smlt_path                                     weight source_model_file                      gsim_logic_tree num_realizations
============================================= ====== ====================================== =============== ================
b11_b20_b31_b43_b52_b62_b72_b82_b91_b103_b112 0.100  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
b11_b21_b32_b43_b52_b62_b72_b82_b92_b102_b112 0.100  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
b11_b21_b32_b43_b52_b62_b73_b82_b92_b103_b113 0.100  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
b11_b22_b31_b43_b52_b64_b73_b84_b92_b104_b112 0.100  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
b11_b22_b32_b42_b51_b61_b72_b83_b91_b101_b111 0.100  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
b11_b22_b32_b42_b53_b62_b72_b81_b92_b103_b112 0.100  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
b11_b22_b33_b42_b52_b62_b72_b82_b92_b100_b112 0.100  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
b11_b23_b32_b43_b52_b62_b73_b82_b93_b101_b113 0.100  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
b11_b24_b32_b41_b51_b62_b71_b84_b93_b101_b111 0.100  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
b11_b24_b33_b40_b52_b62_b72_b81_b91_b102_b112 0.100  `source_model.xml <source_model.xml>`_ trivial(1)      1/1             
============================================= ====== ====================================== =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== ================= ========= ========== ==========
trt_id gsims             distances siteparams ruptparams
====== ================= ========= ========== ==========
0      BooreAtkinson2008 rjb       vs30       rake mag  
1      BooreAtkinson2008 rjb       vs30       rake mag  
2      BooreAtkinson2008 rjb       vs30       rake mag  
3      BooreAtkinson2008 rjb       vs30       rake mag  
4      BooreAtkinson2008 rjb       vs30       rake mag  
5      BooreAtkinson2008 rjb       vs30       rake mag  
6      BooreAtkinson2008 rjb       vs30       rake mag  
7      BooreAtkinson2008 rjb       vs30       rake mag  
8      BooreAtkinson2008 rjb       vs30       rake mag  
9      BooreAtkinson2008 rjb       vs30       rake mag  
====== ================= ========= ========== ==========

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=10, rlzs=10)
  0,BooreAtkinson2008: ['<0,b11_b20_b31_b43_b52_b62_b72_b82_b91_b103_b112,b11,w=0.1>']
  1,BooreAtkinson2008: ['<1,b11_b21_b32_b43_b52_b62_b72_b82_b92_b102_b112,b11,w=0.1>']
  2,BooreAtkinson2008: ['<2,b11_b21_b32_b43_b52_b62_b73_b82_b92_b103_b113,b11,w=0.1>']
  3,BooreAtkinson2008: ['<3,b11_b22_b31_b43_b52_b64_b73_b84_b92_b104_b112,b11,w=0.1>']
  4,BooreAtkinson2008: ['<4,b11_b22_b32_b42_b51_b61_b72_b83_b91_b101_b111,b11,w=0.1>']
  5,BooreAtkinson2008: ['<5,b11_b22_b32_b42_b53_b62_b72_b81_b92_b103_b112,b11,w=0.1>']
  6,BooreAtkinson2008: ['<6,b11_b22_b33_b42_b52_b62_b72_b82_b92_b100_b112,b11,w=0.1>']
  7,BooreAtkinson2008: ['<7,b11_b23_b32_b43_b52_b62_b73_b82_b93_b101_b113,b11,w=0.1>']
  8,BooreAtkinson2008: ['<8,b11_b24_b32_b41_b51_b62_b71_b84_b93_b101_b111,b11,w=0.1>']
  9,BooreAtkinson2008: ['<9,b11_b24_b33_b40_b52_b62_b72_b81_b91_b102_b112,b11,w=0.1>']>

Number of ruptures per tectonic region type
-------------------------------------------
================ ====== ==================== =========== ============ ======
source_model     trt_id trt                  num_sources eff_ruptures weight
================ ====== ==================== =========== ============ ======
source_model.xml 0      Active Shallow Crust 5           1,925        48    
source_model.xml 1      Active Shallow Crust 5           2,025        50    
source_model.xml 2      Active Shallow Crust 5           2,135        53    
source_model.xml 3      Active Shallow Crust 5           2,035        50    
source_model.xml 4      Active Shallow Crust 5           1,865        46    
source_model.xml 5      Active Shallow Crust 5           2,085        52    
source_model.xml 6      Active Shallow Crust 5           2,075        51    
source_model.xml 7      Active Shallow Crust 5           2,185        54    
source_model.xml 8      Active Shallow Crust 5           1,905        47    
source_model.xml 9      Active Shallow Crust 5           2,025        50    
================ ====== ==================== =========== ============ ======

=============== ======
#TRT models     10    
#sources        50    
#eff_ruptures   20,260
filtered_weight 506   
=============== ======

Informational data
------------------
======================================== ==============
count_eff_ruptures_max_received_per_task 2735          
count_eff_ruptures_num_tasks             50            
count_eff_ruptures_sent.monitor          124400        
count_eff_ruptures_sent.rlzs_assoc       857250        
count_eff_ruptures_sent.sitecol          21850         
count_eff_ruptures_sent.siteidx          250           
count_eff_ruptures_sent.sources          95900         
count_eff_ruptures_tot_received          136750        
hazard.input_weight                      506.5         
hazard.n_imts                            1             
hazard.n_levels                          3.0           
hazard.n_realizations                    10            
hazard.n_sites                           1             
hazard.n_sources                         0             
hazard.output_weight                     30.0          
hostname                                 'gem-tstation'
======================================== ==============

Slowest sources
---------------
============ ========= ============ ====== ========= =========== ========== =========
trt_model_id source_id source_class weight split_num filter_time split_time calc_time
============ ========= ============ ====== ========= =========== ========== =========
0            1         AreaSource   8.125  1         0.002       0.0        0.0      
9            1         AreaSource   10     1         0.001       0.0        0.0      
2            5         AreaSource   10     1         0.001       0.0        0.0      
1            1         AreaSource   9.375  1         0.001       0.0        0.0      
5            1         AreaSource   9.375  1         0.001       0.0        0.0      
6            2         AreaSource   11     1         0.001       0.0        0.0      
3            3         AreaSource   12     1         0.001       0.0        0.0      
7            5         AreaSource   10     1         0.001       0.0        0.0      
1            4         AreaSource   9.375  1         0.001       0.0        0.0      
4            3         AreaSource   11     1         0.001       0.0        0.0      
5            4         AreaSource   9.375  1         0.001       0.0        0.0      
8            3         AreaSource   9.750  1         0.001       0.0        0.0      
2            2         AreaSource   11     1         0.001       0.0        0.0      
0            3         AreaSource   11     1         0.001       0.0        0.0      
7            2         AreaSource   11     1         0.001       0.0        0.0      
9            4         AreaSource   8.125  1         0.001       0.0        0.0      
6            5         AreaSource   9.375  1         0.001       0.0        0.0      
3            5         AreaSource   9.375  1         0.001       0.0        0.0      
8            4         AreaSource   10     1         0.001       0.0        0.0      
6            1         AreaSource   10     1         0.001       0.0        0.0      
============ ========= ============ ====== ========= =========== ========== =========

Information about the tasks
---------------------------
Not available

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
reading composite source model 0.493     0.0       1     
managing sources               0.373     0.0       1     
filtering sources              0.070     0.0       50    
total count_eff_ruptures       0.015     0.0       50    
store source_info              0.007     0.0       1     
aggregate curves               0.001     0.0       50    
reading site collection        4.721E-05 0.0       1     
============================== ========= ========= ======