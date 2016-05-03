event based risk
================

gem-tstation:/home/michele/ssd/calc_994.hdf5 updated Thu Apr 28 15:39:29 2016

num_sites = 7, sitecol = 1015 B

Parameters
----------
============================ ===================
calculation_mode             'event_based_risk' 
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 200.0} 
investigation_time           50.0               
ses_per_logic_tree_path      2                  
truncation_level             3.0                
rupture_mesh_spacing         2.0                
complex_fault_mesh_spacing   2.0                
width_of_mfd_bin             0.1                
area_source_discretization   10.0               
random_seed                  24                 
master_seed                  0                  
avg_losses                   True               
oqlite_version               '0.13.0-git93d6f64'
============================ ===================

Input files
-----------
=================================== ================================================================================
Name                                File                                                                            
=================================== ================================================================================
business_interruption_vulnerability `downtime_vulnerability_model.xml <downtime_vulnerability_model.xml>`_          
contents_vulnerability              `contents_vulnerability_model.xml <contents_vulnerability_model.xml>`_          
exposure                            `exposure_model.xml <exposure_model.xml>`_                                      
gsim_logic_tree                     `gsim_logic_tree.xml <gsim_logic_tree.xml>`_                                    
job_ini                             `job.ini <job.ini>`_                                                            
nonstructural_vulnerability         `nonstructural_vulnerability_model.xml <nonstructural_vulnerability_model.xml>`_
occupants_vulnerability             `occupants_vulnerability_model.xml <occupants_vulnerability_model.xml>`_        
source_model_logic_tree             `source_model_logic_tree.xml <source_model_logic_tree.xml>`_                    
structural_vulnerability            `structural_vulnerability_model.xml <structural_vulnerability_model.xml>`_      
=================================== ================================================================================

Composite source model
----------------------
========= ====== ========================================== =============== ================
smlt_path weight source_model_file                          gsim_logic_tree num_realizations
========= ====== ========================================== =============== ================
b1        0.250  `source_model_1.xml <source_model_1.xml>`_ complex(2,2)    4/4             
b2        0.750  `source_model_2.xml <source_model_2.xml>`_ simple(2,0)     2/2             
========= ====== ========================================== =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== ================================= =========== ======================= =================
trt_id gsims                             distances   siteparams              ruptparams       
====== ================================= =========== ======================= =================
0      BooreAtkinson2008 ChiouYoungs2008 rx rjb rrup vs30measured z1pt0 vs30 ztor mag rake dip
1      AkkarBommer2010 ChiouYoungs2008   rx rjb rrup vs30measured z1pt0 vs30 ztor mag rake dip
2      BooreAtkinson2008 ChiouYoungs2008 rx rjb rrup vs30measured z1pt0 vs30 ztor mag rake dip
====== ================================= =========== ======================= =================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=6, rlzs=6)
  0,BooreAtkinson2008: ['<0,b1,b11_b21,w=0.1125>', '<1,b1,b11_b22,w=0.075>']
  0,ChiouYoungs2008: ['<2,b1,b12_b21,w=0.0375>', '<3,b1,b12_b22,w=0.025>']
  1,AkkarBommer2010: ['<0,b1,b11_b21,w=0.1125>', '<2,b1,b12_b21,w=0.0375>']
  1,ChiouYoungs2008: ['<1,b1,b11_b22,w=0.075>', '<3,b1,b12_b22,w=0.025>']
  2,BooreAtkinson2008: ['<4,b2,b11_@,w=0.5625>']
  2,ChiouYoungs2008: ['<5,b2,b12_@,w=0.1875>']>

Number of ruptures per tectonic region type
-------------------------------------------
================== ====== ==================== =========== ============ ======
source_model       trt_id trt                  num_sources eff_ruptures weight
================== ====== ==================== =========== ============ ======
source_model_1.xml 0      Active Shallow Crust 1           1            482   
source_model_1.xml 1      Stable Shallow Crust 1           4            4.000 
source_model_2.xml 2      Active Shallow Crust 1           4            482   
================== ====== ==================== =========== ============ ======

=============== ===
#TRT models     3  
#sources        3  
#eff_ruptures   9  
filtered_weight 968
=============== ===

Informational data
------------------
====================================== ==============
event_based_risk_max_received_per_task 113592        
event_based_risk_num_tasks             6             
event_based_risk_sent.assetcol         26502         
event_based_risk_sent.monitor          16116         
event_based_risk_sent.riskinput        27698         
event_based_risk_sent.riskmodel        64488         
event_based_risk_sent.rlzs_assoc       41574         
event_based_risk_tot_received          523461        
hostname                               'gem-tstation'
require_epsilons                       True          
====================================== ==============

Specific information for event based
------------------------------------
======================== ===
Total number of ruptures 9  
Total number of events   106
Rupture multiplicity     11 
======================== ===

Maximum memory allocated for the GMFs
-------------------------------------
The largest GMF block is for trt_model_id=1, contains 4 IMT(s), 4 realization(s)
and has a size of 44.19 KB / num_tasks

Estimated data transfer for the avglosses
-----------------------------------------
7 asset(s) x 6 realization(s) x 5 loss type(s) x 2 losses x 8 bytes x 40 tasks = 131.25 KB

Exposure model
--------------
=========== =
#assets     7
#taxonomies 3
=========== =

======== =======
Taxonomy #Assets
======== =======
tax1     4      
tax2     2      
tax3     1      
======== =======

Slowest sources
---------------
============ ========= ==================== ====== ========= =========== ========== =========
trt_model_id source_id source_class         weight split_num filter_time split_time calc_time
============ ========= ==================== ====== ========= =========== ========== =========
0            1         SimpleFaultSource    482    15        0.003       0.151      0.441    
2            1         SimpleFaultSource    482    15        0.003       0.083      0.390    
1            2         SimpleFaultSource    4.000  1         0.011       0.0        0.021    
3            2         CharacteristicFaultS 1.000  1         0.002       0.0        0.003    
============ ========= ==================== ====== ========= =========== ========== =========

Information about the tasks
---------------------------
================================= ===== ===== ===== ======
measurement                       min   max   mean  stddev
compute_ruptures.time_sec         0.003 0.079 0.029 0.020 
compute_ruptures.memory_mb        0.0   0.012 0.001 0.003 
compute_gmfs_and_curves.time_sec  0.072 0.083 0.078 0.005 
compute_gmfs_and_curves.memory_mb 0.0   0.012 0.003 0.005 
event_based_risk.time_sec         0.275 0.452 0.362 0.080 
event_based_risk.memory_mb        0.0   0.074 0.013 0.030 
================================= ===== ===== ===== ======

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
total event_based_risk         2.170     0.074     6     
computing risk                 1.760     0.0       42    
total compute_ruptures         0.866     0.012     30    
managing sources               0.537     0.0       1     
compute poes                   0.509     0.0       18    
total compute_gmfs_and_curves  0.468     0.012     6     
aggregate losses               0.355     0.0       66    
building hazard                0.314     0.0       6     
saving event loss tables       0.259     0.0       6     
splitting sources              0.234     0.0       2     
bulding hazard curves          0.154     0.0       6     
make contexts                  0.092     0.0       18    
filtering ruptures             0.056     0.0       9     
reading composite source model 0.049     0.0       1     
save curves_by_rlz             0.047     0.0       1     
compute and save statistics    0.041     0.0       1     
getting hazard                 0.037     0.0       42    
store source_info              0.026     0.0       1     
aggregating hcurves            0.020     0.0       22    
filtering sources              0.019     0.0       4     
saving gmfs                    0.015     0.0       22    
reading exposure               0.013     0.0       1     
saving ruptures                0.011     0.0       1     
aggregate curves               0.006     0.0       52    
reading site collection        1.001E-05 0.0       1     
============================== ========= ========= ======