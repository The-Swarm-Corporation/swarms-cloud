resource "kubernetes_horizontal_pod_autoscaler" "cogvlm_hpa" {
  metadata {
    name = "cogvlm-hpa"
  }

  spec {
    max_replicas = 50 // Adjust based on the maximum expected scale
    min_replicas = 2
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.cogvlm_deployment.metadata[0].name
    }
    metrics {
      type = "Pods"
      pods {
        metric {
          name = "inference_requests_per_minute" // Adjusted to per minute
        }
        target {
          type = "AverageValue"
          average_value = "3" // Target requests per pod per minute
        }
      }
    }
  }
}

resource "kubernetes_horizontal_pod_autoscaler" "qwenvl_hpa" {
  metadata {
    name = "qwenvl-hpa"
  }

  spec {
    max_replicas = 100 // Adjust based on the maximum expected scale
    min_replicas = 2
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.qwenvl_deployment.metadata[0].name
    }
    metrics {
      type = "Pods"
      pods {
        metric {
          name = "inference_requests_per_minute" // Adjusted to per minute
        }
        target {
          type = "AverageValue"
          average_value = "3" // Target requests per pod per minute
        }
      }
    }
  }
}
