Virtual Island - City C, 2 SES, grid=0.1
========================================

gem-tstation:/home/michele/ssd/calc_19657.hdf5 updated Wed May 25 08:33:17 2016

num_sites = 1792, sitecol = 44.71 KB

Parameters
----------
============================ ===================
calculation_mode             'event_based_risk' 
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 200.0} 
investigation_time           50.0               
ses_per_logic_tree_path      2                  
truncation_level             4.0                
rupture_mesh_spacing         10.0               
complex_fault_mesh_spacing   10.0               
width_of_mfd_bin             0.2                
area_source_discretization   None               
random_seed                  1024               
master_seed                  100                
avg_losses                   False              
oqlite_version               '0.13.0-git1cc9966'
============================ ===================

Input files
-----------
======================== ============================================================
Name                     File                                                        
======================== ============================================================
exposure                 `exposure_model.xml <exposure_model.xml>`_                  
gsim_logic_tree          `gsim_logic_tree.xml <gsim_logic_tree.xml>`_                
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
b1        1.000  `source_model.xml <source_model.xml>`_ trivial(1,0)    1/1             
========= ====== ====================================== =============== ================

Required parameters per tectonic region type
--------------------------------------------
====== ================= ========= ========== ==========
trt_id gsims             distances siteparams ruptparams
====== ================= ========= ========== ==========
0      AkkarBommer2010() rjb       vs30       rake mag  
====== ================= ========= ========== ==========

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=1, rlzs=1)
  0,AkkarBommer2010(): ['<0,b1,b1_@,w=1.0>']>

Number of ruptures per tectonic region type
-------------------------------------------
================ ====== ==================== =========== ============ ======
source_model     trt_id trt                  num_sources eff_ruptures weight
================ ====== ==================== =========== ============ ======
source_model.xml 0      Active Shallow Crust 1           44           2,558 
================ ====== ==================== =========== ============ ======

Informational data
------------------
====================================== ==============
event_based_risk_max_received_per_task 4038          
event_based_risk_num_tasks             23            
event_based_risk_sent.assetcol         511451        
event_based_risk_sent.monitor          60674         
event_based_risk_sent.riskinput        1265317       
event_based_risk_sent.riskmodel        437138        
event_based_risk_sent.rlzs_assoc       22011         
event_based_risk_tot_received          92856         
hostname                               'gem-tstation'
require_epsilons                       True          
====================================== ==============

Specific information for event based
------------------------------------
======================== =====
Total number of ruptures 44   
Total number of events   45   
Rupture multiplicity     1.023
======================== =====

Maximum memory allocated for the GMFs
-------------------------------------
The largest GMF block is for trt_model_id=0, contains 1 IMT(s), 1 realization(s)
and has a size of 49.39 KB / num_tasks

Estimated data transfer for the avglosses
-----------------------------------------
548 asset(s) x 1 realization(s) x 1 loss type(s) x 1 losses x 8 bytes x 20 tasks = 85.62 KB

Exposure model
--------------
=========== ===
#assets     548
#taxonomies 11 
=========== ===

========== ===== ====== === === ========= ==========
taxonomy   mean  stddev min max num_sites num_assets
A-SPSB-1   1.250 0.463  1   2   8         10        
MC-RCSB-1  1.286 0.561  1   3   21        27        
MC-RLSB-2  1.256 0.880  1   6   39        49        
MR-RCSB-2  1.456 0.799  1   6   171       249       
MR-SLSB-1  1.000 0.0    1   1   5         5         
MS-FLSB-2  1.250 0.452  1   2   12        15        
MS-SLSB-1  1.545 0.934  1   4   11        17        
PCR-RCSM-5 1.000 0.0    1   1   2         2         
PCR-SLSB-1 1.000 0.0    1   1   3         3         
W-FLFB-2   1.222 0.502  1   3   54        66        
W-SLFB-1   1.265 0.520  1   3   83        105       
*ALL*      1.950 1.306  1   10  281       548       
========== ===== ====== === === ========= ==========

Slowest sources
---------------
============ ========= ================== ====== ========= =========== ========== =========
trt_model_id source_id source_class       weight split_num filter_time split_time calc_time
============ ========= ================== ====== ========= =========== ========== =========
0            F         ComplexFaultSource 2,558  1,119     0.001       1.877      1.889    
============ ========= ================== ====== ========= =========== ========== =========

Computation times by source typology
------------------------------------
================== =========== ========== ========= ======
source_class       filter_time split_time calc_time counts
================== =========== ========== ========= ======
ComplexFaultSource 0.001       1.877      1.889     1     
================== =========== ========== ========= ======

Information about the tasks
---------------------------
========================== ===== ====== ========= ===== =========
measurement                mean  stddev min       max   num_tasks
compute_ruptures.time_sec  0.076 0.120  8.540E-04 0.275 25       
compute_ruptures.memory_mb 0.0   0.0    0.0       0.0   25       
event_based_risk.time_sec  0.041 0.013  0.028     0.082 23       
event_based_risk.memory_mb 0.0   0.0    0.0       0.0   23       
========================== ===== ====== ========= ===== =========

Slowest operations
------------------
============================== ======== ========= ======
operation                      time_sec memory_mb counts
============================== ======== ========= ======
managing sources               1.994    0.0       1     
total compute_ruptures         1.903    0.0       25    
splitting sources              1.877    0.0       1     
total event_based_risk         0.948    0.0       23    
building hazard                0.446    0.0       23    
reading site collection        0.207    0.0       1     
computing riskmodel            0.191    0.0       9,407 
reading exposure               0.158    0.0       1     
building riskinputs            0.103    0.0       1     
compute poes                   0.084    0.0       44    
reading composite source model 0.065    0.0       1     
saving ruptures                0.044    0.0       1     
aggregate losses               0.038    0.0       9,407 
make contexts                  0.018    0.0       44    
store source_info              0.016    0.0       1     
filtering ruptures             0.014    0.0       57    
aggregate curves               0.006    0.0       25    
saving event loss tables       0.006    0.0       23    
filtering sources              0.001    0.0       1     
============================== ======== ========= ======