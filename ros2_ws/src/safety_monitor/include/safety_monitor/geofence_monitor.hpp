#pragma once
#include <string>
#include <vector>

namespace safety_monitor {

/**
 * Geofence monitor using point-in-polygon (eq. 38 in report).
 * Parses a simple WKT POLYGON string.
 * Uses ray-casting (Jordan curve theorem) for O(n) inclusion test.
 */
class GeofenceMonitor {
public:
  explicit GeofenceMonitor(const std::string& wkt_polygon);

  /** Returns true iff (x,y) is inside the geofence. */
  bool inside(double x, double y) const;

private:
  struct Point { double x, y; };
  std::vector<Point> polygon_;

  static std::vector<Point> parse_wkt(const std::string& wkt);
};

} // namespace safety_monitor
