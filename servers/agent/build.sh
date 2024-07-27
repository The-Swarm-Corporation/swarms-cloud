docker build . -t h4ckermike/swarms.world:patch-3
docker push h4ckermike/swarms.world:patch-3
kubectl apply -f deployment.yaml
# kubectl rollout restart deployment -l app=swarms-cloud-server-agent
