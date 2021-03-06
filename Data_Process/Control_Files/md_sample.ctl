Load Data
INFILE '$input'
BADFILE '$input.bad'



APPEND INTO TABLE "GSRDBA"."RAW_MD"
FIELDS TERMINATED BY ','
TRAILING NULLCOLS
(
LAYER_NUMBER,
ABBREV_FORMATION,
LITHOLOGY,
MD_TOP,
MD_BOTTOM,
THICKNESS,
CUM_THICKNESS,
value_attri,
RT_MIN,
RT_MAX,
RT_AVG,
AC_MIN,
AC_MAX,
AC_AVG,
DEN_MIN,
DEN_MAX,
DEN_AVG,
CNL_MIN,
CNL_MAX,
CNL_AVG,
VCL_MIN,
VCL_MAX,
VCL_AVG,
PHI_MIN,
PHI_MAX,
PHI_AVG,
PERM_MIN,
PERM_MAX,
PERM_AVG,
SOG_MIN,
SOG_MAX,
SOG_AVG,
LOG_INTERP_RESULT,
COMMENTS,
WELLID


)
