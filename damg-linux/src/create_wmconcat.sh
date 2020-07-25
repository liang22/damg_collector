# !/bin/bash
sqlplus -S -L /nolog<<EOF
connect / as sysdba
alter user wmsys account unlock;

CREATE OR REPLACE TYPE WM_CONCAT_IMPL AS OBJECT
-- AUTHID CURRENT_USER AS OBJECT
(
CURR_STR VARCHAR2(32767), 
STATIC FUNCTION ODCIAGGREGATEINITIALIZE(SCTX IN OUT WM_CONCAT_IMPL) RETURN NUMBER,
MEMBER FUNCTION ODCIAGGREGATEITERATE(SELF IN OUT WM_CONCAT_IMPL,
P1 IN VARCHAR2) RETURN NUMBER,
MEMBER FUNCTION ODCIAGGREGATETERMINATE(SELF IN WM_CONCAT_IMPL,
RETURNVALUE OUT VARCHAR2,
FLAGS IN NUMBER)
RETURN NUMBER,
MEMBER FUNCTION ODCIAGGREGATEMERGE(SELF IN OUT WM_CONCAT_IMPL,
SCTX2 IN WM_CONCAT_IMPL) RETURN NUMBER
);
/

CREATE OR REPLACE TYPE BODY WM_CONCAT_IMPL
IS
STATIC FUNCTION ODCIAGGREGATEINITIALIZE(SCTX IN OUT WM_CONCAT_IMPL)
RETURN NUMBER
IS
BEGIN
SCTX := WM_CONCAT_IMPL(NULL) ;
RETURN ODCICONST.SUCCESS;
END;
MEMBER FUNCTION ODCIAGGREGATEITERATE(SELF IN OUT WM_CONCAT_IMPL,
P1 IN VARCHAR2)
RETURN NUMBER
IS
BEGIN
IF(CURR_STR IS NOT NULL) THEN
CURR_STR := CURR_STR || ',' || P1;
ELSE
CURR_STR := P1;
END IF;
RETURN ODCICONST.SUCCESS;
END;
MEMBER FUNCTION ODCIAGGREGATETERMINATE(SELF IN WM_CONCAT_IMPL,
RETURNVALUE OUT VARCHAR2,
FLAGS IN NUMBER)
RETURN NUMBER
IS
BEGIN
RETURNVALUE := CURR_STR ;
RETURN ODCICONST.SUCCESS;
END;
MEMBER FUNCTION ODCIAGGREGATEMERGE(SELF IN OUT WM_CONCAT_IMPL,
SCTX2 IN WM_CONCAT_IMPL)
RETURN NUMBER
IS
BEGIN
IF(SCTX2.CURR_STR IS NOT NULL) THEN
SELF.CURR_STR := SELF.CURR_STR || ',' || SCTX2.CURR_STR ;
END IF;
RETURN ODCICONST.SUCCESS;
END;
END;
/

CREATE OR REPLACE FUNCTION wm_concat(P1 VARCHAR2)
RETURN VARCHAR2 AGGREGATE USING WM_CONCAT_IMPL ;
/

create public synonym WM_CONCAT_IMPL for wmsys.WM_CONCAT_IMPL
/
create public synonym wm_concat for wmsys.wm_concat
/
 
grant execute on WM_CONCAT_IMPL to public
/
grant execute on wm_concat to public;
quit;
EOF

exit 0