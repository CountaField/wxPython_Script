
call  GSRDBA.DAILY_CUM_DAYS_PRO();
call  GSRDBA.connect_prod_qc_proc();
call GSRDBA.cum_prod_aux_qc_proc();


exit;
