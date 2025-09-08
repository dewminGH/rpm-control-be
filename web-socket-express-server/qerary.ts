// CREATE OR REPLACE FUNCTION notify_fan_rpm_insert()
// RETURNS trigger AS $$
// BEGIN
//   PERFORM pg_notify('fan_rpm_channel', row_to_json(NEW)::text);
//   RETURN NEW;
// END;
// $$ LANGUAGE plpgsql;

// DROP TRIGGER IF EXISTS fan_rpm_insert_trigger ON fan_rpms;

// CREATE TRIGGER fan_rpm_insert_trigger
// AFTER INSERT ON fan_rpms
// FOR EACH ROW
// EXECUTE FUNCTION notify_fan_rpm_insert();
