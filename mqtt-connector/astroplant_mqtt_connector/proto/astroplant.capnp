@0xfab5802082af6f74;

struct RawMeasurement {
  id @0 :Data;
  kitSerial @1 :Text;
  datetime @2 :UInt64;
  peripheral @3 :Int32;
  quantityType @4 :Int32;
  value @5 :Float64;
}

struct AggregateMeasurement {
  id @0 :Data;
  kitSerial @1 :Text;
  datetimeStart @2 :UInt64;
  datetimeEnd @3 :UInt64;
  peripheral @4 :Int32;
  quantityType @5 :Int32;
  values @6 :List(Value);

  struct Value {
      type @0 :Text;
      value @1 :Float64;
  }
}
