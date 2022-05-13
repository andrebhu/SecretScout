/*
resource "google_cloud_run_service" "scanner" {
  name     = "scanner"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_name}/${var.repo_name}/scanner:latest"

        resources {
          limits = {
            cpu    = 4
            memory = "4000M"
          }
        }

        env {
          name  = "GOOGLE_PROJECT_ID"
          value = var.project_name
        }
        env {
          name  = "INPUT_QUEUE"
          value = google_pubsub_topic.analysis_topic.name
        }
        env {
          name  = "GITHUB_TOKEN"
          value = var.github_api
        }
        env {
          name  = "DATABASE_URL"
          value = var.db_url
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
}
*/

resource "google_cloud_run_service" "bot" {
  name     = "bot"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_name}/${var.repo_name}/bot:latest"

        resources {
          limits = {
            cpu    = 4
            memory = "4000M"
          }
        }

        env {
          name  = "GOOGLE_PROJECT_ID"
          value = var.project_name
        }
        /*
        env {
          name  = "INPUT_QUEUE"
          value = google_pubsub_topic.analysis_topic.name
        }
        */
        env {
          name  = "GITHUB_TOKEN"
          value = var.github_api
        }
        env {
          name  = "DISCORD_TOKEN"
          value = var.discord_token
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
}
