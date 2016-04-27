Event Based Risk for Turkey reduced
===================================

gem-tstation:/home/michele/ssd/calc_131.hdf5 updated Wed Apr 27 11:10:34 2016

num_sites = 14, sitecol = 1.31 KB

Parameters
----------
============================ ===================
calculation_mode             'event_based_risk' 
number_of_logic_tree_samples 0                  
maximum_distance             {'default': 200.0} 
investigation_time           10.0               
ses_per_logic_tree_path      1                  
truncation_level             3.0                
rupture_mesh_spacing         2.0                
complex_fault_mesh_spacing   2.0                
width_of_mfd_bin             0.1                
area_source_discretization   10.0               
random_seed                  323                
master_seed                  42                 
avg_losses                   False              
oqlite_version               '0.13.0-git952b07b'
============================ ===================

Input files
-----------
======================== ==========================================================================
Name                     File                                                                      
======================== ==========================================================================
exposure                 `exposure.xml <exposure.xml>`_                                            
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
5      AkkarBommer2010 CauzziFaccioli2008 ChiouYoungs2008 ZhaoEtAl2006Asc rhypo rx rjb rrup vs30measured z1pt0 vs30 ztor mag hypo_depth rake dip
9      AkkarBommer2010 CauzziFaccioli2008 ChiouYoungs2008 ZhaoEtAl2006Asc rhypo rx rjb rrup vs30measured z1pt0 vs30 ztor mag hypo_depth rake dip
====== ================================================================== ================= ======================= ============================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=8, rlzs=8)
  5,AkkarBommer2010: ['<0,AreaSource,AkkarBommer2010asc_@_@_@_@_@_@,w=0.25>']
  5,CauzziFaccioli2008: ['<1,AreaSource,CauzziFaccioli2008asc_@_@_@_@_@_@,w=0.25>']
  5,ChiouYoungs2008: ['<2,AreaSource,ChiouYoungs2008asc_@_@_@_@_@_@,w=0.142857142857>']
  5,ZhaoEtAl2006Asc: ['<3,AreaSource,ZhaoEtAl2006Ascasc_@_@_@_@_@_@,w=0.0714285714286>']
  9,AkkarBommer2010: ['<4,FaultSourceAndBackground,AkkarBommer2010asc_@_@_@_@_@_@,w=0.1>']
  9,CauzziFaccioli2008: ['<5,FaultSourceAndBackground,CauzziFaccioli2008asc_@_@_@_@_@_@,w=0.1>']
  9,ChiouYoungs2008: ['<6,FaultSourceAndBackground,ChiouYoungs2008asc_@_@_@_@_@_@,w=0.0571428571429>']
  9,ZhaoEtAl2006Asc: ['<7,FaultSourceAndBackground,ZhaoEtAl2006Ascasc_@_@_@_@_@_@,w=0.0285714285714>']>

Number of ruptures per tectonic region type
-------------------------------------------
========================= ====== ==================== =========== ============ ======
source_model              trt_id trt                  num_sources eff_ruptures weight
========================= ====== ==================== =========== ============ ======
models/src/as_model.xml   5      Active Shallow Crust 9           25           1,779 
models/src/fsbg_model.xml 9      Active Shallow Crust 26          11           6,908 
========================= ====== ==================== =========== ============ ======

=============== =====
#TRT models     2    
#sources        35   
#eff_ruptures   36   
filtered_weight 8,687
=============== =====

Informational data
------------------
====================================== ==============
event_based_risk_max_received_per_task 2297          
event_based_risk_num_tasks             36            
event_based_risk_sent.assetcol         101232        
event_based_risk_sent.monitor          21600         
event_based_risk_sent.riskinputs       131721        
event_based_risk_sent.riskmodel        678168        
event_based_risk_sent.rlzs_assoc       1076940       
event_based_risk_tot_received          82035         
hostname                               'gem-tstation'
require_epsilons                       False         
====================================== ==============

Specific information for event based
------------------------------------
======================== =====
Total number of ruptures 36   
Total number of events   36   
Rupture multiplicity     1.000
======================== =====

Maximum memory allocated for the GMFs
-------------------------------------
The largest GMF block is for trt_model_id=5, contains 2 IMT(s), 4 realization(s)
and has a size of 2.06 KB / num_tasks

Estimated data transfer for the avglosses
-----------------------------------------
14 asset(s) x 8 realization(s) x 1 loss type(s) x 1 losses x 8 bytes x 64 tasks = 56 KB

Exposure model
--------------
=========== ==
#assets     14
#taxonomies 9 
=========== ==

======== =======
Taxonomy #Assets
======== =======
RC_HR    1      
RC_LR    3      
RC_MR    1      
SAM_1S   1      
SAM_2S   2      
SAM_3S   1      
SAM_4S   1      
URM_1S   2      
URM_2S   2      
======== =======

Slowest sources
---------------
============ ============ ================= ====== ========= =========== ========== =========
trt_model_id source_id    source_class      weight split_num filter_time split_time calc_time
============ ============ ================= ====== ========= =========== ========== =========
5            AS_GEAS343   AreaSource        625    1         0.001       0.0        5.813    
9            FSBG_TRBG103 AreaSource        282    1         0.001       0.0        2.803    
5            AS_TRAS334   AreaSource        244    1         9.909E-04   0.0        2.317    
5            AS_AMAS453   AreaSource        175    1         0.001       0.0        1.962    
5            AS_TRAS360   AreaSource        182    1         7.300E-04   0.0        1.832    
5            AS_TRAS346   AreaSource        154    1         8.550E-04   0.0        1.403    
5            AS_TRAS395   AreaSource        122    1         7.560E-04   0.0        1.141    
5            AS_TRAS458   AreaSource        121    1         7.272E-04   0.0        1.134    
5            AS_GEAS479   AreaSource        72     1         0.001       0.0        0.838    
5            AS_TRAS410   AreaSource        81     1         7.372E-04   0.0        0.746    
9            FSBG_TRBG989 AreaSource        33     1         7.629E-04   0.0        0.319    
9            FSBG_TRCS114 SimpleFaultSource 958    1         0.002       0.0        0.228    
9            FSBG_TRCS003 SimpleFaultSource 2,026  1,854     0.005       0.910      0.189    
9            FSBG_TRCS113 SimpleFaultSource 413    1         0.002       0.0        0.128    
9            FSBG_TRCS141 SimpleFaultSource 248    1         0.002       0.0        0.098    
9            FSBG_TRCS439 SimpleFaultSource 392    1         0.002       0.0        0.096    
9            FSBG_TRCS437 SimpleFaultSource 390    1         0.002       0.0        0.090    
9            FSBG_TRCS082 SimpleFaultSource 412    1         0.002       0.0        0.086    
9            FSBG_TRCS068 SimpleFaultSource 308    1         0.002       0.0        0.085    
9            FSBG_TRCS322 SimpleFaultSource 374    1         0.002       0.0        0.043    
============ ============ ================= ====== ========= =========== ========== =========

Slowest operations
------------------
============================== ========= ========= ======
operation                      time_sec  memory_mb counts
============================== ========= ========= ======
total compute_ruptures         21        0.363     18    
reading composite source model 9.120     0.0       1     
managing sources               2.081     0.0       1     
splitting sources              0.910     0.0       1     
total event_based_risk         0.563     0.031     36    
total compute_gmfs_and_curves  0.297     0.020     36    
compute poes                   0.292     0.0       72    
computing risk                 0.291     0.0       504   
filtering sources              0.225     0.0       155   
building hazard                0.180     0.0       36    
aggregating hcurves            0.105     0.0       144   
make contexts                  0.086     0.0       72    
bulding hazard curves          0.077     0.0       36    
saving gmfs                    0.054     0.0       144   
store source_info              0.048     0.0       1     
getting hazard                 0.047     0.0       504   
saving ruptures                0.028     0.0       1     
saving event loss tables       0.022     0.0       36    
aggregate curves               0.014     0.0       162   
reading exposure               0.013     0.0       1     
filtering ruptures             0.012     0.0       53    
aggregate losses               0.010     0.0       504   
compute and save statistics    0.003     0.0       1     
reading site collection        1.001E-05 0.0       1     
============================== ========= ========= ======