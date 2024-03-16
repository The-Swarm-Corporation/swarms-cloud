

# Kubernetes Deployments for each model
resource "kubernetes_deployment" "cogvlm_deployment" {
  depends_on = [null_resource.wait_for_k8s]
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
              memory = "25Gi"
            }

            requests = {
              memory = "35Gi"
            }
          }
        }
      }
    }
  }
}


# Kubernetes Deployments for each model
resource "kubernetes_deployment" "qwenvl_deployment" {
  depends_on = [null_resource.wait_for_k8s]
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
          image = "public.ecr.aws/d6u1k1m2/qwenvlm:latest"
          name  = "qwenvl"

          # Define resource requests and limits
          resources {
            limits = {
              memory = "25Gi"
            }

            requests = {
              memory = "35Gi"
            }
          }
        }
      }
    }
  }
}


resource "null_resource" "delay" {
  depends_on = [aws_instance.k8s_master]

  provisioner "local-exec" {
    command = "sleep 120" # Waits for 2 minutes
  }
}
