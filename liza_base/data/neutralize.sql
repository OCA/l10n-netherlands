-- Remove Liza credentials
UPDATE res_company
   SET liza_login = NULL, liza_password = NULL;
