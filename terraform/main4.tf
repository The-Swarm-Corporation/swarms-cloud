

# Kubernetes Deployments for each model
resource "kubernetes_deployment" "cogvlm_deployment" {
  metadata {
    name = "cogvlm-deployment"
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "cogvlm"
      }
    }

    template {
      metadata {
        labels = {
          app = "cogvlm"
        }
      }

      spec {
        container {
          image = "public.ecr.aws/d6u1k1m2/cogvlmquant:latest"
          name  = "cogvlm"

          # Define resource requests and limits
          resources {
            limits = {
              cpu    = "500m"
              memory = "1024Mi"
            }

            requests = {
              cpu    = "250m"
              memory = "512Mi"
            }
          }
        }
      }
    }
  }
}


# Kubernetes Deployments for each model
resource "kubernetes_deployment" "qwenvl_deployment" {
  metadata {
    name = "qwenvl-deployment"
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "qwenvl"
      }
    }

    template {
      metadata {
        labels = {
          app = "qwenvl"
        }
      }

      spec {
        container {
          image = "public.ecr.aws/d6u1k1m2/qwenvl:latest"
          name  = "qwenvl"

          # Define resource requests and limits
          resources {
            limits = {
              cpu    = "500m"
              memory = "1024Mi"
            }

            requests = {
              cpu    = "250m"
              memory = "512Mi"
            }
          }
        }
      }
    }
  }
}
