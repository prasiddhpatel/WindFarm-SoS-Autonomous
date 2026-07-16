# Root build notes

## Hardening pass

This pass focuses on making the repository more build-oriented and less placeholder-fragile:

- Added missing `CMakeLists.txt` files for ROS 2 packages.
- Added executable placeholder nodes where launch files referenced missing binaries.
- Added `sos_interfaces` messages/actions package.
- Added basic compile-safe implementations for control allocation, ESKF, coverage planning, MPC, and safety watchdog nodes.
- Reduced chances of launch-time breakage by aligning package names, executables, and install paths.

## Remaining caveats

The workspace is still not guaranteed fully colcon-clean in every environment because some dependencies, simulation plugins, and runtime integrations remain scaffold-grade. However, this pass significantly narrows the gap between repository structure and buildable ROS 2 layout.
