event based risk
================

gem-tstation:/home/michele/ssd/calc_19652.hdf5 updated Wed May 25 08:32:54 2016

num_sites = 7, sitecol = 1015 B

Parameters
----------
============================ ===================
calculation_mode             'event_based_risk' 
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 200.0} 
investigation_time           10000.0            
ses_per_logic_tree_path      1                  
truncation_level             3.0                
rupture_mesh_spacing         2.0                
complex_fault_mesh_spacing   2.0                
width_of_mfd_bin             0.1                
area_source_discretization   None               
random_seed                  24                 
master_seed                  42                 
avg_losses                   False              
oqlite_version               '0.13.0-git1cc9966'
============================ ===================

Input files
-----------
======================= ============================================================
Name                    File                                                        
======================= ============================================================
exposure                `exposure_model.xml <exposure_model.xml>`_                  
gsim_logic_tree         `gsim_logic_tree.xml <gsim_logic_tree.xml>`_                
job_ini                 `job.ini <job.ini>`_                                        
occupants_vulnerability `vulnerability_model.xml <vulnerability_model.xml>`_        
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
====== =================== ========= ========== ==========
trt_id gsims               distances siteparams ruptparams
====== =================== ========= ========== ==========
0      BooreAtkinson2008() rjb       vs30       rake mag  
====== =================== ========= ========== ==========

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=1, rlzs=1)
  0,BooreAtkinson2008(): ['<0,b1,b1,w=1.0>']>

Number of ruptures per tectonic region type
-------------------------------------------
================ ====== ==================== =========== ============ ======
source_model     trt_id trt                  num_sources eff_ruptures weight
================ ====== ==================== =========== ============ ======
source_model.xml 0      Active Shallow Crust 1           265          482   
================ ====== ==================== =========== ============ ======

Informational data
------------------
====================================== ==============
event_based_risk_max_received_per_task 4992          
event_based_risk_num_tasks             22            
event_based_risk_sent.assetcol         39314         
event_based_risk_sent.monitor          58014         
event_based_risk_sent.riskinput        390467        
event_based_risk_sent.riskmodel        32758         
event_based_risk_sent.rlzs_assoc       18634         
event_based_risk_tot_received          109614        
hostname                               'gem-tstation'
require_epsilons                       True          
====================================== ==============

Specific information for event based
------------------------------------
======================== =====
Total number of ruptures 265  
Total number of events   392  
Rupture multiplicity     1.479
======================== =====

Maximum memory allocated for the GMFs
-------------------------------------
The largest GMF block is for trt_model_id=0, contains 1 IMT(s), 1 realization(s)
and has a size of 10.72 KB / num_tasks

Estimated data transfer for the avglosses
-----------------------------------------
7 asset(s) x 1 realization(s) x 1 loss type(s) x 1 losses x 8 bytes x 20 tasks = 1.09 KB

Exposure model
--------------
=========== =
#assets     7
#taxonomies 1
=========== =

======== ===== ====== === === ========= ==========
taxonomy mean  stddev min max num_sites num_assets
tax1     1.000 0.0    1   1   7         7         
======== ===== ====== === === ========= ==========

Slowest sources
---------------
============ ========= ================= ====== ========= =========== ========== =========
trt_model_id source_id source_class      weight split_num filter_time split_time calc_time
============ ========= ================= ====== ========= =========== ========== =========
0            1         SimpleFaultSource 482    15        0.002       0.035      0.877    
============ ========= ================= ====== ========= =========== ========== =========

Computation times by source typology
------------------------------------
================= =========== ========== ========= ======
source_class      filter_time split_time calc_time counts
================= =========== ========== ========= ======
SimpleFaultSource 0.002       0.035      0.877     1     
================= =========== ========== ========= ======

Information about the tasks
---------------------------
========================== ================ ====== =========== ===== =========
measurement                mean             stddev min         max   num_tasks
compute_ruptures.time_sec  0.063            0.033  0.018       0.145 14       
compute_ruptures.memory_mb -0.0147879464286 0.055  -0.20703125 0.0   14       
event_based_risk.time_sec  0.056            0.015  0.011       0.083 22       
event_based_risk.memory_mb 0.0              0.0    0.0         0.0   22       
========================== ================ ====== =========== ===== =========

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
total event_based_risk         1.243     0.0       22    
building hazard                1.135     0.0       22    
total compute_ruptures         0.883     0.0       14    
filtering ruptures             0.659     0.0       265   
make contexts                  0.617     0.0       265   
compute poes                   0.507     0.0       265   
saving ruptures                0.219     0.0       1     
building riskinputs            0.097     0.0       1     
computing riskmodel            0.081     0.0       154   
managing sources               0.051     0.0       1     
splitting sources              0.035     0.0       1     
aggregate losses               0.026     0.0       154   
store source_info              0.009     0.0       1     
reading composite source model 0.008     0.0       1     
reading exposure               0.007     0.0       1     
aggregate curves               0.007     0.0       14    
saving event loss tables       0.006     0.0       22    
filtering sources              0.002     0.0       1     
reading site collection        6.914E-06 0.0       1     
============================== ========= ========= ======