#include "safety_monitor/geofence_monitor.hpp"
#include <sstream>
#include <regex>
#include <cmath>

namespace safety_monitor {

GeofenceMonitor::GeofenceMonitor(const std::string& wkt)
    : polygon_(parse_wkt(wkt)) {}

/** Ray-casting point-in-polygon test (eq. 38). */
bool GeofenceMonitor::inside(double px, double py) const {
  int n = static_cast<int>(polygon_.size());
  if (n < 3) return false;
  int crossings = 0;
  for (int i = 0, j = n-1; i < n; j = i++) {
    const auto& pi = polygon_[i];
    const auto& pj = polygon_[j];
    if (((pi.y > py) != (pj.y > py)) &&
        (px < (pj.x - pi.x) * (py - pi.y) / (pj.y - pi.y) + pi.x))
      ++crossings;
  }
  return (crossings % 2) == 1;
}

std::vector<GeofenceMonitor::Point>
GeofenceMonitor::parse_wkt(const std::string& wkt) {
  std::vector<Point> pts;
  // Extract coordinate pairs from WKT POLYGON((x1 y1, x2 y2, ...))
  std::regex re(R"((-?\d+\.?\d*)\s+(-?\d+\.?\d*))");
  auto begin = std::sregex_iterator(wkt.begin(), wkt.end(), re);
  auto end   = std::sregex_iterator();
  for (auto it = begin; it != end; ++it) {
    pts.push_back({std::stod((*it)[1].str()),
                   std::stod((*it)[2].str())});
  }
  return pts;
}

} // namespace safety_monitor
