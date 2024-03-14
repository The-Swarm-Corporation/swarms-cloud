
# Kubernetes Service for each model
resource "kubernetes_service" "cogvlm_service" {
  metadata {
    name = "cogvlm-service"
  }
  spec {
    selector = {
      app = "cogvlm"
    }
    port {
      port        = 80
      target_port = 8000
    }
    type = "LoadBalancer"
  }
}


# Kubernetes Service for each model
resource "kubernetes_service" "qwenvl_service" {
  metadata {
    name = "qwenvl-service"
  }
  spec {
    selector = {
      app = "qwenvl"
    }
    port {
      port        = 80
      target_port = 8000
    }
    type = "LoadBalancer"
  }
}
