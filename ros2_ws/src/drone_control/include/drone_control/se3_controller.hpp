#pragma once
#include <Eigen/Dense>
#include <Eigen/Geometry>

namespace drone_control {

/**
 * @brief Geometric SE(3) position + attitude controller.
 *
 * Implements equations (13)-(15) from the SoS technical report.
 * Almost-globally exponentially stable on SE(3); avoids Euler-angle
 * singularities during high-tilt blade-underside imaging manoeuvres.
 */
class SE3Controller {
public:
  struct Gains {
    double kp{6.0}, kv{4.5};          // position / velocity
    double kR{8.0}, kW{2.5};          // attitude / angular-rate
    double ki_p{0.4};                  // position integral
  };

  struct State {
    Eigen::Vector3d p, v;              // position, velocity (world)
    Eigen::Matrix3d R;                 // rotation body->world
    Eigen::Vector3d omega;             // body angular rate
  };

  struct Reference {
    Eigen::Vector3d pd, vd, ad;        // desired pos/vel/acc
    double yaw_d{0.0};
    double yaw_rate_d{0.0};
  };

  struct Output {
    double    thrust;                  // collective thrust [N]
    Eigen::Vector3d torque;            // body torques [Nm]
    Eigen::Matrix3d R_des;             // desired rotation (for logging)
  };

  explicit SE3Controller(double mass_kg, const Eigen::Matrix3d& inertia,
                         const Gains& gains = {});

  Output compute(const State& x, const Reference& ref, double dt);

  void reset_integral();
  void set_gains(const Gains& g) { gains_ = g; }

private:
  double mass_;
  Eigen::Matrix3d J_;
  Gains gains_;
  Eigen::Vector3d int_ep_{Eigen::Vector3d::Zero()};

  static constexpr double g_ = 9.81;

  /** vee-map: skew-symmetric matrix -> vector */
  static Eigen::Vector3d vee(const Eigen::Matrix3d& M);
  /** hat-map: vector -> skew-symmetric matrix */
  static Eigen::Matrix3d hat(const Eigen::Vector3d& v);
};

} // namespace drone_control
