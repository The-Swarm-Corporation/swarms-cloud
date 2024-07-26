docker build . -t h4ckermike/swarms.world:patch-1
docker push h4ckermike/swarms.world:patch-1
kubectl apply -f deployment.yaml
# kubectl rollout restart deployment -l app=swarms-cloud-server-agent
