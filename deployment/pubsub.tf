/*
resource "google_pubsub_topic" "analysis_topic" {
  name = "analysis"
}

// Pushes an excavated fork to analyzer
resource "google_pubsub_subscription" "analysis_sub" {
  name  = "analysis_sub"
  topic = google_pubsub_topic.analysis_topic.name

  // Forks will take time to acknowledge, set deadline to max
  ack_deadline_seconds = 600

  // Forks that fail will be here for a while
  message_retention_duration = "5400s"

  // Make push subscription to the Cloud Run listener endpoint
  push_config {
    push_endpoint = google_cloud_run_service.scanner.status[0].url

    attributes = {
      x-goog-version = "v1"
    }

    // service to service auth, as this is not deployed publicly
    oidc_token {
      service_account_email = google_service_account.scanner_sa.email
    }
  }

  // Retry sending request every 10 minutes
  retry_policy {
    minimum_backoff = "600s"
    maximum_backoff = "600s"
  }

  // Drop failed requests in DLQ after 10 failed requests
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.analysis_dlq.id
    max_delivery_attempts = 10
  }
}

// Dead letter queue for non-retryable messages
resource "google_pubsub_topic" "analysis_dlq" {
  name = "analysis_dlq"
}

// Subscription for dead letter queue
resource "google_pubsub_subscription" "analysis_dlq_sub" {
  name  = "analysis_dlq_sub"
  topic = google_pubsub_topic.analysis_dlq.name
}
*/
