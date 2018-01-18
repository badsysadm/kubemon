# kubemon
Script for get info from kubernetes-api

Create symlink "pki" to catalog "/etc/kubernetes/pki"

python3 kubeapi full - list all pods

python3 kubeapi {namespace} full - show info about pods in ns

python3 kubeapi {namespace} describe - show full info about pods in ns

python3 kubeapi {namespace} {pod name's mask} - show full info about pod

python3 kubeapi nodes - show info about nodes
