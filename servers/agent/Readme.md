

Install tools
https://gist.github.com/vfarcic/8ebbf4943c5c012c8c98e1967fa7f33b
`nix-shell --packages gh kubectl awscli2 helm eksctl`

docker, docker compose
`sudo apt install docker.io`

aws eks --profile swarms --region us-east-1 update-kubeconfig --name eks

Build image
```
docker build . -t h4ckermike/swarms.world:first
docker push h4ckermike/swarms.world:first
```

Check 
https://hub.docker.com/layers/h4ckermike/swarms.world/first/images/sha256-242354461165dd0f9df03f7a1748d4e6569c4d45b61790757709cc1bc71f6e91?context=repo

Following this tutorial
https://docs.aws.amazon.com/codecatalyst/latest/userguide/deploy-tut-eks.html#deploy-tut-eks-ecr
and the notes here
https://bartek-blog.github.io/kubernetes/helm/python/fastapi/2020/12/13/helm.html

```
aws eks update-kubeconfig --region us-east-1 --name cluster --profile swarms
kubectl apply -f deployment.yaml
```

Look in eks and see that the resource has been deployed.
https://us-east-1.console.aws.amazon.com/eks/home?region=us-east-1#/clusters/cluster?selectedTab=cluster-resources-tab&selectedResourceId=pods

* describe
`kubectl describe service swarms-world`

```
Name:                     swarms-world
Namespace:                default
Labels:                   app=swarms-cloud-server-agent
Annotations:              <none>
Selector:                 app=swarms-cloud-server-agent
Type:                     LoadBalancer
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.100.123.185
IPs:                      10.100.123.185
LoadBalancer Ingress:     a34f2f308013145858827f49a34f3bef-1801899861.us-east-1.elb.amazonaws.com
Port:                     <unset>  80/TCP
TargetPort:               8000/TCP
NodePort:                 <unset>  31384/TCP
Endpoints:                172.16.22.218:8000,172.16.27.42:8000,172.16.8.120:8000
Session Affinity:         None
External Traffic Policy:  Cluster
Events:
  Type    Reason                Age                  From                Message
  ----    ------                ----                 ----                -------
  Normal  EnsuringLoadBalancer  8m53s (x3 over 12h)  service-controller  Ensuring load balancer
  Normal  EnsuredLoadBalancer   8m52s (x3 over 12h)  service-controller  Ensured load balancer

```

get the logs
`kubectl logs --all-containers=true -l app=swarms-cloud-server-agent`

Test locally
`docker compose build`
`docker compose up`
`bash ./test2.sh`

Roll out new version
`kubectl rollout restart deployment -l app=swarms-cloud-server-agent`
