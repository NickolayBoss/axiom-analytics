-- Fail if any expected table, FK or partial unique index is absent.
DO $$
DECLARE
  actual_tables integer;
  actual_fks integer;
  captured_unique integer;
BEGIN
 SELECT COUNT(*) INTO actual_tables FROM information_schema.tables
 WHERE table_schema='public' AND table_type='BASE TABLE'
 AND table_name IN ('customers','categories','products','campaigns','orders','order_items','payments','refunds','sessions','events');
 IF actual_tables <> 10 THEN RAISE EXCEPTION 'Expected 10 tables, got %',actual_tables; END IF;
 SELECT COUNT(*) INTO actual_fks FROM pg_constraint c
 JOIN pg_namespace n ON n.oid=c.connamespace
 WHERE n.nspname='public' AND c.contype='f';
 IF actual_fks <> 11 THEN RAISE EXCEPTION 'Expected 11 FKs, got %',actual_fks; END IF;
 SELECT COUNT(*) INTO captured_unique FROM pg_indexes
 WHERE schemaname='public' AND indexname='uq_payments_captured_order'
 AND indexdef ILIKE '%UNIQUE INDEX%' AND indexdef LIKE '%status%captured%';
 IF captured_unique <> 1 THEN RAISE EXCEPTION 'Captured payment unique partial index missing'; END IF;
 RAISE NOTICE 'PASS: 10 tables, 11 FKs and unique captured-payment index';
END $$;
