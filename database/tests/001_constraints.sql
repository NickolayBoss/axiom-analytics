-- Run against a freshly migrated, disposable database:
-- psql -X -v ON_ERROR_STOP=1 -1 -f database/tests/001_constraints.sql
-- Entire fixture is rolled back; DO blocks assert expected SQLSTATE errors.
INSERT INTO customers VALUES (1, '2026-01-01 00:00+00', 'North', 'organic');
INSERT INTO categories VALUES (1, 'Demo');
INSERT INTO products(product_id,category_id,product_name,list_price) VALUES (1,1,'Widget',100);
INSERT INTO campaigns VALUES (1,'Demo campaign','social','2026-01-01','2026-01-31',100);
INSERT INTO orders VALUES (1,1,'2026-01-02 00:00+00','completed');
INSERT INTO order_items VALUES (1,1,1,2,100,10);
INSERT INTO payments VALUES (1,1,'2026-01-02 00:01+00',190,'captured');
INSERT INTO refunds VALUES (1,1,'2026-01-03 00:00+00','2026-01-03 01:00+00',10,'settled','Customer return');
INSERT INTO sessions VALUES (1,1,1,'2026-01-02 00:00+00','2026-01-02 00:10+00');
INSERT INTO events VALUES (1,1,'2026-01-02 00:00+00','session_start',NULL,NULL);
INSERT INTO events VALUES (2,1,'2026-01-02 00:01+00','product_view',NULL,1);
INSERT INTO events VALUES (3,1,'2026-01-02 00:02+00','add_to_cart',NULL,1);
INSERT INTO events VALUES (4,1,'2026-01-02 00:03+00','checkout_start',1,NULL);
INSERT INTO events VALUES (5,1,'2026-01-02 00:04+00','purchase',1,NULL);

DO $test$
DECLARE n integer := 0;
BEGIN
 BEGIN INSERT INTO order_items VALUES (20,1,1,0,10,0);
 EXCEPTION WHEN check_violation THEN n := n+1; END;
 BEGIN INSERT INTO order_items VALUES (21,1,1,1,-1,0);
 EXCEPTION WHEN check_violation THEN n := n+1; END;
 BEGIN INSERT INTO order_items VALUES (22,1,1,1,10,11);
 EXCEPTION WHEN check_violation THEN n := n+1; END;
 BEGIN INSERT INTO orders VALUES (2,1,now(),'invalid');
 EXCEPTION WHEN check_violation THEN n := n+1; END;
 BEGIN INSERT INTO refunds VALUES (20,1,now(),NULL,1,'invalid','Test');
 EXCEPTION WHEN check_violation THEN n := n+1; END;
 BEGIN INSERT INTO orders VALUES (3,999,now(),'placed');
 EXCEPTION WHEN foreign_key_violation THEN n := n+1; END;
 BEGIN INSERT INTO payments VALUES (2,1,now(),190,'captured');
 EXCEPTION WHEN unique_violation THEN n := n+1; END;
 BEGIN INSERT INTO refunds VALUES (21,1,now(),NULL,1,'settled','Test');
 EXCEPTION WHEN check_violation THEN n := n+1; END;
 BEGIN INSERT INTO refunds VALUES (22,1,now(),now(),1,'pending','Test');
 EXCEPTION WHEN check_violation THEN n := n+1; END;
 BEGIN INSERT INTO campaigns VALUES (2,'Bad','social','2026-02-02','2026-02-01',10);
 EXCEPTION WHEN check_violation THEN n := n+1; END;
 BEGIN INSERT INTO sessions VALUES (2,NULL,NULL,now(),now() - interval '1 minute');
 EXCEPTION WHEN check_violation THEN n := n+1; END;
 BEGIN INSERT INTO events VALUES (20,1,now(),'purchase',NULL,NULL);
 EXCEPTION WHEN check_violation THEN n := n+1; END;
 BEGIN INSERT INTO events VALUES (21,1,now(),'product_view',NULL,NULL);
 EXCEPTION WHEN check_violation THEN n := n+1; END;
 IF n <> 13 THEN RAISE EXCEPTION 'Expected 13 constraint failures; observed %',n; END IF;
 RAISE NOTICE 'PASS: 13 expected constraint failures; valid fixtures inserted';
END
$test$;
-- This transaction is rolled back by the caller with the -1 option only if an error occurs.
-- Use the separate test runner below to guarantee rollback on success.
