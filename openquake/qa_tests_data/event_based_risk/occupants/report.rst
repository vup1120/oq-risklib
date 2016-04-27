event based risk
================

gem-tstation:/home/michele/ssd/calc_128.hdf5 updated Wed Apr 27 11:09:58 2016

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
oqlite_version               '0.13.0-git952b07b'
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
====== ================= ========= ========== ==========
trt_id gsims             distances siteparams ruptparams
====== ================= ========= ========== ==========
0      BooreAtkinson2008 rjb       vs30       rake mag  
====== ================= ========= ========== ==========

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=1, rlzs=1)
  0,BooreAtkinson2008: ['<0,b1,b1,w=1.0>']>

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
event_based_risk_max_received_per_task 4895          
event_based_risk_num_tasks             38            
event_based_risk_sent.assetcol         67906         
event_based_risk_sent.monitor          22800         
event_based_risk_sent.riskinputs       406753        
event_based_risk_sent.riskmodel        69958         
event_based_risk_sent.rlzs_assoc       100054        
event_based_risk_tot_received          184245        
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
7 asset(s) x 1 realization(s) x 1 loss type(s) x 1 losses x 8 bytes x 40 tasks = 2.19 KB

Exposure model
--------------
=========== =
#assets     7
#taxonomies 1
=========== =

======== =======
Taxonomy #Assets
======== =======
tax1     7      
======== =======

Slowest sources
---------------
============ ========= ================= ====== ========= =========== ========== =========
trt_model_id source_id source_class      weight split_num filter_time split_time calc_time
============ ========= ================= ====== ========= =========== ========== =========
0            1         SimpleFaultSource 482    15        0.002       0.047      1.327    
============ ========= ================= ====== ========= =========== ========== =========

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
total event_based_risk         1.369     2.434     38    
total compute_ruptures         1.338     3.832     15    
building hazard                1.076     0.0       38    
filtering ruptures             0.920     0.0       265   
make contexts                  0.771     0.0       265   
compute poes                   0.298     0.0       265   
computing risk                 0.242     0.0       266   
saving ruptures                0.169     0.0       1     
managing sources               0.066     0.0       1     
splitting sources              0.047     0.0       1     
aggregate losses               0.016     0.0       266   
store source_info              0.011     0.0       1     
getting hazard                 0.010     0.0       266   
saving event loss tables       0.009     0.0       38    
reading composite source model 0.008     0.0       1     
reading exposure               0.006     0.0       1     
aggregate curves               0.005     0.0       15    
filtering sources              0.002     0.0       1     
reading site collection        6.914E-06 0.0       1     
============================== ========= ========= ======