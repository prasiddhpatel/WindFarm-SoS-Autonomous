resource "google_compute_network" "windfarm_vpc" {
  name                    = "windfarm-sos-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "windfarm_subnet" {
  name          = "windfarm-sos-subnet"
  ip_cidr_range = "10.20.0.0/24"
  network       = google_compute_network.windfarm_vpc.id
  region        = var.region
}

resource "google_compute_firewall" "allow_web" {
  name    = "windfarm-sos-allow-web"
  network = google_compute_network.windfarm_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080", "3000"]
  }
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_instance" "edge_server" {
  name         = "windfarm-sos-edge"
  machine_type = "n2-standard-8"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 100
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.windfarm_subnet.id
    access_config {}
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose-plugin git
    systemctl enable docker
    systemctl start docker
  EOT

  tags = ["windfarm-sos", "edge"]
}
