LOAD DATA
INFILE '$input' 
BADFILE '$input.bad'



APPEND INTO TABLE "GSRDBA"."PRODUCTION_DATA"
FIELDS TERMINATED BY ','
TRAILING NULLCOLS
(
WELLID,
PRODUCTION_DATE date"mm/dd/yyyy",
PROD_TIME,
OPERATIONAL_TIME,
WELL_HEAD_PRESSURE,
WELL_HEAD_TEMPERATURE,
DAILY_PROD_GAS,
prod_cum_gas,
PROD_COMMENTS char(500),
DAILY_INJ_METHANOL,
INJECTION_cum,
DAILY_PROD_COND,
prod_cum_cond,
DAILY_PROD_WATER,
PROD_CUM_WATER
)
