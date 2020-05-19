import capnp
import pkg_resources

_astroplant_schema_filename = pkg_resources.resource_filename(
    "astroplant_mqtt_connector", "proto/astroplant.capnp"
)

capnp.remove_import_hook()
astroplant_capnp = capnp.load(_astroplant_schema_filename)
