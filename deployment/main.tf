terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.81.0"
    }
  }
}

provider "google" {
  project = "secretscout"
  region  = "us-central1"
}

provider "google-beta" {
  project = "secretscout"
  region  = "secretscout"
  zone    = "us-central1"

  //credentials = file(var.google_application_credentials)
}

resource "google_service_account" "service_account" {
  account_id  = "deployer"
  description = "TF-managed service account for SecretScout"
}