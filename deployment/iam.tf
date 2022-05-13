data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location = google_cloud_run_service.bot.location
  project  = google_cloud_run_service.bot.project
  service  = google_cloud_run_service.bot.name

  policy_data = data.google_iam_policy.noauth.policy_data
}

/*
resource "google_service_account" "scanner_sa" {
  account_id = "scanner-sa"
}

// Allow invocation by pubsub to cloud run by bot only
resource "google_cloud_run_service_iam_member" "scanner_iam_member" {
  service  = google_cloud_run_service.scanner.name
  location = google_cloud_run_service.scanner.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scanner_sa.email}"
}

// Restrict publish access only to bot dispatcher
resource "google_pubsub_topic_iam_binding" "scanner_binding" {
  topic   = google_pubsub_topic.analysis_topic.name
  role    = "roles/pubsub.publisher"
  members = ["serviceAccount:${google_service_account.service_account.email}"]
}
*/
