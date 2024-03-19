
# Kubernetes Service for each model
resource "kubernetes_service" "cogvlm_service" {
  depends_on = [
    null_resource.init_k8s_cluster
  ]

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
  depends_on = [
    null_resource.init_k8s_cluster
  ]

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
